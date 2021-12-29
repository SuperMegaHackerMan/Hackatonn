import socket
import threading
import time
import random
import struct

BROADCAST_IP = '255.255.255.255'
UDP_DEST_PORT = 13117
tcpSocket = None
udpSocket = None
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5051
MAX_CLIENTS = 2
CONNECTED_CLIENTS = 0
SCK1 = None
SCK2 = None
FORMAT = "utf-8"
MESSAGE_LENGTH = 1024
ANSWER_TIME = 10
TEAM1 =""
TEAM2 =""
magic_cookie = 0xabcddcba
msg_byte = 0x2
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


#should make it better somehow
def getTeamName(conn , addr):
    """
    this function handles the names received from the client and stores it in the srever.
    :param conn: socket object
    :param addr: the address bound to the socket
    """
    global TEAM1, TEAM2
    end = time.time() + ANSWER_TIME
    while time.time() < end:
        try:
            threadlock.acquire()
            if TEAM1 == "":
                TEAM1 = conn.recv(MESSAGE_LENGTH).decode(FORMAT)
            elif TEAM2 == "":
                TEAM2 = conn.recv(MESSAGE_LENGTH).decode(FORMAT)
            threadlock.release()
        except :
            pass

def send_teams_andQ():
    questions = SimpleQuestions().getQ()
    msg = "Welcome to Quick Maths.\nPlayer 1: " + TEAM1 + "\nPlayer 2: " + TEAM2 + \
          f"\n====\n Please answer the following question as fast as you can: \n {questions[0]}\n"
    msg = msg.encode(FORMAT)
    try:
        SCK1.sendall(msg)
        SCK2.sendall(msg)
        return questions[1]
    except:
        pass

def decide_winner(answer):
    end = time.time() + ANSWER_TIME
    while time.time() < end:
        try:
            if SCK1.recv(MESSAGE_LENGTH).decode(FORMAT) == answer:
                print(TEAM1)
            elif SCK2.recv(MESSAGE_LENGTH).decode(FORMAT) == answer:
                print(TEAM2)
            else:
                print("no winner")
        except:
            pass

def reset():
    global  CONNECTED_CLIENTS, SCK1, SCK2
    CONNECTED_CLIENTS = 0
    SCK1 = None
    SCK2 = None

def start():
    global CONNECTED_CLIENTS ,tcpSocket ,SCK1, SCK2
    broadcast = threading.Thread(target= udp_broadcast , args=()) #will make the broadcasting socket
    broadcast.start()
    init_tcp_server() #makes the tcp server
    print(f"Server started, listening on IP address {SERVER_IP}")
    threads = []
    while CONNECTED_CLIENTS < MAX_CLIENTS:
        try:
            conn,addr = tcpSocket.accept()
            if CONNECTED_CLIENTS == 0: #MAYBE CHANGE
                SCK1 = conn
                print("client 1 connected")
            else:
                SCK2 = conn
                print("client 2 connected")
            thread = threading.Thread(target=getTeamName, args=(conn, addr))
            threads.append(thread)
            CONNECTED_CLIENTS += 1
        except Exception as e:
            raise e
    #2 users have joined
    broadcast.join()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if TEAM1 == "" or TEAM2 == "":
        print("should start all over")
    else:
        answer = send_teams_andQ()
        decide_winner(answer)
        try:
            SCK1.close()
            SCK2.close()
        except:
            print("An exception occurred")


if __name__ == "__main__":
        start()



















