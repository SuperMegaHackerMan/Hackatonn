import socket
import struct

CLIENT_IP = socket.gethostbyname(socket.gethostname())
MESSAGE_LENGTH = 1024
FORMAT = "utf-8"
UDP_PORT = 13117
udpSocket= None
tcpSocket = None
COOKIE = 0xabcddcba
MSG_TYPE = 0x2

def makeUdp():
    global udpSocket
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udpSocket.bind((CLIENT_IP,UDP_PORT))

def maketcp(ip, port):
    global tcpSocket
    try:
        tcpSocket = socket.socket
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpSocket.connect((ip, port))
    except (InterruptedError, ConnectionRefusedError, ConnectionResetError) as e:
        print("error message")


def receiveOffer(self):
    message, server_address = udpSocket.recvfrom(MESSAGE_LENGTH)
    cookie, msg_type, tcp_port = struct.unpack('IBH', message)
    return cookie, msg_type, tcp_port, server_address


def startClient():
    makeUdp()
    cookie,msg_type ,tcp_port,server_address = receiveOffer()
    if cookie == COOKIE and msg_type == MSG_TYPE:
        maketcp(server_address[0],tcp_port)
        name_message = input()
        tcpSocket.send(name_message.encode(FORMAT))
        print(tcpSocket.recv(MESSAGE_LENGTH).decode(FORMAT))
        answer = input()
        tcpSocket.send(answer.encode(FORMAT))
        print(tcpSocket.recv(MESSAGE_LENGTH).decode(FORMAT))
        tcpSocket.close()
        print("Server Disconnected")

