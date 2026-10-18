#!/usr/bin/env python3
import calendar
from datetime import datetime
import json
now = datetime.now()
print(json.dumps({'text': '󰥔 ' + now.strftime('%H:%M'), 'tooltip': now.strftime('%A · %d.%m.%Y') + '\n\n' + calendar.month(now.year, now.month)}, ensure_ascii=False))
