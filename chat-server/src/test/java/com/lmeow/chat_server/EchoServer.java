package com.lmeow.chat_server;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class EchoServer {

    public static void main(String[] args) {
        final int PORT = 6789; // Let's use a different port for our test
        System.out.println("Echo Server: Starting up...");

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Echo Server: Waiting for a client to connect on port " + PORT + "...");

            // This line BLOCKS. The program will pause here until a client connects.
            Socket clientSocket = serverSocket.accept();

            System.out.println("Echo Server: Client connected! " + clientSocket.getRemoteSocketAddress());

            // Setup tools to read from and write to the client
            BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true); // true for auto-flush

            // Read one single line of text from the client.
            String clientMessage = reader.readLine();
            System.out.println("Echo Server: Received from client: '" + clientMessage + "'");

            // Send the same message back to the client.
            writer.println("You said: " + clientMessage);
            System.out.println("Echo Server: Sent echo back to client.");

            System.out.println("Echo Server: Closing connection and shutting down.");

        } catch (Exception e) {
            System.err.println("Echo Server: An error occurred: " + e.getMessage());
        }
    }
}