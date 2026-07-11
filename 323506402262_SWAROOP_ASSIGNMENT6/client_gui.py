import socket
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

PORT = 5000


class LoginWindow:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("GUI Based Multi Client Chat")

        self.root.geometry("350x250")

        self.root.resizable(False, False)

        tk.Label(
            self.root,
            text="GUI Based Multi Client Chat",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="Server IP"
        ).pack()

        self.server_ip = tk.Entry(
            self.root,
            width=30
        )

        self.server_ip.insert(0, "127.0.0.1")

        self.server_ip.pack()

        tk.Label(
            self.root,
            text="Username"
        ).pack()

        self.username = tk.Entry(
            self.root,
            width=30
        )

        self.username.pack()

        tk.Label(
            self.root,
            text="Password (Optional)"
        ).pack()

        self.password = tk.Entry(
            self.root,
            show="*",
            width=30
        )

        self.password.pack()

        tk.Button(
            self.root,
            text="Connect",
            width=15,
            command=self.connect
        ).pack(pady=15)

        self.root.mainloop()

    def connect(self):

        username = self.username.get().strip()

        if username == "":

            messagebox.showerror(
                "Error",
                "Username cannot be empty."
            )

            return

        ip = self.server_ip.get().strip()

        try:

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect((ip, PORT))

            first = self.client.recv(1024).decode()
            if first == "USERNAME":

                self.client.send(username.encode())

            self.root.destroy()

            ChatWindow(
                self.client,
                username
            )
        except Exception as e:

            messagebox.showerror(
                "Connection Error",
                str(e)
            )


class ChatWindow:

    def __init__(self, client, username):

        self.client = client

        self.username = username

        self.root = tk.Tk()

        self.root.title(
            f"Chat - {username}"
        )

        self.root.geometry("900x600")

        left_frame = tk.Frame(self.root)

        left_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        right_frame = tk.Frame(
            self.root,
            width=180,
            bg="#eeeeee"
        )

        right_frame.pack(
            side="right",
            fill="y"
        )

        self.chat_area = ScrolledText(
            left_frame,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 11)
        )

        self.chat_area.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        input_frame = tk.Frame(left_frame)

        input_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.message_entry = tk.Entry(
            input_frame,
            font=("Arial",12)
        )
        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            width=10,
            command=self.send_message
        )

        self.send_button.pack(
            side="left",
            padx=5
        )

        self.disconnect_button = tk.Button(
            input_frame,
            text="Disconnect",
            width=12,
            command=self.disconnect
        )

        self.disconnect_button.pack(
            side="left",
            padx=5
        )

        tk.Label(
            right_frame,
            text="Online Users",
            font=("Arial", 12, "bold"),
            bg="#eeeeee"
        ).pack(pady=5)

        self.user_list = tk.Listbox(
            right_frame,
            width=22
        )

        self.user_list.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.status = tk.Label(
            self.root,
            text="Status : Connected",
            fg="green"
        )

        self.status.pack(
            side="bottom",
            fill="x"
        )

        self.message_entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )

        self.receive_thread.start()

        self.refresh_users()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.disconnect
        )

        self.root.mainloop()

    # ----------------------------------------
    # Display Message
    # ----------------------------------------

    def display_message(self, message):

        self.chat_area.config(state="normal")

        self.chat_area.insert(
            tk.END,
            message + "\n"
        )

        self.chat_area.config(state="disabled")

        self.chat_area.see(tk.END)


    # ----------------------------------------
    # Send Message
    # ----------------------------------------

    def send_message(self):

        message = self.message_entry.get().strip()

        if message == "":
            return

        try:

            self.client.send(message.encode())

            self.display_message(
                f"You : {message}"
            )

            self.message_entry.delete(
                0,
                tk.END
            )

        except:

            messagebox.showerror(
                "Error",
                "Unable to send message."
            )


    # ----------------------------------------
    # Receive Messages
    # ----------------------------------------

    def receive_messages(self):

        while True:

            try:

                message = self.client.recv(1024).decode()

                if not message:
                    break

                # Online users received
                if message.startswith("\nOnline Users") or message.startswith("Online Users"):

                    self.user_list.delete(0, tk.END)

                    lines = message.split("\n")

                    for line in lines:

                        line = line.strip()

                        if (
                            line == "" or
                            line == "Online Users" or
                            line.startswith("---")
                        ):
                            continue

                        self.user_list.insert(
                            tk.END,
                            line
                        )

                else:

                    self.display_message(message)

            except:
                break


    # ----------------------------------------
    # Refresh Users
    # ----------------------------------------

    def refresh_users(self):

        try:

            self.client.send("/list".encode())

        except:
            return

        self.root.after(3000, self.refresh_users)


    # ----------------------------------------
    # Disconnect
    # ----------------------------------------

    def disconnect(self):

        try:

            self.client.close()

        except:
                pass

        self.root.destroy()


    # ----------------------------------------
    # Update Online User List
    # ----------------------------------------

    def update_user_list(self, users):

        self.user_list.delete(0, tk.END)

        for user in users:

            self.user_list.insert(
                tk.END,
                user
            )


# ----------------------------------------
# Start Application
# ----------------------------------------

if __name__ == "__main__":

    LoginWindow()
