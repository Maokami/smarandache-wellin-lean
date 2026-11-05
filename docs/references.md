# 참고문헌

## 수열

- OEIS A019518, Smarandache–Wellin 수: https://oeis.org/A019518
- OEIS A046035, 소수인 항의 인덱스 (1, 2, 4, 128, 174, 342, 435, 1429). 주석: k ≤ 34736 까지 다른 항 없음 (Weisstein, 2015): https://oeis.org/A046035
- OEIS A263959, 소수 항의 자릿수 (1, 2, 4, 355, 499, 1171, 1543, 5719): https://oeis.org/A263959
- MathWorld, Smarandache–Wellin Prime. Rodenkirch 의 탐색: 1.5·10⁶ (2016), 2.5·10⁶ (2025-08-10), 4·10⁶ (2025-11-29), 새 소수 없음: https://mathworld.wolfram.com/Smarandache-WellinPrime.html

## AI + Lean 사례 (운영 방식의 참고)

- N. Sothanaphan, *Resolution of Erdős Problem #728: a writeup of Aristotle's Lean proof*, arXiv:2601.07421. GPT-5.2 Pro 의 비형식 논증을 Aristotle 이 Lean 으로 옮김. 팩토리얼 나눗셈 → 이항계수 → Kummer 정리로 표현을 바꾼 것이 핵심.
- Google DeepMind, AlphaProof Nexus (*Advancing Mathematics Research with AI-Driven Formal Proof Search*, arXiv:2605.22763; Science 2026-10). Erdős 9/353, OEIS 44/492. 공개 저장소의 OEIS 증명은 38개라는 지적이 있음 (arXiv:2608.11941).
- Harmonic, Aristotle 기술 논문. 자연어 증명을 보조명제로 분해 → 형식화 → 성공·실패를 자연어 추론으로 되돌림.
- Anthropic, Fermat 의 마지막 정리 Lean 형식화 (2026-09-04). 기존 증명의 형식화. 정리 의존 관계를 DAG 로 관리.
- OpenAI, Navier–Stokes (외력 있는 변형) 해결 주장과 Lean 형식화 (2026-09-08). 학계 검토 미완, Clay 연구소는 미해결로 취급, 우선권 분쟁 중.
- First Proof (arXiv:2602.05192, 2606.18119). OpenAI 는 2026-02 제출에서 2번 문제를 외부 검토 후 오답으로 정정.
- T. Tao, *AI contributions to Erdős problems* 위키. 2026-06-30 이후 갱신 중단. 선택 편향 주의: https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems

## 연속 소수의 나머지류 (장부 H3, Hd(q), IT(q) 의 근거)

상세 대조는 `docs/literature/2026-11-05-shiu-bft-maynard.md` (원문 인용 포함). 요약:

- D. K. L. Shiu, *Strings of congruent primes*, J. London Math. Soc. (2) 61 (2000), 359–373. DOI 10.1112/S0024610799007863.
  (a, q) = 1 이면 모든 k 에 대해 같은 류 a (mod q) 의 연속 소수 k 개가 존재. **원문 미열람** (유료). Thorne, Maynard, BFT,
  Lemke Oliver–Soundararajan 등 2차 문헌으로 재구성.
- W. D. Banks, T. Freiberg, C. L. Turnage-Butterbaugh, *Consecutive primes in tuples*, Acta Arith. 167 (2015), 261–266,
  arXiv:1311.7003. **Corollary 3**: (a, D) = 1, D ≥ 3, m ≥ 2 이면 p_{r+1} ≡ ⋯ ≡ p_{r+m} ≡ a (mod D) 인 r 이 무한히 많다.
  D = 3, m = 3 이 곧 **H3** (`SameClassTriples3`). "무한히 많다" 형태라 구간 [x, 2x] 판은 주지 않는다.
- J. Maynard, *Dense clusters of primes in subsets*, Compositio Math. 152 (2016), 1517–1554, arXiv:1405.2593.
  **Theorem 3.3**: 고정 m, q, (a, q) = 1 에 대해 p_n ≡ ⋯ ≡ p_{n+m} ≡ a (mod q), p_{n+m} − p_n ≤ ε log x 인 p_n ≤ x 가
  양의 비율. 증명 중 **식 (6.24)** (출판본; arXiv v2 는 (6.26)): x > x₀(ε, q) 인 모든 x 에 대해 x ≤ n ≤ 2x 이고
  [qn, qn + η log x] 안에 같은 류의 연속 소수 ≫ log k 개가 있는 n 이 ≫ x / (q^k exp(C₆ k⁵)) 개. 여기서 x = 10^{e}/q 로 두면
  `[10^e, 3·10^e]` 안에 같은 류의 연속 소수 세 개가 있다: 이것이 **IT(q)** (`IntervalTriples q`) 이고 **Hd(q)** 가 따른다.
  "[x, 2x] 형태" 를 정리문으로 적은 출판 논문은 없고, 정리문 (Thm 3.3) 만으로는 [x, Tx] (T 는 q, m, ε 에 따른 상수) 까지만
  나온다. Theorem 3.1 + 정의 (2.1) (A(x) = [x, 2x)) + "Moreover" 절 (연속 소수) 경로도 같은 결론을 준다.
- R. J. Lemke Oliver, K. Soundararajan, *Unexpected biases in the distribution of consecutive primes*, PNAS 113 (2016),
  E4446–E4454, arXiv:1603.03720. 연속 소수가 같은 류를 피하는 편향. 처음 10⁶ 개 소수에서 mod 3 같은 류 쌍 432,086 개
  (비율 0.432; 우리 측정 0.4243 @ 2·10⁵, 0.4352 @ 2·10⁶ 와 정합). 서로 다른 류의 패턴 (a₁, …, a_m) 은 어느 단일
  비상수 패턴도 무한성이 증명되어 있지 않다 (서론; Lau arXiv:2409.12819). 따라서 이 프로젝트의 가정은 **같은 류** 패턴만 쓴다.
- Mathlib 에는 Dirichlet 정리 (`Mathlib.NumberTheory.LSeries.PrimesInAP`) 만 있고 연속 소수의 나머지류 결과는 없다.

## Lean

- Lean 4 / Mathlib v4.35.0. `Nat.nth`, `Nat.nth_prime_*_eq_*`, `Nat.ModEq`, `Nat.digits`.
- `#print axioms` 로 `sorryAx` 와 추가 공리를 확인한다. `native_decide` 는 커널 환원과 신뢰 범위가 다르다.
