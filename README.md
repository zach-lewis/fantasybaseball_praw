# fantasybaseball_praw
Program to analyze the top MLB players mentioned each day in r/fantasybaseball in an effort to identify top prospects, utilizing Python Reddit API Wrapper (PRAW)

- praw_mod.py: Main module containing two classes that aggregate and process subreddit comments for mentions of MLB players. Approach relies on players being mentioned by full name, necessitated by the frequency of certain last names and tendency to refer to players as such (e.g. Cabrera, Sanchez), and the assumption that most up-and-coming, low-rostered players will be referred to by full name (as opposed to someone like deGrom). 

- fb_send_top_mentions.py: Utilizes Twilio to send a custom report each day with the top mentioned players, and any players in top mentions on that day not mentioned in the previous day

- run_praw.bat: Batch file to run program daily when paired with a program such as Windows Task Scheduler

- mentions_analysis.ipynb: Analysis of top mentions to date and their correlation to fantasy points. Runs outside of main program schedule
