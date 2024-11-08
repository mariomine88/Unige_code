package assignment.user;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import assignment.cart.Cart;

public class User {
    private static final Logger logger = Logger.getLogger(User.class.getName());

    private String userID;
    private String username;
    private String firstname;
    private String lastname;
    private List<String> titles = new ArrayList<>();
    private String[] roles = new String[5];
    private boolean accountActive;
    private Cart cart;

    public User(String userID, String username, String firstname, String lastname,
                boolean accountActive, List<String> titles, String[] roles) {
        this.userID = userID;
        this.username = username;
        this.firstname = firstname;
        this.lastname = lastname;
        this.accountActive = accountActive;
        this.titles = titles;
        this.roles = roles;
    }

    public String getUserID() {
        return userID;
    }

    public String getUsername() {
        return username;
    }

    public String getFirstname() {
        return firstname;
    }

    public String getLastname() {
        return lastname;
    }

    public boolean isAccountActive() {
        return accountActive;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setAccountActive(boolean accountActive) {
        this.accountActive = accountActive;
    }

    public void updateUsername(String newUsername) {
        this.username = newUsername;
    }

    public List<String> getTitles(){
        return titles;
    }

    public boolean isActive(){
        return (accountActive);
    }

    public boolean deactivateAccount(String id) {
        if (accountActive && this.userID.equals(id)) {
            accountActive = false;
            return true;
        }
        return false;
    }

    public boolean isEquals(User u) {
        return u.userID.equals(this.userID);
    }

    public void printUserInfo() {
        logger.log(Level.INFO, "User Info: {0} {1} (Username: {2})", new Object[]{firstname, lastname, username});
    }

    public void linkCart(Cart cart) {
        if (cart == null)
            throw new IllegalArgumentException("Cart cannot be null");
        this.cart = cart;
    }

    public Cart getCart() {
        return cart;
    }

    public String printAllRoles() {
        return Arrays.toString(roles);
    }

    public void printEveryRole() {
        for (int i = roles.length; i > 0; i--) {
            logger.log(Level.INFO, roles[i]);
        }
    }
}
