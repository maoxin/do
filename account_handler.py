import tornado.web
import db_handler
import info_encrypt
import json
from datetime import datetime

class BaseHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.client = self.settings['client']
    
        
class LoginHandler(BaseHandler):
    """Response for request for login"""
    def func(self, result, info):
        if result and info_encrypt.match(result['password'], info['password']):
            message = {"response": "ok"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'connected succeed'
            
            self.finish()
            return
            
            # return a json file with a token(token is a hash string generated with email and log_in time)
            
        else:
            message = {"response": "fail"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'connected fail'
            
            self.finish()
            return
    
    @tornado.web.asynchronous
    def post(self):
        print "connected"
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
                    log.write('connected, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_LOGIN'))
        tag = json_file['tag']
        info = json_file['info']
        password = json_file['password']
        
        collection = db_handler.DBHandler(self.client, 'users', 'contact_with_password')
        query = {tag: info}
        
        collection.do_find_one(query, self.func, {'password': password})
        
        
        
            
class RegisterHandler(BaseHandler):
    """Response for request for regist"""
    def func(self, result, info):
        if not result:        
            message = {"response": "ok"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'register succeed'
            
            self.client.users.contact_with_password.insert(info)
        
        else:
            message = {"response": "fail"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'register fail'
        
        self.finish()
        return
    
    @tornado.web.asynchronous
    def post(self):
        print "register"
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
                    log.write('register, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_SIGN'))
        name = json_file['name']
        email = json_file['email']
        phone = json_file['phone']
        password = json_file['password']
        
        password = info_encrypt.encrypt(password)
        info = {'name': name, 'email': email, 'phone': phone, 'password': password}
        
        query_1 = {'email': email}
        query_2 = {'phone': phone}
        
        query = {
            '$or': [
                query_1,
                query_2
            ]
        }
        
        collection = db_handler.DBHandler(self.client, 'users', 'contact_with_password')
        collection.do_find_one(query, self.func, info)
            
        
        
       