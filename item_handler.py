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
    def response_to_client(self, item_id, error):
        if not error:
            print 'Item Create Succeed'
            
            item_id = str(item_id)
            write_message = {"response": item_id}
            
            self.write_info_to_client(write_message)
            
        else:
            print error
            write_message = {"response": error}
            
            self.write_info_to_client(write_message)
    
    def create_mission(self, user_info, nothing_to_read):
        if user_info:
            self.item_info.insert(self.mission_info, callback=self.response_to_client)
        
        else:
            write_message = {"response": "id_key_not_matched"}
            self.write_info_to_client(write_message)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('post_item', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_CREATE_ITEM'))
        
        email = json_file['mission_up_email']
        user_id = json_file['user_id']
        user_key = json_file['user_key']
        
        mission_up_email = json_file['mission_up_email']
        mission_up_name = json_file['mission_up_name']
        
        mission_tag = json_file['mission_tag']
        mission_name = json_file['mission_name']
        mission_description = json_file['mission_description']
        
        mission_place_name = json_file['mission_place_name']
        mission_lat = json_file['mission_lat']
        mission_lon = json_file['mission_lon']
        
        user_place_name = json_file['user_place_name']
        user_lat = json_file['user_lat']
        user_lon = json_file['user_lon']
        
        mission_begin_time = json_file['mission_begin_time']
        mission_continue = json_file['mission_continue']
        
        mission_accept_num = json_file['mission_accept_num']

        
        self.mission_info = {
            'mission_up_email': mission_up_email,
            'mission_up_name': mission_up_name,

            'mission_tag': mission_tag,
            'mission_name': mission_name,
            'mission_description': mission_description,
            
            'mission_place_name': mission_place_name,
            'mission_lat': mission_lat,
            'mission_lon': misssion_lon,
            
            'user_place_name': user_place_name,
            'user_lat': user_lat,
            'user_lon': user_lon,
            
            'mission_begin_time': mission_begin_time,
            'mission_continue': mission_continue,           
            
            'mission_accept_num': int(mission_accept_num),
            
            'mission_attendee': [],
            # the uper himself maybe or not a member. need detail.
            
            'mission_pic_path': None,
        }
        
        self.user_id_key_identify(user_id, user_key, email, self.create_mission)
        
 
class PostItemPicure(BaseHandler):
    def response_to_client(self, update_result, nothing_to_read):
        if update_result:
            write_message = {"response": 'ok'}
            
            self.write_info_to_client(write_message)
            
        else:
            write_message = {"response": 'fail'}
            
            self.write_info_to_client(self.write_message)
   
    @tornado.web.asynchronous
    def post(self):
        log_info('post_picture', self.log_operation)
        
        json_file = json.loads(self.get_argument('JSON_POST_ITEM_PIC'))
        
        mission_name = json_file['mission_name']
        mission_up_email = json_file['mission_up_email']
        mission_picture = json_file['mission_picture']
        
        pic_decode = base64.b64decode(mission_picture)
        
        pic_path = './item_photo/' + mission_up_email + '+' + mission_name + '.png'
        with open(pic_path, 'wb') as pc:
            pc.write(pic_decode)
        
        query_for_insert_pic = {
            'mission_name': mission_name,
            'mission_up_email': mission_up_email
        }
        
        change = {
            "$set": {'mission_pic_path': pic_path}
        }
        
        info_to_response_to_clinet = {}
        
        print query_for_insert_pic
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_update(query_for_insert_pic, change, self.response_to_client, info_to_response_to_clinet)
        
        
class GetNewItemHandler(BaseHandler):
    def package_deleted_items_and_response_to_client(self, deleted_items, items_info):
        write_message = {'response': items_info}
        
        if deleted_items:
            deleted_ids = [str(x['deleted_item_id']) for x in deleted_items]
            write_message['delete_ids'] = delete_ids
        
        else:
            pass
         
        self.write_info_to_client(write_message)
        
    
    
    def package_new_items(self, items, latest_id):
        if items:
            new_items = filter(lambda x: x['_id'] > latest_id, items)
            items_info = []
            
            for item in new_items:
                info = {
                    'mission_id': str(item['_id']),
                    'mission_up_email': item['mission_up_email'],
                    'mission_up_name': item['mission_up_name'],
        
                    'mission_tag': item['mission_tag'],     
                    'mission_name': item['mission_name'],
                    'mission_description': item['mission_description'],

                    'mission_place_name': item['mission_place_name'],
                    'mission_lat': item['mission_lat'],
                    'mission_lon': item['mission_lon'],

                    'mission_begin_time': item['mission_begin_time'],
                    'mission_continue': item['mission_continue'],
                    'mission_accept_num': item['mission_accept_num'],

                    'mission_attendee': item['mission_attendee'],

                    'mission_pic_path': item['mission_pic_path'],
                }
                
                items_info.append(info)
            
            query_for_delete_items = {
                '_id': {
                    '$in': self.ids
                }
            }
               
            
            collection = db_handler.DBHandler(self.deleted_item_info)
            collection.do_find(query_for_delete_items, self.package_deleted_items_and_response_to_client, items_info, direction=-1, axis="_id", limit=15)
            
        else:
            write_message = {"response": "fail"}
            
            self.write_info_to_client(write_message)
    
    
    @tornado.web.asynchronous
    def post(self):
        log_info('get_new_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_GET_NEW_ITEM'))

        ids = list(np.unique(json_file['ids']))
        print ids
        ids = [ObjectId(x) for x in ids]
        self.ids = ids
        
        if not ids or not ids[0]:
            latest_id = 0
        else:
            latest_id = max(ids)
        
        query_for_find_new_operation = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find(query_for_find_new_operation, self.package_new_items, max_id, direction=-1, axis="_id", limit=15)
        
