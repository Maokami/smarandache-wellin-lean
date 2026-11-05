#!/usr/bin/env python3
"""확률 모형 보정 (docs/research-plan.md §2). 증명이 아니다.

E(a, b) = Σ_{n=a}^{b} c / (D_n · ln 10),   c = 10/φ(10) = 2.5
  - D_n = Σ_{k≤n} d(p_k) 는 W_n 의 자릿수, 그러므로 ln W_n ≈ D_n ln 10.
  - n ≥ 4 부터 W_n 은 10 과 서로소 (Congruence.lean, coprime_ten_of_three_le) 이므로 2, 5 보정 인자 c 를 붙인다.
비교 대상:
  - 알려진 소수 항 인덱스 1, 2, 4, 128, 174, 342, 435, 1429 (OEIS A046035). n ≥ 4 인 것은 6 개.
  - 탐색 구간 [1430, 4·10^6] 에서 새 항 0 개 (MathWorld, Rodenkirch 2025-11-29).

사용:  python3 -I scripts/sw_heuristic.py --n-max 4000000
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-max", type=int, default=4_000_000)
    a = ap.parse_args()
    N = a.n_max
    limit = int(N * (math.log(N) + math.log(math.log(N)))) + 10
    ps = primes_upto(limit)
    assert len(ps) >= N
    c = 2.5
    ln10 = math.log(10)
    D = 0
    E = [0.0] * (N + 1)  # E[n] = Σ_{4 ≤ k ≤ n}
    for n in range(1, N + 1):
        D += len(str(ps[n - 1]))
        E[n] = E[n - 1] + (c / (D * ln10) if n >= 4 else 0.0)
    known = [1, 2, 4, 128, 174, 342, 435, 1429]
    print(f"# c = {c}, N = {N}, D_N = {D} 자리")
    print(f"E(4, 1429)      = {E[1429]:.3f}   observed = {sum(1 for k in known if k >= 4)}")
    print(f"E(1430, {N}) = {E[N] - E[1429]:.3f}   observed = 0   Poisson P(0) = {math.exp(-(E[N] - E[1429])):.3f}")
    print(f"E(4, {N})    = {E[N]:.3f}")
    print("# 소수 항 사이의 기대 간격: 다음 항이 나올 때까지 필요한 E 의 증가량 1 에 해당하는 N 의 배율")
    print("# 외삽 (D_n ln 10 ≈ p_n ≈ n ln n 이므로 E 의 증가량 ≈ c·Δ(ln ln N)):")
    for M in (10**7, 10**8, 10**9, 10**12):
        dE = c * (math.log(math.log(M)) - math.log(math.log(N)))
        print(f"  E({N}, {M:.0e}) ≈ {dE:.3f}")


if __name__ == "__main__":
    main()
