import os
from pathlib import Path

import markdown

from i_hate_papers.arxiv_utils import get_file_list, get_file_content
from i_hate_papers.latex_utils import process_latex_content
from i_hate_papers.openai_utils import openai_request


def main():
    arxiv_id = "2106.09685"
    #
    # files = get_file_list(arxiv_id)
    # for i, (name, size) in enumerate(files):
    #     print(f"    [{i}] {name}, {size:,}b")
    # selected_file = int(input("What file should I summarise [0]? ") or "0")
    #
    # file_name = files[selected_file][0]
    # content = get_file_content(arxiv_id, file_name)
    #
    # sections = process_latex_content(content)
    # output_markdown = ""
    #
    # for section_title, section_content in sections.items():
    #     print(f"Summarising: {section_title}")
    #     response = openai_request(
    #         (
    #             "Summarise the following section for someone with a only high-level understanding of "
    #             "the subject matter. Go into detail where necessary. Format your response using markdown syntax:"
    #         ),
    #         section_content,
    #         temperature=0.3,
    #     )
    #     output_markdown += f"#{section_title}\n\n" f"{response}\n\n"
    #
    md_path = Path(f"summary-{arxiv_id}.md")
    # md_path.write_text(output_markdown)

    html_path = Path(f"summary-{arxiv_id}.html")
    md = markdown.Markdown(
        extensions=["mdx_math"],
        extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
    )

    html_path.write_text(HTML % md.convert(md_path.read_text()))
    os.system(f"open {html_path}")


HTML = """<!DOCTYPE html>
<html>
<head>
    
</head>
<body>
    %s
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js"></script>
    <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      config: ["MMLorHTML.js"],
      jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
      extensions: ["MathMenu.js", "MathZoom.js"]
    });
    </script>
</body>
</html>


"""


if __name__ == "__main__":
    main()
