# -*- encoding=UTF-8 -*-

from haostagram import app

@app.route('/')
def index():
    return 'Hello'