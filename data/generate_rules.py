import json
import random

def generate_synthetic_rules(num_rules: int = 100000) -> list:
    rules = []
    for i in range(num_rules):
        rule = {
            "id": f"r_{i}",
            "priority": random.randint(1, 65535),
            "match": {
                "src_ip": f"10.0.{random.randint(0,255)}.{random.randint(0,255)}",
                "dst_ip": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
                "proto": random.choice(["TCP", "UDP"]),
                "src_port": random.randint(1024, 65535),
                "dst_port": random.randint(1, 1024)
            },
            "action": random.choice(["FORWARD", "DROP"])
        }
        if i > 0 and i % 10 == 0:
            rule["match"]["dst_ip"] = rules[i-1]["match"]["dst_ip"]
        rules.append(rule)
    return rules

if __name__ == "__main__":
    rules = generate_synthetic_rules(100000)
    with open("data/rules/sample_100k.json", "w") as f:
        json.dump(rules, f, indent=2)
    print("Generated 100,000 synthetic rules.")
