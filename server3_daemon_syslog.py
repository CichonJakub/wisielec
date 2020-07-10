import socket
import random
import time
from settings import *
import struct
import syslog
import os
import sys


class Server:

    try:
        syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL7)
    except:
        print("could not handle syslog")

    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            syslog.syslog("exited first parent")
            #print("exited first parent")
            sys.exit(0)
    except OSError as e:
        syslog.syslog("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
        #print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)
    

    home_dir = '.'
    os.chdir(home_dir)
    os.setsid()
    os.umask(0)
    
    
    
    
    def __init__(self):
        self.sourceIP = "10.0.2.15"
        self.sourcePort = 8080
        self.serverAddress = (self.sourceIP, self.sourcePort)
        self.bufferSize = 1024
        # multicast
        #self.mcast_grp = '224.0.0.1'
        self.mcast_grp = '224.3.29.71'
        self.serverAddressMul = ('', 10000)

        syslog.syslog("lool")
        #print('lool')

        # create UDP socket
        self.serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        syslog.syslog("lol2")
        #print('lol2')
        # creating UDP multicast socket
        self.serverSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        syslog.syslog("lool3")
        #print('lool3')

    def binding(self, serverAddress):
        # socket.bind((sourceIP, sourcePort)) + multicast gniazdo 2
        try:
            self.serverSocket.bind(serverAddress)
            syslog.syslog("I am listening :)")
            #print("I am listening :)")
            self.serverSocket2.bind(self.serverAddressMul)
            group = socket.inet_aton(self.mcast_grp)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.serverSocket2.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        except:
            syslog.syslog("Bind error!")
            #print("Bind error!")

    def play(self):

        while (True):
            # 2 try do multicastu
            try:
                syslog.syslog("xD")
                #print('xD')
                #bytesAddressPair = self.serverSocket.recvfrom(self.bufferSize)
                #print(bytesAddressPair[0])
                bytesAddressPair2 = self.serverSocket2.recvfrom(self.bufferSize)
                syslog.syslog("odebralem")
                #print('odebralem')
                message2 = bytesAddressPair2[0]
                self.cliAddress = bytesAddressPair2[1]
                
                syslog.syslog(message2)
                syslog.syslog(self.cliAddress)
                #print(message2)
                #print(self.cliAddress)
                
                #connection = self.sourceIP + ':' + str(self.sourcePort)
                #print(connection)
                time.sleep(2)
                #self.response("Hello my friendo !")
                self.response2("Hello my friendo !", self.cliAddress)
                syslog.syslog("wyslalem")
                #print('wyslalem')

            except:
                syslog.syslog("Error when receiving multicast message")
                #print('Error when recieving multicast message')

            try:
                game = True
                syslog.syslog("LOOP")
                #print("LOOP")
                bytesAddressPair = self.serverSocket.recvfrom(self.bufferSize)
                message = bytesAddressPair[0]
                syslog.syslog(message)
                #print(message)
                self.cliAddress = bytesAddressPair[1]
                category, word = random.choice(list(wordBank.items()))
                guessed_letters = []
                is_guessed = False
                break

            except:
                syslog.syslog("Error when receiving message")
                #print("Error when receiving message")

        while (game):

            lives = 5

            clientMSG = "Message from Client: {}".format(message)
            clientIP = "Client IP Address:{}".format(self.cliAddress)

            syslog.syslog(clientMSG)
            syslog.syslog(clientIP)
            syslog.syslog(category)
            syslog.syslog(word)
            #print(clientMSG)
            #print(clientIP)
            #print(category)
            #print(word)

            self.secretWord = ''

            # zamienienie liter na '_ '
            for letter in word:
                self.secretWord += '_ '

            self.response("WELCOME TO 'THE HANGMAN' GAME")
            time.sleep(1)

            self.response("Phrase from category: {}".format(category))
            time.sleep(1)

            self.response("Guess letter or entire phrase if You can ;)")
            time.sleep(1)

            self.response("You have got {} lives".format(lives))

            self.response(self.secretWord)
            time.sleep(1)

            while (lives > 1):
                # receiving letter from client
                isCorrect = False

                msgFromClient = self.serverSocket.recvfrom(self.bufferSize)
                guess = msgFromClient[0].decode()
                syslog.syslog(guess)
                #print(guess)

                if guess not in guessed_letters and len(guess) == 1:
                    for loc, letter in enumerate(word):
                        if guess == letter:
                            isCorrect = True
                            self.secretWord = self.secretWord[:loc * 2] + guess + self.secretWord[loc * 2 + 1:]
                    guessed_letters.append(guess)

                if len(guess) == len(word):
                    if guess == word:
                        self.secretWord = word
                        is_guessed = True

                # recv
                syslog.syslog(lives)
                #print(lives)
                if isCorrect and not is_guessed:
                    self.response("Congrats, You guessed it !")
                    self.response(self.secretWord)

                if not isCorrect and not is_guessed:
                    lives -= 1
                    self.response("You have got {} lives, dont give up!".format(str(lives)))
                    self.response(self.secretWord)

                if '_' not in self.secretWord:
                    self.response("You guessed the phrase {} correctly, congratulations ! You won !".format(word))
                    time.sleep(1)
                    game = False
                    break

            if lives < 1:
                self.response("Unfortunately You lost, the phrase was {}. Good luck next time :)".format(word))
                time.sleep(1)
                game = False

            # mozna tu jeszcze dopisac opcje wybrania kolejnej gry lub wylaczenie ale to wiecej rzeczy bedzie do spradzania, wykonalne owszem, czy potrzebne nie wiem :/

    def response(self, msg):
        bytesToSend = str.encode(msg)
        self.serverSocket.sendto(bytesToSend, self.cliAddress)
        time.sleep(1)

    def response2(self, msg, destination):
        bytesToSend = str.encode(msg)
        self.serverSocket2.sendto(bytesToSend, destination)
        time.sleep(1)


try:
    server = Server()
    syslog.syslog("1")
    #print('1')
    server.binding(server.serverAddress)
    syslog.syslog("1")
    #print('2')
    server.play()
    syslog.syslog("1")
    #print('3')
except:
    print("sth goes wrong :/")