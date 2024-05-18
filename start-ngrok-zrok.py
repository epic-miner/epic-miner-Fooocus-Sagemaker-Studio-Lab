import argparse
import json
import os
import subprocess
import sys
import socket
from multiprocessing import Process
import time

DATA_FILE = 'data.json'
DEFAULT_PORT = 7865

def load_saved_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

def signal_handler(sig, frame):
    print('Terminating the application gracefully...')
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

def run_application(env):
    cmd = 'python Fooocus/entry_with_update.py --always-high-vram > log.txt & ' \
          'ssh -o StrictHostKeyChecking=no -p 80 -R0:localhost:7865 a.pinggy.io > log.txt'
    subprocess.run(cmd, shell=True, env=env)

def print_url():
    print("Waiting for the output...")
    time.sleep(2)
    sys.stdout.flush()
    
    found = False
    with open('log.txt', 'r') as file:
        end_word = '.pinggy.link'
        for line in file:
            start_index = line.find("http:")
            if start_index != -1:
                end_index = line.find(end_word, start_index)
                if end_index != -1:
                    print("Click the URL:")
                    print("URL: " + line[start_index:end_index + len(end_word)])
                    print("##############")
                    found = True
    if not found:
        print_url()
    else:
        with open('log.txt', 'r') as file:
            for line in file:
                print(line)

def get_zrok_token(args, saved_data):
    if args.token_zrok is None:
        args.token_zrok = saved_data.get('token_zrok', input('Enter the Zrok session token: ') or None)
        saved_data['token_zrok'] = args.token_zrok
        save_data(saved_data)

def main():
    env = os.environ.copy()
    
    if is_port_in_use(DEFAULT_PORT):
        find_and_terminate_process(DEFAULT_PORT)
    else:
        print(f"Port {DEFAULT_PORT} is free.")
    
    parser = argparse.ArgumentParser(description='Console app with token and domain arguments')
    parser.add_argument('--token', help='Specify the ngrok token')
    parser.add_argument('--domain', help='Specify the ngrok domain')
    parser.add_argument('--tunnel', help='Select the tunnel [1, 2, 3]')
    parser.add_argument('--token_zrok', help='Specify the Zrok token')
    parser.add_argument('--reset', action='store_true', help='Reset saved data')

    args = parser.parse_args()
    saved_data = load_saved_data()

    if args.reset:
        saved_data.clear()
    else:
        for key in ('token', 'domain', 'tunnel', 'token_zrok'):
            if getattr(args, key) is not None:
                saved_data[key] = getattr(args, key)

    if args.tunnel is None:
        args.tunnel = saved_data.get('tunnel', input('Enter a tunnel: pinggy [1], zrok [2], ngrok [3] (1/2/3): ') or '1')
        saved_data['tunnel'] = args.tunnel
            
    save_data(saved_data)
    
    cmd = 'python Fooocus/entry_with_update.py --always-high-vram'
    
    print("Tunnel:", args.tunnel)
    if args.tunnel == '3':
        if args.token is None:
            args.token = saved_data.get('token', input('Enter the token: ') or None)
            saved_data['token'] = args.token

        if args.domain is None:
            args.domain = saved_data.get('domain', input('Enter the domain: ') or '')
            saved_data['domain'] = args.domain
        save_data(saved_data)                        
        print('Token:', args.token)
        print('Domain:', args.domain)
        print('Using ngrok')
        print('Token:', args.token)
        if args.token:
            ngrok.kill()
            srv = ngrok.connect(DEFAULT_PORT, pyngrok_config=conf.PyngrokConfig(auth_token=args.token),
                                bind_tls=True, domain=args.domain).public_url
            print(srv)
            signal.signal(signal.SIGINT, signal_handler)
            print('Press Ctrl+C to exit')   
            subprocess.run(cmd, shell=True, env=env)
            signal.pause()
        else:
            print('An ngrok token is required. You can get one on https://ngrok.com')
