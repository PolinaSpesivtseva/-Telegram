import streamlit as st
import io
import pandas as pd

@st.cache_data(ttl=3600, max_entries=1000)
def posts_to_excel(posts, comments=None):
    in_memory_excel = io.BytesIO()
    with pd.ExcelWriter(in_memory_excel) as writer:
        df = pd.DataFrame(posts)
        df["reactions"] = df["reactions"].astype(str)
        df.date = pd.to_datetime(df.date, unit='s')
        df.to_excel(writer, sheet_name='posts')
        if comments is not None:
            df = pd.DataFrame(comments)
            df["reactions"] = df["reactions"].astype(str)
            df.date = pd.to_datetime(df.date, unit='s')
            df.to_excel(writer, sheet_name='comments')
    return in_memory_excel.getvalue()