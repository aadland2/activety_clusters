# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 23:36:41 2016

@author: aadlandma
"""
import requests   
import unicodecsv as csv  
from bs4 import BeautifulSoup   
  
  


def edit_history(url):
    """ returns the revision date for a wikipedia url """
    result_set = []
    soup = BeautifulSoup(requests.get(url).text)
    ul_list = soup.find_all("ul")
    revision_list = ul_list[1]
    date_anchors = revision_list.find_all("a",{"class":"mw-changeslist-date"})
    for date in date_anchors:
        result_set.append(date.contents[0])
    return result_set

def russia_history(url):
    result_set = []
    soup = BeautifulSoup(requests.get(url).text)
    ul_list = soup.find_all("ul")
    revision_list = ul_list[0]
    date_anchors = revision_list.find_all("a",{"class":"mw-changeslist-date"})
    for date in date_anchors:
        result_set.append(date.contents[0])
    return result_set
    
# tests 
url= "https://en.wikipedia.org/w/index.php?title=Crimea&offset=20170101000000&limit=5&action=history&tagfilter="
dates = edit_history(url)
url2 = "https://en.wikipedia.org/w/index.php?title=Russian_military_intervention_in_Ukraine_(2014%E2%80%93present)&offset=&limit=500&action=history"
dates2 = edit_history(url2)
# in russian 
url3 = "https://ru.wikipedia.org/w/index.php?title=%D0%9A%D1%80%D1%8B%D0%BC&action=history"
dates3 = russia_history(url3)
result_set = []
soup = BeautifulSoup(requests.get(url3).text)
ul_list = soup.find_all("ul")
revision_list = ul_list[0]
date_anchors = revision_list.find_all("a",{"class":"mw-changeslist-date"})
for date in date_anchors:
    result_set.append(date.contents[0])
    
url4 = "https://ru.wikipedia.org/w/index.php?title=%D0%9F%D0%BB%D0%B0%D0%BD%D1%82%D0%B5%D0%BD,_%D0%A5%D1%80%D0%B8%D1%81%D1%82%D0%BE%D1%84%D0%BE%D1%80&action=history"
russia_history(url4)