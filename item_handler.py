import tornado.web
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
        with open('./log/logfile.txt', 'a') as log:
            log.write('post item, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_ITEM_CREATE'))
        up_email = json_file['mission_up_email']
        
        tag = json_file['mission_tag']
        name = json_file['mission_name']
        description = json_file['mission_description']
        
        place_name = json_file['mission_place_name']
        lat = json_file['mission_place'][0]
        lon = json_file['mission_place'][1]
        
        user_place_name = json_file['user_info_str']
        user_lat = json_file['user_info_geo'][0]
        user_lon = json_file['user_info_geo'][1]
        
        begin_time = json_file['mission_begin_time']
        continue_time = json_file['mission_continue']
        
        accept_num = json_file['mission_accept_num']

        
        info = {
            'up_email': up_email,

            'tag': tag,
            'name': name,
            'description': description,
            
            #
            'place_name': place,
            'lat': lat,
            'lon': lon,
            
            #
            'user_place_name': user_place_name,
            'user_lat': user_lat,
            'user_lon': user_lon,
            
            'begin_time': begin_time,
            'continue_time': continue_time,
            
            'accept_num': accept_num,
            
            #
            'attendee': [],
            # the uper himself maybe or not a member. need detail.
            
            'create_time': str(datetime.now()) + '\n',
            
            #
            'picture_path': None,
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
        with open('./log/logfile.txt', 'a') as log:
            log.write('post picture, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_IMAGE'))
        name = json_file['mission_name']
        up_email = json_file['mission_up_email']
        picture = json_file['mission_picture']
        
        pic_decode = base64.b64decode(picture)
        
        pic_path = './photo/' + up_email + '+' + name + '.png'
        with open(pic_path, 'wb') as pc:
            pc.write(pic_decode)
        
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
            
            self.client.resource.items.update(query, {'$push': {'join_email': info['join_email']}, 'accept_num': result['accept_num'] - 1}, callback=self.func_write)
        
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
                    'up_email': i['up_email'],
                    'id': str(i['_id']),

                    'tag': i['tag'],
                    'name': i['name'],
                    'description': i['description'],
                    'accept_num': i['accept_num'],
                    'attendee': i['attendee'],
                    
                    'begin_time': i['begin_time'],
                    'continue_time': i['continue_time'],
                    
                    'place_name': i['place_name'],
                    'lat': i['lat'],
                    'lon': i['lon'],
        
                    'picture_path': i['picture'],
                    'create_time': str(i['create_time']),

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
        print 'get new item'
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
            log.write('get new item, ' + str(datetime.now()) + '\n')
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        document = collection.do_find({}, self.func, None, direction=-1, axis="_id", limit=10)
        
class GetMissionPictureHandler(BaseHandler):
    def post(self):
        print 'get picture'
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
            log.write('get picture, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_PICTURE_GET'))
        name = json_file['picture_path']
        
        picture = open(name, 'r').read()
        self.set_header("Content_Type", "image/png")
        self.write(picture)
        
        return
        
        
        
        
        
        