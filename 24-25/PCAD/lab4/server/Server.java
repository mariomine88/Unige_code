package server;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public abstract class Server {
    protected final int port;
    protected final StringQueue queue;
    protected final ExecutorService threadPool;
    protected volatile boolean running = true;

    public Server(int port ,StringQueue queue) {
        this.port = port;
        this.queue = queue;
        this.threadPool = Executors.newCachedThreadPool();
    }


    public void start() {
        try (ServerSocket serverSocket = new ServerSocket(port)) {
            
            while (running) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Client connected: " + clientSocket.getInetAddress());
                threadPool.execute(new ClientHandler(clientSocket, queue));
            }
        } catch (IOException e) {
            System.err.println("Server error: " + e.getMessage());
        } finally {
            threadPool.shutdown();
        }
    }

    public void stop() {
        running = false;
        threadPool.shutdown();
    }
}