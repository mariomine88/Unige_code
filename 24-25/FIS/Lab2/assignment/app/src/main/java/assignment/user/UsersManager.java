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

    public static final  String BASIC_USER_ID = "User00-";
    public static final  List<User> users = new ArrayList<>();


    public boolean findUserFromDB(String userID) throws SQLException {
        try (Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydatabase", BASIC_USER_ID+userID, System.getenv("password"));) {
            String query = "select firstname, lastname " + "from USERS where username="+ (BASIC_USER_ID+userID);
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
        titles.removeIf(String::isEmpty);
    }

    void addCartToUser(User user, Cart cart) throws Exception{
            user.linkCart(cart);
            user.linkCart(cart);
        } catch (Exception e) {
            throw e;
        }
        user.linkCart(cart);
        } catch (Exception e) {
            throw e;
        }
    }









}
