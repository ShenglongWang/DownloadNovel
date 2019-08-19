# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:46:58 2019

@author: shenglong wang
@version:01.00.00
"""
import sys
import os
import requests
from urllib.parse import quote
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from lxml import html
import xml
from multiprocessing import Pool

Headers = {"User-Agent":("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36")
        }
BASE_URL = 'http://www.biquge.cm'

ONLY_ONE = 1
HAVE_MORE = 2
NONE_HAVE = 0

#获取Http://www等网页中的内容
def get_url(url):
    response = ''
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
    return response

#从requests返回的章节列表中获取章节名及链接，返回[(章节名:链接地址),]
def get_chapterList(result):
    chapterList = []
    soup = BeautifulSoup(result.content,"lxml")
    for k in soup.find_all('div',id = 'list'):
        for j in k.find_all('a'):
            chapterList.append((j.text,j.get('href')))
    return chapterList


#判断搜索小说名后获得结果是否唯一，若唯一则requests返回的是章节内容，若不是，返回的则是包含小说名的几个列表。
#此函数仅判断结果是否唯一，唯一则返回True,反之亦然。
def judgeSearchReturnType(result):
    soup = BeautifulSoup(result.content,"lxml")
    resultList = soup.find_all('div',id = 'list')
    if(len(resultList) > 0):
        return ONLY_ONE
    else:
        resultList = soup.find_all('tr',id = 'nr')
        if(len(resultList) > 0):
            return HAVE_MORE
        else:
            return NONE_HAVE


#搜索后有可能会有多个结果显示，此函数返回搜索后的小说列表[(小说名,作者,响应链接),]
def get_allNovelList(result):
    novel_List = []
    soup = BeautifulSoup(result.content,'lxml')
    for k in soup.find_all('tr',id = 'nr'):
        novelTd = k.find_all('td',class_= 'odd')
        link = novelTd[0].find_all('a')
        novel_List.append((link[0].text,novelTd[1].text,link[0].get('href')))
    return novel_List
            

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


#按照用户所下载的内容保存到相应txt文件中
def save(arg):
    chapter_name,url = arg
    with open(chapter_name + '.txt','w',encoding = 'utf-8') as f:
        print('[%d]正在下载%s\n' %  (os.getpid(),chapter_name), file=sys.stderr)
        f.write(chapter_name + '\n')
        f.write(get_text(url) + '\n')

#获取用户所要下载的小说名
def get_NovelName():
    name = ''
    while(True):
        name = input('请输入小说名称（全称）：\n')
        if name != '':
            break
    return name

def display_tenChapterTitle(chapterList):
    print('最新10章：\n')
    if(len(chapterList) > 10):
        tmplist = chapterList[-1:-11:-1]
    else:
        tmplist = chapterList
    for title,link in tmplist:
        print(title + '\n')
        
def mergeTxt(novel_name,downlist):
    with open(novel_name + '.txt','w',encoding = 'utf-8') as novelFile:
        for chapter_name,url in downlist:
            with open(chapter_name + '.txt','r',encoding = 'utf-8') as f:
                for line in f.readlines():
                    novelFile.write(line)
            os.remove(chapter_name + '.txt')
    
def main():
    
    while(True):
        novel_name = get_NovelName()
        
        search = get_searchResult(novel_name)
        
        searchReturnType = judgeSearchReturnType(search)
        
        if(NONE_HAVE == searchReturnType):
            print("抱歉，搜索没有结果，请重新输入!\n")
        elif(HAVE_MORE ==searchReturnType):
            novel_list = get_allNovelList(search)
            while(True):
                index = 1
                print('相似小说如下，请选择需下载的小说(输入序号即可)：\n')
                for name,author,link in novel_list:
                    print(str(index) + '.' + name + ' 作者：'+ author +'\n')
                    index += 1
                select = int(input('小说序号：\n'))
                if select in range(1,len(novel_list)+1):
                    novel_name,author,novel_url = novel_list[select-1]
                    chapterList = get_chapterList(get_url(novel_url))
                    break
            break
        elif(ONLY_ONE == searchReturnType):
            chapterList = get_chapterList(search)
            break
        
    print('搜索到小说《' + novel_name + '》，总共' + str(len(chapterList)) +'章\n')
    
    display_tenChapterTitle(chapterList)
    
    index = int(input('请输入需要下载的章节数(正数表示从第一章开始下载；\n负数表示从最新一章往前下载；)\n'))
    
    if(abs(index) > len(chapterList)):
        print("输入章节数大于总章节，默认下载全部章节。\n")
        index = len(chapterList)
    if(index >= 0):
        downlist = chapterList[0:index]
    else:
        downlist = chapterList[index:]
    Pool().map(save,[(chapter_name,url) for chapter_name,url in downlist])
    
    mergeTxt(novel_name,downlist)
    
if __name__ == '__main__':
    main()