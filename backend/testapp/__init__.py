from flask import Flask
from flask_cors import CORS
import socket  # Telloに送るためにsocketを使用
from dpmatch01 import DP_ans, load_dataset 
import os

app = Flask(__name__)
CORS(app)

import testapp.views
