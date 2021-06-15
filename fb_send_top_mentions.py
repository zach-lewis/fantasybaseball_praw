# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 09:42:53 2021

@author: zlewis
"""

import pandas as pd
import json
import time
from twilio.rest import Client

time.sleep(3)

account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'
twilio_cl = Client(account_sid, auth_token)
my_twilio_num = 'YOUR_TWILIO_NUMBER'
my_phone = 'YOUR_PERSONAL_NUMBER'

with open('data/mentions_data.json', 'r') as f:
    json_ver = json.load(f)
    latest_data = pd.read_json(json_ver, orient='columns')
    

top_15 = latest_data.groupby('date').head(15)

today_15 = top_15.iloc[-15:, 0]
yesterday_15 = top_15.iloc[-30:-15, 0]

new_mentions = "\n".join(today_15[~today_15.isin(yesterday_15)])
top_mentions = "\n".join(today_15)

msg_body = f'Top 15 Mentions in r/fantasybaseball Today: \n{top_mentions}\
\n\nNew Players Mentioned in the Top 15 Today: \n{new_mentions}'
print(msg_body)
message = twilio_cl.messages.create(body=msg_body, from_=my_twilio_num,
                                     to=my_phone)