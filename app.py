from flask import Flask, render_template, request, redirect, session
import sqlite3, datetime

app = Flask(__name__)
app.secret_key = "brooks-secret"
DB = "blog.db"


# ---------- DB ----------

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- PAGES ----------

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/work')
def work():
    return render_template('work.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    conn = sqlite3.connect(DB)
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    conn = sqlite3.connect(DB)
    post = conn.execute('SELECT * FROM posts WHERE id=?',(id,)).fetchone()
    conn.close()
    return render_template('post.html', post=post)

# ---------- ADMIN ----------

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username']=='admin' and request.form['password']=='Brooks123':
            session['admin']=True
            return redirect('/admin')
    return render_template('admin/login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin/login')

    conn = sqlite3.connect(DB)
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('admin/dashboard.html', posts=posts)

@app.route('/admin/new', methods=['GET','POST'])
def new_post():
    if not session.get('admin'):
        return redirect('/admin/login')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = str(datetime.date.today())

        conn = sqlite3.connect(DB)
        conn.execute(
            'INSERT INTO posts(title,content,created_at) VALUES(?,?,?)',
            (title, content, date)
        )
        conn.commit()
        conn.close()

        return redirect('/admin')

    return render_template('admin/new_post.html')
@app.route("/admin/delete/<int:post_id>")
def delete_post(post_id):

    # only logged in admin
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- RUN ----------

if __name__ == '__main__':
    app.run(debug=True)
