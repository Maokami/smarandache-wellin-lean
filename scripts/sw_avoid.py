#!/usr/bin/env python3
"""장부 Q1 (유한 소수 집합 회피) 의 계산 점검. 증명이 아니다.

(1) 유한 소수 집합 S 에 대해 "S 의 어느 원소도 W_n 을 나누지 않는" n (1 ≤ n ≤ N) 의 비율을 세고
    독립 모형의 예측 ∏_{q∈S} (1 - 1/q) 와 비교한다.
(2) 두 소수 q, r 에 대해 블록 B_n = 10^{d(p_{n+2})} p_{n+1} + p_{n+2} 가 q 로도 r 로도 나누어지지 않는
    n 의 비율을 세고 (1 - 1/q)(1 - 1/r) 와 비교한다. 이것이 Avoid.lean 의 avoid_two_of_block 의 가정이다.

사용:  python3 -I scripts/sw_avoid.py --n 200000
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
    assert len(ps) >= n + 1, (len(ps), n)
    return ps[: n + 1]  # B_N 에 p_{N+1} 이 필요하므로 하나 더


def residues(ps: list[int], q: int) -> list[int]:
    """r[n] = W_n mod q, n = 0..len(ps)."""
    r = [0]
    x = 0
    for p in ps:
        x = (pow(10, len(str(p)), q) * x + p) % q
        r.append(x)
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=200000)
    a = ap.parse_args()
    N = a.n
    ps = first_primes(N)
    Q = [3, 7, 11, 13, 17, 19, 23]
    res = {q: residues(ps[:N], q) for q in Q}

    print(f"# (1) S 회피 비율, 1 ≤ n ≤ {N}")
    for k in range(1, len(Q) + 1):
        S = Q[:k]
        cnt = sum(1 for n in range(1, N + 1) if all(res[q][n] != 0 for q in S))
        pred = math.prod(1 - 1 / q for q in S)
        print(f"S={S}: avoid={cnt / N:.4f}  independent≈{pred:.4f}  (count={cnt})")

    print(f"# (2) 블록 조건 비율: q∤B_n ∧ r∤B_n, 0 ≤ n < {N}")
    for q, r in [(3, 7), (3, 11), (3, 13), (7, 11), (7, 13), (11, 13)]:
        cnt = 0
        for n in range(N):
            p1, p2 = ps[n], ps[n + 1]
            d2 = len(str(p2))
            bq = (pow(10, d2, q) * p1 + p2) % q
            br = (pow(10, d2, r) * p1 + p2) % r
            if bq and br:
                cnt += 1
        pred = (1 - 1 / q) * (1 - 1 / r)
        print(f"(q,r)=({q},{r}): block-avoid={cnt / N:.4f}  independent≈{pred:.4f}  (count={cnt})")

    print(f"# (3) mod 3: 연속 소수가 같은 류 (3 ∤ p_{{n+1}}+p_{{n+2}}) 인 비율, n ≥ 2")
    same = sum(1 for n in range(2, N) if (ps[n] + ps[n + 1]) % 3 != 0)
    print(f"same-class-mod-3={same / (N - 2):.4f}  (independent≈0.5; 연속 소수는 다른 류를 선호한다고 알려져 있음)")


if __name__ == "__main__":
    main()
