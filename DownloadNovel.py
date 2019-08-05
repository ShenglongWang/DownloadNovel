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

#从requests返回的章节列表中获取章节名及链接，返回{章节名:链接地址,}
def get_chapterList(result):
    chapterDict = {}
    soup = BeautifulSoup(result.content,"lxml")
    for k in soup.find_all('div',id = 'list'):
        for j in k.find_all('a'):
            chapterDict[j.text] = j.get('href')
    return chapterDict


#判断搜索小说名后获得结果是否唯一，若唯一则requests返回的是章节内容，若不是，返回的则是包含小说名的几个列表。
#此函数仅判断结果是否唯一，唯一则返回True,反之亦然。
def judgeUniqueness(result):
    soup = BeautifulSoup(result.content,"lxml")
    resultList = soup.find_all('div',id = 'list')
    if(len(resultList) > 0):
        return True
    else:
        return False

def get_allNovelList(result):
    pass

#获取一章小说的内容
def get_text(url):
    chapter_url = BASE_URL + url
    content = ''
    try:
        result = requests.get(chapter_url,headers = Headers)
    except Exception as e:
        print(e)
        return content
    soup = BeautifulSoup(result.content,"lxml")
    content = soup.find_all('div',id = 'content')
    if content != '':
        return content[0].text
    else:
        return content

#模拟在笔趣阁的搜索栏中搜索小说
def get_searchResult(NovelString):
    session = requests.session()
    url = ('http://www.biquge.cm/modules/article/sou.php?'
       'searchkey=%s&ct=2097152&si=biquge.cm&sts=biquge.cm') % quote(NovelString, encoding='gbk')
    try:
        
        result = session.post(url, headers=Headers)
        
    except Exception as e:
        
        print(e)
        print('Request Fail \n')
        exit()
        
    result.encoding = 'gbk'
    
    return result
def save(novel_name,chapterDict):
    with open(novel_name + '.txt','w',encoding = 'utf-8') as f:
        for chapter,url in chapterDict.items():
            print('正在下载%s\n' %  chapter)
            f.write(chapter + '\n')
            f.write(get_text(url) + '\n')
    print("下载完成！！\n")

#获取用户所要下载的小说名
def get_NovelName():
    name = ''
    while(True):
        name = input('请输入小说名称（全称）：\n')
        if name != '':
            break
    return name
def main():
    novel_name = get_NovelName()
    
    search = get_searchResult(novel_name)
    
    result_dict = get_chapterList(search)
    
    save(novel_name,result_dict)
    
if __name__ == '__main__':
    main()