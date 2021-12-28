import socket
import threading
import time
import random

tcpSocket = None
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5050
MAX_CLIENTS = 2
CONNECTED_CLIENTS = 0
SCK1 = None
SCK2 = None
FORMAT = "utf-8"
MESSAGE_LENGTH = 1024
ANSWER_TIME = 10
TEAM1 =""
TEAM2 =""

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

def init_tcp_server():
    global tcpSocket
    try:
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpSocket.bind((SERVER_IP,SERVER_PORT))
        tcpSocket.listen(2)
    except Exception as e:
        raise e


def getTeamName(conn , addr):
    global TEAM1, TEAM2, SCK1, SCK2
    end = time.time() + ANSWER_TIME
    while time.time() < end:
        try:
            if TEAM1 == "":
                TEAM1 = conn.recv(MESSAGE_LENGTH).decode(FORMAT)
                SCK1 = conn
            elif TEAM2 == "":
                TEAM2 = conn.recv(MESSAGE_LENGTH).decode(FORMAT)
                SCK2 = conn
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
    global CONNECTED_CLIENTS ,tcpSocket
    init_tcp_server()
    threads = []
    while CONNECTED_CLIENTS < MAX_CLIENTS:
        try:
            print("server is listening")
            conn,addr = tcpSocket.accept()
            thread = threading.Thread(target=getTeamName, args=(conn, addr))
            threads.append(thread)
            CONNECTED_CLIENTS += 1
        except:
            print("An exception occurred")
    for thread in threads:
        thread.start()
        thread.join()
    if TEAM1 == "" and TEAM2 == "":
        print("should start all over")
    else:
        answer= send_teams_andQ()
        decide_winner(answer)
        try:
            SCK1.close()
            SCK2.close()
        except:
            print("An exception occurred")


if __name__ == "__main__":
        start()



















