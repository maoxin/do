import tornado.web
import tornado.ioloop
import motor
import os

client = motor.MotorClient().open_sync()

settings = {
    'db': client,
    'degbug': True,
    'autoreload': True,
    'cookie_secret': 'a secret cookie should not be told.',
    'login_url': '/login',
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
}

application = tornado.web.Application([
	(r'/', MainHandler),        # normal page, check wether a user logged.
    (r'/login', LoginHandler),  # login and check the the flush info.
    (r'/message_transfer', MessageTransferHandler), 
    # used by users to transfer info to other people,
    # info will be stored in database and be sent to the aim person.
	(r'/state', StateHandler),
    # use to fresh one's state info. State is important for the social contact.
	], **settings)