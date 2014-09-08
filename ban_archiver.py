# author: Noah

# ################################################################### #
#                                                                     #
# This bot is designed to do the following:                           #
#                                                                     #
#   1. Read modmail and look for "you've been banned" threads         #
#   2. Save link to thread and user banned                            #
#   3. Look for user-started modmail threads with 'banned' in title   #
#   4. Reply with link to original ban thread OR ask user to reply    #
#                                                                     #
# ################################################################### #

# imports
import praw
import redis # requires redis-server

import logging
from time import strftime
from configparser import ConfigParser

# global reddit session
r = None

# read config file & set variables
config = ConfigParser()
config.read('config.ini')

owner      = config.get('reddit', 'owner')
version    = config.get('reddit', 'version')
username   = config.get('reddit', 'username')
password   = config.get('reddit', 'password')
user_agent = username + ' by ' + owner + ' version ' + version

# initialize logging & database
logging.basicConfig(filename='/home/michael/py/bots/ban_archiver/bot.log')
link_database = redis.Redis(host='localhost', db=0)

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
            
            # these two lines grab the mods from the banning subreddit
            sub = r.get_subreddit(subreddit)
            moderators = sub.get_moderators()
            
            # if it is a moderator-generated ban message, store subreddit & link id
            if (subject == "you've been banned" and author in moderators):
                link_database.set(user, link_id)
                logging.info('Adding {0} to database (id: {1})'.format(user, link_id))
                continue
                
            # if it is a user-generated ban message, reply with link to ban message
            elif author not in moderators:
                # skip message if there is a response
                if msg.replies: 
                    continue

                # set up reply to user
                reply = 'Please reply to your original ban message'
                if link_database.get(author) != None:
                    link_stripped = str(link_database.get(author))[2:-1]
                    reply = reply + ': [Permalink](//reddit.com/message/messages/' + link_stripped + ')'
                else:
                    reply = reply + '.'
                reply = reply + '\n\n*This is an automated message. If this message was received incorrectly, please disregard it.*'
                
                # reply to the message
                logging.info('Sending reply to user')
                msg.reply(reply)

# ################################################################### #

def main():
    global r
    
    # log into reddit
    while True:
        try:
            r = praw.Reddit(user_agent)
            r.login(username, password)
            logging.info('Logging in as {0}'.format(username))
            print('Logged in')
            break
        except Exception as e:
            logging.error('ERROR: {0}'.format(e))
            print('Unable to log in')
    
    # start reading modmail
    print('Reading modmail')
    read_modmail()

# only run main() if called from interpreter
if __name__ == '__main__':
    main()