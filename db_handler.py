import pymongo
import motor
import tornado.web
import tornado.gen

class DBHandler(object):
    def __init__(self, client, db, collection):
        self.cl = client[db][collection]
    
    
    @tornado.gen.coroutine
    def do_find_one(self, pairs, func, info):
        result = yield self.cl.find_one(pairs)
        func(result, info)
        
    @tornado.gen.coroutine
    def do_find(self, pairs, func, info, direction=pymongo.ASCENDING, axis='_id', limit=10):
        cursor = self.cl.find(pairs)
        cursor.sort( [(axis, direction)] ).limit(limit)
        
        result = yield cursor.to_list(length=limit)
        
        func(result, info)
        
    @tornado.gen.coroutine
    def do_update(self, query, change, func, info, upsert=False):
        print 'update begin'
        result = yield cl.update(query, change, upsert=upsert)
        
        print 'update finish'
        func(result, info)
        
    
        
        
