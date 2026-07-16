# ISEA-Phase3-Tezpuruniversity-Assignment7

A secure multi-client chat application developed using **Python Socket Programming**, **Tkinter GUI**, and **TCP**, built by extending the Assignment 6 GUI chat application. This project implements practical application-level security features such as **user authentication**, **SHA-256 password hashing**, **duplicate login prevention**, **failed login protection**, **session management**, **input validation**, and **secure logging**.

---

## 📌 Objective

The objective of this project is to enhance a GUI-based multi-client TCP chat application by implementing practical security mechanisms while maintaining reliable client-server communication. The project demonstrates secure authentication, password protection, session management, and secure network programming concepts.

---

## ✨ Features

- 🔐 User Authentication (Username & Password)
- 🔒 Secure Password Storage using SHA-256
- 🚫 Duplicate Login Prevention
- ⚠️ Failed Login Protection (Account Lock after 5 Attempts)
- ✅ Input Validation
- ⏱️ Session Timeout Management
- 📋 Secure Security Logging
- 💬 Broadcast Messaging
- 👤 Private Messaging (`/msg`)
- 👥 Online User List
- 📝 Persistent Chat History
- 🖥️ GUI-based Chat Interface using Tkinter
- 🔄 Background Message Receiving Thread
- 🌐 Multi-client TCP Communication
- 📡 Wireshark Verification

---

# 🛠️ Technologies Used

- Python 3
- Socket Programming
- Tkinter
- Threading
- hashlib (SHA-256)
- CSV
- Mininet
- Wireshark
- Ubuntu 24.04 LTS
- Oracle VirtualBox

---

# 📂 Project Structure

```text
ISEA-Phase3-TezpurUniversity-Assignment7/
│
├── server.py
├── client_gui.py
├── users.csv
├── chat_history.csv
├── security_log.txt
├── server_log.txt
├── screenshots/
│   ├── login_window.png
│   ├── login_success.png
│   ├── login_failed.png
│   ├── duplicate_login.png
│   ├── chat_window.png
│   ├── broadcast_message.png
│   ├── private_message.png
│   ├── logout.png
│   ├── wireshark_login.png
│   ├── wireshark_failed_login.png
│   ├── wireshark_authenticated_chat.png
│   └── wireshark_logout.png
├── report.pdf
└── README.md
```

---

# 🖥️ Software Requirements

- Ubuntu 24.04 LTS
- Python 3.x
- Mininet
- Wireshark
- Tkinter
- Oracle VirtualBox

---

# 🌐 Network Topology

```
           Chat Server (h1)
                 |
        -----------------------
        |      |      |      |
      h2      h3     h4      h5
   ClientA ClientB ClientC ClientD
```

Start Mininet:

```bash
sudo mn --topo single,5
```

Verify:

```bash
nodes
net
pingall
```

---

# 🚀 Execution Steps

## 1. Start Mininet

```bash
sudo mn --topo single,5
```

---

## 2. Open Terminals

```bash
xterm h1 h2 h3 h4 h5
```

---

## 3. Start Server

```bash
python3 server.py
```

---

## 4. Start GUI Clients

Run on each client terminal:

```bash
python3 client_gui.py
```

---

## 5. Login

Enter:

- Username
- Password

Click **Connect**.

---

## 6. Test Features

- Broadcast Message
- Private Message (`/msg`)
- Online User List
- Duplicate Login
- Failed Login
- Logout
- Session Timeout

---

# 🔐 Security Features

- SHA-256 Password Hashing
- User Authentication
- Duplicate Login Prevention
- Failed Login Protection
- Secure Session Management
- Input Validation
- Secure Logging
- Password Protection
- Logout Handling

---

# 📡 Wireshark Verification

Use the display filter:

```text
tcp.port == 5000
```

Capture screenshots for:

- Login
- Failed Login
- Successful Authentication
- Broadcast Message
- Private Message
- Logout

---

# 📷 Sample Screenshots

Add screenshots for:

- Login Window
- Successful Login
- Main Chat Window
- Broadcast Messaging
- Private Messaging
- Online User List
- Logout
- Duplicate Login
- Failed Login
- Wireshark Login
- Wireshark Communication
- Wireshark Logout

---

# 📚 Learning Outcomes

- TCP Socket Programming
- Client–Server Architecture
- GUI Programming using Tkinter
- Authentication & Authorization
- Password Hashing using SHA-256
- Secure Session Management
- Network Security Fundamentals
- Wireshark Packet Analysis
- Concurrent Programming using Threads

---

# 📄 Report

The project report includes:

- Objective
- Security Features Implemented
- System Architecture
- Implementation
- Testing
- Wireshark Verification
- Conclusion

---

# 📖 References

1. Python Socket Programming Documentation
2. Python Tkinter Documentation
3. Python hashlib Documentation
4. Mininet Documentation
5. Wireshark User Guide
6. Andrew S. Tanenbaum – *Computer Networks*
7. W. Richard Stevens – *TCP/IP Illustrated*

---

# 👨‍💻 Author

**K. M. Swaroop**  
**Roll Number:** 323506402262  
B.Tech – Computer Science Engineering  
Andhra University

---

## ⭐ Project Summary

This project demonstrates a secure GUI-based TCP chat application implementing practical authentication, password hashing, session management, input validation, and secure communication. The application supports multiple authenticated users, private messaging, chat history, and secure logging while following the Assignment 7 requirements.
- Join/Leave notifications
