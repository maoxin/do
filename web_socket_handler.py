import json
from dateutil import parser
from datetime import datetime
import motor
from log_info import log_info
import tornado.websocket

client = motor.MotorClient()

class TalkWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        log_info('talk_web_socket_connected', client)
        
        self.write_message({'status': "connected"})
    
    
    def write_content_to_team_mate(self, content):
        info = {
            'status': 'get_talk',
            'talk_name': self.name,
            'talk_content': content,
            'item_id': self.item_id,
        }

        for attendee in TalkWebSocket.attendees[self.item_id]:
            attendee.write_message(info)

        
    def on_message(self, message):
        json_file = json.loads(message)
        
        if json_file.has_key('status') and json_file['status'] == 'log_in':
            log_info('talk_web_socket_logged', client)
            try:
                name = json_file['name']
                email = json_file['email']
                item_id = json_file['mission_id']
                
                self.name = name
                self.email = email
                self.item_id = item_id
                
                if TalkWebSocket.attendees.has_key(item_id):
                    for item in TalkWebSocket.attendees[item_id]:
                        if item.email == self.email:
                            self.write_message( {'status': 'already exist'} )
                            break
                    else:
                        TalkWebSocket.attendees[item_id].append(self)
                
                else:
                    TalkWebSocket.attendees[item_id] = [self, ]
        
                self.write_message( {'status': 'add_to_talk_list'} )
            
            except KeyError:
                print 'Key Error in talk web socket'
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                
        
        elif json_file.has_key('status') and json_file['status'] == 'talk':
            log_info('talk_web_socket_talk', client)
            try:
                content = json_file['talk_content']
                
                info = {
                    'status': 'get_talk',
                    'talk_name': self.name,
                    'talk_content': content,
                }
            
                for attendee in TalkWebSocket.attendees:
                    attendee.write_message(info)
                    
            except KeyError:
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                    
        else:
            self.write_message({'status': 'error', 'detail': 'please enter a \'status\' as \'log_in\' or \'talk\''})
                    
                
    def on_close(self):
        log_info('talk_web_socket_disconnected', client)
        try:
            TalkWebSocket.attendees[self.item_id].pop(TalkWebSocket.attendees[self.item_id].index(self))
            if not TalkWebSocket.attendees[self.item_id]:
                TalkWebSocket.attendees.pop(self.item_id)   
        except ValueError:
            if TalkWebSocket.attendees.has_key(self.item_id):
                print 'Already logged out', TalkWebSocket.attendees[self.item_id]
            else:
                print 'Already logged out and delete the key-value'

TalkWebSocket.attendees = {}  

class MapWebSocket(tornado.websocket.WebSocketHandler):      
    def open(self):
        log_info('map_web_socket_connected', client)
        
        self.write_message({'status': "connected"})
    
    def on_message(self, message):
        json_file = json.loads(message)
        
        if json_file.has_key('status') and json_file['status'] == 'log_in':
            log_info('map_web_socket_logged', client)
            try:
                name = json_file['name']
                email = json_file['email']
                item_id = json_file['mission_id']
                
                self.name = name
                self.email = email
                self.item_id = item_id
                
                if MapWebSocket.attendees.has_key(item_id):
                    for item in MapWebSocket.attendees[item_id]:
                        if item.email == self.email:
                            self.write_message( {'status': 'already exist'} )
                            break
                    else:
                        MapWebSocket.attendees[item_id].append(self)
                
                else:
                    MapWebSocket.attendees[item_id] = [self, ]
                
                self.time = datetime.now()
                self.write_message( {'status': 'add_to_talk_list'} )
            
            except KeyError:
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                
        
        elif json_file.has_key('status') and json_file['status'] == 'report_position':
            log_info('map_web_socket_report_map', client)
            try:
                tm_now = datetime.now()
                print json_file['time']
                tm = parser.parse(json_file['time'])
                lat = json_file['lat']
                lon = json_file['lon']
                
                print tm, tm_now
                delta = tm - tm_now
                delta_self = tm - self.time
                
                if (delta.days == 0 and delta.seconds < 30) and \
                   (delta_self.days * 86400 + delta_self.seconds > 0) :
                   
                    self.time = tm
                    
                    info = {
                        'status': 'fresh_position',
                        'time': json_file['time'],
                        'mission_id': self.item_id,
                        'email': self.email,
                        'name':  self.name,
                        'lat': lat,
                        'lon': lon,
                    }
            
                    for attendee in TalkWebSocket.attendees:
                        attendee.write_message(info)
                    
            except KeyError:
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                    
        else:
            pass
    
    def on_close(self):
        log_info('map_web_socket_disconnected', client)
        try:
            MapWebSocket.attendees[self.item_id].pop(MapWebSocket.attendees[self.item_id].index(self))
            if not MapWebSocket.attendees[self.item_id]:
                MapWebSocket.attendees.pop(self.item_id)   
        except ValueError:
            if MapWebSocket.attendees.has_key(self.item_id):
                print 'Already logged out', MapWebSocket.attendees[self.item_id]
            else:
                print 'Already logged out and delete the key-value'

MapWebSocket.attendees = {}
