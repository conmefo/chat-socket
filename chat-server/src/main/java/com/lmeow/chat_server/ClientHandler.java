package com.lmeow.chat_server;

import java.io.*;
import java.net.Socket;

import com.fasterxml.jackson.databind.ObjectMapper;

public class ClientHandler implements Runnable{
    private Socket clientSocket;
    private ChatServer server;
    private String username;
    private PrintWriter writer;

    public ClientHandler(Socket clientSocket, ChatServer server) {
        this.clientSocket = clientSocket;
        this.server = server;
    }

    @Override
    public void run() {
        try {
            InputStream input = clientSocket.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(input));

            OutputStream output = clientSocket.getOutputStream();
            this.writer = new PrintWriter(output, true);

            String line;

            while ((line = reader.readLine()) != null){
                ObjectMapper mapper = new ObjectMapper();
                ChatMessage chatMessage = mapper.readValue(line, ChatMessage.class);
                
                switch (chatMessage.getType()) {
                    case CONNECT:
                        this.username = chatMessage.getUsername();
                        server.addClient(this.username, this);
                        System.out.println(this.username + " has connected.");

                        ChatMessage joinMessage = new ChatMessage(MessageType.SYSTEM, ""
                            , this.username + " has joined the chat");
                        
                        server.broadcast(joinMessage);

                        break;
                    case CHAT:
                        System.out.println("Chat from " + this.username + ": " + chatMessage.getMessage());
                        chatMessage.setUsername(this.username);

                        server.broadcast(chatMessage);
                        break;
                    case DISCONNECT:
                        clientSocket.close();
                        return;
                }
            }
        } catch (IOException e) {

            e.printStackTrace();
        } finally {
            if (this.username != null) {
                System.out.println(this.username + " has disconnected.");
                server.removeClient(this.username);

                ChatMessage leaveMessage = new ChatMessage(MessageType.SYSTEM, "", 
                    this.username + " has left the chat.");

                server.broadcast(leaveMessage);
            }

            try {
                clientSocket.close();
            } catch (IOException e) {
            
            }
        }
    }

    void sendMessage(ChatMessage message) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            String jsonMessage = mapper.writeValueAsString(message);
            writer.println(jsonMessage);
        } catch (IOException e) {
            // We should probably remove the client if we can't send a message to them.
            System.err.println("Failed to send message to " + username + ". " + e.getMessage());
            server.removeClient(this.username);
        }
    }

    
}
