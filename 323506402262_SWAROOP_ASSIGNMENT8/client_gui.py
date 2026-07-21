import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)

PORT = config["PORT"]
BUFFER_SIZE = config["BUFFER_SIZE"]


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI Based Multi Client Chat")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        tk.Label(self.root, text="GUI Based Multi Client Chat", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.root, text="Server IP").pack()
        self.server_ip = tk.Entry(self.root, width=30)
        self.server_ip.insert(0, "127.0.0.1")
        self.server_ip.pack()

        tk.Label(self.root, text="Username").pack()
        self.username = tk.Entry(self.root, width=30)
        self.username.pack()

        tk.Label(self.root, text="Password").pack()
        self.password = tk.Entry(self.root, show="*", width=30)
        self.password.pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Login", width=12, command=self.connect).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Register", width=12, command=self.register).pack(side=tk.LEFT, padx=5)

        self.root.mainloop()

    def connect(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        
        if username == "" or password == "":
            messagebox.showerror("Error", "Username and Password are required.")
            return

        ip = self.server_ip.get().strip()

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, PORT))

            self.client.send(f"LOGIN|{username}|{password}".encode())
            response = self.client.recv(BUFFER_SIZE).decode().strip()
            
            if not response.startswith("LOGIN_SUCCESS"):
                messagebox.showerror("Login Failed", response)
                self.client.close()
                return

            self.client.send("READY\n".encode())
            self.root.destroy()
            ChatWindow(self.client, username)

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def register(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        ip = self.server_ip.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "Username and Password are required.")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, PORT))
            client.send(f"REGISTER|{username}|{password}".encode())
            
            response = client.recv(BUFFER_SIZE).decode().strip()
            messagebox.showinfo("Registration", response)
            client.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


class ChatWindow:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"Chat - {username}")
        self.root.geometry("900x600")

        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(self.root, width=180, bg="#eeeeee")
        right_frame.pack(side="right", fill="y")

        self.chat_area = ScrolledText(left_frame, wrap=tk.WORD, state="disabled", font=("Consolas", 11))
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.message_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.send_button = tk.Button(input_frame, text="Send", width=10, command=self.send_message)
        self.send_button.pack(side="left", padx=5)

        self.disconnect_button = tk.Button(input_frame, text="Disconnect", width=12, command=self.disconnect)
        self.disconnect_button.pack(side="left", padx=5)

        tk.Label(right_frame, text="Online Users", font=("Arial", 12, "bold"), bg="#eeeeee").pack(pady=5)
        self.user_list = tk.Listbox(right_frame, width=22)
        self.user_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.status = tk.Label(self.root, text="Status : Connected", fg="green")
        self.status.pack(side="bottom", fill="x")

        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.display_message("SYSTEM: Login Successful. Fetching chat data...")

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)
        self.root.mainloop()

    def display_message(self, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def send_message(self):
        message = self.message_entry.get().strip()
        if message == "":
            return
        try:
            self.client.send((message + "\n").encode())
            self.display_message(f"You: {message}")
            self.message_entry.delete(0, tk.END)
        except BrokenPipeError:
            messagebox.showerror("Disconnected", "Server connection lost.")
        except OSError:
            messagebox.showerror("Socket Error", "Connection closed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.client.recv(BUFFER_SIZE).decode()
                if not data:
                    break

                buffer += data

                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)

                    if message.startswith("USERLIST|"):
                        users_str = message.split("|", 1)[1]
                        users = users_str.split(",") if users_str else []
                        self.user_list.delete(0, tk.END)
                        for user in users:
                            if user.strip():
                                self.user_list.insert(tk.END, user.strip())
                    
                    elif message.startswith("CHAT|"):
                        _, sender, text = message.split("|", 2)
                        self.display_message(f"{sender}: {text}")
                    
                    elif message.startswith("SYSTEM|"):
                        self.display_message(message.split("|", 1)[1])
                    
                    elif message.startswith("TIMEOUT|"):
                        messagebox.showwarning("Timeout", "Disconnected due to inactivity.")
                        self.disconnect()
                        break
                    
                    elif message.startswith("PRIVATE|"):
                        _, sender, text = message.split("|", 2)
                        self.display_message(f"[PRIVATE] {sender}: {text}")
                    
                    else:
                        # Fallback for unexpected messages
                        if message.strip():
                            self.display_message(message)
            
            except ConnectionResetError:
                messagebox.showerror("Connection Lost", "Server disconnected.")
                break
            except OSError:
                break
            except Exception as e:
                print(e)
                break

    def disconnect(self):
        try:
            # We append \n here to match the new server framing rule
            self.client.send("DISCONNECT\n".encode())
        except (BrokenPipeError, OSError):
            pass
        except Exception:
            pass
            
        try:
            self.client.close()
        except Exception:
            pass
            
        self.root.destroy()


if __name__ == "__main__":
    LoginWindow()