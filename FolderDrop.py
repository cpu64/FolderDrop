from flask import Flask
from flask import render_template
import argparse

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

# run the application
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script for sharing a directory over the internet.")
    parser.add_argument('-d', '--directory',  default='./share', help='Specify the share directory. Default "./share"')
    args = parser.parse_args()
    app.config['directory'] = args.directory
    app.run(debug=True)
