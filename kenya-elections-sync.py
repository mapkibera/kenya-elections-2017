#/usr/bin/python
import urllib, urllib2
import json
import os
from pprint import pprint

def readfile(filename):
  with open(filename, 'r') as f:
    read_data = f.read()
  f.closed
  return read_data

def readjson(filename):
  with open(filename, 'r') as f:
    read_data = json.load(f)
  f.closed
  return read_data

def writefile(file_name, buf):
  if not os.path.exists(os.path.dirname(file_name)):
    try:
        os.makedirs(os.path.dirname(file_name))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

  myFile = open(file_name, 'w')
  myFile.write(buf)
  myFile.close()

def url2file(url,file_name):
  if os.path.isfile(file_name):
    return

  req = urllib2.Request(url)
  try:
    rsp = urllib2.urlopen(req)
  except urllib2.HTTPError, err:
    print str(err.code) + " " + url
    return

  writefile(file_name, rsp.read())

def id2hierarchy(id):
  #     Country[1]:County[3]:Constitiuency[3]:Ward[4]:Polling center[3]:Polling station[2]
  delim = '%2F'

  id = str(id)
  country = id[0:1]
  hierarchy = country
  if (len(id) > 1):
      county = id[1:4]
      hierarchy = hierarchy + delim + country + county

  if (len(id) > 4):
      constituency = id[4:7]
      hierarchy = hierarchy + delim + country + county + constituency

  if (len(id) > 7):
      ward = id[7:11]
      hierarchy = hierarchy + delim + country + county + constituency + ward

  if (len(id) > 11):
      polling_center = id[11:14]
      hierarchy = hierarchy + delim + country + county + constituency + ward + polling_center

  if (len(id) > 14):
      polling_station = id[14:16]
      hierarchy = hierarchy + delim + country + county + constituency + ward + polling_center + polling_station

  return hierarchy


urlbase = 'https://public.rts.iebc.or.ke/jsons/round1/'
filebase = 'data/'

elections_file = 'config/elections.json'
url2file(urlbase + elections_file, filebase + elections_file)
elections = readjson(filebase + elections_file)

for i in range(1, len(elections['elections'])):
  election_name = elections['elections'][i]['id']

  for territory_id in elections['elections'][i]['territories']:

      territory_file = 'config/' + election_name + '/' + territory_id + '.json'
      url2file(urlbase + territory_file, filebase + territory_file)
      territory = readjson(filebase + territory_file)

      for location in territory:
          info_file = 'results/' + election_name + '%2F' + id2hierarchy(location[0]) + '/info.json'
          url2file(urlbase + info_file, filebase + info_file)

          if not os.path.exists(os.path.dirname(filebase + info_file)):
              print info_file
