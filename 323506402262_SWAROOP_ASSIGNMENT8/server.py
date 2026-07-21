import socket
import threading
import csv
import os
import hashlib
import re
import time
import json
import traceback
import psutil  # Step 2: Added psutil
from datetime import datetime

# ------------------------------------
# Load Configuration
# ------------------------------------
with open("config.json", "r") as file:
    config = json.load(file)

HOST = config["HOST"]
PORT = config["PORT"]
CHAT_HISTORY = config["CHAT_HISTORY"]
USERS_FILE = config["USERS_FILE"]
SECURITY_LOG = config["SECURITY_LOG"]
BUFFER_SIZE = config["BUFFER_SIZE"]
SESSION_TIMEOUT = config["SESSION_TIMEOUT"]
MAX_LOGIN_ATTEMPTS = config["MAX_LOGIN_ATTEMPTS"]

clients = []
usernames = {}
user_info = {}
failed_attempts = {}

clients_lock = threading.Lock()

stats = {
    "connected_users": 0,
    "messages_processed": 0,
    "broadcast_messages": 0,
    "private_messages": 0
}

# Step 3: Performance tracking variables
performance = {
    "start_time": time.time(),
    "message_count": 0
}


# ------------------------------------
# Hash Password
# ------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------------------------
# Validate Input
# ------------------------------------
def validate_input(username, password):
    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Username can contain only letters, numbers and _"

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    return True, ""


# ------------------------------------
# Security Log
# ------------------------------------
def write_security_log(event):
    with open(SECURITY_LOG, "a") as file:
        file.write(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {event}\n"
        )


# ------------------------------------
# Register User
# ------------------------------------
def register_user(username, password):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as file:
            file.write("username,password_hash\n")

    with open(USERS_FILE, "r") as file:
        for line in file.readlines()[1:]:
            user = line.strip().split(",")
            if len(user) >= 2 and user[0] == username:
                return False

    with open(USERS_FILE, "a") as file:
        file.write(f"{username},{hash_password(password)}\n")
    return True


# ------------------------------------
# Verify Login
# ------------------------------------
def verify_user(username, password):
    if not os.path.exists(USERS_FILE):
        return False

    with open(USERS_FILE, "r") as file:
        for line in file.readlines()[1:]:
            user = line.strip().split(",")
            if len(user) >= 2:
                if user[0] == username and user[1] == hash_password(password):
                    return True
    return False


# ------------------------------------
# Create history & performance files
# ------------------------------------
if not os.path.exists(CHAT_HISTORY):
    with open(CHAT_HISTORY, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "sender", "receiver", "message_type", "message"])

# Step 4: Create Performance CSV
if not os.path.exists("performance_results.csv"):
    with open("performance_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "Connected Clients",
            "Delay(ms)",
            "Throughput(msg/sec)",
            "CPU Usage(%)",
            "Memory Usage(MB)"
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
# Log Performance Data (Step 5)
# ------------------------------------
def log_performance():
    cpu = psutil.cpu_percent(interval=0.1)

    process = psutil.Process(os.getpid())
    memory = process.memory_info().rss / (1024 * 1024)

    elapsed = max(time.time() - performance["start_time"], 1)

    throughput = performance["message_count"] / elapsed

    delay = (1000 / throughput) if throughput > 0 else 0

    with open("performance_results.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            len(clients),
            round(delay, 2),
            round(throughput, 2),
            round(cpu, 2),
            round(memory, 2)
        ])


