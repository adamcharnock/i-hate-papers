import logging
import tarfile
from pathlib import Path
from tarfile import TarInfo

import arxiv

from i_hate_papers.settings import CACHE_DIR

PATH = "src/arXiv_src_{id1}_{id2}.tar"

logger = logging.getLogger(__name__)


def download_paper(arxiv_id: str, force=False) -> Path:
    """Download the given arXiv paper, returning from cache if possible"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    download_to = CACHE_DIR / f"{arxiv_id}.tar"
    if download_to.exists() and not force:
        logger.debug(f"Paper source found in cache. {arxiv_id=}")
        return download_to

    logger.debug(
        f"Paper source not found in cache. Will download and store in cache. {arxiv_id=}"
    )
    paper = next(arxiv.Search(id_list=[arxiv_id]).results())
    paper.download_source(dirpath=str(download_to.parent), filename=download_to.name)

    return download_to


def get_file_list(arxiv_id: str) -> list[tuple[str, int]]:
    """Get the list of source files within the arXiv paper"""
    tar_path = download_paper(arxiv_id)

    out = []
    with tarfile.open(tar_path) as f:
        member: TarInfo
        for member in f.getmembers():
            out.append((member.name, member.size))

    out = sorted(out, key=lambda f: (f[0].endswith(".tex"), f[1], f[0]), reverse=True)
    return out


def get_file_content(arxiv_id: str, file_name: str) -> str:
    """Get the source file content for the given arXiv paper"""
    tar_path = download_paper(arxiv_id)

    with tarfile.open(tar_path) as f:
        return f.extractfile(file_name).read().decode("utf8")
