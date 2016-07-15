# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 12:41:17 2016

@author: aadlandma
"""
import json
import requests 
import datetime 
import calendar 
import os 
import urllib
import csv


# global key 
# global check_time

#### create default date ####

def default_date():
    fmt = '%Y-%m-%d'
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    check_time = yesterday.strftime(fmt)
    return check_time

def launch_key(cred_key):
    global key 
    key = cred_key 
    return key 
        

def places_search(lat,lon,page=1,radius=1.0):
    """ Radius query of wikimapi api. 
    Args:
        lat  (float): latitude
        lon  (float): longitude
        radius (float): number of kilometers to search 
        page (int): page to search
    Returns:
        search_results(dict): json object of the query results 
    """
    radius = radius * 1000
    url = ("http://api.wikimapia.org/?key={0}&function=place.search&q=&"
       "lat={1}&lon={2}&page={3}&count=100&"
       "category=&categories_or=&categories_and=&distance={4}&"
       "format=json&pack=&language=en")
    
    url = url.format(key,lat,lon,page,radius)
    response = requests.get(url)
    if response.status_code == 200:
        search_results = json.loads(response.content)
        return search_results
    else:
        return None

def bbox_search(lon_min,lat_min,lon_max,lat_max,page):
    """ Bounding Box query of wikimapia API. 
    Args:
        lon_min (float): minimum longitude
        lat_min (float): minimum latitude
        lon_max (float): maximum longitude
        lat_max (float): maximum latitude 
        page (int): page to search
    Returns:
        search_results(dict): json object of the query results 
    """
    url = ("http://api.wikimapia.org/?key={0}&function=place.getbyarea&"
        "coordsby=bbox&bbox={1}%2C{2}%2C{3}%2C{4}&"
        "format=json&pack=&language=en&page={5}&count=100&category="
        "&categories_or=&categories_and="
    )
    url = url.format(key,lon_min,lat_min,lon_max,lat_max,page)
    response = requests.get(url)
    if response.status_code == 200:
        search_results = json.loads(response.content)
        return search_results
    else:
        return None

def bbox_pages(lon_min,lat_min,lon_max,lat_max):
    """ Returns the json of all the pages from a bbox_search. 
    Args:
        lat  (float): latitude
        lon  (float): longitude
        radius (float): number of kilometers to search 
    Returns:
        page_responses(list): list of json objects from the page responses 
    """
    page_responses = [] 
    page = 1
    found = bbox_search(lon_min,lat_min,lon_max,lat_max,1)
    total_pages = (int(found['found']) / 100) + 1
    while page <= total_pages:
        search_results = bbox_search(lon_min,lat_min,lon_max,lat_max,page=page)
        if search_results:
            page_responses.append(search_results)
        page += 1 
    return page_responses 

def get_all_pages(lat,lon,radius):
    """ Returns the json of all the pages from a radius search. 
    Args:
        lon_min (float): minimum longitude
        lat_min (float): minimum latitude
        lon_max (float): maximum longitude
        lat_max (float): maximum latitude 
    Returns:
        page_responses(list): list of json objects from the page responses 
    """
    page_responses = [] 
    page = 1
    found = places_search(lat,lon,page,radius)
    total_pages = (int(found['found']) / 100) + 1
    while page <= total_pages:
        search_results = places_search(lat=lat,lon=lon,page=page,radius=radius)
        if search_results:
            page_responses.append(search_results)
        page += 1 
    return page_responses 
    

def check_time(upload_time,check_time=None):
    """ Checks whether a photo was uploaded after a check time.
        
        Args:
            upload_time(int): epoch date of when the photo was uploaded to wiki
            check_time(str):  date str formatted YYYY-MM-DD (defaults to yesterday)
        Returns:
            True if the upload_time is newer than check_time 
    """
    if check_time == None:
        check_time = default_date()
    date_object = datetime.datetime.strptime(check_time, '%Y-%m-%d')
    epoch_time = calendar.timegm(date_object.timetuple())
    return True if upload_time > epoch_time else False

def iterate_places(search_results):
    pass

def iterate_photos(place,check=False):
    for photo in place['photos']:
            if check:
                updated = check_time(photo['time'],check_time=check_time)
                if updated:
                    save_photos(photo['big_url'],photo['id'])
            else:
                save_photos(photo['big_url'],photo['id'])
    return
            
def get_all_photos(result,lat,lon,radius):
    page = 1
    total_pages = (int(result['found']) / 100) + 1
    while page <= total_pages:
        search_results = places_search(lat=lat,lon=lon,page=page,radius=radius)
        if search_results:
            for place in search_results['places']:
                iterate_photos(place)
        page += 1 
    return 



def get_buildings(response):
    """ Filters page response for buildings. 
    Args:
       response(dict): json dictionary from a page response 

    Returns:
        buildings(list): list of page response for buildings 
    """   
    buildings = []
    for place in response['places']:
        if place['is_building']:
            buildings.append(place)
    return buildings 
        
def photo_time(response,check=False,date=None):
    """Gets the coordinates, time uploaded, and url of a photo. 
    Args:
       response(dict): json dictionary from a page response 

    Returns:
        buildings(list): list of page response for buildings 
    """   
    photo_objects = []
    for place in response['places']:
        lat,lon = place['location']['lat'],place['location']['lon']
        for photo in place['photos']:
            if check:
                if check_time(photo['time'],date):
                    time_string = datetime.datetime.fromtimestamp(photo['time']).strftime('%Y-%m-%d')
                    photo_objects.append([photo['id'],lat,lon,time_string,photo['big_url']])
            else:
                time_string = datetime.datetime.fromtimestamp(photo['time']).strftime('%Y-%m-%d')
                photo_objects.append([photo['id'],lat,lon,time_string,photo['big_url']])            
    return photo_objects 
        

def place_edit(place):
    """Parses a wikimapia place 
    Args:
       place(dict): json dictionary of a place object 

    Returns:
        (tuple): returns place id, lat,lon, edit time, and userid as a tuple 
    """   
    edit = place['edit_info']
    time_string = datetime.datetime.fromtimestamp(edit['date']).strftime('%Y-%m-%d')
    return (place['id'],place['location']['lat'],
            place['location']['lon'],time_string,edit['user_id'])


def to_geojson(photo_time_response):
    pass

def save_photos(photo_url,photo_id,date=check_time):
    """ Saves the image of a url as a jpeg. 
    Args:
       photo_url(str): url path to a photo
       photo_id(str):  the wikimapia id of said photo
       date(str): a string of a date formatted 'YYYY-MM-DD'

    Returns:
        None
    """   
    location = os.path.realpath(os.path.join(os.getcwd(), 
                                             os.path.dirname(__file__)))
    path = location + "\\images"                                          
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise                                         
    with open(path + "\\" + str(photo_id) + '.jpg','wb') as f:
        f.write(urllib.urlopen(photo_url).read())
    return 
    


def csv_output(rows,filename):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(rows)



if __name__ == "__main__":
    location = os.path.realpath(os.path.join(os.getcwd(), 
                                             os.path.dirname(__file__)))
    cred_path = os.path.join(location,"creds.json")                                         
    with open(cred_path) as data_file: creds = json.load(data_file)   
    key = creds['key']                                     
    lat = 59.924121
    lon = 30.2719319                                    
    e = get_all_pages(lat=lat,lon=lon,radius=1)    
    all_photos = []
    for response in e:
        for place in response['places']:
            for photo in place['photos']:
                all_photos.append(photo)
      

    
    
