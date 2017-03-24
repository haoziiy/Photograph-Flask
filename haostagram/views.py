# -*- encoding=UTF-8 -*-

from haostagram import app, db, login_manager
from models import Image, User
from flask import render_template, redirect, request, flash, get_flashed_messages
import hashlib, random
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)

@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image==None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)

@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user==None:
        return redirect('/')
    return render_template('profile.html', user=user)

@app.route('/regloginpage/')
def regloginpage():
    if current_user.is_authenticated:
        return redirect('/')
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg += m
    return render_template('login.html', msg=msg)

def redirect_with_msg(target, msg, category):
    if msg !=None:
        flash(msg, category=category)
    return redirect(target)

@app.route('/reg/',methods={'post','get'})
def reg():
    # request.args
    # request.form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    user = User.query.filter_by(username=username).first()

    if username=='' or password=='':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', category='reglogin')
    if user != None:
        return redirect_with_msg('/regloginpage/', u'用户名已存在', category='reglogin')

    salt = '.'.join(random.sample('0123456789abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST', 10))
    m = hashlib.md5()
    m.update(password + salt) # salt强化密码
    password = m.hexdigest()

    # 提交新注册到user到数据库
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    logout_user(user)

    return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')