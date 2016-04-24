import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        self.drop_table('subreddits')
        self.drop_table('threads')

        # Check if tables exist and make them if they don't
        self.create_table('subreddits','''
        CREATE TABLE subreddits
        (id INTEGER PRIMARY key,
         subreddit VARCHAR(256) NOT NULL)''')
        self.create_table('threads', '''
        CREATE TABLE threads
        (id INTEGER PRIMARY key,
        reddit_id VARCHAR(50) NOT NULL,
        url VARCHAR(256) NOT NULL,
        title VARCHAR(128) NOT NULL),
        FOREIGN KEY(subreddits) REFERENCES subreddits(id)''')
        self.create_table('comments','')

        # if(self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'table_name'")
        # print("crap")

    def execute(self, query):
        self.cursor.execute(query)

    def fetch(self):
        return self.cursor.fetchall()

    def drop_table(self, table_name):
        self.execute("DROP TABLE IF EXISTS {}".format(table_name))

    def check_table_exists(self, table_name):
        self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name))
        if self.fetch():
            return True
        else:
            return False

    def create_table(self, table_name, table_query):
        if self.check_table_exists(table_name):
            print("TABLE {} ALREADY EXISTS, SKIPPING TABLE CREATION".format(table_name))
        else:
            print("TABLE {} DOES NOT EXIST, CREATING TABLE...".format(table_name))
            self.execute(table_query)


# c.execute('''CREATE TABLE subreddits(AUTOINCREMENT INTEGER id, VARCHAR title, INTEGER subscribers, DATE scan_date)''')

# c.execute('''INSERT INTO subreddits VALUES('')''')