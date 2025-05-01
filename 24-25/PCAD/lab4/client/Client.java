package client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public abstract class Client {
    protected final String host;
    protected final int port;
    
    public Client(String host, int port) {
        this.host = host;
        this.port = port;
    }
    
    protected Socket createSocket() throws IOException {
        return new Socket(host, port);
    }
    
    protected static int parsePort(String portStr) {
        try {
            return Integer.parseInt(portStr);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid port number");
        }
    }
}