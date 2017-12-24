import http.client
import json
import time

class PriceDownloader:



    USER_AGENT = 'Mozilla/5.0'
    REQUEST_METHOD = 'GET'
    USER_AGENT_HEADER = 'User-Agent'
    HTTP_DOWNLOAD_ERROR = 'Error while downloading http request: '
    HTTP_VALID_STATUS = 200
    FILE_MODE = 'a'
    FILE_SAVE_ERROR = 'Error while writing the file '
    BITSO = 'Bitso'





    def __init__(self, host, resource, fileName, exchangeName, currenciesPair):
        self.host = host
        self.resource = resource
        self.fileName = fileName
        self.exchangeName = exchangeName
        self.currenciesPair = currenciesPair








    # Ask for a file with prices from a online exchange
    def requestData(self):
        return PriceDownloader.httpRequest(self.host, self.resource)

    # Parse price from Bitso file
    def extractLastPriceBitso(self, data):
        jsonString = json.loads(data)
        payload = jsonString['payload']
        lastPrice = payload['last']
        return lastPrice

    # Generates a json string array from data
    # Array includes [ Exchange_name, currency_pair, price, date , seconds since epoch ]
    def generatePriceLine(self, data):
        price = None
        if self.exchangeName==PriceDownloader.BITSO:
            price = self.extractLastPriceBitso(data)
        priceLine = []
        priceLine.append(self.exchangeName)
        priceLine.append(self.currenciesPair)
        priceLine.append(price)
        priceLine.append(time.asctime())
        priceLine.append( str(time.time()) )

        jsonPriceLine = json.dumps(priceLine)
        jsonPriceLine = jsonPriceLine + '\n'
        return jsonPriceLine

    # Saves the priceLine String into a File
    def savePriceLine(self, priceLine):
        try:
            myfile = open(self.fileName, PriceDownloader.FILE_MODE)
            myfile.write(priceLine)
        except Exception:
            print(PriceDownloader.FILE_SAVE_ERROR, self.fileName)
        finally:
            myfile.close()

    # Downloads the price from a exchange and
    # stores it into a file
    def downloadPrice(self):
        data = self.requestData()
        if data==None:
            return
        priceLine = self.generatePriceLine(data)
        if priceLine==None:
            return
        print(priceLine)
        self.savePriceLine(priceLine)





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
        except Exception:
            print(PriceDownloader.HTTP_DOWNLOAD_ERROR, host + resource)

        data = data.decode('utf-8')
        return data








def test1():
    data = PriceDownloader.httpRequest('api.bitso.com', '/v3/ticker/?book=xrp_mxn')
    print(data)


def test2():
    priceDownloader = PriceDownloader('api.bitso.com', '/v3/ticker/?book=xrp_mxn','prueba_xrp.json',PriceDownloader.BITSO,'xrp_mxn')
    priceDownloader.downloadPrice()


test2()