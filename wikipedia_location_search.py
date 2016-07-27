# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 19:02:15 2016

@author: aadlandma
"""

from scipy import stats
import csv
import requests 
import json 

def geo_search(lat,lon,radius):
    if radius > 10:
        print "Radius cannot be more than 10 km. Setting to 10"
        radius = 10
    radius = radius * 1000
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=geosearch"
    "&gscoord={0}%7C{1}"
    "&gsradius={2}&gslimit=500&format=json").format(lat,lon,radius)
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
        return None 
 
def format_view(view):
    items = view['items']
    view_count = [item['views'] for item in items]
    time_stamp = [item['timestamp'] for item in items]
    return [view_count,time_stamp]

def format_table(coords,scores,raw_values,timeseries):
    output_list = []
    for i in range(len(scores)):
        date = str(timeseries[i])
        date_string = "{0}-{1}-{2}".format(date[0:4],date[4:6],date[6:8])
        output_list.append((coords[0],coords[1],scores[i],raw_values[i],date_string))
    return output_list

def csv_output(rows,filename):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

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
    

def bundle_places(pairs,views):
    rows = []
    for i in range(len(pairs)):
        discrete = [discretize(x) for x in stats.zcore(views[i][0])]
        current_row = format_table(pairs[i],discrete,views[i][0],discrete,views[i][1])
        rows += current_row
    return rows 

results = geo_search(50.9010, 4.4856,1)
pairs = [(x['lat'],x['lon']) for x in results]
formatted_titles = [x["title"].replace(" ","_") for x in results] 
views = [page_views(x.encode('utf8'),20150101,20160101) for x in formatted_titles]
formatted_views = [format_view(x) for x in views]



#### Airport ####
brussels_airport = page_views("Brussels_Airport",2015010100,2016032100)
brussels_airport_view = format_view(brussels_airport)
z_scores = stats.zscore(brussels_airport_view[0])
z_scores = list(z_scores)
airport_discret = [discretize(x) for x in z_scores]
coords = (50.9010, 4.4856)
rows = format_table(coords,airport_discret ,brussels_airport_view[0],brussels_airport_view[1])
csv_output(rows,"brussels_airport.csv")

#### Malebeek #### 
metro_stations = page_views("List_of_Brussels_Metro_stations",2015010100,2016032100)
metro_stations_view = format_view(metro_stations)
metro_z_scores = stats.zscore(metro_stations_view[0])
metro_discret = [discretize(x) for x in metro_z_scores]
metro_coords = (50.843889, 4.376667)
metro_rows = format_table(metro_coords,metro_discret,metro_stations_view[0],metro_stations_view[1])

all_rows = rows + metro_rows
csv_output(all_rows,"metro_and_airpot.csv")