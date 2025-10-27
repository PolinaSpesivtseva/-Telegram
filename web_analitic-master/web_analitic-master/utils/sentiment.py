import streamlit as st
import pandas as pd
import torch
import re
from openai import AsyncOpenAI, RateLimitError
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import asyncio
import numpy as np
import os
from utils.gpt import aclient
st.set_option('client.showErrorDetails', False)

current_file_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_file_path, "rubert-finetuned")


inverse_sentiment_mapping = {0: "neutral",
                             1: "positive",
                             -1: "negative"}

async def a_promp_gpt(question, model="gpt-4o-mini", aclient=None):
    messages = [
        {
            "role": "system",
            "content": (
                "You will be provided with a tweet, and your task is to classify its sentiment "
                "as exactly one of these three labels: 'neutral', 'positive', or 'negative'.\n\n"
                "Important: Return only one of these words exactly with no explanation or extra text.\n"
                "Your output must be strictly 'neutral', 'positive', or 'negative'.\n"
                "Do not add any punctuation, reasoning, or additional words."
            ),
        },
        {"role": "user", "content": question},
    ]
    chat_completion = await aclient.chat.completions.create(
        messages=messages,
        model=model,
    )
    return chat_completion.choices[0].message.content

async def a_croud_gpt(
    df,
    results,
    model="gpt-4o-mini",
    num_executors=50,
    aclient=None
):
    tasks = asyncio.Queue()

    async def worker(tasks, results):
        while not tasks.empty():
            idx, question = await tasks.get()
            print(f"parsing idx {idx}")
            while True:
                try:
                    result = await a_promp_gpt(question, model=model, aclient=aclient)
                    results[idx] = result.lower()
                    df.loc[idx, "prompt"] = result.lower()
                    print(f"finished idx {idx}")
                    break
                except RateLimitError:
                    print(f"sleeping for {idx}")
                    await asyncio.sleep(60)
                except:
                    results[idx] = None
                    print(f"bad query for {idx}")
                    break

    for row in df[df["prompt"].isna()].iterrows():
        await tasks.put((row[0], row[1]["text"]))

    workers = [
        asyncio.create_task(worker(tasks, results)) for _ in range(num_executors)
    ]
    await asyncio.gather(*workers)
    return results

async def query_gpt(data, aclient):
    data["prompt"] = None
    model = "gpt-4o-mini"
    results = [None] * len(data)
    labels = await a_croud_gpt(
        data,
        results,
        model=model,
        num_executors=20,
        aclient=aclient
    )
    return labels

def clean_text(input_text):
    phrases = []
    with open("del_texts.txt", 'r', encoding='utf-8') as file:
        phrases = file.read().splitlines()
    cleaned_text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+', '', input_text)
    cleaned_text = re.sub(r'[\u2000-\u206F\u2E00-\u2E7F]+', '', cleaned_text)
    cleaned_text = re.sub(r'http[s]?://\S+|www\.\S+|t\.me/\S+', '', cleaned_text)
    cleaned_text = re.sub(r'(Подпишись на|Подписывайся|Читайте нас|Поддержать телеграм-канал|Подробнее в|Подробнее на|Подписывайтесь|Подписаться|Предложить новость).*', '', cleaned_text)
    for phrase in phrases:
        cleaned_text = re.sub(re.escape(phrase), '', cleaned_text)
    return cleaned_text.replace('\n', ' ')

def clean_data(data):
    data = pd.json_normalize(data)
    data['text'] = data['text'].apply(clean_text)
    return data

def rubert_inference(data, tokenizer, model, device):
    texts = data.text.tolist()
    batch_size = 64
    results = np.array([], dtype=int)

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:min(i+batch_size, len(texts))]

        encodings = tokenizer(batch_texts, truncation=True, padding=True,
                              max_length=512, return_tensors="pt")

        input_ids = encodings['input_ids'].to(device)
        attention_mask = encodings['attention_mask'].to(device)

        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

        probs = torch.nn.functional.softmax(logits, dim=-1)
        preds = torch.argmax(probs, dim=-1).cpu().numpy()
        preds = np.where(preds == 2, -1, preds)

        results = np.append(results, preds)

    data['numeric_sentiment'] = results
    data['sentiment'] = [inverse_sentiment_mapping[res] for res in results]

    return data

def get_data_sentiment(data):
    
    data = clean_data(data)

    selected_model = st.session_state.get('selected_model', 'Rubert')

    if selected_model == 'chatgpt':

        results = asyncio.run(query_gpt(data, aclient))
        sentiment_mapping = {v: k for k, v in inverse_sentiment_mapping.items()}
        numeric_sentiment_list = [sentiment_mapping[sentiment] for sentiment in results]
        data = data.assign(numeric_sentiment=numeric_sentiment_list)
        data = data.assign(sentiment=results)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.to(device)

        data = rubert_inference(data, tokenizer, model, device)

    return data