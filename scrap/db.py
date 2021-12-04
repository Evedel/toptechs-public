#!/usr/bin/env python

import sqlite3
from typing import Dict, List

def cmd(c, string):
  c.execute(string)

def get_keywords_dicts(dbname):
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  cmd(c, "SELECT * FROM search_keys")
  response = c.fetchall()
  searchkeys = {}
  prettykeys = {}
  for r in response:
    searchkeys[r[1]] = r[2]
  cmd(c, "SELECT * FROM techs")
  response = c.fetchall()
  for r in response:
    prettykeys[r[0]] = r[1]
  conn.close()
  return prettykeys, searchkeys

def increment_vacancy_amount(c,table_name,date_field,tech_id):
  cstr  = f"SELECT * FROM {table_name} "
  cstr += f"WHERE check_date={date_field} AND tech_id={tech_id}"
  cmd(c, cstr)
  res = c.fetchall()
  if (len(res) == 0):
    cstr  = f"INSERT INTO {table_name} (tech_id, check_date, amount) "
    cstr += f"VALUES ({tech_id},{date_field},1)"
    cmd(c, cstr)
  else:
    cstr  = f"UPDATE {table_name} SET amount={res[0][3]+1} "
    cstr += f"WHERE id={res[0][0]} "
    cmd(c, cstr)

def increment_group_amount(c,table_name,date_field,idmin,idmax):
  cstr  = f"SELECT * FROM {table_name} WHERE "
  cstr += f"check_date ={date_field} AND "
  cstr += f"tech_id ={idmin} AND linked_tech_id = {idmax} "
  cmd(c, cstr)
  response = c.fetchall()
  if (len(response) == 0):
    cstr  = f"INSERT INTO {table_name} (tech_id, linked_tech_id, amount, check_date)"
    cstr += f"VALUES ({idmin}, {idmax}, 1, {date_field})"
    cmd(c, cstr)
  else:
    cstr  = f"UPDATE {table_name} "
    cstr += f"SET amount={response[0][3]+1} "
    cstr += f"WHERE id={response[0][0]} "
    cmd(c, cstr)

def store_data(dbname:str, techs_dict:Dict, date:str="'now'") -> None:
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  cmd(c,f'SELECT date({date})')
  res = c.fetchall()
  date_full = res[0][0]

  for tech1 in techs_dict:
    increment_vacancy_amount(c,'vacancies',f"date('{date_full}')",tech1)
    for tech2 in techs_dict:
      if tech1 < tech2:
        increment_group_amount(c,'groups',f"date('{date_full}')",tech1,tech2)

  conn.commit()
  conn.close()

def read_npi_links(dbname,date="'now'"):
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  qstr = f"SELECT * FROM jobs WHERE check_date = date({date})"
  cmd(c,qstr)
  res = c.fetchall()
  conn.close()
  if (len(res) == 0): return 0,0
  return res[0][1], res[0][2]

def write_npi_links(dbname,nlinks,plinks,date="'now'"):
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  cstr  = "SELECT * FROM jobs "
  cstr += f"WHERE check_date = date({date}) "
  cmd(c, cstr)
  response = c.fetchall()
  if (len(response) == 0):
    cstr  = "INSERT INTO jobs (check_date, n_jobs_total, n_jobs_devs) "
    cstr += f"VALUES (date({date}),{nlinks},{plinks})"
  else:
    nold=response[0][1]
    pold=response[0][2]
    cstr  = "UPDATE jobs "
    cstr += f"SET n_jobs_total={nlinks+nold},n_jobs_devs={plinks+pold} "
    cstr += f"WHERE check_date=date({date})"
  cmd(c, cstr)
  conn.commit()
  conn.close()

def vacuum(dbname):
  # https://sqlite.org/lang_vacuum.html
    conn = sqlite3.connect(dbname)
    conn.execute("VACUUM")
    conn.close()

def read_stop_urls(dbname:str) -> List:
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  cmd(c, f'SELECT * FROM general_info')
  urls = c.fetchall()[0][1]
  if (urls == None):
    return ''
  else:
    return urls.split(', ')

def write_stop_urls(dbname:str, lurls:List) -> None:
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  urls = ', '.join(lurls)
  cmd(c, f'UPDATE general_info SET last_checked_urls="{urls}"')
  conn.commit()
  conn.close()
