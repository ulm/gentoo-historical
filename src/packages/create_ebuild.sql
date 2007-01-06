DROP TABLE IF EXISTS ebuild;
CREATE TABLE ebuild
(
	category VARCHAR(30),
	name VARCHAR(45),
	version VARCHAR(30) NOT NULL,
	when_found TIMESTAMP,
	arch VARCHAR(160),
	changelog MEDIUMTEXT,
    prevarch VARCHAR(160),
    is_masked TINYINT(4),
	PRIMARY KEY (category,name,version)
)
