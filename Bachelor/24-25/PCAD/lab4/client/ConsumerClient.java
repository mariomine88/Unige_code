package client;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class ConsumerClient {
    private final String host;
    private final int port;
    
    public ConsumerClient(String host, int port) {
        this.host = host;
        this.port = port;
    }
    
    public String receiveMessage() {
        try (Socket socket = new Socket(host, port);
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
            
            // Identify as consumer
            out.println("consumer");
            
            // Wait for confirmation
            String response = in.readLine();
            if ("okcons".equals(response)) {
                // Receive the message
                String message = in.readLine();
                System.out.println("Message received: " + message);
                return message;
            } else {
                System.err.println("Unexpected server response: " + response);
                return null;
            }
            
        } catch (IOException e) {
            System.err.println("Consumer client error: " + e.getMessage());
            return null;
        }
    }
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java ConsumerClient <host> <port>");
            return;
        }
        
        String host = args[0];
        int port;
        try {
            port = Integer.parseInt(args[1]);
        } catch (NumberFormatException e) {
            System.err.println("Invalid port number");
            return;
        }
        
        ConsumerClient client = new ConsumerClient(host, port);
        client.receiveMessage();
    }
}