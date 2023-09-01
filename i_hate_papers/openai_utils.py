from hashlib import sha1

import openai

from i_hate_papers.settings import CACHE_DIR


def openai_request(question, text, temperature, model):
    """Sends a request to a openai large language model."""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""{question}:\n\n{text}"""}
        ],
        temperature=temperature,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.0,
        timeout=5,
    )
    return response["choices"][0]["message"]["content"].strip()


def summarise_latex(
    title: str, content: str, detail_level: int, force=False, model="gpt-3.5-turbo"
):
    detail_request = {
        0: "Assume the reader has no grasp of the subject. Do not go into detail, simplify advanced terminology. ",
        1: "Assume the reader has only a high-level understanding of the subject. ",
        2: "Assume the reader has has a detailed understanding of the subject. Go into detail where necessary. ",
    }[detail_level]

    prompt = f"Summarise the following section.{detail_request} Format your response using markdown syntax:"
    temperature = 0.3

    cache_hash = sha1((prompt + content + str(temperature) + model).encode("utf8"))
    cache_path = CACHE_DIR / "summaries" / cache_hash.hexdigest()
    cache_path.parent.mkdir(exist_ok=True, parents=True)

    if cache_path.exists() and not force:
        return cache_path.read_text("utf8")

    response = openai_request(
        prompt,
        content,
        temperature=temperature,
        model=model,
    )
    summary = f"## {title}\n\n{response}\n\n"
    cache_path.write_text(summary, "utf8")
    return summary
