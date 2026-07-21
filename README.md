# 🚀 Application Optimization, Scalability and Reliability (Assignment 8)

A Python-based **GUI Multi-Client Chat Application** developed using **TCP Socket Programming** and **Tkinter**, enhanced with optimization, scalability, and reliability features. This project extends the secure chat application developed in Assignment 7 by improving connection management, resource handling, configuration management, and overall application performance.

---

# 📌 Project Overview

This project demonstrates a reliable and scalable client-server chat application capable of handling multiple concurrent users while maintaining stable communication. The application includes secure authentication, GUI-based messaging, centralized configuration, automatic resource management, and performance evaluation.

---

# ✨ Features

## 🔐 Security Features (Inherited from Assignment 7)

- User Authentication
- SHA-256 Password Hashing
- Duplicate Login Prevention
- Failed Login Protection
- Session Management
- Secure Logging
- Online User List
- Broadcast Messaging
- Private Messaging
- Chat History

---

## ⚡ Optimization Features (Assignment 8)

- Improved Thread Management
- Automatic Client Cleanup
- Better Socket Resource Management
- Graceful Client Disconnection
- Automatic Timeout Handling
- Improved Exception Handling
- Configuration Management using JSON
- Support for 10 Concurrent Clients
- Performance Monitoring
- Wireshark Verification

---

# 🛠 Technologies Used

- Python 3
- Socket Programming
- Tkinter
- Threading
- JSON
- CSV
- hashlib
- Mininet
- Wireshark
- Ubuntu 24.04 LTS
- Oracle VirtualBox

---

# 📂 Project Structure

```text
Assignment8/
│
├── server.py
├── client_gui.py
├── config.json
├── users.csv
├── security_log.txt
├── server_log.txt
├── chat_history.csv
├── performance_results.csv
│
├── graphs/
│   ├── clients_vs_delay.png
│   ├── clients_vs_throughput.png
│   ├── clients_vs_cpu.png
│   └── clients_vs_memory.png
│
├── screenshots/
│   ├── server_running.png
│   ├── client_login.png
│   ├── multiple_clients.png
│   ├── broadcast_message.png
│   ├── private_message.png
│   ├── online_users.png
│   ├── graceful_shutdown.png
│   ├── wireshark_capture.png
│   └── graphs.png
│
├── report.pdf
└── README.md
```

---

# 💻 Software Requirements

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
------------------------------------------------
|        |        |        |        |         |
h2       h3       h4       h5      ...       h11

ClientA  ClientB  ClientC  ClientD         Client10
```

---

# 🚀 Setup Instructions

## 1. Start Mininet

```bash
sudo mn --topo single,11
```

---

## 2. Open XTerm Windows

```bash
xterm h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11
```

---

## 3. Start the Server

```bash
python3 server.py
```

---

## 4. Start GUI Clients

On each client terminal:

```bash
python3 client_gui.py
```

---

# ⚙ Configuration

Application settings are stored in **config.json**.

Example:

```json
{
    "host": "0.0.0.0",
    "port": 5000,
    "max_clients": 10,
    "buffer_size": 1024,
    "socket_timeout": 30,
    "reconnect_attempts": 5,
    "heartbeat_interval": 10,
    "history_limit": 5
}
```

This allows easy modification of server settings without changing the source code.

---

# 📊 Performance Evaluation

The following metrics were evaluated:

- Average Message Delay
- Throughput
- CPU Usage
- Memory Usage

Graphs generated:

- Clients vs Average Delay
- Clients vs Throughput
- Clients vs CPU Usage
- Clients vs Memory Usage

---

# 📡 Wireshark Verification

Launch Wireshark:

```bash
sudo wireshark &
```

Display filter:

```text
tcp.port == 5000
```

Captured events include:

- Client Connection
- Authentication
- Broadcast Messages
- Private Messages
- Graceful Disconnection

---

# 📈 Performance Results

| Clients | Delay (ms) | Throughput (msg/sec) | CPU (%) | Memory (MB) |
|---------:|-----------:|---------------------:|---------:|------------:|
| 5 | 1.85 | 240 | 14 | 48 |
| 8 | 2.31 | 378 | 21 | 63 |
| 10 | 2.94 | 465 | 27 | 74 |

---

# 🎯 Optimizations Implemented

- Improved scalability for multiple concurrent users
- Reliable thread management
- Automatic resource cleanup
- Socket timeout management
- Graceful shutdown
- Centralized configuration
- Better exception handling
- Improved maintainability
- Stable multi-client communication

---

# 📚 Learning Outcomes

Through this project, the following concepts were explored:

- TCP Socket Programming
- GUI Development with Tkinter
- Concurrent Programming using Threads
- Network Optimization
- Scalable Client–Server Architecture
- Configuration Management
- Performance Analysis
- Wireshark Packet Inspection
- Reliable Network Application Design

---

# 🔮 Future Enhancements

- TLS/SSL Encryption
- Database Integration
- Async I/O using asyncio
- Load Balancing
- Group Chat Support
- File Sharing
- Voice and Video Communication
- Cloud Deployment
- Role-Based Access Control

---

# 📖 References

1. Python Socket Programming Documentation
2. Python Threading Documentation
3. Python Tkinter Documentation
4. Python JSON Documentation
5. Mininet Documentation
6. Wireshark User Guide
7. Andrew S. Tanenbaum – *Computer Networks*
8. W. Richard Stevens – *TCP/IP Illustrated*

---

# 👨‍💻 Author

**K. M. Swaroop**  
**Roll Number:** 323506402262  
B.Tech – Computer Science Engineering  
Andhra University

---

## ⭐ Project Summary

This project extends the Assignment 7 secure chat application by introducing optimization, scalability, and reliability improvements. It supports multiple concurrent clients, centralized configuration, improved connection management, automatic resource cleanup, and performance evaluation while maintaining secure and reliable TCP-based communication.
