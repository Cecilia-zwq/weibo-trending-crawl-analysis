import pymongo
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import json

# 连接到 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.weibo
collection = db.top_search


# 定义分组逻辑
def get_category(genre):
    if genre in ["剧集", "电影", "综艺", "电视剧", "影视"]:
        return '影视剧'
    elif genre in ["社会", "时事", "政务", "军事"]:
        return '社会时事'
    elif genre in ["房产", "电商", "财经", "汽车"]:
        return '商业'
    elif genre in ["音乐", "游戏", "演出", "时尚", "体育", "盛典", "直播", "明星"]:
        return '娱乐'
    elif genre in ["搞笑", "互联网", "生活记录", "情感", "星座", "美食", "地区"]:
        return '生活'
    elif genre in ["科普", "教育"]:
        return '教育'
    else:
        return '其他'


def process_category(genre):
    if genre:
        if isinstance(genre, list):
            if len(genre) > 0:
                # 取类别数组中的第一个元素
                last_genre = genre[0].split("-")
                # 有些类别要取"-"之前的字符串
                if len(last_genre) > 0:
                    last_genre = last_genre[0]
                genre =  last_genre
            else:
                genre = "其他"
        else:
            genre = "其他"
    else:
        genre = "其他"
    return get_category(genre)


# 聚合管道
pipeline = [
    {
        "$match": {
            "rank_data.time": {
                "$gte": datetime(2024, 5, 17),
                "$lt": datetime(2024, 5, 18)
            }
        }
    },
    {
        "$unwind": "$rank_data"
    },
    {
        "$match": {
            "rank_data.time": {
                "$gte": datetime(2024, 5, 17),
                "$lt": datetime(2024, 5, 18)
            }
        }
    },
    {
        "$group": {
            "_id": {
                "genre": "$genre",
                "time": "$rank_data.time"
            },
            "total_heat": {
                "$sum": {
                    "$toInt": "$rank_data.heat"
                }
            }
        }
    }
]

# 执行聚合查询
result = collection.aggregate(pipeline)

# 处理结果
heat_by_genre_and_time = defaultdict(lambda: defaultdict(int))

for doc in result:
    genre = doc["_id"]["genre"]  # Assuming genre is a list
    category = process_category(genre)
    time = doc["_id"]["time"]
    total_heat = doc["total_heat"]
    heat_by_genre_and_time[category][time] += total_heat

# 输出结果
plot_data = {}
for category, time_data in heat_by_genre_and_time.items():
    print(f"Category: {category}")
    for time, total_heat in sorted(time_data.items()):
        print(f"  Time: {time}, Total Heat: {total_heat}")
        times = sorted(time_data.keys())
        heats = [time_data[time] for time in times]
        plot_data[category] = (times, heats)

print(plot_data)

with open("./trend.json", "w", encoding="utf8") as f:
    json.dump(plot_data, f, ensure_ascii=False)
