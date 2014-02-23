import tornado.web
import tornado.ioloop
# import tornado.auth
import motor
import os
import time

client = motor.MotorClient().open_sync()

settings = {
    'db': client,
    'degbug': True,
    'autoreload': True,
    'cookie_secret': 'a secret cookie should not be told.',
    'login_url': '/login',
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
}       

class BaseHandler(tornado.web.RequestHandler):
    
    def get_current_user(self):
        return self.get_secure_cookie("name")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("%s, You have Logged." % self.current_user)
        time.sleep(3)
        self.redirect("/message_transfer")

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', post_page='/login')
    
    def post(self):
        self.db = self.settings['db']
        name = self.get_argument('name')
        password = self.get_argument('password')
        self.set_secure_cookie('name', name)
        self.set_secure_cookie('password', password)
        
        user = {
            'name': name,
            'password': password,
        }
        self.db.users.user_and_password.insert(user)
        self.db.users.user.insert({
            'name': name,
        })
        
        self.redirect("/")
        
        
class MessageTransferHandler(BaseHandler):
    # currently transfer data via post form.
    def get(self):
        self.render('message.html', post_page='/message_transfer')
    
    def post(self):
        self.db = self.settings['db']
        aim_person = self.get_argument('name')
        message = self.get_argument('message')
        entry = {
            'from_person': self.current_user,
            'to_person': aim_person,
            'message': message,
            'time': time.time(),
        }
        self.db.resource.entries.insert(entry)
        
        self.write("Message has been sent!")
        

application = tornado.web.Application([
	(r'/', MainHandler),        # normal page, check wether a user logged.
    (r'/login', LoginHandler),  # login and check the the flush info.
    (r'/message_transfer', MessageTransferHandler), 
    # used by users to transfer info to other people,
    # info will be stored in database and be sent to the aim person.
    # (r'/state', StateHandler),
    # use to fresh one's state info. State is important for the social contact.
	], **settings)
 
if __name__ == '__main__':   
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()