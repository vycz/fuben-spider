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
from selenium.common.exceptions import NoSuchElementException

db = pymysql.connect("localhost", "root", "123456", "fuben", charset="utf8")
cursor = db.cursor()
COOKIE = ""
opt = webdriver.ChromeOptions()
opt.headless = False
driver = webdriver.Chrome(executable_path="./chromedriver", options=opt)
loginPage = "http://www.oracle.com/webapps/redirect/signon?nexturl="
useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection':'keep-alive',
    'Host':'download.oracle.com',
    'Sec-Fetch-Dest':'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'


}
cookie_dict = {}
count = 0
isFrist = True
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
    print("获得urls成功")
    return urls
def reLogin(url):
    print("重新登录:"+url)
    global COOKIE
    global cookie_dict
    print("清除cookie")
    driver.delete_all_cookies()
    driver.get(url)
    print("判断登录状态")
    try:
        driver.find_element_by_css_selector('.u28prof').click()
        driver.find_element_by_link_text("chengzhi yao")
        print("已登录")
        driver.find_element_by_css_selector('.icn-download-locked').click()
        time.sleep(3)
        el = driver.find_elements_by_xpath("//input[@name='licenseAccept']")
        el[1].click()
        # driver.switch_to_default_content()
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']
        return
    except Exception as e:
        print("未登录，重新登录")
        time.sleep(1)
        driver.find_element_by_css_selector(".u28btn1").click()
        # driver.find_element_by_id('sso_username').send_keys('492241408@qq.com')
        # driver.find_element_by_id('ssopassword').send_keys('Vycz123.')
        # driver.find_element_by_css_selector('input[onclick="doLogin(document.LoginForm);"]').click()
        time.sleep(1)
        driver.find_element_by_css_selector('.icn-download-locked').click()
        time.sleep(1)
        # driver.switch_to(driver.find_element_by_id("trustarcNoticeFrame"))
        # driver.find_element_by_css_selector('input[name="licenseAccept"]').click()
        el = driver.find_elements_by_xpath("//input[@name='licenseAccept']")
        el[1].click()
        # driver.switch_to_default_content()
        time.sleep(2)
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']

def firstLogin(url):
    print("首次登录")
    global COOKIE
    global cookie_dict
    print("dirver获得的url:" + url)
    driver.get(url)
    time.sleep(10)
    try:
        driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@title='TrustArc Cookie Consent Manager']"))
        driver.find_element_by_xpath("//a[@class='call']").click()
        driver.switch_to.default_content()
        print("需要确认cookie")
        driver.find_element_by_css_selector('.u28prof').click()
        driver.find_element_by_css_selector(".u28btn1").click()
        driver.find_element_by_id('sso_username').send_keys('492241408@qq.com')
        driver.find_element_by_id('ssopassword').send_keys('Vycz123.')
        driver.find_element_by_css_selector('input[onclick="doLogin(document.LoginForm);"]').click()
        driver.find_element_by_css_selector('.icn-download-locked').click()
        time.sleep(3)
        el = driver.find_elements_by_xpath("//input[@name='licenseAccept']")
        el[1].click()
        # driver.switch_to_default_content()
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']
    except NoSuchElementException:
        print("无需确认cookie协议")
        driver.find_element_by_css_selector('.u28prof').click()
        driver.find_element_by_css_selector(".u28btn1").click()
        driver.find_element_by_id('sso_username').send_keys('492241408@qq.com')
        driver.find_element_by_id('ssopassword').send_keys('Vycz123.')
        driver.find_element_by_css_selector('input[onclick="doLogin(document.LoginForm);"]').click()
        driver.find_element_by_css_selector('.icn-download-locked').click()
        time.sleep(3)
        el = driver.find_elements_by_xpath("//input[@name='licenseAccept']")
        el[1].click()
        # driver.switch_to_default_content()
        cookie_list = driver.get_cookies()
        for cookie in cookie_list:
            cookie_dict[cookie['name']] = cookie['value']
    print("首次登录成功")

def getCookie(url):
    global COOKIE
    global cookie_dict
    # 尝试登陆
    driver.get(url)
    print("dirver获得的url:"+url)
    #判断是否登录
    try:

        driver.find_element_by_link_text("chengzhi yao")
    except Exception as e:
        driver.find_element_by_css_selector(".u28btn1").click()

    print()
    if 'Downloads' in driver.title:
        print("dirver进入下载页")
        driver.quit()
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
        driver.quit()
        return
    print('dirver进入其他页')
    print()
    print(driver.page_source)
    driver.quit()

def getPage(url):
    print("进入新页面")
    try:
        req = request.Request(url)
        req.add_header('User-Agent', useragent)
        with request.urlopen(req) as f:
            html = f.read().decode('utf-8')
    except:
        return 'error'
    soup = BeautifulSoup(html, 'html.parser')
    for selection in soup.find_all(attrs={"data-licenses":"/a/ocom/docs/download-licenses.json"}):
        parceSelection(selection,url)


def saveFile(content, name):
    dir = "/data/jdk"
    if not os.path.exists(dir):
        os.mkdir(dir)
    filePath = dir+name
    with open(filePath,'wb') as f:
        f.write(content)
        f.close()


def downFile(link,name,url):
    global COOKIE
    global cookie_dict
    global header
    try:
        with requests.get(link,headers = header,cookies=cookie_dict,allow_redirects=True,stream=True) as res:
            if 'AuthParam' not in res.url:
                print("登录失效，重新获得登录态")
                reLogin(url)
                downFile(link,name,url)
                return
            print("获得下载链接"+res.url)
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



def parceSing(selection,version,url):
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
        downFile(link,name,url)


def parceSelection(selection,url):
    version = selection.find("h4")
    print(version.text)
    parceSing(selection,version.text,url)

def start():
    # 获得文件url
    urls = readFile()
    # 首次登录
    # firstLogin(urls[0])
    # 解析页面内容
    # for url in urls:
    #     getPage(url)
    firstLogin(urls[0])
    getPage(urls[0])
if __name__ == "__main__":
    start()

