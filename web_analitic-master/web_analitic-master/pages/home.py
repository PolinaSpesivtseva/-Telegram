import streamlit as st
import extra_streamlit_components as stx 

def page_home(theme):
    
    if theme == "Тёмная":
      text_color = "#FFFFFF"
    else:
      text_color = "#112D69"
    st.set_option('client.showErrorDetails', False)

    st.markdown(f"""
    <style>
      .custom-title {{
        text-align: center;
        font-size: 3rem;
        font-family: 'Roboto Mono', monospace;
        color: {text_color};
        margin-bottom: 1rem;
      }}

      @keyframes typing {{
        0%   {{ width: 0ch; }}
        66%  {{ width: 55ch; }}
        100% {{ width: 55ch; }}
      }}
      @keyframes blink-caret {{
        0%,100% {{ border-color: transparent; }}
        50%     {{ border-color: {text_color}; }}
      }}

      .typewriter-container {{
        text-align: center;
        overflow: hidden;      
        margin-bottom: 2rem;
      }}

      .typewriter {{
        display: inline-block;
        font-family: 'Roboto Mono', monospace;
        font-size: 1.75rem;
        white-space: nowrap;
        overflow: hidden;
        border-right: .15em solid {text_color};
        width: 0ch;
        animation:
          typing 4s steps(55, end) infinite,
          blink-caret .75s step-end infinite;
      }}

      .description {{
        text-align: center;
        font-size: 1rem;
        font-family: 'Roboto Mono', monospace;
        color: {text_color};
        max-width: 800px;
        margin: 0 auto 2rem auto;
        line-height: 1.2 !important;  
        white-space: pre-wrap;
      }}
    </style>

    <h1 class="custom-title">Sentigram</h1>

    <div class="typewriter-container">
      <div class="typewriter">
        Анализ новостных событий с помощью машинного обучения
      </div>
    </div>

    <div class="description">
      Данное ПО разрабатывается для исследователей и аналитиков.
      Оно позволяет изучать распространение новостных событий во времени,
      анализировать новостные события с помощью методов машинного обучения,
      проводить визуализацию этих данных, строить временную шкалу,
      отражающую распространение новостных событий.
    </div>
    """, unsafe_allow_html=True)
