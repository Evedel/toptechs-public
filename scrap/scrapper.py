#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import os
import re
import datetime
import argparse

import db
import common
import db_init

parser = argparse.ArgumentParser(description='Do some durty deeds...')
parser.add_argument('--nostdout', help='should I be keep my mouth shut?',action="store_true")
parser.add_argument('--nologs', help='should I remember what I did?',action="store_true")
parser.add_argument('--withproxy', help='should I hide behind this guy?',action="store_true")
args = parser.parse_args()

class GlobalData:
  def __init__(self):
    self.nlinks = 0
    self.ilinks = 0
    self.plinks = 0
    self.visited_jobs = []

    self.db_name = 'hottesttechs.db'
    self.log_empty_name = '01_strange_jobs.log'
    self.log_ignore_name = '02_ignored_jobs.log'
    self.log_not_enough_name = '03_not_enough_techs.log'

    self.prettykeys = {}
    self.searchkeys = {}
    self.compiledkeys = {}
    self.intersectkeys = {}
    self.localdate = None
    self.timezone = ''

    self.stop_urls = []
    self.is_first_run = True
    self.is_stop_urls = False
  
  def get_write_date(self) -> str:
    return common.as_write_date_from_timezone(self.localdate, self.timezone)

def is_position_ignored(position, black_list, white_list):
  split_chars = ['-', '(', ')','/',',','\s','\'','!',':']
  pos = position.lower()
  delims = '['+''.join(split_chars)+']'
  words = re.split(delims,pos)
  for w in words:
    if (w != '') and (w in white_list): return w, False
    if (w != '') and (w in black_list): return w, True
  return '', False

def is_position_contains_techs(description, prettykeys, searchkeys, compiledkeys, intersectkeys):
  res = {}
  resarr = []
  is_contain_any = False
  for tech in searchkeys:
    if compiledkeys[tech].search(description) != None:
      res[searchkeys[tech]] = prettykeys[searchkeys[tech]]
      resarr.append(tech)
      is_contain_any = True

  # resarr = {45: 'Java', 35: 'JavaScript'}, but interesection = {'Java': ['Java Script']}
  for key1 in resarr:
    if key1 in intersectkeys:
      for key2 in intersectkeys[key1]:
        if key2 in resarr:
          # 'Java' is key1, 'Java Script' is key2
          # if found 3 'Java' and 1 'Java Script' => there should be 'Java' by itself
          # if found 3 'Java' and 3 'Java Script' => this is only 'Java Script'
          # if found 1 'Java' and 3 'Java Script' => it is 'Java Script/JS/JavaScript' in text
          numKey1 = len(compiledkeys[key1].findall(description))
          numKey2 = len(compiledkeys[key2].findall(description))
          if numKey1 <= numKey2:
            if key1 in searchkeys:
              if searchkeys[key1] in res:
                del res[searchkeys[key1]]
              else:
                info('...some rare error... dict:res = '+str(res)+' key:searchkeys[key1] = '+str(searchkeys[key1]))
            else:
              info('...some rare error... dict:searchkeys = '+str(searchkeys)+'. key:key1 = '+str(key1))

  return is_contain_any, res

def retry_request_until_ok(path, headers, global_data):
  attempts = 100
  iter = 0
  while True:
    iter += 1
    if (iter > attempts):
      info(">|< now i'm sure that something is wrong with the network")
      exit(1)

    try:
      if (args.withproxy):
        r = requests.get(path, headers=headers, proxies=global_data.proxy)
      else:
        r = requests.get(path, headers=headers)
      if r.status_code < 500:
        return r
      else:
        common.sleep_exact(5)
        info(">|< server failed ...retrying...")
        info(path)
    except:
      common.sleep_exact(5)
      info(">|< request failed ...retrying...")
      info(path)

