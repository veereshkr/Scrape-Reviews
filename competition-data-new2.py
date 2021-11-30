from pymongo import MongoClient
import json
import datetime
import uuid
import datetime
#import uuid
client = MongoClient('')
db = client.competition
posts = db.competition_data
import urllib2
from bs4 import BeautifulSoup
import re
import numpy as np
import random
links = np.load('links_new.txt.npy')
print len(links)
url=links[random.randint(1,100000000)%len(links)]
#url = links[96]
try:
    found = "-".join(url.split("-", 2)[1:2])
    #found = re.search('https://www.tripadvisor.com/Hotels-(.+?)-Palo_Alto_California-Hotels.html', text).group(1)
except AttributeError:
    # AAA, ZZZ not found in the original string
    found = '' # apply your error handling
if("-".join(url.split("-", 3)[2:3]) == "".join(url.split("-", -1)[-1])):
    print found
    page_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(found)+ str(datetime.datetime.now().date())).hex)[:16]
else:
    print found+'-'+"-".join(url.split("-", 3)[2:3])
    page_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(found)+str("-".join(url.split("-", 3)[2:3]))+str(datetime.datetime.now().date())).hex)[:16]
c=0

while(posts.find_one({'page_id':page_id})):
    url=links[random.randint(1,100000000)%len(links)]
    print url
    try:
        found = "-".join(url.split("-", 2)[1:2])
        #found = re.search('https://www.tripadvisor.com/Hotels-(.+?)-Palo_Alto_California-Hotels.html', text).group(1)
    except AttributeError:
        # AAA, ZZZ not found in the original string
        found = '' # apply your error handling
    if("-".join(url.split("-", 3)[2:3]) == "".join(url.split("-", -1)[-1])):
        print (found, 'found new page')
        page_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(found)+ str(datetime.datetime.now().date())).hex)[:16]
    else:
        print (found+'-'+"-".join(url.split("-", 3)[2:3]), 'found new page')
        page_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(found)+str("-".join(url.split("-", 3)[2:3])) + str(datetime.datetime.now().date())).hex)[:16]
    c=c+1
    if(c >len(links)):
        break
else:
    if (c<len(links)):
        data = urllib2.urlopen(url).read()
        soup = BeautifulSoup(data, "html.parser")
        div_arr =[]
        complete_info =[]
        count =0
        for i in soup.find_all('span',class_='count'):
            count += int(i.text.strip().replace("(",'').replace(")",''))
        print ('hotels count', count)
        append_count =0
        if count >30:
            new_links =[]
            for i in range(1,(count/30)+1):
                page = 'oa'+str(30*i)
                new_link = "-".join(url.split("-", 2)[0:2])+'-'+page+'-'+ "".join(url.split("-", -1)[-1])
                if(new_link not in links):
                    links = np.append(links,new_link)
                    append_count+=1
                    print new_link
        if append_count >0:
             np.save('links_new.txt.npy',links)
             print 'file updated'

        for i in soup.select('div.prw_rup.prw_meta_hsx_responsive_listing'):
            div_arr.append(i)
        #print len(div_arr)
        for tag in div_arr:
            comp_info ={}
            location_id =''
            comp_info['area_code']= str(found).encode("utf-8")
            for i in tag.find_all('a', href=True, class_='property_title'):
                #print i.text.strip()
                #print i['href']
                comp_info['href'] = i['href'].encode("utf-8")
                location_id = comp_info['location_id'] = ("-".join(i['href'].split("-", 3)[2:3])).encode("utf-8")
                _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, location_id+ str(datetime.datetime.now())).hex)[:16]
                comp_info['_id'] = _id.encode("utf-8")
                comp_info['page_id'] = page_id.encode("utf-8")
                comp_info['property_title']=(i.text.strip()).encode("utf-8")
                comp_info['created_at']=datetime.datetime.now().isoformat()
            for i in tag.select('div.price.autoResize'):
                #print i.text.strip()
                comp_info['price']=i.text.strip().encode("utf-8")
            for j in tag.find_all('span', alt=True ,class_="ui_bubble_rating"):
                x =re.search('(.+?) of 5 bubbles',str(j['alt'])).group(1)
                #print x
                j['alt'] = round(float(x),1)
                comp_info['rating']=j['alt']
                #print j['alt']
            for i in  tag.find_all('a', class_='review_count'):
                #print i.text.strip()
                comp_info['review_count']= int((i.text.strip().split(" ", 1)[0]).replace(',',''))
            #print comp_info
            if (location_id != ''):
                #print comp_info
                complete_info.append(comp_info)
        print '---------'
        #print complete_info

        try:
            print url
            print str(datetime.datetime.now())
            #posts.insert_many(complete_info)
            #posts.update({ '_id':_id}, {'$set':{'_id':_id ,'competitors':complete_info, 'area_code':found, 'updated_at':datetime.datetime.now().isoformat() } }, upsert=True)
        except:
            print 'failed to update db'

