"""json vs orjson PoC: 파싱(loads) / 저장(dumps, 파일 저장) 성능 비교"""

import json
import orjson
import time
import random
import string
import os


def make_sample_data(n_records=10000):
    def random_str(length=8):
        return "".join(random.choices(string.ascii_letters, k=length))

    return [
        {
            "id": i,
            "name": random_str(10),
            "email": f"{random_str(6)}@example.com",
            "age": random.randint(18, 80),
            "is_active": random.choice([True, False]),
            "tags": [random_str(5) for _ in range(5)],
            "meta": {"created_at": "2026-07-14T00:00:00Z", "score": random.random()},
        }
        for i in range(n_records)
    ]


def bench(label, func, repeat=5):
    times = []
    result = None
    for _ in range(repeat):
        start = time.perf_counter()
        result = func()
        times.append(time.perf_counter() - start)
    avg = sum(times) / len(times)
    print(f"{label:30s} avg: {avg * 1000:8.3f} ms  (min: {min(times)*1000:.3f} ms)")
    return result


def main():
    data = make_sample_data(10000)

    print("=== 직렬화 (dumps) ===")
    json_bytes = bench("json.dumps", lambda: json.dumps(data).encode("utf-8"))
    orjson_bytes = bench("orjson.dumps", lambda: orjson.dumps(data))

    print("\n=== 파일 저장 ===")
    bench("json -> file", lambda: open("out_json.json", "wb").write(json.dumps(data).encode("utf-8")))
    bench("orjson -> file", lambda: open("out_orjson.json", "wb").write(orjson.dumps(data)))

    print("\n=== 파싱 (loads) ===")
    bench("json.loads", lambda: json.loads(json_bytes))
    bench("orjson.loads", lambda: orjson.loads(orjson_bytes))

    print("\n=== 결과 파일 크기 ===")
    print(f"out_json.json:   {os.path.getsize('out_json.json'):,} bytes")
    print(f"out_orjson.json: {os.path.getsize('out_orjson.json'):,} bytes")

    # 정리
    os.remove("out_json.json")
    os.remove("out_orjson.json")


if __name__ == "__main__":
    main()
