# -*- encoding=UTF-8 -*-
from c2 import app
from flask_script import Manager
manager = Manager(app)

@manager.option('-n',  '--name', dest='name', default='haoziiy')
def hello(name):
    print 'hello', name

# 装饰器方式表示这是个命令
@manager.command
def initialize_database():
    'initialize database'
    print 'database ...'

if __name__ == '__main__':
    manager.run()