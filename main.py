from flask import Flask, jsonify, request, session
import sqlite3
from flask_sessionstore import Session


app = Flask(__name__)
app.config["DEBUG"] = True
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)


def get_db():
    conn = None
    try:
        conn = sqlite3.connect("blog.sqlite")
    except Exception as e:
        print(e)

    return conn


@app.route('/signup', methods=['POST'])
def signup():
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        name = request.form["user_name"]
        password = request.form["password"]
        cursor = cursor.execute(f"select * from User where user_name='{name}';")
        user = cursor.fetchall()
        if len(user) > 0:
            return "User already exist"
        sql = """insert into User (user_name,password) values (?, ?)"""
        cursor = cursor.execute(sql, (name, password,))
        db.commit()
        db.close()
        return f"user created"

    return "hello"


@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        name = request.form["user_name"]
        password = request.form["password"]
        query = f"select * from User where user_name='{name}' and password='{password}';"
        print(query)
        cursor = cursor.execute(f"select * from User where user_name='{name}' and password='{password}';")
        user = cursor.fetchall()
        if len(user) < 0:
            return "Invalid credentials"
        session["user_name"] = name
        return f"user login"

    return "hello"


@app.route('/logout', methods=['POST'])
def logout():
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        session["user_name"] = None
        return f"user logout"

    return "hello"


@app.route('/user', methods=['GET', 'POST'])
def User():
    db = get_db()
    cursor = db.cursor()

    if request.method == "GET":
        cursor = cursor.execute("select * from User;")
        user_list = [
            dict(id=row[0], username=row[1], password=row[2]) for row in cursor.fetchall()
        ]

        if len(user_list) > 0:
            return jsonify(user_list)
        else:
            return "Nothing found"

    if request.method == "POST":
        name = request.form["user_name"]
        password = request.form["password"]
        cursor = cursor.execute(f"select * from User where user_name='{name}';")
        user = cursor.fetchall()
        if len(user) > 0:
            return "User already exist"
        sql = """insert into User (user_name,password) values (?, ?)"""
        cursor = cursor.execute(sql, (name, password,))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    return "hello"


@app.route('/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def UserAction(user_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == "GET":
        cursor = cursor.execute(f"select * from User where id={user_id};")
        row = cursor.fetchall()[0]
        user_list = dict(id=row[0], username=row[1], password=row[2])

        if len(user_list) > 0:
            return jsonify(user_list)
        else:
            return "Nothing found"

    if request.method == "PUT":
        name = request.form["user_name"]
        password = request.form["password"]
        sql = """update User set user_name=?, password=? where id=?"""
        cursor = cursor.execute(sql, (name, password, user_id))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    if request.method == "DELETE":
        sql = """delete from User where id=?"""
        cursor = cursor.execute(sql, (user_id,))
        db.commit()
        db.close()
        return f"deleted {user_id}"

    return "hello"


@app.route('/blog', methods=['GET', 'POST'])
def Blog():
    db = get_db()
    cursor = db.cursor()
    if not session.get("user_name"):
        return "you are not login"

    if request.method == "GET":
        cursor = cursor.execute("select * from Blog;")
        blog_list = [
            dict(title=row[0], subtitle=row[1], body=row[2], blogger=row[3], id=row[4]) for row in cursor.fetchall()
        ]

        if len(blog_list) > 0:
            return jsonify(blog_list)
        else:
            return "Nothing found"

    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        body = request.form["body"]
        blogger = request.form["blogger"]
        sql = """insert into Blog (title,subtitle,body,blogger) values (?, ?, ?, ?)"""
        cursor = cursor.execute(sql, (title, subtitle, body, blogger))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    return "hello"


@app.route('/blog/<int:blog_id>', methods=['GET', 'PUT', 'DELETE'])
def BlogAction(blog_id):
    db = get_db()
    cursor = db.cursor()
    if not session.get("user_name"):
        return "you are not login"

    if request.method == "GET":
        cursor = cursor.execute(f"select * from Blog inner join Comment on Blog.id=Comment.blog and Blog.id={blog_id};")
        rows = cursor.fetchall()
        if len(rows) < 1:
            return "Nothing found"
        blog_list = dict(title=rows[0][0], subtitle=rows[0][1], body=rows[0][2], blogger=rows[0][3], id=rows[0][4])
        blog_list["comments"] = [
            dict(
                body=row[5],
                commentor=row[6],
                blog=row[7],
                approved=True if row[8] != 0 else False,
                id=row[9]
            ) for row in rows
        ]

        if len(blog_list) > 0:
            return jsonify(blog_list)
        else:
            return "Nothing found"

    if request.method == "PUT":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        body = request.form["body"]
        blogger = request.form["blogger"]
        sql = """update Blog set title=?, subtitle=?, body=?, blogger=? where id=?"""
        cursor = cursor.execute(sql, (title, subtitle, body, blogger, blog_id))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    if request.method == "DELETE":
        sql = """delete from Blog where id=?"""
        cursor = cursor.execute(sql, (blog_id,))
        db.commit()
        db.close()
        return f"deleted {blog_id}"

    return "hello"


@app.route('/comment', methods=['GET', 'POST'])
def Comment():
    if not session.get("user_name"):
        return "you are not login"
    db = get_db()
    cursor = db.cursor()

    if request.method == "GET":
        cursor = cursor.execute("select * from Comment;")
        blog_list = [
            dict(
                body=row[0],
                commentor=row[1],
                blog=row[2],
                approved=True if row[3] != 0 else False,
                id=row[4]
            ) for row in cursor.fetchall()
        ]

        if len(blog_list) > 0:
            return jsonify(blog_list)
        else:
            return "Nothing found"

    if request.method == "POST":
        body = request.form["body"]
        commentor = request.form["commentor"]
        blog = request.form["blog"]
        approved = request.form.get("approved", 0)
        sql = """insert into Comment (body,commentor,blog,approved) values (?, ?, ?, ?)"""
        cursor = cursor.execute(sql, (body, commentor, blog, approved))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    return "hello"


@app.route('/comment/<int:comment_id>', methods=['GET', 'PUT', 'DELETE'])
def CommentAction(comment_id):
    if not session.get("user_name"):
        return "you are not login"
    db = get_db()
    cursor = db.cursor()

    if request.method == "GET":
        cursor = cursor.execute(f"select * from Comment where id={comment_id};")
        row = cursor.fetchall()[0]
        blog_list = dict(
                body=row[0],
                commentor=row[1],
                blog=row[2],
                approved=True if row[3] != 0 else False,
                id=row[4]
            )

        if len(blog_list) > 0:
            return jsonify(blog_list)
        else:
            return "Nothing found"

    if request.method == "PUT":
        body = request.form["body"]
        commentor = request.form["commentor"]
        blog = request.form["blog"]
        approved = request.form.get("approved", 0)
        sql = """update Comment set body=?, commentor=?, blog=?, approved=? where id=?"""
        cursor = cursor.execute(sql, (body, commentor, blog, approved, comment_id))
        db.commit()
        db.close()
        return f"done {cursor.lastrowid}"

    if request.method == "DELETE":
        sql = """delete from Comment where id=?"""
        cursor = cursor.execute(sql, (comment_id,))
        db.commit()
        db.close()
        return f"deleted {comment_id}"

    return "hello"


app.run()
