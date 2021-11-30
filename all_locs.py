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
import numpy as np
locs  = posts.find({ "location_id" :{'$exists':True}},{ 'location_id':1, '_id':0})
uni_loc =[]
for loc in locs:
    if loc['location_id'] not in uni_loc:
	uni_loc.append(loc['location_id'])
np.save('/home/su/scrapy-pro/locs.npy', uni_loc)
print len(uni_loc)
