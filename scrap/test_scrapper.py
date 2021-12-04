#!/usr/bin/env python

import sqlite3

import pytz
import scrapper
import common
import db
import db_init

import random as rnd
import os
import datetime

from typing import Tuple

class Stata:
  def __init__(self):
    self.tot = 0
    self.ok = 0

  def count(self, func):
    log, tot, ok = func()
    self.tot += tot
    self.ok += ok
    if (tot != ok):
      print(log)
      print("Failed: - : "+func.__name__)
    else:
      print("Passed: + : "+func.__name__)

  def summary(self):
    res = -1
    print('\n\t------++++++******++++++------')
    if (self.tot != self.ok):
      print("\t    ("+str(self.ok)+"/"+str(self.tot)+") --- Failed")
      res = 1
    else:
      print("\t    ("+str(self.ok)+"/"+str(self.tot)+") --- Passed")
      res = 0
    print('\t------++++++......++++++------')
    return res

def test(tot: int, ok: int, log: str, is_faled: bool, msg: str) -> Tuple[int,int,str]:
  tot += 1
  ok += 1
  if is_faled:
    ok -= 1
    log += msg
  return tot, ok, log

def test_is_position_ignored():
  tot = 0
  ok = 0

  positions = [
    ('INVESTIGATION Officer', 'officer', True),
    ('   INVESTIGATION Officer    ', 'officer', True),
    ('Investigation Officer', 'officer', True),
    ('Investigation Officer - more info', 'officer', True),
    ('Investigation Officer (more info)', 'officer', True),
    ('Investigation Officer / more info', 'officer', True),
    ('Investigation Officer/more info', 'officer', True),
    ('Investigation Officer in russia', 'officer', True),
    ('Investigation Officer in russia/Australia (preferably)', 'officer', True),
    ('Investigation Officer Assistant', 'officer', True),
    ('Analytical Chemistry - Senior Analyst (24 month Fixed Term), Wollongong NSW', 'chemistry', True),
    ('Developer', 'developer', False),
    ('Developer/some rubish', 'developer', False),
    ('Information Technology Manager', 'information', False),
    ('Cyber Security Specialist - Red Team', 'cyber', False)
  ]
  
  log = ""
  ignore_words = common.load_ignored()
  important_words = common.load_important()
  for p in positions:
    tot += 1
    r = scrapper.is_position_ignored(p[0], ignore_words, important_words)
    if (r[0] != p[1]) or (r[1] != p[2]):
      log += 'test_is_position_ignored: FAIL X '+str(p[0])+' | got: '+str(r)+' | want: '+str((p[1],p[2]))+'\n'
    else:
      ok += 1
      log += 'test_is_position_ignored: PASS | '+str(p[0])+'\n'

  return log, tot, ok

def getCleanGD():
  GD = scrapper.GlobalData()
  GD.db_name = 'test.db'
  GD.log_empty_name = 'test.log'
  GD.log_ignore_name = 'test.log'
  GD.log_not_enough_name = 'test.log'
  GD.localdate = datetime.datetime.now()
  GD.timezone = 'Australia/Melbourne'
  GD.is_first_run = False

  return GD

def getSearchKeys(GD):
  GD.prettykeys, GD.searchkeys = db.get_keywords_dicts('hottesttechs.db')
  GD.compiledkeys, GD.intersectkeys = common.get_searchkeys_variants_compiled(GD.searchkeys)
  return GD

