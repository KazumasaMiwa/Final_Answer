import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
import time
import re
import socket
import ssl
import OpenSSL
import pandas as pd

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
header = {
    'User-Agent': user_agent
}

count=0
i=0
table=[['店舗名','電話番号','メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']]

while count<=49:
    main='https://r.gnavi.co.jp/area/aream2115/rs/?date=20240219&fw=%E5%B1%85%E9%85%92%E5%B1%8B&people=96&time=1900&p='
    sub=str(count//24 + 1)
    url=main+sub
    response = requests.get(url, headers=header)
    response.encoding=response.apparent_encoding
    bs = BeautifulSoup(response.text, 'html.parser')
    elements=bs.find_all("a", class_="style_titleLink__oiHVJ")
    url=elements[i].get('href')
    
    response = requests.get(url, headers=header)
    response.encoding=response.apparent_encoding
    bs = BeautifulSoup(response.text, 'html.parser')
    list=[]
    
    names=bs.find_all("p", class_="fn org summary")
    for name in names:
        list.append(name.text.replace("\xa0"," "))
    phonenumbers=bs.find_all("span", class_="number")
    for phonenumber in phonenumbers:
        list.append(phonenumber.text)
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
    list.append(buffa)
    addresses=bs.find_all("span", class_="region")
    for address in addresses:
        matches=re.match(r'(...??[都道府県])((?:札幌|仙台|さいたま|千葉|横浜|川崎|相模原|新潟|静岡|浜松|名古屋|京都|大阪|堺|神戸|岡山|広島|北九州|福岡|熊本)市.+?区|(?:蒲郡|大和郡山)市|(?:余市|高市|杵島|[^市]+?)郡(?:玉村|大町|.+?)[町村]|[^市]+?[区]|(?:野々市|四日市|廿日市|.+?)[市]|.+?[町村])(.+)',address.text)
        list.append(matches[1])
        list.append(matches[2])
        list.append(matches[3])
    
    buffai=''
    buildings=bs.find_all("span", class_="locality")
    for building in buildings:
        if building.text is None:
            buffai=buffai+''
        else:
            buffai=buffai+building.text
    list.append(buffai)
   
    URL=''
    list.append(URL)
    SSH=''
    list.append(SSH)
    table.append(list)
    count=count+1
    if i<len(elements)-1:
        i=i+1
    else:
        i=0
    time.sleep(3)

df = pd.DataFrame(table)
df.to_csv("1-1.csv",sep=',',encoding='cp932',index=False,header=False)
