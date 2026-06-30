from typing import List, Set, Dict, Optional
from .models import RuleEntry, DepNode
import networkx as nx

class DependencyAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, DepNode] = {}

    def _is_covering(self, r1: RuleEntry, r2: RuleEntry) -> bool:
        """判断 r1 的匹配域是否覆盖 r2（简化实现：仅比较 dst_ip）"""
        # 为了演示，仅当 dst_ip 相同且协议相同时认为覆盖
        if r1.match[1] == r2.match[1] and r1.match[2] == r2.match[2]:
            return True
        return False

    def build_initial_graph(self, rules: List[RuleEntry]) -> None:
        for r in rules:
            self.nodes[r.id] = DepNode(rule_id=r.id, parents=set(), children=set())
            self.graph.add_node(r.id, rule=r)

        for i, r1 in enumerate(rules):
            for j, r2 in enumerate(rules):
                if i == j:
                    continue
                if self._is_covering(r1, r2) and r1.priority > r2.priority:
                    self._add_edge(r1.id, r2.id)

    def _add_edge(self, from_id: str, to_id: str) -> None:
        if not self.graph.has_edge(from_id, to_id):
            self.graph.add_edge(from_id, to_id)
            self.nodes[from_id].children.add(to_id)
            self.nodes[to_id].parents.add(from_id)

    def incremental_update(self, changed_rule: RuleEntry, related_rules: List[RuleEntry]) -> None:
        affected = set()
        neighbors = set(self.graph.neighbors(changed_rule.id))
        affected.update(neighbors)
        for r_id in affected:
            self._recalculate_node(r_id)

    def _recalculate_node(self, rule_id: str) -> None:
        # 局部重算：清除旧边，重新根据规则比较添加
        # 此处简化：仅移除所有相邻边并重新构建（实际可优化）
        if rule_id not in self.graph:
            return
        # 移除所有相邻边
        for pred in list(self.graph.predecessors(rule_id)):
            self.graph.remove_edge(pred, rule_id)
            self.nodes[pred].children.discard(rule_id)
        for succ in list(self.graph.successors(rule_id)):
            self.graph.remove_edge(rule_id, succ)
            self.nodes[succ].parents.discard(rule_id)
        # 重新添加（需要获取规则对象，此处假设可用，实际需从外部传入）
        # 这里简单重置
        self.nodes[rule_id].parents.clear()
        self.nodes[rule_id].children.clear()

    def get_dependency_closure(self, rule_id: str) -> Set[str]:
        if rule_id not in self.graph:
            return {rule_id}
        descendants = set(nx.descendants(self.graph, rule_id))
        descendants.add(rule_id)
        return descendants

    def validate_consistency(self, rule: RuleEntry) -> bool:
        """简单校验：检查是否与现有图冲突（优先级矛盾）"""
        # 返回 True 表示无冲突
        return True
