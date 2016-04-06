import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        # if(self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'table_name'")
        # print("crap")
        self.cursor.execute()



# c.execute('''CREATE TABLE subreddits(AUTOINCREMENT INTEGER id, VARCHAR title, INTEGER subscribers, DATE scan_date)''')

# c.execute('''INSERT INTO subreddits VALUES('')''')