def test_nlinks_increase_with_new_links():
  tot = 0
  ok = 0
  log = ""

  GD = getCleanGD()
  links = []
  ignore_words = []
  important_words = []

  scrapper.args.nostdout = True

  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  if(GD.nlinks != 0):
    log += 'FAIL X for empty link list want GD.nlinks = 0 | got GD.nlinks = '+str(GD.nlinks)
    tot += 1
  
  class linkmock:
    class spanmock:
      def __init__(self,name):
        self.contents = [name]

    def __init__(self,name,href):
      self.span = self.spanmock(name)
      self.href = href+"?uselessparams"
    
    def get(self,key):
      if (key == 'href'):
        return self.href

  original_sleep = common.sleep
  original_get_descr = scrapper.get_description

  scrapper.get_description = lambda path : ""
  common.sleep = lambda : None

  links.append(linkmock('developer','link1'))
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 2
  ok += 2
  if(GD.nlinks != 1):
    log += 'FAIL X one processed link want GD.nlinks = 1 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.visited_jobs != ['link1']):
    log += 'FAIL X one processed link want GD.visited_jobs = [\'link1\'] | got GD.nlinks = '+str(GD.visited_jobs)+"\n"
    ok -= 1


  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 2
  ok += 2
  if(GD.nlinks != 1):
    log += 'FAIL X one repeatedly processed link want GD.nlinks = 1 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.visited_jobs != ['link1']):
    log += 'FAIL X one repeatedly processed link want GD.visited_jobs = [\'link1\'] | got GD.nlinks = '+str(GD.visited_jobs)+"\n"
    ok -= 1

  GD = getCleanGD()

  links.append(linkmock('developer1','link1'))
  GD.visited_jobs.append('link1')
  GD.nlinks += 1

  links.append(linkmock('developer2','link2'))
  links.append(linkmock('developer3','link3'))
  
  links.append(linkmock('ignore_me','link4'))
  ignore_words.append('ignore_me')

  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 4
  ok += 4
  if(GD.nlinks != 4):
    log += 'FAIL X "2p, 1i, 1v, no tech" link want GD.nlinks = 4 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.plinks != 0):
    log += 'FAIL X "2p, 1i, 1v, no tech" link want GD.plinks = 0 | got GD.plinks = '+str(GD.plinks)+"\n"
    ok -= 1
  if(GD.ilinks != 1):
    log += 'FAIL X "2p, 1i, 1v, no tech" link want GD.ilinks = 1 | got GD.ilinks = '+str(GD.ilinks)+"\n"
    ok -= 1
  if(len(GD.visited_jobs) != 3):
    log += 'FAIL X "2p, 1i, 1v, no tech" link want len(GD.visited_jobs) = 3 | got len(GD.visited_jobs) = '+str(len(GD.visited_jobs))+"\n"
    ok -= 1

  GD = getCleanGD()
  GD2 = getSearchKeys(GD)
  GD.prettykeys, GD.searchkeys, GD.compiledkeys, GD.intersectkeys = GD2.prettykeys, GD2.searchkeys, GD2.compiledkeys, GD2.intersectkeys

  links = []
  links.append(linkmock('developer1','link1'))
  scrapper.get_description = lambda path : " aws go js "
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 3
  ok += 3
  if(GD.nlinks != 1):
    log += 'FAIL X "1p.v1" not enough techs link want GD.nlinks = 1 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.plinks != 0):
    log += 'FAIL X "1p.v1" not enough techs link want GD.plinks = 0 | got GD.plinks = '+str(GD.plinks)+"\n"
    ok -= 1
  if(GD.ilinks != 0):
    log += 'FAIL X "1p.v1" not enough techs link want GD.ilinks = 0 | got GD.ilinks = '+str(GD.ilinks)+"\n"
    ok -= 1

  GD = getCleanGD()
  GD.prettykeys, GD.searchkeys, GD.compiledkeys, GD.intersectkeys = GD2.prettykeys, GD2.searchkeys, GD2.compiledkeys, GD2.intersectkeys

  links = []
  links.append(linkmock('developer1','link1'))
  scrapper.get_description = lambda path : " aws go js vue react node "
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 3
  ok += 3
  if(GD.nlinks != 1):
    log += 'FAIL X "1p.v2" not enough techs link want GD.nlinks = 1 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.plinks != 1):
    log += 'FAIL X "1p.v2" not enough techs link want GD.plinks = 1 | got GD.plinks = '+str(GD.plinks)+"\n"
    ok -= 1
  if(GD.ilinks != 0):
    log += 'FAIL X "1p.v2" not enough techs link want GD.ilinks = 0 | got GD.ilinks = '+str(GD.ilinks)+"\n"
    ok -= 1

  GD = getCleanGD()
  GD.prettykeys, GD.searchkeys, GD.compiledkeys, GD.intersectkeys = GD2.prettykeys, GD2.searchkeys, GD2.compiledkeys, GD2.intersectkeys

  links = []
  links.append(linkmock('developer1','link1'))
  scrapper.get_description = lambda path : " aws go js vue react node c c++ c# .net azure "
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  tot += 3
  ok += 3
  if(GD.nlinks != 1):
    log += 'FAIL X "1p.v3" link want GD.nlinks = 1 | got GD.nlinks = '+str(GD.nlinks)+"\n"
    ok -= 1
  if(GD.plinks != 1):
    log += 'FAIL X "1p.v3" link want GD.plinks = 1 | got GD.plinks = '+str(GD.plinks)+"\n"
    ok -= 1
  if(GD.ilinks != 0):
    log += 'FAIL X "1p.v3" link want GD.ilinks = 0 | got GD.ilinks = '+str(GD.ilinks)+"\n"
    ok -= 1

  scrapper.get_description = lambda path : ""
  common.sleep = original_sleep
  scrapper.get_description = original_get_descr
  scrapper.args.nostdout = False
  return log,tot,ok

