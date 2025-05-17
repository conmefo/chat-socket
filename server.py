import socket
import threading
import json
import time

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        """Initialize the chat server"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # Dictionary to store client connections {socket: username}
        self.running = False
    
    def start(self):
        """Start the chat server"""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            print(f"Server started on {self.host}:{self.port}")
            
            # Start accepting client connections
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New connection from {client_address}")
                    
                    # Start a new thread to handle the client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:  # Only show error if we're still supposed to be running
                        print(f"Error accepting connection: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the chat server"""
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            
        print("Server stopped")
    
    def handle_client(self, client_socket, client_address):
        """Handle client connection"""
        username = None
        
        try:
            # Receive messages from the client
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Process the received data
                message_data = json.loads(data.decode('utf-8'))
                
                # Handle different message types
                if "type" in message_data:
                    # Handle connection messages
                    if message_data["type"] == "connect":
                        username = message_data.get("username", f"User_{client_address[1]}")
                        self.clients[client_socket] = username
                        print(f"{username} connected from {client_address}")
                        
                        # Send system message to all clients
                        system_message = {
                            "type": "system",
                            "message": f"{username} has joined the chat"
                        }
                        self.broadcast(system_message)
                        continue
                        
                    # Handle disconnection messages
                    elif message_data["type"] == "disconnect":
                        break
                
                # Handle regular chat messages
                username = message_data.get("username", username or f"User_{client_address[1]}")
                if not username:
                    username = f"User_{client_address[1]}"
                    message_data["username"] = username
                
                print(f"Message from {username}: {message_data.get('message', '')}")
                
                # Broadcast the message to all clients
                self.broadcast(message_data)
                
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            # Clean up when client disconnects
            if client_socket in self.clients:
                username = self.clients[client_socket]
                del self.clients[client_socket]
                
                # Send disconnect message to all clients
                system_message = {
                    "type": "system",
                    "message": f"{username} has left the chat"
                }
                self.broadcast(system_message)
                
                print(f"{username} disconnected")
            
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast(self, message_data):
        """Broadcast a message to all connected clients"""
        message_json = json.dumps(message_data)
        
        # Send to all connected clients
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.send(message_json.encode('utf-8'))
            except:
                # If sending fails, the client is probably disconnected
                # The client will be removed in the handle_client method
                pass

if __name__ == "__main__":
    # Create and start the chat server
    server = ChatServer()
    
    # Start the server in the main thread
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopping...")
    finally:
        server.stop()