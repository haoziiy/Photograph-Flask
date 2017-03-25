# -*- encoding=UTF-8 -*-
import os, uuid

from haostagram import app, db, login_manager
from models import Image, User, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import hashlib, random, json
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
@app.route('/index')
def index():
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=5)
   #images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', has_next=paginate.has_next, images=paginate.items)

@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    # 参数检查
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)

    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username': comment.user.username,
                             'user_id': comment.user_id,
                             'content': comment.content
                             })
        imgvo = {'id': image.id,
                 'url': image.url,
                 'comment_count': len(image.comments),
                 'user_id': image.user_id,
                 'head_url': image.user.head_url,
                 'created_date': str(image.created_date),
                 'comments': comments
                 }
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)

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
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)
    return render_template('profile.html', user = user, has_next=paginate.has_next, images=paginate.items)

@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)

    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


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

@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    # 校验
    user = User.query.filter_by(username=username).first()
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage', u'用户名和密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/regloginpage', u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update(password + user.salt)
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage', u'密码错误', 'reglogin')

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')



@app.route('/reg/', methods={'post', 'get'})
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

    login_user(user)

    return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name

@app.route('/upload/', methods={'post'})
def upload():
    # print type(request.files)
    file = request.files['file']
    # dir(file)
    file.ext = ''

    if file.filename.find('.') > 0:
        file.ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file.ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file.ext
        url = save_to_local(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)

@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)

@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code": 0, "id": comment.id,
                       "content": comment.content,
                       "username": comment.user.username,
                       "user_id": comment.user_id})
