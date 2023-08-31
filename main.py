import os
from pathlib import Path

from markdown import markdown

from i_hate_papers.arxiv_utils import get_file_list, get_file_content
from i_hate_papers.latex_utils import process_latex_content
from i_hate_papers.openai_utils import openai_request


def main():
    arxiv_id = "2106.09685"

    files = get_file_list(arxiv_id)
    for i, (name, size) in enumerate(files):
        print(f"    [{i}] {name}, {size:,}b")
    selected_file = int(input("What file should I summarise [0]? ") or "0")

    file_name = files[selected_file][0]
    content = get_file_content(arxiv_id, file_name)

    sections = process_latex_content(content)
    output_markdown = ""

    for section_title, section_content in sections.items():
        response = openai_request(
            (
                "Summarise the following content for someone with a only high-level understanding of "
                "the subject matter. Format your response using markdown syntax:"
            ),
            section_content,
            temperature=0.3,
        )
        output_markdown += f"#{section_title}\n\n" f"{response}\n\n"

    md_path = Path(f"summary-{arxiv_id}.md")
    html_path = Path(f"summary-{arxiv_id}.html")

    md_path.write_text(output_markdown)
    html_path.write_text(markdown(output_markdown))
    os.system(f"open {html_path}")


if __name__ == "__main__":
    main()
