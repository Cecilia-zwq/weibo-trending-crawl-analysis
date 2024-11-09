import pymongo
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

# 连接到MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.weibo
collection = db.top_search

# 定义查询时间范围
start_date = datetime(2024, 5, 17)
end_date = datetime(2024, 5, 18)

# 查询数据
documents = collection.find()

# print(documents)

# 初始化每两个小时的时间段
time_slots = defaultdict(list)
current_time = start_date

while current_time < end_date:
    next_time = current_time + timedelta(hours=2)
    time_slots[(current_time, next_time)] = []
    current_time = next_time

print(time_slots)

# 分配topic到对应的时间段
for doc in documents:
    for rank_data in doc.get("rank_data", []):
        rank_time = rank_data["time"]
        print(rank_time)
        for (start, end) in time_slots.keys():
            if start <= rank_time < end:
                time_slots[(start, end)].append(doc["topic"])
                print(doc["topic"])
                break

# 生成和绘制词云
for (start, end), topics in time_slots.items():
    if topics:
        text = " ".join(topics)
        word_list = jieba.cut(text, cut_all=False)
        word_cloud_text = " ".join(word_list)

        wordcloud = WordCloud(
            font_path='./HGYT_CNKI.TTF',  # 替换为你的字体路径
            width=800,
            height=400,
            background_color='white'
        ).generate(word_cloud_text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"词云图 ({start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')})")
        plt.show()

        # 保存词云图
        wordcloud.to_file(f"wordcloud_{start.strftime('%Y%m%d_%H%M')}_{end.strftime('%H%M')}.png")
