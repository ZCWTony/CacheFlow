#!/usr/bin/env python3
"""
CacheFlow P4Runtime 控制平面
负责：1) 连接BMv2交换机  2) 下发依赖感知的缓存规则
"""
import sys
import time
import argparse
import random
import grpc
from p4runtime_sh import P4RuntimeSH
from p4runtime_sh.p4runtime import p4runtime_pb2
from p4runtime_sh.shell import set_up, tear_down, get_p4info

# ---------- 模拟规则生成（与实验脚本保持一致）----------
def generate_test_rules(num_rules=100):
    """生成测试规则（五元组 + 动作）"""
    rules = []
    for i in range(num_rules):
        src_ip = f"10.0.0.{random.randint(1, 254)}"
        dst_ip = f"192.168.1.{random.randint(1, 254)}"
        proto = random.choice([6, 17])  # TCP/UDP
        src_port = random.randint(1024, 65535)
        dst_port = random.randint(1, 1024)
        action = random.choice([1, 0])  # 1:forward, 0:drop
        rules.append({
            "src": src_ip, "dst": dst_ip,
            "proto": proto, "src_port": src_port, "dst_port": dst_port,
            "action": action
        })
    return rules

def ip_to_bytes(ip_str):
    return bytes(map(int, ip_str.split('.')))

def install_rule(p4info, match_fields, action_id, action_params):
    """下发一条规则到cache_table"""
    table_entry = p4runtime_pb2.TableEntry()
    # 获取表ID（假设cache_table是第一个表）
    table_entry.table_id = 1  # 实际需从p4info解析，此处简化为固定值

    # 添加匹配键（五个字段）
    field_ids = [1, 2, 3, 4, 5]  # 对应src,dst,protocol,src_port,dst_port
    values = [
        ip_to_bytes(match_fields['src']),
        ip_to_bytes(match_fields['dst']),
        match_fields['proto'].to_bytes(1, 'big'),
        match_fields['src_port'].to_bytes(2, 'big'),
        match_fields['dst_port'].to_bytes(2, 'big')
    ]
    for fid, val in zip(field_ids, values):
        m = table_entry.match.add()
        m.field_id = fid
        m.ternary.value = val
        m.ternary.mask = b'\xff' * len(val)  # 精确匹配

    # 设置动作
    action = table_entry.action.action
    action.action_id = action_id
    for pid, pval in action_params:
        p = action.params.add()
        p.param_id = pid
        p.value = pval

    # 写入表项
    P4RuntimeSH.write(table_entry)
    return True

def main(sw_addr):
    # 连接到BMv2交换机
    set_up(grpc_addr=sw_addr, p4info_path="build/p4info.txt", bv2_path="build/cacheflow.json")
    print(f"[Controller] Connected to BMv2 at {sw_addr}")

    # 生成并下发100条规则
    rules = generate_test_rules(100)
    print(f"[Controller] Installing {len(rules)} rules...")
    for i, r in enumerate(rules):
        action_id = 1 if r['action'] == 1 else 0
        # forward需要port参数，drop不需要
        if action_id == 1:
            params = [(1, b'\x00\x01')]  # port=1
        else:
            params = []
        install_rule(get_p4info(), r, action_id, params)
        if i % 10 == 0:
            print(f"[Controller] Installed {i+1}/{len(rules)} rules")

    print("[Controller] All rules installed. Waiting for traffic...")

    # 周期性读取统计寄存器（每10秒）
    try:
        while True:
            time.sleep(10)
            # 读取寄存器（需要实现寄存器读取逻辑，此处演示）
            print("[Controller] Reading counters...")
    except KeyboardInterrupt:
        print("[Controller] Shutting down...")
    finally:
        tear_down()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sw-addr', default='127.0.0.1:50051')
    args = parser.parse_args()
    main(args.sw_addr)
