import json
import tornado.websocket

class TalkWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.write_message({'status': "connected"})
        
    def on_message(self, message):
        json_file = json.loads(message)
        
        if json_file.has_key('status') and json_file['status'] == 'log_in':
            try:
                name = json_file['name']
                email = json_file['email']
                item_id = json_file['mission_id']
                
                self.name = name
                self.email = email
                self.item_id = item_id
                
                if TalkWebSocket.attendees.has_key(item_id):
                    TalkWebSocket.attendees[item_id].append(self)
                else:
                    TalkWebSocket.attendees[item_id] = [self, ]
        
                self.write_message( {'status': 'add_to_talk_list'} )
            
            except KeyError:
                self.write_message( {'status': 'error', 'detail': 'enter the right key'})
                
        
        elif json_file.has_key('status') and json_file['status'] == 'talk':
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
        print self.email, 'disconnected'
        
    

        