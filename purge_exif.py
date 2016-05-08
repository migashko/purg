#!/usr/bin/python
# -*- coding: utf-8 -*-

# для устаовки PIL
# pip-2.7 install Pillow

import sys
import datetime
import time
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import httplib
import json

def _get_if_exist(data, key):
    if key in data:
        return data[key]
                
    return None
        
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)
 
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)
 
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)
 
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
 
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
 
    return exif_data
 
 
def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None
 
    if "GPSInfo" in exif_data:          
        gps_info = exif_data["GPSInfo"]
 
        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
 
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat
 
            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
 
    return lat, lon


def get_datetime(exif_data):    
  if "DateTimeOriginal" in exif_data:
    strtime= exif_data["DateTimeOriginal"]
    return datetime.datetime.strptime(strtime, "%Y:%m:%d %H:%M:%S")
  return None

def load_exif_data(path):
  try:
    image = Image.open(path)
    return get_exif_data(image)
  except:
    return None
  
# (55.75758472222222, 37.542615)
# http://maps.googleapis.com/maps/api/geocode/json?latlng=55.75758472222222,37.542615
def get_geo_items(path):
  try:
    image = Image.open(path)
    exif_data = get_exif_data(image)
    gps = get_lat_lon(exif_data)
    if len(gps)==2:
      if not gps[0] or not gps[1]:
        print("exif invalid geo")
        return None
      url = "/maps/api/geocode/json?latlng={0},{1}&language=ru".format(gps[0],gps[1])
      print("maps.googleapis.com" + url)
      h1 = httplib.HTTPConnection("maps.googleapis.com")
      while True:
        h1.request("GET", url)
        resp = h1.getresponse()
        data = resp.read()
        js = json.loads(data)
        if js["status"]=="OVER_QUERY_LIMIT":
          print("Google жмот. Ждем 1 секунд")
          time.sleep(1)
          continue
        break
      return js['results']
    else:
      print("exif no geo")
  except:
    pass
  return None
  

  
  
if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit(0)
  path=sys.argv[1]
  print (path)
  data = load_exif_data(path)
  ll = get_lat_lon(data)
  dt = get_datetime(data)
  
  print(ll)
  print(dt)
  
  goo_json = get_geo_items(path)
  print( json.dumps(goo_json) )
