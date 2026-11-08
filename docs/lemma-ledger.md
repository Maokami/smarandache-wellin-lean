# 보조명제 장부

상태: `추측` / `계산상 지지` / `자연어 증명` / `Lean 검증` / `반례 발견` / `보류`.
`Lean 검증` 은 `sorry` 와 추가 공리 없이 컴파일되고 `#print axioms` 가 `propext`, `Classical.choice`, `Quot.sound`
만 보이는 것을 뜻한다.

표기: pₖ 는 k 번째 소수 (p₁ = 2). Lean 에서는 pₙ₊₁ = `Nat.nth Nat.Prime n`.

의존 그래프와 Lean 이름의 기준은 블루프린트 (`blueprint/src/content.tex`) 다. 블루프린트 노드 제목에 붙은 B1, C4 등이 이 장부의 ID 다.

## 검증된 것

| ID | 명제 | 상태 | 가정 | 역할 | 비고 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | W 1 = 2, W 2 = 23, W 3 = 235, W 4 = 2357; 2, 23, 2357 소수, 235 합성 | Lean 검증 | 없음 | 정의가 OEIS A019518/A046035 와 일치함을 확인 | | `Basic.lean` |
| B2 | Wₙ 엄격 증가, 단사 | Lean 검증 | 없음 | 기반 | | `W_strictMono` |
| B3 | Wₙ₊₁ mod m = (10^{d} mod m · (Wₙ mod m) + pₙ₊₁ mod m) mod m | Lean 검증 | 없음 | Wₙ 을 만들지 않고 나머지를 추적하는 근거 | `scripts/sw_mod.py` 가 이 점화식을 쓴다 | `W_succ_mod` |
| B4 | Wₙ₊₁ ≡ pₙ₊₁ (mod 10) | Lean 검증 | 없음 | 끝자리 | | `W_succ_modEq_ten` |
| B5 | SWInfinitude ↔ {n ∣ Wₙ 소수} 무한 ↔ {Wₙ ∣ 소수} 무한 | Lean 검증 | 없음 | 목표 명제의 서술 고정 | | `swInfinitude_iff_image` |
| C1 | 10 ≡ 1 (mod m) ⇒ Wₙ ≡ Σₖ≤ₙ pₖ (mod m). 특히 m = 3, 9 | Lean 검증 | 없음 | 작은 모듈러스 구조 | mod 11 은 10 ≡ −1 이라 교대합이 되며 자릿수 패리티가 끼어든다. 미형식화 | `W_modEq_sum_of_ten_modEq_one` |
| C2 | 소수 q ∣ Wₙ, q ≠ pₙ₊₁ ⇒ q ∤ Wₙ₊₁ | Lean 검증 | 없음 | 고정 소수 하나는 연속 두 항을 못 나눈다 | 대화에서는 pₙ₊₁ > q 로 썼으나 q ≠ pₙ₊₁ 이면 충분. **서로 다른 소수가 번갈아 나누는 가능성은 배제 못 함** | `not_dvd_succ_of_dvd`, `not_dvd_succ_of_dvd_of_lt` |
| C3 | n ≥ 4 ⇒ gcd(Wₙ, 10) = 1 | Lean 검증 | 없음 | 2, 5 자동 배제. 휴리스틱의 보정 인자 | | `coprime_ten_of_three_le` |
| C4 | Wₙ₊₂ = 10^{d(pₙ₊₂)+d(pₙ₊₁)} Wₙ + Bₙ, Bₙ := 10^{d(pₙ₊₂)} pₙ₊₁ + pₙ₊₂. q ∣ Wₙ ⇒ (q ∣ Wₙ₊₂ ↔ q ∣ Bₙ) | Lean 검증 | 없음 | 두 칸 간격의 가분성을 소수 블록으로 환원 (C2 의 두 칸 판) | | `W_add_two`, `dvd_add_two_iff` |
| C5 | Q1, \|S\| = 1: 소수 q 에 대해 연속한 세 항 Wₙ₊₁, Wₙ₊₂, Wₙ₊₃ 중 하나는 q ∤. 따라서 q ∤ Wₙ 인 n 이 무한 | Lean 검증 | 없음 | Q1 의 첫 경우 | | `not_dvd_of_three_consecutive`, `exists_not_dvd` |
| C6 | Q1, \|S\| = 2 의 환원: HB(q) ⇒ (q ∤ Wₙ ∧ r ∤ Wₙ 인 n 이 무한), r 은 임의의 소수 | Lean 검증 (조건부) | HB(q) | Q1 을 W 가 아니라 연속 소수의 조건으로 바꿈 | 두 소수가 모든 항을 덮으려면 번갈아 나눠야 하므로 q 는 n 또는 n+1 에서 두 칸 간격으로 나누고, C4 로 q ∣ Bₙ ∨ q ∣ Bₙ₊₁ (`block_dvd_or_succ_of_cover`). 처음 판 (q ∤ Bₙ ∧ r ∤ Bₙ 인 n 무한 ⇒ 결론, `block_dvd_of_cover`, `avoid_two_of_block`) 도 남겨 둠. HB(q) 는 r 과 무관하다 | `block_dvd_or_succ_of_cover`, `avoid_two_of_block_succ` |
| C7 | Q1, S = {3, r}: H3 ⇒ (3 ∤ Wₙ ∧ r ∤ Wₙ 인 n 이 무한), r 은 임의의 소수 | Lean 검증 (조건부) | H3 | 3 이 든 모든 쌍을 소수만의 가정 하나로 처리 | 3 ∣ Bₙ ↔ 3 ∣ pₙ₊₁ + pₙ₊₂ (`three_dvd_B_iff`) 이고, pₙ₊₁ ≡ pₙ₊₂ (mod 3), 3 ∤ pₙ₊₁ 이면 합은 2pₙ₊₁ ≢ 0. 그래서 같은 류의 세 쌍은 HB(3) 을 준다 | `not_dvd_nth_prime_of_le`, `not_three_dvd_B_of_modEq`, `avoid_three_of_triples` |
| C8 | pₙ₊₁ ≡ pₙ₊₂ (mod q), q ∤ pₙ₊₁, q ∣ Bₙ ⇒ q ∣ 10^{d(pₙ₊₂)} + 1. 소수 q 는 10^d + 1 과 10^{d+1} + 1 을 동시에 못 나눈다 | Lean 검증 | 없음 | 같은 류의 쌍에서 블록 조건을 자릿수 조건으로 바꿈 | Bₙ ≡ pₙ₊₁(10^d + 1). 둘 다 나누면 q ∣ 9, q = 3 인데 3 ∤ 10^d + 1 | `dvd_pow_add_one_of_dvd_B`, `not_three_dvd_pow_add_one`, `not_dvd_pow_add_one_both` |
| C9 | Q1, S = {q, r}: Hd(q) ⇒ (q ∤ Wₙ ∧ r ∤ Wₙ 인 n 이 무한), q, r 임의의 소수 | Lean 검증 (조건부) | Hd(q) | \|S\| = 2 전체를 구간 판 Shiu 정리 하나로 환원 | 덮개 아래서 d 자리 세 쌍은 q ∣ 10^d + 1, d+1 자리 세 쌍은 q ∣ 10^{d+1} + 1 을 주어 C8 과 모순 | `dvd_pow_add_one_of_cover`, `avoid_two_of_digit_triples` |
| Q1-two | IT-all 이면 모든 소수 q, r 와 모든 N 에 대해 N < n, q ∤ Wₙ, r ∤ Wₙ 인 n 이 있다 | Lean 검증 (조건부) | `IntervalTriplesAll` (모든 소수 q ≥ 3 에 대한 IT(q)) | \|S\| = 2 전체의 조건부 결론을 한 선언으로 연결 | q ≥ 3 은 C9 의 구간 판 환원, q = 2 는 C3·C5. IT-all 자체는 Lean 밖의 가정이며 최종 소수 무한성 추측은 미해결 | `avoid_two_of_intervalTriplesAll`, blueprint `cor:Q1-two`. PR #4 head `a17c050` 의 CI·Blueprint 통과 후 병합 |

