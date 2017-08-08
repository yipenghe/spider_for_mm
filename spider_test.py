# -*- coding:utf-8 -*-
import requests
import threading # multi-threading process
from bs4 import BeautifulSoup
#from lxml import etree 
from selenium import webdriver
 

#inspired by http://anchengdeng.com/2017/07/22/bespiderman/


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
    comments = soup.select("[class~=re_content]")
    floors = soup.select("[class~=floor]")
    count = 0
    for comment in comments:
        if 'quote' in str(comment): #ignore the qutoe part of repost
            cmt = str(comment).split("</div>")[-2]
        else:
            cmt =  comment.text
        print "floor ",
        print floors[count].text,
        print ":   ",
        print cmt
        count += 1
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

def main(): 
    start_url = "http://q.mama.cn/group/1/"
    driver = webdriver.PhantomJS()
    driver.get("http://q.mama.cn/group/1/")
    for i in range(10):
        print "=================================="
        print "getting page " + str(i+1) + "..."
        print "=================================="
        next_page = grab_nxt(driver)
        get_threads(driver)
        driver.get(next_page)
        print "finished page" + str(i+1)
    driver.quit()

main()