def test_np_links_stored_correctly():
  tot = 0
  ok = 0
  log = ""

  tot += 2
  ok += 2
  devs = rnd.randint(0,20)

  n0, d0 = db.read_npi_links('test.db')
  try:
    db.write_npi_links('test.db',100,devs)
  except:
    log += 'FAIL X write to db failed\n'
    ok -= 1
  
  n,d = 0,0
  try:
    n, d = db.read_npi_links('test.db')
  except:
    log += 'FAIL X read from db failed\n'
    ok -= 1

  tot += 2
  ok += 2
  if (n != 100+n0):
    log += f'FAIL X stored number of jobs | want db.n = {100+n0} | got db.n = {n}\n'
    ok -= 1
  if (d != devs+d0):
    log += f'FAIL X stored number of jobs | want db.d = {devs+d0} | got db.d = {d}\n'
    ok -= 1

  return log, tot, ok

def test_is_position_contains_techs():
  log = ''
  tot = 0
  ok = 0
  GD = getCleanGD()
  GD = getSearchKeys(GD)
  
  tot += 1
  ok += 1
  description = ''
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )

  if (is_contain_any):
    ok -= 1
    log += 'FAIL | empty description | want contain = False | got contain = '+str(is_contain_any)+"\n"
  if (len(res) > 0):
    ok -= 1
    log += 'FAIL | empty description | want res = {} | got res = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = 'balblablalbla Java sfasdfdas'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )

  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 1 position, spaces, middle | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (45 not in res):
    ok -= 1
    log += 'FAIL | 1 position, spaces, middle | want res[45] = Java | got res[45] = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = ' Java sfasdfdas'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )
  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 1 position, spaces, string start | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (45 not in res):
    ok -= 1
    log += 'FAIL | 1 position, spaces, string start | want res = {45:Java} | got res = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = 'C++ /PythON, AWS; RHEl'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )
  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 4 positions, mix | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (res != {1: 'Python', 2: 'Amazon Web Services', 116: 'C++', 151: 'Red Hat Linux'}):
    ok -= 1
    log += 'FAIL | 4 positions, mix | want res = {1: \'Python\', 2: \'Amazon Web Services\', 116: \'C++\', 151: \'Red Hat Linux\'} | got res = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = 'Java, Java Script'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )
  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 2 positions, name intersection | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (res != {45: 'Java', 35: 'JavaScript'}):
    ok -= 1
    log += 'FAIL | 2 positions, name intersection | want res = {45: \'Java\', 35: \'JavaScript\'} | got res = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = 'Java Script'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )
  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 1 position, name intersection | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (res != {35: 'JavaScript'}):
    ok -= 1
    log += 'FAIL | 1 position, name intersection | want res = {35: \'JavaScript\'} | got res = '+str(res)+"\n"

  tot += 2
  ok += 2
  description = 'Java, JavaScript'
  is_contain_any, res = scrapper.is_position_contains_techs(description,
    GD.prettykeys,
    GD.searchkeys,
    GD.compiledkeys,
    GD.intersectkeys
  )
  if (not is_contain_any):
    ok -= 1
    log += 'FAIL | 2 positions, name intersection | want contain = True | got contain = '+str(is_contain_any)+"\n"
  if (res != {45: 'Java', 35: 'JavaScript'}):
    ok -= 1
    log += 'FAIL | 2 positions, name intersection | want res = {45: \'Java\', 35: \'JavaScript\'} | got res = '+str(res)+"\n"

  return log, tot, ok

def db_clear_vac(conn,c):
  db.cmd(c,'DELETE FROM vacancies')
  db.cmd(c,'DELETE FROM groups')
  conn.commit()

