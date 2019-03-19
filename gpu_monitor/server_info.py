import json
import re
from collections import OrderedDict

from fabric import Connection


def load_config(file):
    config = json.load(open(file, "rt"))

    user_id = config['USER_INFO']['id']
    user_pw = config['USER_INFO']['password']

    server_list = config['SERVER_LIST']

    return user_id, user_pw, server_list


class ServerInfo(object):
    command = "gpustat -ucp"

    def __init__(self, host, user_id, user_pw):
        self.host = host
        self.user_id = user_id
        self.user_pw = user_pw
        self.info = []

        self.update()

    def update(self):
        with Connection(self.host, self.user_id) as conn:
            conn.connect_kwargs.password = self.user_pw
            try:
                output = conn.run(self.command)
                self._parse(output.stdout)
            except Exception as e:
                pass

    def _parse(self, gpu_stats: str):
        self.info = OrderedDict()
        for i, line in enumerate(gpu_stats.split("\n")[:-1]):
            if i == 0:
                self.server_name = line.split(" ")[0]
            else:
                gpu_stats, stats, mem_stats, proc_stats = map(lambda x: x.strip(), line.split("|"))
                gpu_no, gpu_name = re.match(r"\[(\d+)\] ([\s\S]+)", gpu_stats).groups()
                temperature, cpu_usage = re.match(r"(\d+)[\S]+C[,\s]+(\d+)", stats).groups()
                cur_mem, total_mem = re.match(r"(\d+)[\s/]+(\d+)", mem_stats).groups()

                procs = []
                for user_id, proc_name, proc_id, mem_usage in re.findall(r"([\w]+):([\w\-\_]+)/(\d+)\((\d+)M\)", proc_stats):
                    procs.append({
                        'user_id': user_id,
                        'proc_name': proc_name,
                        'proc_id': int(proc_id),
                        'mem_usage': int(mem_usage)
                    })
                mem_percentage = int(float(cur_mem) / float(total_mem) * 100)
                mem_color_class = {
                    'success': False,
                    'normal': False,
                    'warning': False,
                    'danger': False
                }
                if mem_percentage < 30:
                    mem_color_class['success'] = True
                elif mem_percentage < 50:
                    mem_color_class['normal'] = True
                elif mem_percentage < 70:
                    mem_color_class['warning'] = True
                else:
                    mem_color_class['danger'] = True

                cpu_color_class = {
                    'success': False,
                    'normal': False,
                    'warning': False,
                    'danger': False
                }

                cpu_usage = int(cpu_usage)
                if cpu_usage < 30:
                    cpu_color_class['success'] = True
                elif cpu_usage < 50:
                    cpu_color_class['normal'] = True
                elif cpu_usage < 70:
                    cpu_color_class['warning'] = True
                else:
                    cpu_color_class['danger'] = True

                self.info[gpu_no] = {
                    'gpu_no': int(gpu_no),
                    'gpu_name': gpu_name,
                    'temperature': int(temperature),
                    'cpu_usage': cpu_usage,
                    'cur_mem': int(cur_mem),
                    'total_mem': int(total_mem),
                    'mem_percentage': mem_percentage,
                    'mem_color_class': mem_color_class,
                    'cpu_color_class': cpu_color_class,
                    'procs': procs
                }

    @property
    def json(self):
        return {"host": self.host, "server_name": self.server_name, "info": self.info}

    def __str__(self):
        return self.host, str(self.info)

    def __eq__(self, other):
        return other == self.host


def install_gpustat(host, user_id, user_pw):
    connection = Connection(host, user_id)
    connection.connect_kwargs.password = user_pw
    output = connection.run("pip install gpustat")
    print(output.stdout)


if __name__ == '__main__':
    user_id, user_pw, server_list = load_config("server_info.json")
    # for host in server_list:
    #     install_gpustat(host, user_id, user_pw)
    servers = [ServerInfo(host, user_id, user_pw) for host in server_list]

    for server in servers:
        print(server.host)
        print(server.info)
        print("=======================")
