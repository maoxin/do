import motor
import tornado.web
import db_handler

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
        
        collection.do_find_one(query, func_after_check_id, {})