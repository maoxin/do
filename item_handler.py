import json
import base64
import numpy as np
import tornado.web
import db_handler
import info_encrypt
from web_socket_handler import TalkWebSocket
from datetime import datetime
from bson.objectid import ObjectId
from base_handler import BaseHandler
from log_info import log_info
        
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
        log_info('post_item', self.client)
        
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
        log_info('post_picture', self.client)
        
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
    def func_delete_items(self, result, info):
        if result:
            delete_ids = [str(x['delete_time_id']) for x in result]
            self.items_info['delete'] = delete_ids
        
        else:
            pass
         
        message_json = json.dumps({'response': self.items_info})
        self.set_header("Content_Type", "application/json")
        self.write(message_json)

        self.finish()
        return
        
    
    
    def func_new_item(self, result, info):
        if result:
            latest_id = info
            
            items = filter(lambda x: x['_id'] > latest_id, result)
            self.items_info = []
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
                
                self.items_info.append(info)
            
            query = {
                '_id': {
                    '$in': self.ids
                }
            }
            
            info = {}    
            
            collection = db_handler.DBHandler(self.client, 'resource', 'delete_items')
            collection.do_find(query, self.func_delete_items, info, direction=-1, axis="_id", limit=15)
            
        else:
            message = {"response": "fail"}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
        
            self.finish()
            return
    
    
    @tornado.web.asynchronous
    def post(self):
        log_info('get_new_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_NEW_ITEM'))

        ids = list(np.unique(json_file['ids']))
        print ids
        ids = [ObjectId(x) for x in ids]
        self.ids = ids
        
        if not ids or not ids[0]:
            info = 0
        else:
            info = max(ids)
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        collection.do_find({}, self.func_new_item, info, direction=-1, axis="_id", limit=15)
        
        

class GetMissionPictureHandler(BaseHandler):
    def post(self):
        log_info('get_picture', self.client)
        
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
        log_info('recieve_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_RECEIVE_ITEM'))
        item_id = json_file['mission_id']
        join_email = json_file['join_email']

        self.query = {
         '_id': ObjectId(item_id),
        }

        info = {'_id': self.query['_id'], 'join_email': join_email}

        self.collection = db_handler.DBHandler(self.client, 'resource', 'items')

        document = self.collection.do_find_one(self.query, self.func, info)     

    
    
class DeleteItemHandler(BaseHandler):
    def func_write(self, result, error):
        if not error:

            message = {"response": 'ok', 'id': str(self.query['_id'])}
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
            
        
    def func_delete(self, result, error):
        if not error:
            self.client.resource.items.remove(self.query, callback=self.func_write)
        else:
            message = {'response': error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
    
    def func_insert(self, result, info):
        if result:
            result['delete_time_id'] = result['_id']
            result.pop('_id')
            
            self.client.resource.delete_items.insert(result, callback=self.func_delete)
        
        else:
            message = {'response': 'fail'}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
        
    
    @tornado.web.asynchronous
    def post(self):
        log_info('delete_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_DELETE_ITEM'))
        item_id = json_file['mission_id']
        up_email = json_file['mission_up_email']
        
        self.query = {
            '_id': ObjectId(item_id),
            'up_email': up_email,
        }
        
        info = {}
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        document = collection.do_find_one(self.query, self.func_insert, info)


class ArchiveItemHandler(BaseHandler):
    def func_write(self, result, error):
        if not error:

            message = {"response": 'ok', 'id': str(self.query['_id'])}
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
            
        
    def func_delete(self, result, error):
        if not error:
            self.client.resource.items.remove(self.query, callback=self.func_write)
        else:
            message = {'response': error}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
    
    def func_insert(self, result, info):
        if result:
            result['archive_time_id'] = result['_id']
            result.pop('_id')
            
            self.client.resource.archive_items.insert(result, callback=self.func_delete)
        
        else:
            message = {'response': 'fail'}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            self.finish()
            return
        
    
    @tornado.web.asynchronous
    def post(self):
        log_info('archive_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_ARCHIVE_ITEM'))
        item_id = json_file['mission_id']
        up_email = json_file['mission_up_email']
        
        self.query = {
            '_id': ObjectId(item_id),
            'up_email': up_email,
        }
        
        info = {}
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        document = collection.do_find_one(self.query, self.func_insert, info)

class ItemTalkHandler(BaseHandler):
    def after_insert_func(self, result, error):
        if not error:
            item_id = str(self.info['item_id'])
            name = self.info['talking_name']
            content = self.info['talking_content']

            message = {"response": 'ok'}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)
            
            try:
                talk_man_group = TalkWebSocket.attendees[item_id]
                talk_man_pool = filter(lambda man: man.name == name, talk_man_group)
                if talk_man_pool:
                    talk_man = talk_man_pool[0]
                    talk_man.write_content_to_team_mate(content)
            except KeyError:
                raise KeyError
            
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
        log_info('talk_in_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_ITEM_TALK'))
        item_id = json_file['mission_id']
        talking_email = json_file['talking_email']
        talking_name = json_file['talking_name']
        talking_content = json_file['talking_content']
        
        self.info = {
            'item_id': ObjectId(item_id),
            'talking_email': talking_email,
            'talking_name':  talking_name,
            'talking_content': talking_content
        }
        
        self.client.resource.talks.insert(self.info, callback=self.after_insert_func)
        
class ItemGetTalkHandler(BaseHandler):
    def func_after_find_talks(self, result, info):
        if result:
            latest_id = info
        
            talks = filter(lambda x: x['_id'] > latest_id, result)
            self.items_info = []
            
            for talk in talks:
                self.items_info.append(
                    {
                        'talking_id': str(talk['_id']),
                        'mission_id': str(talk['item_id']),
                        'talking_email': talk['talking_email'],
                        'talking_name':  talk['talking_name'],
                        'talking_content': talk['talking_content'],
                    }
                )
            
            message_json = json.dumps({'response': self.items_info})
            self.set_header("Content_Type", "application/json")
            self.write(message_json)

            self.finish()
            return
        
        else:
            message_json = json.dumps({'response': 'fail'})    
            self.set_header("Content_Type", "application/json")
            self.write(message_json)

            self.finish()
            return
            
    
    def func_after_find_item(self, result, info):
        if result:
            query = self.query_talk
            info = info
            
            collection = db_handler.DBHandler(self.client, 'resource', 'talks')
            collection.do_find(query, self.func_after_find_talks, info, direction=-1, axis="_id", limit=10)
    
    
    @tornado.web.asynchronous
    def post(self):
        log_info('get_talks_in_item', self.client)
            
        json_file = json.loads(self.get_argument('JSON_ITEM_GET_TALK'))
        item_id = json_file['mission_id']
        join_email = json_file['join_email']
        talk_ids = list(np.unique(json_file['talk_ids']))
        
        talk_ids = [ObjectId(x) for x in talk_ids]
        self.talk_ids = talk_ids
        
        if not talk_ids or not talk_ids[0]:
            info = 0
        else:
            info = max(talk_ids)
            
        self.query_item = {
            '_id': ObjectId(item_id),
            'attendee': {
                '$in': [join_email],
            }
        }
        
        self.query_talk = {
            'item_id': ObjectId(item_id),
        }
        
        
        collection = db_handler.DBHandler(self.client, 'resource', 'items')
        collection.do_find_one(self.query_item, self.func_after_find_item, info)
        
        
        
