from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id =    db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body =  db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def is_valid(self):

        if self.title and self.body:
            return True
        else:
            return False

@app.route('/', methods=['GET', 'POST'])
def index():

    blogs = Blog.query.all()
    # completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('blogs.html',title="Build a Blog!", 
        blogs=blogs)


@app.route('/blog', methods=['GET', 'POST'])
def blog():

    # blog_id = Blog.query.get(blog.id)
    blog_id = request.args.get('id')

    if blog_id:
        blog = Blog.query.get(blog_id)
        # title = blog.title
        # body = blog.body
        return render_template('blog_entry.html', blog=blog)
    else:
        blogs = Blog.query.all()
        # first of the pair matches to {{}} in for loop inblogs the .html template, second of the pair matches to variable declared above
        return render_template('blogs.html', blogs=blogs)
        
@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        new_blog = Blog(new_title, new_body)
 
        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()
       
            # url = "/blog?id=" + str(new_blog.id)
            # return redirect(url)
            return redirect("/blog?id=" + str(new_blog.id))
            # return render_template('blog_entry.html', title=new_blog.title, body=new_blog.body)
        else:
            flash("You must include a title and body for all new blog posts.")
            return render_template('newpost.html', title="Make a New Blog Post")

    else:
        return render_template('newpost.html', title="Make a New Blog Post")

if __name__ == '__main__':
    app.run(debug=True)
