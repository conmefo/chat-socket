package com.lmeow.chat_server;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class EchoClient {

    public static void main(String[] args) {
        final String HOST = "localhost"; // 'localhost' means "this same computer"
        final int PORT = 6789;           // Must match the server's port
        System.out.println("Echo Client: Starting up...");

        try (Socket socket = new Socket(HOST, PORT)) {
            System.out.println("Echo Client: Successfully connected to server.");

            // Setup tools to read from and write to the server
            PrintWriter writer = new PrintWriter(socket.getOutputStream(), true);
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            // Setup a tool to read what YOU type in the console
            BufferedReader consoleReader = new BufferedReader(new InputStreamReader(System.in));

            System.out.print("Echo Client: Enter a message to send to the server: ");
            String messageToSend = consoleReader.readLine();

            // Send your message to the server
            writer.println(messageToSend);
            System.out.println("Echo Client: Sent '" + messageToSend + "' to the server.");

            // Wait for the server's response and read it
            String serverResponse = reader.readLine();
            System.out.println("Echo Client: Received response from server: '" + serverResponse + "'");

            System.out.println("Echo Client: Closing connection.");

        } catch (Exception e) {
            System.err.println("Echo Client: An error occurred: " + e.getMessage());
        }
    }
}