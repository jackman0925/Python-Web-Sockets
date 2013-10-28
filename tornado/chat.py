#!/usr/bin/env python

import json
import logging

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.log import enable_pretty_logging
from tornado.websocket import WebSocketHandler

import pusher

class ChatWebSocket (WebSocketHandler):
  sockets = set()
  
  def open (self):
    logging.info("WebSocket opened")
    self.username = 'Not Set'
    ChatWebSocket.sockets.add(self)
    
  def on_message (self, data):
    data = json.loads(data)
    if data['task'] == 'set_user':
      self.username = data['username']
      logging.info("%s user set" % self.username)
      
      m = '%s entered the room.' % self.username
      ChatWebSocket.send_updates({'username': 'moderator', 'message': m})
      
    elif data['task'] == 'message':
      logging.info("%s: %s" % (self.username, data['message']))
      ChatWebSocket.send_updates({'username': self.username, 'message': data['message']})
      
  @classmethod
  def send_updates (cls, data):
    for socket in cls.sockets:
      socket.write_message(json.dumps(data))
      
  def on_close (self):
    ChatWebSocket.sockets.remove(self)
    logging.info("%s closed" % self.username)
    
class MainHandler (tornado.web.RequestHandler):
  def get (self):
    fh = open('chat.html', 'r')
    chat_html = fh.read()
    fh.close()
    self.write(chat_html)
    
application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/chat", ChatWebSocket),
])

if __name__ == "__main__":
  tornado.autoreload.start()
  enable_pretty_logging()
  
  application.listen(8000)
  logging.info('Web Server Started')
  tornado.ioloop.IOLoop.instance().start()
  