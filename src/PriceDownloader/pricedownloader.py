import http.client
import json
import time
import pymysql
import threading
import traceback


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
        sql = None
        try:
            sql = 'insert into coin_price(date_time_sec, exchange_id, currency_pair_id, price, date_time, price_type_id) '
            sql = sql + 'values(' + str(self.dataTimeSec) + ', '
            sql = sql + str( self.getExchangeId(bd) ) + ', '
            sql = sql + str( self.getCurrencyPairId(bd) ) + ', '
            sql = sql + str(self.price) + ', '
            sql = sql + 'NOW(), '
            sql = sql + str( self.getPriceTypeId(bd) ) + ')'
        except Exception as err:
            th = threading.current_thread()
            print(str(err) + '\n')
            print(th.name, PriceDownloader.SQL_SELECT_ERROR)
            print()
        return sql

    # Returns the id from the database related with its currency Pair
    def getCurrencyPairId(self, db):
        cursor = db.cursor()
        sql = 'select id from currency_pair where name = \"' + self.currencyPair + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        cursor.close()
        return data

    # Return the id from the database related with its exchange Name
    def getExchangeId(self, db):
        cursor = db.cursor()
        sql = 'select id from exchange where name = \"' + self.exchangeName + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        cursor.close()
        return data

    # Return the id from the database related with its price type
    def getPriceTypeId(self, db):
        cursor = db.cursor()
        sql = 'select id from price_type where name = \"' + self.priceType + '\"'
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        cursor.close()
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

    # HTTP CONNECTION PARAMENTERS

    USER_AGENT = 'Mozilla/5.0'
    REQUEST_METHOD = 'GET'
    USER_AGENT_HEADER = 'User-Agent'
    HTTP_VALID_STATUS = 200

    # ERROR MESSAGES

    JSON_FILE_PARSING_ERROR = 'Error uploading or parsing json file : '
    BITSO_JSON_LAST_PRICE_ERROR = 'Error parsing last price from bitso file'
    BITFINEX_JSON_LAST_PRICE_ERROR = 'Error parsing last price from bitfinex file'
    FILE_SAVE_ERROR = 'Error while writing the file '
    HTTP_DOWNLOAD_ERROR = 'Error while downloading http request: '
    DOWNLOAD_NOT_FINISHED_ERROR = 'Download could not be finished '
    SQL_INSERT_ERROR = 'Error while saving price into database '
    SQL_SELECT_ERROR = 'Error while extracting information from database '

    # EXCHANGES NAMES

    BITSO = 'bitso'
    BITFINEX = 'bitfinex'

    # CURRENCY PAIRS

    BTC_MXN = 'btc_mxn'
    ETH_MXN = 'eth_mxn'
    XRP_MXN = 'xrp_mxn'
    BTC_USD = 'btc_usd'
    XRP_USD = 'xrp_usd'
    ETH_USD = 'eth_usd'
    BCH_USD = 'bch_usd'
    LTC_USD = 'ltc_usd'
    IOT_USD = 'iot_usd'
    XMR_USD = 'xmr_usd'



    STARTED_SUCCESFULLY = 'Pricedownloader started succesfully '
    PRICE_DOWNLOAD_SUCCESFULL = 'Price downloaded succesfully'
    WAITING_FOR_NEXT_DOWNLOAD = 'Waiting...'
    DOWNLOADER_STOPPED = 'Stopped'
    FILE_MODE = 'a'
    EXCHANGES_URLS_FILE_NAME = '../../database/exchanges_paths.json'
    DEFAULT_WAIT_TIME = 5*60
    HOSTS = 'hosts'
    RESOURCES = 'resources'
    PRICE_LAST = 'last'
    EXCHANGES_URL_MAP = None
    LAST_PRICE_EXTRACTOR = {}






    # CONFIGURATION

    def __init__(self, host, resource, exchangeName, currencyPair, priceType):
        self.host = host
        self.resource = resource
        self.exchangeName = exchangeName
        self.currencyPair = currencyPair
        self.priceType = priceType
        self.wait_time = PriceDownloader.DEFAULT_WAIT_TIME
        self.db = None

    def __str__(self):
        mystr = 'PriceDownloader {'
        mystr = mystr + 'Exchange: ' + self.exchangeName + '\n'
        mystr = mystr +'Currency Pair: ' + self.currencyPair + '\n'
        mystr = mystr + 'Price Type: ' + self.priceType + '\n'
        mystr = mystr + 'Database status: '
        mystr = mystr + ( 'disconnected' if self.db==None  else 'connected' ) + '\n'
        mystr = mystr + '}\n'
        return mystr

    def setDatabaseConnection(self, db):
        self.db = db

    def setStoreFileName(self, fileName):
        self.fileName = fileName

    def setWaitTime(self,wait_time):
        self.wait_time = wait_time

    def getIdentifier(self):
        th = threading.current_thread()
        mystr = '[' + th.name + ', ' + self.exchangeName + ', ' + self.currencyPair + ']'
        return mystr






    # MAIN METHODS FOR DOWNLOADING, PARSING AND SAVING


    # Ask for a file with prices from a online exchange
    # It return a string that may be a json
    def requestPriceFromExchange(self):
        return PriceDownloader.httpRequest(self.host, self.resource)

    # Retuns a PriceRecord object from data downloaded from exchange
    def generatePriceRecord(self, data):
        pr = None
        extractor = PriceDownloader.LAST_PRICE_EXTRACTOR[self.exchangeName]
        price = extractor(data)
        if price!=None:
            dateTimeSec = time.time()
            exchangeName = self.exchangeName
            currencyPair = self.currencyPair
            dateTime = time.asctime()
            priceType = self.priceType
            pr = PriceRecord(dateTimeSec,exchangeName,currencyPair,price,dateTime,priceType)
        return pr

    # Stores a priceRecord object to database
    def savePriceRecordToDatabase(self, priceRecord):
        sql = priceRecord.getSQLInsertStatement(self.db)
        result = False
        if sql != None :
            try:
                cursor = self.db.cursor()
                cursor.execute(sql)
                cursor.close()
                self.db.commit()
                result = True
            except Exception as err:
                print(self.getIdentifier(), PriceDownloader.SQL_INSERT_ERROR , '\n' )
                print(traceback.format_exc())
                print(err,'\n')
        return result
    # request a file from the exchange, extracts the price and stores it 
    # in the database
    def downloadLastPrice(self):
        data = self.requestPriceFromExchange()
        if data==None :
            return PriceDownloader.DOWNLOAD_NOT_FINISHED_ERROR
        pr = self.generatePriceRecord(data)
        if pr==None :
            return PriceDownloader.DOWNLOAD_NOT_FINISHED_ERROR
        ans = self.savePriceRecordToDatabase(pr)
        if ans==False:
            return PriceDownloader.DOWNLOAD_NOT_FINISHED_ERROR
        return PriceDownloader.PRICE_DOWNLOAD_SUCCESFULL

    # Main function of the class, infinite loop witch downloads a price and
    # stores it in a database, then it sleeps for some time
    def begin(self):
        self.startSuccefulMessage()
        while self.runningFlag :
            result = self.downloadLastPrice()
            self.downloadResultMessage(result)
            self.waitingMessage()
            time.sleep(self.wait_time)
        self.stopMessage()





    # STATUS MESSAGES

    def startSuccefulMessage(self):
        print(self.getIdentifier(), PriceDownloader.STARTED_SUCCESFULLY)
        print()

    def downloadResultMessage(self,result):
        print(self.getIdentifier(), result)
        print()

    def waitingMessage(self):
        print(self.getIdentifier(), PriceDownloader.WAITING_FOR_NEXT_DOWNLOAD)
        print()

    def stopMessage(self):
        print(self.getIdentifier(), PriceDownloader.DOWNLOADER_STOPPED )
        print()





    # CONCURRENT METHODS

    
    def start(self):
        th = threading.Thread(target=self.begin)
        self.runningFlag = True
        th.start()
        self.myThread = th
        return th

    def stop(self):
        self.runningFlag = False




    # PRICE EXTRACTORS

    # Parse price from Bitso file, returns integer with price
    @staticmethod
    def extractLastPriceBitso(data):
        lastPrice = None
        try:
            data = data.decode('utf-8')
            jsonString = json.loads(data)
            payload = jsonString['payload']
            lastPrice = payload['last']
        except Exception as err:
            print(PriceDownloader.BITSO_JSON_LAST_PRICE_ERROR)
            print(err)
        return lastPrice

    @staticmethod
    def extractLastPriceBitfinex(data):
        #print("extractLastPriceBitfinex",data)
        lastPrice = None
        try:
            data = data.decode('utf-8')
            jsonString = json.loads(data)
            lastPrice = jsonString['last_price']
        except Exception as err:
            print(PriceDownloader.BITFINEX_JSON_LAST_PRICE_ERROR)
            print(err)
        return lastPrice







    # STATIC METHODS

    # Merges all extractors function inside a dictionary
    @staticmethod
    def uploadLastPriceExtractors():
        PriceDownloader.LAST_PRICE_EXTRACTOR[PriceDownloader.BITSO] = PriceDownloader.extractLastPriceBitso
        PriceDownloader.LAST_PRICE_EXTRACTOR[PriceDownloader.BITFINEX] =PriceDownloader.extractLastPriceBitfinex

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
            else:
                print('Error descargando la informacion', ans.status )
        except Exception as err:
            print(PriceDownloader.HTTP_DOWNLOAD_ERROR, host + resource)
            print(err)
        return data

    # opens a file containing the host url of the exchanges 
    # and resources path
    # returns a dictionary 
    @staticmethod
    def uploadExchangesURLs():
        try:
            exchangesPathsFiles = open(PriceDownloader.EXCHANGES_URLS_FILE_NAME, 'r')
            jsonString = exchangesPathsFiles.read()
            data = json.loads(jsonString)
            return data
        except Exception as err:
            print( PriceDownloader.JSON_FILE_PARSING_ERROR + PriceDownloader.EXCHANGES_URLS_FILE_NAME)
            print(err)
        finally:
            exchangesPathsFiles.close()

    # returns host url associated wit exchangeName
    @staticmethod
    def getHostURL(exchangeName):
        return PriceDownloader.EXCHANGES_URL_MAP[PriceDownloader.HOSTS][exchangeName]

    # returns resource path associate with that exchangeName and currencyPath
    @staticmethod
    def getResourceURL(exchangeName, currencyPair):
        return PriceDownloader.EXCHANGES_URL_MAP[PriceDownloader.RESOURCES][exchangeName][currencyPair]








    # FACTORY METHODS

    # returns a PriceDownloader object with the given exchangeName and currencyPair
    # it is connected with the database and ready to use
    @staticmethod
    def getLastPriceDownloader(exchangeName, currencyPair, db):
        host = PriceDownloader.getHostURL(exchangeName)
        resource = PriceDownloader.getResourceURL(exchangeName, currencyPair)
        priceType = PriceDownloader.PRICE_LAST
        obj = PriceDownloader(host,resource,exchangeName,currencyPair,priceType)
        obj.setDatabaseConnection(db)
        return obj

    @staticmethod
    def getBitsoBtcMxn(db):
        return PriceDownloader.getLastPriceDownloader(PriceDownloader.BITSO, PriceDownloader.BTC_MXN, db)

    @staticmethod
    def getBitsoXrpMxn(db):
        return PriceDownloader.getLastPriceDownloader(PriceDownloader.BITSO, PriceDownloader.XRP_MXN, db)

    @staticmethod
    def getBitsoEthMxn(db):
        return PriceDownloader.getLastPriceDownloader(PriceDownloader.BITSO, PriceDownloader.ETH_MXN, db)

    @staticmethod
    def getBitfinexBtcUsd(db):
        return PriceDownloader.getLastPriceDownloader(PriceDownloader.BITFINEX, PriceDownloader.BTC_USD, db)






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



