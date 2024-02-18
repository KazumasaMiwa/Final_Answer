from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time
import datetime
from datetime import datetime as dt
import socket
import ssl
import OpenSSL
import pandas as pd
import sys

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
 
options = webdriver.ChromeOptions()
options.add_argument('--user-agent=' + user_agent)

driver = webdriver.Chrome(service=Service('C:\\Users\\user\\Downloads\\chromedriver_win32\\chromedriver-win32\\chromedriver.exe'))

def getoffiurl(url):
    driver.get(url)
    cur_url = ""
    try:
        time.sleep(4)
        a_item = driver.find_elements(By.CSS_SELECTOR, ("#sv-site > li"))
        a_i = a_item[0]
        a_item2 = a_i.find_element(By.TAG_NAME, ("a"))
        a_item2.click()
        time.sleep(3)
        main_tab = driver.current_window_handle
        new_tab = [x for x in driver.window_handles if x != main_tab][0]
        driver.close()
        driver.switch_to.window(new_tab)
        time.sleep(3)
        cur_url = driver.current_url
    except:

    return cur_url

def get_server_certificate(hostname):
    hostname = hostname.split("/")[2]
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as sslsock:
                der_cert = sslsock.getpeercert(True)
                return ssl.DER_cert_to_PEM_cert(der_cert),True
    except OSError as err:
        return 0,False

# MAIN
alllist=[['店舗名','電話番号','メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']]


urlpool=[]
i=0
count=0
boss='https://r.gnavi.co.jp/area/aream2115/rs/?date=20240219&fw=%E5%B1%85%E9%85%92%E5%B1%8B&people=96&time=1900'
i=0
driver.get(boss)
driversource=driver.page_source
bs = BeautifulSoup(driversource, 'html.parser')
elements=bs.find_all("a", class_="style_titleLink__oiHVJ")
for urls in elements:
    urlsub=urls.get('href')
    urlpool.append(urlsub)
    
for i in range(5):
    s_item = driver.find_elements(By.CSS_SELECTOR, ("#__next > div > div.layout_body__LvaRc > main > div.style_pageNation__AZy1A > nav > ul > li > a"))
    if len(s_item)<=11:
        s_item[len(s_item)-2].click()
    else:
        s_item[9].click()
    time.sleep(3)
    driver.current_url
    driversource=driver.page_source
    bs = BeautifulSoup(driversource, 'html.parser')
    elements=bs.find_all("a", class_="style_titleLink__oiHVJ")
    for urls in elements:
        urlsub=urls.get('href')
        urlpool.append(urlsub)
    if 50 < len(urlpool):
        break
    
del urlpool[50:]

ii = 0
for urlsub in urlpool:
    ii = ii + 1
    driver.get(urlsub)
    response=driver.page_source
    bs = BeautifulSoup(response, 'html.parser')
    sublist = []
    names=bs.find_all("p", class_="fn org summary")
    for name in names:
        sublist.append(name.text.replace("\xa0"," "))
    phonenumbers=bs.find_all("span", class_="number")
    for phonenumber in phonenumbers:
        sublist.append(phonenumber.text)
    infos=bs.select("#info-table > table > tbody > tr > td > ul > li > a")
    buffa=''
    for info in infos:
        m=info.get('href')
        j="mailto" in m
        if j is False:
            buffa=buffa+''
        else:
            target = ':'
            idx = m.find(target)
            r = m[idx+1:]
            buffa=buffa+r
    buffa = buffa + ''
    sublist.append(buffa)
    addresses=bs.find_all("span", class_="region")
    for address in addresses:
        matches=re.match(r'(...??[都道府県])((?:札幌|仙台|さいたま|千葉|横浜|川崎|相模原|新潟|静岡|浜松|名古屋|京都|大阪|堺|神戸|岡山|広島|北九州|福岡|熊本)市.+?区|(?:蒲郡|大和郡山)市|(?:余市|高市|杵島|[^市]+?)郡(?:玉村|大町|.+?)[町村]|[^市]+?[区]|(?:野々市|四日市|廿日市|.+?)[市]|.+?[町村])(.+)',address.text)
        sublist.append(matches[1])
        sublist.append(matches[2])
        sublist.append(matches[3])
    buffai=''
    buildings=bs.find_all("span", class_="locality")
    for building in buildings:
        if building.text is None:
            buffai=buffai+''
        else:
            buffai=buffai+building.text
    sublist.append(buffai)
    g=getoffiurl(urlsub)
    sublist.append(g)
    valid=False
    if g!="":
        cert = get_server_certificate(g)
        valid=cert[1]

        if valid==True:
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert[0].encode('utf-8'))
            not_before = dt.strptime(str(x509.get_notBefore())[2:16],'%Y%m%d%H%M%S') + datetime.timedelta(hours=9)
            not_after  = dt.strptime(str(x509.get_notAfter())[2:16],'%Y%m%d%H%M%S')  + datetime.timedelta(hours=9)
            period=not_after - dt.now()
            if period.days>0:
                valid=True
            else:
                valid=False
    sublist.append(valid)
    alllist.append(sublist)
    time.sleep(3)

df = pd.DataFrame(alllist)
df.to_csv("1-2.csv",sep=',',encoding='cp932',index=False,header=False)
#end
