CREATE TABLE ebuild
(
	category VARCHAR(30),
	name VARCHAR(45),
	version VARCHAR(30) NOT NULL,
	when_found TIMESTAMP,
	arch VARCHAR(160),
	changelog MEDIUMTEXT,
	PRIMARY KEY (category,name,version)
)
