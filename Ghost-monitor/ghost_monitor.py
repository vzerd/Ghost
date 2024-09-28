"""
GHOST-MONITOR
v1.0.0

Author: vzerd

Monitoring application to display the memory
and CPU usage percentage of m number of Docker
Containers, running on n number of Nodes(Hosts)
via GHOST-NODE.
"""

# required imports
import os
import socket
import sys
import time
import requests

# global variables
version = "v1.0.0"
node_port = 8096
node_count = 1
node_ip_dict = {}
logger_mode = 0
logger_interval = 0
logger_node_ip = ""


def display_config_info():
    """
    To display the configurations, set during the initial
    setup of GHOST-MONITOR. These configurations are constant
    throughout the process life cycle of the application.
    """
    print("Current configuration:\n")
    print("Version:\t", version)
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.connect(("8.8.8.8", 80))
    print("Monitor IP:\t", skt.getsockname()[0])
    skt.close()
    print("Node port:\t", node_port, "\n")
    print("Node IP\t->\tAlias")
    for ip_addr, alias in node_ip_dict.items():
        print(ip_addr + "\t->\t" + alias)
    print()


def set_config_info():
    """
    To set the configurations, that will be used,
    during the complete life cycle of the application.
    """
    print("\tGreetings!\n")
    # pointing to the global variables
    global node_port
    global node_count
    global node_ip_dict

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
            break

    while True: # code segment ensuring valid Node count is set
        try:
            node_count = int(input("# of nodes (numeric only): "))
            if node_count <= 0:
                clear_screen(1)
                print("Node # cannot be 0 or negative. Please try again.\n")
            else:
                break
        except ValueError:
            clear_screen(1)
            print("Single numeric value is expected. Please try again.\n")

    for i in range(node_count): # code segment to set IPv4 addresses of # Nodes and their Alias
        ip_addr = input(f"Node {i+1} IPv4 address (dotted decimal notation only): ").strip()
        node_ip_dict[ip_addr] = input(f"Alias for node {ip_addr}: ")

    clear_screen(1) # clearing screen post setting configurations


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
        print("\n==== GHOST-MONITOR ====\n")


def set_logger_mode():
    """
    To set the logger mode to either one of the following:
        1. Single Node Logging: Logging for only a single Node (Host).
            Defaults to this option if 1 Node is set during setup, else,
        2. All Node Logging: Logging for all the Containers.
    """
    # pointing to the global variables
    global logger_mode
    global logger_node_ip

    if node_count > 1: # if Node count is more than 1, then ask for mode selection
        print(f"{node_count} Nodes found\n")

        while True: # code segment ensuring valid mode is set
            print("Select mode:")
            print("1. Single Node Logging")
            print("2. All Node Logging")
            try:
                logger_mode = int(input("Choice (1 or 2): "))
                if logger_mode != 1 and logger_mode != 2:
                    clear_screen(1)
                    print("Choose between either 1 or 2. Please try again.\n")
                    continue
                else:
                    break
            except ValueError:
                clear_screen(1)
                print("Single numeric value is expected. Please try again.\n")
        clear_screen(1)

        if logger_mode == 1: # if Single Node Logging is set,

            while True: # code segment to select 1 Node among # Nodes
                print("Select node:")
                i = 0
                for ip_addr, alias in node_ip_dict.items(): # show all the Node's IPv4 addresses with their alias
                    i += 1
                    print(f"{i}. {ip_addr} -> {alias}")
                try:
                    ip_addr_index = int(input(f"Choice (1 to {i}): "))
                    if 1 > ip_addr_index or ip_addr_index > i:
                        clear_screen(1)
                        print(f"Choose between node 1 to {i}. Please try again.\n")
                        continue
                    else:
                        logger_node_ip = list(node_ip_dict.keys())[ip_addr_index - 1]
                        print(logger_node_ip)
                        break
                except ValueError:
                    clear_screen(1)
                    print("Single numeric value is expected. Please try again.\n")
    else: # set mode to Single Node Logging automatically as Node # is 1
        logger_mode = 1
        logger_node_ip = list(node_ip_dict.keys())[0]
        print("Single Node found")
        print("Logging mode: Single Node Logging")


