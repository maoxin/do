import json
import tornado.web
import db_handler
import info_encrypt
import uuid
from datetime import datetime
from dateutil import parser
from base_handler import BaseHandler
from log_info import log_info

        
class LoginHandler(BaseHandler):
    """Response for request for login"""
    
    def response_to_client(self, update_result, write_message):
        if update_result:
            print 'log in succeed'
            self.write_info_to_client(write_message)
            
        else:
            print 'connected fail'
            write_message = {"response": "fail"}
            self.write_info_to_client(write_message)
    
    def check_pass_and_refresh_id_key(self, user_info, dic_contain_pass):
        if user_info and info_encrypt.match(user_info['password'], dic_contain_pass['password']):
            print 'pass ok'
            user_id, user_key = str(uuid.uuid4()), str(uuid.uuid4())
            
            write_message = {
                "response": "ok", 
                'email': user_info['email'], 
                'phone_number': user_info['phone_number'], 
                'user_name': user_info['user_name'],
                'user_id': user_id,
                'user_key': user_key,
            }
            
            query_for_refresh = {
                "_id": user_info['_id'],
            }
            
            update_message = {
                '$set':{
                    'user_id': user_id,
                    'user_key': user_key,
                    'id_key_time': str(datetime.now())
                }
            }
            
            collection = db_handler.DBHandler(self.user_info)
            collection.do_update(query_for_refresh, update_message, self.response_to_client, write_message, upsert=True)
            
            
        else:
            write_message = {"response": "fail"}
            self.write_info_to_client(write_message)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('user_connected', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_LOGIN'))
       
        log_in_tag = json_file['log_in_tag']
        # the way log in use, use 'email' or 'phone_number'
        tag_info = json_file['tag_info']
        # the info response to the tag, like 'maoxin.horizon@gmail.com' for 'email'
        password = json_file['password']
        
        collection = db_handler.DBHandler(self.user_info)
        query = {log_in_tag: tag_info}
        dic_contain_pass = {
            'password': password
        }
        
        collection.do_find_one(query, self.check_pass_and_refresh_id_key, dic_contain_pass)
        
        
        
            
class RegisterHandler(BaseHandler):
    """Response for request for regist"""
    def create_account(self, recure_result, account_info):
        if not recure_result:
            user_id, user_key = str(uuid.uuid4()), str(uuid.uuid4())
            account_info['user_id'] = user_id
            account_info['user_key'] = user_key
            account_info['id_key_time'] = str(datetime.now())
            
            write_message = {
                "response": "ok",
                "user_id": user_id,
                "user_key": user_key,
                
            }
            
            self.user_info.insert(account_info)
            self.write_info_to_client(write_message)
        
        else:
            write_message = {"response": "fail"}
            self.write_info_to_client(write_message)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('register', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_REGISTER'))
        
        user_name = json_file['user_name']
        email = json_file['email']
        phone_number = json_file['phone_number']
        password = info_encrypt.encrypt(json_file['password'])
        
        account_info = {
            'user_name': user_name, 
            'email': email, 
            'phone_number': phone_number, 
            'password': password,
            
            'user_picture_path': None,
            'user_description': None,
        }
        
        query_email = {'email': email}
        query_phone_number = {'phone_number': phone_number}
        
        query_for_check_recur = {
            '$or': [
                query_email,
                query_phone_number,
            ]
        }
        
        collection = db_handler.DBHandler(self.user_info)
        collection.do_find_one(query_for_check_recur, self.create_account, account_info)
            
#class ChangeProfileHandler(BaseHandler):
#    def func_response(self, result, error):
#        if not error:
#            message = {
#                "change_password": "ok",
#                "change_name":     "ok",
#                "change_picture":  "ok",
#                "change_description": "ok",
#            }
#            
#            message_json = json.dumps(message)
#            self.set_header("Content_Type", "application/json")
#            self.write(message_json)
#        
#            self.finish()
#            return
#            
#        else:
#            message = {"response": "fail"}
#            message_json = json.dumps(message)
#            self.set_header("Content_Type", "application/json")
#            self.write(message_json)
#        
#            self.finish()
#            return
#    
#    def func_after_check_name(self, result, info):
#        if not result:
#            self.collection.update({'email': self.email}, {'$set': info}, call_back = self.func_response)
#        
#        else:
#            message = {
#                "change_name": "name been used",
#                "change_password": "ok",
#                "change_picture":  "ok",
#                "change_description": "ok",
#            }
#            message_json = json.dumps(message)
#            self.set_header("Content_Type", "application/json")
#            self.write(message_json)
#        
#            self.finish()
#            return
#    
#    def func(self, result, info):
#        
#        if result:
#            if info.has_key('picture'):
#                pic_decode = base64.b64decode(picture)
#                pic_path = './user_photos/' + info['email'] + '.png'
#                with open(pic_path, 'wb') as pc:
#                    pc.write(pic_decode)
#                
#                info['picture_path'] = pic_path
#                info.pop['picture']
#            
#            if info.has_key('name'):
#                query = {'name': info['name']}
#                self.collection.do_find_one(query, self.func_after_check_name, info)
#            
#            if info.has_key('password'):
#                if info_encrypt.match(result['password'], self.password):
#                    info['password'] = info_encrypt.encrypt(info['password']) 
#                    self.collection.update({'email': self.email}, {'$set': info}, call_back = self.func_response)
#            
#                else:
#                    message = {
#                        "change_password": "password wrong",
#                        "change_name":     "ok",
#                        "change_picture":  "ok",
#                        "change_description": "ok",
#                    }
#                
#                    message_json = json.dumps(message)
#                    self.set_header("Content_Type", "application/json")
#                    self.write(message_json)
#            
#                    self.finish()
#                    return
#                    
#        
#        else:
#            message = {"response": "fail"}
#            message_json = json.dumps(message)
#            self.set_header("Content_Type", "application/json")
#            self.write(message_json)
#        
#            self.finish()
#            return       
#    
#    @tornado.web.asynchronous
#    def post(self):
#        log_info('change_profile', self.log_operation)
#        
#        self.allow_item = ['name', 'password', 'picture', 'description']
#        json_file = json.loads(self.get_argument('JSON_CHANGE_PROFILE'))
#        
#        self.email = json_file['email']
#        self.user_id = json_file['user_id']
#        self.user_key = json_file['user_key']
#        
#        changes = json_file['changes']
#        if 'password' in changes:
#            self.password = json_file['password']
#        
#        self.info = {}
#        self.has_item = []
#        for item in self.allow_item:
#            if item in changes:
#                self.has_item.append(item)
#                self.info[item] = json_file['change_' + item]
#        
#        
#        self.user_id_key_identify('email', self.user_id, self.user_key, self.email, self.func)  
        
class LookOwnProfileHandler(BaseHandler):
    def send_profile_to_client(self, user_info, nothing_to_read):
        if user_info:
            print 'look own success'
            
            write_message = {
                "response": "ok",
                'email': user_info['email'], 
                'phone_number': user_info['phone_number'],
                'user_name': user_info['user_name'],
                'user_description': user_info['user_description'],
                'user_pic_path': user_info['user_pic_path'],
            }
            
            self.write_info_to_client(write_message)
    
        else:
            print 'connected fail'
            
            write_message = {"response": "fail"}
            self.write_info_to_client(write_message)
                
    
    @tornado.web.asynchronous
    def post(self):
        log_info('look_own_profile', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_LOOK_OWN_PROFILE'))
        
        email = json_file['email']
        user_id = json_file['user_id']
        user_key = json_file['user_key']
        
        
        self.user_id_key_identify(user_id, user_key, email, self.send_profile_to_client)
        
        
class LookOtherProfile(BaseHandler):
    def send_profile_to_client(self, user_info, nothing_to_read):
        if user_info:    
            print 'look other succeed'
            
            write_message = {
                "response": "ok",
                'user_name': user_info['user_info'],
                'user_description': user_info['user_description'],
                'user_pic_path': user_info['user_pic_path'],
            }
            
            self.write_info_to_client(write_message)

        else:
            write_message = {"response": "fail"}
            self.write_info_to_client(write_message)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('look_other_profile', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_LOOK_PROFILE'))
        user_name = json_file['user_name']
        
        collection = db_handler.DBHandler(self.user_info)
        query_for_find_some_one = {'user_name': user_name}
        info_to_send_profile_function = {}
        
        collection.do_find_one(query_for_find_some_one, self.send_profile_to_client, info_to_send_profile_function)