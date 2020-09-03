import scrapy
import re
import time
import requests
import html
from scrapy import Selector
from BookReviewCrawler.items import Book
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoodReadsSpider(scrapy.Spider):
    name = 'goodreads'
    BASE_URL = 'https://www.goodreads.com'
    start_urls = ['https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30']
    wait_time = 100

    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        bookURLs = response.css(".bookTitle").xpath("@href").extract()

        # get all books on the page
        for url in bookURLs:
            link = self.BASE_URL + url
            bookItem = Book()
            bookItem['Link'] = link
            bookItem['BookID'] = re.findall(r'\d+', link)[0]
            yield scrapy.Request(link, callback=self.parse_book, meta={'item' : bookItem})

        # go to the books on next page if exists
        next_page = response.css(".current+ a").xpath("@href").extract_first()
        if next_page is not None:
            yield scrapy.Request(self.BASE_URL + next_page, callback=self.parse)


    def parse_book(self, response):
        bookItem = response.meta['item']
        bookItem['Title'] = response.css("#bookTitle::text").extract()[0].lstrip().rstrip()
        bookItem['Author'] = response.css(".authorName span::text").extract()[0].lstrip().rstrip()
        bookItem['Rate'] = float(response.css("span[itemprop='ratingValue']::text").extract()[0])
        
        descriptionList = response.css("#description span")
        # There is no description
        if len(descriptionList) == 0:
            bookItem['Description'] = None
        # There is a description
        elif len(descriptionList) == 1:
            bookItem['Description'] = ''.join(descriptionList[0].css("::text").extract()).lstrip().rstrip()
        # The description is truncated
        else:
            bookItem['Description'] = ''.join(descriptionList[1].css("::text").extract()).lstrip().rstrip()    

        bookItem['Review'] = self.parse_review(response)

        yield bookItem

    def parse_review(self, response):
        self.driver.get(response.request.url)
        
        # view reviews of all languages
        try:
            print(self.driver.find_element_by_xpath("//select[@name='language_code']/option[@selected='selected']").text)
            self.driver.find_element_by_xpath("//select[@name='language_code']/option[text()='All Languages']").click()
            WebDriverWait(self.driver, self.wait_time).until(EC.invisibility_of_element((By.XPATH, "//select[@name='language_code']/option[@selected='selected']")))
        except:
            pass

        res = []
        while True:
            selenium_response_text = self.driver.page_source
            response = Selector(text=selenium_response_text)
            reviewList = response.xpath("//div[contains(@class, 'friendReviews elementListBrown')]")
            
            # get all reviews on the page
            for review in reviewList:
                user_name = review.css(".user::text").extract()[0]
                user_id = re.findall(r'\d+', review.css(".review a").xpath("@href").extract()[0])[0]
                rate = len(review.css("[class='staticStar p10']"))
                date = review.css(".reviewDate::text").extract()[0]
                contentList = review.css(".readable span")
                content = None
                # There is a review content
                if len(contentList) == 1:
                    content = ''.join(contentList[0].css("::text").extract()).lstrip()
                # The review content is truncated
                elif len(contentList) > 1:
                    content = ''.join(contentList[1].css("::text").extract()).rstrip()
                
                # get comments for this review
                commentList = None
                if len(contentList) != 0:
                    comment_page = self.BASE_URL + review.css(".likeItContainer+ a").xpath("@href").extract()[0]
                    commentList = self.parse_comment(comment_page)

                # add a review to res
                res.append([{
                    'UserName' : user_name,
                    'UserID' : user_id,
                    'Rate' : rate,
                    'Date' : date,
                    'Content' : content,
                    'Comment' : commentList
                }])

            # check if there is another page of reviews
            try:
                cur_page_index = self.driver.find_element_by_xpath("//div[@class='uitext']/div[1]/em[@class='current']").text
                self.driver.find_element_by_xpath("//div[@class='uitext']/div[1]/a[@rel='next']").click()
                WebDriverWait(self.driver, self.wait_time).until(EC.invisibility_of_element((By.XPATH, "//div[@class='uitext']/div[1]/em[@class='current' and text()="+cur_page_index+"]")))
            except:
                break

        return res if len(res) > 0 else None       

    def parse_comment(self, url):
        req = requests.get(url)
        response = scrapy.Selector(req)
        commentList = response.css("#comment_list [class='comment u-anchorTarget']")
        res = []
        for comment in commentList:
            res.append(''.join(comment.css(".reviewText::text").extract()).lstrip().rstrip())
        return res if len(res) > 0 else None
