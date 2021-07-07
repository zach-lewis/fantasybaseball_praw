# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 14:56:55 2021

@author: zlewis
"""

import praw
import collections
import pandas as pd
import numpy as np
from nltk.util import ngrams
from datetime import date
import matplotlib.pyplot as plt
import json
import time

class RedditScraper():
    
    def __init__(self, client_id, client_secret, user_agent, subreddit):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.subreddit = subreddit
        self.hot_comments_list = []
        self.hot_posts = []
        
    def __str__(self):
        return
        f"""
        Reddit Scraper Object
        - subreddit: {self.subreddit}
        - user_agent: {self.user_agent}
        """
    def hot_comments(self, lim=100):
        reddit = praw.Reddit(client_id = self.client_id, 
                     client_secret = self.client_secret,
                     user_agent = self.user_agent)
        
        subreddit = reddit.subreddit(self.subreddit)

        for post in subreddit.hot(limit=lim):
            self.hot_posts.append(post.title)
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                self.hot_comments_list.append(comment.body)
        
        print(f"\n********Top Posts on r/{self.subreddit} Currently********\n")
        for title in self.hot_posts[:10]:
            print(f"\t - {title}\n")
        
        print(f"All valid comments for top {lim} hot posts returned")
        return self.hot_comments_list
    
class GramDataProcessor():
    
    def __init__(self, data_input: pd.DataFrame(), comment_data: list, data_key: str):
        self.data_input = data_input.apply(lambda x: x.str.lower())
        self.data_key = data_key
        self.comment_data = comment_data
        self.cleaned_comments = pd.DataFrame()
        self.data_output = pd.DataFrame()
        
    def clean_comments(self):
        lower_comments = pd.Series(self.comment_data).str.lower()
        #Clean out symbols and filter for only comments with a valid length remaining
        comments = pd.DataFrame(lower_comments.str.replace(r'[^A-z\s]',"", regex=True), columns = ['comment'])
        comments['length'] = comments.comment.apply(lambda x : len(x.split()))
        candidate_comments = comments[comments.length>1]['comment']
        self.cleaned_comments = candidate_comments
        
    def most_common_grams(self, num_grams: int):
        if self.cleaned_comments.empty:
            print("Comments must be cleaned by using clean_comments() method first")
        else:
             #Get n-grams
            grams = self.cleaned_comments.apply(lambda x: list(ngrams(x.split(), num_grams)))
            grams = grams.reset_index(drop=True)
            all_ngrams = pd.DataFrame(np.concatenate(grams.dropna()))
            all_ngrams['joint'] = all_ngrams.agg(" ".join, axis=1)
            
            #Inner join n-grams on input to filter for valid hits
            full_data = all_ngrams.merge(self.data_input, left_on = 'joint', 
                                         right_on = self.data_key, how='inner')
            full_data['joint'] = full_data.joint.str.title()
            self.data_output = pd.DataFrame(collections.Counter(full_data.joint).most_common(),
                                columns=['gram', "frequency"])
   
    
if __name__ == '__main__':
    
    """Scrape comment data and format for plotting"""
    r_fb = RedditScraper(client_id = 'YOUR_CLIENT_ID', 
                            client_secret = 'YOUR_CLIENT_SECRET',
                            user_agent = 'YOUR_USER_AGENT', 
                            subreddit = 'fantasybaseball')
    
    all_comments = r_fb.hot_comments()    
        
    data_input = pd.read_excel('data/mlb_players.xlsx')
    data_input['full_name'] = data_input['First Name'].str.lower() + " " + data_input['Last Name'].str.lower()
    
    data_p = GramDataProcessor(data_input, all_comments, 'full_name')
    data_p.clean_comments()
    data_p.most_common_grams(2)
    top_mentions = data_p.data_output
    
    cur_date = date.today().strftime("%b-%d-%Y") 
    top_mentions['date'] = date.today()
    
    """Load data to json file if not previously recorded"""
    with open('data/mentions_data.json', 'r') as f:
        check_date = pd.read_json(json.load(f))
        
    if str(date.today()) not in np.concatenate(check_date.date.astype(str).str.split()):
        with open('data/mentions_data.json', 'w') as f:
            updated = check_date.append(top_mentions).reset_index(drop=True)
            json.dump(updated.to_json(), f, indent=4)
    
    #Uncomment to view graph on daily runs. Commented out for simplicity with
    #Daily runs from .bat file
    
    # """Plot Top Ten Player Data"""
    # plt.style.use('seaborn')
    # fig, ax = plt.subplots()
    
    # ax.bar(x=[num for num in range(10)],
    #        height=top_mentions.frequency[:10],
    #        tick_label = top_mentions.gram[:10])
    
    # ax.set_xlabel('MLB Players')
    # ax.set_ylabel('Number of Mentions')
    # plt.xticks(rotation = 45)
    # ax.set_title(f'Top Players Mentioned in r/fantasybaseball\n{cur_date}') 
    # plt.show()
    
    time.sleep(5)

      
        
        
        




