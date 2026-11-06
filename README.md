# smarandache-wellin-lean

Smarandache–Wellin 소수의 무한성 추측을 Lean 4 + Mathlib 으로 연구하는 프로젝트.

## 문제

소수열 p₁ = 2, p₂ = 3, p₃ = 5, … 의 처음 n 개를 십진수로 이어 붙인 수를 Wₙ 이라 한다.

```
W₀ = 0,   Wₙ₊₁ = 10^{d(pₙ₊₁)} · Wₙ + pₙ₊₁        (d(m) = m 의 십진 자릿수)
2, 23, 235, 2357, 235711, 23571113, …           (OEIS A019518)
```

소수인 항이 Smarandache–Wellin 소수다. 알려진 소수 항의 인덱스는 다음이 전부다 (OEIS A046035).

```
n = 1, 2, 4, 128, 174, 342, 435, 1429
```

그 뒤로는 n ≤ 4·10⁶ 까지 탐색에서 새 항이 없다 (MathWorld, 2025-11 기준).

**최종 목표 명제** (`SW.SWInfinitude`, 미해결 추측):

```lean
∀ N : ℕ, ∃ n : ℕ, N < n ∧ (W n).Prime
```

지수적으로 커지는 결정적 수열에서 소수가 무한히 많다는 증명은 알려진 사례가 없다. 그래서 이 프로젝트의
현실적 산출물은 완전 증명이 아니라, (1) 형식화된 구조, (2) 각 전략의 핵심 미해결 보조명제, (3) 조건부 정리,
(4) 실패 기록이다. 자세한 것은 `docs/research-plan.md` 참고.

## 현재 상태

아래는 모두 `sorry` 와 추가 공리 없이 검증되었다 (`SmarandacheWellin/Audit.lean` 이 `#print axioms` 를 출력한다).

| 명제 | Lean 이름 | 파일 |
| --- | --- | --- |
| W 1 = 2, W 2 = 23, W 3 = 235, W 4 = 2357 와 소수성 | `W_one` … `W_four_prime` | `Basic.lean` |
| Wₙ 은 엄격 증가, 단사 | `W_strictMono`, `W_injective` | `Basic.lean` |
| 임의 모듈러스의 나머지 점화식 | `W_succ_mod` | `Basic.lean` |
| Wₙ₊₁ ≡ pₙ₊₁ (mod 10) | `W_succ_modEq_ten` | `Basic.lean` |
| 목표 명제 ↔ 소수 인덱스 무한 ↔ 서로 다른 SW 소수 무한 | `swInfinitude_iff_infinite`, `swInfinitude_iff_image` | `Basic.lean` |
| 10 ≡ 1 (mod m) ⇒ Wₙ ≡ Σ pₖ (mod m); m = 3, 9 | `W_modEq_sum_of_ten_modEq_one`, `W_modEq_sum_three`, `W_modEq_sum_nine` | `Congruence.lean` |
| 소수 q ∣ Wₙ, q ≠ pₙ₊₁ ⇒ q ∤ Wₙ₊₁ | `not_dvd_succ_of_dvd` | `Congruence.lean` |
| n ≥ 4 ⇒ gcd(Wₙ, 10) = 1 | `coprime_ten_of_three_le` | `Congruence.lean` |
| 두 칸 점화식과 블록 Bₙ: q ∣ Wₙ ⇒ (q ∣ Wₙ₊₂ ↔ q ∣ Bₙ) | `W_add_two`, `dvd_add_two_iff` | `Avoid.lean` |
| Q1, \|S\| = 1: 연속한 세 항 중 하나는 q ∤; q ∤ Wₙ 인 n 무한 | `not_dvd_of_three_consecutive`, `exists_not_dvd` | `Avoid.lean` |
| Q1, \|S\| = 2 의 환원: (q ∤ Bₙ ∧ r ∤ Bₙ 인 n 무한) ⇒ (q ∤ Wₙ ∧ r ∤ Wₙ 인 n 무한) | `block_dvd_of_cover`, `avoid_two_of_block` | `Avoid.lean` |
| 3 ∣ Bₙ ↔ 3 ∣ pₙ₊₁ + pₙ₊₂ | `three_dvd_B_iff` | `Avoid.lean` |
| 덮개 아래서 q ∣ Bₙ ∨ q ∣ Bₙ₊₁; (q ∤ Bₙ ∧ q ∤ Bₙ₊₁ 인 n 무한) ⇒ Q1({q, r}) | `block_dvd_or_succ_of_cover`, `avoid_two_of_block_succ` | `Avoid.lean` |
| H3 (mod 3 같은 류의 연속 소수 세 쌍 무한) ⇒ Q1({3, r}) | `not_three_dvd_B_of_modEq`, `avoid_three_of_triples` | `Avoid.lean` |
| 같은 류 쌍에서 q ∣ Bₙ ⇒ q ∣ 10^d + 1; 어떤 소수도 10^d + 1, 10^{d+1} + 1 을 둘 다 못 나눔 | `dvd_pow_add_one_of_dvd_B`, `not_dvd_pow_add_one_both` | `Avoid.lean` |
| Hd(q) (두 자릿수 구간의 같은 류 세 쌍) ⇒ Q1({q, r}) | `dvd_pow_add_one_of_cover`, `avoid_two_of_digit_triples` | `Avoid.lean` |
| 10^e ≤ n < 10^{e+1} ⇒ n 은 e+1 자리 | `digitsLen_eq` | `Interval.lean` |
| IT(q) (큰 x 마다 [x, 3x] 에 같은 류의 연속 소수 세 개) ⇒ Hd(q), IT(3) ⇒ H3 | `digitTriples_of_intervalTriples`, `sameClassTriples3_of_intervalTriples` | `Interval.lean` |
| IT(q) ⇒ Q1({q, r}) | `avoid_two_of_interval_triples`, `avoid_three_of_interval_triples` | `Interval.lean` |

