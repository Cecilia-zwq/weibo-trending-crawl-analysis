import json
import streamlit as st
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins
import mpld3
import streamlit.components.v1 as components
plt.rcParams.update({'font.size': 8})

with open("./genre_count.json", "r", encoding="utf8") as f:
    genre_count = json.load(f)

option = st.selectbox(
    "微博热搜分类占比",
    ("所有分类占比", "社会时事", "影视剧", "商业", "娱乐", "生活", "教育"))

container = st.container()
# if option == "所有分类占比":
# 绘制大分类下的count饼状图
categories = list(genre_count.keys())
counts = [values['count'] for values in genre_count.values()]
fig_all = plt.figure(figsize=(8, 6))
plt.subplot(121)
plt.pie(counts, labels=categories, autopct='%1.1f%%')
plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
plt.title('微博热搜分类占比')

if option != "所有分类占比":
    categories = [cat for cat in genre_count[option].keys() if cat != "count"]
    counts = [genre_count[option][cat] for cat in categories]
    # fig_cat = plt.figure(figsize=(6, 6))
    plt.subplot(122)
    plt.pie(counts, labels=categories, autopct='%1.1f%%')
    plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
    plt.title(f'{option}占比')
else:
    plt.subplot(122)
    plt.bar(categories, counts)
    plt.title(f'{option}柱状图')
    plt.tight_layout()

# st.pyplot(fig_all)
# fig_html = mpld3.fig_to_html(fig_all)
# st.write(fig_html)
container.pyplot(fig_all)
# components.html(fig_html, height=500, width=800)
