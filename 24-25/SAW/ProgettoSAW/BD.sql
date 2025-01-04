CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL,
    activation_token VARCHAR(64)
    is_admin BOOLEAN NOT NULL DEFAULT FALSE;
);

CREATE TABLE auth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    selector CHAR(32) NOT NULL UNIQUE,
    token CHAR(64) NOT NULL,
    user_id INT NOT NULL,
    expires DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE password_resets (
    email VARCHAR(255) PRIMARY KEY,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE community (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    member_count INT DEFAULT 0,
    UNIQUE KEY unique_community_name (name)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    community_id INT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    like_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (community_id) REFERENCES community(id) ON DELETE SET NULL,
    INDEX idx_created_at (created_at),
    INDEX idx_like_count (like_count)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    like_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_at (created_at)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE follows (
    follower_id INT NOT NULL,
    followed_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE community_members (
    follower_id INT NOT NULL,
    community_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, community_id),
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (community_id) REFERENCES community(id) ON DELETE CASCADE
);

CREATE TABLE post_likes (
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE comment_likes (
    user_id INT NOT NULL,
    comment_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE
) DEFAULT CHARSET=utf8mb4;


--triger to be added

-- Trigger to remove expired tokens
DELIMITER //

CREATE TRIGGER cleanup_expired_tokens_trigger 
AFTER INSERT ON auth_tokens
FOR EACH ROW
BEGIN
    DELETE FROM auth_tokens WHERE expires < NOW();
END //

DELIMITER ;

-- Trigger for password reset tokens cleanup
DELIMITER //

CREATE TRIGGER cleanup_expired_password_resets
BEFORE INSERT ON password_resets
FOR EACH ROW
BEGIN
    DELETE FROM password_resets WHERE expires_at < NOW();
END //

DELIMITER ;

-- Trigger for updating member_count in community table
DELIMITER //

CREATE TRIGGER after_member_join
AFTER INSERT ON community_members
FOR EACH ROW
BEGIN
    UPDATE community 
    SET member_count = member_count + 1
    WHERE id = NEW.community_id;
END//

CREATE TRIGGER after_member_leave
AFTER DELETE ON community_members
FOR EACH ROW
BEGIN
    UPDATE community 
    SET member_count = member_count - 1
    WHERE id = OLD.community_id;
END//

DELIMITER ;

-- Triggers for maintaining like_count columns
DELIMITER //

CREATE TRIGGER after_post_like_insert
AFTER INSERT ON post_likes
FOR EACH ROW
BEGIN
    UPDATE posts SET like_count = like_count + 1
    WHERE id = NEW.post_id;
END //

CREATE TRIGGER after_post_like_delete
AFTER DELETE ON post_likes
FOR EACH ROW
BEGIN
    UPDATE posts SET like_count = like_count - 1
    WHERE id = OLD.post_id;
END //

CREATE TRIGGER after_comment_like_insert
AFTER INSERT ON comment_likes
FOR EACH ROW
BEGIN
    UPDATE comments SET like_count = like_count + 1
    WHERE id = NEW.comment_id;
END //

CREATE TRIGGER after_comment_like_delete
AFTER DELETE ON comment_likes
FOR EACH ROW
BEGIN
    UPDATE comments SET like_count = like_count - 1
    WHERE id = OLD.comment_id;
END //

DELIMITER ;