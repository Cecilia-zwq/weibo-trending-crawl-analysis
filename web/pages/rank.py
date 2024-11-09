import streamlit as st
import pymongo
from datetime import datetime
import matplotlib.pyplot as plt
import mpld3
import streamlit.components.v1 as components
import json
import pandas as pd
import seaborn as sns

# 连接到 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.weibo
collection = db.top_search

with open("./average_ranks.json", "r", encoding="utf8") as f:
    average_ranks = json.load(f)

with open("./rank_box.csv", "r", encoding="utf8") as f:
    df = pd.read_csv(f)

# 绘制柱状图
categories = list(average_ranks.keys())
avg_ranks = list(average_ranks.values())

fig = plt.figure(figsize=(10, 6))
plt.bar(categories, avg_ranks, color='skyblue')
plt.xlabel('类别')
plt.ylabel('最高排名平均值')
plt.title('每个话题类别下的平均最高排名')
plt.gca()
plt.xticks(rotation=45)
#plt.show()
st.pyplot(fig)

# 绘制箱线图
fig_box = plt.figure(figsize=(12, 8))
sns.boxplot(x='类别', y='最高排名', data=df, palette='Set3')
plt.xlabel('类别')
plt.ylabel('最高排名')
plt.title('每个话题类别下最高排名的箱线图')
plt.xticks(rotation=45)
plt.gca().invert_yaxis()  # 反转y轴，使得排名最小（最高）在顶部
st.pyplot(fig_box)
