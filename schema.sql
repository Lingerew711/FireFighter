DROP TABLE IF EXISTS  USERS cascade ; 
DROP TABLE IF EXISTS  LOCATIONS cascade ; 


CREATE TABLE USERS (
    u_id SERIAL,
    c_name VARCHAR(150),
    p_number VARCHAR(30),
    profile_url VARCHAR(255),
    PRIMARY KEY(u_id) 
);

CREATE TABLE LOCATIONS (
location_id INT(10) NOT NULL AUTO_INCREMENT,
C_name VARCHAR(150) NOT NULL,
C_address VARCHAR(255) NOT NULL,
lat FLOAT(10,6) NOT NULL,
lon FLOAT(10,6) NOT NULL,
tag TEXT NOT NULL,
PRIMARY KEY (location_id)
FOREIGN KEY(c_name) REFERENCES USERS(u_id),
)