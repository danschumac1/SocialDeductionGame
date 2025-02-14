import socket
import selectors
import types
from typing import Dict


class ChatServer:
    """
    A TCP-based chat server that handles multiple clients and includes a chatbot.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 65432):
        """
        Initializes the chat server.

        Args:
            host (str): The IP address to bind the server to.
            port (int): The port number for the server.
        """
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.clients: Dict[socket.socket, str] = {}

    def chatbot_response(self, message: str) -> str:
        """
        Generates a response for the chatbot.

        Args:
            message (str): The received message.

        Returns:
            str: The chatbot's response.
        """
        responses = {
            "hello": "Hello! How can I assist you?",
            "who are you": "I'm a chatbot here to help!",
            "bye": "Goodbye! Have a great day!",
        }
        return responses.get(message.lower(), "I'm not sure what you mean. 🤖")

    def accept_connection(self, sock: socket.socket) -> None:
        """
        Accepts a new client connection.

        Args:
            sock (socket.socket): The listening socket.
        """
        conn, addr = sock.accept()
        print(f"New connection from {addr}")
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, data=types.SimpleNamespace(addr=addr))
        self.clients[conn] = f"{addr[0]}:{addr[1]}"

    def handle_client(self, sock: socket.socket) -> None:
        """
        Handles incoming messages from a client.

        Args:
            sock (socket.socket): The client's socket.
        """
        try:
            data = sock.recv(1024)
            if data:
                message = data.decode().strip()
                sender = self.clients.get(sock, "Unknown")
                print(f"Received from {sender}: {message}")

                # Broadcast message to all clients
                self.broadcast_message(f"{sender}: {message}")

                # Generate chatbot response
                bot_reply = self.chatbot_response(message)
                self.broadcast_message(f"Chatbot: {bot_reply}")

            else:
                self.disconnect_client(sock)

        except ConnectionResetError:
            self.disconnect_client(sock)

    def broadcast_message(self, message: str) -> None:
        """
        Sends a message to all connected clients.

        Args:
            message (str): The message to broadcast.
        """
        print(f"Broadcasting: {message}")
        for client in self.clients.keys():
            try:
                client.sendall(message.encode())
            except:
                self.disconnect_client(client)

    def disconnect_client(self, sock: socket.socket) -> None:
        """
        Removes a client from the server.

        Args:
            sock (socket.socket): The client's socket.
        """
        addr = self.clients.pop(sock, None)
        if addr:
            print(f"Client {addr} disconnected.")
        self.sel.unregister(sock)
        sock.close()

    def run(self) -> None:
        """
        Starts the chat server.
        """
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()
        server_sock.setblocking(False)
        self.sel.register(server_sock, selectors.EVENT_READ, data=None)

        print(f"Server running on {self.host}:{self.port}")

        try:
            while True:
                events = self.sel.select()
                for key, _ in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        self.handle_client(key.fileobj)
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            server_sock.close()


if __name__ == "__main__":
    server = ChatServer()
    server.run()
