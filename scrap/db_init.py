#!/usr/bin/env python

import sqlite3
import common
import time

def cmd(c, string):
  c.execute(string)

def v1(c):
  print(' >> -- up to v1')

  cmd(c, "PRAGMA foreign_keys = ON")

  cstr  = "CREATE TABLE IF NOT EXISTS general_info ("
  cstr += "check_date TEXT NOT NULL UNIQUE,"
  cstr += "n_jobs_total INTEGER NOT NULL,"
  cstr += "n_jobs_devs INTEGER NOT NULL)"
  cmd(c, cstr)
  
  cstr  = "CREATE TABLE IF NOT EXISTS techs ("
  cstr += "id INTEGER NOT NULL PRIMARY KEY,"
  cstr += "name TEXT NOT NULL UNIQUE)"
  cmd(c, cstr)

  cstr  = "CREATE TABLE IF NOT EXISTS search_keys ("
  cstr += "id INTEGER NOT NULL PRIMARY KEY,"
  cstr += "key TEXT NOT NULL UNIQUE,"
  cstr += "tech_id INTEGER NOT NULL,"
  cstr += "FOREIGN KEY (tech_id) REFERENCES techs (id))"
  cmd(c, cstr)

  cstr  = "CREATE TABLE IF NOT EXISTS vacancies ("
  cstr += "id INTEGER NOT NULL PRIMARY KEY,"
  cstr += "tech_id INTEGER NOT NULL,"
  cstr += "check_date TEXT NOT NULL,"
  cstr += "amount INTEGER NOT NULL,"
  cstr += "FOREIGN KEY (tech_id) REFERENCES techs (id))"
  cmd(c, cstr)

  cstr  = "CREATE TABLE IF NOT EXISTS groups ("
  cstr += "id INTEGER NOT NULL PRIMARY KEY,"
  cstr += "tech_id INTEGER NOT NULL,"
  cstr += "linked_tech_id INTEGER NOT NULL,"
  cstr += "amount INTEGER NOT NULL,"
  cstr += "check_date TEXT NOT NULL,"
  cstr += "FOREIGN KEY (tech_id) REFERENCES techs (id),"
  cstr += "FOREIGN KEY (linked_tech_id) REFERENCES techs (id))"
  cmd(c, cstr)

def v2(c):
  print(' >> -- up to v2')

  cmd(c, "DELETE FROM vacancies WHERE check_date < '2020-10-06' ")
  cmd(c, "DELETE FROM groups WHERE check_date < '2020-10-06' ")
  cmd(c, "DELETE FROM search_keys WHERE key='' ")
  
  cstr  = "UPDATE general_info "
  cstr += "SET n_jobs_total=973, "
  cstr += "n_jobs_devs=46 "
  cstr += "WHERE check_date='2020-10-18'"
  cmd(c, cstr)

  cmd(c, "ALTER TABLE general_info RENAME TO jobs")

  cstr  = "CREATE TABLE IF NOT EXISTS general_info ("
  cstr += "db_version INTEGER NOT NULL)"
  cmd(c, cstr)

def v3(c):
  print(' >> -- up to v3')

  cstr  = "SELECT * FROM vacancies WHERE check_date='2020-11-19' OR  check_date='2020-11-20'"
  cmd(c, cstr)
  res = c.fetchall()
  for r in res:
    vid = r[0]
    num = r[3]
    if num != 1:
      numfix = int(num/2)
      cstr  = f"UPDATE vacancies "
      cstr += f"SET amount={numfix} "
      cstr += f"WHERE id={vid} "
      cmd(c, cstr)

  cstr  = "SELECT * FROM groups WHERE check_date='2020-11-19' OR  check_date='2020-11-20'"
  cmd(c, cstr)
  res = c.fetchall()
  for r in res:
    gid = r[0]
    num = r[3]
    if num != 1:
      numfix = int(num/2)
      cstr  = f"UPDATE groups "
      cstr += f"SET amount={numfix} "
      cstr += f"WHERE id={gid} "
      cmd(c, cstr)

  cstr  = "UPDATE general_info "
  cstr += "SET db_version=3"
  cmd(c, cstr)

def v4(c):
  print(' >> -- up to v4')
  cstr  = 'ALTER TABLE general_info '
  cstr += 'ADD COLUMN last_checked_urls TEXT '
  cmd(c, cstr)
  cstr  = 'UPDATE general_info '
  cstr += 'SET db_version=4'
  cmd(c, cstr)

def fill_techs(c):
  techs = common.load2D('techs.txt')
  for tech in techs:
    cmd(c, "INSERT OR IGNORE INTO techs(name) VALUES('"+tech[0]+"')")
    cmd(c, "SELECT id FROM techs WHERE name='"+tech[0]+"'")
    tech_id = c.fetchall()[0][0]
    for i in range(1,len(tech)):
      cstr  = "INSERT OR IGNORE INTO search_keys (key, tech_id) "
      cstr += "VALUES ('"+tech[i]+"',"+str(tech_id)+")"
      cmd(c, cstr)
  cmd(c, "SELECT * FROM search_keys WHERE key='' ")
  res = c.fetchall()
  if (len(res) != 0):
    print(f'>> -- need to sanitise search_keys: {res}')

def upgradedb(conn,c,v):
  if v == 2:
    v3(c)
  if v == 3:
    v4(c)
  conn.commit()

def get_v(c):
    cmd(c, "SELECT db_version FROM general_info")
    return c.fetchall()[0][0]

def init_db(dbname):
  print(' >> init BD '+dbname)
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
  curversion = 4

  try:
    thisversion = get_v(c)
  except:
    print(' >> this db version is unknown')
    v1(c)
    fill_techs(c)
    v2(c)
    conn.commit()
    cmd(c, "INSERT INTO general_info(db_version) VALUES(2)")

  thisversion = get_v(c)
  fill_techs(c)
  print(f' >> this db version: v{thisversion}')
  while (thisversion < curversion):
    upgradedb(conn,c,thisversion)
    thisversion = get_v(c)

  conn.commit()
  conn.execute("VACUUM")

if (__name__ == "__main__"): init_db('hottesttechs.db')