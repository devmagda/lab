import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the local machine name
host = socket.gethostname()
port = 12345

# Connect to the server
client_socket.connect((host, port))

while True:
    message = input("Enter a message: ")
    client_socket.send(message.encode())
    data = client_socket.recv(1024).decode()
    print(f"Received from server: {data}")

# Close the socket
client_socket.close()