PriceDownloader.EXCHANGES_URL_MAP = PriceDownloader.uploadExchangesURLs()
PriceDownloader.uploadLastPriceExtractors()


class ValFelpo:


    def __init__(self, active_prices_file_name):
        self.active_prices_file_name = active_prices_file_name


    def start(self):
        my_pairs = open(self.active_prices_file_name, 'r')
        for line in my_pairs:
            exchange, currencyPair = line.split()
            db = pymysql.connect("localhost", "root", "root", "crypto_prices")
            pd = PriceDownloader.getLastPriceDownloader(exchange,currencyPair,db);
            pd.start()



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

def test5():
    PriceDownloader.uploadExchangesURLs()

def test6():
    db = pymysql.connect("localhost", "root", "didu.2015", "crypto_prices")
    pr = PriceDownloader.getBitsoBtcMxn(db)
    pr.downloadLastPrice()

def test7():
    db = pymysql.connect("localhost", "root", "root", "crypto_prices")
    pr = PriceDownloader.getBitsoBtcMxn(db)
    pr.setWaitTime(2*60)
    pr.start()

def test8():
    db = pymysql.connect("localhost", "root", "root", "crypto_prices")
    pr = PriceDownloader.getBitfinexBtcUsd(db)
    pr.start()

def test9():
    db = pymysql.connect("localhost", "root", "root", "crypto_prices")
    pr = PriceDownloader.getBitfinexBtcUsd(db)
    pr.start()

def test10():
    db1 = pymysql.connect("localhost", "root", "root", "crypto_prices")
    db2 = pymysql.connect("localhost", "root", "root", "crypto_prices")
    db3 = pymysql.connect("localhost", "root", "root", "crypto_prices")
    prbitsobtc = PriceDownloader.getBitsoBtcMxn(db1)
    prbitsoxrp = PriceDownloader.getBitsoXrpMxn(db2)
    prbitfinexbtc = PriceDownloader.getBitfinexBtcUsd(db3)
    prbitsobtc.setWaitTime(2*60)
    prbitsoxrp.setWaitTime(2*60)
    prbitfinexbtc.setWaitTime(2*60)
    prbitsobtc.start()
    prbitsoxrp.start()
    prbitfinexbtc.start()

    time.sleep(10)
    #prbitsobtc.stop()
    #prbitsoxrp.stop()
    #prbitfinexbtc.stop()

def test11():
    vf = ValFelpo('active_prices.txt')
    vf.start()

test11()