from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, abort
from flask_session import Session
from Utils import get_contents, Sort
import os

class FlaskApp:
    # Class to share a directory over the internet
    # directory: The directory to share
    # password: The password to access the shared directory
    # host: The host object to log messages to
    def __init__(self, config):
        self.app = Flask(__name__)
        self.app.config.update(SESSION_PERMANENT=False,SESSION_TYPE="filesystem")
        self.app.secret_key = os.urandom(24)
        self.config = config
        self.setup_routes()

    # Setup the routes for the Flask app
    def setup_routes(self):
        self.app.add_url_rule('/FolderDrop-icon.svg', 'favicon', self.favicon)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/', 'index', self.index, methods=['GET', 'POST'])
        self.app.add_url_rule('/<path:subpath>', 'index', self.index, methods=['GET', 'POST'])

    # Route to serve the favicon
    def favicon(self):
        return send_from_directory(os.path.join(self.app.root_path , 'static'), 'FolderDrop-icon.svg')

    # Route to login to the shared directory
    def login(self):
        if request.method == 'POST':
            if self.config['password'].encode('utf-8') == request.form["password"].encode('utf-8'):
                # self.host.log("Correct password entered.")
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                # self.host.log("Incorrect password entered.")
                return render_template('login.html', error="Incorrect password, try again.")
        return render_template('login.html')

    # Route to respond to requests for the shared directory
    # subpath: The path to the requested file or directory
    # Returns a rendered HTML template for directories or a file download for files
    # If the requested path is a directory, it will return a list of files and directories in that directory
    # If the requested path is a file, it will return the file for download
    # If the requested path is not found, it will return a 404 error
    def respond(self, subpath):
        full_path = os.path.join(self.config['directory'], subpath)
        parent_subpath = '/'.join(subpath.split('/')[:-1]) if subpath else '' # Compute parent directory path

        if os.path.isdir(full_path):
            return render_template('index.html', files=get_contents(full_path, session['Sort']), subpath=subpath, parent_subpath=parent_subpath)
        elif os.path.isfile(full_path):
            return send_from_directory(self.config['directory'], subpath, as_attachment=True)

    # Route to serve the shared directory
    def index(self, subpath=''):
        if self.config["password"] and not session.get('logged_in'):
            return redirect(url_for('login'))
        if not session.get('Sort'):
            session['Sort'] = Sort.SIZE_DESCENDING

        if request.method == 'GET':
            return self.respond(subpath)
        elif request.method == 'POST':
            if request.form["Sort"] == 'Name':
                session['Sort'] = session['Sort']%2 + Sort.NAME_ASCENDING
            elif request.form["Sort"] == 'Size':
                session['Sort'] = session['Sort']%2 + Sort.SIZE_ASCENDING
            elif request.form["Sort"] == 'Modification Date':
                session['Sort'] = session['Sort']%2 + Sort.DATE_ASCENDING
            return self.respond(subpath)
        abort(404)

