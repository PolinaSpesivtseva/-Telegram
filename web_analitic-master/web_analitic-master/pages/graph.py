import streamlit as st
import streamlit.components.v1 as components
import json
from pathlib import Path

def page_graph():
    
    posts = st.session_state.get("json_result", [])
    posts_json = json.dumps(posts)

    html = f"""
    <style>
      html, body {{
        margin: 0; padding: 0; height: 100%; overflow: hidden;
      }}
      /* контейнер для sigma */
      #graph-container {{
        position: absolute;
        top: 0; left: 0;
        right: 300px; /* уступаем место под панель */
        bottom: 0;
        background: #f5f5f5;
        z-index: 0;
      }}
      /* правая панель управления */
      #sidebar {{
        position: fixed;
        top: 0; right: 0;
        width: 300px; height: 100vh;
        background: #ffffff;
        border-left: 1px solid #ddd;
        padding: 1rem;
        box-sizing: border-box;
        overflow-y: auto;
        z-index: 1;
        font-family: 'Roboto Mono', monospace;
        color: #112D69;
      }}
      #sidebar h2 {{
        margin-top: 0;
        font-size: 1.1rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
      }}
      #sidebar label {{
        display: block;
        margin-bottom: 0.5rem;
        cursor: pointer;
      }}
      #statistics {{
        margin-top: 2rem;
      }}
      #statistics .stat {{
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
      }}
      /* Info-box */
      #info-box {{
        position: fixed;
        top: 1rem;
        left: 1rem;
        width: 300px;
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        font-family: 'Roboto Mono', monospace;;
        font-size: 0.9rem;
        color: #112D69;
        display: none;
        z-index: 2;
        overflow: hidden;
    }}
        #info-box .info-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f0f0f0;
        padding: 0.5rem 1rem;
        border-bottom: 1px solid #ddd;
    }}
    #info-box .info-header .title {{
        font-weight: bold;
        font-size: 1rem;
    }}
    #info-box .info-header .close-btn {{
        background: none;
        border: none;
        font-size: 1.2rem;
        line-height: 1;
        cursor: pointer;
    }}
    #info-box .info-content {{
        padding: 1rem;
    }}
    #info-box .info-row {{
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
    }}
    #info-box .info-row:last-child {{
        margin-bottom: 0;
    }}
    #info-box .info-row .icon {{
        width: 1.25rem;
        text-align: center;
        margin-right: 0.5rem;
        font-size: 1.1rem;
    }}
    #info-box .info-row .label {{
        font-weight: 500;
        margin-right: 0.25rem;
    }}
    #info-box .info-row .value a {{
        color: #0366d6;
        text-decoration: none;
        word-break: break-all;
    }}
    </style>

    <div id="graph-container"></div>

    <div id="sidebar">
      <h2>🛠️Управление</h2>
      <div id="sentiment-filters">
        <strong>Фильтр по сентименту:</strong>
        <label><input type="checkbox" value="positive" checked> 🟢Позитив (<span id="count-pos">0</span>)</label>
        <label><input type="checkbox" value="neutral" checked> 🔵Нейтрал (<span id="count-neu">0</span>)</label>
        <label><input type="checkbox" value="negative" checked> 🔴Негатив (<span id="count-neg">0</span>)</label>
      </div>

      <div id="statistics">
        <h2>Статистика</h2>
        <div class="stat">📍Узлов: <span id="stats-nodes">0</span></div>
        <div class="stat">🔗Связей: <span id="stats-edges">0</span></div>
      </div>
    </div>

    <div id="info-box">
    <div class="info-header">
        <span class="title">ℹ️ Информация</span>
        <button class="close-btn" id="info-close">&times;</button>
    </div>
    <div class="info-content" id="info-content">
    </div>
    </div>

    <script type="module">
      import Graph from 'https://cdn.skypack.dev/graphology@0.21.1';
      import forceAtlas2 from 'https://cdn.skypack.dev/graphology-layout-forceatlas2@0.10.1';
      import Sigma from 'https://cdn.skypack.dev/sigma@2.3.0';

      const posts = {posts_json};
      const SENTIMENT_COLORS = {{
        negative: "#ff3333",
        neutral:  "#3366cc",
        positive:"#33cc33",
        default: "#888888"
      }};

      let countPos = 0, countNeu = 0, countNeg = 0;

      // 1) Создание графа
      const graph = new Graph();
      posts.forEach(p => {{
        const src = p.fwd_from, tgt = p.channel, s = p.sentiment;
        const color = s ? SENTIMENT_COLORS[s] : SENTIMENT_COLORS.default;

        // добавляем целевую ноду
        if (tgt) {{
          if (!graph.hasNode(tgt)) {{
            graph.addNode(tgt, {{
              label: tgt,
              url: p.url,
              date: p.date,
              views: p.views,
              cnt_rep: p.reposts_count,
              cnt_com: p.comments_count,
              size: 4,
              color: color,
              sentiment: s,
              channel_category: p.channel_category,
              channel_country: p.channel_caountry,
              x: Math.random(),
              y: Math.random()
            }});
          }} else {{
            graph.mergeNodeAttributes(tgt, {{
              url: p.url,
              date: p.date,
              views: p.views,
              cnt_rep: p.reposts_count,
              cnt_com: p.comments_count,
              channel_category: p.channel_category,
              channel_country: p.channel_caountry,
            }});
          }}
        }}

        // добавляем исходную ноду и ребро
        if (src && src !== tgt) {{
          if (!graph.hasNode(src)) {{
            graph.addNode(src, {{
              label: src,
              size: 4,
              color: SENTIMENT_COLORS.default,
              sentiment: null,
              x: Math.random(),
              y: Math.random()
            }});
          }}
          if (!graph.hasEdge(src, tgt)) {{
            graph.addEdge(src, tgt, {{
              color: "#888",
              size: 1
            }});
          }}
        }}
      }});

      // динамический размер узлов
      graph.forEachNode(n => {{
        const d = graph.outDegree(n);
        graph.setNodeAttribute(n, "size", Math.min(10, Math.max(4, d + 4)));
      }});

      // вес для ForceAtlas2
      graph.forEachEdge((e, attr) => {{
        graph.setEdgeAttribute(e, "weight", 0.1);
      }});

      // 2) Считаем исходные количества сентиментов
      graph.forEachNode(node => {{
        const s = graph.getNodeAttribute(node, "sentiment");
        if (s === "positive") countPos++;
        else if (s === "neutral") countNeu++;
        else if (s === "negative") countNeg++;
      }});
      document.getElementById("count-pos").textContent = countPos;
      document.getElementById("count-neu").textContent = countNeu;
      document.getElementById("count-neg").textContent = countNeg;

      // 3) ForceAtlas2
      forceAtlas2.assign(graph, {{ iterations: 200, scalingRatio: 10 }});

      // 4) Отображение статистики
      document.getElementById("stats-nodes").textContent = graph.order;
      document.getElementById("stats-edges").textContent = graph.size;

      // 5) Рендерим Sigma.js
      const active = new Set(["positive","neutral","negative","default"]);
      const renderer = new Sigma(graph, document.getElementById("graph-container"), {{
        renderLabels: false,
        nodeReducer: (node, data) => {{
          const s = graph.getNodeAttribute(node, "sentiment") || "default";
          return active.has(s) ? data : {{ ...data, hidden: true }};
        }},
        edgeReducer: (edge, data) => {{
          const s1 = graph.getNodeAttribute(graph.source(edge), "sentiment") || "default";
          const s2 = graph.getNodeAttribute(graph.target(edge), "sentiment") || "default";
          return (active.has(s1) && active.has(s2))
            ? data
            : {{ ...data, hidden: true }};
        }}
      }});

      // 6) Привязываем фильтры
      document.querySelectorAll("#sentiment-filters input").forEach(ch => {{
        ch.addEventListener("change", () => {{
          if (ch.checked) active.add(ch.value);
          else active.delete(ch.value);
          renderer.refresh();
        }});
      }});

      // 7) Info-box при клике
      const info = document.getElementById("info-box");
      const infoContent = document.getElementById("info-content");
      const closeBtn = document.getElementById("info-close");
      closeBtn.addEventListener("click", () => {{
        info.style.display = "none";
      }});
      let cur = null, shown = false;
      renderer.on("clickNode", ({{ node }}) => {{
        const a = graph.getNodeAttributes(node);
        if (cur === node && shown) {{
          info.style.display = "none"; shown = false;
        }} else {{
          cur = node; shown = true;
          infoContent.innerHTML = `
            <div class="info-row">
                <div class="icon">👤</div>
                <div class="label">Канал:</div>
                <div class="value">${{a.label}}</div>
            </div>
            <div class="info-row">
                <div class="icon">🔗</div>
                <div class="label">Ссылка:</div>
                <div class="value"><a href="${{a.url}}" target="_blank">${{a.url}}</a></div>
            </div>
            <div class="info-row">
                <div class="icon">📅</div>
                <div class="label">Дата:</div>
                <div class="value">${{new Date(a.date * 1000).toLocaleString()}}</div>
            </div>
            <div class="info-row">
                <div class="icon">👀</div>
                <div class="label">Просмотров:</div>
                <div class="value">${{a.views}}</div>
            </div>
            <div class="info-row">
                <div class="icon">🔁</div>
                <div class="label">Репостов:</div>
                <div class="value">${{a.cnt_rep}}</div>
            </div>
            <div class="info-row">
                <div class="icon">💬</div>
                <div class="label">Комментариев:</div>
                <div class="value">${{a.cnt_com}}</div>
            </div>
            <div class="info-row">
                <div class="icon">📂</div>
                <div class="label">Категория канала:</div>
                <div class="value">${{a.channel_category}}</div>
            </div>
            <div class="info-row">
                <div class="icon"> 🌍 </div>
                <div class="label">Страна канала:</div>
                <div class="value">${{a.channel_country}}</div>
            </div>
            `;
          info.style.display = "block";
        }}
      }});
    </script>
    """

    components.html(html, height=800, scrolling=False)


