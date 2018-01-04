

SELECT a.date_time , b.name as "Currency Pair ", c.name as "Exchange", a.price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id;


ALTER TABLE coin_price MODIFY price DOUBLE	PRECISION(18,2);


SELECT a.date_time_sec, a.date_time, b.name, c.name, a.price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn';


SELECT a.date_time_sec, a.date_time, b.name, c.name, a.price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'xrp_usd';


SELECT a.date_time_sec, a.date_time, b.name, c.name, a.price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'btc_usd';