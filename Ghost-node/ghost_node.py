from flask import Flask
import json
import docker
import threading
import socket
from waitress import serve

app = Flask(__name__)
version = "v1.0.0"
port = 8096

def display_config_info():

    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.connect(("8.8.8.8", 80))
    print("\n==== GHOST-NODE ====  ")
    print()
    print("Version:\t", version)
    print("Client IP:\t", skt.getsockname()[0])
    print("Port:\t\t", port)
    print("Endpoint:\t /api/v1/containers/get_metrics")
    print("URL:\t\t", str(skt.getsockname()[0]) +
          ":" + str(port) + "/api/v1/containers/get_metrics")
    print("\t|-> For apps using GHOST-NODE apart from GHOST-MONITOR\n")
    skt.close()

def process_container_details_list(container, lock, container_details_list):

    container_resource_object = {}

    container_stat = container.stats(stream=False)

    used_memory = (container_stat["memory_stats"]["usage"] -
                   container_stat["memory_stats"]["stats"]["cache"])
    available_memory = container_stat["memory_stats"]["limit"]
    memory_usage_percentage = round(((used_memory / available_memory) * 100.0), 2)

    cpu_delta = (container_stat["cpu_stats"]["cpu_usage"]["total_usage"] -
                 container_stat["precpu_stats"]["cpu_usage"]["total_usage"])
    system_cpu_delta = (container_stat["cpu_stats"]["system_cpu_usage"] -
                        container_stat["precpu_stats"]["system_cpu_usage"])
    number_cpus = container_stat["cpu_stats"]["online_cpus"]
    cpu_usage_percentage = round(((cpu_delta / system_cpu_delta) * number_cpus * 100.0), 2)

    container_resource_object["id"] = container.short_id
    container_resource_object["memory_usage_%"] = memory_usage_percentage
    container_resource_object["cpu_usage_%"] = cpu_usage_percentage
    lock.acquire()
    container_details_list.append(container_resource_object)
    lock.release()


@app.route('/api/v1/containers/get_metrics', methods=['GET'])
def get_metrics():

    response_object = {}
    container_details_list = []

    client = docker.from_env()
    if not client.containers.list():
        return "", 404

    lock = threading.Lock()
    threads = []

    for container in client.containers.list():
        thread = threading.Thread(target=process_container_details_list,
                                  args=(container, lock, container_details_list,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    response_object["containers"] = container_details_list
    return json.dumps(response_object), 200

#---------------------------------------------
if __name__ == '__main__':
    display_config_info()
    serve(app, host='0.0.0.0', port=port)
