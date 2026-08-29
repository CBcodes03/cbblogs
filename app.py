import verify
import time
import os
from flask import Flask,render_template, url_for, request, session, flash, redirect, g, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
from flask_bcrypt import Bcrypt
from flask import session
from flask import send_file, abort
import os
import mysql.connector

#functions
conn = mysql.connector.connect(
    host="localhost",
    user="chirag",
    password="12345678",
    database="blogdb"
)
cursor = conn.cursor()
def setupdb():
    try:
        try:
            create_db='CREATE DATABASE blogdb'
            cursor.execute(create_db)
        except:
            print("database already exist!!")
        createusertable = '''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB;
        '''
        posts = '''
        CREATE TABLE IF NOT EXISTS posts (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title TEXT NOT NULL,
            publish_date DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        '''
        post_sections = '''
        CREATE TABLE IF NOT EXISTS post_sections (
            id INT PRIMARY KEY AUTO_INCREMENT,
            post_id INT NOT NULL,
            section_type ENUM('heading','subheading','text','code','image','video') NOT NULL,
            content TEXT,
            file_path VARCHAR(255),
            position INT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        '''
        createcomment = '''
        CREATE TABLE IF NOT EXISTS comments (
            id INT PRIMARY KEY AUTO_INCREMENT,
            pid INT NOT NULL,
            user VARCHAR(255) NOT NULL,
            body TEXT NOT NULL,
            publish_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pid) REFERENCES posts(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        '''
        createfavtable='''
        CREATE TABLE IF NOT EXISTS favourites (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) NOT NULL,
            post_id INT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;'''
        cursor.execute(posts)
        cursor.execute(post_sections)
        cursor.execute(createusertable)
        cursor.execute(createcomment)
        cursor.execute(createfavtable)
        conn.commit()
    except FileNotFoundError:
        print("database already exist!!")
    return None

def getpostsections(pid):
    cursor.execute("""
        SELECT section_type, content, file_path
        FROM post_sections
        WHERE post_id=%s
        ORDER BY position
    """, (pid,))
    sections = cursor.fetchall()
    return sections

def get_all_users():
    query="Select * from users;"
    cursor.execute(query)
    result=cursor.fetchall()
    return result

def create_user(un, ue, up):
    createuser = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s);"
    cursor.execute(createuser, (un, ue, up))
    conn.commit()
    return None

def create_posts(title,imagepath,body):
    putpost = "INSERT INTO posts (title, imagepath, body) VALUES (%s, %s, %s);"
    cursor.execute(putpost, (title, imagepath, body))
    cursor.execute("SELECT last_insert_rowid()")
    pid=cursor.fetchone()
    pid=str(pid[0])
    return pid

def create_comment(pid,username,cbody):
    addcomment = """
    INSERT INTO comments (pid, user, body, publish_date)
    VALUES (%s, %s, %s, NOW());
    """

    cursor.execute(addcomment, (pid, username, cbody))
    conn.commit()
    return None

def create_user_session(un,ue,up):
    session['current_user'] = {'username':un,'email':ue,'password':up, 'is_admin': is_admin(un)}

def auth(ee,ep=None):
    cursor.execute('SELECT * FROM users WHERE email=\'{}\''.format(ee))
    res=cursor.fetchone()
    return res

def checkusername(eu):
    cursor.execute('SELECT * FROM users WHERE name=\'{}\''.format(eu))
    res=cursor.fetchone()
    return res

def fetchposts_with_sections():
    cursor.execute('SELECT * FROM posts ORDER BY publish_date DESC LIMIT 3')
    posts = cursor.fetchall()

    posts_with_sections = []
    for post in posts:
        cursor.execute('SELECT * FROM post_sections WHERE post_id=%s', (post[0],))
        sections = cursor.fetchall()
        posts_with_sections.append((post, sections))  # tuple of post + its sections
    return posts_with_sections


def getpost(pid):
    cursor.execute('SELECT * FROM posts WHERE id = {}'.format(pid))
    post = cursor.fetchone()
    return post

def getcomments(pid):
    cursor.execute('SELECT * FROM comments WHERE pid = {}'.format(pid))
    res = cursor.fetchall()
    return res

def search_posts(query):
    # fetch posts (id, title) from your DB

    cursor.execute("SELECT id, title FROM posts")
    rows = cursor.fetchall()
    # make dict {title: id}
    posts_dict = {title: pid for pid, title in rows}

    # filter by query
    query = query.lower()
    results = {title: pid for title, pid in posts_dict.items() if query in title.lower()}

    return results

