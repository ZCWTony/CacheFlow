#!/usr/bin/env python3
"""
使用 Python 模拟 P4 交换机运行 CacheFlow 实验
（大量流，均匀随机，不区分热冷流，验证缓存学习能力）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from p4.emulator import P4SwitchEmulator
import random

def generate_flow_set(num_flows=500):
    """生成 num_flows 个不同的五元组（流）"""
    flows = []
    used = set()
    while len(flows) < num_flows:
        src = random.randint(1, 100)
        dst = random.randint(1, 100)
        proto = 6          # TCP
        sport = random.randint(1024, 65535)  # 随机源端口，增加多样性
        dport = random.choice([80, 443, 22, 53, 8080])  # 常见目的端口
        key = (f"10.0.0.{src}", f"192.168.1.{dst}", proto, sport, dport)
        if key not in used:
            used.add(key)
            flows.append(key)
    return flows

def main():
    # 初始化模拟交换机（容量 512）
    switch = P4SwitchEmulator(capacity=512)

    # 生成 500 个不同的流
    all_flows = generate_flow_set(500)
    print(f"Generated {len(all_flows)} distinct flows.")

    # 发送 1000 个数据包，均匀随机选择流
    total_packets = 2000
    print(f"Sending {total_packets} packets (uniformly random) ...")

    hit_counts = []  # 记录每 100 个包的命中数

    for i in range(total_packets):
        flow = random.choice(all_flows)
        lookup_packet = {
            'src_ip': flow[0],
            'dst_ip': flow[1],
            'protocol': flow[2],
            'src_port': flow[3],
            'dst_port': flow[4]
        }
        hit, _ = switch.lookup(lookup_packet)
        if not hit:
            # 未命中则添加该流到缓存
            switch.add_rule(flow, "forward")

        # 每 100 个包记录一次统计
        if (i + 1) % 100 == 0:
            stats = switch.get_stats()
            hit_counts.append((i+1, stats['hit_rate']))

    # 最终统计
    final_stats = switch.get_stats()
    print(f"\n=== Final Results ===")
    print(f"Total packets: {final_stats['total']}")
    print(f"Total hits: {final_stats['hit_count']}")
    print(f"Total misses: {final_stats['miss_count']}")
    print(f"Overall hit rate: {final_stats['hit_rate']:.2%}")

    print("\n=== Hit Rate Progression (per 100 packets) ===")
    for cnt, rate in hit_counts:
        print(f"  After {cnt} packets: {rate:.2%}")

if __name__ == "__main__":
    main()