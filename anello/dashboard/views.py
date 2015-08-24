from django.shortcuts import render
from .models import Query

from dateutil import parser as dateparser

import json

def home_page(request):
  data = Query.objects.all().order_by('date')
  data = data.reverse()[0]
  cards = json.loads(data.payload)

  # get the data
  done_list, number_completed = get_done_list(cards)
  this_month, number_thismonth = get_this_month(cards, done_list)
  # create the graph data


  return render(request, 'home.html', {'number_completed':number_completed, 'number_thismonth':number_thismonth, 'done':done_list, 'thismonth':this_month})


def get_done_list(cards):
  # create a list of done items
  done_items = [v for k,v in cards.items() if v['list']=='done']
  done_list = {}
  for di in done_items:
    project = di['labels'][0]
    date_done = di['history'][0][1]
    name = di['name']
    if project in done_list:
      done_list[project].append([dateparser.parse(date_done), name, di['checklists']])
    else:
      done_list[project] = [[dateparser.parse(date_done), name, di['checklists']]]
  #
  for key in done_list:
    done_list[key] = sorted(done_list[key], reverse=True)
  #
  return done_list, len(done_items)

def get_this_month(cards, done_list):
  done_items = [v for k,v in cards.items() if v['list']=='done']
  # create a list of items this month
  month_items = []
  for k,v in cards.items():
    history = [hi[0] for hi in v['history']]
    if 'this month' in history or 'this week' in history or 'do today' in history or 'in progress' in history or 'done' in history:
      month_items.append(v)
  thismonth = []
  done_thismonth = [di['name'] for di in done_items]
  for mi in month_items:
    completed = False
    if mi['name'] in done_thismonth:
      completed = True
    thismonth.append([dateparser.parse(mi['history'][0][1]), mi['labels'][0], mi['name'], completed])
  # sort the results
  this_month = sorted(thismonth, reverse=True)
  #
  return this_month, len(month_items)