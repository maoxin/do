import tornado.web
import tornado.ioloop
import db_handler
from bson.objectid import ObjectId
import info_encrypt
import json
from datetime import datetime
import base64

class BaseHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.client = self.settings['client']
        
class PostItemHandler(BaseHandler):
    def func(self, result, error):
        if not error:
            item_id = str(result)
            message = {"response": item_id}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            print item_id
            self.finish()
            return
            
        else:
            print error
            message = {"response": error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
    
    @tornado.web.asynchronous
    def post(self):
        print "post item"
        print datetime.now()
        json_file = json.loads(self.get_argument('JSON_ITEM_CREATE'))
        name = json_file['mission_name']
        description = json_file['mission_description']
        # place = json_file['mission_place']
        begin_time = json_file['mission_begin_time']
        continue_time = json_file['mission_continue']
        accept_num = json_file['mission_accept_num']
        up_email = json_file['mission_up_email']
        tag = json_file['mission_tag']
        
        info = {
            'name': name,
            'description': description,
            # 'place': place,
            'begin_time': begin_time,
            'continue_time': continue_time,
            'accept_num': accept_num,
            'up_email': up_email,
            'attendee': [up_email],
            'create_time': datetime.now(),
            'picture': None,
            'tag': tag
        }

        self.client.resource.items.insert(info, callback=self.func)
        
 
class PostItemPicure(BaseHandler):
    def func(self, result, error):
        if not error:

            message = {"response": 'ok'}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
            
        else:
            message = {"response": error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
   
    @tornado.web.asynchronous
    def post(self):
        print 'post picture'
        print datetime.now()
        json_file = json.loads(self.get_argument('JSON_IMAGE'))
        name = json_file['mission_name']
        up_email = json_file['mission_up_email']
        picture = json_file['mission_picture']
        pic_decode = base64.b64decode(picture)
        
        pic_path = './photo/' + up_email + '+' + name + '.png'
        pc = open(pic_path, 'wb')
        pc.write(pic_decode)
        pc.close()
        
        query = {
            'name': name,
            'up_email': up_email
        }
        
        print query
        
        self.client.resource.items.update(query, {"$set": {'picture': pic_path} }, callback=self.func)


class JoinItemHandler(BaseHandler):
    def func_write(self, result, error):
        if not error:
            message = {"response": 'ok'}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
            
        else:
            print error
            message = {"response": error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
    
    def func(self, result, info):
        if result and len(result['attendee']) < result['accept_num']:
            query = {
                'item_id': info['item_id']
            }
            
            self.client.resource.items.update(query, {'$push': {'join_email': info['join_email']}, 'accept_num': result['accept_num'] + 1}, callback=self.func_write)
        
        else:
            if not result:
                message = {"response": "item not found"}
                message_json = json.dumps(message)
                self.set_header("Content_Type", "application/json")
                self.write(message_json)
            
                self.finish()
                return
           
            elif len(result['attendee']) >= result['accept_num']:
                message = {"response": "attendee full"}
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
        json_file = json.loads(self.get_argument('JSON_ITEM_JOIN'))
        item_id = json_file['item_id']
        join_email = json_file['join_email']
        
        query = {
            'item_id': ObjectId(item_id),
        }
        
        info = {
            'item_id': ObjectId(item_id),
            'join_email': join_email
        }
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        
        document = collection.do_find_one(query, func, info)
        
        
class GetNewItemHandler(BaseHandler):
    def func(self, result, info):
        if result:
            message = []
            
            for i in result:
                ms = {
                    'id': str(i['_id']),
                    'name': i['name'],
                    'description': i['description'],
                    'begin_time': i['begin_time'],
                    'continue_time': i['continue_time'],
                    'picture_path': i['picture'],
                    'accept_num': i['accept_num'],
                    'up_email': i['up_email'],
                    'attendee': i['attendee'],
                    'create_time': str(i['create_time']),
                    'tag': i['tag']
                }
                
                message.append(ms) 
                
            message_json = json.dumps({'response': message})
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
    def get(self):
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        document = collection.do_find({}, self.func, None, direction=-1, axis="_id", limit=10)
        
class GetMissionPictureHandler(BaseHandler):
    def post(self):
        json_file = json.loads(self.get_argument('JSON_PICTURE_GET'))
        name = json_file['picture_path']
        
        picture = open(name, 'r').read()
        self.set_header("Content_Type", "image/png")
        self.write(picture)
        
        return
        
        
        
        
        
        