import argparse
from datetime import datetime, timezone
import logging
import os
import platform
import re
from pathlib import Path

from i_hate_papers.arxiv_utils import get_file_list, get_file_content
from i_hate_papers.html_utils import process_html_content
from i_hate_papers.latex_utils import process_latex_content
from i_hate_papers.markdown_utils import process_markdown_content
from i_hate_papers.openai_utils import summarise_latex, extract_glossary

logger = logging.getLogger(__name__)


def main():
    # Argument parsing
    args = _parse_args()

    # Setup logging
    _setup_logging(verbosity=args.verbosity)

    input_ = args.INPUT

    # Get the input file content, and some kind of file identifier
    input_id, content_format, content = _get_input_content(
        input_=input_,
        no_input=args.no_input,
    )

    title, sections = _parse_input_content(
        content=content,
        content_format=content_format,
    )

    # Summarise it
    output_markdown = (
        _summarise_content(
            title=title,
            sections=sections,
            detail_level=args.detail_level,
            model=args.model,
        )
        + "\n\n"
    )

    if not args.no_glossary:
        # Make a glossary from the summarised content
        # TODO: The summarised content is sometimes not enough for the LLM to correctly
        #       define a term. What would be better is to generate the list of words using
        #       the summarised content, but then define the words using the original content.
        #       However, the original content is often quite large, so passing that all at once to the
        #       LLM may prove difficult without some intelligence.
        output_markdown += (
            _make_glossary(
                content=output_markdown,
                model=args.model,
            )
            + "\n\n"
        )

    if not args.no_footer:
        output_markdown += _make_metadata_footer(args) + "\n\n"

    # Write the output
    file_name = f"summary-{input_id}-d{args.detail_level}-{args.model}"
    _write_output(
        output_markdown=output_markdown,
        file_name=file_name,
        make_html=not args.no_html,
        open_html=not args.no_open,
    )


def _parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Summarise an academic paper\n\n"
            "You must set the OPENAI_API_KEY environment variable using your OpenAi.com API key"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "INPUT",
        help="arXiv paper ID (example: 1234.56789) or path to a .tex/.html/.md file",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="Set the logging verbosity (0 = quiet, 1 = info logging, 2 = debug logging). Default is 1",
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
        "--no-footer",
        action="store_true",
        help="Don't include a footer containing metadata",
    )
    parser.add_argument(
        "--no-glossary",
        action="store_true",
        help="Don't include a glossary",
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
        default="gpt-3.5-turbo-16k",
        help="What model to use to generate the summaries",
    )
    # TODO: No-cache parameter
    return parser.parse_args()


def _setup_logging(verbosity):
    log_level = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(verbosity)

    logging.basicConfig(
        format="%(name)-30s [%(levelname)-8s] %(message)s", level=log_level
    )


def _get_input_content(input_: str, no_input: bool) -> tuple[str, str, str]:
    # Get a list of source files for this paper from arXiv (or from a tex or md file)

    # If this isn't an arXiv then assume it is a path to a file
    if not re.match(r"\d+\.\d+", input_):
        logger.debug(
            f"Input '{input_}' isn't an arXiv ID. Assuming it is a file, will read from disk"
        )
        path = Path(input_)

        if path.suffix == ".html":
            return path.stem, "html", path.read_text(encoding="utf8")
        elif path.suffix == ".tex":
            return path.stem, "latex", path.read_text(encoding="utf8")
        elif path.suffix == ".md":
            return path.stem, "markdown", path.read_text(encoding="utf8")
        else:
            raise Exception(f"Unknown file type: {path.suffix}")

    # Ok, it is a arXiv paper ID
    arxiv_id = input_

    logger.debug(f"Getting input content from arXiv. {arxiv_id=} {no_input=}")

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
    return arxiv_id, "latex", get_file_content(arxiv_id, file_name)


def _parse_input_content(
    content: str, content_format: str
) -> tuple[str, dict[str, str]]:
    # Parse the tex content into sections
    logger.debug(f"Parsing {len(content):,}b of input content.")

    if content_format == "latex":
        title, sections = process_latex_content(content)
    elif content_format == "html":
        title, sections = process_html_content(content)
    elif content_format == "markdown":
        title, sections = process_markdown_content(content)
    else:
        raise Exception(f"Unknown content format: {content_format}")

    logger.debug(f"Found {len(content)} latex sections, document title: {title}")

    return title, sections


def _summarise_content(
    title: str, sections: dict[str, str], detail_level: int, model: str
) -> str:
    """Summarise the content using ChatGPT"""

    logger.debug(f"Summarising {len(sections)} sections. {detail_level=}, {model=}")

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

    return output_markdown.strip()


def _make_glossary(content: str, model: str):
    """Generate a glossary as markdown"""
    logger.info(f"Creating glossary")
    terms = extract_glossary(content, model=model)

    return (
        "## Glossary (Generated)\n\n"
        "This glossary has been generated based on the terminology used in the summarised content above.\n\n"
    ) + terms


def _make_metadata_footer(args):
    footer = "# About this summary\n\n"
    footer += "| Argument | Value |\n"
    footer += "| -- | -- |\n"

    metadata = args._get_kwargs()

    for name, value in metadata:
        footer += f"| {name} | {value} |\n"
    footer += "\n"

    footer += f"Summary was created at `{datetime.now(timezone.utc).isoformat()}`\n\n"

    return footer.strip()


def _write_output(
    output_markdown: str, file_name: str, make_html: bool, open_html: bool
):
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
            extensions=["mdx_math", "tables"],
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
