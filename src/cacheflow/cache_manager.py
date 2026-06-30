from typing import List, Optional, Set
from .models import CacheSlot, MetaIndex, RuleEntry
from .dependency import DependencyAnalyzer

class CacheManager:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.slots: List[CacheSlot] = []
        self.meta_index = MetaIndex()
        self.dep_analyzer = DependencyAnalyzer()
        self.hit_count = 0
        self.miss_count = 0

    def handle_miss(self, rule_id: str) -> bool:
        closure = self.dep_analyzer.get_dependency_closure(rule_id)
        needed_size = len(closure)
        free_slots = self.capacity - len(self.slots)
        if free_slots >= needed_size:
            self._load_closure(closure)
            return True
        else:
            self._evict_dependency_aware(needed_size - free_slots)
            self._load_closure(closure)
            return True

    def _evict_dependency_aware(self, needed: int) -> None:
        # 第一层：孤立冷规则
        candidates = [s for s in self.slots if not self.dep_analyzer.graph.has_node(s.rule_ref.id)]
        candidates.sort(key=lambda x: x.hotness)
        evicted = self._evict_candidates(candidates, needed)
        if evicted >= needed:
            return

        # 第二层：叶子节点（无子依赖）
        remaining = needed - evicted
        leaf_nodes = []
        for s in self.slots:
            if s.rule_ref.id in self.dep_analyzer.nodes:
                if len(self.dep_analyzer.nodes[s.rule_ref.id].children) == 0:
                    leaf_nodes.append(s)
        leaf_nodes.sort(key=lambda x: x.hotness * 0.5)
        self._evict_candidates(leaf_nodes, remaining)

    def _evict_candidates(self, candidates: List[CacheSlot], needed: int) -> int:
        count = 0
        for slot in candidates[:needed]:
            if slot in self.slots:
                self.slots.remove(slot)
                self.meta_index.remove_rule(slot.rule_ref.id)
                count += 1
        return count

    def _load_closure(self, closure: Set[str]) -> None:
        # 从控制器获取规则详情（此处模拟）
        for r_id in closure:
            # 假设从外部能获取规则对象，这里构造一个占位
            dummy_rule = RuleEntry(id=r_id, match=("0.0.0.0", "0.0.0.0", "TCP", 0, 0), priority=0, action="FORWARD")
            slot = CacheSlot(slot_id=len(self.slots), rule_ref=dummy_rule, hotness=0)
            self.slots.append(slot)
            self.meta_index.add_rule(dummy_rule)

    def get_hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total

    def record_hit(self) -> None:
        self.hit_count += 1

    def record_miss(self) -> None:
        self.miss_count += 1
