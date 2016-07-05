# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 18:44:21 2015

@author: aadlandma
"""
import psycopg2
import pandas as pd
import time 
connection = psycopg2.connect("dbname=SocialMedia user=postgres password=postgres host=localhost")
cursor = connection.cursor()
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

def reset_cursor():
    cursor = connection.cursor()

import sys, urllib
import xml.etree.ElementTree as xml
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
API_KEY = u'' # put API KEY here
HOST = 'https://api.flickr.com'
API = '/services/rest'

def flickr_search(woe_id, page, min_date_taken,max_date_taken):
   ''' a function that seraches the flickr api for photos usin woe_id,page,min and max date 
       returns xml as a response '''
   method = 'flickr.photos.search'
   args = '&woe_id=%s&sort=%s&page=%i&extras=%s%s%s&min_taken_date=%s&max_taken_date=%s' % (woe_id, 'date-taken-asc', page, 'geo','%2Ctags', '%2Cdate_taken',min_date_taken, max_date_taken)
   url = '%s%s/?&method=%s&api_key=%s&%s' % (HOST, API, method,API_KEY, args)
   u = urllib.urlopen(url)
   response = u.read() # get an XML response from flickr
   return response

 
def parse_xml(response, data=None):
   '''a function to parse the xml response from flick's search method. returns a tuple of the current page, number of pages and photo tuples''' 
   if data == None:
       data=[]
   doc = xml.fromstring(response)
   photos = doc[0]
   page = photos.get('page')
   num_pages = photos.get('pages')
   total_photos = photos.get('total')
   for photo in photos:
      photo_id = photo.get('id')
      photo_woe_id = photo.get('woeid')
      photo_longitude = photo.get('longitude')
      photo_latitude = photo.get('latitude')
      photo_tags = photo.get('tags')
      photo_title = photo.get('title')
      date_created = photo.get('datetaken')
      ownerid = photo.get('owner')
      text = photo_tags + photo_title
      # text.encode('utf-8')
      data.append((photo_id,photo_woe_id, photo_longitude, photo_latitude,date_created,ownerid, text))
   return (page, num_pages, total_photos, data)


def complete_search(woe_id, min_date_taken, max_date_taken,max_num_pages=sys.maxint):
   '''iterate through all search pages (or until the optional max_num_pages parameter) 
   returns: a tuple of number of pages retrieved, total number of pages, total number of photos available, photo data tuple list'''
   page_counter = 1
   total_pages = -1
   photo_data = []
   while ((page_counter < total_pages or page_counter == 1) and page_counter <= max_num_pages):
      response = flickr_search(woe_id, page_counter, min_date_taken,max_date_taken)
      (page, num_pages, total_photos, photo_data) = parse_xml(response, photo_data)
      total_pages = int(num_pages)
      total_photos = int(total_photos)
      page_counter += 1
   return (page_counter-1, total_pages, total_photos, photo_data)


def build_csv_str(photo_data):
   ''' function to build a bar delimited file from the xml response'''
   for line in photo_data:
       cursor.execute("INSERT INTO flickr VALUES (%s,%s,%s,%s,%s,%s,%s);", (line[0],line[1],line[2],line[3],line[4],line[5],line[6]))

   connection.commit()

def iter_month(start,end):
    (pages_ret, total_pages, total_photos, photo_data) = complete_search('	55875320', start,end, 100)
    build_csv_str(photo_data)
    return total_pages 



starts = pd.date_range('2005-01-01','2016-06-15',freq='2D')
ends = pd.date_range('2005-01-02','2016-06-16',freq='2D')
max_pages = 3600 
page_counter = 0 

for i in range(len(starts)):
    start = starts[i].strftime('%Y-%m-%d')
    end = ends[i].strftime('%Y-%m-%d')
    page_counter += iter_month(start,end)
    if page_counter >= max_pages:
        page_counter = 0
        print "sleeping"
        time.sleep(3600)
        print "done sleeping"
    
    
connection.close()