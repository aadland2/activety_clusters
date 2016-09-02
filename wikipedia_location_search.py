# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 19:02:15 2016

@author: aadlandma
"""

from scipy import stats
import csv
import requests 
import json 

def geo_search(lat,lon,radius,language="en"):
    if radius > 10:
        print "Radius cannot be more than 10 km. Setting to 10"
        radius = 10
    radius = radius * 1000
    url = ("https://{0}.wikipedia.org/w/api.php?action=query&list=geosearch"
    "&gscoord={1}%7C{2}"
    "&gsradius={3}&gslimit=500&format=json").format(language,lat,lon,radius)
    response = requests.get(url)
    if response.status_code == 200:
        search_results = json.loads(response.content)
        return search_results['query']['geosearch']
    else:
        return None
 
def page_views(title,start,end):
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/"
            "per-article/en.wikipedia/all-access/all-agents/{0}"
            "/daily/{1}/{2}").format(title,start,end)
    response = requests.get(url)
    if response.status_code == 200:
        search_results = json.loads(response.content)
        return search_results
    else:
        return [None,title] 
 
def format_view(view):
    try:
        items = view['items']
        view_count = [item['views'] for item in items]
        time_stamp = [item['timestamp'] for item in items]
        return [view_count,time_stamp]
    except:
        return None

def format_table(title,coords,scores,raw_values,timeseries):
    output_list = []
    for i in range(len(scores)):
        date = str(timeseries[i])
        date_string = "{0}-{1}-{2}".format(date[0:4],date[4:6],date[6:8])
        output_list.append((title,coords[0],coords[1],scores[i],raw_values[i],date_string))
    return output_list

def csv_output(rows,filename):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        for row in rows:
            row = list(row)
            row[0] = row[0].encode('utf-8')
            writer.writerow(row)

def discretize(value):
    if value < 1:
        return 0
    elif value >= 5:
        return 5
    elif value >= 4:
        return 4
    elif value >= 3:
        return 3
    elif value >= 2:
        return 2
    elif value >= 1:
        return 1
    

def bundle_places(titles,pairs,views):
    rows = []
    for i in range(len(pairs)):
        discrete = [discretize(x) for x in stats.zscore(views[i][0])]
        current_row = format_table(titles[i],pairs[i],discrete,views[i][0],views[i][1])
        rows += current_row
    return rows 


def wrapper(coords,radius,language,dates,title):
    results = geo_search(coords[0],coords[1],radius,language)
    # format titles 
    formatted_titles = [x["title"].replace(" ","_") for x in results] 
    # get views
    views = [page_views(x.encode('utf8'),dates[0],dates[1]) for x in formatted_titles]
    # extract titles without information available 
    broken_titles = [x[1].decode('utf8').replace("_"," ") for x in views if type(x) == list]
    filtered_views = [x for x in views if type(x) == dict]
    # get geo coords for remaining views 
    pairs = [(x['lat'],x['lon']) for x in results if x['title'] not in broken_titles]
    # format the views 
    formatted_views = [format_view(x) for x in filtered_views]
    # buindle the data into csv rows 
    return bundle_places(formatted_titles,pairs,formatted_views)

# csv_output(rows,"{0}.csv".format(title))

    
coords = [59.917197,30.277542]
language = "en"
dates = [20150101,20160721]
radius = 3
title = "Astrakhan Shipbuilding Production Association JSC".lower()
title = title.replace(" ","_")
rows = wrapper(coords,radius,language,dates,title)


#
#path = "C:/Users/aadlandma/Desktop/prisons_wikipedia/ftm.csv"
#with open(path, 'rb') as f:
#    reader = csv.reader(f)
#    for row in reader:
#        title = row[0].lower()
#        title = title.replace(" ","_")
#        title = title + "_ru"
#        coords = [float(row[1]),float(row[2])]
#        wrapper(coords,radius,language,dates,title)
