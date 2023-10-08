import time


from yahooquery.login import YahooSelenium

import logging
import socket
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataServer:
    def __init__(self, host='localhost', port=7979):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"Server started on {self.host}:{self.port}")
        self. yahoo = YahooSelenium()

    def start(self):
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
            self.yahoo.driver.quit()


def main():
    server = DataServer()
    server.start()


if __name__ == '__main__':
    main()
