import pymongo
import motor
import tornado.web
import tornado.gen

class DBHandler(object):
    def __init__(self, collection):
        self.cl = collection
    
    
    @tornado.gen.coroutine
    def do_find_one(self, query, func_after_find, info_to_following_function):
        result = yield self.cl.find_one(query)
        func_after_find(result, info_to_following_function)
        
    @tornado.gen.coroutine
    def do_find(self, query, func_after_find, info_to_following_function, direction=pymongo.ASCENDING, axis='_id', limit=10):
        cursor = self.cl.find(query)
        cursor.sort( [(axis, direction)] ).limit(limit)
        
        result = yield cursor.to_list(length=limit)
        
        func_after_find(result, info_to_following_function)
        
    @tornado.gen.coroutine
    def do_update(self, query, change, func_after_update, info_to_following_function, upsert=False):
        print 'update begin'
        result = yield self.cl.update(query, change, upsert=upsert)
        
        print 'update finish'
        func_after_update(result, info_to_following_function)
        
    
# New

       
        
