from django.shortcuts import render
from .models import Query

from calendar import monthrange
from dateutil import parser as dateparser
from itertools import accumulate

import datetime
import json

def home_page(request):
  data = Query.objects.all().order_by('date')
  data = data.reverse()[0]
  cards = json.loads(data.payload)
  # get the done dictionary
  done_dict = create_done_dict(cards)
  number_completed = sum([len(done_dict[di]) for di in done_dict])
  # get the the items for this month
  thismonth = create_thismonth_list(cards)
  number_thismonth = len(thismonth)
  # burndown charts
  actual_bdown = compute_actual_burndown(cards)
  ideal_bdown = compute_ideal_burndown(cards)
  # histogram of done items
  done_hist = create_done_histogram(create_done_dict(cards))
  # create the day labels
  now = datetime.datetime.now()
  number_days = days_in_month(now)
  d0 = datetime.datetime(now.year,now.month,1)
  labels = [d0+datetime.timedelta(days=di) for di in range(0,number_days)]
  labels = [di.strftime('%Y-%m-%d') for di in labels]


  # # get the data
  # done_list, number_completed = get_done_list(cards)
  # this_month, number_thismonth = get_this_month(cards, done_list)
  # # create the graph data
  # d0 = this_month[0][0] # just the first date this month
  # number_days = monthrange(d0.year,d0.month)[1]
  # # ideal burn down chart based on total tasks evenly spread throughout the month
  # ideal_bdown = compute_ideal_burndown(cards, number_days)
  # # actual burndown chart
  # done_hist = compute_done_histogram(done_list, number_days)
  # actual_bdown = compute_actual_burndown(cards, done_hist, number_days)
  # # get the day labels
  # d0 = datetime.datetime(d0.year,d0.month,1)
  # labels = [d0+datetime.timedelta(days=di) for di in range(0,number_days)]
  # labels = [di.strftime('%Y-%m-%d') for di in labels]
  #
  return render(request, 'home.html', {'number_completed':number_completed, 'number_thismonth':number_thismonth, 'done':done_dict, 'thismonth':thismonth, 'labels': labels, 'done_hist': done_hist, 'ideal_bdown': ideal_bdown, 'actual_bdown': actual_bdown, 'query_time':dateparser.parse(data.date)})
  #return render(request, 'home.html', {'number_completed': number_done, 'done':done_dict, 'number_thismonth':number_thismonth, 'thismonth':thismonth, 'done_hist':done_hist, 'ideal_bdown':ideal_bdown, 'actual_bdown':actual_bdown, 'query_time':dateparser.parse(data.date)})

def days_in_month(adate):
    return monthrange(adate.year, adate.month)[1]

def create_done_dict(cards):
  done_items = [v for k,v in cards.items() if v['history'][0][0]=='done']
  done_dict = {}
  for di in done_items:
    project = di['labels'][0]
    date_done = dateparser.parse(di['history'][0][1])
    name = di['name']
    if project in done_dict:
      done_dict[project].append([date_done, name, di['checklist']])
    else:
      done_dict[project] = [[date_done, name, di['checklist']]]
  #
  for key in done_dict:
    done_dict[key] = sorted(done_dict[key], reverse=True)
  #
  return done_dict

def create_thismonth_list(cards):
  done_items = [v['name'] for k,v in cards.items() if v['history'][0][0]=='done']
  tmonth_items = []
  for k,v in cards.items():
    history = [hi[0] for hi in v['history']]
    if history[0]=='someday':
      continue
    if 'this month' in history or 'this week' in history or 'do today' in history or 'in progress' in history or 'done' in history:
        tdate, tproj, tname = dateparser.parse(v['history'][0][1]), v['labels'][0], v['name']
        if tname in done_items:
          tmonth_items.append((tdate, tproj, tname, True))
        else:
          tmonth_items.append((tdate, tproj, tname, False))
  #
  return sorted(tmonth_items, reverse=True)

def create_done_histogram(done_dict):
  number_days = days_in_month(next(iter(done_dict.values()))[0][0])
  data = [0]*number_days
  done_hist = [0]*number_days
  for k,v in done_dict.items():
    for vi in v:
      thisday = vi[0].day-1
      done_hist[thisday] += 1
  #
  return done_hist

def compute_actual_burndown(cards):
  dd = create_done_dict(cards)
  number_days = days_in_month(next(iter(dd.values()))[0][0])
  done_hist = create_done_histogram(dd)
  dates = sorted([dateparser.parse(cards[ci]['history'][0][1]) for ci in cards if cards[ci]['history'][0][0]!='someday'])
  newitems = [0]*number_days
  for di in dates:
    newitems[di.day-1] += 1
  # cumulative frequency of new items
  newitems_cumfreq = [si for si in accumulate(newitems)]
  # cumulative freq of completed items
  done_cumfreq = [si for si in accumulate(done_hist)]
  # burndown is the difference
  actual_bdown = [newitems_cumfreq[ii]-val for ii,val in enumerate(done_cumfreq)]
  #
  return actual_bdown

def compute_ideal_burndown(cards):
  dd = create_done_dict(cards)
  number_days = days_in_month(next(iter(dd.values()))[0][0])
  dates = sorted([dateparser.parse(cards[ci]['history'][0][1]) for ci in cards if cards[ci]['history'][0][0]!='someday'])
  histo = [0]*number_days
  for di in dates:
    histo[di.day-1] += 1
  # compute the burn down chart
  index = next((i for i,v in enumerate(histo) if v!=0), None)
  ideal_bdown = [0]*number_days
  for ii,hi in enumerate(histo):
    if ii<index:
      ideal_bdown[ii] = 0
      continue
    if hi>0:
      curr_total = ideal_bdown[ii]+hi
      days_left = number_days-ii
      ideal_bdown[ii:] = [curr_total-di*curr_total/(days_left-1) for di in range(0,days_left)]
  #
  return ideal_bdown