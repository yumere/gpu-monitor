from flask import Blueprint, jsonify
from flask import render_template

from gpu_monitor.server_info import ServerInfo, load_config

user_id, user_pw, server_list = load_config("config.json")
servers = [ServerInfo(host, user_id, user_pw) for host in server_list]

gpuinfo = Blueprint("gpuinfo", "gpuinfo", url_prefix="/gpuinfo")


@gpuinfo.route("/", methods=["GET"])
def index():
    return render_template("gpuinfo/index.html")


@gpuinfo.route("/refresh", methods=["GET"])
def refresh():
    for server in servers:
        server.update()
        
    return jsonify({
        'results': [server.json for server in servers]
    })
