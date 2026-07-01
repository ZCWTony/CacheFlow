import random
import json
from .cache_manager import CacheManager
from .scheduler import ConsistencyScheduler
from .models import RuleEntry

class CacheFlowController:
    def __init__(self):
        self.cache_manager = CacheManager(capacity=1024)
        self.scheduler = ConsistencyScheduler()
        self.hit_count = 0
        self.miss_count = 0

    def _parse_rule(self, rule_json: dict) -> RuleEntry:
        return RuleEntry(
            id=rule_json.get("id", "unknown"),
            match=(rule_json.get("src_ip", "0.0.0.0"),
                   rule_json.get("dst_ip", "0.0.0.0"),
                   rule_json.get("proto", "TCP"), 0, 0),
            priority=rule_json.get("priority", 0),
            action=rule_json.get("action", "FORWARD")
        )

    def install_rule(self, rule_json: dict) -> bool:
        rule = self._parse_rule(rule_json)
        if not self.cache_manager.dep_analyzer.validate_consistency(rule):
            return False
        return self.cache_manager.handle_miss(rule.id)

    def query_cache(self, match_fields: tuple) -> list:
        return list(self.cache_manager.meta_index.hash_map.values())

    def sync_hw(self, batch_updates: list) -> bool:
        for update in batch_updates:
            self.scheduler.prepare_migration(set(update))
        return True

    def metrics(self, window_ms: int) -> dict:
        return {
            "hit_rate": self.cache_manager.get_hit_rate(),
            "avg_latency": self.scheduler.get_avg_delay()
        }

    def process_packet(self, packet: dict) -> dict:
        # 模拟包处理，实际应进行依赖检查和缓存查询
        # 这里使用随机命中演示，后续可替换为真正的依赖查询
        if random.random() < 0.6:
            self.hit_count += 1
            self.cache_manager.record_hit()
            return {"hit": True}
        else:
            self.miss_count += 1
            self.cache_manager.record_miss()
            # 模拟安装规则
            self.install_rule({"id": "suggested", "priority": 100, "action": "FORWARD"})
            return {"hit": False, "suggested_rule": {"id": "suggested"}}

    def load_rules(self, rule_file: str) -> None:
        """从JSON文件加载规则到cache_manager，每1000条打印进度"""
        try:
            with open(rule_file, 'r') as f:
                rules_data = json.load(f)
                total = len(rules_data)
                print(f"Loading {total} rules from {rule_file}...")
                for idx, rdata in enumerate(rules_data):
                    rule = self._parse_rule(rdata)
                    self.cache_manager.meta_index.add_rule(rule)
                    if (idx + 1) % 1000 == 0:
                        print(f"Loaded {idx + 1}/{total} rules")
                # 加载完成后，还可以构建依赖图（如有需要）
                # self.cache_manager.dep_analyzer.build_initial_graph(list of rules)
                print(f"Finished loading {total} rules from {rule_file}")
        except Exception as e:
            print(f"Error loading rules: {e}")