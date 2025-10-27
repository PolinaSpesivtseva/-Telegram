import asyncio
import pandas as pd
from utils.sentiment import get_data_sentiment
from utils.summarizer import summarize_with_gpt
from utils.gpt import aclient

async def run_sentiment(data: list, loop) -> pd.DataFrame:
    return await loop.run_in_executor(None, lambda: get_data_sentiment(data))

async def run_summary(data: list, max_chars=20000) -> str:
    texts = []
    char_count = 0
    for item in data:
        txt = item.get("text", "")
        if txt and len(txt.strip()) > 50:
            if char_count + len(txt) > max_chars:
                break
            texts.append(txt.strip())
            char_count += len(txt)
    full_text = "\n\n".join(texts)
    return await summarize_with_gpt(full_text, aclient)

async def prepare_enriched_data(raw_data: list) -> tuple[list, str]:
    loop = asyncio.get_event_loop()
    sentiment_task = asyncio.create_task(run_sentiment(raw_data, loop))
    summary_task = asyncio.create_task(run_summary(raw_data))
    enriched_df, summary = await asyncio.gather(sentiment_task, summary_task)
    return enriched_df.to_dict(orient="records"), summary
