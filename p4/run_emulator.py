cat > p4/run_emulator.py << 'EOF'
#!/usr/bin/env python3
"""
使用 Python 模拟 P4 交换机运行 CacheFlow 实验
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from p4.emulator import P4SwitchEmulator
from data.generate_traffic import TrafficGenerator

def main():
    # 初始化模拟交换机
    switch = P4SwitchEmulator(capacity=512)

    # 生成并下发规则（使用与模拟实验相同的规则生成逻辑，但这里简化）
    print("Loading rules into switch...")
    # 为了演示，从文件加载规则（可选），或直接生成随机规则
    # 这里我们生成1000条随机规则
    import random
    for i in range(1000):
        src = f"10.0.{random.randint(0,255)}.{random.randint(0,255)}"
        dst = f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"
        proto = random.choice([6, 17])
        sport = random.randint(1024, 65535)
        dport = random.randint(1, 1024)
        key = (src, dst, proto, sport, dport)
        action = random.choice(["forward", "drop"])
        switch.add_rule(key, action)
    print(f"Loaded {len(switch.table)} rules.")

    # 生成流量并测试
    print("Generating traffic...")
    traffic_gen = TrafficGenerator(mode="mixed")
    total_packets = 500
    for i in range(total_packets):
        packet = next(traffic_gen.stream())
        # 转换包格式以匹配模拟器查找键
        # 为了演示，从包中生成简单五元组
        pkt_tuple = (f"10.0.0.{packet.get('src', 1)}",
                     f"192.168.1.{packet.get('dst', 1)}",
                     6, 12345, 80)
        # 构造实际包字典
        lookup_packet = {
            'src_ip': pkt_tuple[0],
            'dst_ip': pkt_tuple[1],
            'protocol': pkt_tuple[2],
            'src_port': pkt_tuple[3],
            'dst_port': pkt_tuple[4]
        }
        hit, action = switch.lookup(lookup_packet)
        # 模拟处理
        if hit:
            pass
        else:
            # 未命中时触发缓存加载（模拟）
            # 这里模拟添加规则（如果是重要的流）
            if i % 10 == 0:
                switch.add_rule((lookup_packet['src_ip'], lookup_packet['dst_ip'],
                                 lookup_packet['protocol'], lookup_packet['src_port'],
                                 lookup_packet['dst_port']), "forward")

    # 输出统计
    stats = switch.get_stats()
    print(f"\n=== Experiment Results ===")
    print(f"Total packets: {stats['total']}")
    print(f"Hit count: {stats['hit_count']}")
    print(f"Miss count: {stats['miss_count']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")

if __name__ == "__main__":
    main()
EOF