def get_description(path, global_data):
  headers = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  path = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  r = retry_request_until_ok(path, headers, global_data)
  soup = BeautifulSoup(r.text, 'html.parser')
  descr = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  if descr == None:
    print(path)
    print(soup)
    print(descr)
    return ''
  text = descr.get_text(separator=' ')
  return text

def get_links(page=0, global_data=None):
  info(f"getting links from page {page}")

  headers = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url  = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  base_url += XXXXXXXXXXXXXXXXXXXXXXXXXXXX

  r = retry_request_until_ok(base_url, headers, global_data)
  soupmain = BeautifulSoup(r.text, 'html.parser')
  status_code = r.status_code

  links = XXXXXXXXXXXXXXXXXXXXXXXXXXXX
  links_return = []
  for link in links:
    if XXXXXXXXXXXXXXXXXXXXXXXXXXXX != XXXXXXXXXXXXXXXXXXXXXXXXXXXX:
      if XXXXXXXXXXXXXXXXXXXXXXXXXXXX != XXXXXXXXXXXXXXXXXXXXXXXXXXXX:
        links_return.append(link)

  return links_return, status_code

def process_chunk(global_data:GlobalData, links, ignore_words, important_words):

  log_empty_techs = []
  log_not_enough = []
  log_ignore_name = []
  runtime = datetime.timedelta()
  runnums = 0

  nlinks_initial = global_data.nlinks
  plinks_initial = global_data.plinks

  if global_data.is_first_run:
    global_data.stop_urls = db.read_stop_urls(global_data.db_name)[:]
    info("stop urls before: " + str(global_data.stop_urls))
    urls = []
    for i in range(len(links)):
      job_link = links[i].get('href')
      job_link = job_link[0:job_link.find('?')]
      urls.append(job_link)
    db.write_stop_urls(global_data.db_name,urls)
    info("stop urls after: " + str(db.read_stop_urls(global_data.db_name)[:]))
    global_data.is_first_run = False

  for link in links:
    job_link = link.get('href')
    job_link = job_link[0:job_link.find('?')]
    info(job_link)

    if job_link in global_data.stop_urls:
      global_data.is_stop_urls = True
      break

    global_data.nlinks += 1
    position_name = link.span.contents[0]

    found_ignore_word,is_ignored = is_position_ignored(position_name, ignore_words, important_words)
    if (is_ignored):
      global_data.ilinks += 1
      log_ignore_name.append(found_ignore_word + "     :     "+position_name.strip('\n'))
      info('ignored: ' + log_ignore_name[-1])
      continue

    if job_link in global_data.visited_jobs:
      global_data.nlinks -= 1
      info('already visited: ' + position_name)
      continue
    
    global_data.visited_jobs.append(job_link)
    common.sleep()
    description = get_description(job_link, global_data)

    t1 = datetime.datetime.now()
    is_with_tech, techs = is_position_contains_techs(description,
      global_data.prettykeys,
      global_data.searchkeys,
      global_data.compiledkeys,
      global_data.intersectkeys
    )

    runtime += datetime.datetime.now() - t1
    runnums += 1

    if is_with_tech:
      info('techs found: '+str(techs))
      n_techs_found = len(techs)
      if n_techs_found > 5:
        global_data.plinks += 1
        db.store_data(global_data.db_name,techs,date=global_data.get_write_date())
        info('processed: ' + position_name)
      elif n_techs_found > 3:
        global_data.plinks += 1
        db.store_data(global_data.db_name,techs,date=global_data.get_write_date())
        log_not_enough.append(position_name)
        log_not_enough.append(str(techs))
        log_not_enough.append(description+'\n\n\n')
        info('processed, not enough techs: ' + position_name)
      else:
        log_not_enough.append(position_name)
        log_not_enough.append(str(techs))
        log_not_enough.append(description+'\n\n\n')
        info('not storing, not enough techs: ' + position_name)
    else:
      log_empty_techs.append(position_name)
      log_empty_techs.append(description+'\n\n\n')
      info('no techs found, sent to log: ' + position_name)

  if (len(log_empty_techs) > 0) and (not args.nologs):
    info('dumping positions with no techs')
    common.dump(log_empty_techs, global_data.log_empty_name)
  if (len(log_ignore_name) > 0) and (not args.nologs):
    info('dumping ignored positions')
    common.dump(log_ignore_name, global_data.log_ignore_name)
  if (len(log_not_enough) > 0) and (not args.nologs):
    info('dumping positions with not enough techs')
    common.dump(log_not_enough, global_data.log_not_enough_name)
  db.write_npi_links(global_data.db_name,
    global_data.nlinks-nlinks_initial,
    global_data.plinks-plinks_initial,
    date=global_data.get_write_date())
  
  procstr = 'average processing time: '
  procstr += '0' if runnums == 0 else common.fstr(runtime.total_seconds()/runnums, 6)
  info(procstr)
  return global_data