def is_admin(username):
    cursor.execute("SELECT is_admin FROM users WHERE name = %s", (username,))
    row = cursor.fetchone()
    return bool(row[0]) if row else False

def get_favourites(username):
    # Placeholder logic for favourites
    cursor.execute("""
        SELECT p.id, p.title
        FROM posts p
        JOIN favourites f ON p.id = f.post_id
        WHERE f.username = %s
    """, (username,))
    favourites = cursor.fetchall()
    return favourites

#globals

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = './templates/static/postimages'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}
STATIC_DIR = os.path.join(app.root_path, "templates/static/postimages")

#routes here
@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    posts = fetchposts_with_sections()

    if query:
        posts = [
            (post, sections) for post, sections in posts
            if query.lower() in post[1].lower()  # search in title
        ]

    posts = fetchposts_with_sections()
    return render_template('index.html', posts=posts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        ee=request.form['email']
        ep=request.form['password']
        row=auth(ee,ep)
        print(row)
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
    pquery="DELETE FROM comments where id = '{}'".format(id)
    cursor.execute(pquery)
    conn.commit()
    return redirect(request.referrer)

@app.route('/del_post/<int:pid>', methods=['POST'])
def del_post(pid):
    # 1. Get all media file paths linked to the post
    cursor.execute("SELECT file_path FROM post_sections WHERE post_id = %s", (pid,))
    file_paths = cursor.fetchall()

    for fp in file_paths:
        if fp and fp[0]:  # ensure not None
            if os.path.isfile(fp[0]):  # delete actual file
                os.remove(fp[0])

    # 2. Delete all post sections
    cursor.execute("DELETE FROM post_sections WHERE post_id = %s", (pid,))

    # 3. Delete all comments for the post
    cursor.execute("DELETE FROM comments WHERE pid = %s", (pid,))

    # 4. Delete the post itself
    cursor.execute("DELETE FROM posts WHERE id = %s", (pid,))

    conn.commit()

    flash("Post deleted successfully!", "success")
    return redirect(url_for('index'))

#admin here
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == "GET":
        if 'current_user' in session:
            if is_admin(session['current_user']['username']):
                return render_template('admin.html', a=True)
        return redirect(url_for('index'))

    if request.method == "POST":
        try:
            title = request.form['title']
            # 1. Create post entry
            cursor.execute("INSERT INTO posts (title) VALUES (%s)", (title,))
            post_id = cursor.lastrowid   # MySQL way

            # 2. Loop over dynamic text sections
            position = 0
            for key in request.form:
                if key.startswith("sections["):
                    section = request.form[key]
                    if not section.strip():
                        continue

                    if "][heading]" in key:
                        section_type = "heading"
                    elif "][subheading]" in key:
                        section_type = "subheading"
                    elif "][text]" in key:
                        section_type = "text"
                    elif "][code]" in key:
                        section_type = "code"
                    else:
                        continue

                    cursor.execute(
                        "INSERT INTO post_sections (post_id, section_type, content, position) VALUES (%s, %s, %s, %s)",
                        (post_id, section_type, section, position)
                    )
                    position += 1

            # 3. Handle uploaded files
            for key in request.files:
                if key.startswith("sections["):
                    file = request.files[key]
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)

                        if "][image]" in key:
                            section_type = "image"
                        elif "][video]" in key:
                            section_type = "video"
                        else:
                            continue

                        cursor.execute(
                            "INSERT INTO post_sections (post_id, section_type, file_path, position) VALUES (%s, %s, %s, %s)",
                            (post_id, section_type, file_path, position)
                        )
                        position += 1

            # --- COMMIT ---
            conn.commit()

            flash("Post created successfully!", "success")
            return redirect(url_for('admin'))

        except Exception as e:
            conn.rollback()
            print("Post creation failed:", e)
            flash("Something went wrong. Post was NOT saved.", "danger")
            return redirect(url_for('admin'))

        
@app.route('/image')
def get_image():
    filename = request.args.get('filename')

    if not filename:
        abort(404)

    # If absolute/relative full path exists, send directly
    if os.path.exists(filename):
        return send_file(filename)

    # Otherwise, try static folder
    if "/" not in filename:
        static_path = os.path.join(STATIC_DIR, filename)
        if os.path.exists(static_path):
            return send_from_directory(STATIC_DIR, filename)

    abort(404)


@app.route('/video')
def get_video():
    filename = request.args.get('filename')

    if not filename:
        abort(404)

    if os.path.exists(filename):
        return send_file(filename)

    if "/" not in filename:
        static_path = os.path.join(STATIC_DIR, filename)
        if os.path.exists(static_path):
            return send_from_directory(STATIC_DIR, filename)

    abort(404)

