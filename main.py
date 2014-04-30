import os
import motor
import pymongo
import tornado.web
import tornado.ioloop
import account_handler
import item_handler
import relation_handler
import web_socket_handler

client = motor.MotorClient()
# use the motor(http://motor.readthedocs.org) to operate mongodb in tornado.

settings = {
    'degbug': True,
    'autoreload': True,
    'client': client,
    # 'cookie_secret': 'a secret cookie should not be told.',
    # we can use something more secret stored in db.
    # 'static_path': os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
    # (r'/is_logged', account_handler.IsLoggedHandler),
    # not neccessary. We can view the past info from sqlite
    #  and login to read more. 
    (r'/login', account_handler.LoginHandler),
    (r'/register', account_handler.RegisterHandler),
    (r'/change_profile', account_handler.ChangeProfileHandler),
    
    (r'/item/post_item', item_handler.PostItemHandler),
    (r'/item/picture', item_handler.PostItemPicure),
    
    (r'/item/get_new_item', item_handler.GetNewItemHandler),
    (r'/item/get_mission_picture', item_handler.GetMissionPictureHandler),
    
    (r'/item/receive', item_handler.RecieveItemHandler),
    (r'/item/delete', item_handler.DeleteItemHandler),
    (r'/item/archive', item_handler.ArchiveItemHandler),
    
    (r'/relation/follow', relation_handler.FollowHandler),
    # post the latest items stored in mobile and get the new one.
    
    (r'/item/talk_in_item', item_handler.ItemTalkHandler),
    (r'/item/get_talk_in_item', item_handler.ItemGetTalkHandler),
    
    (r'/talk_web_socket', web_socket_handler.TalkWebSocket),
    (r'/position_web_socket', web_socket_handler.MapWebSocket),
	], **settings)
 
if __name__ == '__main__':   
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()    
