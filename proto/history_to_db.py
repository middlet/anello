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

def get_all_details(trello):
  """
  get all the lists on a trello board
  """
  print("\tquerying API")
  board = trello.get_board(BOARD_ID)
  all_lists = board.all_lists()

  # create a dictioary of all the cards and their history
  cards = {}
  for li in all_lists:
    for ci in li.list_cards():
      # get all the card info and the creation date
      ci.fetch()
      ci.fetch_actions(action_filter='createCard')
      # get the name without any prefix
      actual_name = ci.name.decode()
      if actual_name.find(':'):
        actual_name = actual_name.split(':')[1].strip()
      # get the labels
      actual_labels = []
      for ai in ci.labels:
        actual_labels.append(ai.name.decode())
      # initial data to insert
      datum = {"name":actual_name, "labels":actual_labels,
               "created":ci.actions[0]['date'],
               "list":li.name.decode()}
      # get the history of this card (list, date)
      history = []
      for mi in ci.listCardMove_date():
        history.append([mi[1], mi[2].strftime('%Y-%m-%dT%H:%M:%SZ')])
      if len(history)==0:
        history = [[datum['list'], datum['created']]]
      datum['history'] = history
      checklists = []
      for chlist in ci.checklists:
        for check in chlist.items:
          checklists.append((check['checked'], check['name']))
      datum['checklists'] = checklists
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
  cursor.execute('''insert into dashboard_query(payload,date) values(?,?)''', (json.dumps(cards), dt.strftime('%Y-%m-%dT%H:%M:%SZ')))
  conn.commit()





if __name__ == '__main__':
  if OAUTH_TOKEN!='[insert token here]':
    trello = TrelloClient(API_KEY, token=OAUTH_TOKEN)
    cursor = create_db("../anello/datastore.sqlite3")

    #while(True):
    update_database(trello, cursor)
    print('\tdone')



