package client;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class ProducerClient {
    private final String host;
    private final int port;
    
    public ProducerClient(String host, int port) {
        this.host = host;
        this.port = port;
    }
    
    public void sendMessage(String message) {
        try (Socket socket = new Socket(host, port);
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
            
            // Identify as producer
            out.println("producer");
            
            // Wait for confirmation
            String response = in.readLine();
            if ("okprod".equals(response)) {
                // Send the message
                out.println(message);
                System.out.println("Message sent: " + message);
            } else {
                System.err.println("Unexpected server response: " + response);
            }
            
        } catch (IOException e) {
            System.err.println("Producer client error: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("Usage: java ProducerClient <host> <port> <message>");
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
        
        String message = args[2];
        
        ProducerClient client = new ProducerClient(host, port);
        client.sendMessage(message);
    }
}