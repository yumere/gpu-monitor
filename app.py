from flask import Flask
from flask import render_template

import gpuinfo_bp

app = Flask(__name__)

app.register_blueprint(gpuinfo_bp.gpuinfo)


@app.route("/")
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10113, debug=True)
