package assignment.cart;

import java.util.HashMap;
import java.util.Map;

public class Cart {
    private Map<Product, Integer> products;

    public Cart() {
        this.products = new HashMap<>();
    }

    public void addProduct(Product product, int quantity) {
        if (quantity > 0)
            products.put(product, products.getOrDefault(product, 0) + quantity);
            else 
        products.put(product, products.getOrDefault(product, 0));

    }

    public void removeProduct(Product product) {
        products.remove(product);
    }

    public void updateProductQuantity(Product product, int quantity) {
        if (products.containsKey(product)==true)
            if (quantity <= 0) 
                removeProduct(product);
            else 
                products.put(product, quantity);
            
    }

    public double calculateTotal() {
        double total = 0.0;
        for (Map.Entry<Product, Integer> entry : products.entrySet()) {
            Product product = entry.getKey();
            int quantity = entry.getValue();
            total += product.getUnitPrice() * quantity; 
        }
        return total;
    }

    public Map<Product, Integer> getProducts() {
        return new HashMap<Product, Integer>(products);
    }

    public void clearCart() {
        products.clear();
    }

    public boolean calc(Cart cart1, Cart cart2) {
        if(this.calculateTotal() >= cart1.calculateTotal() && this.calculateTotal() >= cart2.calculateTotal())
            return true;
        else 
            return false;
    }

    public void calcHigher(Cart cart1, Cart cart2) {
        calc(cart2, cart1);
    }




}
