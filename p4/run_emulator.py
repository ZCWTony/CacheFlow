#!/usr/bin/env python3
"""
使用 Python 模拟 P4 交换机运行 CacheFlow 实验
（均匀随机流，自动保存结果）
"""
import sys
import os
import datetime
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
        proto = 6
        sport = random.randint(1024, 65535)
        dport = random.choice([80, 443, 22, 53, 8080])
        key = (f"10.0.0.{src}", f"192.168.1.{dst}", proto, sport, dport)
        if key not in used:
            used.add(key)
            flows.append(key)
    return flows

def main():
    switch = P4SwitchEmulator(capacity=512)
    all_flows = generate_flow_set(500)
    print(f"Generated {len(all_flows)} distinct flows.")

    total_packets = 2000
    print(f"Sending {total_packets} packets (uniformly random) ...")

    hit_counts = []  # (packet_count, hit_rate)

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
            switch.add_rule(flow, "forward")

        if (i + 1) % 100 == 0:
            stats = switch.get_stats()
            hit_counts.append((i+1, stats['hit_rate']))

    final_stats = switch.get_stats()
    print(f"\n=== Final Results ===")
    print(f"Total packets: {final_stats['total']}")
    print(f"Total hits: {final_stats['hit_count']}")
    print(f"Total misses: {final_stats['miss_count']}")
    print(f"Overall hit rate: {final_stats['hit_rate']:.2%}")

    print("\n=== Hit Rate Progression (per 100 packets) ===")
    for cnt, rate in hit_counts:
        print(f"  After {cnt} packets: {rate:.2%}")

    # 保存结果到文件
    result_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(result_dir, f"experiment_{timestamp}.txt")
    with open(result_file, 'w') as f:
        f.write(f"Total packets: {final_stats['total']}\n")
        f.write(f"Total hits: {final_stats['hit_count']}\n")
        f.write(f"Total misses: {final_stats['miss_count']}\n")
        f.write(f"Overall hit rate: {final_stats['hit_rate']:.2%}\n")
        f.write("\n=== Hit Rate Progression ===\n")
        for cnt, rate in hit_counts:
            f.write(f"After {cnt} packets: {rate:.2%}\n")
    print(f"\nResults saved to {result_file}")

if __name__ == "__main__":
    main()
