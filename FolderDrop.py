from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory, abort
import argparse
import datetime
import os
import threading
import igd
import curio
import socket

class FolderDrop:
    # Class to share a directory over the internet
    # directory: The directory to share
    # password: The password to access the shared directory
    # host: The host object to log messages to
    def __init__(self, directory='./share', password='test', host=None):
        self.app = Flask(__name__)
        self.app.config['directory'] = directory
        self.host = host
        self.app.secret_key = os.urandom(24)
        self.password = password.encode('utf-8')
        self.server_thread = None
        self.port = 50505
        self.gateway = None

        self.setup_routes()

    # Setup the routes for the Flask app
    def setup_routes(self):
        self.app.add_url_rule('/FolderDrop-icon.svg', 'favicon', self.favicon)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/', 'index', self.index, methods=['GET', 'POST'])
        self.app.add_url_rule('/<path:subpath>', 'index', self.index, methods=['GET', 'POST'])

    # Convert a size in bytes to a human readable format
    def size_human_readable(self, size):
        for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
            if abs(size) < 1024.0:
                return f"{size:3.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}YiB"

    # Get the size of a directory
    def size_of_dir(self, path: str):
        size = 0
        for path, dirs, files in os.walk(path):
            for f in files:
                size += os.path.getsize(os.path.join(path, f))
        return size

    # Get the contents of a directory
    # Returns a list of tuples with the following format:
    # (type, name, size, modified time)
    # type: 'd' for directory, 'f' for file
    # name: The name of the file or directory
    # size: The size of the file or directory in human readable format
    # modified time: The modified time of the file or directory
    def get_contents(self, path: str):
        contents = []
        for f in os.listdir(path):
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path, f))).replace(microsecond=0).isoformat(' ')
            if os.path.isdir(os.path.join(path, f)):
                size = self.size_of_dir(os.path.join(path, f))
                contents.append(('d', f, size, mod_time))
            elif os.path.isfile(os.path.join(path, f)):
                size = os.path.getsize(os.path.join(path, f))
                contents.append(('f', f, size, mod_time))
        if session.get("Sort") == 1:
            contents.sort(key=lambda tup: tup[2], reverse=True)
        res = []
        for i in contents:
            res.append((i[0], i[1], self.size_human_readable(i[2]), i[3]))
        return res

    # Route to serve the favicon
    def favicon(self):
        return send_from_directory(os.path.join(self.app.root_path , 'static'), 'FolderDrop-icon.svg')

    # Route to login to the shared directory
    def login(self):
        if request.method == 'POST':
            if self.password == request.form["password"].encode('utf-8'):
                self.host.log("Correct password entered.")
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                self.host.log("Incorrect password entered.")
                return render_template('login.html', error="Incorrect password, try again.")
        return render_template('login.html')

    def respond(self, subpath):
        full_path = os.path.join(self.app.config['directory'], subpath)
        parent_subpath = '/'.join(subpath.split('/')[:-1]) if subpath else '' # Compute parent directory path

        if os.path.isdir(full_path):
            return render_template(
                'index.html',
                files=self.get_contents(full_path),
                subpath=subpath,
                parent_subpath=parent_subpath
            )
        elif os.path.isfile(full_path):
            return send_from_directory(self.app.config['directory'], subpath, as_attachment=True)

    # Route to serve the shared directory
    def index(self, subpath=''):
        if self.password and not session.get('logged_in'):
            return redirect(url_for('login'))

        if request.method == 'POST':
            if request.form["Size"] == 'Size':
                session['Sort'] = 1
                # print("drgrdhdhdhdhtfhdjhdjtfjytdhgtdhfdzikghzrudighndthnidn")

            return self.respond(subpath)
        elif request.method == 'GET':
            return self.respond(subpath)
        abort(404)

    def get_ip_address(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, 80))
        return s.getsockname()[0]

    async def get_link(self):
        try:
            async with curio.timeout_after(2):
                self.gateway = await igd.find_gateway()
                ip = self.get_ip_address(self.gateway.ip)
                mapping = igd.proto.PortMapping(remote_host='', external_port=self.port, internal_port=self.port,
                    protocol='TCP', ip=ip, enabled=True, description='FolderDrop', duration=12*60*60)
                external_ip = await self.gateway.get_ext_ip()
                await self.gateway.add_port_mapping(mapping)
        except curio.TaskTimeout as e:
            raise Exception(f"Trying to open a port took too long. It's likely the router doesn't support the required protocols and FolderDrop will not work. (original: {repr(e)})")
        return f'http://{external_ip}:{self.port}'

    # Start the Flask server
    def run(self):
        # link = curio.run(self.get_link)
        self.host.log("FolderDrop started.")
        self.server_thread = threading.Thread(target=self.app.run, kwargs={'debug': True, 'use_reloader': False, 'port': self.port, 'host': '0.0.0.0'})
        self.server_thread.start()
        return link

    # Stop the Flask server
    def stop(self):
        if self.server_thread:
            # curio.run(self.gateway.delete_port_mapping, self.port, 'TCP')
            self.host.log("FolderDrop stopped.")
            os._exit(0)
        else:
            self.host.log("FolderDrop not running.")

# Class to be used instead of HostGUI if the GUI is not needed
class Host():
    def __init__(self):
        pass

    def log(self, text):
        print(text)

# Main function to start the FolderDrop server if launched standalone
if __name__ == "__main__":
    host = Host()
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Specify the share directory. Default "./share"')
    args = parser.parse_args()
    folderdrop = FolderDrop(directory=args.directory, host=host)
    folderdrop.run()
