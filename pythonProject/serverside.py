import base64
import socket
import struct

CLIENT_IP = socket.gethostbyname(socket.gethostname())
MESSAGE_LENGTH = 1024
FORMAT = "utf-8"
UDP_PORT = 13117
udpSocket = None
tcpSocket = None
COOKIE = 0xabcddcba
MSG_TYPE = 0x2


def maketcp(ip, port):
    global tcpSocket
    try:
        tcpSocket = socket.socket
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpSocket.connect((ip, port))
    except (InterruptedError, ConnectionRefusedError, ConnectionResetError) as e:
        print("error message")


# def input_and_server_msg(already_answerd):
#     global tcpSocket
#     readers, _, _ = select.select([tcpSocket, sys.stdin], [], [])
#     for reader in readers:
#         if reader is tcpSocket:
#             print(tcpSocket.recv(MESSAGE_LENGTH).decode(FORMAT))
#         elif not already_answerd:
#             msg = sys.stdin.readline()[0]
#             tcpSocket.send(msg.encode(FORMAT))
#             already_answerd = True
#             input_and_server_msg(already_answerd)
#         else:
#             input_and_server_msg(already_answerd)


def startClient():
    global tcpSocket
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udpSocket.bind((CLIENT_IP, UDP_PORT))
    print("Listening...")
    message, server_address = udpSocket.recvfrom(MESSAGE_LENGTH)
    cookie, msg_type, tcp_port = struct.unpack('IBH', message)
    if cookie == COOKIE and msg_type == MSG_TYPE:
        maketcp(server_address[0], tcp_port)
        print("Send Team Name")
        name_message = input()
        tcpSocket.send(name_message.encode(FORMAT))

        WelcomeMsgFromServer = tcpSocket.recvfrom(MESSAGE_LENGTH)
        print(WelcomeMsgFromServer[0].decode(FORMAT))

        Question = tcpSocket.recvfrom(MESSAGE_LENGTH)
        print(Question[0].decode(FORMAT))

        name_message = input()
        tcpSocket.send(name_message.encode(FORMAT))

        result = tcpSocket.recvfrom(MESSAGE_LENGTH)
        print(result[0].decode(FORMAT))

        print("Server Disconnected")
    tcpSocket.close()


if __name__ == "__main__":
    startClient()
