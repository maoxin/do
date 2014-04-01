import tornado.web
import tornado.ioloop
import pymongo
import motor
import account_handler
import os
import item_handler
import relation_handler

client = motor.MotorClient().open_sync()
# use the motor(http://motor.readthedocs.org) to operate mongodb in tornado.

settings = {
    'degbug': True,
    'autoreload': True,
    'client': client,
    'cookie_secret': 'a secret cookie should not be told.',
    # we can use something more secret stored in db.
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
    # (r'/is_logged', account_handler.IsLoggedHandler),
    # not neccessary. We can view the past info from sqlite
    #  and login to read more. 
    (r'/login', account_handler.LoginHandler),
    (r'/register', account_handler.RegisterHandler),
    (r'/item/post_item', item_handler.PostItemHandler),
    # (r'/item/join_item', item_handler.JoinItemHandler),
    (r'/item/picture', item_handler.PostItemPicure),
    (r'/item/get_new_item', item_handler.GetNewItemHandler),
    (r'/item/receive', item_handler.RecieveItemHandler),
    (r'/item/get_mission_picture', item_handler.GetMissionPictureHandler),
    (r'/relation/follow', relation_handler.FollowHandler),
    # post the latest items stored in mobile and get the new one.
    # (r'/item/talk_in_item', communication_handler.ItemTalkHandler),
    # (r'/item/get_talk_in_item', communication_handler.ItemGetTalkHandler),
	], **settings)
 
if __name__ == '__main__':   
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()    