import logging
from hashlib import sha1

import openai
from openai import InvalidRequestError

from i_hate_papers.settings import CACHE_DIR

logger = logging.getLogger(__name__)


def openai_request(question, text, temperature, model):
    """Sends a request to a openai large language model."""
    kwargs = dict(
        model=model,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""{question}:\n\n{text}"""}
        ],
        temperature=temperature,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.0,
        timeout=5,
    )
    logger.debug(f"Calling ChatCompletion API: {kwargs=}")
    try:
        response = openai.ChatCompletion.create(**kwargs)
        return response["choices"][0]["message"]["content"].strip()
    except InvalidRequestError as e:
        if e.error.code == "context_length_exceeded":
            logger.error(f"Failed to summarise some content: {e.error.message}")
            return "Content too large, failed to summarise"
        else:
            raise


def summarise_latex(
    content: str,
    detail_level: int,
    force=False,
    model="gpt-3.5-turbo",
):
    detail_request = {
        0: "Assume the reader has no grasp of the subject. Do not go into detail, simplify advanced terminology. ",
        1: "Assume the reader has only a high-level understanding of the subject. ",
        2: "Assume the reader has has a detailed understanding of the subject. Go into detail where necessary. ",
    }[detail_level]

    prompt = (
        f"Summarise the following section. "
        f"{detail_request} "
        f"Format your response using markdown syntax:"
    )
    temperature = 0.3

    cache_hash = sha1((prompt + content + str(temperature) + model).encode("utf8"))
    cache_path = CACHE_DIR / "summaries" / cache_hash.hexdigest()
    cache_path.parent.mkdir(exist_ok=True, parents=True)

    if cache_path.exists() and not force:
        logger.debug(f"Summary found in cache: {cache_path}")
        return cache_path.read_text("utf8")

    logger.debug(
        f"Summary not found in cache. Will summarise and store in cache at: {cache_path}"
    )
    response = openai_request(
        prompt,
        content,
        temperature=temperature,
        model=model,
    )
    cache_path.write_text(response, "utf8")
    return response


def extract_glossary(
    content: str,
    force=False,
    model="gpt-3.5-turbo",
):
    """Extract a glossary from the given content"""
    prompt = (
        f"Create a long & comprehensive glossary of unusual terminology given the following markdown-formatted content. "
        f"Format results using markdown. Terms must be bold, term definitions must not be bold. "
        f"Term definitions must be a single line. "
        f"Do not include any introductory text or headings."
    )
    temperature = 0

    cache_hash = sha1((prompt + content + str(temperature) + model).encode("utf8"))
    cache_path = CACHE_DIR / "key-terms" / cache_hash.hexdigest()
    cache_path.parent.mkdir(exist_ok=True, parents=True)

    if cache_path.exists() and not force:
        logger.debug(f"Key terms found in cache: {cache_path}")
        markdown = cache_path.read_text("utf8")
    else:
        logger.debug(
            f"Key terms not found in cache. Will summarise and store in cache at: {cache_path}"
        )
        response = openai_request(
            prompt,
            content,
            temperature=temperature,
            model=model,
        )
        cache_path.write_text(response, "utf8")
        markdown = response

    lines = [m for m in markdown.splitlines() if m.strip() and not m.startswith("#")]
    sorted(lines)
    return "\n\n".join(lines)
