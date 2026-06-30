import asyncio
from typing import List, Set

class ConsistencyScheduler:
    def __init__(self):
        self.buffer_version = 0
        self.latency_sum = 0.0
        self.update_count = 0

    async def prepare_migration(self, rule_set: Set[str]) -> None:
        self._lock_dependencies(rule_set)
        shadow_ids = await self._install_shadow_rules(rule_set)
        self.buffer_version += 1
        await self._switch_traffic_to_hardware(rule_set)
        await self._remove_shadow_rules(shadow_ids)
        self._unlock_dependencies(rule_set)

    def _lock_dependencies(self, rule_set: Set[str]) -> None:
        # 模拟锁定
        pass

    async def _install_shadow_rules(self, rule_set: Set[str]) -> List[str]:
        # 模拟安装影子规则
        return list(rule_set)

    async def _switch_traffic_to_hardware(self, rule_set: Set[str]) -> None:
        # 模拟切换
        await asyncio.sleep(0.001)

    async def _remove_shadow_rules(self, shadow_ids: List[str]) -> None:
        # 模拟移除
        await asyncio.sleep(0.001)

    def _unlock_dependencies(self, rule_set: Set[str]) -> None:
        pass

    async def incremental_update(self, changed_rule_id: str) -> None:
        # 模拟增量更新
        await asyncio.sleep(0.005)

    def record_latency(self, latency: float) -> None:
        self.latency_sum += latency
        self.update_count += 1

    def get_avg_delay(self) -> float:
        if self.update_count == 0:
            return 0.0
        return self.latency_sum / self.update_count
