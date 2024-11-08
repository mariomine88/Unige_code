package assignment.user;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.ArrayList;


import assignment.cart.Cart;


public class UsersManager {

    public final static String basicUserID = "User00-";
    public final static List<User> users = new ArrayList<User>();


    public boolean findUserFromDB(String userID) throws SQLException {
        try (Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydatabase", basicUserID+userID, "password");) {
            String query = "select firstname, lastname " + "from USERS where username="+ (basicUserID+userID);
            PreparedStatement stmt = conn.prepareStatement(query);
            ResultSet rs = stmt.executeQuery();
            while (rs.next())
                if(rs != null)
                    return true;
            return false;

        } catch (SQLException e) {
            return false;
        }
    }

    void addUser(User user) throws SQLException{
        if(!findUserFromDB(user.getUserID()))
            users.add(user);
    }
    
    void removeEmptyTitlesFromUser(User user) {      
        List<String> titles = user.getTitles();
        for (int i = 0; i < titles.size(); i++) {
          if (titles.get(i).isEmpty()) {
            titles.remove(i); 
          }
        }
    }

    void addCartToUser(User user, Cart cart) throws Exception{
        try {
            user.linkCart(cart);
        } catch (Exception e) {
            throw e;
        }
    }









}
