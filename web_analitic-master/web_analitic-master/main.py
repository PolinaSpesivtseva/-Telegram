import streamlit as st
from utils.auth import authentication_middleware
from streamlit_navigation_bar import st_navbar

import pages as pg

from utils.config import DEBUG
import os

st.set_page_config(
    page_title="Sentigram",
    page_icon="static/HSE_logo.ico",
    initial_sidebar_state="collapsed",
    layout="wide",
)

theme = st.sidebar.radio(
    "Тема",
    options=["Светлая", "Тёмная"],
    index=0
)
st.sidebar.markdown("---") 

pages = ["Загрузка данных", "Визуализация данных", "Семантический анализ", "Аккаунт"]
parent_dir      = os.path.dirname(os.path.abspath(__file__))
light_logo_path = os.path.join(parent_dir, "static/image_logo.svg")
dark_logo_path  = os.path.join(parent_dir, "static/black_logo.svg")
logo_path = light_logo_path if theme == "Светлая" else dark_logo_path
urls = {"Аккаунт": "http://localhost:8002/accounts/email" if DEBUG else "/accounts/email/"}

is_authenticated = authentication_middleware()

if theme == "Тёмная":
    bg_app       = "#333333"
    text_color   = "#FFFFFF"
    nav_bg       = "#333333"
    nav_border   = "#FF6D01"
    active_color = "#FF6D01"

    bg_block     = "#2D2D2D"
    shadow       = "rgba(0,0,0,0.5)"
    input_bg     = "#2D2D2D"
    input_border = "#444444"

    info_bg      = "#FF6D01"
    info_text    = "#FFFFFF"

    btn_bg       = "#FF6D01"
    btn_color    = "#333333"
    active_bg    = "transparent"
else:
    bg_app       = "#f0f2f6"
    text_color   = "#112D69"
    nav_bg       = "#f0f0f0"
    nav_border   = "#112D69"
    active_color = "#112D69"

    bg_block     = "#ffffff"
    shadow       = "rgba(0,0,0,0.1)"
    input_bg     = "#ffffffcc"
    input_border = "#ddd"

    info_bg      = "#112D69"
    info_text    = "#ffffff"

    btn_bg       = "#112D69"
    btn_color    = "#ffffff"
    active_bg    = "#112d694d"

st.markdown(f"""
<link
  href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap"
  rel="stylesheet"
/>
<style>
  [data-testid="stAppViewContainer"] {{
    background-color: {bg_app};
    color: {text_color};
  }}
  [data-testid="stBlock"] {{
    background-color: {bg_block};
    box-shadow: 0 4px 12px {shadow};
  }}
  [data-testid="stAppViewContainer"] h2 {{
    color: {text_color} !important;
  }}
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stDateInput"] input {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 1px solid {input_border} !important;
  }}
  [data-testid="stAppViewContainer"] h2 {{
  color: {text_color} !important;
  }}
  [data-testid="stAppViewContainer"] label[for^="upload"] {{
    color: {text_color} !important;
  }}
  [data-testid="stAppViewContainer"] .stSpinner {{
    color: {text_color} !important;
  }}
  [data-testid="stAppViewContainer"] label[for^="text_input"] {{
    color: {text_color} !important;
  }}
  [data-testid="stAppViewContainer"] input::placeholder {{
    color: {text_color} !important;
  }}
  h1 {{
    color: {active_color};
    text-decoration: underline {active_color};
    text-underline-offset: 0.4em;
  }}
  nav[role="navigation"] {{
    background-color: {nav_bg} !important;
    border-bottom: 2px solid {nav_border};
  }}
  a, a:hover {{
    color: {text_color} !important;
  }}
  .navbar-item-active {{
    color: {active_color} !important;
    background-color: {active_bg} !important;
  }}
  .info-box {{
    background-color: {info_bg} !important;
    color: {info_text} !important;
    padding: 1rem;
    border-radius: 8px;
  }}
  button[class*="stButton"] > div {{
    background-color: {btn_bg} !important;
    color: {btn_color} !important;
  }}
  .stMarkdown, .stMarkdown * {{
    color: {text_color} !important;
  }}
  .stHeader, .stHeader * {{
    color: {text_color} !important;
  }}
  .stMarkdown h1,
  .stMarkdown h2,
  .stMarkdown h3,
  .stMarkdown h4,
  .stMarkdown h5,
  .stMarkdown h6 {{
    color: {text_color} !important;
  }}
  .stMarkdown p,
  .stMarkdown li,
  .stMarkdown blockquote {{
    color: {text_color} !important;
  }}
</style>
""", unsafe_allow_html=True)

styles = {
    "nav": {
        "background-color": nav_bg,
        "border-bottom":    f"4px solid {nav_border}",
        "width":            "100%",
        "box-sizing":       "border-box",
        "display":          "flex",
        "align-items":      "left",
        "justify-content":  "left",
        "height":           "4rem",
        "position":         "sticky",
        "top":              "0",
        "z-index":          "1000",
    },
    "ul": {
        "display": "flex",
        "gap":     "2rem",
        "margin":  "0",
        "padding": "0",
    },
    "li": {
        "list-style":   "none",
        "display":      "inline-flex",
        "align-items":  "left",
    },
    "img": {
        "height": "10rem",
        "width":  "10rem",
        "padding-right": "1rem",
    },
    "span": {
        "color":           text_color,
        "padding":         "1rem 2.5rem",
        "font-size":       "1.25rem",
        "font-family":     "'Roboto Mono', monospace",
        "font-weight":     "700",
        "text-decoration": "none",
    },
    "active": {
        "background-color": active_bg,
        "color":            active_color,
        "font-weight":      "700",
        "padding":          "1rem 2.5rem",
        "font-size":        "1.25rem",
    },
}

options = {"show_menu": False, "show_sidebar": True}

page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    options=options,
)

functions = {
    "Home": lambda: pg.page_home(theme),
    "Загрузка данных": lambda: pg.page_load_data(is_authenticated),
    "Визуализация данных": lambda: pg.page_graph(),
    "Семантический анализ": lambda: pg.page_semantic_analysis(
        st.session_state.get("json_result", []),
        is_authenticated
    )
}

if page in functions:
    functions[page]()
