import motor
import tornado.web
import tornado.websocket

client = motor.MotorClient()

class BaseHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.client = self.settings['client']
        
class BaseWebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def prepare(self):
        self.client = client