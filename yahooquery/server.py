import json
import time


from yahooquery.login import YahooSelenium

import logging
import socket
from yahooquery.ticker import Ticker
from yahooquery import misc
import urllib.parse
from selenium.webdriver.common.by import By


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def construct_get_url(base_url, params):
    # Parse the base URL to extract its components
    parsed_url = urllib.parse.urlparse(base_url)

    # Create a dictionary to hold the query parameters
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # Update the dictionary with the provided parameters
    for key, value in params.items():
        query_params[key] = value

    # Convert the updated parameters back to a query string
    query_string = urllib.parse.urlencode(query_params, doseq=True)

    # Reconstruct the URL with the updated query string
    updated_url = urllib.parse.urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        query_string,
        parsed_url.fragment
    ))

    return updated_url

class Response:
    def __init__(self, url, data):
        self.url=url
        self.data = json.loads(data)
    def json(self):
        return self.data
    
class Session:
    def __init__(self) -> None:
        self.yahoo = YahooSelenium()
        self.driver = self.yahoo.driver

    def get_exchanges(self):
        return misc.get_exchanges()
    
    def get_ticker(self, ticker):
        return Ticker(ticker, session=self)
    
    def get(self,url ,params):
        print(url)
        print(params)
        full_url = construct_get_url(url, params)
        self.yahoo.driver.get(full_url)
        body = self.driver.find_element(By.TAG_NAME, 'pre')
        html_body = body.get_attribute('innerHTML')
        return Response(url, html_body)
    
    def close(self):
        self.driver.close()


class DataServer:
    def __init__(self, host='localhost', port=7979):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"Server started on {self.host}:{self.port}")
        self.session=Session()

    def start(self):
        #print(self.session.get_exchanges())
        ticker = self.session.get_ticker('AAPL')
        print(ticker.asset_profile)
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Got a connection from {addr}")
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    client_socket.sendall(data)
                client_socket.close()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            self.server_socket.close()
            self.session.close()


def main():
    server = DataServer()
    server.start()


if __name__ == '__main__':
    main()
