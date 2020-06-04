#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Orange'

from bs4 import BeautifulSoup
import re
from urllib import request, parse
import requests
import pymysql
import os
from selenium import webdriver

db = pymysql.connect("localhost", "root", "123456", "fuben", charset="utf8")
cursor = db.cursor()
COOKIE = ""
opt = webdriver.ChromeOptions()
opt.headless = False
driver = webdriver.Chrome(executable_path="./chromedriver", options=opt)
loginPage = "http://www.oracle.com/webapps/redirect/signon?nexturl="
useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
cookie_dict = {}
def readFile():
    urls = []
    f = open('./java.txt', 'r')
    while True:
        lines = f.readline()
        matchObj = re.search('https.*html', lines)
        if matchObj:
            urls.append(matchObj.group())
        if not lines:
            break
    print("获得urls")
    return urls

def getCookie(url):
    global COOKIE
    global cookie_dict
    # 尝试登陆
    print("清空cookie")
    driver.delete_all_cookies()
    driver.get(url)
    print("dirver获得的url:"+url)
    if 'Downloads' in driver.title:
        print("dirver进入下载页")
        return
    if '登录' in driver.title:
        print("dirver进入登录页")
        driver.find_element_by_id('sso_username').send_keys('492241408@qq.com')
        driver.find_element_by_id('ssopassword').send_keys('Vycz123.')
        driver.find_element_by_css_selector('input[onclick="doLogin(document.LoginForm);"]').click()
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']
        cookie_dict['oraclelicense'] = '141'
        cookieTmp = ""
        last = list(cookie_dict)[-1]
        for i in cookie_dict:
            if i==last:
                cookieTmp += i + "=" + cookie_dict[i]
            else:
                cookieTmp += i+"="+cookie_dict[i]+";"
        print("获得cookie"+cookieTmp)
        COOKIE = cookieTmp
        return
    print('dirver进入其他页')
    print()
    print(driver.page_source)

def getPage(url):
    try:
        req = request.Request(url)
        req.add_header('User-Agent', useragent)
        with request.urlopen(req) as f:
            html = f.read().decode('utf-8')
    except:
        return 'error'
    soup = BeautifulSoup(html, 'html.parser')
    for selection in soup.find_all(attrs={"data-licenses":"/a/ocom/docs/download-licenses.json"}):
        parceSelection(selection)


def saveFile(content, name):
    dir = "/data/jdk"
    if not os.path.exists(dir):
        os.mkdir(dir)
    filePath = dir+name
    with open(filePath,'wb') as f:
        f.write(content)
        f.close()


def downFile(link,name):
    global COOKIE
    global cookie_dict
    try:
        with requests.get(link,headers = {'user-agent':useragent},cookies=cookie_dict,allow_redirects=True,stream=True) as res:
            print(res.url)
            if "login" in res.url:
                print("cookie失效，重新获得"+res.url)
                getCookie(res.url)
                downFile(link,name)
                return
            # 数据落库 更新状态为1 下载中
            sql = "update t_jdk SET STATUS = %s WHERE NAME = '%s'" % (
                1,name)
            print("sql:" + sql)
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print("失败", e)
                db.rollback()

            with open("./"+name,'wb') as f:
                print("正在下载:"+name)
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                # 数据落库 更新状态为2 下载完成
                sql = "update t_jdk SET STATUS = %s WHERE NAME = '%s'" % (
                    2, name)
                print("sql:" + sql)
                try:
                    cursor.execute(sql)
                    db.commit()
                except Exception as e:
                    print("失败", e)
                    db.rollback()
        # saveFile(response.content,name)
    except Exception as e:
        print("请求出错",link,e)



def parceSing(selection,version):
    version = version.strip()
    soup = selection.find("tbody")
    for tr in soup.find_all("tr"):
        print("=====")
        tds = tr.find_all("td")
        des = tds[0].text.strip()
        size = tds[1].text.strip()
        link = tds[2].find("a")["data-file"].replace("//","https://").strip()
        name = tds[2].text.strip()
        print('version'+version+' des '+des +' size '+size+' link '+link)
        #查询数据库
        sql = "SELECT status FROM t_jdk WHERE name='%s'" %(name)
        try:
            ex = cursor.execute(sql)
            if ex >0:
                status = cursor.fetchone()
                if status[0] == 2:
                    continue

        except Exception as e:
            print("失败", e)
            db.rollback()
        # 数据落库 创建状态为0
        sql = " insert into t_jdk(name , size, description, version,category_id,status) values ('%s','%s','%s','%s',%s,%s)" % (
        name , size, des, version,3,0)
        print("sql:"+sql)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("失败", e)
            db.rollback()
        downFile(link,name)


def parceSelection(selection):
    version = selection.find("h4")
    print(version.text)
    parceSing(selection,version.text)

if __name__ == "__main__":
    # 获得文件url
    urls = readFile()
    # 首次登录获得cookie
    getCookie(loginPage+urls[0])
    # 解析页面内容
    for url in urls:
        getPage(url)

