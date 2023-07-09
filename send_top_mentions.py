# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 01:29:27 2023

@author: zlewis
"""

from email.message import EmailMessage
import ssl
import smtplib

import pandas as pd
import json
from datetime import datetime

today = datetime.today().strftime("%m-%d-%Y")

email_sender = 'YOUR_EMAIL'
email_password = 'YOUR_PASSWORD'
email_recipient = 'RECEIPIENT_EMAIL'

email_subject = f'Fantasy Baseball Top Mentions {today}'

with open('mentions_data.json', 'r') as f:
    json_ver = json.load(f)
    latest_data = pd.read_json(json_ver, orient='columns')

top_15 = latest_data.groupby('date').head(15)

today_15 = top_15.iloc[-15:, 0]
yesterday_15 = top_15.iloc[-30:-15, 0]

new_mentions = "\n".join(today_15[~today_15.isin(yesterday_15)])
top_mentions = "\n".join(today_15)

email_body = f"""
Hi Zach,

See below for your r/fantasybaseball mentions summary:

Top 15 Mentions in r/fantasybaseball Today: \n{top_mentions}

New Players Mentioned in the Top 15 Today: \n{new_mentions}
"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_recipient
em['Subject'] = email_subject
em.set_content(email_body)

context =  ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp_sesh:
    smtp_sesh.login(email_sender, email_password)
    smtp_sesh.sendmail(email_sender, email_recipient, em.as_string())
    
