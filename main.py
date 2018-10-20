import json

from fabric import SerialGroup


def load_config(file):
    config = json.load(open(file, "rt"))

    user_id = config['USER_INFO']['id']
    user_pw = config['USER_INFO']['password']

    server_list = config['SERVER_LIST']

    return user_id, user_pw, server_list


if __name__ == '__main__':
    user_id, user_pw, server_list = load_config("config.json")
    servers = SerialGroup(*server_list, user=user_id)
    for c in servers:
        c.connect_kwargs.password = user_pw

    command = "nvidia-smi --query-gpu=timestamp,name,driver_version,pstate,pcie.link.gen.max,pcie.link.gen.current,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv"
    output = servers.run(command)
