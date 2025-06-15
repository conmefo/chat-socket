package com.lmeow.chat_server;

public class ChatMessage {
    private MessageType type;
    private String username;
    private String message;

    public ChatMessage (MessageType type, String username, String message){
        this.type = type;
        this.username = username;
        this.message = message;
    }

    public ChatMessage () {}

    public MessageType getType() {
        return type;
    }

    public void setType(MessageType type) {
        this.type = type;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
