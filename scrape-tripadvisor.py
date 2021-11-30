import requests
from pymongo import MongoClient
import json
import datetime
import uuid
import datetime
#import uuid
client = MongoClient('')
db = client.competition
reviews = db.reviews
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
#link  = posts.find_one({ 'review_ids_updated_at':{'$exists':False}, "review_count" :{'$mod':[2,0]}})
hotels =db.hotels_data
oldlink = True
locs = random.randint(25,35)
target =50
links  = hotels.find({  'first_review_reached':{'$exists':False} ,'review_count':{'$gt':105}, '$or':[ {'scraper_counter':{'$exists':False} }, {'scraper_counter':{'$lt':49} }  ] },{ '_id':1, 'review_ids':1, 'review_count':1, 'scraper_counter':1}).limit(locs)
#links  = hotels.find({  'first_review_reached':{'$exists':False} ,'$or':[ {'scraper_counter':{'$exists':False} }, {'scraper_counter':{'$lt':49} }  ] ,'$or':[{ 'review_ids':{'$size':50}}, { 'review_ids':{'$size':51}}, { 'review_ids':{'$size':52}},{ 'review_ids':{'$size':53}} , { 'review_ids':{'$size':54}}] },{ '_id':1, 'review_ids':1, 'review_count':1, 'scraper_counter':1}).limit(locs)
addedlist =''
locations =[]
f_r_r ={}
s_c ={}
for link in links:
    #print link['review_ids']
    #print link
    if 'scraper_counter' in link:
        print ('-------', link['scraper_counter'], link['review_count'])
        start = link['scraper_counter']
    else:
        start = 5
    end = start+ random.randint(2,4)
    state =False
    if(end >= len(link['review_ids']) ):
        print link['_id']
        end = len(link['review_ids'])
        if(end >=link['review_count']):
            state = True
    print (start, end)
    s_c[link['_id']]= end
    f_r_r[link['_id']]= state
    locations.append(link['_id'])
    for i in link['review_ids'][start:end]:
        addedlist += str(i)+','
addedlist = addedlist[:-1]
#print addedlist
print locations
url ='https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS&metaReferer=Hotel_Review&reviews='+addedlist
print url

proxy_host = "proxy.crawlera.com"
proxy_port = "8010"
proxy_auth = ''
proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
      "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}

#url = 'https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS&metaReferer=Hotel_Review&reviews=571164063'
res = r= requests.get(url, proxies=proxies,verify=False )
print("""
Requesting [{}]
through proxy [{}]

Response Time: {}
Response Code: {}

""".format(url, proxy_host, r.elapsed.total_seconds(),
           r.status_code, r.headers, r.text))
if(r.status_code ==200):
    #print links
    for location in locations:
        if(f_r_r[location]):
            hotels.update({'_id':location},{'$set':{'first_review_reached': True} }, upsert=True)
        else:
            hotels.update({'_id':location},{'$set':{'scraper_counter':s_c[location]  } }, upsert=True)
    doc = Selector(text=res.text, type="html")
    sel = doc.css('div.reviewSelector').extract()
    #print sel
    print len(sel)
    r_d ={}
    for i in range(len(sel)):
        s =  Selector(text = sel[i], type ='html')
        r_d['_id'] = int(s.css('div.reviewSelector::attr(data-reviewid)')[0].extract())
        try:
            r_i = s.css('div.reviewItemInline')[0].extract()
            r_i = Selector(text=r_i, type='html')
            ratings= r_i.css('span.ui_bubble_rating::attr(class)')[0].extract()
            ratings = ("".join(ratings.split(" ", 2)[1:2])).encode("utf-8")
            if(ratings == 'bubble_50'):
                r_d['ratings'] = 5
            if(ratings == 'bubble_40'):
                r_d['ratings'] = 4
            if(ratings == 'bubble_30'):
                r_d['ratings'] = 3
            if(ratings == 'bubble_20'):
                r_d['ratings'] = 2
            if(ratings == 'bubble_10'):
                r_d['ratings'] = 1
            if(ratings == 'bubble_0'):
                r_d['ratings'] = 0
        except:
            pass
        r_d['avatar'] = s.css('img.basicImg::attr(src)')[0].extract()
        r_d['guest_name'] = s.css('span.scrname::text')[0].extract()
        r_d['badge_values'] = s.css('span.badgetext::text').extract()
        r_d['rating_date'] =  datetime.datetime.strptime(s.css('span.ratingDate::attr(title)')[0].extract(), '%B %d, %Y').isoformat()
        try:
            title =s.css('span.noQuotes::text')[0].extract()
            r_d['title'] = title
        except:
            pass
        try:
            r_r = s.css('div.entry').extract()
            if (len(r_r) >1):
                r_revs = Selector(text=r_r[0], type='html')
                r_revs = r_revs.css('p.partial_entry::text').extract()
                review = ''
                if(len(r_revs)>1):
                    for rev in range(len(r_revs)):
                        review += r_revs[rev]+'\n'
                else:
                    review +=r_revs[0]
                r_d['review'] = review
                r_resps = Selector(text=r_r[1], type='html')
                r_resps = r_resps.css('p.partial_entry::text').extract()
                response = ''
                if(len(r_resps)>1):
                    for resp in range(len(r_resps)):
                        response += r_resps[resp]+'\n'
                else:
                    response +=r_resps[0]
                r_d['response'] =response
            else:
                r_revs = Selector(text=r_r[0], type='html')
                r_revs = r_revs.css('p.partial_entry').extract()
                review = ''
                if(len(r_revs)>1):
                    for rev in range(len(r_revs)):
                        review += r_revs[rev]+'\n'
                else:
                    review +=r_revs[0]
                r_d['review'] = review
        except:
            pass
        try:
            room_tip = s.css('div.inlineRoomTip::text')[0].extract()
            r_d['room_tip'] = room_tip
        except:
            pass
        try:
            reco_title = s.css('div.recommend-titleInline::text')[0].extract()
            r_d['reco_title'] = reco_title
        except:
            pass
        try:
            bubbles = s.css('div.ui_bubble_rating::attr(class)').extract()
            reco_desc = s.css('div.recommend-description::text').extract()
            recommendations ={}
            for b, d in zip(bubbles, reco_desc):
                recommendations[d] = ("".join(b.split(" ", 2)[1:2])).encode("utf-8")
            r_d['recommendations'] = recommendations
        except:
            pass
        r_d['location_id'] = 'd'+s.css('span.taLnk::attr(data-locid)')[0].extract()
        sub = s.css('div.quote').extract()
        sub = Selector(text = sub[0], type ='html')
        r_d['review_url'] = sub.css('a::attr(href)')[0].extract()
        #print '----------------'
        #print r_d
        #print '----------------'
        reviews.insert(r_d)

