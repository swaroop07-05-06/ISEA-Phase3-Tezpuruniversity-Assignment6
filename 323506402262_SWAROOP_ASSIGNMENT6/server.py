import socket
import threading
import csv
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

clients = []
usernames = {}

user_info = {}

stats = {
    "connected_users": 0,
    "messages_processed": 0,
    "broadcast_messages": 0,
    "private_messages": 0
}

CHAT_HISTORY = "chat_history.csv"


# ------------------------------------
# Create chat history file if missing
# ------------------------------------
if not os.path.exists(CHAT_HISTORY):
    with open(CHAT_HISTORY, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "sender",
            "receiver",
            "message_type",
            "message"
        ])


# ------------------------------------
# Save every message
# ------------------------------------
def save_history(sender, receiver, msg_type, message):
    with open(CHAT_HISTORY, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sender,
            receiver,
            msg_type,
            message
        ])


# ------------------------------------
# Show last 5 messages after reconnect
# ------------------------------------
def show_last_messages(username, client):
    if not os.path.exists(CHAT_HISTORY):
        return

    rows = []

    with open(CHAT_HISTORY, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["sender"] == username:
                rows.append(row)

    rows = rows[-5:]

    if rows:
        client.send(
            "\n--- Last 5 Messages ---\n".encode()
        )

        for row in rows:
            line = (
                f'{row["timestamp"]} -> '
                f'{row["receiver"]}: '
                f'{row["message"]}\n'
            )
            client.send(line.encode())

        client.send(
            "-----------------------\n".encode()
        )


# ------------------------------------
# Broadcast message
# ------------------------------------
def broadcast(message, sender=None):

    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:
                pass
# ------------------------------------
# Send private message
# ------------------------------------
def private_message(sender_socket, sender_name, target_name, message):

    if target_name not in usernames.values():
        sender_socket.send(
            f"User '{target_name}' not found.\n".encode()
        )
        return

    for sock, name in usernames.items():

        if name == target_name:

            text = f"[PRIVATE] {sender_name}: {message}"

            sock.send(text.encode())

            sender_socket.send(
                f"[To {target_name}] {message}".encode()
            )

            stats["private_messages"] += 1

            save_history(
                sender_name,
                target_name,
                "PRIVATE",
                message
            )

            return


# ------------------------------------
# Send online user list
# ------------------------------------
def send_user_list(client):

    online = []

    for sock in clients:
        online.append(usernames[sock])

    text = "\nOnline Users\n"
    text += "------------------\n"

    for user in online:
        text += user + "\n"

    client.send(text.encode())


# ------------------------------------
# Handle one client
# ------------------------------------
def handle_client(client):

    while True:

        try:

            msg = client.recv(1024).decode()

            if not msg:
                break

            stats["messages_processed"] += 1

            sender = usernames[client]

            # /list command
            if msg.strip() == "/list":
                send_user_list(client)
                continue

            # /msg command
            if msg.startswith("/msg "):

                parts = msg.split(" ", 2)

                if len(parts) < 3:

                    client.send(
                        "Usage: /msg username message\n".encode()
                    )

                    continue

                private_message(
                    client,
                    sender,
                    parts[1],
                    parts[2]
                )

                continue

            # Broadcast message
            message = f"[{sender}] {msg}"

            broadcast(message.encode(), client)

            stats["broadcast_messages"] += 1

            save_history(
                sender,
                "ALL",
                "BROADCAST",
                msg
            )

        except:
            break

    # Client disconnected
    username = usernames[client]

    clients.remove(client)

    del usernames[client]

    user_info[username]["status"] = "Offline"

    stats["connected_users"] -= 1

    broadcast(
        f"\n*** {username} left the chat ***\n".encode()
    )

    print(f"{username} disconnected.")

    client.close()
# ------------------------------------
# Accept new clients
# ------------------------------------
def receive():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))

    server.listen()

    print(f"Advanced Chat Server running on port {PORT}...\n")

    while True:

        client, address = server.accept()

        client.send("USERNAME".encode())

        username = client.recv(1024).decode().strip()

        clients.append(client)

        usernames[client] = username

        user_info[username] = {
            "ip": address[0],
            "port": address[1],
            "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Online"
        }

        stats["connected_users"] += 1

        print("=" * 50)
        print(f"User Connected : {username}")
        print(f"IP Address     : {address[0]}")
        print(f"Port           : {address[1]}")
        print(f"Login Time     : {user_info[username]['login_time']}")
        print("=" * 50)

        broadcast(
            f"\n*** {username} joined the chat ***\n".encode()
        )

        show_last_messages(username, client)

        thread = threading.Thread(
            target=handle_client,
            args=(client,)
        )

        thread.start()

        print("\n------ Server Statistics ------")
        print(f"Connected Users   : {stats['connected_users']}")
        print(f"Messages Processed: {stats['messages_processed']}")
        print(f"Broadcast Messages: {stats['broadcast_messages']}")
        print(f"Private Messages  : {stats['private_messages']}")
        print("-------------------------------\n")
# ------------------------------------
# Start Server
# ------------------------------------
if __name__ == "__main__":

    print("=" * 50)
    print(" Advanced Multi-Client Chat Server ")
    print("=" * 50)

    receive()
