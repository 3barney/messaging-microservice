import yaml

from flask import Flask, render_template, request
from flask.views import MethodView
from flask.json import jsonify

from nameko.standalone.rpc import ClusterRpcProxy # allows us to make RPCs outside a Nameko service.

#Tell flask wwhere to find RabbitMq
with open('config.yaml', 'r') as config_file:
  config = yaml.load(config_file)

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html')


class MessageAPI(MethodView):
  
  def get(self):
    with ClusterRpcProxy(config) as rpc:
      messages = rpc.message_service.get_all_messages()

    return jsonify(messages)

  def post(self):
    data = request.get_json(force=True)

    try:
      message = data['message']
    except KeyError:
      return 'No message given', 400
    
    with ClusterRpcProxy(config) as rpc:
      rpc.message_service.save_message(message)
    
    return '', 204

  
app.add_url_rule('/messages', view_func=MessageAPI.as_view('messages'))
