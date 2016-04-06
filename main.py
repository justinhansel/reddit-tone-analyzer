import threading,time,json
from watson_developer_cloud import ToneAnalyzerV3Beta
from database import Database
from redditcrawler import Browser

tone_analyzer = json.load(open('bluemix_credentials.json'))

if __name__ == "__main__":
    # db = Database()
    """ db.c.execute('''CREATE TABLE subreddits
                    (id INTEGER PRIMARY key,
                     subreddit VARCHAR(256) NOT NULL,
                     subscribers INTEGER NOT NULL,
                     scan_date DATE NOT NULL)''')
    """

    b = Browser()

    while not b.website_up:
        b.check_reddit_status()

    b.get_comment_links()


    # print("yep")
    # print(json.dumps(tone_analyzer.tone(text='A word is dead when it is said, some say. Emily Dickinson'), indent=2))