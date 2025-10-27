from openai import AsyncOpenAI
from utils.gpt import aclient

async def summarize_with_gpt(text: str, aclient: AsyncOpenAI, model="gpt-4o-mini") -> str:
    prompt = (
        "Ты — ассистент, который составляет краткое описание события на основе телеграм-постов.\n"
        "Вот посты на заданную тему. Сделай связное и сжатое описание на основе представленных сообщений:\n\n"
        + text
    )

    messages = [
        {"role": "system", "content": "Ты создаешь краткие, объективные резюме на основе группы постов."},
        {"role": "user", "content": prompt}
    ]

    response = await aclient.chat.completions.create(
        model=model,
        messages=messages,
        stop=["\n\n"],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
