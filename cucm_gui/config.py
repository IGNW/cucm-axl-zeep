import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_me_to_something_random_or_set_the_env_parameter'
