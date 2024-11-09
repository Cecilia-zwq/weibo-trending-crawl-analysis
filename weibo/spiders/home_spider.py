# encoding=utf-8
import scrapy
from pathlib import Path
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # 输入框回车
from selenium.webdriver.common.by import By  # 与下面的2个都是等待时要用到
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # 异常处理
import time


class HomeSpider(scrapy.Spider):
    name = "home"

    def start_requests(self):
        urls = ["https://www.weibo.com", ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            'Cookie': 'SINAGLOBAL=336350334225.3615.1712411427119; UOR=,,www.bilibili.com; ULV=1717063238391:14:8:3:1451607318519.5654.1717063238382:1717044765977; XSRF-TOKEN=v2OWotwp5d87c_bN009wNDu3; PC_TOKEN=97a5043bae; ALF=1719741089; SUB=_2A25LXe3xDeRhGeNN6lQW-CfEyTWIHXVoE285rDV8PUJbkNANLUrmkW1NScYniYchKjOLpbZjJbYpLJy7qErxDGtO; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFAkeXCzzjPFwNufe3nxH8o5JpX5KzhUgL.Fo-0eKqN1h.Reo.2dJLoIEXLxK.L1KnLB.qLxK-LBo.LB.zLxKML1-2L1hBLxK-LBoMLBKnLxKnL1-BL12-t; WBPSESS=2xuHjDs9p_bFnADjPRQTmpXYTbdMJCj7g6nFphhSoFOk-7mhAd05WWgXULHk5ZmM3bm5e3C2lgE4KTSKEiiiKQSnKc6i1cclSJORywCDHnDjFYzcWUI5x4TQ2fZx5knZj_MT0F5Jo8zU4AHpI4kP4g==',
        }
        for url in urls:
            yield SeleniumRequest(url=url, callback=self.parse_home, headers=headers)

    def parse_home(self, response):
        driver = response.request.meta["driver"]
        WebDriverWait(driver, 5)
        # 获取当前页面的高度
        last_height = driver.execute_script("return document.body.scrollHeight")
        # 模拟下拉操作，直到滑动到底部
        while True:
            # 模拟下拉操作
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 等待页面加载
            time.sleep(2)
            # 获取当前页面的高度
            new_height = driver.execute_script("return document.body.scrollHeight")
            # 判断是否已经到达页面底部
            if new_height == last_height:
                break
            # 继续下拉操作
            last_height = new_height

        element = driver.find_element(By.XPATH, "/html/body")
        print(element.text)
