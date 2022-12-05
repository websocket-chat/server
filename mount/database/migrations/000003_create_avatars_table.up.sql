CREATE TABLE avatars (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    breakpoint VARCHAR(255) NOT NULL,
    content_type VARCHAR(255) NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    filesize INT NOT NULL,
    public_url VARCHAR(512) NOT NULL,
    status VARCHAR(16) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
