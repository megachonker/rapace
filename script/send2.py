import socket
import sys

def send_udp_message(source_port, dest_ip, dest_port, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', source_port))
            sock.sendto(message.encode(), (dest_ip, dest_port))
            print(f"Message '{message}' sent from {sock.getsockname()} to {dest_ip}:{dest_port}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <source_port> <dest_ip> <dest_port> <message>")
        sys.exit(1)

    source_port = int(sys.argv[1])
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    message = sys.argv[4]

    send_udp_message(source_port, dest_ip, dest_port, message)
