# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # 头部加上这句
from flask import Flask, render_template, request, make_response, redirect, flash, get_flashed_messages
import logging
from logging.handlers import RotatingFileHandler

# 定义一个应用
app = Flask(__name__)

# 在flask项目中，Session, Cookies以及一些第三方扩展都会用到SECRET_KEY值，这是一个比较重要的配置值。
# 一般需要设置一个随机的SECRET_KEY值，可以用时钟做种子。此处简化用一个字符串测试。
# (服务器通过session来识别是同一个人)
app.secret_key = 'haoziiy_photograph'

# 装饰器，route作用:路径映射
@app.route('/')
@app.route('/index/')
def index():
    res = ''
    for msg in get_flashed_messages():
        res += msg + '<br>'
    res += 'Hello'
    return res

@app.route('/profile/<int:uid>/',methods=['GET','post'])
def profile(uid):
    colors = ('red', 'black')
    infos = {'name': 'abc', 'id': '123'}
    return render_template("profile.html", uid=uid, colors=colors, infos=infos)
@app.route('/request')
def request_demo():
    res = ''
    key = request.args.get('key', 'defaultkey')
    res += request.args.get('key', 'defaultkey') + '<br>'
    res = request.url + '+++++' + request.path
    for property in dir(request):
        res += str(property) + '|====|<br>' + str(eval('request.' + property)) + '<br>'
    response = make_response(res)
    response.set_cookie(key)
    return response

@app.route('/newpath')
def newpath_demo():
    return 'newpath'

@app.route('/re/<int:code>')
def redirect_demo(code):
    return redirect('/newpath', code=code)

@app.errorhandler(404)
def page_not_found(error):
    print error
    return render_template('not_found.html', url=request.url)

@app.route('/login')
def login():
    app.logger.info('login seccess')
    flash('登录成功') # 发送至flash message ( 可以理解为发送到session的一个buffer )
    return 'ok'


def set_logger():
    info_file_handler = RotatingFileHandler('\\User\\sherry\\PycharmProjects\\photograph\\logs\\info.txt')
    info_file_handler.setLevel(logging.INFO)
    app.logger.addHandler(info_file_handler)

    warn_file_handler = RotatingFileHandler('\\User\\sherry\\PycharmProjects\\photograph\\logs\\warn.txt')
    warn_file_handler.setLevel(logging.WARN)
    app.logger.addHandler(warn_file_handler)

    error_file_handler = RotatingFileHandler('\\User\\sherry\\PycharmProjects\\photograph\\logs\\error.txt')
    error_file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_file_handler)

if __name__ == '__main__':
    set_logger()
    app.run(debug=True)