package server;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class ClientHandler implements Runnable {
    private Socket clientSocket;
    private StringQueue stringQueue;

    public ClientHandler(Socket socket, StringQueue queue) {
        this.clientSocket = socket;
        this.stringQueue = queue;
    }

    @Override
    public void run() {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
             PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)) {

            String clientType = in.readLine();
            System.out.println("Client type: " + clientType);
            
            if ("producer".equals(clientType)) {
                handleProducer(in, out);
            } else if ("consumer".equals(clientType)) {
                handleConsumer(out);
            } else {
                System.out.println("Unknown client type: " + clientType);
            }
        } catch (IOException | InterruptedException e) {
            System.err.println("Error handling client: " + e.getMessage());
        } finally {
            try {
                clientSocket.close();
                System.out.println("Client disconnected");
            } catch (IOException e) {
                System.err.println("Error closing client socket: " + e.getMessage());
            }
        }
    }
    
    private void handleProducer(BufferedReader in, PrintWriter out) throws IOException, InterruptedException {
        out.println("okprod");
        String message = in.readLine();
        System.out.println("Received message from producer: " + message);
        stringQueue.add(message);
    }
    
    private void handleConsumer(PrintWriter out) throws InterruptedException {
        out.println("okcons");
        String message = stringQueue.remove();
        System.out.println("Sending message to consumer: " + message);
        out.println(message);
    }
}