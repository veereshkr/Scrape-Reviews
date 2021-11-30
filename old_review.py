import requests
from pymongo import MongoClient
import json
import datetime
import uuid
import datetime
#import uuid
client = MongoClient('')
db = client.competition
posts = db.competition_data
import re
#import numpy as np
import random
#ips = np.load('proxies.npy')
#print len(ips)
#ip=ips[random.randint(1,100000000)%(3)]
#print ip
#proxies = { 'https':ip}
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from scrapy import Selector
from multiprocessing.dummy import Pool as ThreadPool

#link  = posts.find_one({ 'review_ids_updated_at':{'$exists':False}, "review_count" :{'$mod':[2,0]}})
hotels =db.hotels_data
def one_loop(t):
    print ('------',t, '------')
    oldlink = True
    target =50
    r = random.randint(100,200)
    link  = posts.find({ 'review_count':{'$gt':5},'$or':[{ 'scraped_reviews_count':{'$exists':False}},{ '$and': [{'scraped_reviews_count':{'$lt':target}}, {'old_reviews_scraped_completely':{'$exists':False}} ] }  ] }).limit(1).skip(r).next()
    #print (link['href'], link['review_count'])
    main_link  = link['href']
    count = link['review_count']
    location = link['location_id']
    print count
    scraped_review_count = hotels.find_one({'_id': location},{'review_ids':1, '_id':1})
    if (((len(scraped_review_count['review_ids']) )%5) >0 ) :
	c_count = len(scraped_review_count['review_ids']) + (5-((len(scraped_review_count['review_ids']) )%5))
    else:
	c_count = len(scraped_review_count['review_ids'])
    if(( c_count< count) and (c_count< 55)  ):
	review_ids = scraped_review_count['review_ids']
	print ('eligible', c_count)
	proxy_host = "proxy.crawlera.com"
	proxy_port = "8010"
	proxy_auth = ':'
	proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
	      "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}

	url = 'https://www.tripadvisor.com'+link['href']
	url = ("-".join(url.split("-", 4)[0:4])).encode("utf-8") + '-or'+str(c_count)+'-'+("-".join(url.split("-", -2)[-2:])).encode("utf-8")
	print url

	res = r= requests.get(url, proxies=proxies,verify=False )
	print("""
	Requesting [{}]
	through proxy [{}]

	Response Time: {}
	Response Code: {}

	""".format(url, proxy_host, r.elapsed.total_seconds(),
		   r.status_code, r.headers, r.text))

	if(r.status_code ==200):
	    #posts.update({ '_id':link['_id']}, {'$set':{'price':price,'review_ids_updated_at':datetime.datetime.now().isoformat() } }, upsert=True)
	    sel = Selector(text=res.text, type="html")
	    r_c = sel.css('span.reviewCount::text')[0].extract()
	    r_c = int((r_c.strip().split(" ", 1)[0]).replace(',',''))
	    print r_c
	    s = sel.css('a.title').xpath('@href').extract()
	    o_review_ids =[]
	    for i in s:
		r_id = (("-".join(i.split("-", 4)[3:4])).encode("utf-8"))
		#print r_id
		o_review_ids.append (int(r_id[1:]))
	    review_ids +=o_review_ids
	    #print review_ids
	    rating_dist =[]
	    r_d = sel.css('span.row_count::text').extract()
	    for i in r_d:
		rating_dist.append(int(i[:-1]))
	    #print rating_dist

	    #print sel.css('p.partial_entry')[0].extract()
	    hotels.update({ '_id':location}, {'$addToSet':{ 'review_ids':{ '$each':o_review_ids}}, '$set':{"review_count":r_c , 'rating_dist':rating_dist }},upsert=True)
	    print (datetime.datetime.now().isoformat(), '----------------')
	    if(len(review_ids) >= count):
		posts.update({'location_id':location}, {'$set':{'scraped_reviews_count':len(review_ids), 'old_reviews_scraped_completely':True}}, multi=True , upsert=True)
	    else:
		posts.update({'location_id':location}, {'$set':{'scraped_reviews_count':len(review_ids)}}, multi= True  ,upsert =True)

tracker =range(6)
pool = ThreadPool(6)
results = pool.map(one_loop, tracker)
