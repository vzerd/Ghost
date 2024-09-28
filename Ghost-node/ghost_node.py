"""
GHOST-NODE
v1.0.0

Author: vzerd

Application to extract the memory and CPU
usage percentage of m number of Docker
Containers of the current Node(Host) and
send the data back to calling application.
"""

# required imports
import os
import time
from flask import Flask
import json
import docker
import threading
import socket
from waitress import serve

# init Flask app and global variables
app = Flask(__name__)
version = "v1.0.0"
node_port = 8096


def display_config_info():
    """
    To display the configuration information
    of GHOST-NODE on the Terminal.
    """
    print("Version:\t", version)
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.connect(("8.8.8.8", 80))
    print("Node IP:\t", skt.getsockname()[0])
    print("Port:\t\t", node_port)
    print("Endpoint:\t /api/v1/containers/get_metrics")
    print("URL:\t\t", str(skt.getsockname()[0]) +
          ":" + str(node_port) + "/api/v1/containers/get_metrics")
    print(" |-> For apps using GHOST-NODE apart from GHOST-MONITOR\n")
    skt.close()
    print("Press 'ctrl + c' to quit.")


def set_config_info():
    """
    To set the configuration, that will be used,
    during the complete life cycle of the application.
    """
    # pointing to the global variable
    global node_port

    while True: # code segment ensuring valid Node port is set
        try:
            node_port = int(input("Node port (Default 8096. Press Enter to set default): "))
            if node_port <= 0:
                clear_screen(1)
                print("Node port cannot be 0 or negative. Please try again.\n")
            else:
                break
        except ValueError:
            clear_screen(1)
            print("Default port 8096 is set.\n")
            time.sleep(4)
            clear_screen(1)
            break


def clear_screen(state):
    """
    To clear screen based on state value:
        if 1: print application name post screen clear,
        else: only screen clear.
    :param state: int -> 1 or any other number
    """
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')
    if state == 1:
        print("\n==== GHOST-NODE ====\n")


def process_container_details_list(container, lock, container_details_list):
    """
    To process the details of each container,
    and append it the details to the container_details_list.
    :param container: object containing data of a specific container
    :param lock: to lock the critical section for a thread
    :param container_details_list: dict -> to save each container's details
    """
    container_resource_object = {} # dict to hold the resources usage data of the container

    container_stat = container.stats(stream=False) # get the stats of the container

    # Calculating the memory usage percentage
    used_memory = (container_stat["memory_stats"]["usage"] -
                   container_stat["memory_stats"]["stats"]["cache"])
    available_memory = container_stat["memory_stats"]["limit"]
    memory_usage_percentage = round(((used_memory / available_memory) * 100.0), 2)

    # calculating the cpu usage percentage
    cpu_delta = (container_stat["cpu_stats"]["cpu_usage"]["total_usage"] -
                 container_stat["precpu_stats"]["cpu_usage"]["total_usage"])
    system_cpu_delta = (container_stat["cpu_stats"]["system_cpu_usage"] -
                        container_stat["precpu_stats"]["system_cpu_usage"])
    number_cpus = container_stat["cpu_stats"]["online_cpus"]
    cpu_usage_percentage = round(((cpu_delta / system_cpu_delta) * number_cpus * 100.0), 2)

    # setting the calculated resource usage data into the container_resource_object
    container_resource_object["id"] = container.short_id
    container_resource_object["memory_usage_%"] = memory_usage_percentage
    container_resource_object["cpu_usage_%"] = cpu_usage_percentage
    # using lock, accessing the critical section and appending the
    # container_resource_object to the container_details_list
    with lock:
        container_details_list.append(container_resource_object)


@app.route('/api/v1/containers/get_metrics', methods=['GET'])
def get_metrics():
    """
    Endpoint to return the calculated metrics of all the
    available containers.
    :return: HTTP JSON response
    """
    response_object = {}
    container_details_list = []

    client = docker.from_env() # setting up the client object for Docker Engine API communication
    if not client.containers.list(): # if no containers found
        return "", 404

    lock = threading.Lock()
    threads = []

    for container in client.containers.list(): # spinning up threads for each container present in the Node to collect metrics
        thread = threading.Thread(target=process_container_details_list,
                                  args=(container, lock, container_details_list,))
        thread.start()
        threads.append(thread)

    for thread in threads: # waiting for all threads to finish
        thread.join()
    # returning the final list encapsulated in a response_object
    response_object["containers"] = container_details_list
    return json.dumps(response_object), 200


#---------------------------------------------
if __name__ == '__main__':
    clear_screen(1) # clear screen before start
    set_config_info() # setting configuration information
    display_config_info() # displaying configuration information
    serve(app, host='0.0.0.0', port=node_port) # start serving the application with 0.0.0.0:8096