import tornado.web
import tornado.ioloop
import tornado.gen
import motor
import pymongo
import os
import time
import json

client = motor.MotorClient().open_sync()

settings = {
    'db': client,
    'degbug': True,
    'autoreload': True,
    'cookie_secret': 'a secret cookie should not be told.',
    'login_url': '/login',
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
}       

class BaseHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.db = self.settings['db']
    
    def get_current_user(self):
        return self.get_secure_cookie("name")
            
    

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.redirect("/message_transfer")

class RegisterHandler(BaseHandler):
    @tornado.gen.engine
    def do_find_one(self, name, password, col):
        if col == 'user_and_password':
            collection = self.db.users.user_and_password
        else:
            collection = self.db.users.user
        
        name_exist = yield motor.Op(
            collection.find_one, {'name': name}
        )
        
        if not name_exist:
            user = {
                'name': name,
                'password': password,
            }
            self.db.users.user_and_password.insert(user)
            self.db.users.user.insert({
                'name': name,
            })
            
            self.set_secure_cookie('name', name)
            self.set_secure_cookie('password', password)
            
            self.redirect("/")
        
        else:
            self.write('Account been registered!, Fresh Page to try again.')
        
        self.finish()
    
    def get(self):
        self.render('account.html', post_page='/register')
    
    @tornado.web.asynchronous
    def post(self):
        name = self.get_argument('name')
        password = self.get_argument('password')
        
        self.do_find_one(name, password, 'user')
            
        
        

class LoginHandler(BaseHandler):
    @tornado.gen.engine
    def check(self, name, password):
        document = yield motor.Op(
            self.db.users.user_and_password.find_one, {'name': name}
        )
        
        if document and document['password'] == password:
            self.set_secure_cookie('name', name)
            self.set_secure_cookie('password', password)
            
            self.redirect("/")
        
        else:
            self.write('Account not exists or password wrong!')
            
        self.finish()
    
    def get(self):
        if self.current_user:
            self.redirect("/")
            
        else:
            self.render('account.html', post_page='/login')
    
    @tornado.web.asynchronous
    def post(self):
        name = self.get_argument('name')
        password = self.get_argument('password')
        
        self.check(name, password)
        
        
        
class MessageTransferHandler(BaseHandler):
    # currently transfer data via post form.
    def get(self):
        self.render('message.html', post_page='/message_transfer')
    
    def post(self):
        aim_person = self.get_argument('name')
        message = self.get_argument('message')
        photo = None
        
        entry = {
            'from_person': self.current_user,
            'to_person': aim_person,
            'message': message,
            'time': time.time(),
            'photo_name': None,
        }
        
        try:
            photo = self.request.files['photo'][0]
            file_name = photo['filename']
            name_length = len(file_name)
            if os.path.exists(os.path.join(os.path.dirname(__file__), 'photo',file_name)[:name_length]) and file_name == 'None':
                i = 1
                while os.path.exists(os.path.join(os.path.dirname(__file__), 'photo', file_name)[:name_length]) and file_name == 'None':
                    file_name = file_name[:name_length] + str(i)
            fl = open(file_name, 'wb')
            fl.write(photo['body'])
            entry['photo_name'] = file_name
            fl.close()
            self.db.resource.entries.insert(entry)

        except KeyError:
            self.db.resource.entries.insert(entry)
        
        self.write("Message has been sent!")
        
class GetMessageHandler(BaseHandler):
    @tornado.gen.engine
    def do_find(self, name):
        cursor = self.db.resource.entries.find({'to_person': name})
        # the latest 10 items.
        
        cursor.sort( [('time', pymongo.DESCENDING)] ).limit(10)
        # get the latest 10 items.
        
        messages = yield motor.Op(cursor.to_list)
        if messages:
            self.set_header('Content-Type', 'application/json')
            for document in messages:
                message_obj = {
                    'from_person': document['from_person'],
                    'message': document['message'],
                }
                
                message_json = json.dumps(message_obj)
                self.write(message_json)
                
        else:
            self.write("No Message Now.")
        
        self.finish()
        # finish is necessary because nothing will be write before the end.
    
    def get(self):
        self.render('my_message.html', post_page='/my_message')
    
    @tornado.web.asynchronous
    def post(self):
        name = self.get_argument('name')
        self.do_find(name)
        
        

application = tornado.web.Application([
	(r'/', MainHandler),        # normal page, check wether a user logged.
    (r'/login', LoginHandler),  # login and check the the flush info.
    (r'/message_transfer', MessageTransferHandler), 
    (r'/my_message', GetMessageHandler),
    (r'/register', RegisterHandler),
    # used by users to transfer info to other people,
    # info will be stored in database and be sent to the aim person.
    
    # (r'/state', StateHandler),
    # use to fresh one's state info. State is important for the social contact.
    
	], **settings)
 
if __name__ == '__main__':   
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()