package server;
public class LimitedFifoServer extends Server {
    
    public LimitedFifoServer(int port, int queueCapacity) {
        super(port, new StringQueue(queueCapacity)); // Limited queue
    }
    
    public static void main(String[] args) {
        int port = 8080; // Default port
        int capacity = 5; // Default capacity
        
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid port number. Using default port 8080.");
            }
        }
        
        if (args.length > 1) {
            try {
                capacity = Integer.parseInt(args[1]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid capacity. Using default capacity 5.");
            }
        }
        
        System.out.println("Server started on port " + port + " with capacity " + capacity);
        LimitedFifoServer server = new LimitedFifoServer(port, capacity);
        server.start();
    }
}