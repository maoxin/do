import pymongo
import motor
import tornado.web
import tornado.gen

class DBHandler(object):
    def __init__(self, client, db, collection):
        self.cl = client[db][collection]
    
    
    @tornado.gen.engine
    def do_find_one(self, pairs, func, info):
        result = yield motor.Op(
            self.cl.find_one, pairs
        )
        print info
        func(result, info)
        
    @tornado.gen.engine
    def do_find(self, pairs, func, info, direction=pymongo.ASCENDING, axis='_id', limit=10):
        cursor = self.cl.find(pairs)
        cursor.sort( [(axis, direction)] ).limit(limit)
        
        result = yield motor.Op(cursor.to_list)
        
        func(result, info)
        
        