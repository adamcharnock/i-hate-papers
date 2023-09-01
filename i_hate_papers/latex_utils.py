import re
from pathlib import Path


def process_latex_content(content: str, split_at="section") -> (str, list[str]):
    """Extract sections from latex file.

    This function takes in the path to a latex file and processes it. The function reads the file, removes all the latex commands, comments, and align environment. Then, it splits the file at the given 'split_at' command (default = "section") and returns a dictionary with the title of the split as the key and the text as the value.

    Credit to: https://github.com/fjosw/sumtex
    """
    raw_data = content

    tmp_data = raw_data
    tmp_data = tmp_data[: tmp_data.find("\n\\appendix")]
    tmp_data = tmp_data[: tmp_data.find("\n\\end{document}")]

    title_matches = re.search(r"\\title\{([^}]*)\}", raw_data)
    if title_matches:
        title = title_matches.group(1)
    else:
        title = "[Unknown Title]"

    tmp_data = re.sub(r"\\cite\{([^}]*)\}", "", tmp_data)
    tmp_data = re.sub(r"\\label\{([^}]*)\}", "", tmp_data)
    tmp_data = re.sub(r"\\ref\{([^}]*)\}", "", tmp_data)
    tmp_data = re.sub(r"\\cref\{([^}]*)\}", "", tmp_data)
    tmp_data = re.sub(
        r"\\begin{align}([^}]*)\\end{align}", "", tmp_data, flags=re.DOTALL
    )
    tmp_data = re.sub(
        r"\\begin{figure}([^}]*)\\end{figure}", "", tmp_data, flags=re.DOTALL
    )
    tmp_data = re.sub(r"\\begin{pyin}([^}]*)\\end{pyin}", "", tmp_data, flags=re.DOTALL)
    tmp_data = re.sub(r"^%.*\n?", "", tmp_data, flags=re.MULTILINE)

    for format_name in ["texttt", "textbf", "textit", "mathrm"]:
        tmp_data = re.sub(rf"\\{format_name}{{([^}}]*)}}", "\\1", tmp_data)

    section_starts = [
        i for i in range(len(tmp_data)) if tmp_data.startswith(rf"\{split_at}{{", i)
    ]
    section_starts.append(-1)

    sections = {}

    for start, stop in zip(section_starts[:-1], section_starts[1:]):
        section_text = tmp_data[start:stop]
        section_title = (
            re.search(rf"\\{split_at}\{{([^}}]*)\}}", section_text).group(1).strip()
        )

        for sec_name in ["section", "subsection", "paragraph"]:
            section_text = re.sub(rf"\\{sec_name}{{([^}}]*)}}", "\\1", section_text)

        sections[section_title] = section_text

    return title, sections
