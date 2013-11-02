import json
import logging
import urllib

from django import http
from django.template.response import TemplateResponse

from pulsar.apps import ws, pubsub

def home (request):
  return TemplateResponse(request, 'chat.html', {})
  
class Client (pubsub.Client):
  def __init__ (self, connection):
    self.connection = connection
    
  def __call__ (self, channel, message):
    if channel == 'webchat':
      self.connection.write(message)
      
class Chat (ws.WS):
  _pubsub = None

  def pubsub (self, websocket):
    if not self._pubsub:
      # Uses local memory backend by default, not scalable to multiple processes
      self._pubsub = pubsub.PubSub()
      self._pubsub.subscribe('webchat')
      
    return self._pubsub
    
  def on_close (self, websocket):
    username = websocket.handshake.get('username')
    logging.info("%s left" % username)
    m = '%s left the room.' % username
    msg = {'username': 'moderator', 'message': m}
    self.pubsub(websocket).publish('webchat', json.dumps(msg))
    
  def on_open (self, websocket):
    self.pubsub(websocket).add_client(Client(websocket))
    
    username = websocket.handshake.get('username')
    logging.info("%s joined" % username)
    
    m = '%s entered the room.' % username
    msg = {'username': 'moderator', 'message': m}
    self.pubsub(websocket).publish('webchat', json.dumps(msg))
    
  def on_message (self, websocket, data):
    if data:
      data = json.loads(data)
      username = websocket.handshake.get('username')
      
      if data['task'] == 'message':
        message = data['message']
        
        logging.info("%s: %s" % (username, message))
        msg = {'username': username, 'message': message}
        self.pubsub(websocket).publish('webchat', json.dumps(msg))
        
CHATROOM = ws.WebSocket('/chat', Chat())
def chat (request):
  username = request.COOKIES.get('username', '')
  if username:
    environ = request.META
    environ['username'] = urllib.unquote(username)
    response = CHATROOM(environ)
    
    if response is not None:
      # we have a response, this is the websocket upgrade.
      resp = http.HttpResponse(status=response.status_code, content_type=response.content_type)
      for header, value in response.headers:
        resp[header] = value
        
      return resp
      
  raise http.Http404
  