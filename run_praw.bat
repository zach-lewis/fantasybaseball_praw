@ECHO OFF
Rem Call Anaconda Base if Relevant. Remove for non-Anaconda Python Env
call C:\users\your_user_name\Anaconda3\Scripts\activate.bat C:\users\your_user_name\Anaconda3

python praw_fb.py

python send_top_mentions.py
