import socket
import sys

# must match the server port
SERVER_PORT = 7494

# client main function
def main():
    if len(sys.argv) < 2:
        print("usage: python yamotd_client.py <server_ip>")
        return

    server_ip = sys.argv[1]

    # create TCP socket and connect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, SERVER_PORT))
        print(f"connected to YAMOTD server at {server_ip}:{SERVER_PORT}")

        while True:
            # get user command
            cmd = input("enter command (MSGGET, MSGSTORE, QUIT, SHUTDOWN): ").strip()

            # handle MSGGET
            if cmd == "MSGGET":
                s.sendall(b"MSGGET\n")
                response = s.recv(1024).decode()
                print(response)

            # handle MSGSTORE
            elif cmd == "MSGSTORE":
                s.sendall(b"MSGSTORE\n")
                ok = s.recv(1024).decode()
                if "200 OK" in ok:
                    msg = input("enter your message of the day: ").strip()
                    s.sendall((msg + "\n").encode())
                    final_ack = s.recv(1024).decode()
                    print(final_ack)

            # handle QUIT
            elif cmd == "QUIT":
                s.sendall(b"QUIT\n")
                response = s.recv(1024).decode()
                print(response)
                break

            # handle SHUTDOWN
            elif cmd == "SHUTDOWN":
                s.sendall(b"SHUTDOWN\n")
                response = s.recv(1024).decode()
                print(response)
                if "300 PASSWORD REQUIRED" in response:
                    password = input("enter shutdown password: ").strip()
                    s.sendall((password + "\n").encode())
                    final_ack = s.recv(1024).decode()
                    print(final_ack)
                    if "200 OKAY" in final_ack:
                        break

            else:
                print("invalid command. try again.")

if __name__ == "__main__":
    main()
