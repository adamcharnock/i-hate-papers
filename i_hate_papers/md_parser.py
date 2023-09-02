import re
from functools import lru_cache
from hashlib import sha1
from pathlib import Path
from typing import Union


class MarkdownParser:
    """Parses a large markdown file"""

    root: "DocumentTreeNode"

    def __init__(self, path: Path):
        self.path = path

        content = path.read_text()
        node = DocumentTreeNode(source=content, name="DOCUMENT ROOT")
        node.parse()
        self.root = node

    def __str__(self):
        return str(self.root)


class DocumentTreeNode:
    """Pulled from another of my projects. Can likely be heavily simplified"""

    source: list[str]
    # The depth of this heading. The source will contain no headings of this depth or less
    depth: int
    children: list[Union[str, "DocumentTreeNode"]]

    def __init__(
        self,
        source: str | list,
        name="",
        depth: int = 0,
        parent: "DocumentTreeNode" = None,
    ):
        if hasattr(source, "splitlines"):
            source = source.splitlines()

        self.name = name
        self.source = source
        self.depth = depth
        self.parent = parent
        self.children = None

    def parse(self):
        self.children = self._parse(self.source)
        return self

    def _parse(self, source: list[str]) -> list[Union[str, "DocumentTreeNode"]]:
        i = 0
        output = []

        # While we have source lines to parse
        while i < len(source):
            # Get the next line to parse
            line = source[i]
            # How deep is this heading? (indicated by the number of '#' chars)
            # (Will be None if it is not a heading)
            heading_depth = get_heading_depth(line)
            # If this is a heading, and it is adjacent to or higher than the current heading,
            # then extract the content as a subsection
            if heading_depth and heading_depth <= self.depth + 1:
                # Get all the content to the next heading at this depth
                subsection = self._split_text_to_next_heading(source[i:], heading_depth)
                # Get the name of this new subscription (i.e. the heading)
                name = subsection[0].strip("#").strip()
                # Create the subsection using the heading, and all content under that heading
                node = DocumentTreeNode(
                    source=subsection[1:], name=name, depth=heading_depth, parent=self
                )
                # Parse the markdown and append to our list of children
                node.parse()
                output.append(node)
                # Continue iterating, skipping over all the lines we just parsed in the subsection
                i += len(subsection)
            else:
                # This is just plain text, append it to the output and keep on going
                output.append(TextNode(line, depth=self.depth, parent=self))
                i += 1

        return output

    def _split_text_to_next_heading(self, source, depth) -> list[str]:
        subsection = []
        for i, line in enumerate(source):
            heading_depth = get_heading_depth(line)
            if i > 0 and heading_depth and heading_depth <= depth:
                return subsection
            else:
                subsection.append(line)

        return subsection

    def as_markdown(
        self,
        indent=0,
        with_ids=False,
        trim_chars: int = None,
        headings_only=False,
        html_indent=False,
        html_highlight_nodes: dict = None,
    ):
        def _id(l):
            if not with_ids:
                return ""
            if isinstance(l, TextNode):
                return ""
            if l.node_id() == "2bbec0dc9c":
                breakpoint()

            return f" - ID:{l.node_id()}, TOKENS:{l.total_tokens():,}, CHARS:{l.total_chars():,}"

        html_highlight_nodes = html_highlight_nodes or {}
        indent_str = " " * indent * (self.depth - 1)
        out = f"{indent_str}{'#' * self.depth} {self.name}{_id(self)}\n"

        for line in self.children:
            if isinstance(line, TextNode):
                if headings_only:
                    continue
                out_line = f"{indent_str}{line}"
                if trim_chars and len(out_line) > trim_chars:
                    out_line = out_line[:70] + f"{_id(line)}...\n"
                else:
                    out_line += _id(line) + "\n"
            else:
                out_line = (
                    line.as_markdown(
                        indent=indent,
                        with_ids=with_ids,
                        trim_chars=trim_chars,
                        headings_only=headings_only,
                        html_indent=html_indent,
                        html_highlight_nodes=html_highlight_nodes,
                    )
                    + "\n"
                )
                if html_indent:
                    node_id = line.node_id()
                    highlight_css = ""
                    highlight_content = ""

                    if line.node_id() in html_highlight_nodes:
                        highlight_css = (
                            "border-left: solid 5px yellow; padding-left: 10px;"
                        )
                        highlight_content = f"""\n<div style="background: yellow;" >{html_highlight_nodes[node_id]}</div>\n\n"""

                    out_line = f"""\n<div style="margin-left: 20px; {highlight_css}" markdown="1">\n\n{highlight_content}{out_line}</div>\n"""

            out += out_line
        return out

    def __str__(self):
        return self.as_markdown(with_ids=False, trim_chars=None, indent=0)

    def __repr__(self):
        return f"<DTN {self.name} [{', '.join(map(repr, self.children))}]>"

    def node_id(self):
        return node_id(self)

    def walk(self) -> list[Union["TextNode", "DocumentTreeNode"]]:
        yield self
        for child in self.children:
            for c in child.walk():
                yield c

    def total_chars(self):
        return len(str(self))

    def total_words(self):
        return count_words(str(self))

    def total_tokens(self):
        return count_tokens(str(self))

    def path(self):
        return node_path(self)

    @property
    def is_section(self):
        return True

    @property
    def sections(self):
        return [c for c in self.children if c.is_section]


class TextNode:
    def __init__(self, text, depth: int, parent: "DocumentTreeNode"):
        self.text = text
        self.depth = depth
        self.parent = parent

    def node_id(self):
        return node_id(self)

    def walk(self):
        yield self

    def as_markdown(self, **kwargs):
        return self

    def total_chars(self):
        return len(self.text)

    def total_words(self):
        return count_words(self.text)

    def total_tokens(self):
        return count_tokens(self.text)

    def path(self):
        return node_path(self)

    def __str__(self):
        return self.text

    @property
    def is_section(self):
        return False


HEADING_REGEX = re.compile(r"^(#+)")


def get_heading_depth(text: str) -> int:
    match = HEADING_REGEX.match(text)
    if not match:
        return None
    else:
        return len(match.group(0))


def count_words(s: str):
    words = s.split()
    total_words = len([w for w in words if len(w) > 3])
    return total_words


def count_tokens(s: str):
    return int(round(count_words(s) * 0.75))


def node_path(node):
    path = []
    while node.parent:
        path.append(node)
        node = node.parent
    return list(reversed(path))


@lru_cache(maxsize=10_000)
def node_id(node):
    digest_maker = sha1()
    for parent in node.path():
        digest_maker.update(str(parent).encode("utf8"))
    digest_maker.update(str(node).encode("utf8"))
    return digest_maker.hexdigest()[:10]
