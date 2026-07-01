import yaml
import time
import sys
import os
import csv
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.cacheflow import CacheFlowController
from data.generate_traffic import TrafficGenerator

def run_experiment(config_path: str, output_dir: str = None):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    controller = CacheFlowController()
    traffic_gen = TrafficGenerator(mode=config['traffic_mode'])

    # 加载规则（如果规则文件存在）
    rule_file = config.get('rule_file')
    if rule_file and os.path.exists(rule_file):
        controller.load_rules(rule_file)
        print(f"Loaded rules from {rule_file}")
    else:
        print("Warning: No rule file found, using default rules.")

    start = time.time()
    stats = {
        'hits': 0,
        'misses': 0,
        'updates': 0,
        'out_of_order': 0,
        'total_packets': 0
    }

    duration = config.get('duration_sec', 30)
    for packet in traffic_gen.stream():
        result = controller.process_packet(packet)
        stats['total_packets'] += 1
        if result['hit']:
            stats['hits'] += 1
        else:
            stats['misses'] += 1
            controller.install_rule(result['suggested_rule'])

        if time.time() - start > duration:
            break

    hit_rate = stats['hits'] / stats['total_packets'] if stats['total_packets'] > 0 else 0.0
    print(f"Hit Rate: {hit_rate:.2%}")
    print(f"Controller Interactions: {stats['misses']}")

    # 保存结果到CSV
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_dir, f"experiment_{timestamp}.csv")
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        writer.writerow(['hit_rate', hit_rate])
        writer.writerow(['hits', stats['hits']])
        writer.writerow(['misses', stats['misses']])
        writer.writerow(['total_packets', stats['total_packets']])
        writer.writerow(['controller_interactions', stats['misses']])  # 简化
    print(f"Results saved to {csv_file}")

if __name__ == "__main__":
    # 如果传入参数则使用，否则默认运行mininet配置
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "experiments/configs/mininet_experiment.yaml"
    run_experiment(config_path)
