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
        "--verbosity",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Set the logging verbosity (0 = quiet, 1 = info logging, 2 = debug logging)",
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
    parser.add_argument(
        "--detail-level",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="How detailed should the summary be? (0 = minimal detail, 1 = normal, 2 = more detail)",
    )
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="What model be used to generate the summaries ()",
    )
    # TODO: No-cache parameter
    args = parser.parse_args()

    # Setup logging
    log_level = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(args.verbosity)

    logging.basicConfig(
        format="%(name)-30s [%(levelname)-8s] %(message)s", level=log_level
    )

    arxiv_id = args.ARXIV_ID

    # Get the input file content
    content = _get_input_content(
        arxiv_id=arxiv_id,
        no_input=args.no_input,
    )

    # Summarise it
    output_markdown = _summarise_content(
        content=content,
        detail_level=args.detail_level,
        model=args.model,
    )

    # Write the output
    file_name = f"summary-{arxiv_id}-d{args.detail_level}-{args.model}"
    _write_output(
        output_markdown=output_markdown,
        file_name=file_name,
        make_html=not args.no_html,
        open_html=not args.no_open,
    )


def _get_input_content(arxiv_id, no_input):
    # Get a list of source files for this paper from arXiv
    logger.debug(f"Getting input content. {arxiv_id=} {no_input=}")

    files = get_file_list(arxiv_id)
    logger.debug(f"Got a list of {len(files)} files")

    # Which file do we want to convert?
    if no_input:
        # Always use the first (the largest .tex file)
        selected_file = 0
    else:
        # Ask the user
        for i, (name, size) in enumerate(files):
            print(f"    [{i}] {name}, {size:,}b")
        selected_file = int(input("What file should I summarise [0]? ") or "0")

    # Return the file content
    file_name, _ = files[selected_file]
    logger.debug(f"Getting content for file {file_name}")
    return get_file_content(arxiv_id, file_name)


def _summarise_content(content, detail_level, model):
    """Summarise the content using ChatGPT"""
    # Parse the tex content into sections
    logger.debug(
        f"Parsing {len(content):,}b of input content. {detail_level=}, {model=}"
    )
    title, sections = process_latex_content(content)

    logger.debug(f"Found {len(content)} latex sections, document title: {title}")

    # Document title
    output_markdown = f"# {title}\n\n"

    # Summarise each section into markdown
    for section_title, section_content in sections.items():
        logger.info(f"Summarising: {section_title}")
        output_markdown += f"## {section_title}\n\n"
        # This will call ChatGPT
        output_markdown += (
            summarise_latex(
                content=section_content,
                detail_level=detail_level,
                model=model,
            )
            + "\n\n"
        )

    logger.debug(f"Summarising complete")

    return output_markdown


def _write_output(output_markdown, file_name, make_html, open_html):
    """Write the output markdown to a file and render the HTML"""
    logger.debug(f"Writing output {file_name=}, {make_html=}, {open_html=}")

    # TODO: Add markdown footer with metadata
    # Write out the markdown
    md_path = Path(f"{file_name}.md")
    md_path.write_text(output_markdown)

    logger.info(f"Written markdown to: {md_path}")

    # Render HTML from markdown and write it out
    if make_html:
        import markdown

        html_path = Path(f"{file_name}.html")
        md = markdown.Markdown(
            extensions=["mdx_math"],
            extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
        )
        html_path.write_text(HTML % md.convert(output_markdown))
        logger.info(f"Written HTML to: {html_path}")
        if open_html and platform.system() == "Darwin":
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
