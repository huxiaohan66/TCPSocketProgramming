from socket import*
import sys
import random
import struct

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# 写入数据到文件
def write_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)

# 将数据分块
def split_data(data, lmin, lmax):
    blocks = []
    length = len(data)
    while length > 0:
        block_size = random.randint(lmin, lmax)  # 生成一个随机块大小
        if block_size > length:
            block_size = length
        blocks.append(data[:block_size])  # 添加块到列表
        data = data[block_size:]  # 更新剩余数据
        length -= block_size
    return blocks

def main():
    if len(sys.argv) != 7:
        print("Usage: python client.py <server_ip> <server_port> <file_path> <Lmin> <Lmax> <output_file>")
        return
    
    # 获取命令行参数
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]
    lmin = int(sys.argv[4])
    lmax = int(sys.argv[5])
    output_file = sys.argv[6]
    
    # 读取文件并分块
    data = read_file(file_path)
    blocks = split_data(data, lmin, lmax)
    block_count = len(blocks)
    
    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))
        
        # 发送初始化消息
        initialization_message = struct.pack('!H', 1) + struct.pack('!I', block_count)
        client_socket.sendall(initialization_message)
        
        # 接收同意消息
        response = client_socket.recv(1024)
        response_type = struct.unpack('!H', response[:2])[0]
        if response_type != 2:
            print("Expected agree message")
            return
        
        reversed_data = []
        
        # 发送反转请求
        for i, block in enumerate(blocks):
            block_length = len(block)
            reverse_request_message = struct.pack('!H', 3) + struct.pack('!I', block_length) + block.encode()
            client_socket.sendall(reverse_request_message)
            
            # 接收反转答案
            response = client_socket.recv(1024)
            response_type = struct.unpack('!H', response[:2])[0]
            if response_type != 4:
                print("Expected reverse answer message")
                return
            reversed_block_length = struct.unpack('!I', response[2:6])[0]
            reversed_block = response[6:6 + reversed_block_length].decode()
            print(f"第{i+1}块：反转文本 {reversed_block}")
            reversed_data.append(reversed_block)
        
        # 将反转的数据写入文件
        write_file(output_file, ''.join(reversed_data))

if __name__ == "__main__":
    main()
