package server;
public class UnlimitedServer extends Server {
    
    public UnlimitedServer(int port) {
        super(port ,new StringQueue()); // Unlimited queue
    }
    
    
    public static void main(String[] args) {
        int port = 8080; // Default port
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid port number. Using default port 8080.");
            }
        }
        
        System.out.println("Server started on port " + port + " with unlimited capacity");
        UnlimitedServer server = new UnlimitedServer(port);
        server.start();
    }
}