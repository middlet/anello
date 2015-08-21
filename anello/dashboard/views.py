from django.shortcuts import render
from .models import Query

import json

def home_page(request):
  data = Query.objects.all()[0]
  cards = json.loads(data.payload)
  done_items = [v for k,v in cards.items() if v['list']=='done']
  month_items = []
  for k,v in cards.items():
    history = [hi[0] for hi in v['history']]
    if 'this month' in history or 'this week' in history or 'do today' in history or 'in progress' in history:
      month_items.append(v)


  return render(request, 'home.html', {'number_completed':len(done_items), 'number_thismonth':len(month_items)})
