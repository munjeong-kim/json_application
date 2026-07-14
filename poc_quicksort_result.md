# Quick Sort PoC 결과

- 실행 스크립트: `poc_quicksort.py`
- 데이터 크기: 3,000 (패턴 x pivot 비교), 1,000 / 5,000 / 20,000 (내장 정렬 비교)
- 환경: Python 3.13 (.venv)

## 1. 데이터 패턴 x Pivot 전략 (평균 실행시간, ms)

| pattern | first | last | middle | random |
|---|---|---|---|---|
| random | 4.41 | 3.92 | 3.75 | 4.20 |
| sorted | 249.07 | 261.80 | 2.54 | 3.78 |
| reversed | 257.91 | 259.35 | 2.54 | 3.80 |
| duplicates | 0.62 | 0.66 | 0.64 | 0.77 |

**관찰**
- 이미 정렬되었거나 역순인 데이터에서 `first`/`last` pivot은 매번 최소/최대값을 골라 O(n²) 최악 케이스에 빠짐 (250ms대)
- `middle`/`random` pivot은 어떤 패턴에서도 안정적으로 빠름 (2~4ms)
- 중복이 많은 데이터는 pivot 전략과 무관하게 빠름 (equal 그룹으로 많이 빠짐)

## 2. Quick Sort(random pivot) vs 내장 sorted() (random 데이터)

| n | quicksort | sorted() | 배율 |
|---|---|---|---|
| 1,000 | 1.294 ms | 0.064 ms | 20.3x |
| 5,000 | 6.397 ms | 0.409 ms | 15.6x |
| 20,000 | 29.238 ms | 2.107 ms | 13.9x |

**관찰**
- 내장 `sorted()`(Timsort, C 구현)가 순수 Python Quick Sort보다 14~20배 빠름
- 데이터가 커질수록 격차가 다소 줄어드는 경향 (리스트 컴프리헨션 오버헤드 비중 감소)

## 정확성 검증

`quicksort(sample) == sorted(sample)` 통과

## 결론

- 실무에서는 pivot을 무조건 `first`/`last`로 고정하면 정렬된 데이터에서 성능이 급격히 나빠질 위험이 있음 → `random`/`middle` pivot 권장
- 순수 Python 구현은 내장 `sorted()`(Timsort)를 성능으로 이길 수 없음 → 실제 서비스에서는 내장 정렬 사용 권장, Quick Sort는 알고리즘 학습/이해 목적으로 적합
