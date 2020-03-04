from flask import Flask
from cucm_gui.config import Config

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

from cucm_gui import routes
