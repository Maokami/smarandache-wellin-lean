#!/usr/bin/env python3
"""W_n mod m 의 궤도를 계산한다. W_n 자체는 만들지 않는다 (Basic.lean 의 W_succ_mod).

사용:  python3 -I scripts/sw_mod.py --n 100000 --mod 3 7 11 13
출력:  각 m 에 대해 나머지별 방문 횟수, m | W_n 인 n 의 개수와 처음 몇 개.
목적:  docs/lemma-ledger.md 의 Q2 (균등분포 추측) 를 작은 계산으로 압박한다. 증명이 아니다.
"""
import argparse
import math


def primes_upto(limit: int) -> list[int]:
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, math.isqrt(limit) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(range(i * i, limit + 1, i)))
    return [i for i, b in enumerate(sieve) if b]


def first_primes(n: int) -> list[int]:
    # p_n < n (ln n + ln ln n) for n ≥ 6 (Rosser–Schoenfeld)
    limit = 15 if n < 6 else int(n * (math.log(n) + math.log(math.log(n)))) + 10
    ps = primes_upto(limit)
    assert len(ps) >= n, (len(ps), n)
    return ps[:n]


def orbit(ps: list[int], m: int):
    r = 0
    counts = [0] * m
    zeros = []
    for i, p in enumerate(ps, start=1):
        r = (pow(10, len(str(p)), m) * r + p) % m
        counts[r] += 1
        if r == 0:
            zeros.append(i)
    return counts, zeros


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=10000, help="처음 n 개 소수까지")
    ap.add_argument("--mod", type=int, nargs="+", default=[3, 7, 11, 13], help="모듈러스들")
    a = ap.parse_args()
    ps = first_primes(a.n)
    for m in a.mod:
        counts, zeros = orbit(ps, m)
        print(
            f"m={m:>4}  visits={counts}  zeros={len(zeros)} (uniform≈{a.n / m:.0f})  first zeros={zeros[:8]}"
        )


if __name__ == "__main__":
    main()
