import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading
import json
import socket
import time

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Chat Application")
        self.root.geometry("600x500")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.username = None
        self.get_username()
        
        self.connected = False
        self.socket = None
        
        # Create the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the chat display area
        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Create the input area
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.message_entry = tk.Entry(self.input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Create connection frame
        self.connection_frame = tk.Frame(self.main_frame)
        self.connection_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.host_entry = tk.Entry(self.connection_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.port_entry = tk.Entry(self.connection_frame, width=6)
        self.port_entry.insert(0, "5555")
        self.port_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.connect_button = tk.Button(self.connection_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side=tk.LEFT, padx=(5, 0))
        
        self.status_label = tk.Label(self.connection_frame, text="Disconnected", fg="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Display welcome message
        self.update_chat(f"Welcome to the chat, {self.username}!\n")
        self.update_chat("Connect to a server to begin chatting.\n")
    
    def get_username(self):
        """Prompt for username"""
        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        if not self.username:
            self.username = f"User_{int(time.time()) % 10000}"
    
    def update_chat(self, message):
        """Update the chat display with a new message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send a message to the server"""
        message = self.message_entry.get().strip()
        if not message or not self.connected:
            return
        
        try:
            # Create message packet with "CHAT" type
            packet = {
                "type": "CHAT",
                "username": self.username,
                "message": message
            }
            
            # Send to socket backend, adding a newline character
            self.socket.send((json.dumps(packet) + '\n').encode('utf-8'))
            
            # Clear input field
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            self.update_chat(f"Error sending message: {str(e)}\n")
            self.disconnect()
    
    def toggle_connection(self):
        """Connect to or disconnect from the server"""
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """Connect to the chat server"""
        host = self.host_entry.get()
        try:
            port = int(self.port_entry.get())
            
            # Create socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Update UI
            self.connected = True
            self.connect_button.config(text="Disconnect")
            self.status_label.config(text="Connected", fg="green")
            self.update_chat(f"Connected to {host}:{port}\n")
            
            # Send connection message with "CONNECT" type
            welcome_packet = {
                "type": "CONNECT",
                "username": self.username
            }
            self.socket.send((json.dumps(welcome_packet) + '\n').encode('utf-8'))
            
            # Start listener thread
            self.listener_thread = threading.Thread(target=self.listen_for_messages)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
        except Exception as e:
            self.update_chat(f"Connection error: {str(e)}\n")
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket and self.connected:
            try:
                # Send disconnect message with "DISCONNECT" type
                disconnect_packet = {
                    "type": "DISCONNECT",
                    "username": self.username
                }
                self.socket.send((json.dumps(disconnect_packet) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Could not send disconnect packet: {e}")
            finally:
                self.socket.close()
                self.socket = None
                self.connected = False
        
        # This part should run regardless of whether the socket was open
        self.connected = False
        self.socket = None
        self.connect_button.config(text="Connect")
        self.status_label.config(text="Disconnected", fg="red")
        self.update_chat("Disconnected from server\n")
    
    def listen_for_messages(self):
        """Listen for incoming messages from the server"""
        buffer = ""
        while self.connected:
            try:
                # Receive data from the socket
                data_chunk = self.socket.recv(4096).decode('utf-8')
                if not data_chunk:
                    # Server closed the connection
                    break
                
                buffer += data_chunk
                
                # Process all complete JSON messages in the buffer
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    
                    if message_str:
                        message_data = json.loads(message_str)
                        
                        # Format the message for display based on type
                        msg_type = message_data.get("type")

                        if msg_type == "SYSTEM":
                            formatted_message = f"SYSTEM: {message_data['message']}\n"
                        elif msg_type == "CHAT":
                            username = message_data.get("username", "Anonymous")
                            message = message_data.get("message", "")
                            formatted_message = f"{username}: {message}\n"
                        else:
                            # Handle unknown message types if necessary
                            formatted_message = f"UNKNOWN: {message_str}\n"
                        
                        # Update the chat display from the main thread
                        self.root.after(0, self.update_chat, formatted_message)
                
            except (ConnectionResetError, ConnectionAbortedError):
                if self.connected:
                    self.root.after(0, self.update_chat, "Connection to server was lost.\n")
                break
            except Exception as e:
                if self.connected:
                    self.root.after(0, self.update_chat, f"Error receiving message: {str(e)}\n")
                break
        
        # If the loop breaks, we are disconnected
        self.disconnect()

    def on_closing(self):
        """Handle window closing"""
        if self.connected:
            self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()