from flask import Flask
from flask import render_template

from gpu_monitor.server_info import ServerInfo
from gpu_monitor.server_info import load_config

user_id, user_pw, server_list = load_config("server_info.json")
servers = [ServerInfo(host, user_id, user_pw) for host in server_list]

from gpu_monitor import gpuinfo_bp
app = Flask(__name__)
app.register_blueprint(gpuinfo_bp.gpuinfo)


@app.route("/")
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10113, debug=True)
