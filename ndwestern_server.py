import socket
import threading
import concurrent.futures

# Retrieves the host's IP automatically
HOST = socket.gethostbyname(socket.gethostname())

if HOST == '127.0.0.1':
    print('You are connected to your localhost (127.0.0.1), not to the LAN network')
#
# # Get the last 4 digits and convert them to an integer
# raw_port = ''.join(HOST.split('.')[2:])
# PORT = int(raw_port)
#
# # Make sure the PORT is within the permissible range (use a default port if not)
# if PORT<1024 or PORT>65535:
PORT = 65534  # default port



LISTENER_LIMIT = 5
active_clients = []
active_threads = []  # List of active threads


# Rest of the code remains the same...

# Function to listen for upcoming messages from a client
# Server code
def listen_for_messages(client, username):
    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            if message == "QUIT":
                send_message_to_client(client, "SERVER~QUIT")
                remove_client(client, username)
                break
            elif message == "ALERT":
                with open('alert.txt', 'r') as file:
                    alert_message = file.read()
                send_message_to_client(client, f"SERVER~{alert_message}")
                send_file(client, 'alert.txt')
            elif message:
                final_msg = f"{username}~{message}"
                send_messages_to_all(final_msg)
            else:
                print(f"The message sent from client {username} is empty")
        except Exception as e:
            print(f"Error receiving from {username}: {e}")
            remove_client(client, username)
            break

# Function to send message to a single client
def send_message_to_client(client, message):
    try:
        client.sendall(message.encode())
    except Exception as e:
        print(f"Error sending to client: {e}")
        remove_client(client)
# Function to send a file to a client



def send_file(client, file_path):
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client.sendall(data)
        client.sendall(b'')  # Send termination signal

# Function to remove a client
def remove_client(client, username=None):
    for user in active_clients:
        if user[1] == client:
            active_clients.remove(user)
            print(f"Client {username if username else 'unknown'} disconnected")
            break

# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

# Function to handle client
def client_handler(client):
    try:
        # Server will listen for client message that will Contain the username
        username = client.recv(2048).decode('utf-8')
        if username:
            active_clients.append((username, client))
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message)
            listen_for_messages(client, username)
        else:
            print("Client username is empty")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client.close()

# Main function
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=LISTENER_LIMIT) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            try:
                server.bind((HOST, PORT))
                print(f"Running the server on {HOST} {PORT}")
                server.listen(LISTENER_LIMIT)

                # This while loop will keep listening to client connections
                while True:
                    client, address = server.accept()
                    print(f"Successfully connected to client {address[0]} {address[1]}")
                    active_threads.append(executor.submit(client_handler, client))
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                for future in concurrent.futures.as_completed(active_threads):
                    future.result()

if __name__ == '__main__':
    main()
