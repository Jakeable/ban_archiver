# author: Noah

# ################################################################### #
#                                                                     #
# This bot is designed to do the following:                           #
#                                                                     #
#   3. Look for user-started modmail threads with 'ban' in title      #
#   4. Tell the user to reply to their original ban message           #
#                                                                     #
# ################################################################### #

# imports
import praw

import logging
from time import strftime
from requests.exceptions import HTTPError
from configparser import ConfigParser

# global reddit session
r = None

config = ConfigParser()
config.read('config.ini')

owner      = config.get('reddit', 'owner')
version    = config.get('reddit', 'version')
username   = config.get('reddit', 'username')
password   = config.get('reddit', 'password')
user_agent = username + ' by ' + owner + ' version ' + version

logging.basicConfig(filename='/home/michael/py/bots/ban_archiver/bot.log', level=logging.INFO)

# ################################################################### #

def read_modmail():
    for msg in r.get_mod_mail(limit=10):
        subreddit = str(msg.subreddit)
        author = str(msg.author)
        subject = str(msg.subject)
        link_id = str(msg.id)
        user = str(msg.dest)
        print('Reading message...')

        if 'ban' in msg.subject:
            logging.info('Message found, processing')
            
            sub = r.get_subreddit(subreddit)
            moderators = sub.get_moderators()
            
            if not (subject == "you've been banned" and author in moderators):
                if msg.replies: 
                    continue

                reply = ''''If you believe you are banned, please reply to your original ban message.\n\n 
                            This can be found [in your inbox](//reddit.com/message/inbox),
                            and will say "You have been banned from posting to /r/AskReddit [...]."'''
                reply += '\n\n*This is an automated message. If this message was received incorrectly, please ignore.*'
                
                logging.info('Sending reply to user')
                msg.reply(reply)

# ################################################################### #

def main():
    global r
    
    while True:
        try:
            r = praw.Reddit(user_agent)
            r.login(username, password)
            logging.info('Logging in as {0}'.format(username))
            print('Logged in')
            r.send_message('noahjk', 'ban_archiver is running', 'ban_archiver is running')
            break
        except Exception as e:
            logging.error('ERROR: {0}'.format(e))
            print('Unable to log in')
    
    while True:
        try:
        
            print('Reading modmail')
            read_modmail()
        
        except HTTPError:
            time.sleep(30)
            continue
        except:
            break
        break

if __name__ == '__main__':
    main()