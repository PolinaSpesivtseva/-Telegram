import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from utils.auth import authentication_middleware
from utils.tg_stat import prepare_tgstat_data, query_tgstat_api_sync
from utils.excel import posts_to_excel
from utils.config import redirection_url

def page_load_data(is_authenticated):

    st.markdown("""
    <style>
      .page-title {
        text-align: center;
        font-size: 2.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
      }
      .page-desc {
        text-align: center;
        font-size: 1rem;
        max-width: 800px;
        margin: 0 auto 2rem auto;
        line-height: 1.5;
      }
      .alert-success {
        background-color: #e6ffed;
        border-left: 4px solid #00ce94;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        max-width: 800px;
        margin: 1rem auto;
        font-size: 1rem;
      }
      .alert-warning {
        background-color: #fff4e5;
        border-left: 4px solid #f5a623;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        max-width: 800px;
        margin: 1rem auto;
        font-size: 1rem;
      }
      .summary-header {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
      }
      .summary-box {
        max-width: 800px;
        margin: 1rem auto 2rem auto;
        padding: 1rem;
        background-color: #f0f4f8;
        border-radius: 4px;
        font-size: 1rem;
        line-height: 1.5;
      }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
      <h1 class="page-title">Загрузка данных</h1>
      <div class="page-desc">
        Здесь можно загрузить данные с локальной машины, или же загрузить их по фильтрам, 
        воспользовавшись поиском ниже. Далее эти данные будут сохранены в сессии, 
        и по ним можно будет получать инфографику в других вкладках приложения.
      </div>
    """, unsafe_allow_html=True)

    if not is_authenticated:
        st.markdown(
            "<div class='alert-warning'>"
            "⚠ Для классификации используется встроенная модель. Саммари недоступно. "
            "Войдите, чтобы получить доступ к расширенным возможностям."
            "</div>",
            unsafe_allow_html=True
        )
        cols = st.columns([1] * 17)
        with cols[8]:
            st.link_button("Войти", redirection_url)

    st.session_state["selected_model"] = 'ChatGPT' if is_authenticated else 'Rubert'

    upload_tab, search_tab = st.tabs(["📁 Загрузка выборки", "🔍 Поиск через TGStat API"])

    with upload_tab:
        st.subheader("Загрузка выборки в формате TGStat")
        uploaded_xlsx = st.file_uploader("Загрузите файл XLSX из TGStat", type=["xlsx"])
        if uploaded_xlsx is not None:
            with st.spinner("Пожалуйста, подождите, идёт обработка данных…"):
              xlsx = pd.ExcelFile(uploaded_xlsx)
              data = prepare_tgstat_data(xlsx)
            st.session_state["json_result"] = data
            st.markdown(
                "<div class='alert-success'>✅ Данные успешно загружены и обработаны!</div>",
                unsafe_allow_html=True
            )

    with search_tab:
        st.subheader("Поиск постов по параметрам")
        with st.form(key="search_form"):
            tg_stat_api = st.text_input("API-ключ TGStat (опционально)", "")
            key_words  = st.text_input("Ключевые слова", "")
            stop_words = st.text_input("Стоп-слова", "")
            from_date  = st.date_input("Дата начала", datetime.today() - timedelta(days=7))
            to_date    = st.date_input("Дата окончания", datetime.today())
            country    = st.text_input("География каналов", "")
            submitted  = st.form_submit_button("🔍 Найти посты")

            if submitted:
                with st.spinner("Загружаем посты с TGStat API..."):
                    result = query_tgstat_api_sync(
                        q=key_words,
                        minusWords=stop_words,
                        startDate=from_date,
                        endDate=to_date,
                        country=country,
                        api_key=tg_stat_api
                    )
                    if result:
                        st.session_state["json_result"] = result
                        st.markdown(
                            "<div class='alert-success'>✅ Данные успешно получены и сохранены!</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div class='alert-warning'>Не удалось получить данные. Проверьте параметры запроса.</div>",
                            unsafe_allow_html=True
                        )

    if "json_result" in st.session_state:
        if is_authenticated and st.session_state.get("summary"):
            st.markdown("<div class='summary-header'>Краткое содержание по постам:</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='summary-box'>{st.session_state['summary']}</div>",
                unsafe_allow_html=True
            )

        st.download_button(
            label="💾 Скачать посты (JSON)",
            file_name="posts.json",
            mime="application/json",
            data=json.dumps(st.session_state["json_result"], indent=4, ensure_ascii=False)
        )
        st.download_button(
            label="📊 Скачать посты (Excel)",
            file_name="posts.xlsx",
            data=posts_to_excel(st.session_state["json_result"])
        )