def get_top():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()

  db.cmd(c,"SELECT COUNT(*) FROM techs")
  total_techs = c.fetchall()[0][0]
  techs = []
  tid = rnd.randint(1,total_techs-20)
  for i in range(5):
    db.cmd(c,f"SELECT id,name FROM techs WHERE id={tid+i*3}")
    techs.append(c.fetchall()[0])
  months = [10,11,12,1,2]
  vacs_d = {}

  for i in range (100):
    year = 0
    mnth = months[rnd.randint(0,len(months)-1)]
    day  = rnd.randint(1,28)
    if mnth < 5:
      year = '2021'
    else:
      year = '2020'
    date = '2020-'+str(mnth) if mnth > 5 else '2021-0'+str(mnth)
    daystr = '-'+str(day) if (day>9) else '-0'+str(day)
    date += daystr
    vacs_d[date] = {}
  for t in techs:
    for d in vacs_d:
      vacs_d[d][t[0]] = 0

  for d in vacs_d:
    for t in techs:
      v = rnd.randint(0,10)
      vacs_d[d][t[0]] += v

  conn.commit()
  conn.close()
  return techs,vacs_d

def del_leq_zero(tmpdict):
  delids = []
  for t in tmpdict:
    if (tmpdict[t] < 1):
        delids.append(t)
  for did in delids:
    del tmpdict[did]
  return tmpdict

def get_amount_fromdb(c,table_name,date_field):
  qstr=f"SELECT * FROM {table_name} WHERE check_date = {date_field}"
  db.cmd(c, qstr)
  res = c.fetchall()
  got = {}
  for r in res:
    got[r[1]] = r[3]
  return got

def test_store_data():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()

  log = ''
  tot = 0
  ok = 0

  db_clear_vac(conn, c)
  techs, vacs_d = get_top()
  lastkey = ''
  for d in vacs_d:
    lastkey = d
    tmp = dict(vacs_d[d])
    tmp = del_leq_zero(tmp)
    while (len(tmp) > 0):
      db.store_data('test.db',tmp,date="'"+d+"'")
      for t in tmp:
        tmp[t] -= 1
      tmp = del_leq_zero(tmp)

  for d in vacs_d:
    got = get_amount_fromdb(c,f'vacancies',f"DATE('{d}')")
    tot += 1
    ok += 1
    if (del_leq_zero(vacs_d[d]) != got):
      ok -= 1
      log += f'FAIL | vacancies in db differ from actual | want res=' + \
        str(del_leq_zero(vacs_d[d]))+' | got res='+str(got)+"\n"

  def get_tmp_dict():
    groups_tmp = {}
    for t1 in techs:
      groups_tmp[t1[0]] = {}
      for t2 in techs:
        if t1[0] < t2[0]:
          groups_tmp[t1[0]][t2[0]] = 0
    return groups_tmp
  def tmp_dict_clean_leq_zero(groups_tmp):
    todel1 = []
    for t1 in techs:
      todel2 = []
      for t2 in techs:
        if t1[0] < t2[0]:
          if (groups_tmp[t1[0]][t2[0]] == 0):
            todel2.append(t2[0])
      for did2 in reversed(todel2):
        del groups_tmp[t1[0]][did2]
      if len(groups_tmp[t1[0]]) == 0:
        todel1.append(t1[0])
    for did1 in reversed(todel1):
      del groups_tmp[did1]
    return groups_tmp

  groups_want = {}
  for d in vacs_d:
    groups_want[d] = get_tmp_dict()

  for d in vacs_d:
    for t1 in vacs_d[d]:
      for t2 in vacs_d[d]:
        if (t1 < t2):
          groups_want[d][t1][t2] += min(vacs_d[d][t1],vacs_d[d][t2])

  groups_got = {}
  for d in vacs_d:
    groups_want[d] = tmp_dict_clean_leq_zero(groups_want[d])

    qstr=f"SELECT * FROM groups WHERE check_date='{d}'"
    db.cmd(c, qstr)
    res = c.fetchall()
    groups_got[d] = {}
    for r in res:
      if r[1] not in groups_got[d]:
        groups_got[d][r[1]] = {}
      groups_got[d][r[1]][r[2]] = r[3]

    tot += 1
    ok += 1
    if (groups_want[d] != groups_got[d]):
      ok -= 1
      log += f'FAIL | groups differ in db from actual | {d}'\
        f' | want res={groups_want[d]} | got res={groups_got[d]}\n'

  return log, tot, ok

