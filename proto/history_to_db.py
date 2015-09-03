#!/usr/bin/env python3

# put the boards history to sqlite

import datetime
import json
import os
import sqlite3
import sys
import time

from dateutil import parser as dateparser
from trello import TrelloClient

# add the directory above to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
  from secrets import *
except:
  # api credentials
  OAUTH_TOKEN = "[insert token here]"
  API_KEY = "[insert api key]"

  # board to investigate
  BOARD_ID = "[insert board id]"


def create_db(fname):
  """
  create the tables if needed and return a cursor
  """
  conn = sqlite3.connect(fname)
  c = conn.cursor()
  c.execute("select name from sqlite_master where type='table';")
  if len(c.fetchall())==0:
    print("\tcreating table")
    c.execute('''create table dashboard_query (id integer primary key, payload text, date text)''')
    conn.commit()
  return conn

def json_datetime_serialize(obj):
    if isinstance(obj, datetime.datetime):
        serialized = obj.isoformat()
        return serialized
    raise TypeError("type not serializable")

def split_name(cname):
    if type(cname)==type(b''):
        cname = cname.decode()
    name = cname.strip()
    if cname.find(':')>=0:
        name = cname.split(':')[1]
        name = name.strip()
    #
    return name

def get_checklists(card_item):
  checklists = []
  for ch in card_item.checklists:
    for check in ch.items:
      checklists.append((check['checked'], check['name']))
  #
  return checklists

def get_history(card_item):
  # get creation date
  card_item.fetch_actions(action_filter='createCard')
  creation_date = dateparser.parse(card_item.actions[0]['date'])
  creation_list = card_item.actions[0]['data']['list']['name']
  # construct the cards history
  history = []
  for hi in card_item.listCardMove_date():
    history.append(hi[1:])
  # append the creation date
  history.append([creation_list, creation_date])
  #
  return history

def get_all_details(trello):
  """
  get all the lists on a trello board
  """
  print("\tquerying API")
  board = trello.get_board(BOARD_ID)
  all_lists = board.all_lists()
  cards = {}
  for li in all_lists:
    for ci in li.list_cards():
      ci.fetch()
      datum = {'name':split_name(ci.name), 'labels':[tag.name.decode() for tag in ci.labels], 'checklist': get_checklists(ci), 'history': get_history(ci)}
      cards[ci.id] = datum
  #
  return cards


def update_database(trello, conn):
  """
  update the database based on the information from the API
  """
  cards = get_all_details(trello)
  print("\tupdating db")
  dt = datetime.datetime.now()
  cursor = conn.cursor()
  cursor.execute('''insert into dashboard_query(payload,date) values(?,?)''', (json.dumps(cards, default=json_datetime_serialize), dt.strftime('%Y-%m-%dT%H:%M:%SZ')))
  conn.commit()


if __name__ == '__main__':
  if OAUTH_TOKEN!='[insert token here]':
    trello = TrelloClient(API_KEY, token=OAUTH_TOKEN)
    cursor = create_db("../anello/datastore.sqlite3")

    while(True):
      print('{:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()))
      update_database(trello, cursor)
      print('\tdone')
      time.sleep(600) # wait 10 minutes



