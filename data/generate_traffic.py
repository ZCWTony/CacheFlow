import random
import time

class TrafficGenerator:
    def __init__(self, mode="stable"):
        self.mode = mode

    def stream(self):
        while True:
            if self.mode == "burst":
                if random.random() < 0.1:
                    for _ in range(100):
                        yield {"src": random.randint(1,100), "dst": random.randint(1,100)}
                else:
                    yield {"src": random.randint(1,100), "dst": random.randint(1,100)}
            else:
                yield {"src": random.randint(1,100), "dst": random.randint(1,100)}
            time.sleep(0.001)
