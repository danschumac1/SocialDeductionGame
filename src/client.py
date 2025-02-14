import socket
import threading
from typing import NoReturn


class ChatClient:
    """
    A TCP-based chat client that connects to a chat server.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 65432):
        """
        Initializes the chat client.

        Args:
            host (str): The IP address of the server.
            port (int): The port number of the server.
        """
        self.host = host
        self.port = port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self) -> NoReturn:
        """
        Listens for incoming messages from the server.
        """
        try:
            while True:
                message = self.client_sock.recv(1024).decode()
                if message:
                    print(message)
                else:
                    print("Disconnected from server.")
                    break
        except:
            print("Connection lost.")
        finally:
            self.client_sock.close()

    def start(self) -> None:
        """
        Connects to the server and starts the chat.
        """
        self.client_sock.connect((self.host, self.port))
        print("Connected to chat. Type your message below:")

        # Start a background thread for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

        try:
            while True:
                message = input()
                if message.lower() == "exit":
                    break
                self.client_sock.sendall(message.encode())
        except KeyboardInterrupt:
            pass
        finally:
            self.client_sock.close()
            print("Disconnected.")


if __name__ == "__main__":
    client = ChatClient()
    client.start()
