


CREATE TABLE exchange (
	id 		SMALLINT 	NOT NULL AUTO_INCREMENT,
	name 	CHAR(35) 	NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE currency_pair (
	id 		SMALLINT 	NOT NULL AUTO_INCREMENT,
	name 	CHAR(35)	NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE price_type (
	id 		SMALLINT	NOT NULL AUTO_INCREMENT,
	name 	CHAR(30)	NOT NULL,
	PRIMARY KEY (id) 	
);



CREATE TABLE  coin_price (
	date_time_sec 		BIGINT 		NOT NULL,
	exchange_id 		SMALLINT 	NOT NULL,
	currency_pair_id 	SMALLINT 	NOT NULL,
	price 				DOUBLE	PRECISION(18,2)	NOT NULL,
	date_time 			DATETIME  	NOT NULL,
	price_type_id		SMALLINT 	NOT NULL,
	PRIMARY KEY (date_time_sec, exchange_id, currency_pair_id ),
	FOREIGN KEY (exchange_id)  REFERENCES exchange (id),
	FOREIGN KEY (currency_pair_id) REFERENCES currency_pair (id),
	FOREIGN KEY (price_type_id) REFERENCES price_type (id)
);





