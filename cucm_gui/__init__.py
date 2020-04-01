from flask import Flask
from cucm_gui.config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
bootstrap = Bootstrap(app)

from cucm_gui import routes
