CREATE TABLE UserData( usernameSpecialHash VARCHAR(70) NOT NULL,
                       privateKeyEncrypted VARCHAR(100) NOT NULL,
                       nameEncrypted       VARCHAR(100) NOT NULL,
                       sex                 CHAR(1)   NOT NULL,
                       age                 INT      NOT NULL,
                       balances            VARCHAR(60000) NOT NULL,
                       PRIMARY KEY(usernameSpecialHash)
);