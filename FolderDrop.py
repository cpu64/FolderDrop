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


# TODO: in gui mode quit evrything when ^C is pressed
class FolderDrop():
    gateway = None
    app = None
    args = None

    def __init__(self, args):
        self.args = args
        signal.signal(signal.SIGINT, self.interrupt_handler)
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

        local_ip = get_local_ip(curio.run(get_gateway()) or "8.8.8.8")
        public_ip = curio.run(get_public_ip())
        ips = ["127.0.0.1", local_ip, public_ip] if public_ip else ["127.0.0.1", local_ip]

        if public_ip:
            try:
                self.gateway = curio.run(open_port(local_ip, args.port))
            except Exception as e:
                print(e)

        flaskApp = FlaskApp(vars(args))
        cherrypy.tree.graft(flaskApp.app.wsgi_app, '/')
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': args.port,
            'engine.autoreload.on': False,
            'server.ssl_module': 'pyopenssl',
            'server.ssl_context': create_self_signed_cert(ips)
        })

        if self.args.gui:
            window = MainWindow(ips, args.port)
            window.show()
            cherrypy.engine.start()
            self.app.exec()
        else:
            cherrypy.engine.start()
            line = "continue"
            while line!= "stop":
                line = input().strip()
        self.close()


    def close(self):
        if self.gateway:
            try:
                curio.run(gateway.delete_port_mapping, args.port, 'TCP')
                # print(curio.run(gateway.get_port_mappings()))
            except Exception as e:
                print(f"Error: {repr(e)}")
        cherrypy.engine.stop()

    def interrupt_handler(self, signum, frame):
        self.close()
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Directory to share. Default: "./share"')
    parser.add_argument('-p', '--password',  default='', help='Password.  Default: ""')
    parser.add_argument('-P', '--port',  default=50505, help='Port to serve FolderDrop on.  Default: "50505"')
    parser.add_argument('--gui', default=True, action=argparse.BooleanOptionalAction, help='GUI for the host. Default: "Yes"')
    parser.add_argument('--downloading', default=True, action=argparse.BooleanOptionalAction, help='Allow downloading files. Default: "Yes"')
    parser.add_argument('--uploading', default=True, action=argparse.BooleanOptionalAction, help='Allow uploading files. Default: "Yes"')
    parser.add_argument('--renaming', default=False, action=argparse.BooleanOptionalAction, help='Allow renaming files. Default: "No"')
    parser.add_argument('--deleting', default=False, action=argparse.BooleanOptionalAction, help='Allow deleting files. Default: "No"')
    args = parser.parse_args()

    FolderDrop(args)
