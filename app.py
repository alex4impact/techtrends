import sqlite3
import logging

from flask import Flask, json, render_template, request, url_for, redirect, flash

# global variable to count amount of connections made to the db
db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # This variable makes reference to the global variable within the function 
    # and adds 1 each time the function is called to present the amount of times 
    # a connection to the database has been established in the metrics endpoint 
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('Article not existent')
        return render_template('404.html'), 404
    else:
        title = post['title']
        app.logger.info(f'Article retrieved: { title }')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page request successfull')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            app.logger.info(f'Article: {title}')
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# return the status of the application
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

# return metrics related to amount of articles and live connections to the database
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    count_posts = connection.execute('SELECT COUNT(id) FROM posts').fetchone()
    connection.close()
    data = {
        "db_connection_count":db_connection_count,
        "post_count":[row for row in count_posts][0]
    }
    response = app.response_class(
            response = json.dumps(data),
            status=200,
            mimetype='application/json'
    )

    return response


# start the application on port 3111
if __name__ == "__main__":
    ## stream logs to a file 
    ## each time an existing article is retrieved, the title is recorded in the log line
    ## each time a non-existing article is acessed and a 404 page is returned
    ## each time the "About Us" page is retrieved
    ## each time a new article is created, the title is recorded in the log line
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p - -', filename='app.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