class GetItemInMapHandler(BaseHandler):
    def package_deleted_items_and_response_to_client(self, deleted_items, items_info):
        write_message = {'response': items_info}
        
        if deleted_items:
            deleted_ids = [str(x['deleted_item_id']) for x in deleted_items]
            write_message['delete_ids'] = delete_ids
        
        else:
            pass
         
        self.write_info_to_client(write_message)
        
    
    
    def package_new_items(self, items, latest_id):
        if items:
            new_items = filter(lambda x: x['_id'] > latest_id, items)
            items_info = []
            
            for item in new_items:
                info = {
                    'mission_id': str(item['_id']),
                    'mission_up_name': item['mission_up_name'],
        
                    'mission_name': item['mission_name'],

                    'mission_lat': item['mission_lat'],
                    'mission_lon': item['mission_lon'],
                }
                
                items_info.append(info)
            
            query_for_delete_items = {
                '_id': {
                    '$in': self.ids
                }
            }
               
            
            collection = db_handler.DBHandler(self.deleted_item_info)
            collection.do_find(query_for_delete_items, self.package_deleted_items_and_response_to_client, items_info, direction=-1, axis="_id", limit=15)
            
        else:
            write_message = {"response": "fail"}
            
            self.write_info_to_client(write_message)
    
    
    @tornado.web.asynchronous
    def post(self):
        log_info('get_new_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_GET_NEW_ITEM'))

        ids = list(np.unique(json_file['ids']))
        print ids
        ids = [ObjectId(x) for x in ids]
        self.ids = ids
        
        if not ids or not ids[0]:
            latest_id = 0
        else:
            latest_id = max(ids)
        
        query_for_find_new_operation = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find(query_for_find_new_operation, self.package_new_items, max_id, direction=-1, axis="_id", limit=15)

class RecieveItemHandler(BaseHandler):
    def response_to_client(self, update_result, item):
        if update_result:
            item['mission_attendee'].append(self.join_email)
            item_info = {
                'response': 'ok',
                'mission_attendee': item['mission_attendee'],
                'id': str(result['_id'])
            }
        
            write_message = item_info
            
            self.write_info_to_client(write_message)
            
        else:
            write_message = {"response": error}
            
            self.write_info_to_client(write_message)
    
    def check_user_not_exist_and_allow(self, item, nothing_to_read):
        if item and (len(item['mission_attendee']) < int(item['mission_accept_num'])):
            print len(item['mission_attendee']), item['mission_accept_num']
            
            mission_attendee = item['mission_attendee']
            
            if self.join_email not in mission_attendee:
            
                query_for_update = {
                    '_id': self.mission_id
                }
                
                change = {
                    '$push': {'mission_attendee': self.join_email}
                }
                
                info_to_following_func = item
                
                collection = db_handler.DBHandler(self.item_info)
                collection.do_update(query_for_update, change, self.response_to_client, info_to_following_func)
            
            else:
                write_message = {
                    'response': 'user_already_join_the_item'
                }
                
                self.write_info_to_client(write_message)
        
        else:
            if not item:
                write_message = {"response": "item not found"}
           
            elif len(item['mission_attendee']) >= int(item['mission_accept_num']):
                write_message = {"response": "attendee full"}
                
            else:
                write_message = {"response": "fail"}
                
            self.write_info_to_client(write_message)
            

    def find_the_item(self, user_info, nothing_to_read):
        if user_info:
            query_for_find_the_item = {
                '_id': self.mission_id,
            }
            
            info_to_following_func = {}
            
            collection = db_handler.DBHandler(self.item_info)
            collection.do_find_one(query_for_find_the_item, self.check_user_not_exist_and_allow, info_to_following_func)

    @tornado.web.asynchronous
    def post(self):
        log_info('recieve_item', self.log_operation)
            
        email = json_file['join_email']
        user_id = json_file['user_id']
        user_key = json_file['user_key']
        
        json_file = json.loads(self.get_argument('JSON_RECEIVE_ITEM'))
        self.mission_id = ObjectId(json_file['mission_id'])
        self.join_email = json_file['join_email']

        self.user_id_key_identify(user_id, user_key, email, self.find_the_item)

             

    
    
