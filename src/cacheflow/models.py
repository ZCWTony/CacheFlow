from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import time

@dataclass
class RuleEntry:
    """原始规则实体"""
    id: str
    match: tuple          # 五元组或掩码
    priority: int
    action: str           # FORWARD / DROP
    version: int = 0

@dataclass
class DepNode:
    """依赖图节点"""
    rule_id: str
    parents: Set[str]     # 依赖的上级规则 (高优先级覆盖)
    children: Set[str]    # 下级规则
    weight: float = 0.0   # 依赖重要性权重

@dataclass
class CacheSlot:
    """TCAM缓存槽元信息"""
    slot_id: int
    rule_ref: RuleEntry
    timestamp: float = time.time()
    hotness: int = 0      # 热度计数 (滑动窗口)

class MetaIndex:
    """两层索引：哈希表 + 优先级链表"""
    def __init__(self):
        self.hash_map: Dict[str, RuleEntry] = {}
        self.priority_list: List[RuleEntry] = []

    def add_rule(self, rule: RuleEntry) -> None:
        self.hash_map[rule.id] = rule
        self.priority_list.append(rule)
        self.priority_list.sort(key=lambda x: x.priority)

    def get_by_id(self, rule_id: str) -> Optional[RuleEntry]:
        return self.hash_map.get(rule_id)

    def remove_rule(self, rule_id: str) -> None:
        if rule_id in self.hash_map:
            rule = self.hash_map.pop(rule_id)
            self.priority_list.remove(rule)
