from hashlib import sha1

import openai

from i_hate_papers.settings import CACHE_DIR


def openai_request(question, text, temperature):
    """Sends a request to a openai large language model."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""{question}:\n\n{text}"""}
        ],
        temperature=temperature,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.0,
    )
    return response["choices"][0]["message"]["content"].strip()


def summarise_latex(title: str, content: str, force=False):
    cache_path = CACHE_DIR / "summaries" / sha1(content.encode("utf8")).hexdigest()
    cache_path.parent.mkdir(exist_ok=True, parents=True)

    if cache_path.exists() and not force:
        return cache_path.read_text("utf8")

    response = openai_request(
        (
            "Summarise the following section for someone with a only high-level understanding of "
            "the subject matter. Go into detail where necessary. Format your response using markdown syntax:"
        ),
        content,
        temperature=0.3,
    )
    cache_path.write_text(response, "utf8")
    return f"##{title}\n\n" f"{response}\n\n"
