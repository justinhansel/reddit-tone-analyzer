from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Handles browser crawling functions
class Browser:
    def __init__(self):
        # self.driver = webdriver.Firefox(self.minimal_firefox_profile())
        self.driver = webdriver.Firefox()
        self.driver.set_script_timeout(5)
        self.driver.set_page_load_timeout(5)

        self.wait = WebDriverWait(self.driver,10)
        self.implicit_wait = 30

        self.reddit_base_url = "https://www.reddit.com/"
        self.website_up = False

    def reset_implicit_wait(self):
        self.driver.implicitly_wait(self.implicit_wait)

    # Check if website is up
    def check_reddit_status(self):
        self.driver.implicitly_wait(5)
        self.driver.get(self.reddit_base_url)
        try:
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
            self.driver.implicitly_wait(5)
        else:
            self.driver.implicitly_wait(implicit_wait)
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

    def get_comment_links(self):
        subreddit_name = "buildapcsales"
        test_url = "https://www.reddit.com/r/" + subreddit_name
        self.driver.get(test_url)

        # Find exception helpers
        find = self.find_exception
        f = lambda: self.driver.find_element_by_id("header")
        subreddit_threads = []
        subreddit_page = find(f, 1, subreddit_name + " subreddit")
        if subreddit_page is not None: # Subreddit page loaded correctly
            f = lambda: self.driver.find_elements_by_css_selector("div.entry.unvoted > ul > li.first > a")
            page_link_elements = find(f, 1, subreddit_name + " page link elements")
            if page_link_elements is not None: # Found page link elements
                # Get links from elements
                page_links = []
                for element in page_link_elements:
                    data = element.get_attribute("href")
                    if subreddit_name in data:
                        page_links.append(data)
                threads_read = 0
                comments_read = 0
                for url in page_links:
                    # Get unique thread id from url
                    thread_id = str(url).split('/')[6]

                    # Thread data holds keys for id, TODO: figure out what else goes here
                    thread_data = {}
                    thread_data["id"] = thread_id

                    # Navigate to thread url
                    self.driver.get(url)
                    f = lambda: self.driver.find_element_by_id("header")
                    thread_page = find(f, 10,"Thread " + thread_id)
                    if thread_page is not None: # Thread page loaded properly
                        # Get thread title
                        f = lambda: str(self.driver.find_element_by_css_selector("div.entry.unvoted > p.title > a").text)
                        title = find(f, 1, "Thread title " + thread_id)
                        thread_data["title"] = title

                        # Get comment elements
                        f = lambda: self.driver.find_elements_by_css_selector("div.entry.unvoted")
                        comment_elements = find(f, 1, "Thread comment elements " + thread_id)
                        if comment_elements is not None:
                            comment_count = 0
                            for element in comment_elements:
                                f = lambda: element.find_element_by_css_selector("ul.flat-list > li.first > a")
                                comment_id = find(f, 1, "\tcomment_id")
                                if comment_id is not None:
                                    comment_id = comment_id.get_attribute("href")
                                else:
                                    continue

                                f = lambda: element.find_element_by_css_selector("p.tagline > a.author")
                                author = find(f, 1, "\tauthor")
                                if author is not None:
                                    author = author.text
                                else:
                                    continue

                                f = lambda: element.find_element_by_css_selector("p.tagline > span.score.unvoted")
                                karma = find(f, 1, "\tkarma")
                                if karma is not None:
                                    karma = karma.text
                                else:
                                    continue

                                f = lambda: element.find_element_by_css_selector("p.tagline > time")
                                time_posted = find(f, 1, "\ttime_posted")
                                if time_posted is not None:
                                    time_posted = time_posted.get_attribute("title")
                                else:
                                    continue

                                f = lambda: element.find_elements_by_css_selector("form > div > div.md")
                                content = ""
                                contents = find(f, 1, "\tcontent")
                                if contents is not None:
                                    for p in contents:
                                        content += p.text + "\n"
                                else:
                                    continue
                                print("author: {}\nkarma:{}\ntime_posted:{}\ncontent:{}".format(author, karma, time_posted, content))
                                comment_count += 1
                                if comment_count > 9:
                                    print("READ OVER THREAD COMMENTS LIMIT, STOP READING THREAD COMMENTS")
                                    break
                            comments_read += comment_count
                            print("FINISHED PROCESSING THREAD " + thread_id + ": " + thread_data["title"])
                            print("\tTOTAL COMMENTS READ: " + str(comments_read))
                            if comments_read > 99:
                                print("READ OVER SUBREDDIT COMMENTS LIMIT, STOP READING LINKS/PAGES")
                                break


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
