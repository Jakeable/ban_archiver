# author: Noah

# imports
import subprocess
import praw
import traceback
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
location   = config.get('reddit', 'location')
user_agent = username + ' by ' + owner + ' version ' + version

# ################################################################### #

def main():
    global r
    
    while True:
        try:
            r = praw.Reddit(user_agent)
            r.login(username, password)
            print('Logged in')
            break
        except Exception as e:
            print('Unable to log in')
            continue
    
    keep_going = True
    while keep_going:
        try:
        
            print('Checking if down...')
            
            for msg in r.get_unread(limit=None):
                if (str(msg.author).lower() == 'noahjk' and str(msg.subject).lower() == 're: ban_archiver went down' and str(msg.body) == 'restart'):
                    subprocess.call([location + 'run_ban_archiver.sh'])
                    r.reply('successfully restarted.')
                    print('Down. Restarted')
                msg.mark_as_read()
            
            break
        
        except HTTPError as e:
            time.sleep(30)
            continue
        except:
            print(traceback.format_exc())
            break

if __name__ == '__main__':
    main()