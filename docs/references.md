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

## Lean

- Lean 4 / Mathlib v4.35.0. `Nat.nth`, `Nat.nth_prime_*_eq_*`, `Nat.ModEq`, `Nat.digits`.
- `#print axioms` 로 `sorryAx` 와 추가 공리를 확인한다. `native_decide` 는 커널 환원과 신뢰 범위가 다르다.
