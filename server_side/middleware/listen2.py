import socket
import requests
from datetime import datetime

def start_server(host, port):
    URL = "http://127.0.0.1:5000/"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        data = client_socket.recv(1024)
        print("Data:", data)
        if data:  
            data = data.decode()           

            if "Temperature" in data and "Begin" not in data:                         
                data = data.split("||")
                
                temp = data[0]
                temp = float(temp.split(":")[1].strip())
                hum = data[1]
                hum = float(hum.split(":")[1].strip())

                body = {"Temperature": temp, "Humidity": hum, "time": str(datetime.now)}        
                resp = requests.post(
                    url=URL+"add",
                    json=body
                )      

if __name__ == "__main__":
    host = "0.0.0.0"  # Listen on all available interfaces
    port = 8080  # Choose a suitable port number

    start_server(host, port)