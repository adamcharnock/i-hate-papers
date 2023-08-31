import openai


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
