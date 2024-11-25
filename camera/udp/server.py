from socket import socket, AF_INET, SOCK_DGRAM

HOST = '127.0.0.1'
PORT = 9000# 何でも良い

s = socket(AF_INET, SOCK_DGRAM)

s.bind((HOST, PORT))

while True:
    rcv_data, addr = s.recvfrom(1024)
    print("receive data : [{}]  from {}".format(rcv_data,addr))
    
s.close()