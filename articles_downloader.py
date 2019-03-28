
## Description: Matrix Home assignment.
## Author: Dor Mordechai.


from requests import get
from bs4 import BeautifulSoup
from os import path, makedirs, getcwd, listdir
import re
from json import loads, dump
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Website:

    """
    Class that defines a Website. mostly used for it inner functions.
    """

    def __init__(self):
        """
        Initiate the class, running ensure_dir() function.
        """
        self.ensure_dir()

    def getBSContent(self, url):

        """
        Getting the website source code using Requests package.

        :param url: Url for web scrapping.
        :return: BeautifulSoup object for this website.
        """

        # Getting the content of a web page using GET request
        raw_web_data = get(url = url)
        web_data = raw_web_data.content.decode("utf-8")

        # Returning a BeautifulSoup object created with the web page content data.
        return BeautifulSoup(web_data, "html.parser")


    def getBSContent_selenuim(self, url):

        """
        Getting the website source code using Selenium package.

        :param url: Url for web scrapping using Selenium instead of Requests package.
        :return: BeautifulSoup object for this website.
        """

        # Chrome driver path location supposed to be in the current folder under /files folder.
        CHROMEDRIVER_PATH = getcwd() + r"\Files\chromedriver.exe"

        # Creates headless chrome browser.
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
        driver.get(url)

        # Getting the web page source code.
        web_data = driver.page_source
        driver.close()

        # Returning a BeautifulSoup object created with the web page content data.
        return BeautifulSoup(web_data, "html.parser")



    def ensure_dir(self):

        """
        Checks it there is a folder with the name of the class (a.k.a the website) in the current dir,
        if not - it creates one.

        :return: Nothing.
        """

        # dir_name = name of the object, for example "CnnNews"
        dir_name = self.__class__.__name__

        # Create the directory if not exist. for example - the "CnnNews" directory
        if not path.exists(dir_name):
            makedirs(dir_name)


    def remove_spec_char(self, title):

        """
        Taking a string, and removing special characters from it.

        :param title: A string for special characters removing operation.
        :return: The same string without special characters
        """

        # Returning the same title without special characters using regular expression.
        return re.sub("[^A-Za-z0-9 ]+", "", title)


    def search_in_data(self, key_word):

        """
        Getting a keyword, and search in every file in the object folder for this keyword.

        :param key_word: String contains Word/sentence to search in these files.
        :return: List that contains the files that contains the key_word
        """

        dir_name = getcwd() + "\\" + self.__class__.__name__
        prefix_in_files = []

        try:
            # Go through every file on the selected directory.
            for filename in listdir(dir_name):
                with open('{}\\{}'.format(dir_name, filename), 'r') as infile:

                    # Opening the file and getting the JSON data.
                    json_from_file = loads(infile.read())
                    infile.close()

                # If the file contains the key_word string - add filename to a list.
                if re.search(key_word, json_from_file['data']):
                    prefix_in_files.append(filename)

        except Exception as e:
            print("Exception in file: {} , exception is:  {}".format(filename, str(e)))

        return(prefix_in_files)