## 미해결

| ID | 명제 | 상태 | 가정 | 역할 | 실패 이유·장애물 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| H3 | pₘ₊₁ ≡ pₘ₊₂ ≡ pₘ₊₃ (mod 3) 인 m 이 무한히 많다 (`SameClassTriples3`) | 자연어 증명 (문헌) | 없음 | C7 의 가정. 성립하면 3 이 든 모든 쌍에서 Q1 | W 와 무관한 소수만의 명제. **Banks–Freiberg–Turnage-Butterbaugh (2015) Corollary 3** (D = 3, m = 3) 이 "무한히 많은 r" 형태로 그대로 준다. Shiu (2000) 의 임의 길이 문자열, Maynard (2016) Thm 3.3 (양의 비율) 에서도 따른다. Lean 밖의 가정으로 둔다 (Maynard 체의 형식화는 범위 밖). n < 2·10⁶ 에서 비율 0.18 (독립 0.25; 연속 소수가 같은 류를 피하는 편향). **Mathlib 에 없음** | `docs/experiments/2026-11-05-triples-2M.txt` |
| HB(q) | q ∤ Bₙ ∧ q ∤ Bₙ₊₁ 인 n 이 무한히 많다 | 계산상 지지 | 없음 | C6 의 가정. q 하나만 성립해도 임의의 r 에 대해 Q1({q, r}) | q = 3 이면 H3 과 동치. n < 2·10⁶ 비율: 3: 0.18, 7: 0.67, 11: 0.84, 13: 0.83, 17: 0.94, 19: 0.89, 23: 0.91. 10^d ≡ −1 (mod q) 인 자릿수에서는 Bₙ ≡ pₙ₊₂ − pₙ₊₁ 이라 간격 조건이 됨. 일반 q 는 Hd(q) 를 거쳐 증명 가능 (C9) | `docs/experiments/2026-11-05-triples-2M.txt` |
| Hd(q) | 임의로 큰 M 뒤에, mod q 같은 류의 연속 소수 세 쌍이 d 자리 안에도 d+1 자리 안에도 있는 d 가 존재 (`DigitTriples q`) | Lean 검증 (조건부: IT(q)) | 없음 | C9 의 가정. 성립하면 \|S\| = 2 의 Q1 완결 | IT(q) 에서 Lean 으로 유도 (`digitTriples_of_intervalTriples`, `Interval.lean`): [10^e, 3·10^e] 의 수는 모두 e+1 자리. 계산: q ≤ 13 은 d ≥ 6 에서 매번 관측, q = 17 은 d = 7 에서 11 개가 첫 관측, q = 19, 23 은 d = 8 에서야 13, 3 개로 약한 지지 | `docs/experiments/2026-11-05-triples-2M.txt` |
| IT(q) | 어떤 x₀ 가 있어 x ≥ x₀ 이면 [x, 3x] 안에 mod q 같은 류의 연속 소수 세 개가 있다 (`IntervalTriples q`) | 자연어 증명 (문헌, 증명 내부 식) | 없음 | Hd(q), H3 의 공통 근원. IT(q) ⇒ Q1({q, r}) (`avoid_two_of_interval_triples`) | **Maynard (2016) Theorem 3.3 증명의 식 (6.24)** 에서 x = 10^e/q 로 두면 따른다 (ε = 1, m = 2). 정리문 자체는 "[x, 2x]" 형태가 아니며 [x, Tx] (T = T(q, m, ε)) 까지만 준다. 그래서 상태를 `자연어 증명` 중에서도 "증명 내부 식 인용" 으로 구분해 둔다. Theorem 3.1 + 정의 (2.1) 경로가 정리문 기반 대안. 상세: `docs/literature/2026-11-05-shiu-bft-maynard.md` (C) | `docs/references.md` |
| H1 | q ∤ Bₙ ∧ r ∤ Bₙ 인 n 이 무한히 많다 | 보류 (HB(q) 로 대체) | 없음 | C6 의 처음 가정 | HB(q) 보다 강하고 r 까지 끌어들인다. 더 이상 필요 없음 | `docs/experiments/2026-11-05-avoid-200k.txt` |
| Q1 | 임의의 유한 소수 집합 S (\|S\| ≥ 3) 에 대해 ∀ q ∈ S, q ∤ Wₙ 인 n 이 무한히 많다 | 계산상 지지 | 없음 | 체 방법 1단계 (research-plan §3 의 (A) 의 약한 형태) | \|S\| = 1 은 C5. \|S\| = 2 는 C6·C7·C9 로 Shiu 형 가정 (H3, Hd(q)) 에 환원됨. \|S\| ≥ 3 은 덮는 패턴이 주기적일 필요가 없어 C6 의 환원이 바로 되지 않는다. n ≤ 2·10⁵ 에서 회피 비율이 독립 모형 ∏(1−1/q) 와 0.3% 이내 일치 | `docs/experiments/2026-11-05-avoid-200k.txt` |
| Q2 | 고정된 m (gcd(m,10)=1) 에 대해 Wₙ mod m 의 방문 빈도는 균등하다 | 계산상 지지 | 없음 | 동역학·체 접점. Q1 의 입력 | 각 단계가 Z/m 의 순열이라도 궤도가 균등분포한다는 보장은 없다. pₙ mod m 의 균등분포(Dirichlet)가 누적 상태의 균등분포를 함의하지 않는다 | n ≤ 2·10⁵, m ∈ {3,7,9,11,13,17,19,23}: 모든 나머지의 방문 횟수가 균등 기대값의 ±3% 이내 (`docs/experiments/2026-11-04-swmod-200k.txt`). 증명 아님 |
| Q3 | Q2 류의 분포 가정 H 아래서 (A) 또는 더 약한 결론이 따른다 | 미정 | H 명시 필요 | 조건부 정리 | H 가 원래 추측의 재서술이 아닌지 점검해야 함 | 미착수 |
| Q4 | 분포 정보로 "남은 항이 큰 소수들의 곱일 가능성" 을 배제한다 | 추측 | 미정 | 가장 약한 고리 규칙의 3 번. 핵심 미해결 단계 | 일반 체 방법의 패리티 장벽 | 미착수 |
| G | SWInfinitude | 추측 | 없음 | 최종 목표 | 계산: n = 1429 이후 n ≤ 4·10⁶ 까지 새 항 없음 (MathWorld, 2025-11). 유한 계산으로 판정 불가. 보정 확률 모형(c = 2.5): E(4,1429) = 2.98 vs 관측 6, E(1430, 4·10⁶) = 1.49 vs 관측 0 (P₀ ≈ 0.23). 다음 항의 기대 위치 n ~ 10¹⁰–10¹² 이라 계산 탐색은 사실상 불가능 | `Defs.lean`, `docs/experiments/2026-11-05-heuristic-4e6.txt` |

## 반례·폐기

(아직 없음)
