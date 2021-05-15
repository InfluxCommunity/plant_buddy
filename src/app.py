from flask import Flask
import users

app = Flask(__name__)


@app.route("/")
def index():
    user = users.authorize_and_get_user()

    return (
        '<!DOCTYPE html>\n'
        '<meta charset="utf-8">\n<title>Plant Buddy</title>\n'
        '<img src="/static/logo.png">\n'
        '<H3>Hello {}</H3\n'.format(user["user_name"])
    )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)