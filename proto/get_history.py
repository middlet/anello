#!/usr/bin/env python3

# prototype to see if i can get the boards history

import datetime
import os
import sys

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


def get_all_details(trello):
  """
  get all the lists on a trello board
  """
  print("querying API")
  board = trello.get_board(BOARD_ID)
  all_lists = board.all_lists()

  cards = {}
  for li in all_lists:
    for ci in li.list_cards():
      ci.fetch()
      ci.fetch_actions(action_filter='createCard')
      actual_name = ci.name.decode()
      if actual_name.find(':'):
        actual_name = actual_name.split(':')[1].strip()
      actual_labels = []
      for ai in ci.labels:
        actual_labels.append(ai.name.decode())
      datum = {"name":actual_name, "labels":actual_labels,
               "created":dateparser.parse(ci.actions[0]['date']),
               "list":li.name.decode()}
      history = []
      for mi in ci.listCardMove_date():
        history.append(mi[1:])
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


def print_summary(cards):
  """
  print a summary of all the information
  """
  for key,datum in cards.items():
    print('{} ({})'.format(datum['name'],key))
    print('\tcreated: {}'.format(datum['created']))
    print('\tcurrent list: {}'.format(datum['list']))
    # label list
    labels = '\tlabels: '
    for li in datum['labels']:
      labels += '{} '.format(li)
    print(labels)
    # history of card
    print('\thistory:')
    for hi in datum['history']:
      print('\t\t{}: {}'.format(hi[1],hi[0]))
    # the checklist
    if datum['checklists']:
      print('\tchecklist:')
      for ci in datum['checklists']:
        print('\t\t{}'.format(ci))
  #
  print('='*79)

def print_done_list(cards):
  """
  print out a done list
  """
  # initially we need to get all the done items
  done_items = [v for k,v in cards.items() if v['list']=='done']
  done_list = {}
  for di in done_items:
    project = di['labels'][0]
    date_done = di['history'][0][1]
    name = di['name']
    if project in done_list:
      done_list[project].append([date_done, name, di['checklists']])
    else:
      done_list[project] = [[date_done, name, di['checklists']]]
  #
  projects = sorted([di for di in done_list])

  for di in projects:
    print(di)
    items = done_list[di]
    items_sorted = sorted(items, reverse=True)
    for it in items_sorted:
      print("\t{} : {}".format(it[0].strftime('%Y%m%d'), it[1]))
      if len(it[2])!=0:
        for ci in it[2]:
          print("\t\t* {}".format(ci[1]))
  #
  print('='*79)

def print_this_month(cards):
  done_items = [v['name'] for k,v in cards.items() if v['list']=='done']
  month_items = []
  for k,v in cards.items():
    history = [hi[0] for hi in v['history']]
    if 'this month' in history:
      month_items.append(v)
  #
  thismonth = []
  for mi in month_items:
    completed = False
    if mi['name'] in done_items:
      completed = True
    thismonth.append([mi['history'][0][1], mi['labels'][0], mi['name'], completed])
  # sort the results
  for si in sorted(thismonth, reverse=True):
    if si[3]:
      print('\033[1;31m* {}: {} {}\033[0;0m'.format(si[0].strftime('%Y-%m-%d %H:%M:%S'), si[1], si[2]))
    else:
      print('\033[1;32m* {}: {} {}\033[0;0m'.format(si[0].strftime('%Y-%m-%d %H:%M:%S'), si[1], si[2]))




if __name__ == '__main__':
  if OAUTH_TOKEN!='[insert token here]':
    trello = TrelloClient(API_KEY, token=OAUTH_TOKEN)
    cards = get_all_details(trello)

    print_summary(cards)
    print_done_list(cards)
    print_this_month(cards)



