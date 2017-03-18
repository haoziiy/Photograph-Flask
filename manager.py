# -*- encoding=UTF-8 -*-
from flask-script import Manager
from c2 import app

manager = Manager(app)

@manager.option('-n',  '--name', dest='name', default='nowcoder')
def hello(name):
    print 'hello', name

@manager.command
def initialize_database():
    'initialize database'
    print 'database ...'

if __name__ == '__main__':
    manager.run()