# 使用selenium模拟浏览器抓取淘宝美食
# 使用Chrome和phantomJS作为浏览器
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
from config import *
from selenium.webdriver.chrome.options import Options

# 使用Chrom的 headless 模式
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)


def search(keyword):
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com')
        # 搜索输入框, 直到输入框出现
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        # 搜索按钮， 直到搜索按钮可以点击
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        # 输入要搜索的内容
        input.send_keys(keyword)
        # 点击搜索按钮
        submit.click()
        # 返回总页数
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))
        )
        # 获取商品信息
        get_product()
        return total.text
    except TimeoutException:
        return search()


def next_page(page_number):
    print('正在翻页{page_number}'.format(page_number=page_number))
    try:
        # 页码输入框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        # 页码提交按钮
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        # 清除页码输入框内容
        input.clear()
        # 传入页码
        input.send_keys(page_number)
        # 确定按钮，跳转到对应页码
        submit.click()
        # 直到页码跳转成功为止
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )
        # 获取商品信息
        get_product()
    except TimeoutException:
        next_page(page_number)


def get_product():
    # 等待商品信息加载完成
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item'))
    )
    # 获取网页源代码
    html = browser.page_source
    doc = pq(html)
    # 获取全部商品
    items = doc('#mainsrp-itemlist .items .item').items()
    # 解析商品
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text().replace('\n', ''),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text()
        }
        print(product)


def main():
    total = search(KEYWORD)
    total = int(re.compile('(\d+)').search(total).group(1))
    for i in range(2, total + 1):
        next_page(i)


if __name__ == '__main__':
    main()
