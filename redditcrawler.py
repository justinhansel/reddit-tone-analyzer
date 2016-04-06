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

    def get_comment_links(self):
        subreddit_name = "buildapcsales"
        test_url = "https://www.reddit.com/r/" + subreddit_name
        self.driver.get(test_url)
        try:
            self.driver.find_element_by_id("header")
            print("Test subreddit, website is up.")
            self.website_up = True
        except TimeoutException:
            print("Timeout, test subreddit down?")
            self.website_up = False
        except NoSuchElementException:
            print("Web Element Missing, test subreddit down?")
            self.website_up = False

        try:
            test_elements = self.driver.find_elements_by_css_selector("div.entry.unvoted > ul > li.first > a")
            print("found something, " + str(test_elements.__len__()))
            comment_list = []
            for element in test_elements:
                data = element.get_attribute("href")
                if(subreddit_name in data):
                    comment_list.append(data)

            print("Final URLs")
            for url in comment_list:
                print(url)
        except NoSuchElementException:
            print("didn't find anything")


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
