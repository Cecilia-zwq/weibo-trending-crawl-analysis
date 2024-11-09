# encoding=utf-8
import json
import pymongo
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.weibo
collection = db.top_search
plt.rcParams['font.family'] = 'SimHei'

# 定义类别处理函数
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
                genre = last_genre
            else:
                genre = "其他"
        else:
            genre = "其他"
    else:
        genre = "其他"
    return get_category(genre)


# 查询数据
documents = collection.find()

# # 分类并计算平均值
category_ranks = defaultdict(list)

for doc in documents:
    genre = doc.get("genre", [])
    category = process_category(genre)
    highest_rank = doc.get("detail_data", {}).get("highest_rank")
    if highest_rank is not None:
        category_ranks[category].append(highest_rank)

# 箱线图
# 转换为用于绘图的数据格式
data = []
for category, ranks in category_ranks.items():
    if category in ["教育", "其他"]:
        continue
    for rank in ranks:
        if rank > 15:
            continue
        data.append({'类别': category, '最高排名': rank})

# 创建DataFrame
df = pd.DataFrame(data)
df.to_csv("./rank_box.csv")
# 绘制箱线图
plt.figure(figsize=(12, 8))
sns.boxplot(x='类别', y='最高排名', data=df, palette='Set3')
plt.xlabel('类别')
plt.ylabel('最高排名')
plt.title('每个话题类别下highest_rank字段的箱线图')
plt.xticks(rotation=45)
plt.gca().invert_yaxis()  # 反转y轴，使得排名最小（最高）在顶部
plt.show()


# 计算平均值
average_ranks = {}
for category, ranks in category_ranks.items():
    if category in ["教育", "其他", "生活"]:
        continue
    for rank in ranks:
        if rank > 15:
            continue
        average_ranks[category] = sum(ranks) / len(ranks)

# # 聚合管道操作
# pipeline = [
#     {"$unwind": "$genre"},  # 展开genre数组
#     {"$group": {"_id": "$genre", "count": {"$sum": 1}}},  # 按照genre分组计数
#     {"$sort": {"count": -1}}  # 按照count降序排序
# ]
#
# # 执行聚合操作
# result = collection.aggregate(pipeline)
#
# # 打印结果
# print("不同的genre值和数量：")
# for doc in result:
#     genre = doc["_id"]
#     count = doc["count"]
#     print(f"{genre}: {count}")
#
# 查询热搜数据
# genres = collection.find({}, {"genre": 1})
# genre_counts = {}
# for doc in genres:
#     genre = doc.get("genre")
#     if genre:
#         if isinstance(genre, list):
#             if len(genre) > 0:
#                 # 取类别数组中的第一个元素
#                 last_genre = genre[0].split("-")
#                 # 有些类别要取"-"之前的字符串
#                 if len(last_genre) > 0:
#                     last_genre = last_genre[0]
#                 genre_counts[last_genre] = genre_counts.get(last_genre, 0) + 1
#         else:
#             genre_counts["其他"] = genre_counts.get("其他", 0) + 1
#     else:
#         genre_counts["其他"] = genre_counts.get("其他", 0) + 1
#
# # 输出统计结果
# genre_all = {'影视剧': {}, '社会时事': {}, '商业': {}, '娱乐': {}, '生活': {}, '教育': {}, '其他': {}}
# for genre, count in genre_counts.items():
#     cat = ""
#     if genre in ["剧集", "电影", "综艺", "电视剧", "影视"]:
#         cat = '影视剧'
#     elif genre in ["社会", "时事", "政务", "军事"]:
#         cat = '社会时事'
#     elif genre in ["房产", "电商", "财经", "汽车"]:
#         cat = '商业'
#     elif genre in ["音乐", "游戏", "演出", "时尚", "体育", "盛典", "直播", "明星"]:
#         cat = '娱乐'
#     elif genre in ["搞笑", "互联网", "生活记录", "情感", "星座", "美食", "地区"]:
#         cat = '生活'
#     elif genre in ["科普", "教育"]:
#         cat = '教育'
#     else:
#         cat = '其他'
#     genre_all[cat][genre] = count
#     if "count" in genre_all[cat]:
#         genre_all[cat]["count"] += count
#     else:
#         genre_all[cat]["count"] = count
#
#     # print(f"{genre}: {count}")
#
# print(genre_all)
#
with open("./average_ranks.json", "w", encoding="utf8") as f:
    json.dump(average_ranks, f, ensure_ascii=False)
