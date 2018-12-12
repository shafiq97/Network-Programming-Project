import socket
import _thread
import sys
import pyAesCrypt
import hashlib
from datetime import datetime
import os


# import thread module
from _thread import start_new_thread
import threading


def get_time():
    current_date_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return current_date_time


def logger(string, file_=open('logfile.txt', 'a'), lock=_thread.allocate_lock()):
    with lock:
        file_.write(string + '\n\n')
        file_.flush()  # optional, makes data show up in the logfile more quickly, but is slower


def hashmd5(c, filename):  # hash md5
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read()
    hasher.update(buf)
    nbuf = hasher.hexdigest()
    print(f"Hash: {nbuf}")
    c.send(nbuf.encode())


def send_file(c, file_download):
    f = open(file_download, "r")
    bf = f.read().encode()  # read file content
    c.send(bf)
    print("File uploaded to server...")


def encrypt_file(filename):
    # encryption/decryption buffer size - 64K
    bufferSize = 64 * 1024
    password = "anjingkurap"
    filename_aes = filename + ".aes"
    # encrypt
    pyAesCrypt.encryptFile(filename, filename_aes, password, bufferSize)


def accept_file(c, filename):
    f = open(filename, 'w')
    data = c.recv(1024)
    data = f.write(data.decode())
    f.close()


def threaded(c, addr):
    while True:

        # data received from client
        choice = c.recv(1024).decode()
        print(f"Client choice: {choice}")
        if choice == "1":
            filename = c.recv(1024).decode()
            print(f"Client filename: {filename}")
            accept_file(c, filename)
        if choice == "2":
            file_download = c.recv(1024).decode()
            print(f"Client filename: {file_download}")
            send_file(c, file_download)
        if choice == "3":
            filename = c.recv(1024).decode()
            print(f"Client filename: {filename}")
            hashmd5(c, filename)
        if not choice:
            print(
                f'{str(addr)} disconnected\nWaiting for new connection...\n\n')
            # lock released on exit
            break

    # connection closed

    c.close()
    current_close_time = get_time()
    logger(
        f"----> Client {str(addr[0])} disconnect at: " + current_close_time + " UTC")


def Main():
    host = str(sys.argv[1])
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1000)

    s.bind((host, port))
    print("socket binded to post", port)

    # put the socket into listening mode
    s.listen(5)
    print("Socket is listening...\n")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()
        current_time = get_time()
        logger(
            f"Client {str(addr[0])} connected at:   " + current_time + "UTC")

        # lock acquired by client

        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c, addr))
    s.close()


if __name__ == '__main__':
    Main()
