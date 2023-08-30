from hack import app, create_db, db
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, BlogForm
from hack.models import User, BlogPost
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

create_db(app)
app.config['UPLOAD_FOLDER'] = 'hack/static/thumbnails'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    blogs = BlogPost.query.filter_by(category='News').all() + BlogPost.query.filter_by(category='Fashion').all() + BlogPost.query.filter_by(category='Finance').all()
    featured = BlogPost.query.order_by(BlogPost.views.desc()).first()

    return render_template('index.html', blogs=blogs, featured=featured)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists'
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
    return render_template('reg.html', form=form, mess=mess)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = BlogForm()
    if form.validate_on_submit():
        thumbnail = request.files['thumbnail']
        if thumbnail and allowed_file(thumbnail.filename):
            filename = f"{secure_filename(thumbnail.filename)}"
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            thumbnail.save(thumbnail_path)
            
            # Create a new BlogPost entry
            new_post = BlogPost(
                thumbnail=filename,
                title=form.title.data,
                short_desc=form.short_desc.data,
                content=form.content.data,
                category=form.category.data,
                author=current_user.username
            )
            db.session.add(new_post)
            db.session.commit()

            print("Form data saved and thumbnail uploaded!")

    return render_template('post.html', form=form)

@app.route('/blogs/<id>')
def blogs(id):
    Blog = BlogPost.query.filter_by(id=id).first()
    Blog.views +=1 
    db.session.add(Blog)
    db.session.commit()
    return render_template('blog.html', blog=Blog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password.'
    return render_template('login.html', mess=mess, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
