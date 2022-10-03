import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(50)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    from waitress import serve

    serve(app, host="0.0.0.0", port=int(os.environ['APP_PORT']))
