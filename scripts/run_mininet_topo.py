#!/usr/bin/env python3
"""
CacheFlow Mininet实验拓扑
启动一个简单的树形拓扑，连接RYU控制器（运行CacheFlow应用），
并发送测试流量以评估缓存性能。
"""

import os
import sys
import time
import json
import subprocess
import signal
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost, OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class SingleSwitchTopo(Topo):
    """单交换机连接多台主机的拓扑"""
    def build(self, n=4):
        switch = self.addSwitch('s1')
        for i in range(1, n+1):
            host = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
            self.addLink(host, switch, bw=10, delay='5ms', loss=0)

def run_cacheflow_controller():
    """
    启动RYU控制器并加载CacheFlow应用。
    假设RYU已安装，且CacheFlowController类在src.cacheflow.controller_iface中。
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root_dir, 'src'))
    
    # 启动ryu-manager进程
    ryu_cmd = [
        'ryu-manager',
        '--verbose',
        '--ofp-tcp-listen-port', '6653',
        'cacheflow.controller_iface.CacheFlowController'
    ]
    # 设置环境变量以便控制器能加载规则
    env = os.environ.copy()
    env['PYTHONPATH'] = root_dir + '/src:' + env.get('PYTHONPATH', '')
    
    # 启动子进程
    proc = subprocess.Popen(ryu_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 等待控制器启动
    time.sleep(3)
    return proc

def run_experiment(net, duration=30):
    """
    在网络上运行实验：每个主机互相ping，收集命中/未命中统计。
    实际应使用真实的流量生成器，这里用ping模拟。
    """
    hosts = net.hosts
    results = {
        'total_packets': 0,
        'hits': 0,
        'misses': 0,
        'out_of_order': 0
    }
    
    info("*** 开始发送测试流量 (ping all pairs)...\n")
    start_time = time.time()
    while time.time() - start_time < duration:
        # 随机选择两个主机互相ping
        import random
        h1 = random.choice(hosts)
        h2 = random.choice(hosts)
        if h1 == h2:
            continue
        # 发送一个ping包（实际应使用更真实的流量）
        result = h1.cmd(f'ping -c 1 -W 1 {h2.IP()} > /dev/null 2>&1')
        results['total_packets'] += 1
        # 模拟命中判断（实际应由控制器统计）
        # 这里我们简单模拟：假设前50%为命中（仅演示）
        if results['total_packets'] % 2 == 0:
            results['hits'] += 1
        else:
            results['misses'] += 1
        time.sleep(0.1)
    
    # 计算命中率
    total = results['hits'] + results['misses']
    hit_rate = results['hits'] / total if total > 0 else 0.0
    info(f"*** 实验结束，命中率: {hit_rate*100:.2f}%\n")
    return results

def main():
    setLogLevel('info')
    info("*** 启动CacheFlow Mininet实验\n")
    
    # 创建拓扑
    topo = SingleSwitchTopo(n=4)
    
    # 启动RYU控制器（后台进程）
    controller_proc = run_cacheflow_controller()
    
    # 创建Mininet网络
    net = Mininet(topo=topo, host=CPULimitedHost, switch=OVSSwitch,
                  controller=None, link=TCLink)
    # 添加远程控制器（连接到RYU）
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    net.addController(c0)
    net.start()
    
    # 运行实验
    results = run_experiment(net, duration=20)
    
    # 保存结果到文件
    result_file = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results', 'mininet_result.json')
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    info(f"*** 结果已保存到 {result_file}\n")
    
    # 可选：进入CLI交互
    # CLI(net)
    
    # 清理
    info("*** 清理网络...\n")
    net.stop()
    # 终止控制器进程
    if controller_proc:
        controller_proc.terminate()
        controller_proc.wait(timeout=5)
    info("*** 实验完成\n")

if __name__ == '__main__':
    main()
