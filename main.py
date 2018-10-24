from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def is_valid(self):

        if self.title and self.body:
            return True
        else:
            return False


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    # TODO Look-up the alternate way to whitelist
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect("/blog")


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    error = {"user_error": "", "pass_error": "", "verify_error": ""}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "":
            error["user_error"] = "Username cannot be blank"
        if password == "":
            error["pass_error"] = "Password cannot be blank"
        elif len(password) < 2:
            error["pass_error"] = "Password must be more than two characters long"
        else:
            if password != verify:
                error["verify_error"] = "Password and Verify must match"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error["user_error"] = "There is already somebody with that username"
        if (
            error["user_error"] == "" and
            error["pass_error"] == "" and
            error["verify_error"] == ""
            ):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect('/')
        else:
            # TODO - user better response messaging
            # Trying out flash and error handler
            flash("There is already somebody with that username")
            error["user_error"] = "Username Taken, Try Another"
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/blog', methods=['GET', 'POST'])
def blog():

    blogs = Blog.query.all()
    blog_id = request.args.get('id')

    if blog_id:
        blog = Blog.query.get(blog_id)
        # title = blog.title
        # body = blog.body
        return render_template('blog_entry.html', blog=blog)
    else:
        blogs = Blog.query.all()
        # first of the pair matches to {{}} in for loop inblogs the .html
        # template, second of the pair matches to variable declared above
        return render_template('blogs.html', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        new_blog = Blog(new_title, new_body)

        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()

            return redirect("/blog?id=" + str(new_blog.id))
        else:
            flash("You must include a title and body for all new blog posts.")
            return render_template('newpost.html',
                                   title="Make a New Blog Post")

    else:
        return render_template('newpost.html', title="Make a New Blog Post")


if __name__ == '__main__':
    app.run(debug=True)
