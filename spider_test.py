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
    print page
    soup = BeautifulSoup(response, "lxml")
    comments = soup.select("[class~=re_content]")
    floors = soup.select("[class~=floor]")
    userstatus = soup.select("[class~=userstatus]")

    title = soup.select("[class~=h1]")
    try:
        title_n = title[0].text
        print "Title:  ",
        print title_n
        count = 0
        for comment in comments:
            if 'quote' in str(comment): #ignore the quote part of repost
                cmt = str(comment).split("</div>")[-2]
            else:
                cmt =  comment.text
            print "floor ",
            print floors[count].text,

            print " ",
            name = userstatus[count].select("[class~=user_name]")
            if len(name) == 0:
                print "anonymous user",
            else:
                print name[0].text,
            print ":   ",
            print cmt
            count += 1
    except:
        return "error"
    return grab_nxt_bs(soup, page)

def get_threads(driver):
    links = driver.find_elements_by_id("threadlist")#/a[@target = '_blank']")
    for link in links:
        for l in link.find_elements_by_tag_name("a"):
            if "_blank" in l.get_attribute("target"):
                global visited
                next_page = l.get_attribute("href") + "1/"
                if "q.mama.cn" not in next_page:
                    continue
                visited.add(next_page)
                while next_page is not None and next_page != "error":
                    next_page = get_comments(next_page)
                if next_page == "error":
                    print "the group is deleted"
                    return
                print "~~~~~~~~~~~~~~~~~"

def get_group_post(driver, page):
    print page
    driver.get(page)
    group_name = driver.find_element_by_class_name("h3").get_attribute("text")
    print "Exploring group " + group_name
    for i in range(2):
        print "=================================="
        print "getting page " + str(i+1) + " of group " + group_name
        print "=================================="
        next_page = grab_nxt(driver)
        get_threads(driver)
        driver.get(next_page)
        print "finished page " + str(i+1) + " of group " + group_name


def get_groups_url(page):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0: WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    request = requests.get(url=page, headers=headers)
    response = request.text
    soup = BeautifulSoup(response, "lxml")
    raw_groups = soup.find_all("div", class_ = "layoutLeft topGroup")
    groups = list()
    count = 0
    for soup in raw_groups:
        groups.append(list())
        titles = soup.select("[class~=tit]")
        for group in titles:
            groups[count].append("http:"+group["href"])
        count+=1
    return groups

def get_community():
    driver = webdriver.PhantomJS("C:/Users/yiphe/Desktop/phantomjs.exe")
    start_url = "http://q.mama.cn/"
    group_links = get_groups_url(start_url)
    for cate in group_links:
        for group in cate:
            get_group_post(driver, group)
    driver.quit()

got = set()
def explore_hot_tags(page = "http://www.mama.cn/ask/list/k2626-p1.html"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0: WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    request = requests.get(url=page, headers=headers)
    response = request.text
    soup = BeautifulSoup(response, "lxml")
    pager = soup.find("ul", class_ = "pager")
    tab_name = soup.find("li", class_ = "now").find("strong")
    all_q = soup.find_all("p", class_ = "htitle")
    page = pager.find_all("span")
    #try:
       # print tab_name.text + " " + page[-1].text
    #except:
     #   pass
    global got
    for q in all_q:
        if q in got:
            continue
        got.add(q)
        print q.text
        #print q.find("a")["href"]
    next_page = pager.find_all("li")[-1].find("a")["href"]
    if next_page not in got:
        got.add(next_page)
        #print next_page
    return next_page

def explore_n_page(page, num = 3):
    next_page = page
    for i in range(num):
        next_page = explore_hot_tags(next_page)

def start_qa_collecting(tag_list):
    threads = []
    for url in tag_list:
        th = threading.Thread(target=explore_n_page, args=(url, 20))
        th.start()
        threads.append(th)

def get_qa():
    page = "http://www.mama.cn/ask/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0: WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    request = requests.get(url=page, headers=headers)
    response = request.text
    soup = BeautifulSoup(response, "lxml")
    souper = soup.find("ul", class_ = "hotTag cl")
    hot_tags = souper.find_all("li")
    tag_list = list()
    for tags in hot_tags:
        hot_tag = tags.find("a")["href"]
        tag_list.append(hot_tag)
    start_qa_collecting(tag_list)
    print len(got)
get_qa()
