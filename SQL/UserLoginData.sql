CREATE TABLE UserLoginData( hashedUsername  VARCHAR(70)  NOT NULL,
                            hashedPassword  VARCHAR(100)  NOT NULL,
                            encryptionKey   VARCHAR(100) NOT NULL,
                            PRIMARY KEY(hashedUsername)
);