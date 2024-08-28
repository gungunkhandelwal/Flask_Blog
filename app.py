from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import json

with open('config.json','r') as c:
    params=json.load(c)["params"]

local_server=True
app=Flask(__name__)
app.secret_key = 'secret-key'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    date=db.Column(db.String(12),nullable=True)
    phone_no = db.Column(db.String(12),nullable=False)
    message = db.Column(db.String(200),nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    description = db.Column(db.String(500),nullable=False)
    date=db.Column(db.String(12),nullable=True)
    img_file = db.Column(db.String(12),nullable=False)
    slug=db.Column(db.String(12))

@app.route('/')
def home():
    posts=Post.query.filter_by().all()[0:params['number_of_post']]
    return render_template('index.html',params=params,posts=posts)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if "user" in session and session['user']==params['admin_user']:
        posts = Post.query.all()
        return render_template("dashboard.html",posts=posts,params=params)
    
    if request.method == 'POST':
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            posts = Post.query.all()
            return render_template('dashboard.html',posts=posts,params=params)
    else:
        return render_template('login.html',params=params)
    
@app.route('/add_post',methods=['GET','POST'])
def add_post():
    if "user" in session and session['user']==params['admin_user']:
        if request.method =='POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            description = request.form.get('description')
            img_file = request.form.get('img_file')
            date = datetime.now()
            post=Post(title=box_title, slug=slug,description=description,img_file=img_file,date=date)
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        return render_template('add_post.html')
    return redirect('/dashboard')
    
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        phone_no=request.form.get('phone_no')
        message=request.form.get('message')
        entry=Contact(name=name,email=email,date=datetime.now(),phone_no=phone_no,message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>/",methods=['GET'])
def post_route(post_slug):
    posts=Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=posts,params=params)


@app.route("/edit/<string:id>/" , methods=['GET', 'POST'])
def edit_post(id):
    if "user" in session and session['user']==params['admin_user']:
        if request.method=="POST":
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            description = request.form.get('description')
            img_file = request.form.get('img_file')
            date = datetime.now()
        
            if id=='0':
                post = Post(title=box_title, slug=slug,description=description, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(id=id).first()
                post.title = box_title
                post.slug = slug
                post.description = description 
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+id)
        else:
            post = Post.query.filter_by(id=id).first()
            return render_template('edit.html', params=params, post=post)
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=True)

