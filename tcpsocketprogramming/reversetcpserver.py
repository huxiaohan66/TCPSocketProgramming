from socket import *
import struct
import threading
import sys
import os

def handle_client(client_socket):
    """
    接收和解析客户端消息，并根据消息类型执行相应操作。
    """
    try:
        while True:
            # 接收消息类型
            msg_type_data = client_socket.recv(2)
            if not msg_type_data:
                break
            msg_type = struct.unpack('!H', msg_type_data)[0]

            if msg_type == 1:  # 初始化消息
                block_count_data = client_socket.recv(4)
                block_count = struct.unpack('!I', block_count_data)[0]
                print(f"Initialization received with {block_count} blocks.")
                # 发送同意消息
                agree_message = struct.pack('!H', 2)
                client_socket.sendall(agree_message)
            elif msg_type == 3:  # 反转请求消息
                block_length_data = client_socket.recv(4)
                block_length = struct.unpack('!I', block_length_data)[0]
                block_data = client_socket.recv(block_length).decode('utf-8')
                reversed_block = block_data[::-1]
                # 发送反转应答消息
                reverse_answer_message = struct.pack('!H', 4) + struct.pack('!I', len(reversed_block)) + reversed_block.encode('utf-8')
                client_socket.sendall(reverse_answer_message)
            else:
                print("未知类型信息")
    finally:
        client_socket.close()

def listen_for_shutdown():
   
    while True:
        user_input = input()
        if user_input.lower() == 'end':
            print("服务端已关闭")
            os._exit(0)   #end关闭服务器

def main():
    """
    设置并启动服务器，接受客户端连接，
    并为每个客户端启动一个单独的线程进行处理。
    """
    server_ip = '0.0.0.0'
    server_port = 12345

    # 创建并绑定服务器套接字
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind((server_ip, server_port))
        server_socket.listen(5)
        print("Server listening on port", server_port)
        
        # 启动线程监听服务器控制台的关闭命令
        threading.Thread(target=listen_for_shutdown, daemon=True).start()
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            # 为每个客户端启动一个单独的线程进行处理
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    main()
