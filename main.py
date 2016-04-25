import threading,time,json
from database import Database
from redditcrawler import Browser
from tonehelper import ToneHelper


if __name__ == "__main__":

    db = Database()

    # b = Browser(db)

    # while not b.website_up:
    #  b.check_reddit_status()

    # subreddits = ['leagueoflegends', 'dota2', 'hearthstone', 'The_Donald', 'SandersForPresident', 'politics']

    # for subreddit in subreddits:
    #     b.crawl_subreddit(subreddit)

    # th = ToneHelper(db)

    # all_comments = db.get_all_comments()
    # for comment in all_comments:
    #    id = int(comment[0])
    #    th.analyze(id)

# Example query
    """
SELECT
comment_sentence_tone.anger, comments.content, subreddits.subreddit
FROM
comment_sentence_tone, comment_tone, comments, threads, subreddits
WHERE
comment_sentence_tone.comment_tone_id = comment_tone.id AND
comment_tone.comment_id = comments.id AND
comments.thread_id = threads.id AND
threads.subreddit_id = subreddits.id
ORDER BY comment_sentence_tone.anger DESC
    """