class DeleteItemHandler(BaseHandler):
    def response_to_client(self, remove_result, error):
        if not error:
            write_message = {"response": 'ok', 'id': str(self.mission_id)}

            self.write_info_to_client(write_message)
            
        else:
            write_message = {"response": error}
            
            self.write_info_to_client(write_message)
           
            
        
    def delete_the_item(self, insert_result, error):
        if not error:
            query_for_remove_item = {
                '_id': self.mission_id,
            }
            
            self.item_info.remove(query_for_remove_item, callback=self.response_to_client)
        else:
            write_message = {'response': error}
            self.write_info_to_client(write_message)
    
    def create_deleted_item(self, item, nothing_to_read):
        if item:
            item['delete_time_id'] = item['_id']
            item.pop('_id')
            
            self.deleted_item_info.insert(item, callback=self.delete_the_item)
        
        else:
            write_message = {'response': 'fail'}
            self.write_info_to_client(write_message)
        
    def find_the_item(self, user_info, nothing_to_read):
        
        query_for_find_the_item = {
            '_id': self.mission_id,
            'mission_up_email': self.mission_up_email,
        }
        
        info_to_following_func = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find_one(query_for_find_the_item, self.create_deleted_item, info_to_following_func)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('delete_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_DELETE_ITEM'))
        
        email = json_file['email']
        user_id = json_file['user_id']
        user_key = json_file['user_key']
        
        self.mission_id = ObjectId(json_file['mission_id'])
        self.mission_up_email = json_file['mission_up_email']
        
        self.user_id_key_identify(user_id, user_key, email, self.find_the_item)

class ArchiveItemHandler(BaseHandler):
    def response_to_client(self, remove_result, error):
        if not error:
            write_message = {"response": 'ok', 'id': str(self.mission_id)}

            self.write_info_to_client(write_message)
            
        else:
            write_message = {"response": error}
            
            self.write_info_to_client(write_message)
           
            
        
    def archive_the_item(self, insert_result, error):
        if not error:
            query_for_remove_item = {
                '_id': self.mission_id,
            }
            
            self.item_info.remove(query_for_remove_item, callback=self.response_to_client)
        else:
            write_message = {'response': error}
            self.write_info_to_client(write_message)
    
    def create_archived_item(self, item, nothing_to_read):
        if item:
            item['delete_time_id'] = item['_id']
            item.pop('_id')
            
            self.archiveded_item_info.insert(item, callback=self.archive_the_item)
        
        else:
            write_message = {'response': 'fail'}
            self.write_info_to_client(write_message)
        
    def find_the_item(self, user_info, nothing_to_read):
        
        query_for_find_the_item = {
            '_id': self.mission_id,
            'mission_up_email': self.mission_up_email,
        }
        
        info_to_following_func = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find_one(query_for_find_the_item, self.create_archived_item, info_to_following_func)
    
    @tornado.web.asynchronous
    def post(self):
        log_info('archive_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_DELETE_ITEM'))
        
        email = json_file['email']
        user_id = json_file['user_id']
        user_key = json_file['user_key']
        
        self.mission_id = ObjectId(json_file['mission_id'])
        self.mission_up_email = json_file['mission_up_email']
        
        self.user_id_key_identify(user_id, user_key, email, self.find_the_item)

