from flask import Blueprint, jsonify
from flask import render_template
from app import servers, server_list

gpuinfo = Blueprint("gpuinfo", "gpuinfo", url_prefix="/gpuinfo")


@gpuinfo.route("/", methods=["GET"])
def index():
    return render_template("gpuinfo/index.html")


@gpuinfo.route("/<string:host>", methods=["GET"])
def get_server_info(host: str):
    global server_list
    global servers

    for server in servers:
        if host == server:
            return jsonify({
                "success": True,
                "server_info": server.json
            })

    else:
        return jsonify({
            "success": False
        })


@gpuinfo.route("/hosts", methods=["GET"])
def get_host_list():
    global server_list
    return jsonify({
        "server_list": server_list
    })


@gpuinfo.route("/refresh", methods=["GET"])
def refresh():
    global servers
    global server_list
    for server in servers:
        server.update()

    return jsonify({
        'results': [server.json for server in servers]
    })
