#!/usr/bin/env python
from datetime import date
import random
import time
import re
import json
import os.path
import pytz

def load(name):
  arr = []
  with open(name, 'r') as f:
    arr = f.readlines()
    for i in range(len(arr)):
      arr[i] = arr[i].strip('\n')
  return arr

def load2D(name):
  arr = [[]]
  with open(name, 'r') as f:
    arr = f.readlines()
    for i in range(len(arr)):
      if (arr[i].find('~') != -1):
        arr[i] = arr[i].split('~')
        for j in range(len(arr[i])):
          arr[i][j] = arr[i][j].strip('\n')
      else:
        arr[i] = arr[i].strip('\n')
  return arr

def dump(log, name):
  with open(name, 'a+') as f:
    f.write('\n'.join(log))
  return

def sleep_exact(sleep_time):
  time.sleep(sleep_time)

def sleep(log=True):
  sleep_time = 5*(1 + 2*random.random())
  print(' >> sleep: '+'{:.2f}'.format(sleep_time)+'s')
  time.sleep(sleep_time)
  return None

def fstr(number, digits):
  return ('{:.'+str(digits)+'f}').format(number)

def get_searchkeys_variants_compiled(searchkeys):
  prefixes = ['\ ', '/', '\\\\', ',', '\.','-','\)','\(',';']
  suffixes = prefixes[:]
  
  prefixes.append('^')
  suffixes.append('$')
  
  compiled = {}
  allrawpatterns = {}

  for key in searchkeys:
    pattern = ''
    rawpattern = ''
    for p in prefixes:
      for s in suffixes:
        pattern += p+re.escape(key)+s+"|"
        if (p == '^') and (s == '$'):
          rawpattern += "\n"+key+"\n"+"|"
        elif (p == '^'):
          rawpattern += "\n"+key+s+"|"
        elif (s == '$'):
          rawpattern += p+key+"\n"+"|"
        else:
          rawpattern += p+key+s+"|"
    allrawpatterns[key] = rawpattern
    compiled[key] = re.compile(pattern[:-1],flags=re.IGNORECASE|re.MULTILINE)

  intersections = {}

  intersFileName = 'intersections.json'
  timeout = 12*60*60
  if (not os.path.isfile(intersFileName)) or (time.time() > (os.path.getmtime(intersFileName)+timeout)):
    for t1 in searchkeys:
      for t2 in searchkeys:
        if t1 != t2:
          matchObj = compiled[t2].search(allrawpatterns[t1])
          if matchObj != None:
            if t2 not in intersections:
              intersections[t2] = [t1]
            else:
              intersections[t2].append(t1)
            break
    with open(intersFileName, 'w') as f:
      json.dump(intersections, f)

  else:
    with open(intersFileName, 'r') as f:
      intersections = json.load(f)

  return compiled, intersections

def get_array_lower(array):
  for i in range(len(array)):
    array[i] = array[i].lower()
  return array

def load_ignored():
  l = load('ignore.txt')
  l = get_array_lower(l)
  return l

def load_important():
  l = load('important.txt')
  l = get_array_lower(l)
  return l

def as_write_date_from_timezone(datetime: date, timezone:str) -> str:
  newdt = datetime.astimezone(pytz.timezone(timezone))
  return f"'{newdt.isoformat()[:newdt.isoformat().find('T')]}'"