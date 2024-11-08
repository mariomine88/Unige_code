package assignment.user;


import java.util.List;

import assignment.cart.Cart;

import java.util.ArrayList; 

public class User {
    private String userID; 
    private String username; 
    private String firstname; 
    private String lastname;
    private List<String> titles = new ArrayList<String>();
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
        if(accountActive)
            return true;
        return false;
    }

    public boolean deactivateAccount(String id) {
        if (accountActive && this.userID == id) {
            accountActive = false;
            return true;
        }
        return false;
    }

    public boolean isEquals(User u){
        return u.userID == this.userID;
    }

    public void printUserInfo() {
        System.out.println("User Info: " + firstname + " " + lastname + " (Username: " + username + ")");
    }

    public void linkCart(Cart cart) throws Exception{
        if(cart == null)
            throw new Exception();
        this.cart = cart;
    }

    public Cart getCart(){
        return cart;
    }

    public String printAllRoles(){
        return roles.toString();
    }

    public void PrintEveryRole(){
        for (int i = roles.length; i > 0; i++){
            System.out.println(roles[i]);
        }
    }



}
