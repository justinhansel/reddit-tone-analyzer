import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        # self.drop_table('subreddits')
        # self.drop_table('threads')
        # self.drop_table('comments')

        # Check if tables exist and make them if they don't
        self.create_table('subreddits', '''
CREATE TABLE IF NOT EXISTS subreddits(
  id INTEGER PRIMARY KEY,
  subreddit CHAR(256) UNIQUE NOT NULL
);
''')
        self.create_table('threads', '''
CREATE TABLE IF NOT EXISTS threads(
  id INTEGER PRIMARY KEY,
  reddit_id CHAR(50) UNIQUE NOT NULL,
  url CHAR(256) NOT NULL,
  title CHAR(128) NOT NULL,
  subreddit_id INT NOT NULL,
  crawled INT NOT NULL,
  FOREIGN KEY(subreddit_id) REFERENCES subreddits(id)
);
''')
        self.create_table('comments', '''
CREATE TABLE IF NOT EXISTS comments(
  id INTEGER PRIMARY KEY,
  reddit_id CHAR(50) UNIQUE NOT NULL,
  username CHAR(256) NOT NULL,
  content CHAR(15000) NOT NULL,
  thread_id INT NOT NULL,
  karma INT NOT NULL,
  FOREIGN KEY (thread_id) REFERENCES threads(id)
);
''')
        self.create_table('comment_tone', '''
CREATE TABLE IF NOT EXISTS comment_tone(
  id INTEGER PRIMARY KEY,
  anger REAL NOT NULL,
  disgust REAL NOT NULL,
  fear REAL NOT NULL,
  joy REAL NOT NULL,
  sadness REAL NOT NULL,
  analytical REAL NOT NULL,
  confident REAL NOT NULL,
  tentative REAL NOT NULL,
  openness REAL NOT NULL,
  conscientiousness REAL NOT NULL,
  extraversion REAL NOT NULL,
  agreeableness REAL NOT NULL,
  neuroticism REAL NOT NULL,
  comment_id INT NOT NULL,
  content CHAR (15000) NOT NULL,
  FOREIGN KEY (comment_id) REFERENCES comments(id)
);
''')
        self.create_table('comment_sentence_tone', '''
CREATE TABLE IF NOT EXISTS comment_sentence_tone(
  id INTEGER PRIMARY KEY,
  anger REAL NOT NULL,
  disgust REAL NOT NULL,
  fear REAL NOT NULL,
  joy REAL NOT NULL,
  sadness REAL NOT NULL,
  analytical REAL NOT NULL,
  confident REAL NOT NULL,
  tentative REAL NOT NULL,
  openness REAL NOT NULL,
  conscientiousness REAL NOT NULL,
  extraversion REAL NOT NULL,
  agreeableness REAL NOT NULL,
  neuroticism REAL NOT NULL,
  content CHAR (1000) NOT NULL,
  comment_tone_id INT NOT NULL,
  FOREIGN KEY (comment_tone_id) REFERENCES comment_tone(id)
);
''')

    def execute(self, query):
        # print("EXECUTING QUERY: {}".format(query))
        self.cursor.execute(query)
        # print("QUERY RESULT: {}".format(self.cursor.fetchone()))

    def fetch(self):
        return self.cursor.fetchall()

    def drop_table(self, table_name):
        self.execute("DROP TABLE IF EXISTS {}".format(table_name))

    def check_table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)
        self.execute(query)
        if self.fetch():
            return True
        else:
            return False

    def create_table(self, table_name, table_query):
            self.execute(table_query)

    def check_exists(self, query, query_tuple):
        self.cursor.execute(query, query_tuple)
        results = self.cursor.fetchone()
        if results:
            return True
        else:
            return False

    def get_subreddit_comments_count(self, subreddit):
        if self.check_exists("SELECT id FROM subreddits WHERE subreddit=?", (subreddit,)):
            print("subreddit {} exists, check number of comments in database".format(subreddit))
            self.cursor.execute("SELECT id FROM subreddits WHERE subreddit=?", (subreddit,))
            subreddit_id = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT * FROM comments,threads WHERE comments.thread_id=threads.id AND threads.subreddit_id=?", (subreddit_id,))
            results = self.cursor.fetchall()
            print("total comments in subreddit {} is {}".format(subreddit, len(results)))
            if results:
                return len(results)
            else:
                return None
        else:
            print("subreddit {} does not exist, continue...".format(subreddit))
            return None

    def add_subreddit(self, subreddit):
        # INSERT INTO salespeople (first_name, last_name, commission_rate) VALUES ('Fred', 'Flinstone', 10.0);
        if self.check_exists("SELECT id FROM subreddits WHERE subreddit=?", (subreddit,)):
            print("subreddit {} exists".format(subreddit))
        else:
            self.cursor.execute("INSERT INTO subreddits VALUES(NULL, ?);", (subreddit,))
            self.conn.commit()

    def get_thread_comments_count(self, thread_reddit_id):
        if self.check_exists("SELECT * FROM threads WHERE reddit_id=?", (thread_reddit_id,)):
            self.cursor.execute("SELECT id FROM threads WHERE reddit_id=?", (thread_reddit_id,))
            thread_id = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT * FROM comments WHERE thread_id=?", (thread_id,))
            results = self.cursor.fetchall()
            if results:
                return len(results)
            else:
                return None
        else:
            return None

    def get_thread_crawled(self, thread_id):
        print ("test this")
        if self.check_exists("SELECT * FROM threads WHERE reddit_id=?", (thread_id,)):
            # Thread exists, check if it's been crawled yet
            self.cursor.execute("SELECT crawled FROM threads WHERE reddit_id=?", (thread_id,))
            crawled = self.cursor.fetchone()[0]
            if int(crawled) > 0:
                return True
            else:
                return False
        else:
            return False

    def set_thread_crawled(self, thread_id):
        if self.check_exists("SELECT * FROM threads WHERE reddit_id=?", (thread_id,)):
            self.cursor.execute("UPDATE threads SET crawled=1 WHERE reddit_id=?", (thread_id,))
            print("hopefully marked thread crawled?")
        else:
            print("thread doesn't exist")

    def add_thread(self, subreddit, thread_data):
        comments_added = 0
        self.cursor.execute("SELECT id FROM subreddits WHERE subreddit=?", (subreddit,))
        subreddit_id = self.cursor.fetchone()[0]

        # Check if thread exists
        if self.check_exists("SELECT id FROM threads WHERE reddit_id=?", (thread_data['reddit_id'],)):
            print("threads exists, skip to adding comments?")
        else:
            self.cursor.execute("INSERT INTO threads VALUES(NULL,?,?,?,?,?)", (thread_data['reddit_id'], thread_data['url'], thread_data['title'], subreddit_id, 0))
            self.conn.commit()

        self.cursor.execute("SELECT id FROM threads WHERE reddit_id=?", (thread_data['reddit_id'],))
        thread_id = self.cursor.fetchone()[0]
        for comment in thread_data['comments']:
            comment_id = comment['comment_id']
            author = comment['author']
            content = comment['content']
            karma = comment['karma']
            # Check if comment exists
            if self.check_exists("SELECT id FROM comments WHERE reddit_id=?", (comment_id,)):
                print("comment {} already exists".format(comment_id))
            else:
                self.cursor.execute("INSERT INTO comments VALUES(NULL,?,?,?,?,?)", (comment_id, author, content, thread_id, karma))
                self.conn.commit()
                comments_added += 1
        return comments_added

    def get_comment(self, comment_id):
        self.cursor.execute("SELECT content FROM comments WHERE id=?",(comment_id,))
        content = self.cursor.fetchone()
        if content:
            return content[0]
        else:
            return None

    def add_document_tone(self, comment_id, content, document_tone):
        anger = 0
        disgust = 0
        fear = 0
        joy = 0
        sadness = 0
        analytical = 0
        confident = 0
        tentative = 0
        openness = 0
        conscientiousness = 0
        extraversion = 0
        agreeableness = 0
        neuroticism = 0

        if 'anger' in document_tone:
            anger = document_tone['anger']
        if 'disgust' in document_tone:
            disgust = document_tone['disgust']
        if 'fear' in document_tone:
            fear = document_tone['fear']
        if 'joy' in document_tone:
            joy = document_tone['joy']
        if 'sadness' in document_tone:
            sadness = document_tone['sadness']
        if 'analytical' in document_tone:
            analytical = document_tone['analytical']
        if 'confident' in document_tone:
            confident = document_tone['confident']
        if 'tentative' in document_tone:
            tentative = document_tone['tentative']
        if 'openness' in document_tone:
            openness = document_tone['openness']
        if 'conscientiousness' in document_tone:
            conscientiousness = document_tone['conscientiousness']
        if 'extraversion' in document_tone:
            extraversion = document_tone['extraversion']
        if 'agreeableness' in document_tone:
            agreeableness = document_tone['agreeableness']
        if 'neuroticism' in document_tone:
            neuroticism = document_tone['neuroticism']

        self.cursor.execute("INSERT INTO comment_tone VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (anger, disgust, fear,
                             joy, sadness, analytical,
                             confident, tentative, openness,
                             conscientiousness, extraversion,
                             agreeableness, neuroticism, comment_id, content))
        self.conn.commit()

    def get_document_tone_id(self, comment_id):
        self.cursor.execute("SELECT id FROM comment_tone WHERE comment_id=?", (comment_id,))
        id = self.cursor.fetchone()
        if id:
            return id[0]
        else:
            return None

    def add_comment_sentence_tone(self, comment_id, content, document_tone):
        comment_tone_id = self.get_document_tone_id(comment_id)
        if comment_tone_id is None:
            return

        anger = 0
        disgust = 0
        fear = 0
        joy = 0
        sadness = 0
        analytical = 0
        confident = 0
        tentative = 0
        openness = 0
        conscientiousness = 0
        extraversion = 0
        agreeableness = 0
        neuroticism = 0

        if 'anger' in document_tone:
            anger = document_tone['anger']
        if 'disgust' in document_tone:
            disgust = document_tone['disgust']
        if 'fear' in document_tone:
            fear = document_tone['fear']
        if 'joy' in document_tone:
            joy = document_tone['joy']
        if 'sadness' in document_tone:
            sadness = document_tone['sadness']
        if 'analytical' in document_tone:
            analytical = document_tone['analytical']
        if 'confident' in document_tone:
            confident = document_tone['confident']
        if 'tentative' in document_tone:
            tentative = document_tone['tentative']
        if 'openness' in document_tone:
            openness = document_tone['openness']
        if 'conscientiousness' in document_tone:
            conscientiousness = document_tone['conscientiousness']
        if 'extraversion' in document_tone:
            extraversion = document_tone['extraversion']
        if 'agreeableness' in document_tone:
            agreeableness = document_tone['agreeableness']
        if 'neuroticism' in document_tone:
            neuroticism = document_tone['neuroticism']

        self.cursor.execute("INSERT INTO comment_sentence_tone VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (anger, disgust, fear,
                             joy, sadness, analytical,
                             confident, tentative, openness,
                             conscientiousness, extraversion,
                             agreeableness, neuroticism, content, comment_tone_id))
        self.conn.commit()

    def get_all_comments(self):
        self.cursor.execute("SELECT id FROM comments")
        ids = self.cursor.fetchall()
        if ids:
            return ids
        else:
            return None