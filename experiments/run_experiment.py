import yaml
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.cacheflow import CacheFlowController
from data.generate_traffic import TrafficGenerator

def run_experiment(config_path: str) -> None:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    controller = CacheFlowController()
    traffic_gen = TrafficGenerator(mode=config['traffic_mode'])

    controller.load_rules(config['rule_file'])

    start = time.time()
    stats = {'hits': 0, 'misses': 0, 'updates': 0, 'out_of_order': 0}

    for packet in traffic_gen.stream():
        result = controller.process_packet(packet)
        if result['hit']:
            stats['hits'] += 1
        else:
            stats['misses'] += 1
            controller.install_rule(result['suggested_rule'])

        if time.time() - start > config['duration_sec']:
            break

    hit_rate = stats['hits'] / (stats['hits'] + stats['misses']) if (stats['hits'] + stats['misses']) > 0 else 0.0
    print(f"Hit Rate: {hit_rate:.2%}")
    print(f"Controller Interactions: {stats['misses']}")

if __name__ == "__main__":
    run_experiment("experiments/configs/cacheflow_full.yaml")
