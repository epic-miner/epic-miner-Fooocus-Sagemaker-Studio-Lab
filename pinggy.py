import argparse
import json
import os
import socket
import subprocess
import sys
import time
import psutil
import signal
from multiprocessing import Process

CONFIG_FILE = 'data.json'
TARGET_PORT = 7865

def get_saved_data():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_and_terminate_process(port):
    for process in psutil.process_iter(['pid', 'name', 'connections']):
        for conn in process.info.get('connections', []):
            if conn.laddr.port == port:
                print(f"Port {port} is in use by process {process.info['name']} (PID {process.info['pid']})")
                try:
                    process.terminate()
                    print(f"Terminated process with PID {process.info['pid']}")
                except psutil.NoSuchProcess:
                    print(f"Process with PID {process.info['pid']} not found")

def run_app(env):
    cmd = 'python Fooocus/entry_with_update.py --always-high-vram > log.txt & ssh -o StrictHostKeyChecking=no -p 80 -R0:localhost:7865 a.pinggy.io > log.txt'
    subprocess.run(cmd, shell=True, env=env)

def print_url():
    print("Waiting for output...")
    time.sleep(2)
    sys.stdout.flush()
    with open('log.txt', 'r') as file:
        for line in file:
            if "http:" in line and ".pinggy.link" in line:
                print("subscribe epic miner")
                return
    print_url()

def main():
    env = os.environ.copy()

    if is_port_in_use(TARGET_PORT):
        find_and_terminate_process(TARGET_PORT)
    else:
        print(f"Port {TARGET_PORT} is free.")

    parser = argparse.ArgumentParser(description='Console app for exposing the application through Pinggy')
    parser.add_argument('--reset', action='store_true', help='Reset saved data')
    args = parser.parse_args()

    saved_data = get_saved_data()

    if args.reset:
        saved_data = {}
    save_data(saved_data)

    cmd = 'python Fooocus/entry_with_update.py --always-high-vram'

    # Check openssh is installed
    try:
        subprocess.check_output(['ssh', '-V'])
    except subprocess.CalledProcessError:
        subprocess.run('conda install -y openssh', shell=True, env=env)

    subprocess.run('touch log.txt', shell=True, env=env)
    open('log.txt', 'w').close()
    p_app = Process(target=run_app, args=(env,))
    p_url = Process(target=print_url)
    p_app.start()
    p_url.start()
    p_app.join()
    p_url.join()

if __name__ == '__main__':
    main()
