import argparse
import cherrypy
import os
import curio
import signal
import sys
from PyQt6.QtWidgets import QApplication
from FlaskApp import FlaskApp
from HostGUI import SetupWindow, MainWindow
from Encryption import create_self_signed_cert
from Utils import get_gateway, get_local_ip, get_public_ip, open_port


class FolderDrop():
    gateway = None
    app = None
    args = None

    def __init__(self, args):
        self.args = args
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.run()

    def run(self):
        if self.args.gui:
            self.app = QApplication(sys.argv)
            window = SetupWindow(args)
            window.show()
            if self.app.exec():
                return

        if not os.path.isdir(args.directory):
            raise NotADirectoryError(f"directory: '{args.directory}' doesn't exist")

        local_ip = get_local_ip("8.8.8.8" or curio.run(get_gateway()))
        public_ip = curio.run(get_public_ip()) if args.public else None
        ips = ["127.0.0.1", local_ip, public_ip] if public_ip else ["127.0.0.1", local_ip]

        if public_ip:
            try:
                self.gateway = curio.run(open_port(local_ip, args.port))
            except Exception as e:
                print(e)

        cert_file = './server.crt'
        key_file = './server.key'
        create_self_signed_cert(ips, cert_file, key_file)

        flaskApp = FlaskApp(vars(args), self.log)
        cherrypy.tree.graft(flaskApp.app.wsgi_app, '/')
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': args.port,
            'engine.autoreload.on': False,
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': cert_file,
            'server.ssl_private_key': key_file
        })

        print(f"\x1B[38;5;26;4mhttps://localhost:{args.port}\x1b[0m \x1B[38;5;11mOnly works on your computer. This link can only be accessed from the device where the service is running.\x1b[0m")
        print(f"\x1B[38;5;26;4mhttps://{ips[1]}:{args.port}\x1b[0m \x1B[38;5;11mWorks on your computer and devices connected to your home network. You can share this link with others in your house.\x1b[0m")
        if len(ips) > 2:
            print(f"\x1B[38;5;26;4mhttps://{ips[2]}:{args.port}\x1b[0m \x1B[38;5;11mWorks outside your home, but not inside your home network. Share this link with people on the internet, but note that it won’t work from inside your home due to router limitations.\x1b[0m")

        if self.args.gui:
            window = MainWindow(ips, args.port)
            window.show()
            self.gui=window
            cherrypy.engine.start()
            os.remove(key_file)
            os.remove(cert_file)
            self.app.exec()
        else:
            cherrypy.engine.start()
            os.remove(key_file)
            os.remove(cert_file)
            line = "continue"
            while line!= "stop":
                line = input().strip()
        self.close()

    def log(self, message):
        if self.args.gui:
            self.gui.log(message)
        else:
            print(message)

        # TODO: log to file

    def close(self):
        if self.gateway:
            try:
                curio.run(self.gateway.delete_port_mapping, args.port, 'TCP')
                # print(curio.run(gateway.get_port_mappings()))
            except Exception as e:
                print(f"Error: {repr(e)}")
        cherrypy.engine.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Directory to share. Default: "./share"')
    parser.add_argument('-p', '--password',  default='', help='Password.  Default: ""')
    parser.add_argument('-P', '--port',  default=50505, help='Port to serve FolderDrop on.  Default: "50505"')
    parser.add_argument('-s', '--max-size',  default=10737418240, help='Max size of the directory.  Default: "10GiB"')
    parser.add_argument('--gui', default=True, action=argparse.BooleanOptionalAction, help='GUI for the host. Default: "Yes"')
    parser.add_argument('--public',  default=True, action=argparse.BooleanOptionalAction, help='Allow sharing files over the internet. Default: "Yes"')
    parser.add_argument('--downloading', default=True, action=argparse.BooleanOptionalAction, help='Allow downloading files. Default: "Yes"')
    parser.add_argument('--uploading', default=True, action=argparse.BooleanOptionalAction, help='Allow uploading files. Default: "Yes"')
    parser.add_argument('--renaming', default=False, action=argparse.BooleanOptionalAction, help='Allow renaming files. Default: "No"')
    parser.add_argument('--deleting', default=False, action=argparse.BooleanOptionalAction, help='Allow deleting files. Default: "No"')
    args = parser.parse_args()

    FolderDrop(args)
