import socket
import threading
import argparse
import pickle
import os


parser = argparse.ArgumentParser()
parser.add_argument('-a', dest='port', default=12000)
args = parser.parse_args()


class Opcodes:
    RRQ = b'\x01'
    WRQ = b'\x02'
    DATA = b'\x03'
    ACK = b'\x04'
    ERROR = b'\x05'

class StringTypes:
    mode = 'netascii'
    err_1 = 'File Not Found'
    err_5 = 'Unknown transfer ID'
    err_6 = 'File Already Exists'

class ErrorCodes:
    err1 = b'\x01'
    err5 = b'\x05'
    err6 = b'\x06'


def makeRRQ(filename):
    return list(bytearray(Opcodes.RRQ)), filename, StringTypes.mode

def makeWRQ(filename):
    return list(bytearray(Opcodes.WRQ)), filename, StringTypes.mode

def makeDATA(blocknumber, data):
    return list(bytearray(Opcodes.DATA)), blocknumber, data

def makeACK(blocknumber):
    return list(bytearray(Opcodes.ACK)), blocknumber

def makeERR(errorcode, errormssg):
    return list(bytearray(Opcodes.ERROR)), errorcode, errormssg

def create():
    try:
        global host
        global port
        global s
        host = ""
        port = args.port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    except socket.error as msg:
        print("Socket creation error " + str(msg))


def bind():
    try:
        global host
        global port
        global s

        port = args.port
        if int(port) in range (0,5000):
            err_header = makeERR(list(bytearray(ErrorCodes.err5)), StringTypes.err_5)
            print(err_header)
            ########################################
            # ERR - ([5], [5], 'Unknown transfer ID')
            ########################################
            return port
        else:
            pass

        s.bind((host, int(port)))
        print("Binding the Port: " + str(port))
        s.listen(5)
        while True:
            c, addr = s.accept()
            print("Client Connected IP: ", str(addr))
            t = threading.Thread(target=file, args=("rtrThread", c))
            t.start()
        s.close()

    except socket.error as msg:
        print("Socket Binding error " + str(msg) + "\n" + "Retrying..")
        bind()



def file(name,sock):

    blocknumber = 0
    filenameByte = sock.recv(1024)
    recvingheader = pickle.loads(filenameByte)
    print(recvingheader)
    
    ########################################
    # RRQ -  ([1], '<FileName>', 'netascii')
    ########################################
    if recvingheader[0] == [1]:

        if os.path.isfile(recvingheader[1]):

            f = open(recvingheader[1], 'rb')
            bytesToSend = f.read(512)
            data_header = makeDATA(blocknumber, bytesToSend)
            data_headerPickle = pickle.dumps(data_header)
            sock.send(data_headerPickle)

            while True:
                bytesToSend = f.read(512)
                blocknumber += 1
                data_header = makeDATA(blocknumber, bytesToSend)
                print(data_header[0:2])
                ########################################
                # DATA -  ([3], <block number>)
                ########################################
                data_headerPickle = pickle.dumps(data_header)
                sock.send(data_headerPickle)
                if len(bytesToSend) < 512:
                    break

                ackrecv = sock.recv(1024)
                recvack = pickle.loads(ackrecv)
                print(recvack)
                ########################################
                # ACK -  ([4], <block number>)
                ########################################

            print("Complete")


        else:
            ########################################
            # ERR - ([5], [1], 'File Not Found')
            ########################################
            err_header = makeERR(list(bytearray(ErrorCodes.err1)), StringTypes.err_1)
            print(err_header)
            err_headerPicle = pickle.dumps(err_header)
            sock.send(err_headerPicle)



    ########################################
    # WRQ -  ([2], '<FileName>', 'netascii')
    ########################################
    elif recvingheader[0] == [2]:

        if os.path.isfile(recvingheader[1]):
            fileexist = "put_" + recvingheader[1]

            if os.path.isfile(fileexist):
                err_header = makeERR(list(bytearray(ErrorCodes.err6)), StringTypes.err_6)
                print(err_header)
                ########################################
                # ERR - ([5], [6], 'File Already Exists')
                ########################################
                err_headerPicle = pickle.dumps(err_header)
                sock.send(err_headerPicle)

            else:

                ack_header = makeACK(blocknumber)
                print(ack_header)
                ##################
                # ACK -  ([4], 0)
                ##################
                ack_headerPickle = pickle.dumps(ack_header)
                sock.send(ack_headerPickle)


                f = open("put_" + recvingheader[1], 'wb')
                datarecv = sock.recv(1024)
                recvdata = pickle.loads(datarecv)
                f.write(recvdata[2])

                if recvdata[0] == [3]:
                    while True:
                        datarecv = sock.recv(1024)
                        recvdata = pickle.loads(datarecv)
                        f.write(recvdata[2])
                        blocknumber += 1
                        print(recvdata[0:2])
                        ########################################
                        # DATA -  ([3], <block number>)
                        ########################################
                        if len(recvdata[2]) < 512:
                            break

                        ack_header = makeACK(blocknumber)
                        print(ack_header)
                        ########################################
                        # ACK -  ([4], <block number>)
                        ########################################
                        ack_headerPickle = pickle.dumps(ack_header)
                        sock.send(ack_headerPickle)

                    print("Complete")

                else:
                    print("Unknown Error")


        else:
            err_header = makeERR(list(bytearray(ErrorCodes.err1)), StringTypes.err_1)
            print(err_header)
            ########################################
            # ERR - ([5], [1], 'File Not Found')
            ########################################
            err_headerPicle = pickle.dumps(err_header)
            sock.send(err_headerPicle)



def main():
    create()
    bind()


main()

'''
If already in Use, use this command

sudo lsof -t -i tcp:12000 | xargs kill -9
'''
