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

  print url
  req = urllib2.Request(url)
  try:
    rsp = urllib2.urlopen(req)
  except urllib2.HTTPError, err:
    print str(err.code) + " " + url
    return

  writefile(file_name, rsp.read())

urlbase = 'https://public.rts.iebc.or.ke/jsons/round1/'
filebase = 'data/'
elections_file = 'config/elections.json'
location_hierarchy = ['Country', 'County', 'Constituency', 'Ward', 'Polling Center', 'Polling Station']
levels = ["Level_1","Level_2","Level_3","Level_4","Level_5","Level_6"]

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

def compile_election_territory(election_name, territory_level):
  results = {}
  parties = {}
  locations = {}
  csv = ""
  locations = build_location_lookup(election_name)

  # Read results files
  territory_file = 'config/' + election_name + '/' + 'Level_' + territory_level + '.json'
  territory = readjson(filebase + territory_file)
  for location in territory:

    results[location[0]] = {}

    info_file = 'results/' + election_name + '%2F' + id2hierarchy(location[0]) + '/info.json'
    if os.path.exists(os.path.dirname(filebase + info_file)):
      info = readjson(filebase + info_file)

      for party in info['results']['parties']:
        results[location[0]][party['name']] = party['votes']['presential'] + party['votes']['absentee'] + party['votes']['international'] + party['votes']['special']
        parties[party['name']] = ''

  p = parties.keys()
  p.sort()
  parties = p

  # construct csv
  header = 'id'
  for i in range(2,int(territory_level)+1):
      header = header + ',' + location_hierarchy[i-1]
  for party in parties:
      header = header + ',' + party
  csv = header + "\n"

  for location in results:
      line = str(location)
      line = line + ',' + locations[location][3]

      for party in parties:
          line = line + ',' + str(results[location][party])

      csv = csv + line + "\n"

  return csv

def build_location_lookup(election_name):
  locations = {}
  elections = readjson(filebase + elections_file)
#  for territory_id in elections['elections'][election_name]['territories']:
  for territory_id in levels:
    territory_file = 'config/' + election_name + '/' + territory_id + '.json'
    territory = readjson(filebase + territory_file)
    for location in territory:
      locations[location[0]] = location

  for location in locations:
    locations[location].append(locations[location][1])
    parent = locations[location][2]
    while (parent > 1):
      locations[location][3] = locations[parent][1] + ',' + locations[location][3]
      parent = locations[parent][2]
  return locations

def scrape():
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
scrape()
#print compile_election_territory('Kenya_Elections_Presidential', '4')
