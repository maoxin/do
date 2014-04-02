import tornado.web
import db_handler
from bson.objectid import ObjectId
import info_encrypt
import json
from datetime import datetime
import base64
from java_list import get_str_list
import numpy as np

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
        up_name = json_file['mission_up_name']
        
        tag = json_file['mission_tag']
        name = json_file['mission_name']
        description = json_file['mission_description']
        
        place_name = json_file['mission_place_name']
        lat = json_file['mission_place_latitude']
        lon = json_file['mission_place_longitude']
        
        user_place_name = json_file['user_info_str']
        user_lat = json_file['user_info_geo_latitude']
        user_lon = json_file['user_info_geo_longitude']
        
        begin_time = json_file['mission_begin_time']
        continue_time = json_file['mission_continue']
        
        accept_num = json_file['mission_accept_num']

        
        info = {
            'up_email': up_email,
            'up_name': up_name,

            'tag': tag,
            'name': name,
            'description': description,
            
            #
            'place_name': place_name,
            'lat': lat,
            'lon': lon,
            
            #
            'user_place_name': user_place_name,
            'user_lat': user_lat,
            'user_lon': user_lon,
            
            'begin_time': begin_time,
            'continue_time': continue_time,
            
            'accept_num': int(accept_num),
            
            #
            'attendee': [],
            # the uper himself maybe or not a member. need detail.
            
            'create_time': str(datetime.now()),
            
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
        
        self.client.resource.items.update(query, {"$set": {'picture_path': pic_path} }, callback=self.func)
        
        
class GetNewItemHandler(BaseHandler):
    def func(self, result, info):
        if result:
            latest_id = info
            
            items = filter(lambda x: x['_id'] > latest_id, result)
            items_info = []
            for item in items:
                info = {
                    'id': str(item['_id']),
                    'up_email': item['up_email'],
                    'up_name': item['up_name'],
        
                    'tag': item['tag'],     
                    'name': item['name'],
                    'description': item['description'],

                    'place_name': item['place_name'],
                    'lat': item['lat'],
                    'lon': item['lon'],

                    'begin_time': item['begin_time'],
                    'continue_time': item['continue_time'],
                    'accept_num': item['accept_num'],

                    'attendee': item['attendee'],

                    'picture_path': item['picture_path'],
                }
                
                items_info.append(info)
            
            message_json = json.dumps({'response': items_info})
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
        print 'get_new_item'
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
            log.write('get_new_item, ' + str(datetime.now()) + '\n')
            
        json_file = json.loads(self.get_argument('JSON_NEW_ITEM'))

        # ids = get_str_list(json_file['ids'][0])
        ids = list(np.unique(json_file['ids']))
        print ids
        ids = [ObjectId(x) for x in ids]
        
        if not ids or not ids[0]:
            info = 0
        else:
            info = max(ids)
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        collection.do_find({}, self.func, info, direction=-1, axis="_id", limit=15)
        
        

class GetMissionPictureHandler(BaseHandler):
    def post(self):
        print 'get picture'
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
            log.write('get picture, ' + str(datetime.now()) + '\n')
        
        json_file = json.loads(self.get_argument('JSON_PICTURE_GET'))
        name = json_file['picture_path']
        print name

        picture = open(name, 'r').read()
        self.set_header("Content-Type", "image/png; charset=utf-8")
        self.write(picture)
        
        return
        

class RecieveItemHandler(BaseHandler):
    
    def func_write(self, result, info):
        if result:
            item_info = {
                'response': 'ok',
                'attendee': result['attendee'],
                'id': str(result['_id'])
            }
        
            message_json = json.dumps(item_info)
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
    
    def func_after_update(self, result, error):
        if not error:
            self.collection.do_find_one(self.query, self.func_write, {})
            
        else:
            print error
            message = {"response": error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
    
    def func(self, result, info):
        if result and (len(result['attendee']) < int(result['accept_num'])):
            print len(result['attendee']), result['accept_num']
            self.info = result
            
            query = {
                '_id': info['_id']
            }
            
            self.client.resource.items.update(query, {'$push': {'attendee': info['join_email']}}, callback=self.func_after_update)
        
        else:
            if not result:
                message = {"response": "item not found"}
                message_json = json.dumps(message)
                self.set_header("Content_Type", "application/json")
                self.write(message_json)
            
                self.finish()
                return
           
            elif len(result['attendee']) >= int(result['accept_num']):
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
        print 'recieve_item'
        print datetime.now()
        with open('./log/logfile.txt', 'a') as log:
            log.write('recieve_item, ' + str(datetime.now()) + '\n')
            
        json_file = json.loads(self.get_argument('JSON_RECEIVE_ITEM'))
        item_id = json_file['mission_id']
        join_email = json_file['join_email']

        self.query = {
         '_id': ObjectId(item_id),
        }

        info = {'_id': self.query['_id'], 'join_email': join_email}

        self.collection = db_handler.DBHandler(self.client, 'resource', 'items')

        document = self.collection.do_find_one(self.query, self.func, info)     

    
    
    
