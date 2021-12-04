#!/usr/bin/env python

import sqlite3

def yes_or_no(question):
  answer = input(question + "(y/n): ").lower().strip()
  print("")
  while not(answer == "y" or answer == "yes" or \
  answer == "n" or answer == "no"):
      print("Input yes or no")
      answer = input(question + "(y/n):").lower().strip()
      print("")
  if answer[0] == "y":
      return True
  else:
      return False

def cmd(c, string):
  c.execute(string)

def print_last_5_days():
  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()
  days_to_print = 5

  results = []
  for d in range(days_to_print):
    qstr  = "SELECT * FROM vacancies "
    qstr += "WHERE check_date = (SELECT DATE('now', '-"+str(days_to_print-1-d)+" day')) "
    qstr += "ORDER BY amount DESC"
    cmd(c, qstr)
    res = c.fetchall()
    results.append(res)
  
  max_rows = max([len(l) for l in results])

  dates = []
  for d in range(days_to_print):
    if (len(results[d]) > 0): dates.append(results[d][0][2])

  lines = []
  h1str = '|'
  h2str = '|'
  h3str = '|'
  lstr = '|'
  csz = 30
  for d in dates:
    h1str += ('{0: ^'+str(csz)+'}').format(d) + '|'
    lstr += ('{0:-^'+str(csz)+'}').format('') + '|'
    qstr  = "SELECT * FROM jobs "
    qstr += "WHERE check_date = '"+str(d)+"'"
    cmd(c, qstr)
    res = c.fetchall()
    if (len(res) != 0):
      h2str += ('{0: ^'+str(csz)+'}').format('Total Jobs: '+str(res[0][1])) + '|'
      h3str += ('{0: ^'+str(csz)+'}').format('Devs Jobs: '+str(res[0][2])) + '|'
    else:
      h2str += ('{0: ^'+str(csz)+'}').format('Total Jobs: Unknown') + '|'
      h3str += ('{0: ^'+str(csz)+'}').format('Devs Jobs: Unknown') + '|'

  lines.append(lstr)
  lines.append(h1str)
  lines.append(lstr)
  lines.append(h2str)
  lines.append(h3str)
  lines.append(lstr)

  iline = 1
  idate = 0
  cdate = dates[idate]

  for ir in range(max_rows):
    estr = '|'
    for ic in range(days_to_print):
      element = None
      if (len(results[ic]) > ir):
        element = results[ic][ir]
      
      if element != None:
        qstr  = "SELECT name FROM techs WHERE id = "+str(element[1])
        cmd(c, qstr)
        res = c.fetchall()
        estr += ('{0: ^'+str(csz)+'}').format(res[0][0] + ' ' + str(element[3])) + '|'
      else:
        estr += ('{0: ^'+str(csz)+'}').format('') + '|'

    lines.append(estr)
    
  lines.append(lstr)
  for l in lines:
    print(l)

def print_all_techs(table):
  conn = sqlite3.connect('hottesttechs.db')
  # conn = sqlite3.connect('test.db')
  c = conn.cursor()
  qstr = 'SELECT * FROM '+table+' ORDER BY name'

  cmd(c, qstr)
  res = c.fetchall()
  columns_number = 5
  column = []
  for il in range(columns_number):
    column.append([])

  il = 0
  ic = 0
  ml = len(res)//columns_number
  if (ml*columns_number != len(res)):
    ml += 1

  csz = 30
  lstr = ''
  for r in res:
    column[ic].append(str(r[0]) + ":" + r[1])
    il += 1
    if il >= ml:
      ic += 1
      il = 0

  for il in range(ml):
    lstr = ''
    for ic in range(len(column)):
      if (len(column[ic]) > il):
        lstr += ('{0: ^'+str(csz)+'}').format(column[ic][il])
      else:
        lstr += ('{0: ^'+str(csz)+'}').format('')
    print(lstr)

