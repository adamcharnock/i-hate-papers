from i_hate_papers import md_parser
from i_hate_papers.markdown_utils import process_markdown_content

COMMON_SECTION_NAMES = (
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusion",
    "acknowledgements",
)


def process_html_content(content: str) -> tuple[str, dict[str, str]]:
    import html2text

    markdown = html2text.html2text(content)
    return process_markdown_content(markdown)