def set_logger_interval():
    """
    To set interval between 5 and 15 minutes
    (inclusive) in between REST API calls to the Node(s).
    """
    # pointing to the global variable
    global logger_interval

    while True: # code segment ensuring valid interval is set
        try:
            logger_interval = int(input(f"\nChoose interval in minutes 5 to 15 (Default no-interval): "))
            if 5 > logger_interval or logger_interval > 15:
                clear_screen(1)
                print(f"Choose between minutes 5 to 15. Please try again.")
                continue
            else:
                clear_screen(1)
                print("Logging interval set to", logger_interval, "minutes")
                break
        except ValueError:
            clear_screen(1)
            print("Default no-interval is set.\n")
            break


def single_node_logger():
    """
    To fetch memory and CPU usage percentage of a
    single Node and log it.
    """
    try:
        while True: # loop until KeyboardInterrupt or ConnectionError exception occurs
            response = requests.get(f"http://{logger_node_ip}:{node_port}/api/v1/containers/get_metrics")
            if response.status_code == 200:
                metrics_data = response.json()
                clear_screen(1)
                print("Container ID\t\tMemory Usage %\t\tCPU Usage %\t\tNode IP\n")
                for container in metrics_data["containers"]:
                    print(container["id"] + "\t\t" +
                          str(container["memory_usage_%"]) + "\t\t\t" +
                          str(container["cpu_usage_%"]) + "\t\t\t" +
                          logger_node_ip)
            elif response.status_code == 404:
                print(f"ALERT: Node {logger_node_ip} ({node_ip_dict[logger_node_ip]}) is running 0 containers.")
            else:
                print(f"Server error occurred in Node {logger_node_ip} ({node_ip_dict[logger_node_ip]})")
                break
            print("\nInterval:", "no-interval" if logger_interval == 0 else (str(logger_interval) + " minutes"))
            print("Press 'ctrl + c' to quit monitoring")
            time.sleep(60 * logger_interval)
    except requests.ConnectionError:
        print("Connection error occurred. Check network or GHOST-NODE in Node(s). Exiting...")
        time.sleep(8)
        clear_screen(1)
    except KeyboardInterrupt:
        clear_screen(1)


def all_node_logger():
    """
    To fetch memory and CPU usage percentage of all the Nodes
    set during configuration and log it.
    """
    # pointing to the global variable
    global logger_node_ip
    try:
        while True: # loop until KeyboardInterrupt or ConnectionError exception occurs
            print("Container ID\t\tMemory Usage %\t\tCPU Usage %\t\tNode IP\n")
            for logger_node_ip in node_ip_dict.keys():
                response = requests.get(f"http://{logger_node_ip}:{node_port}/api/v1/containers/get_metrics")
                if response.status_code == 200:
                    metrics_data = response.json()
                    for container in metrics_data["containers"]:
                        print(container["id"] + "\t\t" +
                            str(container["memory_usage_%"]) + "\t\t\t" +
                            str(container["cpu_usage_%"])  + "\t\t\t" +
                            logger_node_ip)
                elif response.status_code == 404:
                    print(f"ALERT: Node {logger_node_ip} ({node_ip_dict[logger_node_ip]}) is running 0 containers.")
                else:
                    print(f"Server error occurred in Node {logger_node_ip} ({node_ip_dict[logger_node_ip]})")
            print("\nDelay:", "No-delay" if logger_interval == 0 else (str(logger_interval) + " minutes"))
            print("Press 'ctrl + c' to quit monitoring")
            time.sleep(60 * logger_interval)
            clear_screen(1)
    except requests.ConnectionError:
        print("Connection error occurred. Check network or GHOST-NODE in Node(s). Exiting...")
        time.sleep(8)
        clear_screen(1)
    except KeyboardInterrupt:
        clear_screen(1)


def logger():
    """
    Function to loop through setting mode and
    interval configurations, mode based logger calling,
    and quit controlling.
    """
    while True: # loop until quit is confirmed
        set_logger_mode()
        set_logger_interval()

        if logger_mode == 1:
            single_node_logger()
        elif logger_mode == 2:
            all_node_logger()

        while True: # code segment ensuring proper confirmation to quit or not
            consent = input("Quit GHOST-MONITOR? ('y' or 'n'): ")
            if consent == "y":
                clear_screen(1)
                print("Thanks for trying out GHOST ecosystem. Feel free to contribute!\nExiting...")
                time.sleep(5)
                clear_screen(0) # clear screen completely after quitting
                sys.exit(0)
            elif consent == "n":
                clear_screen(1)
                break
            else:
                clear_screen(1)


#---------------------------------------------

if __name__ == '__main__':
    clear_screen(1) # clear screen before start
    set_config_info() # setting primary configuration
    display_config_info() # displaying primary configuration
    logger() # to log metrics based on primary and secondary configuration, and control quitting