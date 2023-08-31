import argparse
import logging
import os
import platform
from pathlib import Path

from i_hate_papers.arxiv_utils import get_file_list, get_file_content
from i_hate_papers.latex_utils import process_latex_content
from i_hate_papers.openai_utils import summarise_latex

logger = logging.getLogger(__name__)


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description=("Summarise an arXiv paper"))
    parser.add_argument("ARXIV_ID", help="arXiv paper ID (example: 1234.56789)")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable detailed logging"
    )
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="Don't prompt for file selection, just use the largest tex file",
    )
    parser.add_argument(
        "--no-html", action="store_true", help="Skip HTML file generation"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't open the HTML file when complete (macOS only)",
    )
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        format="%(name)s [%(levelname)-8s] %(message)s", level=log_level
    )

    arxiv_id = args.ARXIV_ID

    # Which file do we want to convert?
    files = get_file_list(arxiv_id)
    if args.no_input:
        selected_file = 0
    else:
        for i, (name, size) in enumerate(files):
            print(f"    [{i}] {name}, {size:,}b")
        selected_file = int(input("What file should I summarise [0]? ") or "0")

    # Get the file content?
    file_name = files[selected_file][0]
    content = get_file_content(arxiv_id, file_name)

    # Parse the tex and create markdown
    title, sections = process_latex_content(content)
    output_markdown = f"# {title}\n\n"

    for section_title, section_content in sections.items():
        logger.info(f"Summarising: {section_title}")
        output_markdown += f"## {section_title}\n\n"
        output_markdown += summarise_latex(section_title, section_content) + "\n\n"

    # TODO: Add markdown footer with metadata

    # Write out the markdown
    md_path = Path(f"summary-{arxiv_id}.md")
    md_path.write_text(output_markdown)

    # Render HTML from markdown and write it out
    if not args.no_html:
        import markdown

        html_path = Path(f"summary-{arxiv_id}.html")
        md = markdown.Markdown(
            extensions=["mdx_math"],
            extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
        )
        html_path.write_text(HTML % md.convert(md_path.read_text()))
        if not args.no_open and platform.system() == "Darwin":
            os.system(f"open {html_path}")


HTML = """<!DOCTYPE html>
<html>
<head>
    <link href="https://unpkg.com/readable-css/css/readable.css" rel="stylesheet" />
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-MML-AM_CHTML"></script>
    <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      config: ["MMLorHTML.js"],
      jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
      extensions: ["MathMenu.js", "MathZoom.js"]
    });
    </script>
</head>
<body class="readable-content">
    %s
</body>
</html>
"""


if __name__ == "__main__":
    main()
