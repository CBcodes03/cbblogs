import verify
import setup
import time
import os
from flask import Flask,render_template, url_for, request, session, flash, redirect, g, send_from_directory
from werkzeug.utils import secure_filename
from io import BytesIO
from flask_bcrypt import Bcrypt
import sqlite3
from flask import session
#functions
def setupdb():
    try:
        with open('cbblogs.db', 'r'):
            print(f"{'cbblogs.db'} already exists.")
    except FileNotFoundError:
        with sqlite3.connect('cbblogs.db') as conn:
            print(f"{'cbblogs.db'} created successfully.")
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    createusertable='''
                    CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email EMAIL NOT NULL,
                        password TEXT NOT NULL
                    );
                '''
    cre8postable='''
                CREATE TABLE IF NOT EXISTS posts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    publish_date TEXT DEFAULT (DATETIME('now')),
                    imagepath TEXT NOT NULL,
                    body TEXT NOT NULL
                );
                '''
    createcomment='''
            CREATE TABLE IF NOT EXISTS comments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid INTEGER NOT NULL,
                user TEXT NOT NULL,
                body TEXT NOT NULL,
                publish_date TEXT DEFAULT (DATETIME('now')),
                FOREIGN KEY (pid) REFERENCES posts(id)
            );
            '''
    cursor.execute(cre8postable)
    cursor.execute(createusertable)
    cursor.execute(createcomment)
    conn.commit()
    conn.close()
    return None


def create_user(un, ue, up):
    conn = sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    createuser = "INSERT INTO users (name, email, password) VALUES (?, ?, ?);"
    cursor.execute(createuser, (un, ue, up))
    conn.commit()
    conn.close()
    return None

def create_posts(title,imagepath,body):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    putpost = "INSERT INTO posts (title, imagepath, body) VALUES (?, ?, ?);"
    cursor.execute(putpost, (title, imagepath, body))
    cursor.execute("SELECT last_insert_rowid()")
    pid=cursor.fetchone()
    pid=str(pid[0])
    conn.commit()
    conn.close
    return pid

def create_comment(pid,username,cbody):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    addcomment='''INSERT INTO comments (pid, user, body, publish_date)
                    VALUES
                    ('{}', '{}', '{}',DATETIME('now')); 
                '''.format(pid,username,cbody)
    cursor.execute(addcomment)
    conn.commit()
    conn.close
    return None

def create_user_session(un,ue,up):
    session['current_user'] = {'username':un,'email':ue,'password':up}

def auth(ee,ep=None):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=\'{}\''.format(ee))
    res=cursor.fetchone()
    return res

def checkusername(eu):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name=\'{}\''.format(eu))
    res=cursor.fetchone()
    return res

def fetchposts():
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts=cursor.fetchall()
    return posts

def getpost(pid):
    conn = sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = {}'.format(pid))
    post = cursor.fetchone()
    return post

def getcomments(pid):
    conn = sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comments WHERE pid = {}'.format(pid))
    res = cursor.fetchall()
    return res
#globals
if not os.path.exists('./cbblogs.db'):
    setupdb()
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = './templates/static/postimages'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

#routes here
@app.route('/')
def index():
    res=fetchposts()
    return render_template('index.html',posts=res)

@app.route('/blog')
def blog():
    return render_template('blogs.html')


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        ee=request.form['email']
        ep=request.form['password']
        row=auth(ee,ep)
        if row:
            if bcrypt.check_password_hash(row[3], ep):
                create_user_session(row[1],row[2],row[3])
                username=row[1]
                if username == 'admin':
                    return redirect(url_for('admin'))
                return redirect(url_for('index'))
            else:
                flash("incorrect password!")
                return redirect(url_for('login'))

        else:
            flash("user not found")
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('current_user')
    return redirect(url_for('index'))

@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        un = request.form['username']
        ve = request.form['email']
        pa = request.form['password']
        row = auth(ve)
        if row:
            flash("Email already in use!!!", category='error')
            return redirect(url_for('signup'))
        usr_valid = checkusername(un)
        if usr_valid:
            flash("Username is taken!!!", category='error')
            return redirect(url_for('signup'))
        geno = verify.genotp()
        print(geno)
        verify.send_vmail(geno, ve)
        session['verify'] = {'username': un, 'email': ve, 'password': pa, 'geno': geno}
        return redirect(url_for('sverify'))
    
@app.route('/signup/verify', methods=["POST", "GET"])
def sverify():
    if request.method == 'GET':
        return render_template('verify.html')
    if request.method == 'POST':
        otp = request.form.get('otp')
        verify_session = session.get('verify')
        if verify_session and str(otp) == str(verify_session.get('geno')):
            flash('Verification successful!', category='success')
            uname = verify_session.get('username')
            uemail = verify_session.get('email')
            upass = verify_session.get('password')
            pw_hash = bcrypt.generate_password_hash(upass).decode('utf-8')
            create_user(uname, uemail, pw_hash)
            time.sleep(2)
            session.pop('verify', None)
            return redirect(url_for('login'))
        else:
            flash('Verification failed!', category='error')
            time.sleep(2)
            return redirect(url_for('signup'))
        
@app.route('/del_comment/<int:id>', methods=['POST'])
def del_comment(id):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    pquery="DELETE FROM comments where id = '{}'".format(id)
    cursor.execute(pquery)
    conn.commit()
    conn.close()
    return redirect(request.referrer)

@app.route('/del_post/<int:pid>', methods=['POST'])
def del_post(pid):
    conn =  sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT imagepath FROM posts WHERE id = ?", (pid,))
    image_path = cursor.fetchone()
    image_path = str(image_path[0])
    if image_path:
        if os.path.isfile(f"./templates/static/postimages/{image_path}"):
            os.remove(f"./templates/static/postimages/{image_path}")  # Delete the image file from the folder
    pquery="DELETE FROM posts where id = '{}'".format(pid)
    cquery="DELETE FROM comments where pid = '{}'".format(pid)
    cursor.execute(pquery)
    cursor.execute(cquery)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
#admin here
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/admin',methods=["POST","GET"])
def admin():
    if request.method == "GET":
        if 'current_user' in session and session['current_user']['username'] == 'admin':
            #setup.pulling_func()
            return render_template('admin.html')
        else:
            return redirect(url_for('index'))
    if request.method == 'POST':
        title=request.form['title']
        body=request.form['body']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            res=create_posts(title,filename,body)
            link=url_for('gotopost', pid=res, _external=True)
            verify.new_post_notify(link)
            flash("post created!","sucess")
            setup.pushing_func()
            return redirect(url_for('admin'))
        else:
            flash("post not created file error","error")
            return redirect(url_for('admin'))
        
@app.route('/templates/static/postimages/<filename>')
def get_image(filename):
    return send_from_directory('./templates/static/postimages',filename)
        
@app.route('/post<pid>', methods=["POST", "GET"])
def gotopost(pid):
    res = getpost(pid)
    cmnts = getcomments(pid)
    if request.method == "POST":
        un = session.get('current_user', {}).get('username')
        body = request.form.get('body')
        if un and body:
            create_comment(pid, un, body)
            cmnts = getcomments(pid)  
    return render_template('blogs.html', post=res, comments=cmnts)

if __name__ == '__main__':
    app.run(debug=True) 