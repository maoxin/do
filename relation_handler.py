import tornado.web
import db_handler
import json
from datetime import datetime
from base_handler import BaseHandler
from log_info import log_info
        
class FollowHandler(BaseHandler):
    def func(self, result, info):
        if not result:
            message = {"response": "ok"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'follow succeed'
            
            self.client.users.relationship.insert(info)
            
            self.finish()
            return
        
        else:
            message = {"response": "has followed"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'follow fail'
    
    @tornado.web.asynchronous
    def post(self):
        log_info('follow', self.client)
        
        json_file = json.loads(self.get_argument('JSON_FOLLOW'))
        follower_email = json_file['follower_email']
        aim_email = json_file['aim_email']
        
        query = {
            'follower_email': follower_email,
            'aim_email': aim_email,
        }
        
        collection = db_handler.DBHandler(self.client, 'users', 'relationship')
        collection.do_find_one(query, self.func, query)