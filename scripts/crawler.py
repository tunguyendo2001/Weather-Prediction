 # -*- coding: utf-8 -*-

from lib2to3.pgen2 import driver
# from tkinter import SEL
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import datetime
import calendar
import csv
import sys

def check(sentences):
    key = sentences.split(":")
    if len(key) == 1:
        return False
    dic =["1","2","3","4","5","6","7","8","9","10","11","12"]
    if key[0] in dic:
        key2 = key[1].split()
        if key2[0] == "00" or key2[0] == "30":
            return True

    return False
def get_data(words): 
    word = words.split()
    time = word[0]+ " " +word[1]
    temperature = word[2]+ " " +word[3]
    dew_point  = word[4]+ " " +word[5]
    humidity  = word[6]+ " " +word[7]
    wind = word[8]
    wind_speed = word[9]+ " " +word[10]
    wind_gust = word[11]+ " " +word[12]
    presure = word[13]+ " " +word[14]
    presip = word[15]+ " " +word[16]
    condition = word[17]
    return time,temperature,dew_point, humidity, wind, wind_speed, wind_gust, presure, presip, condition
class craigslist_crawler(object):
    def __init__(self, url):
        self.url = url
        self.browser = webdriver.Chrome("./chromedriver")

    def load_page(self,name, writer_log):
        name = "/Users/hadoop/Downloads/ds-proj/data/" + name + '.csv'
        with open(name, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)    
            #mo trang web
            browser = self.browser
            browser.get(self.url)
            sleep(10)

            try: 
                all = browser.find_element(by=By.CLASS_NAME, value="ng-star-inserted") 
                contents = all.text
                content = contents.split("\n")
                for i in content:
                    if check(i):
                        time,temperature,dew_point, humidity, wind, wind_speed, wind_gust, presure, presip, condition = get_data(i)
                        writer.writerow([time,temperature,dew_point, humidity, wind, wind_speed, wind_gust, presure, presip, condition])

                log = "[Success] Tải thành công ngày " + name
                print(" [Success] Tải thành công ngày  {}".format(name))
            except:
                log = "[Error] Tải bị lỗi ngày " + name + "tại link: " + self.url
                print("[Error] Tải bị lỗi ngày {}".format(name))

            
            writer_log.writerow([log])
            browser.close()                              
        
def get_urls(root_url ,end_day , month, year):
    urls = []
    list_date = []
    for day in range (1, end_day+1):
        url = root_url
        date = str(year)+"-"+str(month)+"-"+str(day)
        url = url + date
        urls.append(url)
        date_name ="HN" + str(year)
        if month < 10:
            date_name += "-" + "0"+str(month)
        else:
            date_name += "-" +str(month)
        if day <10: 
            date_name += "-" + "0"+str(day)
        else:
            date_name += "-" +str(day)
        list_date.append(date_name)
    return urls, list_date


def get_calender(start_year, end_year):
    list_urls = []
    list_date = []
    
    for year in range (start_year, end_year + 1):
        urls = []
        dates = []
        for month in range (1,13):
            day =  calendar.monthrange(year, month)[1]
            url, date = get_urls(root_url, day, month, year)
            urls.append(url)
            dates.append(date) 
        list_urls.append(urls)
        list_date.append(dates)    
    return list_urls, list_date

def auto_craw_data(list_urls, list_date, start_year,month_start, end_year, writer_log ):
    count = 0
    for year in range (start_year, end_year + 1):
        if count == 0:
            for month in range (month_start-1,12):
                max_day =  calendar.monthrange(year, month+1)[1]
                for day in range (0,max_day):
                    crawler = craigslist_crawler(list_urls[count][month][day])
                    #crawler = craigslist_crawler('https://www.wunderground.com/history/daily/vn/soc-son/VVNB/date/2021-1-4')
                    crawler.load_page(list_date[count][month][day], writer_log)
        else: 
            for month in range (0,12):
                max_day =  calendar.monthrange(year, month+1)[1]
                for day in range (0,max_day):
                    crawler = craigslist_crawler(list_urls[count][month][day])
                    #crawler = craigslist_crawler('https://www.wunderground.com/history/daily/vn/soc-son/VVNB/date/2021-1-4')
                    crawler.load_page(list_date[count][month][day], writer_log)
        count += 1

def choice_craw_data(link, name, writer_log):
    crawler = craigslist_crawler(link)
    crawler.load_page(name, writer_log)

if __name__ == "__main__":
    root_url = "https://www.wunderground.com/history/daily/vn/soc-son/VVNB/date/"
    choice = 1
    start_year = 2023
    month_start = 1
    end_year = 2023
    time_now = datetime.datetime.now()
    date_now = str(time_now.date())
    # date_now = "2023-02-05"
    name_log = '/Users/hadoop/Downloads/ds-proj/logs/log' + str(date_now) +'.csv'

    with open(name_log, 'w', encoding='UTF8', newline='') as f:
        writer_log = csv.writer(f) 

        if choice == 0:
            list_urls, list_date = get_calender(start_year, end_year)
            auto_craw_data(list_urls, list_date, start_year,month_start , end_year, writer_log)
        else:
            choice_craw_data('https://www.wunderground.com/history/daily/vn/soc-son/VVNB/date/'+date_now, 'HN'+date_now, writer_log)
            
        

