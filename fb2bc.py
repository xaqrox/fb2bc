#!/usr/bin/python
import requests
import xml.etree.ElementTree as ET
import time
import datetime

def tagText(tree, tag):
  return tree.find(tag).text

def fbapi(params):
  response = requests.get(fullUrl, params=params)
  return ET.fromstring(response.text.encode("utf-8"))

def timeconvert(totalseconds):
  hours, minutes, seconds = 0, 0, 0
  if totalseconds >= 3600:
    hours = totalseconds / 3600
    minutes = totalseconds % 3600 / 60
    seconds = totalseconds % 60
  elif totalseconds >= 60:
    minutes = totalseconds / 60
    seconds = totalseconds % 60
  else:
    seconds = totalseconds
  
  return '%dh%dm%ds' % (hours, minutes, seconds)
  

# define some constants
baseUrl = 'http://radcampaign.fogbugz.com/'
userEmail = raw_input("What's your FogBugz user email? ")
userPwd = raw_input("What's your password? ")

# get api info
APIInfo = requests.get(baseUrl + 'api.xml')

parsedAPI = ET.fromstring(APIInfo.text)

apiUrl = parsedAPI.find('url').text

# full target url
fullUrl = baseUrl + apiUrl

# build get request
params = {
  'cmd' : 'logon',
  'email' : userEmail,
  'password' : userPwd
}

token =  tagText(fbapi(params), 'token')

year = raw_input("Start year (YYYY): ")
month = raw_input("Start month (MM): ")
day = raw_input("Start day (DD): ")
hour = raw_input("Start hour (HH, 00-23): ")
minute = raw_input("Start minute (mm): ")

dtStart = '%s-%s-%sT%s:%s:00R' % (year, month, day, hour, minute)
params = {
  'cmd' : 'listIntervals',
  'token' : token,
  'dtStart' : dtStart,
  #'dtEnd' : '2013-09-26T14:00:00R'
}

#print ET.fromstring(response.text).find('token').text
xmlintervals = fbapi(params).find('intervals')
intervals = {} 
for child in xmlintervals:
  intervals[tagText(child, 'ixInterval')] = {
    'case' : tagText(child, 'ixBug'),
    'start' : tagText(child, 'dtStart'),
    'end' : tagText(child, 'dtEnd'),
  }

caseIds = [intervals[i]['case'] for i in intervals]

params = {
  'cmd' : 'search',
  'q' : ','.join(set(caseIds)),
  'cols' : 'sProject',
  'token' : token
}


xmlcases = fbapi(params).find('cases')
cases = {}
for case in xmlcases:
  cases[case.attrib['ixBug']] = tagText(case, 'sProject')

projects = {}
for i in intervals:
  project = cases[intervals[i]['case']]
  if project in projects:
    projects[project].append(intervals[i])
  else:
    projects[project] = [intervals[i]]

fbTimeFormat = '%Y-%m-%dT%H:%M:%SZ'
myTimeFormat = '%Y-%m-%d %H:%M:%S'
totals = {}
for p in projects:
  print p
  total = 0
  for interval in projects[p]:
    startTime = time.strptime(interval['start'], fbTimeFormat)
    endTime = time.strptime(interval['end'], fbTimeFormat)

    seconds = (time.mktime(endTime) - time.mktime(startTime))

    timestring = timeconvert(seconds)
      
    # print '%s - %s : %s' % (time.strftime(myTimeFormat, startTime), time.strftime(myTimeFormat, endTime), timestring)
    total = total + seconds
  print 'total = %s\n' % timeconvert(total)