def test_local_time_is_different_from_desired():
  log = ''
  tot = 0
  ok = 0

  # ie actually local for the server (will be also local for db)
  # will pretend that I want to store at any different TZ
  timehave = datetime.datetime.now()
  datehave = timehave.isoformat()[:timehave.isoformat().find('T')]
  timewant = None
  datewant = None
  zonewant = None
  for tz in pytz.all_timezones:
    timewant = datetime.datetime.now().astimezone(pytz.timezone(tz))
    datewant = timewant.isoformat()[:timewant.isoformat().find('T')]
    zonewant = tz
    if (datehave != datewant):
      break

  tot, ok, log = test(tot, ok, log, (datehave == datewant),
    f'FAIL X pre-test failed X test is impossible as the local date is the same as desired')

  class linkmock:
    class spanmock:
      def __init__(self,name):
        self.contents = [name]

    def __init__(self,name,href):
      self.span = self.spanmock(name)
      self.href = href+"?uselessparams"
    
    def get(self,key):
      if (key == 'href'):
        return self.href

  original_sleep = common.sleep
  original_get_descr = scrapper.get_description

  scrapper.args.nostdout = True
  scrapper.get_description = lambda path : ""
  common.sleep = lambda : None

  GD = getCleanGD()
  GD = getSearchKeys(GD)
  GD.localdate = timehave
  GD.timezone = zonewant

  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  db_clear_vac(conn,c)
  db.cmd(c, f'SELECT * FROM vacancies WHERE check_date="{datewant}"')
  amount_of_vacs_before = len(c.fetchall())

  links = []
  ignore_words = []
  important_words = []
  links.append(linkmock('developer1','link1'))
  scrapper.get_description = lambda path : " aws go js vue react node c c++ c# .net azure "
  amount_of_vacs_want = len(scrapper.get_description('adsf').split())
  
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)

  db.cmd(c, f'SELECT * FROM vacancies WHERE check_date="{datewant}"')
  amount_of_vacs_have = len(c.fetchall())

  tot, ok, log = test(tot, ok, log,(amount_of_vacs_have-amount_of_vacs_before != amount_of_vacs_want),
    f'FAIL X server with different timezone | '
    f'want = len(vacancies[{datewant}]) == {amount_of_vacs_want} | '
    f'have = len(vacancies[{datewant}]) == {amount_of_vacs_have-amount_of_vacs_before} | ')

  common.sleep = original_sleep
  scrapper.get_description = original_get_descr
  scrapper.args.nostdout = False

  return log, tot, ok

