package com.lmeow.chat_server;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.springframework.stereotype.Component;
import jakarta.annotation.PostConstruct;

@Component
public class ChatServer {
    private final Map<String, ClientHandler> clients = new ConcurrentHashMap<>();
    private final ExecutorService pool = Executors.newCachedThreadPool();
    private static final int PORT = 5555;

    @PostConstruct
    public void startServer() {
        new Thread(() -> {
            try (ServerSocket serverSocket = new ServerSocket(PORT)){
                System.out.println("Chat Server is listening on port " + PORT);
                
                while (true){
                    Socket clientSocket = serverSocket.accept();
                    System.out.println("New client connected: " + clientSocket.getRemoteSocketAddress());
                    ClientHandler clientHandler = new ClientHandler(clientSocket, this);
                    pool.execute(clientHandler);
                }

            } catch (IOException e){
                System.err.println("Error in the server: " + e.getMessage());
            }
        }).start();
    }

    public void addClient(String username, ClientHandler clientHandler) {
        clients.put(username, clientHandler);
    }

    public void removeClient(String username) {
        clients.remove(username);
    }

    public void broadcast(ChatMessage message) {
        for (ClientHandler client : clients.values()) {
            client.sendMessage(message);
        }
    }
}
