import http.client
import json
import time
import pymysql


class PriceRecord:

    def __init__(self, dateTimeSec, exchangeName, currencyPair, price, dateTime, priceType ):
        self.dataTimeSec = dateTimeSec
        self.exchangeName = exchangeName
        self.currencyPair = currencyPair
        self.price = price
        self.dateTime = dateTime
        self.priceType = priceType

    def __str__(self):
        return str( self.toMap() )


    # Returns a sql statement ready to insert it into bd
    def getSQLInsertStatement(self, bd):
        sql = 'insert into coin_price(date_time_sec, exchange_id, currency_pair_id, price, date_time, price_type_id) '
        sql = sql + 'values(' + str(self.dataTimeSec) + ', '
        sql = sql + str( self.getExchangeId(bd) ) + ', '
        sql = sql + str( self.getCurrencyPairId(bd) ) + ', '
        sql = sql + str(self.price) + ', '
        sql = sql + 'NOW(), '
        sql = sql + str( self.getPriceTypeId(bd) ) + ')'
        return sql

    # Returns the id from the database related with its currency Pair
    def getCurrencyPairId(self, db):
        cursor = db.cursor()
        sql = 'select id from currency_pair where name = \"' + self.currencyPair + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        return data

    # Return the id from the database related with its exchange Name
    def getExchangeId(self, db):
        cursor = db.cursor()
        sql = 'select id from exchange where name = \"' + self.exchangeName + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        return data

    # Return the id from the database related with its price type
    def getPriceTypeId(self, db):
        cursor = db.cursor()
        sql = 'select id from price_type where name = \"' + self.priceType + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        return data

    def toMap(self):
        mapa = {}
        mapa['dateTimeSec'] = self.dataTimeSec
        mapa['exchangeName'] = self.exchangeName
        mapa['currencyPair'] = self.currencyPair
        mapa['price'] = self.price
        mapa['dateTime'] = self.dateTime
        mapa['priceType'] = self.priceType
        return mapa




class PriceDownloader:


    USER_AGENT = 'Mozilla/5.0'
    REQUEST_METHOD = 'GET'
    USER_AGENT_HEADER = 'User-Agent'
    HTTP_DOWNLOAD_ERROR = 'Error while downloading http request: '
    HTTP_VALID_STATUS = 200
    FILE_MODE = 'a'
    FILE_SAVE_ERROR = 'Error while writing the file '

    BITSO = 'Bitso'

    BTC_MXN = 'btc_mxn'
    ETH_MXN = 'eth_mxn'
    XRP_MXN = 'xrp_mxn'

    PRICE_LAST = 'last'



    # CONFIGURATION

    def __init__(self, host, resource, exchangeName, currencyPair, priceType):
        self.host = host
        self.resource = resource
        self.exchangeName = exchangeName
        self.currencyPair = currencyPair
        self.priceType = priceType

    def setDatabaseConnection(self, db):
        self.db = db

    def setStoreFileName(self, fileName):
        self.fileName = fileName







    # Ask for a file with prices from a online exchange
    # It return a string that may be a json
    def requestPriceFromExchange(self):
        return PriceDownloader.httpRequest(self.host, self.resource)

    # Parse price from Bitso file, returns integer with price
    def extractLastPriceBitso(self, data):
        jsonString = json.loads(data)
        payload = jsonString['payload']
        lastPrice = payload['last']
        return lastPrice

    # Retuns a PriceRecord object from data downloaded from exchange
    def generatePriceRecord(self, data):
        dateTimeSec = time.time()
        exchangeName = self.exchangeName
        currencyPair = self.currencyPair
        price = self.extractLastPriceBitso(data)
        dateTime = time.asctime()
        priceType = self.priceType
        pr = PriceRecord(dateTimeSec,exchangeName,currencyPair,price,dateTime,priceType)
        return pr

    # Stores a priceRecord object to database
    def savePriceRecordToDatabase(self, priceRecord):
        sql = priceRecord.getSQLInsertStatement(self.db)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        except Exception as err:
            print(err)












    # STATIC METHODS

    @staticmethod
    def httpRequest(host, resource):
        data = None
        try:
            headers = {PriceDownloader.USER_AGENT_HEADER: PriceDownloader.USER_AGENT}
            conn = http.client.HTTPSConnection(host)
            conn.request(PriceDownloader.REQUEST_METHOD, resource, '', headers)
            ans = conn.getresponse()
            if ans.status == PriceDownloader.HTTP_VALID_STATUS:
                data = ans.read()
        except Exception as err:
            print(PriceDownloader.HTTP_DOWNLOAD_ERROR, host + resource)
            print(err)

        data = data.decode('utf-8')
        return data






    # Unused methods

    # Downloads the price from a exchange and
    # stores it into a file
    def downloadPrice(self):
        data = self.requestData()
        if data == None:
            return
        priceLine = self.generatePriceLine(data)
        if priceLine == None:
            return
        print(priceLine)
        self.savePriceLine(priceLine)

    # Saves the priceLine String into a File
    def savePriceLine(self, priceLine):
        try:
            myfile = open(self.fileName, PriceDownloader.FILE_MODE)
            myfile.write(priceLine)
        except Exception:
            print(PriceDownloader.FILE_SAVE_ERROR, self.fileName)
        finally:
            myfile.close()

    # Generates a json string array from data
    # Array includes [ Exchange_name, currency_pair, price, date , seconds since epoch ]
    def generatePriceLine(self, data):
        price = None
        if self.exchangeName==PriceDownloader.BITSO:
            price = self.extractLastPriceBitso(data)
        priceLine = []
        priceLine.append(self.exchangeName)
        priceLine.append(self.currencyPair)
        priceLine.append(price)
        priceLine.append(time.asctime())
        priceLine.append( str(time.time()) )

        jsonPriceLine = json.dumps(priceLine)
        jsonPriceLine = jsonPriceLine + '\n'
        return jsonPriceLine






def test1():
    data = PriceDownloader.httpRequest('api.bitso.com', '/v3/ticker/?book=xrp_mxn')
    print(data)

def test2():
    priceDownloader = PriceDownloader('api.bitso.com', '/v3/ticker/?book=xrp_mxn','prueba_xrp.json',PriceDownloader.BITSO,'xrp_mxn')
    priceDownloader.downloadPrice()

def test3():
    priceDownloader = PriceDownloader('api.bitso.com', '/v3/ticker/?book=xrp_mxn', 'prueba_xrp.json',
                                      PriceDownloader.BITSO, 'xrp_mxn')

    db = pymysql.connect("localhost", "root", "root", "crypto_prices")
    priceDownloader.setDatabaseConnection(db)
    priceDownloader.getCurrencyPairId(PriceDownloader.XRP_MXN)

def test4():
    priceDownloader = PriceDownloader('api.bitso.com', '/v3/ticker/?book=xrp_mxn',
                                      PriceDownloader.BITSO, PriceDownloader.XRP_MXN, PriceDownloader.PRICE_LAST )
    db = pymysql.connect("localhost", "root", "root", "crypto_prices")
    priceDownloader.setDatabaseConnection(db)
    pd = priceDownloader
    data = pd.requestPriceFromExchange()
    print(data)
    print()
    pr = pd.generatePriceRecord(data)
    print(pr)
    print()
    time.sleep(2)
    sql = pr.getSQLInsertStatement(db)
    print(sql)
    print()
    time.sleep(1)
    pd.savePriceRecordToDatabase(pr)



test4()