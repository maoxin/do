import json
import tornado.web
import db_handler
import info_encrypt
from datetime import datetime
from base_handler import BaseHandler
from log_info import log_info
        
class LoginHandler(BaseHandler):
    """Response for request for login"""
    def func(self, result, info):
        if result and info_encrypt.match(result['password'], info['password']):
            message = {"response": "ok", 'email': result['email'], 'phone': result['phone'], 'name': result['name']}
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
        log_info('user_connected', self.client)
        
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
        log_info('register', self.client)
        
        json_file = json.loads(self.get_argument('JSON_SIGN'))
        name = json_file['name']
        email = json_file['email']
        phone = json_file['phone']
        password = json_file['password']
        
        password = info_encrypt.encrypt(password)
        info = {
            'name': name, 
            'email': email, 
            'phone': phone, 
            'password': password,
            'picture_path': None,
            'create_time': str(datetime.now()),
        }
        
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
            
class ChangeProfileHandler(BaseHandler):
    def func_response(self, result, error):
        if not error:
            message = {
                "change_password": "ok",
                "change_name":     "ok",
                "change_picture":  "ok",
                "change_describe": "ok",
            }
            
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
        
            self.finish()
            return
            
        else:
            message = {"response": "fail"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
        
            self.finish()
            return
    
    def func_after_check_name(self, result, info):
        if not result:
            self.collection.update({'email': self.email}, {'$set': info}, call_back = self.func_response)
        
        else:
            message = {
                "change_name": "name been used",
                "change_password": "ok",
                "change_picture":  "ok",
                "change_describe": "ok",
            }
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
        
            self.finish()
            return
    
    def func(self, result, info):
        
        if result and info_encrypt.match(result['password'], self.password):
            if info.has_key('picture'):
                pic_decode = base64.b64decode(picture)
                pic_path = './user_photos/' + info['email'] + '.png'
                with open(pic_path, 'wb') as pc:
                    pc.write(pic_decode)
                
                info['picture_path'] = pic_path
                info.pop['picture']
            
            if info.has_key('name'):
                query = {'name': info['name']}
                self.collection.do_find_one(query, self.func_after_check_name, info)
            
            if info.has_key('password'):
                info['password'] = info_encrypt.encrypt(info['password'])
                
                self.collection.update({'email': self.email}, {'$set': info}, call_back = self.func_response)
        
        else:
            if info_encrypt.match(result['password'], self.password):
                message = {
                    "change_password": "password wrong",
                    "change_name":     "ok",
                    "change_picture":  "ok",
                    "change_describe": "ok",
                }
                
                message_json = json.dumps(message)
                self.set_header("Content_Type", "application/json")
                self.write(message_json)
            
                self.finish()
                return
            
            else:
                message = {"response": "fail"}
                message_json = json.dumps(message)
                self.set_header("Content_Type", "application/json")
                self.write(message_json)
            
                self.finish()
                return       
    
    @tornado.web.asynchronous
    def post(self):
        log_info('change_profile', self.client)
        
        self.allow_item = ['name', 'password', 'picture', 'describe']
        json_file = json.loads(self.get_argument('JSON_CHANGE_PROFILE'))
        
        self.email = json_file['tag']
        self.password = json_file['password']
        changes = json_file['changes']
        
        info = {}
        self.has_item = []
        for item in self.allow_item:
            if item in changes:
                self.has_item.append(item)
                info[item] = json_file['change_' + item]
        
        
        self.collection = db_handler.DBHandler(self.client, 'users', 'contact_with_password')
        query = {'email': self.email}
        
        self.collection.do_find_one(query, self.func, info)
        
       
class GetProfilePictureHandler(BaseHandler):
    def post(self):
        log_info('get_profile_picture', self.client)
        
        json_file = json.loads(self.get_argument('JSON_PROFILE_PICTURE_GET'))
        name = json_file['picture_path']
        print name

        picture = open(name, 'r').read()
        self.set_header("Content-Type", "image/png; charset=utf-8")
        self.write(picture)
        
        return
        
class LookOwnProfileHandler(BaseHandler):
    def func(self, result, info):
        if result and info_encrypt.match(result['password'], info['password']):
            message = {
                "response": "ok",
                'email': result['email'], 
                'phone': result['phone'],
                'name': result['name'],
                'describe': result['describe'],
                'picture_path': result['picture_path'],
            }
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'look own success'
            
            self.finish()
            return
    
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
        log_info('look_own_profile', self.client)
        
        json_file = json.loads(self.get_argument('JSON_LOOK_MY_PROFILE'))
        tag = josn_file['tag']
        info = json_file['info']
        password = json_file['password']
        
        collection = db_handler.DBHandler(self.client, 'users', 'contact_with_password')
        query = {tag: info}
        
        collection.do_find_one(query, self.func, {'password': password})
        
class LookOtherProfile(BaseHandler):
    def func(self, result, info):
        if result:    
            message = {
                "response": "ok",
                'name': result['name'],
                'describe': result['describe'],
                'picture_path': result['picture_path'],
            }
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            print 'look own success'
        
            self.finish()
            return

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
        log_info('look_other_profile', self.client)
        
        json_file = json.loads(self.get_argument('JSON_LOOK_PROFILE'))
        name = json_file['name']
        
        collection = db_handler.DBHandler(self.client, 'users', 'contact_with_password')
        query = {'name': name}
        
        collection.do_find_one(query, self.func, {})