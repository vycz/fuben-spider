#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Orange'

import time

from bs4 import BeautifulSoup
import re
from urllib import request, parse
import requests
import pymysql
import os
from selenium import webdriver

db = pymysql.connect("localhost", "root", "123456", "fuben", charset="utf8")
cursor = db.cursor()

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
    if '登录' in driver.title:
        print("dirver进入登录页")
        driver.find_element_by_id('sso_username').send_keys('492241408@qq.com')
        driver.find_element_by_id('ssopassword').send_keys('Vycz123.')
        driver.find_element_by_css_selector('input[onclick="doLogin(document.LoginForm);"]').click()
        print("确认cookie协议")
        time.sleep(10)
        driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@title='TrustArc Cookie Consent Manager']"))
        driver.find_element_by_xpath("//a[@class='call']").click()
        driver.switch_to.default_content()
        print("同意oracle协议")
        driver.find_element_by_css_selector('.icn-download-locked').click()
        time.sleep(1)
        el = driver.find_elements_by_xpath("//input[@name='licenseAccept']")
        el[1].click()
        print("储存cookie")
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']
        cookie_dict['oraclelicense'] = '141'
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
        # step1
        step1 = requests.get(link,headers = {'user-agent':useragent},cookies=cookie_dict,allow_redirects=False)

        with s.get(link,headers = {'user-agent':useragent},cookies=cookie_dict,allow_redirects=True,stream=True) as res:
            if "login" in res.url:
                print("失败"+res.url)
                raise Exception("下载异常")
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
        exit()



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
            print("数据库中已存在数据:",name)
            if ex >0:
                status = cursor.fetchone()
                if status[0] == 2:
                    print("数据已下载完成，准备跳过")
                    continue
                else:
                    print("开始重新尝试下载")
            else:
                print("数据库中无此数据，开始创建:", name)
                # 数据落库 创建状态为0
                sql = " insert into t_jdk(name , size, description, version,category_id,status) values ('%s','%s','%s','%s',%s,%s)" % (
                    name, size, des, version, 3, 0)
                print("sql:" + sql)
                try:
                    cursor.execute(sql)
                    db.commit()
                except Exception as e:
                    print("失败", e)
                    db.rollback()
        except Exception as e:
            print("失败", e)
            db.rollback()
        downFile(link,name)


def parceSelection(selection):
    version = selection.find("h4")
    print(version.text)
    parceSing(selection,version.text)
def start(url):
    getCookie(loginPage + url)
    getPage(url)
if __name__ == "__main__":
    # 获得文件url
    urls = readFile()
    # 解析页面内容
    # for url in urls:
    #     opt = webdriver.ChromeOptions()
    #     opt.headless = False
    #     driver = webdriver.Chrome(executable_path="./chromedriver", options=opt)
    #     start(url)
    #     driver.quit()
    opt = webdriver.ChromeOptions()
    opt.headless = False
    driver = webdriver.Chrome(executable_path="./chromedriver", options=opt)
    start(urls[1])
    driver.quit()

