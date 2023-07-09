# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 14:56:55 2021

@author: zlewis
"""
##IDEAS: Generalize MLBDataProcessor to be a general Comment Processor, removing dependency 
##On Format and make ngrams amount an input
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
    
class MlbDataProcessor():
    
    def __init__(self, mlb_players: str, comment_data: list, data_col = ['First Name', 'Last Name']):
        self.player_file = mlb_players
        self.players = pd.DataFrame()
        self.data_cols = data_col
        self.comment_data = comment_data
        self.full_variations = pd.DataFrame()
        
    def get_players(self):
        self.players = pd.read_excel(self.player_file, sheet_name='full_name')
        self.players['full_name'] = self.players[self.data_cols[0]].str.lower() + " " + self.players[self.data_cols[1]].str.lower()
        
        first_names = pd.read_excel(self.player_file, sheet_name='unique_first')
        last_names = pd.read_excel(self.player_file, sheet_name='unique_last')
        
        self.full_variations = pd.DataFrame(np.concatenate([self.players.full_name, first_names.iloc[:, 0], last_names.iloc[:,0]]), columns=['all_variations'])
        self.full_variations['all_variations']  = self.full_variations.all_variations.str.lower()
        
    def process_comments(self):
        lower_comments = pd.Series(self.comment_data).str.lower()
        comments = pd.DataFrame(lower_comments.str.replace(r'[^A-z\s]',"", regex=True), columns = ['comment'])
        comments['length'] = comments.comment.apply(lambda x : len(x.split()))
        
        candidate_comments = comments[comments.length>1]['comment']
        
        #Original bigrams
        grams = candidate_comments.apply(lambda x: list(ngrams(x.split(),2)))
        grams = grams.reset_index(drop=True)
        
        all_ngrams = pd.DataFrame(np.concatenate(grams.dropna()), columns=['first_gram', 'second_gram'])
        all_ngrams['joint'] = all_ngrams.first_gram.str.strip() + ' ' + all_ngrams.second_gram.str.strip()
        
        #Single Grams
        unigrams = candidate_comments.apply(lambda x: x.split())
        unigrams = unigrams.reset_index(drop=True)
        
        all_unigrams = pd.DataFrame(np.concatenate(unigrams.dropna()), columns=['first_gram'])
        all_unigrams['joint'] = all_unigrams.first_gram.str.strip()

        full_grams = pd.DataFrame(pd.concat([all_ngrams.joint, all_unigrams.joint]), columns = ['joint'])

        all_names = full_grams.merge(self.full_variations, left_on = 'joint', 
                                     right_on = 'all_variations', how='inner')
        all_names['joint'] = all_names.joint.str.title()
        return pd.DataFrame(collections.Counter(all_names.joint).most_common(),
                            columns=['Players', "Num_Mentions"])
   
    
if __name__ == '__main__':
    
    """Scrape comment data and format for plotting"""
    fb_test = RedditScraper(client_id = 'pJsuStRkUNbm6A', 
                            client_secret = 'mw69VcOeNCtTbQikt1sOwJRo8rUvcA',
                            user_agent = 'fb_api', 
                            subreddit = 'fantasybaseball')
    
    all_comments = fb_test.hot_comments()    
        
    data_p = MlbDataProcessor('mlb_players.xlsx', all_comments)
    data_p.get_players()
    top_mentions = data_p.process_comments()

    cur_date = date.today().strftime("%b-%d-%Y") 
    top_mentions['date'] = date.today()
    
    """Load data to json file if not previously recorded"""
    try:
        with open('mentions_data.json', 'r') as f:
            check_date = pd.read_json(json.load(f))
            
    except FileNotFoundError:
        with open('mentions_data.json', 'w') as f:
            json.dump(top_mentions.to_json(), f, indent=4)
            
    else:
        if str(date.today()) not in np.concatenate(check_date.date.astype(str).str.split()):
            with open('mentions_data.json', 'w') as f:
                updated = check_date.append(top_mentions).reset_index(drop=True)
                json.dump(updated.to_json(), f, indent=4)
    
    """Plot Top Ten Player Data"""
    plt.style.use('seaborn')
    fig, ax = plt.subplots()
    
    ax.bar(x=[num for num in range(10)],
           height=top_mentions.Num_Mentions[:10],
           tick_label = top_mentions.Players[:10])
    
    ax.set_xlabel('MLB Players')
    ax.set_ylabel('Number of Mentions')
    plt.xticks(rotation = 45)
    ax.set_title(f'Top Players Mentioned in r/fantasybaseball\n{cur_date}')
    # plt.show()
    
    time.sleep(5)
    
    # Add TF-IDF mechanism?

      
        
        
        




