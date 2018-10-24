import json
from datetime import datetime

from fabric import Connection


def load_config(file):
    config = json.load(open(file, "rt"))

    user_id = config['USER_INFO']['id']
    user_pw = config['USER_INFO']['password']

    server_list = config['SERVER_LIST']

    return user_id, user_pw, server_list


class ServerInfo(object):
    command = "nvidia-smi --query-gpu=timestamp,name,driver_version,temperature.gpu,memory.total,memory.free,memory.used --format=csv"

    def __init__(self, host, user_id, user_pw):
        self.connection = Connection(host, user_id)
        self.connection.connect_kwargs.password = user_pw
        self.host = host
        self.info = []

        self.update()

    def update(self):
        output = self.connection.run(self.command)

        # TODO: exit code exception or no gpu exception
        self._parse(output.stdout)

    def _parse(self, gpu_stats: str):
        self.info = []
        for line in gpu_stats.split("\n"):
            if line.startswith("20"):
                stat_list = line.split(", ")
                timestamp = stat_list[0]
                name = stat_list[1]
                driver_version = stat_list[2]
                temperature = int(stat_list[3])
                total_memory = int(stat_list[4])
                free_memory = int(stat_list[5])
                used_memory = int(stat_list[6])

                memory_percentage = used_memory // total_memory

                self.info.append({
                    'timestamp': timestamp,
                    'name': name,
                    'driver_version': driver_version,
                    'temperature': temperature,
                    'total_memory': total_memory,
                    'free_memory': free_memory,
                    'used_memory': used_memory,
                    'memory_percentage': memory_percentage
                })

    @property
    def json(self):
        return {"host": self.host, "info": self.info}

    def __str__(self):
        return self.host, str(self.info)


if __name__ == '__main__':
    user_id, user_pw, server_list = load_config("config.json")
    servers = [ServerInfo(host, user_id, user_pw) for host in server_list]

    for server in servers:
        print(server.host)
        print(server.info)
        print("=======================")
