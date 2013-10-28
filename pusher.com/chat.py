#!/usr/bin/env python

import json
import logging

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.log import enable_pretty_logging

import pusher

class MainHandler (tornado.web.RequestHandler):
  def post (self):
    self.set_header("Content-Type", "application/json")
    
    username = self.get_argument('username', default=None)
    message = self.get_argument('message', default=None)
    
    if username is not None and message is not None:
      logging.info('%s: %s' % (username, message))
      p = pusher.Pusher(
        app_id='43641',
        key='c35f2f2464da331ba3d3',
        secret='cf9d3cc28f742d39dfa9'
      )
      p['test_channel'].trigger('message_event', {'username': username, 'message': message})
      
    self.write(json.dumps({'status': 'OK'}))
    
  def get (self):
    fh = open('chat.html', 'r')
    chat_html = fh.read()
    fh.close()
    self.write(chat_html)
    
application = tornado.web.Application([
  (r"/", MainHandler),
])

if __name__ == "__main__":
  tornado.autoreload.start()
  enable_pretty_logging()
  
  application.listen(8000)
  logging.info('Web Server Started')
  tornado.ioloop.IOLoop.instance().start()
  