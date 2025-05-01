package server;
public class UnlimitedFifoServer extends Server {
    
    public UnlimitedFifoServer(int port) {
        super(port);
    }
    
    @Override
    protected StringQueue createQueue() {
        return new StringQueue(); // Unlimited queue
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
        
        UnlimitedFifoServer server = new UnlimitedFifoServer(port);
        server.start();
    }
}