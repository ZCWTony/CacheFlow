cat > p4/emulator.py << 'EOF'
#!/usr/bin/env python3
"""
P4 交换机模拟器（纯 Python）
模拟 TCAM 表查找，与控制平面交互，统计命中/未命中。
"""
import random
import time

class P4SwitchEmulator:
    def __init__(self, capacity=1024):
        self.table = {}          # key: tuple(五元组), value: action
        self.capacity = capacity
        self.hit_count = 0
        self.miss_count = 0

    def add_rule(self, key, action):
        """添加规则到 TCAM 表"""
        if len(self.table) >= self.capacity:
            # 简单替换：删除第一条（实际可用依赖感知替换，这里仅为演示）
            first_key = next(iter(self.table))
            del self.table[first_key]
        self.table[key] = action

    def lookup(self, packet):
        """查找包，返回命中或未命中"""
        # 五元组提取（假设包中包含 src_ip, dst_ip, protocol, src_port, dst_port）
        key = (packet.get('src_ip'), packet.get('dst_ip'),
               packet.get('protocol'), packet.get('src_port'), packet.get('dst_port'))
        if key in self.table:
            self.hit_count += 1
            return True, self.table[key]
        else:
            self.miss_count += 1
            return False, None

    def get_stats(self):
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total else 0.0
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'total': total,
            'hit_rate': hit_rate
        }
EOF