class ItemTalkHandler(BaseHandler):
    def send_talk(self, insert_result, error):
        if not error:
            mission_id = str(self.info['mission_id'])
            talking_email = self.info['talking_email']
            talking_name = self.info['talking_name']
            talking_content = self.info['talking_content']
            
            try:
                print 'try send to every one'
                talk_man = TalkWebSocket.attendees[mission_id][talking_email]

                if talk_man:
                    talk_man.write_content_to_team_mate(talking_content)

            except KeyError:
                raise 
            
            write_message = {"response": 'ok'}
            self.write_content_to_team_mate(write_message)
            
        else:
            write_message = {"response": error}
            self.write_content_to_team_mate(write_message)
           
    @tornado.web.asynchronous
    def post(self):
        log_info('talk_in_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_TALK_ITEM'))
        mission_id = ObjectId(json_file['mission_id'])
        talking_email = json_file['talking_email']
        talking_name = json_file['talking_name']
        talking_content = json_file['talking_content']
        
        self.info = {
            'mission_id': mission_id,
            'talking_email': talking_email,
            'talking_name':  talking_name,
            'talking_content': talking_content
        }
        
        self.talk_info.insert(self.info, callback=self.send_talk)
        
class ItemGetTalkHandler(BaseHandler):
    def response_to_client(self, talks, info):
        if talks:
            talks = filter(lambda x: x['_id'] > self.latest_id, talks)
            talks_info = []
            
            for talk in talks:
                talks_info.append(
                    {
                        'talking_id': str(talk['_id']),
                        'mission_id': str(talk['mission_id']),
                        'talking_email': talk['talking_email'],
                        'talking_name':  talk['talking_name'],
                        'talking_content': talk['talking_content'],
                    }
                )
            
            write_message = {'response': self.items_info}
            self.write_info_to_client(write_message)
        
        else:
            write_message = {'response': 'fail'}
            self.write_info_to_client(write_message)
            
    
    def find_talk_place(self, item, nothing_to_read):
        if item:
            query_for_get_talk = {
                'mission_id': self.mission_id,
            }
            
            info_to_following_func = {}
            collection = db_handler.DBHandler(self.talk_info)
            collection.do_find(query, self.response_to_client, info_to_following_func, direction=-1, axis="_id", limit=10)
    
    
    @tornado.web.asynchronous
    def post(self):
        log_info('get_talks_in_item', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_ITEM_GET_TALK'))
        self.mission_id = ObjectId(json_file['mission_id'])
        join_email = json_file['join_email']
        talk_ids = list(np.unique(json_file['talk_ids']))
        
        talk_ids = [ObjectId(x) for x in talk_ids]
        self.talk_ids = talk_ids
        
        if not talk_ids or not talk_ids[0]:
            self.latest_id = 0
        else:
            self.latest_id = max(talk_ids)
            
        query_for_find_the_item = {
            '_id': self.mission_id,
            'attendee': {
                '$in': [join_email],
            }
        }
        
        info_to_following_func = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find_one(self.query_item, self.find_talk_place, info_to_following_func)
        
        
class GetItemDetailHandler(BaseHandler):
    
    def func_after_find_item(self, item, nothing_to_read):
        if result:
            info = {
                'mission_id': str(item['_id']),
                'mission_up_email': item['mission_up_email'],
                'mission_up_name': item['mission_up_name'],

                'mission_tag': item['mission_tag'],     
                'mission_name': item['mission_name'],
                'mission_description': item['mission_description'],

                'mission_place': item['mission_place_name'],
                'mission_lat': item['mission_lat'],
                'mission_lon': item['mission_lon'],

                'mission_begin_time': item['mission_begin_time'],
                'mission_continue': item['mission_continue'],
                'mission_accept_num': item['mission_accept_num'],
                
                'user_lat': item['user_lat'],
                'user_lon': item['user_lon'],
                'user_place_name': item['user_place_name']

                'mission_attendee': item['mission_attendee'],

                'mission_pic_path': item['mission_pic_path'],
                }
            
            write_message = info
            self.write_info_to_client(write_message)
        
        else:
            write_message = {
                'response': 'mission not found'
            }
            
            self.write_info_to_client(write_message)   
    
    @tornado.web.asynchronous
    def post(self):    
        log_info('get_item_detail', self.log_operation)
            
        json_file = json.loads(self.get_argument('JSON_GET_MISSION_MORE'))
        mission_id = ObjectId(json_file['mission_id'])
        
        query_for_find_mission = {
            'mission_id': mission_id,
        }
        
        info_to_following_func = {}
        
        collection = db_handler.DBHandler(self.item_info)
        collection.do_find_one(query_for_find_mission, self.response_to_client, info_to_following_func)
        
