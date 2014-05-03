import motor
import tornado.web
import db_handler
from dateutil import parser

class BaseHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.client = self.settings['client']
    
    @tornado.web.asynchronous
    def user_id_key_identify(self, user_id, user_key, email, func_after_check_id):
        collection = db_handler.DBHandler(self.client, 'users', 'user_id_key')
        query = {
            'user_id': user_id,
            'user_key': user_key,
            'email': email,
        }
        
        print "check begin"
        collection.do_find_one(query, self.check_id_key_timestamp, {})
        
    def check_id_key_timestamp(self, result, info):
        if result:
        
            func_after_check_id = info
        
            old_time = parser.parse(result['time'])
            later_time = datetime.now()
            
            delta = later_time - old_time
            if (delta.days == 0 and delta.seconds < 3600):
                print "check finish"
                func_after_check_id(result, {})
            else:
                message = {"response": "id_key_expired"}
                message_json = json.dumps(message)
                self.set_header("Content_Type", "application/json")
                self.write(message_json)
                print 'check fail'
        
                self.finish()
                return
        
        else:
            message = {"response": "fail"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'check fail'
        
            self.finish()
            return