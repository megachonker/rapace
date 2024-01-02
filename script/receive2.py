import socket
import sys

def receive_udp_message(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('0.0.0.0', port))
            print(f"Listening for UDP messages on port {port}...")

            while True:
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                print(f"Received message: {data.decode()} from {addr}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])

    receive_udp_message(port)
