import json
import motor
from log_info import log_info
import tornado.websocket

client = motor.MotorClient()

class TalkWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        log_info('web_socket_connected', client)
        
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
            log_info('web_socket_logged', client)
            try:
                name = json_file['name']
                email = json_file['email']
                item_id = json_file['mission_id']
                
                self.name = name
                self.email = email
                self.item_id = item_id
                
                if TalkWebSocket.attendees.has_key(item_id):
                    for item in TalkWebSocket.attendees[titem_id]:
                        if item.email == self.email:
                            self.write_message( {'status': 'already exist'} )
                            break
                    else:
                        TalkWebSocket.attendees[item_id].append(self)
                
                else:
                    TalkWebSocket.attendees[item_id] = [self, ]
        
                self.write_message( {'status': 'add_to_talk_list'} )
            
            except KeyError:
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                
        
        elif json_file.has_key('status') and json_file['status'] == 'talk':
            log_info('web_socket_talk', client)
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
        log_info('web_socket_disconnected', client)
        TalkWebSocket.attendees[self.item_id].pop(TalkWebSocket.attendees.index(self))
        if not TalkWebSocket.attendees[self.item_id]:
            TalkWebSocket.attendees.pop(self.item_id)   

TalkWebSocket.attendees = {}        
