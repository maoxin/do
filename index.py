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
    @tornado.web.asynchronous
    @tornado.gen.engine
    def do_find_one(self, email, phone, name, password):
        email_exist = yield motor.Op(
            self.db.users.contact.find_one, {'email': email}
        )
        phone_exist = yield motor.Op(
            self.db.users.contact.find_one, {'phone': phone}
		)
        
        if not email_exist and not phone_exist:
            contact_with_password = {
                'email': email,
				'phone': phone,
				'name': name,
                'password': password,
            }
			
            contact = {
				'email': email,
				'phone': phone,
				'name': name
			}
            
            self.db.users.contact_with_password.insert(contact_with_password)
            self.db.users.contact.insert(contact)

            self.set_secure_cookie('name', name)
            self.set_secure_cookie('password', password)
            self.set_secure_cookie('email', email)
            self.set_secure_cookie('phone', phone)

            message = {"response": 'ok'}
            message_json = json.dumps(message)
            self.set_header('Content_Type', 'application/json')
            self.write(message_json)

            self.redirect("/")
        
        else:
            if email_exist:
                message = {"response": 'Email Exists'}
            elif phone_exist:
                message = {"response": 'Phone Exists'}
            else:
                message = {"response": 'Something Wrong'}
				
            message_json = json.dumps(message)
			
            self.set_header('Content_Type', 'application/json')	
            self.write(message_json)
            self.finish()
    
    def get(self):
        self.render('register.html', post_page='/register')
    
    @tornado.web.asynchronous
    def post(self):
        email = self.get_argument('email')
        phone = self.get_argument('phone')
        name = self.get_argument('name')
        password = self.get_argument('password')

        self.do_find_one(email, phone, name, password)
    
        
        

class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def check(self, email_or_phone, password):
        try:
            int(email_or_phone)
            check_item = 'phone'
        
        except ValueError:
			if "@" in email_or_phone:
				check_item = 'mail'
			else:
				message = {"response": "Please Input Email or Phone"}
				message_json = json.dumps(message)
				self.set_header("Content_Type", "application/json")
				self.write(message_json)
				self.redirect('/login')
		
        document = yield motor.Op(
            self.db.users.contact_with_password.find_one, {check_item: email_or_phone}
        )
        
        if document and document['password'] == password:
            email = document['email']
            phone = document['phone']
            self.set_secure_cookie('name', name)
            self.set_secure_cookie('password', password)
            self.set_secure_cookie('email', email)
            self.set_secure_cookie('phone', phone)

            self.redirect("/")

        else:
            message = {"response": "%s doesn't exist." %check_item}
            message_json = json.dumps(message)
            self.set_header("Content_Type", "application/json")
            self.write(message_json)

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
    @tornado.web.asynchronous
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
 
class CreateItemHandler(BaseHandler):        
	def get(self):
		self.render('create_item.html', post_page='/create_item_post')
	
class CreateItemPostHandler(BaseHandler):
	def post(self):
		item_name = self.get_argument('item_name')
		number_of_people = self.get_argument('number_of_people')
		# the people finally must be between a scale.
		deadline = self.get_argument('deadline')
		happen_time = self.get_argument('happen_time')
		continue_time = self.get_argument('continue_time')
		describe = self.get_argument('describe')
		place = self.get_argument('place')
		participators = [self.current_user,]
		
		item_info = {
			'item_name': item_name,
			'number_of_people': number_of_people,
			'deadline': deadline,
			'happen_time': happen_time,
			'continue_time': continue_time,
			'describe': describe,
			'place': place,
			'participators': participators,
		}
		
		self.db.resource.items.insert(item_info)
        
class JoinItemHandler(BaseHandler):
    def get(self):
        self.render('join_item.html', post_page='/join_item_post')

class JoinItemPostHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def do_push_update(self, participator, item_name):
        document = yield motor.Op(
            self.db.resource.items.update, {'item_name': item_name}, {'$push':{"participators": participator}}
        )
        
        self.finish()
    
    
    @tornado.web.asynchronous
    def post(self):
        participator = self.get_argument('participator')
        item_name = self.get_argument('item_name')
        self.do_push_update(participator, item_name)
        
        
        
        

application = tornado.web.Application([
	(r'/', MainHandler),        # normal page, check wether a user logged.
    (r'/login', LoginHandler),  # login and check the the flush info.
    (r'/message_transfer', MessageTransferHandler), 
    (r'/my_message', GetMessageHandler), 
    (r'/register', RegisterHandler),
	(r'/create_item', CreateItemHandler),
	(r'/create_item_post', CreateItemPostHandler),
    (r'/join_item', JoinItemHandler),
    (r'/join_item_post', JoinItemPostHandler),
    # used by users to transfer info to other people,
    # info will be stored in database and be sent to the aim person.
    
    # (r'/state', StateHandler),
    # use to fresh one's state info. State is important for the social contact.
    
	], **settings)
 
if __name__ == '__main__':   
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()