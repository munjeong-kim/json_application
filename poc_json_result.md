# JSON vs orjson PoC 결과

- 실행 스크립트: `poc_json_compare.py`
- 테스트 데이터: 1만 건의 중첩 dict 리스트 (문자열, 숫자, bool, 리스트, 중첩 객체 포함)
- 환경: Python 3.13 (.venv), orjson 3.11.9

## 결과

| 항목 | json | orjson | 배율 |
|---|---|---|---|
| 직렬화 (dumps) | 18.98 ms | 2.15 ms | 약 9배 빠름 |
| 파일 저장 | 20.70 ms | 2.92 ms | 약 7배 빠름 |
| 파싱 (loads) | 23.36 ms | 10.87 ms | 약 2배 빠름 |
| 결과 파일 크기 | 2,296,763 bytes | 2,086,769 bytes | orjson이 약 9% 작음 |

## 원본 출력

```
=== 직렬화 (dumps) ===
json.dumps                     avg:   18.979 ms  (min: 18.202 ms)
orjson.dumps                   avg:    2.150 ms  (min: 2.087 ms)

=== 파일 저장 ===
json -> file                   avg:   20.698 ms  (min: 19.535 ms)
orjson -> file                 avg:    2.916 ms  (min: 2.727 ms)

=== 파싱 (loads) ===
json.loads                     avg:   23.356 ms  (min: 19.346 ms)
orjson.loads                   avg:   10.868 ms  (min: 9.578 ms)

=== 결과 파일 크기 ===
out_json.json:   2,296,763 bytes
out_orjson.json: 2,086,769 bytes
```

## 참고 사항

- orjson은 `bytes`를 반환하므로 `str`이 필요하면 `.decode()` 필요
- orjson은 datetime/UUID 등 일부 타입을 기본 지원하지만, 커스텀 객체는 `default` 콜백 필요
- orjson은 기본적으로 공백 없는 컴팩트 출력이라 파일 크기도 더 작음
