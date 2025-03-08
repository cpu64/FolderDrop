from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, abort
import argparse
import os

app = Flask(__name__)

password = "test".encode('utf-8')

# Secret key for session management (important for keeping track of user sessions)
app.secret_key = os.urandom(24) # Can be a string for testing purposes but should be random in production
# app.secret_key = "abc123" # For testing purposes

def size_human_readable(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}YiB"

def size_of_dir(path: str):
    size = 0
    for path, dirs, files in os.walk(path):
        for f in files:
            size += os.path.getsize(os.path.join(path, f))
    return size

def get_contents(path: str):
    contents = []
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            size = size_human_readable(size_of_dir(os.path.join(path, f)))
            contents.append(('d', f, size))
        elif os.path.isfile(os.path.join(path, f)):
            size = size_human_readable(os.path.getsize(os.path.join(path, f)))
            contents.append(('f', f, size))
    return contents


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
        return render_template('index.html', files=get_contents(full_path), subpath=subpath)
    elif os.path.isfile(full_path):
        return send_from_directory(app.config['directory'], subpath, as_attachment=True)
    abort(404)


# run the application
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Specify the share directory. Default "./share"')
    args = parser.parse_args()
    app.config['directory'] = args.directory
    app.run(debug=True)