미해결 보조명제와 그 상태는 `docs/lemma-ledger.md` 에 기록한다.

## 빌드

툴체인은 `lean-toolchain` 에, Mathlib 은 `lakefile.toml` 에 `v4.35.0` 으로 고정되어 있다.

```sh
lake build
```

**Mathlib 을 새로 받지 말 것.** 같은 버전의 Mathlib 이 빌드된 프로젝트가 있으면 `.lake/packages` 를
APFS clone(copy-on-write) 으로 가져온다. 추가 디스크를 거의 쓰지 않는다.

```sh
for p in mathlib Cli plausible LeanSearchClient importGraph proofwidgets aesop Qq batteries; do
  cp -c -R -p ../ctic-lean/.lake/packages/$p .lake/packages/$p
done
```

그런 프로젝트가 없으면 `lake exe cache get` 으로 미리 빌드된 olean 을 받는다.

## 블루프린트

`blueprint/src/content.tex` 는 [leanblueprint](https://github.com/PatrickMassot/leanblueprint) 형식의 설계도다.
정의와 보조정리마다 `\lean{...}` (Lean 이름), `\uses{...}` (의존), `\leanok` (Lean 검증), `\notready` (계획 없음)
를 붙이고, 웹 판·PDF 판과 색칠된 의존 그래프를 만든다. 문헌 정리 (H3, IT(q) 의 근거) 는 `\lean` 없는 별도 노드로,
열린 문제 (Q1 |S| ≥ 3, Q2, Q4, 목표 추측) 는 `\notready` 노드로 둔다.

```bash
uv tool install leanblueprint        # graphviz 필요: brew install graphviz
scripts/blueprint.sh                 # 웹 판 + PDF 판 + 대응 검사 (블루프린트 ↔ 소스 ↔ Audit)
scripts/blueprint.sh --lean          # 위에 더해 모든 \lean 이름을 lake env lean 으로 확인 (수 분)
scripts/blueprint.sh serve           # http://127.0.0.1:8000 , 의존 그래프는 dep_graph_document.html
```

산출물 `blueprint/web/`, `blueprint/print/print.pdf`, `blueprint/lean_decls` 는 커밋하지 않는다.
leanblueprint 의 `checkdecls` 는 외부 Lake 패키지를 의존성에 넣어야 해서 쓰지 않고,
`scripts/check_blueprint.py` 가 같은 검사와 역방향 검사 (소스의 모든 선언이 블루프린트에 있는가,
블루프린트의 정리가 모두 감사되는가) 를 한다. 그래프의 색: 초록 = Lean 검증, 파랑 배경 = 의존이 모두 갖춰져
형식화 가능 (문헌 노드는 범위 밖이라 형식화하지 않음), 주황 테두리 = 계획 없음.

장부 (`docs/lemma-ledger.md`) 와의 분담: 블루프린트는 의존 구조와 Lean 대응의 기준이고, 장부는 상태의 세부,
실패 이유, 계산 근거를 기록한다. 새 정리를 추가하면 `Audit.lean`, 블루프린트, 장부를 함께 고친다.

## 검증 기준

- 라이브러리에 들어가는 정리는 `sorry`, 새 `axiom` 없이 컴파일되어야 한다. 미증명 명제는 Lean 파일이 아니라
  `docs/lemma-ledger.md` 에만 둔다.
- `#print axioms` 결과에 `propext`, `Classical.choice`, `Quot.sound` 외의 것이 보이면 안 된다.
- `native_decide` 는 쓰지 않는다. 불가피하면 장부에 명시한다.
- `Defs.lean` 의 정의와 목표 명제를 바꾸는 변경은 증명 변경과 분리해서 검토한다. 탐색 중에 문제가 더 쉬운
  것으로 바뀌는 일을 막기 위해서다.

## 구조

```
SmarandacheWellin/
  Defs.lean         정의: digitsLen, W, SWInfinitude
  Basic.lean        초기값, 증가, 나머지 점화식, 끝자리, 목표 명제의 동치 서술
  Congruence.lean   mod 3·9 항등식, 연속 두 항 비가분 보조정리, 10 과 서로소
  Avoid.lean        유한 소수 집합 회피 (Q1): |S| = 1 증명, |S| = 2 는 Shiu 형 연속 소수 가정 (H3, Hd(q)) 으로 환원
  Interval.lean     구간 판 Shiu 가정 IT(q) 에서 H3, Hd(q) 를 유도 (자릿수 보조정리)
  Audit.lean        #print axioms
blueprint/src/      leanblueprint 설계도 (content.tex, 매크로, 설정)
docs/
  research-plan.md  전략 비교, 가장 약한 고리 규칙, 작업 방식
  lemma-ledger.md   보조명제 장부 (명제·상태·가정·역할·실패 이유·근거)
  references.md     참고문헌
  experiments/      계산 실험 로그 (날짜, 명령, 출력)
  literature/       문헌 대조 보고서 (원문 인용, 판정, 미확인 사항)
scripts/
  sw_mod.py         Wₙ mod m 궤도 계산 (Wₙ 자체는 만들지 않는다)
  sw_avoid.py       유한 집합 회피 비율과 블록 조건 비율 (Q1, H1)
  sw_triples.py     연속 소수 가정 H3, HB(q), Hd(q) 의 비율·개수
  sw_heuristic.py   보정 확률 모형 E(a, b) 와 관측 비교
  check_blueprint.py 블루프린트 ↔ Lean 소스 ↔ Audit 대응 검사
  blueprint.sh      블루프린트 빌드와 검사
```