# ------------------------------------
# Show last 5 messages after reconnect
# ------------------------------------
def show_last_messages(username, client):
    if not os.path.exists(CHAT_HISTORY):
        return

    try:
        with open(CHAT_HISTORY, "r", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != [
                "timestamp",
                "sender",
                "receiver",
                "message_type",
                "message"
            ]:
                return

            rows = []

            for row in reader:
                if row.get("sender") == username:
                    rows.append(row)

            rows = rows[-5:]

            if rows:
                client.send("SYSTEM|===== Last 5 Messages =====\n".encode())

                for row in rows:
                    line = f"{row['timestamp']} -> {row['receiver']}: {row['message']}"
                    client.send(f"SYSTEM|{line}\n".encode())

                client.send("SYSTEM|===========================\n".encode())

    except Exception as e:
        print("History Error:", e)


# ------------------------------------
# Update All User Lists
# ------------------------------------
def update_all_user_lists():
    with clients_lock:
        users = ",".join(usernames.values())
        current_clients = clients.copy()
        
    for client in current_clients:
        try:
            client.send(f"USERLIST|{users}\n".encode())
        except (ConnectionResetError, BrokenPipeError, OSError):
            continue
        except Exception:
            continue


# ------------------------------------
# Broadcast message
# ------------------------------------
def broadcast(message, sender=None):
    dead_clients = []

    with clients_lock:
        current_clients = clients.copy()
        
    for client in current_clients:
        if client != sender:
            try:
                client.send(message)
            except (ConnectionResetError, BrokenPipeError, OSError):
                dead_clients.append(client)

    if dead_clients:
        with clients_lock:
            for client in dead_clients:
                if client in clients:
                    clients.remove(client)

                if client in usernames:
                    del usernames[client]


# ------------------------------------
# Send private message
# ------------------------------------
def private_message(sender_socket, sender_name, target_name, message):
    if target_name not in usernames.values():
        sender_socket.send(f"SYSTEM|User '{target_name}' not found.\n".encode())
        return

    with clients_lock:
        targets = {sock: name for sock, name in usernames.items() if name == target_name}

    for sock, name in targets.items():
        try:
            sock.send(f"PRIVATE|{sender_name}|{message}\n".encode())
            sender_socket.send(f"PRIVATE|To {target_name}|{message}\n".encode())
            
            stats["private_messages"] += 1
            save_history(sender_name, target_name, "PRIVATE", message)
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        return


# ------------------------------------
# Handle one client
# ------------------------------------
def handle_client(client):
    buffer = ""
    sender = usernames.get(client, "Unknown")

    while True:
        try:
            data = client.recv(BUFFER_SIZE).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                msg = msg.strip()

                if not msg:
                    continue
                
                if msg == "DISCONNECT":
                    print(f"{sender} disconnected gracefully.")
                    break

                stats["messages_processed"] += 1
                performance["message_count"] += 1  # Step 6: Update Counter
                
                with clients_lock:
                    sender = usernames[client]
                    user_info[sender]["last_activity"] = datetime.now()

                if msg.startswith("/msg "):
                    parts = msg.split(" ", 2)

                    if len(parts) < 3:
                        client.send("SYSTEM|Usage: /msg username message\n".encode())
                        continue

                    private_message(client, sender, parts[1], parts[2])
                    log_performance()  # Step 7: Log Performance for private msg
                    continue

                print("Received:", msg)
                print("Broadcasting:", f"CHAT|{sender}|{msg}")

                broadcast(f"CHAT|{sender}|{msg}\n".encode(), client)

                stats["broadcast_messages"] += 1
                save_history(sender, "ALL", "BROADCAST", msg)
                log_performance()  # Step 7: Log Performance for broadcast

        except ConnectionResetError:
            print(f"{sender} connection reset.")
            break
        except socket.timeout:
            print(f"{sender} timed out.")
            break
        except OSError:
            print(f"{sender} socket closed.")
            break
        except Exception as e:
            print("Client Error:", e)
            break

    username = usernames.get(client)

    with clients_lock:
        if client in clients:
            clients.remove(client)

        if client in usernames:
            del usernames[client]

    update_all_user_lists()

    if username and username in user_info:
        with clients_lock:
            user_info[username]["status"] = "Offline"
            
        stats["connected_users"] -= 1

        broadcast(
            f"SYSTEM|{username} left the chat\n".encode()
        )

        write_security_log(f"LOGOUT : {username}")

    client.close()


# ------------------------------------
# Session Timeout Monitor
# ------------------------------------
def session_timeout_monitor():
    while True:
        current = datetime.now()
        
        with clients_lock:
            current_clients = clients.copy()
            
        for client in current_clients:
            username = usernames.get(client)
            if username is None:
                continue

            last = user_info[username]["last_activity"]
            elapsed = (current - last).total_seconds()

            if elapsed >= SESSION_TIMEOUT:
                print(f"Session timeout for {username}")
                write_security_log(f"SESSION TIMEOUT : {username}")

                try:
                    client.send("TIMEOUT|Session expired\n".encode())
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass
                except Exception:
                    pass

                try:
                    client.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass

                try:
                    client.close()
                except Exception:
                    pass

        time.sleep(2)


# ------------------------------------
# Accept new clients
# ------------------------------------
def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Advanced Chat Server running on port {PORT}...\n")

    while True:
        try:
            client, address = server.accept()
            
            request = client.recv(BUFFER_SIZE).decode().strip()
            parts = request.split("|")

            if len(parts) != 3:
                client.send("Invalid Request\n".encode())
                client.close()
                continue

            action, username, password = parts[0], parts[1], parts[2]

            if action == "REGISTER":
                valid, message = validate_input(username, password)
                if not valid:
                    write_security_log(f"REGISTER FAILED : {username} ({message})")
                    client.send(f"{message}\n".encode())
                    client.close()
                    continue

                if register_user(username, password):
                    write_security_log(f"REGISTER SUCCESS : {username}")
                    client.send("Registration Successful\n".encode())
                else:
                    write_security_log(f"REGISTER FAILED : {username} (Username Exists)")
                    client.send("Username already exists\n".encode())
                client.close()
                continue

            if action == "LOGIN":
                if username not in failed_attempts:
                    failed_attempts[username] = 0
                
                if failed_attempts[username] >= MAX_LOGIN_ATTEMPTS:
                    client.send("Account Locked. Too many failed login attempts.\n".encode())
                    client.close()
                    continue

                if not verify_user(username, password):
                    failed_attempts[username] += 1
                    write_security_log(f"LOGIN FAILED : {username}")
                    
                    remaining = MAX_LOGIN_ATTEMPTS - failed_attempts[username]

                    if remaining <= 0:
                        write_security_log(f"ACCOUNT LOCKED : {username}")
                        client.send("Account Locked. Too many failed login attempts.\n".encode())
                    else:
                        client.send(f"Invalid username or password. Attempts Remaining: {remaining}\n".encode())
                    client.close()
                    continue
                
                if username in usernames.values():
                    client.send("User already logged in\n".encode())
                    client.close()
                    continue
                
                failed_attempts[username] = 0
                write_security_log(f"LOGIN SUCCESS : {username}")
                client.send("LOGIN_SUCCESS\n".encode())
                
                ready_msg = client.recv(BUFFER_SIZE).decode().strip()
                if ready_msg != "READY":
                    client.close()
                    continue

            with clients_lock:
                clients.append(client)
                usernames[client] = username
                user_info[username] = {
                    "ip": address[0],
                    "port": address[1],
                    "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Online",
                    "last_activity": datetime.now()
                }
                
            stats["connected_users"] += 1

            print("=" * 50)
            print(f"User Connected : {username}")
            print(f"IP Address     : {address[0]}")
            print(f"Port           : {address[1]}")
            print("=" * 50)

            broadcast(f"SYSTEM|{username} joined the chat\n".encode())
            update_all_user_lists()
            show_last_messages(username, client)
            
            thread = threading.Thread(
                target=handle_client,
                args=(client,),
                daemon=True
            )
            thread.start()

        except ConnectionResetError:
            print("Connection reset while accepting client.")
        except OSError:
            print("Socket closed.")
        except Exception as e:
            print("Receive Error:", e)


if __name__ == "__main__":
    print("=" * 50)
    print(" Advanced Multi-Client Chat Server ")
    print("=" * 50)

    threading.Thread(
        target=session_timeout_monitor,
        daemon=True
    ).start()

    receive()