class CnnNews(Website):

    def __init__(self):

        """
        Inherits from "Website" Class.
        using "Website" Init, and adding self.url and self.data object (BeautifulSoup object of Cnn Url)
        """

        super().__init__()
        self.url = "https://edition.cnn.com/"

        # Getting a BeautifulSoup object using selenium for the self.url
        self.data = self.getBSContent_selenuim(self.url)

    def getArticles(self):

        """
        Using the self.data object, search for "cd__headline" class - the beginning of an article, and then search
         for "cd__headline-text" class - the title of this article.
         after getting the above information - creates a dictionary with the following fields:
         "name" - the first 15 characters of the title, without any special chars.
         "url"  - the url of the article.

         and then append it to a list called "articles_data".

         After going through the whole self.data data, append the "articles_data" list to self.articles object.

        :return: None.
        """

        articles_data = []

        # Search in the self.data object (scrapped HTML data of the website) for .cd__headline classes
        for link in self.data.select('.cd__headline'):

            try:

                # If the link contains incomplete data (without http or www for example) - complete it with the full url
                # and then create a dictionary object add it to a list called "articles_data"
                if(link.select('a')[0]["href"].startswith('/')):
                    articles_data.append({"name": self.remove_spec_char(link.select('.cd__headline-text')[0].text[:15]),
                                          "url": "https://edition.cnn.com" + link.select('a')[0]["href"]})
                else:
                    articles_data.append({"name": self.remove_spec_char(link.select('.cd__headline-text')[0].text[:15]),
                                          "url": link.select('a')[0]["href"]})
            except:
                continue

        # Set self.articles to the list called "articles data"
        self.articles = articles_data


    def save_articles(self):

        """
        Go through every article (dictionary) from the self.articles object, checking if there is a
        file name named "articleName.json" (article["name"].json). or if the article is a video file - Continue. else -
        Get the article data from "getBSContent_selenuim()" function, and search for the article body.
        after finding the article body, create dictionary in this format: {"url": article["url"], "data": output}
        and save is as json file with the name of the article.json (article["name"].json).

        :return: None
        """

        dir_name = getcwd() + "\\" + self.__class__.__name__ + "\\"

        # For every article data found in the home page of the website
        for article in self.articles:

            file_path = dir_name + article["name"] + ".json"
            body_content = []

            # If article exist or if it's a video content - skip
            if (article["url"].startswith("https://video") or path.isfile(file_path)):
                continue

            # Getting a BeautifulSoup object using selenium for the article["url"]
            page_data = self.getBSContent_selenuim(article["url"])

            try:
                # Try to get the article body from the BeautifulSoup object
                for page_content in page_data.select('.l-container .zn-body__paragraph'):
                    body_content.append(page_content.text)

                output = '\n'.join(body_content)

                # Save the article body + url in JSON format in a JSON file
                with open(file_path, 'w') as outfile:
                    dump({"url": article["url"], "data": output}, outfile)

            except Exception as e:
                print("Error: " + str(e) + ' In file: ' + str(article["name"]))


class FoxNews(Website):

    def __init__(self):

        """
        Inherits from "Website" Class.
        using "Website" Init, and adding self.url and self.data object (BeautifulSoup object of Cnn Url)
        """

        super().__init__()
        self.url = "https://www.foxnews.com/"

        # Getting a BeautifulSoup object using Requests package for the self.url
        self.data = self.getBSContent(self.url)

    def getArticles(self):

        """
        Using the self.data object, search for "article" class - the beginning of an article, and then search
         "title" class - the title of this article.
         after getting the above information - creates a dictionary with the following fields:
         "name" - the first 15 characters of the title, without any special chars.
         "url"  - the url of the article.

         and then append it to a list called "articles_data".

         After going through the whole self.data data, append the "articles_data" list to self.articles object.

        :return: None.
        """
        atricles_data = []

        # Search in the self.data object (scrapped HTML data of the website) for article classes
        for link in self.data.findAll(class_='article'):

            # If the link contains incomplete data (without http or www for example) - complete it with the full url
            # and then create a dictionary object add it to a list called "articles_data"
            if(link.find(class_='title').find('a')["href"].startswith('//')):
                atricles_data.append({"name": self.remove_spec_char(link.find(class_='title').text[:15]),
                               "url": link.find(class_='title').find('a')["href"].replace("//", r"https://")})

            else:
                atricles_data.append({"name": self.remove_spec_char(link.find(class_='title').text[:15]),
                               "url": link.find(class_='title').find('a')["href"]})

        # Set self.articles to the list called "articles data"
        self.articles = atricles_data


    def save_articles(self):

        """
        Go through every article (dictionary) from the self.articles object, checking if there is a
        file name named "atricleName.json" (article["name"].json). or if the article is a video file - Continue. else -
        Get the article data from "getBSContent()" function, and search for the article body.
        after finding the article body, create dictionary in this format: {"url": article["url"], "data": output}
        and save is as json file with the name of the article.json (article["name"].json).

        :return: None
        """

        dir_name = getcwd() + "\\" + self.__class__.__name__ + "\\"

        # For every article data found in the home page of the website
        for article in self.articles:

            file_path = dir_name + article["name"] + ".json"

            # If article file exist or if it's a video content - skip
            if(article["url"].startswith("https://video") or path.isfile(file_path)):
                continue

            # Getting a BeautifulSoup object using Requests Package for the article["url"]
            page_data = self.getBSContent(article["url"])

            try:
                # Try to get the article body from the BeautifulSoup object
                body_content = page_data.find(True, {'class': ['article-body', 'article-text']}).findAll('p')
                body_content = [cell.getText() for cell in body_content]
                output = '\n'.join(body_content)

                # Save the article body + url in JSON format in a JSON file
                with open(file_path, 'w') as outfile:
                    dump({"url": article["url"], "data": output}, outfile)

            except Exception as e:
                print("Error: " + str(e) + ' In file: ' + str(article["name"]))