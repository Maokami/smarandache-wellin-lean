#!/usr/bin/env python3
"""장부 H3, HB(q), Hd(q) (Avoid.lean 의 연속 소수 가정) 의 계산 점검. 증명이 아니다.

(1) HB(q): q ∤ B_n ∧ q ∤ B_{n+1} 인 n 의 비율. (1 - 1/q)^2 과 비교. (avoid_two_of_block_succ 의 가정)
(2) H3: p_{m+1} ≡ p_{m+2} ≡ p_{m+3} (mod 3) 인 m 의 비율. 독립 모형 1/4 과 비교. (SameClassTriples3)
(3) Hd(q): 자릿수 d 마다, mod q 같은 류의 연속 소수 세 쌍 가운데 p_{m+2}, p_{m+3} 가 d 자리인 것의 개수.
    모든 d 에서 0 이 아니면 Hd(q) 의 계산상 지지. 더불어 q ∣ 10^d + 1 인 d 를 적는다 (그 d 에서는
    같은 류 쌍 (p_{n+1}, p_{n+2}) 에서 q ∣ B_n 이 되어 두 자릿수 구간 논법이 필요한 이유).

사용:  python3 -I scripts/sw_triples.py --n 200000
"""
import argparse
import itertools
import math


def primes_upto(limit: int) -> list[int]:
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, math.isqrt(limit) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(range(i * i, limit + 1, i)))
    return list(itertools.compress(range(limit + 1), sieve))


def first_primes(n: int) -> list[int]:
    limit = 15 if n < 6 else int(n * (math.log(n) + math.log(math.log(n)))) + 10
    ps = primes_upto(limit)
    assert len(ps) >= n + 3, (len(ps), n)
    return ps[: n + 3]


def block(ps: list[int], n: int, q: int) -> int:
    """B_n mod q, B_n = 10^{d(p_{n+2})} p_{n+1} + p_{n+2}. ps[0] = p_1."""
    a, b = ps[n], ps[n + 1]
    return (pow(10, len(str(b)), q) * a + b) % q


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--primes", type=int, nargs="*", default=[3, 7, 11, 13, 17, 19, 23])
    args = ap.parse_args()
    N = args.n
    ps = first_primes(N)
    start = 3  # n ≥ 3 부터 (p_{n+1} ≥ 7, 2·3·5 배제)

    print(f"# n 범위: {start} ≤ n < {N} (p_{{n+1}} ≤ {ps[N - 1]})")
    print()
    print("## (1) HB(q): q ∤ B_n ∧ q ∤ B_{n+1} 비율  vs  (1-1/q)^2")
    for q in args.primes:
        cnt = sum(1 for n in range(start, N) if block(ps, n, q) and block(ps, n + 1, q))
        print(f"q={q:3d}: {cnt / (N - start):.4f}   독립 예측 {(1 - 1 / q) ** 2:.4f}")
    print()
    print("## (2) H3: p_{m+1} ≡ p_{m+2} ≡ p_{m+3} (mod 3) 비율  vs  독립 1/4")
    cnt3 = sum(1 for m in range(start, N) if ps[m] % 3 == ps[m + 1] % 3 == ps[m + 2] % 3)
    pair3 = sum(1 for m in range(start, N) if ps[m] % 3 == ps[m + 1] % 3)
    print(f"세 쌍 비율 {cnt3 / (N - start):.4f}, 같은 류 쌍 비율 {pair3 / (N - start):.4f} (독립 1/2)")
    print()
    print("## (3) Hd(q): 자릿수 d 별, mod q 같은 류 세 쌍 중 p_{m+2}, p_{m+3} 가 d 자리인 개수")
    maxd = len(str(ps[N + 1]))
    for q in args.primes:
        bad = [d for d in range(1, 40) if (pow(10, d, q) + 1) % q == 0]
        counts = {d: 0 for d in range(1, maxd + 1)}
        total = {d: 0 for d in range(1, maxd + 1)}
        for m in range(start, N):
            d2, d3 = len(str(ps[m + 1])), len(str(ps[m + 2]))
            if d2 != d3:
                continue
            total[d2] += 1
            if ps[m] % q == ps[m + 1] % q == ps[m + 2] % q:
                counts[d2] += 1
        row = ", ".join(f"d={d}: {counts[d]}/{total[d]}" for d in range(2, maxd + 1) if total[d])
        print(f"q={q:3d} (q ∣ 10^d+1 인 d: {bad[:4]}{'…' if bad else ''}): {row}")


if __name__ == "__main__":
    main()
