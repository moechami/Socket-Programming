import socket
import threading
import os

# set the server port and default values
SERVER_PORT = 7494
PASSWORD = "123!abc"
DEFAULT_MESSAGE = "An apple a day keeps the doctor away."

# shared message and lock for thread safety
message_of_the_day = DEFAULT_MESSAGE
lock = threading.Lock()

# the function to handle each connected client
def handle_client(client_socket, addr):
    global message_of_the_day
    print(f"[NEW CONNECTION] {addr} connected.")

    expecting_message = False  # flag to track if the next line should be stored as the message

    while True:
        try:
            # receive data from client
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break

            print(f"[RECEIVED FROM {addr}] {data}")

            if expecting_message:
                # store the new message safely
                with lock:
                    message_of_the_day = data
                client_socket.sendall(b"200 OK\n")
                expecting_message = False
                continue

            # handles the MSGGET command
            if data == "MSGGET":
                client_socket.sendall(f"200 OK\n{message_of_the_day}\n".encode())

            # handles the MSGSTORE command
            elif data == "MSGSTORE":
                client_socket.sendall(b"200 OK\n")
                expecting_message = True

            # handles the QUIT command
            elif data == "QUIT":
                client_socket.sendall(b"200 OK\n")
                break

            # handles the SHUTDOWN command
            elif data == "SHUTDOWN":
                client_socket.sendall(b"300 PASSWORD REQUIRED\n")
                password = client_socket.recv(1024).decode().strip()
                if password == PASSWORD:
                    client_socket.sendall(b"200 OKAY\n")
                    client_socket.close()
                    print("[SHUTDOWN] server is shutting down.")
                    os._exit(0)  # force server shutdown
                else:
                    client_socket.sendall(b"301 WRONG PASSWORD\n")

            # handle an unknown command
            else:
                client_socket.sendall(b"400 BAD REQUEST\n")

        except Exception as e:
            print(f"[ERROR] {e}")
            break

    print(f"[DISCONNECTED] {addr} disconnected.")
    client_socket.close()

# main function to start the server
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(5)
    print(f"[STARTED] YAMOTD server listening on port {SERVER_PORT}...")

    while True:
        # accept new client connection
        client_sock, client_addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock, client_addr))
        thread.start()

if __name__ == "__main__":
    main()
