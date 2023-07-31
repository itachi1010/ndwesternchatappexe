# import required modules
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from plyer import notification
import os



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

DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)

# Creating a socket object
# AF_INET: we are going to use IPv4 addresses
# SOCK_STREAM: we are using TCP packets for communication
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to show a toast notification
def show_toast_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)
    show_toast_notification("New Message", message)

def connect():
    try:
        client.connect((HOST, PORT))
        print("Successfully connected to server")
        add_message("[SERVER] Successfully connected to the server")
        show_toast_notification("Chat Update", "Successfully connected to the server")
    except:
        messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    username = 'passive client'

    client.sendall(username.encode())


    threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()

    username_button.config(state=tk.DISABLED)



# Client code
def listen_for_messages_from_server(client):
    while True:
        data = client.recv(1024)
        if data == b'':
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # get the desktop path
            file_path = os.path.join(desktop, 'local mail', 'alert.txt')  # set the file path to 'local mail' folder on the desktop
            receive_file(client, file_path)
        else:
            message = data.decode('utf-8')
            if message == '':
                print("Server has closed the connection")
                add_message("[SERVER] Server has closed the connection")
                break
            else:
                if "~" in message:  # check if "~" is in the message
                    username = message.split("~")[0]
                    content = message.split('~')[1]
                    add_message(f"[{username}] {content}")
                    if content == "ALERT":
                        show_toast_notification("Alert", "Check the received alert.txt file")
                else:  # if "~" is not in the message, then it's the alert.txt file
                    add_message("[SERVER] Received alert.txt file")

def receive_file(client, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # create 'local mail' folder if it doesn't exist
    with open(file_path, 'wb') as file:
        while True:
            data = client.recv(1024)
            if data == b'':
                break
            file.write(data)

# main function
def main():
    root.mainloop()

root = tk.Tk()
root.geometry("600x600")
root.title("ndwestern passive Client")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)


username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.TOP, padx=15)


message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)

if __name__ == '__main__':
    main()
