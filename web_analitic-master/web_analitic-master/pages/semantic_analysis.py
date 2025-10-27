import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

@st.cache_data(ttl=3600, max_entries=1000)
def _prepare_data(raw_records):
    df = pd.DataFrame(raw_records)

    bar = df.sentiment.value_counts().reset_index()
    bar.columns = ['sentiment','count']
    if not bar.empty:
        bar['proportion'] = bar['count'] / bar['count'].sum()
        to_ru = {'positive':"Позитивный",'negative':"Негативный",'neutral':"Нейтральный"}
        bar['sentiment'] = bar['sentiment'].map(lambda x: to_ru.get(x,"Неизвестно"))

    df_sorted = df.sort_values('date')
    n_bins = min(50, len(df_sorted))
    df_sorted['bin'] = pd.cut(df_sorted.date, bins=n_bins)

    avg = (
        df_sorted
        .groupby('bin')['numeric_sentiment']
        .mean()
        .reset_index()
        .dropna()
    )
    channels = (
        df_sorted
        .groupby('bin')['channel']
        .apply(lambda lst: list(set(lst)))
        .reset_index(name='channels')
    )
    avg = avg.merge(channels, on='bin')
    avg['id'] = np.arange(len(avg))

    return bar, avg


def page_semantic_analysis(raw_records: list, is_authenticated: bool):
    """
    Рисует две диаграммы:
      - распределение sentiment
      - динамику numeric_sentiment во времени
    `raw_records` — список словарей с ключами
      ['date', 'sentiment', 'numeric_sentiment', 'channel', …]
    `is_authenticated` — признак, какую модель писать внизу
    """

    if not raw_records:
        st.error("Нет данных для семантического анализа")
        return

    bar_data, time_data = _prepare_data(raw_records)

    st.header("Гистограмма распределения семантической окраски анализируемых постов")
    if not bar_data.empty:
        fig_bar = px.bar(
            bar_data,
            x='sentiment',
            y='proportion',
            color='sentiment',
            color_discrete_map={
                'Негативный': '#f35532',
                'Позитивный': '#00ce94',
                'Нейтральный': '#676dff'
            },
            labels={'sentiment': "Окрас", 'proportion': 'Доля (%)'},
            hover_data={'count':True}
        )
        scale = 1.5
        fig_bar.update_layout(
            width = int(700 * scale),
            height= int(500 * scale),
            showlegend=False,
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.plotly_chart(fig_bar, use_container_width=False)
    else:
        st.info("Слишком мало данных для построения гистограммы.")

    st.header("Эмоциональный окрас новостей во времени")
    if not time_data.empty:
        fig_time = go.Figure()
        # линия
        fig_time.add_trace(go.Scatter(
            x=time_data['id'],
            y=time_data['numeric_sentiment'],
            mode='lines',
            line=dict(shape='spline', color='grey'),
            showlegend=False
        ))
        fig_time.add_trace(go.Scatter(
            x=time_data['id'],
            y=time_data['numeric_sentiment'],
            mode='markers',
            marker=dict(
                size=8,
                color=time_data['numeric_sentiment'],
                colorscale=px.colors.diverging.RdYlGn,
                cmin=-1, cmax=1,
                colorbar=dict(title="", outlinewidth=0, tickvals=[])
            ),
            customdata=time_data['channels'],
            hovertemplate="<b>Каналы:</b> %{customdata}<br>Окрас: %{y:.2f}",
            showlegend=False
        ))
        for y_val, clr in [(-1,'red'),(0,'yellow'),(1,'green')]:
            fig_time.add_shape(
                type='line',
                x0=time_data['id'].min(), x1=time_data['id'].max(),
                y0=y_val, y1=y_val,
                line=dict(color=clr, width=2, dash='dash')
            )
        bins = time_data['bin'].tolist()
        labels = [
            datetime.datetime.fromtimestamp(
                int((interval.left+interval.right)//2)
            ).strftime("%d.%m.%Y %H:%M")
            for interval in bins
        ]
        tick_idx = list(range(0, len(labels), max(1,len(labels)//10)))
        fig_time.update_layout(
            width=1000, height=500,
            yaxis=dict(
                title="Окрас",
                tickvals=[-1,0,1],
                ticktext=["негативный","нейтральный","позитивный"],
                showgrid=True
            ),
            xaxis=dict(
                title="Время",
                tickvals=[time_data['id'][i] for i in tick_idx],
                ticktext=[labels[i] for i in tick_idx],
                showgrid=True
            )
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("Слишком мало данных для построения временного графика.")

    st.markdown("---")
    model_name = "ChatGPT o4-mini" if is_authenticated else "RUbert"
    st.write(f"Используемая модель: **{model_name}**")
