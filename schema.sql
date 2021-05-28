DROP TABLE IF EXISTS  USERS cascade ; 


CREATE TABLE USERS (
    u_id SERIAL,
    c_name VARCHAR(150),
    p_number VARCHAR(30),
    profile_url VARCHAR(255),
    PRIMARY KEY(id) 
);