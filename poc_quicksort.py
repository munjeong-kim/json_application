"""Quick Sort PoC: pivot 전략별 성능, 데이터 패턴별 성능, 내장 sorted()와 비교"""

import random
import time
import sys

sys.setrecursionlimit(20000)


def quicksort(arr, pivot_strategy="last"):
    """리스트를 새로 만들며 정렬 (재귀, in-place 아님 — 구현 단순화 목적)"""
    if len(arr) <= 1:
        return arr

    pivot = _choose_pivot(arr, pivot_strategy)
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]

    return quicksort(less, pivot_strategy) + equal + quicksort(greater, pivot_strategy)


def _choose_pivot(arr, strategy):
    if strategy == "first":
        return arr[0]
    if strategy == "last":
        return arr[-1]
    if strategy == "middle":
        return arr[len(arr) // 2]
    if strategy == "random":
        return random.choice(arr)
    raise ValueError(f"unknown strategy: {strategy}")


def make_data(pattern, n):
    if pattern == "random":
        return [random.randint(0, n) for _ in range(n)]
    if pattern == "sorted":
        return list(range(n))
    if pattern == "reversed":
        return list(range(n, 0, -1))
    if pattern == "duplicates":
        return [random.randint(0, 10) for _ in range(n)]
    raise ValueError(f"unknown pattern: {pattern}")


def bench(func, repeat=3):
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    return sum(times) / len(times)


def main():
    n = 3000  # sorted/reversed 패턴에서 first/last pivot은 O(n^2)라 너무 크면 오래 걸림
    patterns = ["random", "sorted", "reversed", "duplicates"]
    pivot_strategies = ["first", "last", "middle", "random"]

    print(f"=== 데이터 크기: {n} ===\n")

    # 1) 데이터 패턴별 x pivot 전략별 비교
    print("=== Quick Sort: 데이터 패턴 x Pivot 전략 (평균 실행시간, ms) ===")
    header = f"{'pattern':12s}" + "".join(f"{s:>12s}" for s in pivot_strategies)
    print(header)
    for pattern in patterns:
        row = f"{pattern:12s}"
        for strategy in pivot_strategies:
            data = make_data(pattern, n)
            avg = bench(lambda: quicksort(data.copy(), strategy), repeat=3)
            row += f"{avg * 1000:12.2f}"
        print(row)

    # 2) 내장 sorted()와 비교 (random 데이터, best pivot 전략인 random/middle 사용)
    print("\n=== Quick Sort(random pivot) vs 내장 sorted() (random 데이터) ===")
    for size in [1000, 5000, 20000]:
        data = make_data("random", size)
        qs_time = bench(lambda: quicksort(data.copy(), "random"), repeat=5)
        builtin_time = bench(lambda: sorted(data.copy()), repeat=5)
        print(
            f"n={size:6d}  quicksort: {qs_time*1000:8.3f} ms  "
            f"sorted(): {builtin_time*1000:8.3f} ms  "
            f"(배율: {qs_time/builtin_time:.1f}x)"
        )

    # 정확성 검증
    sample = make_data("random", 500)
    assert quicksort(sample.copy()) == sorted(sample)
    print("\n정확성 검증 통과 (quicksort 결과 == sorted() 결과)")


if __name__ == "__main__":
    main()
