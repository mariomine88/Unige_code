package assignment.cart;

public class Product {
    private String id;
    private String name;
    private String description;
    private double unitPrice;
    private int category;
    private String brand;
    private int stockQuantity;
    private boolean isAvailable;

    public Product(String id, String name, String description, double unitPrice, int category) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.unitPrice = unitPrice;
        this.category = category;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public double getUnitPrice() {
        return unitPrice;
    }

    public void setUnitPrice(double unitPrice) {
        this.unitPrice = unitPrice;
    }

    public int getCategory() {
        return category;
    }

    public void setCategory(int category) {
        this.category = category;
    }

    public String getBrand() {
        return brand;
    }
    
    public void setBrand(String brand) {
        this.brand = brand;
    }
    
    public int getStockQuantity() {
        return stockQuantity;
    }
    
    public void setStockQuantity(int stockQuantity) {
        this.stockQuantity = stockQuantity;
    }
    
    public boolean getisAvailable() {
        return isAvailable;
    }
    
    public void setIsAvailable(boolean isAvailable) {
        this.isAvailable = isAvailable; 
    }

    public void setNecesaryDetailedProduct(String id, String name, String description, double unitPrice, 
    int category) {
            this.id = id;
            this.name = name;
            this.description = description;
            this.unitPrice = unitPrice;
            this.category = category;
        }


    public void setnotNecesaryDetailedProduct( String brand, int stockQuantity, boolean isAvailable) {
            this.brand = brand;
            this.stockQuantity = stockQuantity;
            this.isAvailable = isAvailable;
    }
    


}
