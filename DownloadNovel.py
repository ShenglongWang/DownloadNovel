# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:46:58 2019

@author: shenglong wang
@version:01.00.00
"""
import requests
from urllib.parse import quote
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from lxml import html
import xml

Headers = {"User-Agent":("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36")
        }
BASE_URL = 'http://www.biquge.cm'

def get_chapterList(result):
    chapterDict = {}
    soup = BeautifulSoup(result.content,"lxml")
    for k in soup.find_all('div',id = 'list'):
        for j in k.find_all('a'):
            chapterDict[j.text] = j.get('href')
    return chapterDict
def judgeUniqueness(result):
    soup = BeautifulSoup(result.content,"lxml")
    resultList = soup.find_all('div',id = 'list')
    if(len(resultList) > 0):
        return True
    else:
        return False

def get_allNovelList(result):
    pass
def get_url(url):
    pass
def get_searchResult(NovelString):
    session = requests.session()
    url = ('http://www.biquge.cm/modules/article/sou.php?'
       'searchkey=%s&ct=2097152&si=biquge.cm&sts=biquge.cm') % quote(NovelString, encoding='gbk')
    try:
        
        result = session.post(url, headers=headers)
        
    except Exception as e:
        
        print(e)
        print('Request Fail \n')
        exit()
        
    result.encoding = 'gbk'
    
    return result
def save():
    pass




def main():
    result = get_searchResult('伏天氏')
    get_chapterList(result)
if __name__ == '__main__':
    main()