def test_last_checked_url():
  log = ''
  tot = 0
  ok = 0

  conn = sqlite3.connect('test.db')
  c = conn.cursor()

  original_sleep = common.sleep
  original_get_descr = scrapper.get_description
  scrapper.args.nostdout = True
  scrapper.get_description = lambda path : ""
  common.sleep = lambda : None
  class linkmock:
    class spanmock:
      def __init__(self,name):
        self.contents = [name]

    def __init__(self,name,href):
      self.span = self.spanmock(name)
      self.href = href+"?uselessparams"
    
    def get(self,key):
      if (key == 'href'):
        return self.href

  GD = getCleanGD()
  GD = getSearchKeys(GD)
  GD.is_first_run = True
  GD.visited_jobs = []

  n0,p0 = db.read_npi_links('test.db')
  # 1) there is no previous checked url (initial case)
  # -> check all possible jobs
  # -> put first url as a last checked  
  links = []
  for i in range(5):
    links.append(linkmock(f'developer{i}',f'link{i}'))
  ignore_words = []
  important_words = []
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  new_last_link = db.read_stop_urls('test.db')
  n1,p1 = db.read_npi_links('test.db')
  tot,ok,log = test(tot,ok,log,(new_last_link != ['link0', 'link1']),
    f'FAIL X fresh cycle of checks should set the stop_urls'
    f' | want general_info[0][1] = [\'link0\', \'link1\'] | got general_info[0][1] = {new_last_link}')
  tot,ok,log = test(tot,ok,log,(n1 != n0+5),
    f'FAIL X there is no stop_urls should process all links'
    f' | want GD.n = {n0+5} | got GD.n = {n1}')
  tot,ok,log = test(tot,ok,log,(p1 != p0),
    f'FAIL X there is no dev links should be zero'
    f' | want GD.n = {p0} | got GD.n = {p1}')

  # second iteration should not rewrite those links
  links = []
  for i in range(5):
    links.append(linkmock(f'developer{5+i}',f'link{5+i}'))
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  new_last_link = db.read_stop_urls('test.db')
  n2,p2 = db.read_npi_links('test.db')
  tot,ok,log = test(tot,ok,log,(new_last_link != ['link0', 'link1']),
    f'FAIL X repeating cycle should not update the stop_urls'
    f' | want general_info[0][1] = [\'link0\', \'link1\'] | got general_info[0][1] = {new_last_link}')
  tot,ok,log = test(tot,ok,log,(n2 != n1+5),
    f'FAIL X there is no stop_urls should process all links'
    f' | want GD.n = {n1+5} | got GD.n = {n2}')
  tot,ok,log = test(tot,ok,log,(p2 != p1),
    f'FAIL X there is no dev links should be zero'
    f' | want GD.n = {p1} | got GD.n = {p2}')

  # 2) there is a url and it is far behind (no more in the current list)
  # -> check all possible jobs
  # -> put first url as a last checked
  GD.is_first_run = True
  GD.nlinks = 0
  GD.visited_jobs = []
  links = []
  for i in range(5):
    links.append(linkmock(f'developer{10+i}',f'link{10+i}'))
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  new_last_link = db.read_stop_urls('test.db')
  n3,p3 = db.read_npi_links('test.db')
  tot,ok,log = test(tot,ok,log,(new_last_link != ['link10', 'link11']),
    f'FAIL X new cycle on existiong db should update the stop_urls'
    f' | want general_info[0][1] = [\'link10\', \'link11\'] | got general_info[0][1] = {new_last_link}')
  tot,ok,log = test(tot,ok,log,(n3 != n2+5),
    f'FAIL X there is no stop_urls should process all links'
    f' | want GD.n = {n2+5} | got GD.n = {n3}')
  tot,ok,log = test(tot,ok,log,(p3 != p0),
    f'FAIL X there is no dev links should be zero'
    f' | want GD.n = {p0} | got GD.n = {p3}')

  # 3) there is a url and it is in the middle of the list
  # -> check all the jobs before this url
  # -> put first url as a last checked
  GD.is_first_run = True
  GD.nlinks = 0
  GD.visited_jobs = []
  links = []
  for i in range(6):
    links.append(linkmock(f'developer{7+i}',f'link{7+i}'))
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  new_last_link = db.read_stop_urls('test.db')
  n4,p4 = db.read_npi_links('test.db')
  tot,ok,log = test(tot,ok,log,(new_last_link != ['link7', 'link8']),
    f'FAIL X new cycle on existiong db should update the stop_urls'
    f' | want general_info[0][1] = [\'link7\', \'link8\'] | got general_info[0][1] = {new_last_link}')
  tot,ok,log = test(tot,ok,log,(n4 != n3+3),
    f'FAIL X there is stop_urls should process only some links'
    f' | want GD.n = {n3+3} | got GD.n = {n4}')
  tot,ok,log = test(tot,ok,log,(p4 != p0),
    f'FAIL X there is no dev links should be zero'
    f' | want GD.n = {p0} | got GD.n = {p4}')

  # 4) there is a url and it is the very first in the links
  # -> abort stright away
  # -> put first url as a last checked
  GD.is_first_run = True
  GD.nlinks = 0
  GD.visited_jobs = []
  links = []
  for i in range(10):
    links.append(linkmock(f'developer{7+i}',f'link{7+i}'))
  GD = scrapper.process_chunk(GD,links,ignore_words,important_words)
  new_last_link = db.read_stop_urls('test.db')
  n5,p5 = db.read_npi_links('test.db')
  tot,ok,log = test(tot,ok,log,(new_last_link != ['link7', 'link8']),
    f'FAIL X new cycle on the same set of links should not update stop_urls'
    f' | want general_info[0][1] = [\'link7\', \'link8\'] | got general_info[0][1] = {new_last_link}')
  tot,ok,log = test(tot,ok,log,(n5 != n4),
    f'FAIL X there is stop_urls in the very start should not process any links'
    f' | want GD.n = {n4} | got GD.n = {n5}')
  tot,ok,log = test(tot,ok,log,(p5 != p0),
    f'FAIL X there is no dev links should be zero'
    f' | want GD.n = {p0} | got GD.n = {p5}')

  return log, tot, ok

if __name__ == "__main__":
  stata = Stata()
  db_init.init_db('test.db')
  time = datetime.datetime.now()
  seed = time.second*10000+time.minute*100+time.hour
  # seed = 230117
  rnd.seed(seed)
  print(f' >> testing with seed={seed}')

  stata.count(test_is_position_ignored)
  stata.count(test_nlinks_increase_with_new_links)
  stata.count(test_np_links_stored_correctly)
  stata.count(test_is_position_contains_techs)
  stata.count(test_store_data)
  stata.count(test_local_time_is_different_from_desired)
  stata.count(test_last_checked_url)

  os.remove('test.db')
  os.remove('test.log')
  exit(stata.summary())