@app.route('/post<int:pid>', methods=["POST", "GET"])
def gotopost(pid):
    post = getpost(pid)  # fetch (id, title, publish_date)
    sections = getpostsections(pid)  # fetch all sections from post_sections
    cmnts = getcomments(pid)
    print(sections)
    if request.method == "POST":
        un = session.get('current_user', {}).get('username')
        body = request.form.get('body')
        if un and body:
            create_comment(pid, un, body)
            cmnts = getcomments(pid)

    return render_template('blogs.html', post=post, sections=sections, comments=cmnts)

@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = search_posts(query)  # your dict logic
    return jsonify(results)

@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template('forgot.html')
    
    if request.method == "POST":
        email = request.form['email']
        row = auth(email)  # check if email exists

        if not row:
            flash("No account found with this email.", category='error')
            return redirect(url_for('forgot'))

        otp = verify.genotp()
        verify.send_vmail(otp, email)

        # Save OTP and email temporarily in session
        session['reset'] = {'email': email, 'otp': otp, 'step': 'otp_sent'}
        flash("OTP sent to your email.", category='info')
        return redirect(url_for('reset_verify'))


@app.route('/reset_verify', methods=["GET", "POST"])
def reset_verify():
    # Check if the user came from the /forgot step
    if 'reset' not in session or session['reset'].get('step') != 'otp_sent':
        flash("Unauthorized access. Please start again.", category='error')
        return redirect(url_for('forgot'))

    if request.method == "GET":
        return render_template('reset_verify.html')
    
    if request.method == "POST":
        entered_otp = request.form['otp']

        if entered_otp == str(session['reset']['otp']):
            session['reset']['step'] = 'otp_verified'
            flash("OTP verified! Please set your new password.", category='success')
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Try again.", category='error')
            return redirect(url_for('reset_verify'))


@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    # Ensure user verified OTP before accessing this page
    if 'reset' not in session or session['reset'].get('step') != 'otp_verified':
        flash("Unauthorized access. Please start again.", category='error')
        return redirect(url_for('forgot'))

    if request.method == "GET":
        return render_template('reset_password.html')
    
    if request.method == "POST":
        new_pass = request.form['password']
        confirm_pass = request.form['confirm_password']

        if new_pass != confirm_pass:
            flash("Passwords do not match!", category='error')
            return redirect(url_for('reset_password'))

        email = session['reset']['email']

        # Hash new password
        bcrypt = Bcrypt(app)
        hashed_pass = bcrypt.generate_password_hash(new_pass).decode('utf-8')

        cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_pass, email))
        conn.commit()

        session.pop('reset', None)
        flash("Password reset successful! Please login.", category='success')
        return redirect(url_for('login'))

@app.route('/favourites',methods=["GET"])
def favourites():
    if request.method == "GET":
        if session.get('current_user'):
            user = session['current_user']
            favourites = get_favourites(user['username'])
            print(favourites)
            return render_template('favourites.html', favourites=favourites)
        else:
            flash("Please login to view your favourites.", category='error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))

@app.route('/add_favourite/<int:post_id>', methods=['POST'])
def add_favourite(post_id):
    if session.get('current_user'):
        user = session['current_user']
        username = user['username']
        try:
            cursor.execute("SELECT * FROM favourites WHERE username = %s AND post_id = %s", (username, post_id))
            existing = cursor.fetchone()
            if existing:
                flash("Post already in favourites!", category='info')
                return redirect(
                    request.args.get("next") or request.referrer or "/"
                )
        except Exception as e:
            print("Error checking existing favourite:", e)
            flash("An error occurred. Please try again.", category='error')
            return redirect(
                request.args.get("next") or request.referrer or "/"
            )
        cursor.execute("INSERT INTO favourites (username, post_id) VALUES (%s, %s)", (username, post_id))
        conn.commit()
        flash("Post added to favourites!", category='success')
    else:
        flash("Please login to add favourites.", category='error')
    return redirect(
        request.args.get("next") or request.referrer or "/"
    )

@app.route('/remove_favourite/<int:pid>', methods=['GET'])
def remove_favourite(pid):
    if session.get('current_user'):
        user = session['current_user']
        username = user['username']
        cursor.execute("DELETE FROM favourites WHERE username = %s AND post_id = %s", (username, pid))
        conn.commit()
        flash("Post removed from favourites!", category='success')
    else:
        flash("Please login to remove favourites.", category='error')
    return redirect(request.referrer or url_for('favourites'))

if __name__ == '__main__':
    setupdb()
    app.run(debug=True) 
