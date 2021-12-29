import socket
import threading
import time
import random
import struct

BROADCAST_IP = '255.255.255.255'
UDP_DEST_PORT = 13117#v
tcpSocket = None
udpSocket = None
SERVER_IP = socket.gethostbyname(socket.gethostname())#v
SERVER_PORT = 5051
MAX_CLIENTS = 2
CONNECTED_CLIENTS = 0#v
SCK1 = None
SCK2 = None
FORMAT = "utf-8"
MESSAGE_LENGTH = 1024#v
ANSWER_TIME = 10
TEAMS = []
TEAMS_ADDRESSES = []
magic_cookie = 0xabcddcba#v
msg_byte = 0x2#v
threadlock = threading.Lock()


class SimpleQuestions:
    def __init__(self):
        self.questions = [("17 * 2 - 29 = ?", 5), ("(45 + 54) / 11 = ?", 9), ("(35 + 27 - 18) / 11 = ?", 4), ("2 + 3 = ?", 5),
                          ("(40 + 40) / 10 = ?", 8), ("1 + 2 + 5 - 6 = ?", 2), ("3! = ?", 6), ("(34 - 12 + 17 - 9) * 0 = ?", 0),
                          ("(72 - 2 - 10 - 20) / 10 = ?", 4), ("42 / 7 = ?", 6), ("0.5 * 0.5 * 4 = ?", 1), ("1 + 1 + 1 + 1 + 1 + 1 * 0 + 1 + 1 = ?", 7),
                          ("e^0 = ?", 1), ("ln(1) = ?", 0), ("ln(e) = ?", 1), ("ln(1/e) + 1 = ?", 0), ("f(x)=x^2, f'(2) = ?", 4),
                          ("f'(x)=2x, f(3) = ?", 9), ("2x + 3 = 7, x = ?", 2), ("7x - 6 = 8, x = ?", 2), ("2 * 3", 6),("e - (e - 2)", 2),
                          ("25 / 5 = ?", 5), ("2 cats and 1 chickens have ? legs", 9), ("5 + 5 - 1 = ?", 9), ("if anny has 5 apples and danny 4, how much is 5 + 1?", 6),
                          ("how many pants is a pair of pants", 1), ("3 * 3 / 3 * 3 / 3 * 3 / 3", 3)
                          ]
    def getQ(self):
        return self.questions[random.randint(0, len(self.questions)-1)]

def make_udp():
    global udpSocket
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def udp_broadcast():
    make_udp()
    while CONNECTED_CLIENTS < MAX_CLIENTS:
        # lock?
        data = struct.pack('IBH', magic_cookie, msg_byte, SERVER_PORT)
        udpSocket.sendto(data, (BROADCAST_IP, UDP_DEST_PORT))
        time.sleep(1)
    udpSocket.close()

def init_tcp_server():
    global tcpSocket
    try:
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.bind((SERVER_IP,SERVER_PORT))
        tcpSocket.listen(2)
    except Exception as e:
        raise e

def send_teams_andQ(conn):
    questions = SimpleQuestions().getQ()
    msg = "Welcome to Quick Maths.\nPlayer 1: " + TEAMS[0] + "\nPlayer 2: " + TEAMS[1] + \
          f"\n====\n Please answer the following question as fast as you can: \n {questions[0]}\n"
    msg = msg.encode(FORMAT)
    conn.sendall(msg)
    return questions[1]

def reset():
    global  CONNECTED_CLIENTS
    CONNECTED_CLIENTS = 0

def get_winner(conn, answer):
    end = time.time() + ANSWER_TIME
    while time.time() < end:
        try:
            data, address = tcpSocket.recvfrom(MESSAGE_LENGTH)
            if data.decode(FORMAT) == answer:
                if address==TEAMS_ADDRESSES[0]:
                    return TEAMS[0]
                else: return TEAMS[1]
            else:
                if address==TEAMS_ADDRESSES[0]:
                    return TEAMS[0]
                else: return TEAMS[1]
        except:
            pass
    return "no winner"

def getTeamName(conn , addr):
    TEAMS.append(conn.recv(MESSAGE_LENGTH).decode(FORMAT))
    TEAMS_ADDRESSES.append(addr)

def start():
    global CONNECTED_CLIENTS ,tcpSocket 
    broadcast = threading.Thread(target= udp_broadcast , args=()) #will make the broadcasting socket
    broadcast.start()
    init_tcp_server() #makes the tcp server
    print(f"Server started, listening on IP address {SERVER_IP}")
    threads = []

    while CONNECTED_CLIENTS < MAX_CLIENTS:
        # lock
        conn,addr = tcpSocket.accept()
        thread = threading.Thread(target=getTeamName, args=(conn, addr))
        threads.append(thread)
        CONNECTED_CLIENTS += 1
        # lock release

    #2 users have joined
    broadcast.join()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    answer = send_teams_andQ(conn)
    winner = get_winner(conn, answer)
    print(f"Game over!\nThe correct answer was {answer}!\n\n")
    #continue

    conn.close()

if __name__ == "__main__":
        start()
