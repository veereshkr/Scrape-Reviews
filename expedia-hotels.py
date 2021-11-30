import uuid
import numpy as np
import random
import urllib3
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#links = np.load('links_new.txt.npy')
links = np.load('pages.npy')
url=links[random.randint(1,100000000)%len(links)]

start_date =  datetime.date.today()+ timedelta(days=2)
end_date =   datetime.date.today()+ timedelta(days=3)
new_url = "".join(url.split("&", -1)[0])+'&'+'{:02d}'.format(start_date.month)+'/{:02d}'.format(start_date.day)+'/{:02d}'.format(start_date.year)+'&'+'{:02d}'.format(end_date.month)+'/{:02d}'.format(end_date.day)+'/{:02d}'.format(end_date.year)+ "&".join(url.split("&", -1)[-4:])
chrome = webdriver.Chrome(chrome_options=options, executable_path='/home/su/scrapy-pro/bin/chromedriver')
chrome.get(url)
data =chrome.page_source
soup = BeautifulSoup(data, "html.parser")
all_articles =[]
for i in soup.find_all('nav', class_='pagination'):
    if(("".join(url.split("&", -1)[-1]) ) == 'page=1'):
        append_count =0
        if (int(i.get('data-total-results')) >50):
            number_of_pages = (int(i.get('data-total-results'))/50)+1
            for k in range(2, number_of_pages):
                new_url = url[:-1]+str(k)
                if new_url not in links:
                    links = np.append(links,new_url)
                    append_count +=1
        if(append_count > 0):
            np.save('/home/su/scrapy-pro/pages.npy',links)
            print 'file updated'

for i in soup.find_all('article', class_='hotel'):
    all_articles.append(i)


hotels_info =[]
for article in all_articles:
    details ={}
    for i in article.find_all('a', href= True, class_='flex-link'):
        details['hotel_link'] = i['href']
    for i in article.find_all('h4', class_='hotelName'):
        details['hotel_name'] = (i.text.strip()).encode("utf-8")
    for i in article.find_all('span', title= True, class_='stars-grey'):
        details['stars'] = round(float(i['title']),1)
    for stars in article.find_all('li', class_='starRating'):
        for rating in stars.find_all('span', title=True, class_='value_title'):
            details['hotel_rating'] = rating['title']
    for ratings in article.find_all('li', class_='reviewOverall'):
        counter = 0
        for all_ratings in ratings.find_all('span'):
            counter+=1
            if(counter==2):
                details[‘ratings’] = round(float((all_ratings.text.strip()).encode("utf-8”)), 1)
    for review_count in article.find_all('li', class_='reviewCount'):
        counter = 0
        for all_span in review_count.find_all('span'):
            counter+=1
            if(counter==2):
	           details[‘review_count’] =   int((all_span.text.strip()).encode("utf-8”).replace(',','').replace(' reviews)','').replace(‘(‘,’’))

    for prices in article.find_all(‘span’, class_='actualPrice'):
        details[‘actual_price’] = (prices.text.strip()).encode("utf-8")
    hotels_info.append(details)
try:
    print url
    print str(datetime.datetime.now())
#print complete_info
    posts.insert_many(exp_hotel_info)
    #posts.update({ '_id':_id}, {'$set':{'_id':_id ,'competitors':complete_info, 'area_code':found, 'updated_at':datetime.datetime.now().isoformat() } }, upsert=True)
except:
    print 'failed to update db'
chrome.close()
