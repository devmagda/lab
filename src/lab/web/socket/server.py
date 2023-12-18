import socket

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the local machine name
host = socket.gethostname()
port = 12345

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(1)

print(f"Server is listening on {host}:{port}")

# Accept a connection from a client
client_socket, addr = server_socket.accept()
print(f"Got a connection from {addr}")

while True:
    data = client_socket.recv(1024).decode()
    if not data:
        break
    print(f"Received: {data}")
    response = input("Enter your response: ")
    client_socket.send(response.encode())

# Close the sockets
client_socket.close()
server_socket.close()
