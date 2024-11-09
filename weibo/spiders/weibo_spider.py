# encoding=utf-8
import scrapy
from pathlib import Path
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import sys
import datetime
import time
from weibo.items import DetailData, RankData, WeiboItem


class WeiboSpider(scrapy.Spider):
    name = "top"
    count = 0

    def start_requests(self):
        urls = ["https://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6", ]
        for url in urls:
            yield SeleniumRequest(url=url, callback=self.parse_topRank, )

    def parse_topRank(self, response):
        driver = response.request.meta["driver"]
        WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located((By.ID, "pl_top_realtimehot"))
        )
        # 获取当前时间
        t = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        # 定位到热搜table
        self.logger.info("获取到热搜表，取前15位")
        element = driver.find_element(By.ID, "pl_top_realtimehot")
        table = element.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        cnt = 0
        # 先提前保存好
        items = []
        for row in rows:
            td = row.find_elements(By.TAG_NAME, "td")
            if td and (len(td[0].get_attribute('class').split()) == 3):
                item = WeiboItem(host=None, genre=None)
                # 热搜关键字
                item['topic'] = td[1].find_element(By.TAG_NAME, "a").text
                # 当前时间下的排名和热度
                rank_data = RankData()
                rank_data['time'] = t
                rank_data['rank'] = td[0].text
                rank_data['heat'] = td[1].find_element(By.TAG_NAME, "span").text
                item['rank_data'] = rank_data
                # link = f"https://m.s.weibo.com/vtopic/detail_new?click_from=searchpc&q=%23{item['topic']}%23"
                # print(f"started {item['topic']}")
                # yield SeleniumRequest(url=link, callback=self.parse_superTopic, dont_filter=False,
                #                       meta=({'item': item}))
                # 加入到items中
                items.append(item)
                cnt += 1
                if cnt == 15:
                    break
        # driver.quit()
        for item in items:
            # 超话详细数据链接
            link = f"https://m.s.weibo.com/vtopic/detail_new?click_from=searchpc&q=%23{item['topic']}%23"
            # print(f"started {item['topic']}")
            yield SeleniumRequest(url=link, callback=self.parse_superTopic, dont_filter=False,
                                  meta=({'item': item}))
            self.logger.info(f"yield request for {item['topic']}")
            time.sleep(5)
        # Path(f"data/{time}.txt").write_text(table.text, encoding='utf-8')
        # sys.stdout.write("write to file.")

    def parse_superTopic(self, response):
        driver = response.request.meta["driver"]
        # item = WeiboItem()
        # item['rank_data'] = response.meta["item"]['rank_data']
        # item['topic'] = response.meta["item"]['topic']
        item = response.meta["item"]
        self.logger.info(f"parse_ request for {item['topic']}")
        # print('waiting for ' + item['topic'])
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-topic-detail-model"))
            # visibility_of_all_elements_located
        )
        # print('started parsing ' + item['topic'])
        # 最新数据
        detail_data = DetailData()
        # detail_data['link'] = f"https://m.s.weibo.com/vtopic/detail_new?click_from=searchpc&q=%23{item['topic']}%23"
        # 加载话题导语
        try:
            summary = driver.find_element(By.CLASS_NAME, "summary")
            item['summary'] = summary.text
        except Exception as e:
            self.logger.warning(f"{item['topic']}: 没有话题导语")
            item['summary'] = None

        # 话题数据总览：阅读量、讨论两、互动量、原创量
        try:
            overall = driver.find_elements(By.CLASS_NAME, "item-col")
            if len(overall) == 4:
                detail_data['views'] = overall[0].find_element(By.CLASS_NAME, "num").text
                detail_data['discussions'] = overall[1].find_element(By.CLASS_NAME, "num").text
                detail_data['interactions'] = overall[2].find_element(By.CLASS_NAME, "num").text
                detail_data['originals'] = overall[3].find_element(By.CLASS_NAME, "num").text
        except Exception as e:
            self.logger.warning(f"{item['topic']}: 没有话题数据总览")
            detail_data['views'] = None
            detail_data['discussions'] = None
            detail_data['interactions'] = None
            detail_data['originals'] = None
        # 热搜记录：最高排名、在榜时长
        try:
            record = driver.find_elements(By.CLASS_NAME, "area_gray_col")
            if len(record) > 1:
                detail_data["highest_rank"] = int(record[0].find_element(By.CLASS_NAME, "pos").text)
                detail_data["duration"] = record[1].find_element(By.CLASS_NAME, "area_gray_num").text
            item['detail_data'] = detail_data
        except Exception as e:
            self.logger.warning(f"{item['topic']}: 没有热搜记录")
            detail_data["highest_rank"] = None
            detail_data["duration"] = None
        # 主持人和话题分类
        try:
            records = driver.find_elements(By.CLASS_NAME, "item-line")
            if records:
                for record in records:
                    key = record.find_element(By.CLASS_NAME, "more").text
                    value = record.find_element(By.CSS_SELECTOR, "[class*=data]").text
                    if key == "主持人":
                        item['host'] = value
                    if key == "话题分类":
                        item['genre'] = value
        except Exception as e:
            self.logger.warning(f"{item['topic']}: 没有主持人和话题分类")
            item['host'] = ""
            item['genre'] = ""
        # print(item)
        # driver.quit()
        self.count += 1
        self.logger.info('finished parsing ' + item['topic'] + ', remaining ' + str(15 - self.count))
        yield item
