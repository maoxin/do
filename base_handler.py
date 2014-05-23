import motor
import tornado.web
import db_handler
import info_encrypt
from dateutil import parser
from datetime import datetime

class BaseHandler(tornado.web.RequestHandler):
    
# change_begin
    def prepare(self):
        self.client = self.settings['client']
        self.user_info = self.client.users.user_info_with_contact
        
        self.item_info = self.client.resource.items
        self.deleted_item_info = self.client.resource.deleted_items
        self.archived_item_info = self.client.resource.archived_items
        
        self.talk_info = self.cilent.resource.talks
        
        self.log_operation = self.client.server_log.operation_log
    
    def write_info_to_client(self, dic_message):
        message_json = json.dumps(dic_message)
        self.set_header("Content_Type", "application/json")
        self.write(message_json)
        
        print 'write_succeed'
        self.finish()
        return
        
    def send_picture_to_client(self, pic_path):
        picture = open(pic_path, 'r').read()
        self.set_header("Content-Type", "image/png; charset=utf-8")
        self.write(picture)
        
        self.finish()
        return
    
    def user_id_key_identify(self, user_id, user_key, email, func_after_check_id):
        collection = db_handler.DBHandler(self.user_info)
        query = {
            'user_id': user_id,
            'email': email,
        }
        
        info_to_check_id_key_timestamp = {
            'user_key': user_key,
            'func_after_check_id': func_after_check_id,
        }
        
        print query
        print "check begin"
        collection.do_find_one(query, self.check_id_key_timestamp, info_to_check_id_key_timestamp)
        
    def check_id_key_timestamp(self, result, user_key_and_following_function):
        if result:
            print "find user_id"
        
            user_key = info_to_check_id_key_timestamp['user_key']
            func_after_check_id = info_to_check_id_key_timestamp['func_after_check_id']
        
            # check the key
            is_key_right = info_encrypt.match(result['user_key'], user_key)
            
            if is_key_right:
                old_time = parser.parse(result['id_key_time'])
                later_time = datetime.now()
            
                print old_time, later_time
                time_delta = later_time - old_time
                print time_delta
                
                if (time_delta.days == 0 and time_delta.seconds < 3600):
                    fresh_time_query = {
                        "_id": result['_id']
                    }
                    fresh_change = {
                        '$set': {
                            'id_key_time': str(datetime.now())
                        }
                    }
                    self.user_info.update(fresh_time_query, fresh_change)
                    
                    print "check finish"
                    func_after_check_id(result, info_to_following_function = {})
                    # result is the user_info
                    
                else:
                    message = {"response": "id_key_expired"}
                    self.write_info_to_client(message)
            
            else:
                message = {"response": "id_key_not_matched"}
                self.write_info_to_client(message)
        
        else:
            print 'not_find'
            message = {"response": "fail"}
            self.write_info_to_client(message)
            
class GetPictureHandler(BaseHandler):
    def post(self):
        log_info('get_profile_picture', self.client)
        
        json_file = json.loads(self.get_argument('JSON_PROFILE_PICTURE_GET'))
        pic_path = json_file['pic_path']
        print pic_path
        
        self.send_picture_to_client(pic_path)
# change_end