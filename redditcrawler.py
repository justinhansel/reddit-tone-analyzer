from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from datetime import datetime

# Handles browser crawling functions
class Browser:
    def __init__(self, database):
        # self.driver = webdriver.Firefox(self.minimal_firefox_profile())
        self.driver = webdriver.Firefox()
        self.driver.set_script_timeout(5)
        self.driver.set_page_load_timeout(5)

        self.wait = WebDriverWait(self.driver,10)
        self.implicit_wait = 30

        self.reddit_base_url = "https://www.reddit.com/"
        self.website_up = False

        self.MAX_COMMENTS_PER_SUBREDDIT = 500
        self.MAX_COMMENTS_PER_THREAD = 20

        self.find = self.find_exception

        self.db = database

    def reset_implicit_wait(self):
        self.driver.implicitly_wait(self.implicit_wait)

    # Check if website is up
    def check_reddit_status(self):
        try:
            self.driver.implicitly_wait(5)
            self.driver.get(self.reddit_base_url)
            self.driver.find_element_by_id("header")
            print("Success, website is up.")
            self.website_up = True
        except TimeoutException:
            print("Timeout, website down?")
            self.website_up = False
        except NoSuchElementException:
            print("Web Element Missing, website down?")
            self.website_up = False
        self.reset_implicit_wait()

    def goto_subreddit(self,subreddit):
        print("TODO thing")

    def find_exception(self, func, implicit_wait=None, error=None):
        if implicit_wait is not None:
            self.driver.implicitly_wait(0)
        else:
            self.driver.implicitly_wait(0)
        try:
            result = func()
            print(error + " NoExceptions")
            return func()
        except TimeoutException:
            if error is not None:
                print(error + " TimeoutException")
            else:
                print("TimeoutException")
            return None
        except NoSuchElementException:
            if error is not None:
                print(error + " NoSuchElementException")
            else:
                print("NoSuchElementException")
            return None

    def crawl_subreddit(self, subreddit_name):
        # Check if number of comments in database is over limit
        total_comments = self.db.get_subreddit_comments_count(subreddit_name)

        subreddit_url = "https://www.reddit.com/r/" + subreddit_name

        # self.driver.get(subreddit_url)
        self.get_thread_page(subreddit_url, subreddit_name)

        # Add subreddit to database
        self.db.add_subreddit(subreddit_name)

        # Find exception helpers
        find = self.find_exception

        subreddit_threads = []

        page_links = self.get_page_links(subreddit_name)

        if total_comments is None:
            total_comments = 0

        if page_links is None:
            print ("something bad happened")
            return

        for url in page_links:
            if url is None:
                continue
            # Get unique thread id from url
            url_array = str(url).split('/')
            if len(url_array) < 6:
                continue
            thread_id = url_array[6]

            # Check if thread is crawled
            crawled = self.db.get_thread_crawled(thread_id)
            if crawled:
                continue

            # Navigate to thread url
            thread_page = self.get_thread_page(url, thread_id)
            thread_title = self.get_thread_title(thread_page, thread_id)

            thread_comments_elements = self.get_thread_comments_elements(thread_page, thread_id)
            thread_comments = self.get_thread_comments(thread_comments_elements, thread_id)
            thread_data = {"reddit_id": thread_id,
                           "url": url,
                           "title": thread_title,
                           "comments": thread_comments}
            thread_comments_added = self.db.add_thread(subreddit_name, thread_data)
            total_comments += thread_comments_added
            subreddit_threads.append(thread_data)
            print("CURRENT TOTAL COMMENTS: " + str(total_comments))
            if total_comments > self.MAX_COMMENTS_PER_SUBREDDIT:
                print("REACHED MAX COMMENTS FOR SUBREDDIT, EXITING")
                break

    def get_page_links(self, subreddit):
        f = lambda: self.driver.find_element_by_id("header")
        subreddit_page = self.find(f, 1, subreddit + " subreddit")
        page_links = []
        if subreddit_page is not None: # Subreddit page loaded correctly
            f = lambda: self.driver.find_elements_by_css_selector("div.entry.unvoted > ul > li.first > a")
            page_link_elements = self.find(f, 1, subreddit + " page link elements")
            if page_link_elements is not None: # Found page link elements
                # Get links from elements
                for element in page_link_elements:
                    data = element.get_attribute("href")
                    if subreddit in data:
                        page_links.append(str(data))
        if len(page_links) > 0:
            return page_links
        else:
            return None

    def get_thread_page(self, thread_url, thread_id):
        self.driver.get(thread_url)
        f = lambda: self.driver.find_element_by_id("header")
        thread_page = self.find(f, 10, "Thread " + thread_id)
        return thread_page

    def get_thread_title(self, thread_page, thread_id):
        f = lambda: self.driver.find_element_by_css_selector("div.entry.unvoted > p.title > a")
        title = self.find(f, 1, "Thread title " + thread_id)
        return title.text

    def get_thread_comments_elements(self, thread_page, thread_id):
        f = lambda: self.driver.find_elements_by_css_selector("div.entry.unvoted")
        comment_elements = self.find(f, 1, "Thread comment elements " + thread_id)
        if comment_elements is not None:
            return comment_elements
        else:
            return None

    def get_thread_comments(self, thread_comments_elements, thread_id):
        # Check how many comments we've gotten from this thread
        comment_count = self.db.get_thread_comments_count(thread_id)
        if comment_count is None:
            comment_count = 0
        elif comment_count > self.MAX_COMMENTS_PER_THREAD:
            self.db.set_thread_crawled(thread_id)

        f = lambda: self.driver.find_elements_by_css_selector("div.entry.unvoted")
        comment_elements = self.find(f, 1, "Thread comment elements " + thread_id)
        if comment_elements is not None:
            thread_comments = []
            old_comment_count = 0
            curr_dt = datetime.now()
            for element in comment_elements:
                f = lambda: element.find_element_by_css_selector("ul.flat-list > li.first > a")
                comment_id = self.find(f, 1, "\tcomment_id")
                if comment_id is not None:
                    comment_id = str(comment_id.get_attribute("href")).split('/')[8]
                else:
                    continue

                f = lambda: element.find_element_by_css_selector("p.tagline > a.author")
                author = self.find(f, 1, "\tauthor")
                if author is not None:
                    author = author.text
                else:
                    continue

                f = lambda: element.find_element_by_css_selector("p.tagline > span.score.unvoted")
                karma = self.find(f, 1, "\tkarma")
                if karma is not None:
                    karma = karma.text
                    try:
                        karma_num = int(str(karma).strip("point").strip("points").strip(" "))
                        karma = karma_num
                    except ValueError:
                        print("Problems parsing karma")

                else:
                    continue

                f = lambda: element.find_element_by_css_selector("p.tagline > time")
                time_posted = self.find(f, 1, "\ttime_posted")
                if time_posted is not None:
                    time_posted = time_posted.get_attribute("title")
                    time_posted = str(time_posted)
                    dt = datetime.strptime(time_posted, "%a %b %d %X %Y %Z")
                    diff = curr_dt - dt
                    if diff.days > 2:
                        old_comment_count += 1
                        if old_comment_count >= 5:
                            break
                        continue
                else:
                    continue

                f = lambda: element.find_elements_by_css_selector("form > div > div.md")
                content = ""
                contents = self.find(f, 1, "\tcontent")
                if contents is not None:
                    for p in contents:
                        content += p.text + "\n"
                else:
                    continue
                comment = { "comment_id": comment_id,
                            "author": author,
                            "karma": karma,
                            "time_posted": time_posted,
                            "content": content  }
                thread_comments.append(comment)
                print("author: {}\nkarma:{}\ntime_posted:{}\ncontent:{}".format(author, karma, time_posted, content))
                comment_count += 1
                if comment_count > self.MAX_COMMENTS_PER_THREAD:
                    print("READ OVER THREAD COMMENTS LIMIT, STOP READING THREAD COMMENTS")
                    self.db.set_thread_crawled(thread_id)
                    break
            # Mark thread crawled
            self.db.set_thread_crawled(thread_id)
            return thread_comments
        else:
            return None


    # Profile definition to remove images, flash, styling
    def minimal_firefox_profile(self):
        # get the Firefox profile object
        firefoxProfile = FirefoxProfile()
        # Disable CSS
        firefoxProfile.set_preference('permissions.default.stylesheet', 2)
        # Disable images
        firefoxProfile.set_preference('permissions.default.image', 2)
        # Disable Flash
        firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
        return firefoxProfile
