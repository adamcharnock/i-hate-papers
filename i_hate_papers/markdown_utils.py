from i_hate_papers import md_parser

COMMON_SECTION_NAMES = (
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusion",
    "acknowledgements",
)


def process_markdown_content(content: str) -> tuple[str, dict[str, str]]:
    root = md_parser.DocumentTreeNode(source=content)
    root.parse()

    # Get all the sections
    all_sections = [s for s in root.walk() if s.is_section]

    # Find the likely depth of the sections we are looking for
    heading_depth_to_load = None
    for section in all_sections:
        if heading_depth_to_load:
            break

        for common_name in COMMON_SECTION_NAMES:
            if common_name in section.name.lower():
                heading_depth_to_load = section.depth

    # Get the sections to parse
    sections_to_parse = {
        s.name: s.as_markdown()
        for s in all_sections
        if s.depth == heading_depth_to_load
    }

    # Get all the headings at the depth we want to load
    h1_titles = [s.name for s in all_sections if s.depth == 1]
    # Get the longest h1 heading
    sorted(h1_titles, key=lambda h: len(h))
    title = h1_titles[-1]

    return title, sections_to_parse
