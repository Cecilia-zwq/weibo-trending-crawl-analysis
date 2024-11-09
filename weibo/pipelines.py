# encoding=utf-8
import json
import codecs
import pymongo
from datetime import date, datetime
from itemadapter import ItemAdapter
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class WeiboPipeline:

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(
            spider.settings['MONGODB_SERVER'],
            spider.settings['MONGODB_PORT']
        )
        self.db = self.client[spider.settings['MONGODB_DB']]
        self.collection = self.db[spider.settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        # print(item)
        # 将 item 转换为字典
        data = ItemAdapter(item).asdict()

        # 这里要提取一下类别
        if data['genre']:
            data['genre'] = [data['genre'].strip()]
        else:
            data['genre'] = []
        if len(data['rank_data']['heat'].split()) > 1:
            genre = data['rank_data']['heat'].split()[0].strip()
            data['rank_data']['heat'] = data['rank_data']['heat'].split()[1].strip()
            data['genre'].append(genre)

        # 提取数据
        def convert_number(value):
            if '万' in value:
                return int(float(value[:-1]) * 10000)
            elif '亿' in value:
                return int(float(value[:-1]) * 100000000)
            else:
                return safe_int(value)

        detail_data = data['detail_data']
        conversions = {
            'discussions': convert_number,
            'duration': lambda x: int(x.split('小时')[0]) * 60 + safe_int(
                x.split('小时')[1].split('分钟')[0]) if '小时' in x else safe_int(x.split('分钟')[0]),
            'highest_rank': safe_int,
            'interactions': convert_number,
            'originals': convert_number,
            'views': convert_number,
        }
        if detail_data:
            for key, func in conversions.items():
                if detail_data[key]:
                    detail_data[key] = func(detail_data[key])
        try:
            data['rank_data']['time'] = datetime.strptime(data['rank_data']['time'], '%Y-%m-%d-%H-%M')
        except ValueError as e:
            spider.logger.error(f"日期格式错误: {data['rank_data']['time']} - {e}")

        # 构造查询条件
        query = {"topic": data['topic']}
        update = {"$set": {}, "$push": {"rank_data": data['rank_data']}}

        # 检查并添加非空的 detail_data 字段
        if detail_data:
            for key, value in data['detail_data'].items():
                if value:
                    update["$set"][f"detail_data.{key}"] = value

        # 检查并添加非空的其他字段
        if data['genre']:
            update["$set"]["genre"] = data['genre']
        if data['host']:
            update["$set"]["host"] = data['host']
        if data['summary']:
            update["$set"]["summary"] = data['summary']

        # js = json.dumps(update, sort_keys=True, indent=4, separators=(',', ':'), cls=ComplexEncoder)
        # spider.logger.info(f"finished with：\n{js}")

        # 尝试更新文档
        result = self.collection.update_one(query, update)
        # 如果没有匹配的文档，则插入新文档
        if result.matched_count == 0:
            try:
                data['rank_data'] = [data['rank_data']]
                self.collection.insert_one(data)
                spider.logger.info(f"插入新的热搜条目: {data['topic']}")
            except pymongo.errors.DuplicateKeyError:
                spider.logger.error(f"文档已存在: {data['topic']}")
        else:
            spider.logger.info(f"更新热搜条目: {data['topic']}")
        return item

    def close_spider(self, spider):
        self.client.close()
        spider.logger.info('数据库已关闭')
    