def hello_screen():
  print(' >> << >> << >> << >>')
  print(' >> ')
  if (args.withproxy):
    print(' >> proxy is ON')
  else:
    print(' >> proxy is OFF')
  if (args.nologs):
    print(' >> logs is OFF')
  else:
    print(' >> logs is ON')
  if (args.nostdout):
    print(' >> stdout is OFF')
  else:
    print(' >> stdout is ON')
  print(' >> ')

def info(info):
  if (not args.nostdout):
    print(' >> '+info)

def main():
  if not args.nostdout: hello_screen()
  start_time = datetime.datetime.now()
  finish_time = start_time + datetime.timedelta(hours=1)
  info('started  local: ' + start_time.ctime())
  
  global_data = GlobalData()
  global_data.localdate = start_time
  global_data.timezone = 'Australia/Melbourne'

  if (args.withproxy):
    proxy_user = os.environ.get('PROXY_USER')
    proxy_pass = os.environ.get('PROXY_PASS')
    proxy_addr_ip = os.environ.get('PROXY_ADDR_IP')
    proxy_addr_port = os.environ.get('PROXY_ADDR_PORT')
    proxies={'https': f'http://{proxy_user}:{proxy_pass}@{proxy_addr_ip}:{proxy_addr_port}'}
    global_data.proxy = proxies
    info('proxies: ' + f'http://{proxy_user}:xxxx-xxxx-xxxx-xxxx@{proxy_addr_ip}:{proxy_addr_port}')

  db_init.init_db(global_data.db_name)
  ignore_words = common.load_ignored()
  important_words = common.load_important()
  
  global_data.prettykeys, global_data.searchkeys = db.get_keywords_dicts(global_data.db_name)
  global_data.compiledkeys, global_data.intersectkeys = common.get_searchkeys_variants_compiled(global_data.searchkeys)

  code = 200
  istep = 0
  maxpages = 50

  repeat = True
  while repeat:
    links, code = get_links(page=istep,global_data=global_data)
    global_data = process_chunk(global_data,links,ignore_words,important_words)
    istep += 1
    common.sleep()
    if (istep == maxpages):
      info('terminated by max pages')
      repeat = False
    if (datetime.datetime.now() > finish_time):
      info('terminated by max work time reached')
      repeat = False
    if (code != 200):
      info('terminated by api response code ['+str(code)+']')
      repeat = False
    if global_data.is_stop_urls:
      info('terminated by facing stop link')
      repeat = False

    info('')
    if (len(global_data.visited_jobs) > 100):
      global_data.visited_jobs = global_data.visited_jobs[len(global_data.visited_jobs)-100:]

  info('done  local: ' + datetime.datetime.now().ctime())
  info('  Total jobs: '+str(global_data.nlinks)+' Skipped: '+str(global_data.ilinks)+' Processed: '+str(global_data.plinks))
  info(' ~~ SQL vacuum ~~ ')
  db.vacuum(global_data.db_name)

if __name__ == "__main__": main()