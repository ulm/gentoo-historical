DROP TABLE IF EXISTS package;
CREATE TABLE package
(
	category VARCHAR(30),
	name VARCHAR(40),
	homepage VARCHAR(100),
	description VARCHAR(180),
	license VARCHAR(30),
    new TINYINT(4),
	PRIMARY KEY (category,name)
)
