# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 14:23:41 2016

@author: aadlandma
"""
import urllib
import requests
import xml.etree.ElementTree as xml
import os 
import datetime
import json 

global flickr_key
global api_key
global api_secret 

fmt = '%Y-%m-%d'
default_date = datetime.datetime.now().strftime(fmt)

def geosearch(lat,lon,radius = 1,date = default_date):
    """ Searches the Flickr API. 
    Args:
        lat  (float): latitude
        lon  (float): longitude
        radius (int): number of kilometers to search 
        date (str): minimum upload date in format 'YYYY-MM-DD'. 
            Defaults to today
    Returns:
        list: returns a list of xml photo elements. 
    """
    url = ("https://api.flickr.com/services/rest/?method=flickr.photos.search"
        "&api_key={0}&min_upload_date={1}&sort=date-posted-desc&has_geo=1&"
        "lat={2}&lon={3}&radius={4}&radius_units=km&"
        "extras=date_upload%2C+date_taken%2C+owner_name%2C+icon_server%2C+"
        "original_format%2C+last_update%2C+geo%2C+tags%2C++o_dims%2Cviews%2C+"
        "url_sq%2C+url_t%2C+url_s%2C+url_q%2C+url_m%2C+url_n%2C+url_z%2C+url_c%"
        "2C+url_l%2C+url_o&format=rest")
    response = urllib.urlopen(url.format(flickr_key,date,lat,lon,radius))
    xml_data = response.read()
    doc = xml.fromstring(xml_data)
    return doc[0]
    
def tag(image_url):
    """ Tags a photo url using the Imagga API. 
    Args:
        image_url(str): url to the image
    Returns:
        list: returns a list of dictionaries formated {tag:confidence}
    """
    response = requests.get('https://api.imagga.com/v1/tagging?url=%s' % image_url,
                        auth=(imagga_key, imagga_secret))
    response_json = response.json()
    return response_json['results'][0]['tags']
    
def scan_tags(tags,search,confidence):
    """ Searches the machine tags for specific tags. 
    Args:
        tags(list): list of dictionaries formated {tag:confidence}
        search(list): list of strings of desired tags
        confidence(float): minimum confidence score 

    Returns:
        bool: returns true if the machine tags have the desired tags
    """
    approved = [x['tag'] for x in tags if x['confidence'] >= confidence]  
    intersection = set(approved).intersection(set(search))
    return 1 if intersection else 0                     

def urls(photo):
    return photo.get('url_z') if photo.get('url_z') else photo.get('url_q')  

def save_photos(photo_url,photo_id,date=default_date):
    """ Saves the image of a url as a jpeg. 
    Args:
        photo_url(str): url path to a photo
        photo_id(str):  the flickr id of said photo
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
    with open(path + "\\" + photo_id + '.jpg','wb') as f:
        f.write(urllib.urlopen(photo_url).read())
    return 






if __name__ == "__main__":
    location = os.path.realpath(os.path.join(os.getcwd(), 
                                             os.path.dirname(__file__)))
    cred_path = os.path.join(location,"creds.json") 
    parameter_path = os.path.join(location,"parameters.json")                                        
    with open(cred_path) as data_file: creds = json.load(data_file)
    with open(parameter_path) as data_file: parameters = json.load(data_file)    
    flickr_key = creds['flickr_key']
    imagga_key = creds['imagga_key']
    imagga_secret = creds['imagga_secret']
    lat = parameters['latitude']
    lon = parameters['longitude']
    radius = parameters['radius']
    date = parameters['date']
    tags = parameters['tags']
    photos = geosearch(lat=lat,lon=lon,radius=radius,date = date)
    for photo in photos:
        photo_url = urls(photo)
        tagged = tag(photo_url)
        if scan_tags(tagged,tags,10):
            save_photos(photo_url,photo.get('id'))
   


