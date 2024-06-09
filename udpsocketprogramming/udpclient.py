from socket import *
import time
import statistics
import threading

# 客户端配置
server_ip = '172.19.144.1'  
server_port = 12345 
timeout_duration = 0.1  # 超时时间100ms
num_packets = 12  
version = 2 

# 创建UDP套接字
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(timeout_duration)  # 设置超时时间

print("发送 SYN 给服务器端...")
client_socket.sendto("SYN".encode(), (server_ip, server_port))
print("等待服务器端 SYN-ACK...")
syn_ack_response, _ = client_socket.recvfrom(2048)
print("收到服务器端 SYN-ACK")
print("发送 ACK 给服务器端...")
client_socket.sendto("ACK".encode(), (server_ip, server_port))
print("连接建立成功")

received_packets = 0  # 接收到的包数量
rtt_list = []  # 存储RTT的列表

for sequence_number in range(1, num_packets + 1):
    nonum = 'abcdcsjhdhadjasd'
    message = f"sequence_number:{sequence_number},vcr:{version},nolessnum:{nonum}"
    try:
        start_time = time.time()  # 记录发送时间
        client_socket.sendto(message.encode(), (server_ip, server_port))
        modifiedmessage, serverAddresss = client_socket.recvfrom(2048)  # 接收服务器的响应
        end_time = time.time()  # 记录接收时间
        
        rtt = (end_time - start_time) * 1000  # 计算RTT（单位：毫秒）
        rtt_list.append(rtt)
        server_time = modifiedmessage.decode().split(',')[1].split(':')[1]
        received_packets += 1
        print(f"序列号:{sequence_number}, {server_ip}:{server_port}, RTT: {rtt:.2f} ms")
    except timeout:
        print(f"序列号:{sequence_number}, 请求超时")
        
        # 重传逻辑
        for attempt in range(2):  # 尝试重传两次
            try:
                start_time = time.time()
                client_socket.sendto(message.encode(), (server_ip, server_port))
                modifiedmessage, serverAddresss = client_socket.recvfrom(2048)
                end_time = time.time()
                
                rtt = (end_time - start_time) * 1000  # 计算RTT
                rtt_list.append(rtt)
                num_packets+=1
                server_time = modifiedmessage.decode().split(',')[1].split(':')[1]
                received_packets += 1  # 只有在成功接收后才增加计数
                print(f"序列号:{sequence_number}, 重传{attempt+1}, {server_ip}:{server_port}, RTT: {rtt:.2f} ms")
                break
            except timeout:
                num_packets+=1
                print(f"序列号:{sequence_number}, 重传{attempt+1}, 请求超时")
            except ConnectionResetError:
                num_packets+=1
                print(f"序列号:{sequence_number}, 重传{attempt+1}, 连接被重置")
            except Exception as e:
                num_packets+=1
                print(f"序列号:{sequence_number}, 重传{attempt+1}, 发生错误: {e}")
    except ConnectionResetError:
        print(f"序列号:{sequence_number}, 连接被重置")
    except Exception as e:
        print(f"序列号:{sequence_number}, 发生错误: {e}")

# 汇总统计
if rtt_list:
    max_rtt = max(rtt_list)  # 最大RTT
    min_rtt = min(rtt_list)  # 最小RTT
    avg_rtt = sum(rtt_list) / len(rtt_list)  # 平均RTT
    std_dev_rtt = statistics.stdev(rtt_list)  # RTT标准差
else:
    max_rtt = min_rtt = avg_rtt = std_dev_rtt = 0

# 丢包率计算修正
successful_packets = received_packets  # 每个数据包最多重传一次，因此成功接收的原始数据包数量是 received_packets 的一半
loss_rate = ((num_packets - successful_packets) / num_packets) * 100

print(f"\n汇总统计:")
print(f"接收的数据包数量: {successful_packets}")
print(f"丢包率: {loss_rate:.2f}%")
print(f"最大RTT: {max_rtt:.2f} ms")
print(f"最小RTT: {min_rtt:.2f} ms")
print(f"平均RTT: {avg_rtt:.2f} ms")
print(f"RTT标准差: {std_dev_rtt:.2f} ms")

# 模拟 TCP 四次挥手
print("发送 FIN 给服务器端...")
client_socket.sendto("FIN".encode(), (server_ip, server_port))
print("等待服务器端 FIN-ACK...")
fin_ack_response, _ = client_socket.recvfrom(2048)
print("收到服务器端 FIN-ACK")
print("发送 ACK 给服务器端...")
client_socket.sendto("ACK".encode(), (server_ip, server_port))
print("四次挥手完成，关闭客户端")

# 关闭套接字
if client_socket.fileno() != -1:  # 确保套接字在关闭之前是打开的
    client_socket.close()
