import urllib.parse
import shutil
import tempfile
from flask import Flask, render_template, send_file, session, redirect, url_for, request, send_from_directory, abort, flash, jsonify
from Utils import get_contents, Sort, size_of_dir, size_human_readable, num_of_items
import os, uuid
import time
import zipfile
import Utils

class FlaskApp:
    # Class to share a directory over the internet
    # directory: The directory to share
    # password: The password to access the shared directory
    # host: The host object to log messages to
    def __init__(self, config, logger=None):
        self.logger = logger
        self.app = Flask(__name__)
        self.app.config.update(SESSION_PERMANENT=False,SESSION_COOKIE_SECURE=True)
        self.app.secret_key = os.urandom(24)
        self.login_token = os.urandom(100)
        self.config = config
        self.setup_routes()

    def send_notification(self, message, category='info'):
        """
        Sends a notification to the frontend.
        :param message: The notification message to display.
        :param category: The category of the message (e.g., 'info', 'success', 'error').
        """
        flash(message, category)
        #self.log(f"Notification sent: {message}")

    # Method to log messages to the host object or print them to the console
    def log(self, message):
        if not message:
            return

        user_id = session.get('user_id', 'Unknown User')

        if self.logger:
            self.logger(f"[User {user_id}] {message}")
        else:
            print(f"[User {user_id}] {message}")

    def assign_user_id(self):
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())[:8]  # usng the first 8 characters of UUID

    # Setup the routes for the Flask app
    def setup_routes(self):
        self.app.before_request(self.assign_user_id)
        self.app.add_url_rule('/FolderDrop-icon.svg', 'favicon', self.favicon)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/', 'index', self.index, methods=['GET', 'POST'])
        self.app.add_url_rule('/<path:subpath>', 'index', self.index, methods=['GET', 'POST'])

        self.app.add_url_rule('/download_folder', 'download_folder', self.download_folder)
        self.app.add_url_rule('/delete', 'delete', self.delete)
        self.app.add_url_rule('/rename', 'rename', self.rename)
        self.app.add_url_rule('/create_folder', 'create_folder', self.create_folder)

        self.app.add_url_rule('/multi_delete', 'multi_delete', self.multi_delete, methods=['POST'])
        self.app.add_url_rule('/multi_download', 'multi_download', self.multi_download, methods=['POST'])

    # Route to serve the favicon
    def favicon(self):
        return send_from_directory(os.path.join(self.app.root_path , 'static'), 'FolderDrop-icon.svg')

    # Route to login to the shared directory
    def login(self):
        if request.method == 'POST':
            time.sleep(1)
            if self.config['password'].encode('utf-8') == request.form["password"].encode('utf-8'):
                self.log("Correct password entered.")
                session['logged_in'] = self.login_token
                return redirect(url_for('index'))
            else:
                self.log("Incorrect password entered.")
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
            dir_size= size_of_dir(full_path)
            items = num_of_items(full_path)
            readable = size_human_readable(dir_size)
            max_size_human = size_human_readable(int(self.config['max_size']))

            shared_size = f"{Utils.size_human_readable(Utils.size_of_dir(self.config['directory']))}"

            return render_template('index.html', files=get_contents(full_path, session['Sort']), subpath=subpath, parent_subpath=parent_subpath, dir_size=readable, num_of_items=items, max_size=max_size_human, shared_size=shared_size)

        elif os.path.isfile(full_path):
            return send_from_directory(self.config['directory'], subpath, as_attachment=True)
        else:
            # Handle invalid paths
            self.log(f"Invalid path requested: {full_path}")
            return redirect(url_for('index'))

    # TODO: route http to https
    # Route to serve the shared directory
    def index(self, subpath=''):
        if self.config["password"] and session.get('logged_in') != self.login_token:
            return redirect(url_for('login'))
        if not session.get('Sort'):
            session['Sort'] = Sort.SIZE_DESCENDING

        if request.method == 'GET':
            return self.respond(subpath)
        elif request.method == 'POST':
            if 'file' in request.files and self.config['uploading']:
                file = request.files['file']
                if file.filename != '':
                    safe_path = os.path.normpath(file.filename).replace('\\', '/')
                    full_path = os.path.join(self.config['directory'], subpath, safe_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    file.save(full_path)
                    return self.respond(subpath)

            if request.form["Sort"] == 'Name':
                session['Sort'] = session['Sort']%2 + Sort.NAME_ASCENDING
            elif request.form["Sort"] == 'Size':
                session['Sort'] = session['Sort']%2 + Sort.SIZE_ASCENDING
            elif request.form["Sort"] == 'Last modified':
                session['Sort'] = session['Sort']%2 + Sort.DATE_ASCENDING
            return self.respond(subpath)
        abort(404)

    # Route to download a folder as a zip file
    # folder_path: The path to the folder to download
    # Returns a zip file for download
    # If the folder path is invalid, it will return a 404 error
    def download_folder(self):
        folder_path = request.args.get('path')
        folder_path = os.path.join(self.config['directory'], folder_path.lstrip('/'))
        folder_path = urllib.parse.unquote(folder_path)

        if not os.path.isdir(folder_path):
            self.log(f"Invalid folder path: {folder_path}")
            return abort(404)

        # Create a temporary zip file from the folder
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_filename = tmp_zip.name

        # Create the zip archive
        shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', folder_path)

        # Serve the zip file for download
        return send_from_directory(os.path.dirname(zip_filename), os.path.basename(zip_filename), as_attachment=True)

    # Route to delete a file or folder
    # path: The path to the file or folder to delete
    # If the path is invalid, it will return a 404 error
    # If the deletion is successful, it will redirect to the parent directory
    # If the deletion is not allowed, it will return the parent path index page
    def delete(self):
        # TODO: Remove delete button from user interface if deleting is not allowed
        path = request.args.get('path')
        if self.config['deleting'] == True:
            if not path:
                self.log("Deletion failed. No path provided.")
                return redirect(url_for('index'))

            # Decode the URL-encoded path
            path = urllib.parse.unquote(path)
            path = os.path.join(self.config['directory'], path.lstrip('/'))

            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.log(f"Deleted: {path}")
                self.send_notification(f"Deleted: {path}", 'success')
            else:
                self.log(f"Deletion failed. Path not found: {path}")
                self.send_notification(f"Deletion failed. Path not found: {path}", 'error')
        else:
            self.log("Deletion failed. Deleting files and folders is not allowed.")
            self.send_notification("Deletion failed. Deleting files and folders is not allowed.", 'error')

        # Redirect to the parent directory
        parent_path = os.path.dirname(path)
        if parent_path != self.config['directory']:
            return self.respond(parent_path)
        else:
            # If the parent path is the root directory, redirect to the index page
            return redirect(url_for('index'))


    def rename(self):
        path = request.args.get('path')
        new_path = request.args.get('new_path')
        if not path or not new_path:
            self.log("Renaming failed. No path provided.")
            return redirect(url_for('index'))

        # Decode the URL-encoded path
        path = urllib.parse.unquote(path)
        path = os.path.join(self.config['directory'], path.lstrip('/'))

        new_path = urllib.parse.unquote(new_path)
        new_path = os.path.join(self.config['directory'], new_path.lstrip('/'))

        if not os.path.isdir(path):
            extension = path.split(".")[-1]
            new_path = f"{new_path}.{extension}"

        print(path)
        print(new_path)
        if os.path.exists(path):
            os.rename(path, new_path)
            self.send_notification(f"Renamed: {new_path}", 'success')
        else:
            self.send_notification(f"Renaming failed. Path not found: {path}", 'error')

        parent_path = os.path.dirname(new_path)
        if parent_path != self.config['directory']:
            subpath = os.path.relpath(parent_path, self.config['directory'])
            return redirect(url_for('index', subpath=subpath))
        else:
            # If the parent path is the root directory, redirect to the index page
            return redirect(url_for('index'))

    # Route to create new folder
    # folder_path: The path with a name of the new folder to create
    # Returns a 404 error if the folder already exists
    # If the folder name is invalid,  returns a 404 error
    def create_folder(self):
        folder_path = request.args.get('path')
        parent_path = os.path.dirname(folder_path)
        if not folder_path:
            self.log("Folder creation failed. No path provided.")
            return redirect(url_for('index'))

        # Decode the URL-encoded path
        folder_path = urllib.parse.unquote(folder_path)
        folder_path = os.path.join(self.config['directory'], folder_path.lstrip('/'))

        if os.path.exists(folder_path):
            self.log(f"Folder creation failed. Path already exists: {folder_path}")
            self.send_notification(f"Folder creation failed. Path already exists: {folder_path}", 'error')
            return self.respond(parent_path)

        try:
            os.makedirs(folder_path)
            self.log(f"Created folder: {folder_path}")
            self.send_notification(f"Created folder: {folder_path}", 'success')
        except Exception as e:
            self.log(f"Folder creation failed: {e}")
            self.send_notification(f"Folder creation failed: {e}", 'error')

        # Redirect to the parent directory
        if parent_path != self.config['directory']:
            return self.respond(parent_path)
        else:
            # If the parent path is the root directory, redirect to the index page
            return redirect(url_for('index'))

    # Route to download multiple files as a zip file
    # paths: A list of file paths to download
    # Returns a zip file for download
    # If the paths are invalid, it will return a 404 error
    def multi_download(self):
        data = request.get_json(force=True, silent=True) or {}
        paths = data.get('paths', [])
        if not paths:
            return jsonify({'success': False, 'message': 'No files selected'}), 400

        self.log(f"multi_download request.json: {data}")

        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_filename = tmp_zip.name

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for rel_path in paths:
                abs_path = os.path.join(self.config['directory'], rel_path.lstrip('/'))
                if os.path.exists(abs_path):
                    arcname = os.path.basename(abs_path)
                    zipf.write(abs_path, arcname=arcname)

        return send_file(zip_filename, as_attachment=True, download_name="selected_files.zip")
    
    # Route to delete multiple files and folders
    # paths: A list of file and folder paths to delete
    # Returns a JSON response with the status of the deletions
    def multi_delete(self):
        if not self.config['deleting']:
            self.send_notification("Deleting files and folders is not allowed.", 'error')
            return jsonify({'success': False, 'message': 'Deleting not allowed'}), 403

        self.log(f"multi_delete request.json: {request.json}")

        paths = request.json.get('paths', [])
        deleted = []
        errors = []

        for rel_path in paths:
            path = os.path.join(self.config['directory'], rel_path.lstrip('/'))
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    deleted.append(rel_path)
                except Exception as e:
                    errors.append({'path': rel_path, 'error': str(e)})
            else:
                errors.append({'path': rel_path, 'error': 'Not found'})

        if deleted:
            self.send_notification(f"Deleted: {', '.join(deleted)}", 'success')
        if errors:
            self.send_notification(f"Some deletions failed.", 'error')

        return jsonify({'success': True, 'deleted': deleted, 'errors': errors})
    