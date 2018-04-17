from flask import Flask, render_template

from Config import Config

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", config={
        "access" : Config.get_aws_key(),
        "secret": Config.get_aws_secret(),
        "bot" : "WeatherDemo"
    })


if __name__ == '__main__':
    app.run()