def delete_tech(name):
  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()
  qstr = 'SELECT * FROM techs WHERE name=\''+name+'\''
  cmd(c, qstr)
  res = c.fetchall()
  print('going to delete: '+str(res))

  qstr = 'SELECT * FROM groups WHERE tech_id='+str(res[0][0])+' OR linked_tech_id='+str(res[0][0])
  cmd(c, qstr)
  print('')
  print('rm groups')
  print(c.fetchall())
  qstr = 'DELETE FROM groups WHERE tech_id='+str(res[0][0])+' OR linked_tech_id='+str(res[0][0])
  cmd(c, qstr)

  qstr = 'SELECT * FROM vacancies WHERE tech_id='+str(res[0][0])
  cmd(c, qstr)
  print('')
  print('rm vacancies')
  print(c.fetchall())
  qstr = 'DELETE FROM vacancies WHERE tech_id='+str(res[0][0])
  cmd(c, qstr)

  qstr = 'SELECT * FROM search_keys WHERE tech_id='+str(res[0][0])
  cmd(c, qstr)
  print('')
  print('rm search_keys')
  print(c.fetchall())
  qstr = 'DELETE FROM search_keys WHERE tech_id='+str(res[0][0])
  cmd(c, qstr)

  qstr = 'SELECT * FROM techs WHERE id='+str(res[0][0])
  cmd(c, qstr)
  print('')
  print('rm techs')
  print(c.fetchall())
  qstr = 'DELETE FROM techs WHERE id='+str(res[0][0])
  cmd(c, qstr)

  print('')
  if yes_or_no('do it? '):
    pass
    conn.commit()
  else:
    return

def update_tech():
  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()
  qstr = 'SELECT * FROM techs WHERE id=124'
  cmd(c, qstr)
  print(c.fetchall())
  qstr = 'UPDATE techs SET name=\'TCP/IP\' WHERE id=124'
  cmd(c, qstr)
  print(c.fetchall())
  conn.commit()

def delete_search_key(key):
  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()
  qstr = 'SELECT * FROM search_keys WHERE key=\''+key+'\''
  cmd(c, qstr)
  print('')
  print('rm search_keys')
  print(c.fetchall())
  qstr = 'DELETE FROM search_keys WHERE key=\''+key+'\''
  cmd(c, qstr)
  print('')
  if yes_or_no('do it? '):
    conn.commit()
  else:
    return

def debug():
  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()
  qstr="SELECT * FROM vacancies WHERE check_date = DATE('now') ORDER BY amount DESC"
  cmd(c, qstr)
  print(c.fetchall())

def see_groups():
  # HTML
  # tid = 131
  
  # JS
  tid = 2

  conn = sqlite3.connect('hottesttechs.db')
  c = conn.cursor()

  # qstr="SELECT tech_id,linked_tech_id,SUM(amount) FROM groups WHERE tech_id="+str(tid)+" GROUP BY linked_tech_id ORDER BY SUM(amount) DESC"
  # cmd(c, qstr)
  # print(c.fetchall(),'\n')

  # qstr="SELECT linked_tech_id,tech_id,SUM(amount) FROM groups WHERE linked_tech_id="+str(tid)+" GROUP BY tech_id ORDER BY SUM(amount) DESC"
  # cmd(c, qstr)
  # print(c.fetchall(),'\n')

  qstr  = "SELECT t1, t2, SUM(amount) FROM ("
  qstr += "SELECT tech_id AS t1, linked_tech_id AS t2, amount "
  qstr += f"FROM groups WHERE tech_id={tid} "
  qstr += "AND check_date='2020-10-28' "
  qstr += "UNION ALL "
  qstr += "SELECT linked_tech_id AS t1, tech_id AS t2, amount "
  qstr += f"FROM groups WHERE linked_tech_id={tid} "
  qstr += "AND check_date='2020-10-28' "
  qstr += ") subquery1 "
  qstr += "GROUP BY t2 ORDER BY SUM(amount) DESC "

  cmd(c, qstr)
  res = c.fetchall()
  print(res,'\n')

  qstr=f"SELECT name FROM techs WHERE id={tid}"
  cmd(c, qstr)
  res1 = c.fetchall()
  for r in res:
    qstr=f"SELECT name FROM techs WHERE id={r[1]}"
    cmd(c, qstr)
    res2 = c.fetchall()
    print(f'{res1[0][0]} is mentioned with {res2[0][0]} {r[2]} times')


debug()
# print_last_5_days()
# print_all_techs('techs')
# delete_tech('SEO')
# update_tech()
# delete_search_key('MongoBD')
# see_groups()