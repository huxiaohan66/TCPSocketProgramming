from socket import *
import random
import time
import threading

# 服务器配置
server_ip = '127.0.0.1'
server_port = 12345
loss_rate = 0.2  # 丢包率，用于模拟丢包场景

# 创建UDP套接字
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

print(f"服务器正在监听 {server_ip}:{server_port}")

def handle_client(data, client_address):
    # 解包数据
    sequence_number, vcr = data.decode().split(',')
    sequence_number = int(sequence_number.split(':')[1])
    vcr = int(vcr.split(':')[1])
    
    # 模拟丢包
    if random.random() < loss_rate:
       # print(f"丢失数据包 {sequence_number} 来自 {client_address}")
        return
    
    # 回复客户端
    response = f"Seq.no:{sequence_number},server_time:{time.strftime('%H-%M-%S')}"
    server_socket.sendto(response.encode(), client_address)
    print(f"回复 {client_address}，序列号 {sequence_number}")

while True:
    data, client_address = server_socket.recvfrom(1024)  # 接收来自客户端的数据
    client_thread = threading.Thread(target=handle_client, args=(data, client_address))
    client_thread.start()
