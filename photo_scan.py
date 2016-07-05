# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 15:03:06 2016

@author: aadlandma
"""
from sklearn.cluster import DBSCAN as DBSCAN
from math import radians, cos, sin, asin, sqrt
from numpy import array,zeros
from random import randint
import psycopg2

try:
    conn = psycopg2.connect("dbname='SocialMedia' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"

cur = conn.cursor()
### Compute distance clusters first #### 
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) returned as kilometers 
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km
    
def cluster_lists(db,labels):
    cluster_lists = []
    cluster_ids = list(set(list(db)))
    for j in cluster_ids:
        if j != -1:
            current_list = []
            for i in range(len(db)):
                if db[i] ==j:
                    current_list.append(labels[i])
            cluster_lists.append(current_list)
    return cluster_lists
    
cur.execute("""Select photo_id,photo_longitude,photo_latitude from russia_flickr limit 10000""")
rows = cur.fetchall()
labels = [row[0] for row in rows]

ResultArray = array([[row[1],row[2]] for row in rows])


N = ResultArray.shape[0]
distance_matrix = zeros((N, N))
for i in xrange(N):
    for j in xrange(N):
        lati, loni = ResultArray[i]
        latj, lonj = ResultArray[j]
        distance_matrix[i, j] = haversine(loni, lati, lonj, latj)
        distance_matrix[j, i] = distance_matrix[i, j]
        
spatial_scan = DBSCAN(eps=.5,min_samples=10, metric='precomputed', algorithm='auto', 
                      leaf_size=30, p=None, random_state=None)
spatial_clusters = spatial_scan.fit_predict(distance_matrix)

sql = """INSERT INTO russia_clusters
        SELECT %s,* FROM russia_flickr 
        WHERE photo_id IN %s"""
            

labeled_clusters = cluster_lists(spatial_clusters,labels)
for cluster in labeled_clusters:
    uuid = randint(10000, 99999)
    cur.execute(sql, (uuid,tuple(cluster)))
    conn.commit() 