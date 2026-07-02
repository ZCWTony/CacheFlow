#!/bin/bash
# P4实验一键运行脚本
set -e

echo "=== CacheFlow P4 Experiment (BMv2) ==="

# 1. 安装依赖
echo "[1/5] Installing dependencies..."
pip install p4runtime-sh grpcio-tools scapy

# 2. 编译P4程序
echo "[2/5] Compiling P4 program..."
p4c --target bmv2 --arch v1model \
    --p4runtime-files build/p4info.txt \
    -o build/ p4/cacheflow.p4

# 3. 启动BMv2交换机（后台）
echo "[3/5] Starting BMv2 switch..."
sudo simple_switch --p4info build/p4info.txt \
    --bmv2-json build/cacheflow.json \
    -i 1@veth0 -i 2@veth1 \
    --log-console \
    --no-pcap &
SWITCH_PID=$!
sleep 3

# 4. 运行控制平面（下发规则）
echo "[4/5] Running control plane..."
python3 p4/controller.py --sw-addr 127.0.0.1:50051 &
CONTROLLER_PID=$!
sleep 5

# 5. 发送测试流量（使用scapy）
echo "[5/5] Sending test traffic..."
python3 -c "
from scapy.all import *
import time
# 发送100个测试包
for i in range(100):
    pkt = Ether()/IP(src='10.0.0.1', dst='192.168.1.1')/TCP(sport=12345, dport=80)
    sendp(pkt, iface='veth0', verbose=False)
    if i % 10 == 0:
        print(f'Sent {i+1} packets')
"

echo "=== Experiment completed. Check BMv2 logs for hit/miss statistics. ==="
# 停止进程
kill $CONTROLLER_PID $SWITCH_PID 2>/dev/null
