import Mathlib

/-!
# Smarandache–Wellin 수열의 정의

소수열은 `Nat.nth Nat.Prime` 로 0부터 센다: `Nat.nth Nat.Prime 0 = 2`, `… 1 = 3`, `… 2 = 5`.
`W n` 은 처음 `n` 개 소수를 십진수로 이어 붙인 수다.

    W 0 = 0,   W (n+1) = 10 ^ d(p_{n+1}) · W n + p_{n+1}        (d(m) = m 의 십진 자릿수)
    W 1 = 2, W 2 = 23, W 3 = 235, W 4 = 2357, …                 (OEIS A019518)

소수인 항이 Smarandache–Wellin 소수다 (인덱스는 OEIS A046035).
그 무한성 `SWInfinitude` 가 이 프로젝트의 최종 목표 명제이며, 아직 증명되지 않은 추측이다.

`Nat.nth` 가 noncomputable 이므로 `W` 도 noncomputable 이다. 구체적인 값은
`Nat.nth_prime_zero_eq_two` 같은 보조정리로 계산한다 (`Basic.lean`).
-/

namespace SW

/-- `m` 의 십진 자릿수. `m = 0` 이면 `0`. -/
def digitsLen (m : ℕ) : ℕ := (Nat.digits 10 m).length

/-- 처음 `n` 개 소수를 이어 붙인 수. `n+1` 번째 소수는 `Nat.nth Nat.Prime n`. -/
noncomputable def W : ℕ → ℕ
  | 0 => 0
  | n + 1 => 10 ^ digitsLen (Nat.nth Nat.Prime n) * W n + Nat.nth Nat.Prime n

/-- 최종 목표 명제: 소수인 항의 인덱스가 무한히 많다. **미해결 추측**이며 여기서는 서술만 한다. -/
def SWInfinitude : Prop := ∀ N : ℕ, ∃ n : ℕ, N < n ∧ (W n).Prime

end SW
