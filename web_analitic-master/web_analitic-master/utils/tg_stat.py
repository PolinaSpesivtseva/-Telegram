import pandas as pd
import numpy as np
import time
import aiohttp
import asyncio
import os
from datetime import datetime
from utils.processing import prepare_enriched_data
import streamlit as st

from utils.sentiment import get_data_sentiment

def prepare_tgstat_data(xlsx):
    df_preview = pd.read_excel(xlsx, sheet_name=0, skiprows=13)  

    df_preview = df_preview.drop(columns=['Тип источника', 'Кол-во подписчиков', 'Реакций', 'Ссылка на публикацию на TGStat'])
    df_preview = df_preview.rename(columns={
        "Дата публикации": "date",
        "Название источника": "channel",
        "Репост из": "fwd_from",
        "Просмотров": "views",
        "Пересылок": "reposts_count",
        "Комментариев": "comments_count",
        "Ссылка на публикацию в Telegram": "url",
        "Текст публикации": "text"
    })

    df_preview["channel"] = df_preview["channel"].str.strip()
    df_preview["text"] = df_preview["text"].str.strip()
    df_preview["fwd_from"] = df_preview["fwd_from"].str.strip().replace({np.nan: None})
    df_preview['date'] = pd.to_datetime(df_preview['date'], format='%d.%m.%Y %H:%M').apply(lambda x: int(time.mktime(x.timetuple())))

    df_preview["id"] = None
    df_preview["channel_id"] = None
    df_preview["id_owner"] = None
    df_preview["avatar"] = ''
    df_preview["text_length"] = df_preview["text"].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    df_preview["comments"] = None
    df_preview["comments"] = df_preview["comments"].apply(lambda x: [] if pd.isna(x) else x)
    df_preview["tg_channel_id"] = None
    df_preview["reactions"] = None
    df_preview["reactions"] = df_preview["reactions"].apply(lambda x: [] if pd.isna(x) else x)
    df_preview["channel_category"] = None
    df_preview["channel_country"] = None
    df_preview["channel_language"] = None

    column_order = [
        "id", "channel_id", "channel", "date", "text", "views", "id_owner", "url",
        "avatar", "text_length", "reposts_count", "comments_count", "comments",
        "reactions", "fwd_from", "tg_channel_id", "channel_category", "channel_country", "channel_language"
    ]
    df_preview = df_preview[column_order]

    data = df_preview.to_dict(orient="records")

    if st.session_state.get("selected_model").lower() == "chatgpt":
        data, summary = asyncio.run(prepare_enriched_data(data))
        st.session_state["summary"] = summary
    else:
        data = get_data_sentiment(data)
        data = data.to_dict(orient='records')

    return data

TGSTAT_TOKEN = 'yourtoken'

def query_tgstat_api_sync(*args, **kwargs):
    data = asyncio.run(query_tgstat_api(*args, **kwargs))

    if st.session_state.get("selected_model") == "ChatGPT":
        data, summary = asyncio.run(prepare_enriched_data(data))
        st.session_state["summary"] = summary
    else:
        data = get_data_sentiment(data)
        data = data.to_dict(orient='records')

    return data

def merge_posts_with_channel_info(api_response: dict) -> list:
    result = []
    channels_map = {ch["id"]: ch for ch in api_response.get("channels", [])}

    for post in api_response.get("items", []):
        ch = channels_map.get(post["channel_id"], {})
        merged = {
            "id": post["id"],
            "channel_id": post["channel_id"],
            "channel": ch.get("title", ""),
            "date": post["date"],
            "text": post.get("text", ""),
            "views": post.get("views", 0),
            "id_owner": "",
            "url": "https://" + post.get("link", ""),
            "avatar": "",
            "text_length": len(post.get("text", "")),
            "reposts_count": post.get("shares_count", 0),
            "comments_count": post.get("comments_count", 0),
            "comments": [],
            "reactions": [],
            "fwd_from": post.get("forwarded_from"),
            "tg_channel_id": post.get("channel_id"),
            "channel_category": ch.get("category", ""),
            "channel_country": ch.get("country", ""),
            "channel_language": ch.get("language", ""),
        }
        result.append(merged)
    return result

async def fetch_tgstat_page(session, params, offset):
    url = "https://api.tgstat.ru/posts/search"
    params["offset"] = offset
    async with session.get(url, params=params) as resp:
        data = await resp.json()
        if data.get("status") == "ok":
            return data["response"]
        return None

async def query_tgstat_api(q, minusWords="", startDate=None, endDate=None, country=None, api_key=None):
    if api_key is None:
        api_key = TGSTAT_TOKEN

    params = {
        "token": TGSTAT_TOKEN,
        "q": q,
        "limit": 50,
        "peerType": "all",
        "hideForwards": 1,
        "hideDeleted": 1,
        "minusWords": minusWords,
        "extended": 1,
        "strongSearch": 0,
        "extendedSyntax": 0,
    }

    country_dict = {
        "Россия": "ru", "Украина": "ua", "Беларусь": "by", "Узбекистан": "uz",
        "Казахстан": "kz", "Иран": "ir", "Киргизия": "kg"
    }

    if startDate:
        params["startDate"] = int(datetime.combine(startDate, datetime.min.time()).timestamp())
    if endDate:
        params["endDate"] = int(datetime.combine(endDate, datetime.max.time()).timestamp())
    if country:
        params["country"] = country_dict.get(country, "")

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_tgstat_page(session, params.copy(), offset) for offset in range(0, 1000, 50)]
        all_pages = await asyncio.gather(*tasks)

    combined_items = []
    combined_channels = {}

    for page in all_pages:
        if page and "items" in page:
            combined_items.extend(page["items"])
        if page and "channels" in page:
            for ch in page["channels"]:
                combined_channels[ch["id"]] = ch

    merged_response = {
        "items": combined_items,
        "channels": list(combined_channels.values())
    }

    json_result = merge_posts_with_channel_info(merged_response)
    return json_result