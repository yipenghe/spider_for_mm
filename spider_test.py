# -*- coding:utf-8 -*-
import requests
import threading # multi-threading process
from bs4 import BeautifulSoup
#from lxml import etree 
from selenium import webdriver
  
def start_roomnum_collecting(category_html): # 这个函数是使用threading包进行多线程扒取的
    threads = []
    for item in category_html:
        th = threading.Thread(target=get_roomnum, args=(item, )) # get_roomnum是上面的一个函数,item是函数的一个参数
        th.start() # 多线程爬虫开始了！好兴奋！
        threads.append(th)
 
def grab_nxt(driver):
    next_page = driver.find_element_by_class_name("nxt").get_attribute("href")
    return next_page

visited = set()

def grab_nxt_bs(soup, page):
    next_link = soup.find("a", class_ = "nxt")
    global visited
    main = page.split("/")[2]
    if next_link is None or "http://" + main + next_link['href'] in visited:
        return None
    visited.add(next_link['href'])
    main = page.split("/")[2]
    return "http://" + main + next_link['href']

def get_comments(page):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0: WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    request = requests.get(url=page, headers=headers)
    response = request.text
    soup = BeautifulSoup(response, "lxml")
    comments = soup.find_all("div", class_ = "re_content")
    quotes = soup.find_all("div", class_ = "quotes")
    for comment in comments:
        if comment.find("div", class_ = "quote") is not None:
            print str(" ").join(comment.text.split()[4:])
        else:
            print comment.text
    return grab_nxt_bs(soup, page)

def get_threads(driver):
    links = driver.find_elements_by_id("threadlist")#/a[@target = '_blank']")
    for link in links:
        for l in link.find_elements_by_tag_name("a"):
            if "_blank" in l.get_attribute("target"):
                global visited
                next_page = l.get_attribute("href") + "1/"
                visited.add(next_page)
                while next_page is not None:
                    next_page = get_comments(next_page)
                break

def main(): # 主函数，如果未来虎牙更换了网址而网页结构没有改变，直接修改start_url就好了
    start_url = "http://q.mama.cn/group/1/"
    driver = webdriver.PhantomJS()
    driver.get("http://q.mama.cn/group/1/")
    for i in range(1):
        print "getting page " + str(i+1) + "..."
        next_page = grab_nxt(driver)
        get_threads(driver)
        driver.get(next_page)
    driver.quit()


    
    #for link in links:
    #    print link.get_attribute("text")

main()