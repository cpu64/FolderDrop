from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, abort
import argparse
import datetime
import os
import threading

class FolderDrop:
    def __init__(self, directory='./share'):
        self.app = Flask(__name__)
        self.app.config['directory'] = directory
        self.app.secret_key = os.urandom(24)
        self.password = "test".encode('utf-8')
        self.server_thread = None

        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/FolderDrop-icon.svg', 'favicon', self.favicon)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/<path:subpath>', 'index', self.index)

    def size_human_readable(self, size):
        for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
            if abs(size) < 1024.0:
                return f"{size:3.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}YiB"

    def size_of_dir(self, path: str):
        size = 0
        for path, dirs, files in os.walk(path):
            for f in files:
                size += os.path.getsize(os.path.join(path, f))
        return size

    def get_contents(self, path: str):
        contents = []
        for f in os.listdir(path):
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path, f))).replace(microsecond=0).isoformat(' ')
            if os.path.isdir(os.path.join(path, f)):
                size = self.size_human_readable(self.size_of_dir(os.path.join(path, f)))
                contents.append(('d', f, size, mod_time))
            elif os.path.isfile(os.path.join(path, f)):
                size = self.size_human_readable(os.path.getsize(os.path.join(path, f)))
                contents.append(('f', f, size, mod_time))
        return contents

    def favicon(self):
        return send_from_directory(os.path.join(self.app.root_path , 'static'), 'FolderDrop-icon.svg')

    def login(self):
        if request.method == 'POST':
            if self.password == request.form["password"].encode('utf-8'):
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Incorrect password, try again.")
        return render_template('login.html')

    def index(self, subpath=''):
        if self.password and not session.get('logged_in'):
            return redirect(url_for('login'))

        full_path = os.path.join(self.app.config['directory'], subpath)
        if os.path.isdir(full_path):
            return render_template('index.html', files=self.get_contents(full_path), subpath=subpath)
        elif os.path.isfile(full_path):
            return send_from_directory(self.app.config['directory'], subpath, as_attachment=True)
        abort(404)

    def run(self):
        self.server_thread = threading.Thread(target=self.app.run, kwargs={'debug': True, 'use_reloader': False})
        self.server_thread.start()

    def stop(self):
        if self.server_thread:
            os._exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Specify the share directory. Default "./share"')
    args = parser.parse_args()
    folderdrop = FolderDrop(directory=args.directory)
    folderdrop.run()