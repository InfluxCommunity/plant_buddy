from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return (
        '<!DOCTYPE html>\n'
        '<meta charset="utf-8">\n<title>Plant Buddy</title>\n'
        '<img src="/static/logo.png">\n'
    )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)