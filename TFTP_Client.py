import socket
import argparse
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('-g', dest='get_filename')
parser.add_argument('-p', dest='put_filename')
parser.add_argument('-l', dest='host', default= 'localhost')
parser.add_argument('-a', dest='port', default= 12000)
args = parser.parse_args()


class Opcodes:
    RRQ = b'\x01'
    WRQ = b'\x02'
    DATA = b'\x03'
    ACK = b'\x04'
    ERROR = b'\x05'

class StringTypes:
    mode = 'netascii'


def makeRRQ(filename):
    return list(bytearray(Opcodes.RRQ)), filename, StringTypes.mode

def makeWRQ(filename):
    return list(bytearray(Opcodes.WRQ)), filename, StringTypes.mode

def makeDATA(blocknumber, data):
    return list(bytearray(Opcodes.DATA)), blocknumber, data

def makeACK(blocknumber):
    return list(bytearray(Opcodes.ACK)), blocknumber

def makeERR():
    return list(bytearray(Opcodes.ERROR)), StringTypes.ERR



port = args.port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.host, int(port)))

def getfile():

    blocknumber = 0
    sendingheader = makeRRQ(args.get_filename)
    headerPickle = pickle.dumps(sendingheader)
    get_filename = args.get_filename

    s.send(headerPickle)
    print(sendingheader)
    ########################################
    # RRQ -  ([1], '<FileName>', 'netascii')
    ########################################

    datarecv = s.recv(1024)
    recvdata = pickle.loads(datarecv)

    if recvdata[0] == [3]:
        f = open("get_" + get_filename, 'wb')
        f.write(recvdata[2])
        while True:
            datarecv = s.recv(1024)
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
            s.send(ack_headerPickle)

        print("Download Complete")


    else:
        print(recvdata)
        ########################################
        # ERR - ([5], [1], 'File Not Found')
        ########################################

    s.close()



def putfile():

    blocknumber = 0
    wrq_header = makeWRQ(args.put_filename)
    wrq_headerPickle = pickle.dumps(wrq_header)
    put_filename = args.put_filename

    s.send(wrq_headerPickle)
    print(wrq_header)
    ########################################
    # WRQ -  ([1], '<FileName>', 'netascii')
    ########################################

    ackrecv = s.recv(1024)
    recvack = pickle.loads(ackrecv)



    if recvack[0] == [4]:
        print(recvack)
        ##################
        # ACK -  ([4], 0)
        ##################
        f = open(put_filename, 'rb')
        bytesToSend = f.read(512)
        data_header = makeDATA(blocknumber, bytesToSend)
        data_headerPickle = pickle.dumps(data_header)
        s.send(data_headerPickle)

        while True:
            bytesToSend = f.read(512)
            blocknumber += 1
            data_header = makeDATA(blocknumber, bytesToSend)
            print(data_header[0:2])
            ########################################
            # DATA -  ([3], <block number>)
            ########################################
            data_headerPickle = pickle.dumps(data_header)
            s.send(data_headerPickle)
            if len(bytesToSend) < 512:
                break

            ackrecv = s.recv(1024)
            recvack = pickle.loads(ackrecv)
            print(recvack)
            ########################################
            # ACK -  ([4], <block number>)
            ########################################


        print("Upload Complete")


    else:
        print(recvack)
        ########################################
        # ERR - ([5], [1], 'File Not Found')
        # ERR - ([5], [6], 'File Already Exists')
        ########################################



    s.close()


def main():
    if args.get_filename:
        getfile()
    else:
        putfile()

main()

