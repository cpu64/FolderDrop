from flask import Flask, render_template, session, redirect, url_for, request
import argparse
import os

app = Flask(__name__)

password = "test".encode('utf-8')

# Secret key for session management (important for keeping track of user sessions)
app.secret_key = os.urandom(24) # Can be a string for testing purposes but should be random in production
# app.secret_key = "abc123" # For testing purposes

@app.route('/FolderDrop-icon.svg')
def favicon():
    return send_from_directory(os.path.join(app.root_path , 'static'), 'FolderDrop-icon.svg')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if password == request.form["password"].encode('utf-8'):
            session['logged_in'] = True  # Mark the user as logged in
            return redirect(url_for('index'))  # Redirect to the home page
        else:
            return render_template('login.html', error="Incorrect password, try again.")
    return render_template('login.html')

@app.route("/")
@app.route('/<path:subpath>')
def index(subpath=''):
    if password and not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to the login page if not logged in

    full_path = os.path.join(app.config['directory'], subpath)
    if os.path.isdir(full_path):
        return render_template('index.html', files=os.listdir(full_path), subpath=subpath)
    return render_template('index.html', files=os.listdir(app.config['directory']))


# run the application
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Specify the share directory. Default "./share"')
    args = parser.parse_args()
    app.config['directory'] = args.directory
    app.run(debug=True)
