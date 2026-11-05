import SmarandacheWellin.Congruence

/-!
# 유한 소수 집합 회피 (장부 Q1)

Q1: 유한 소수 집합 `S` 에 대해, `S` 의 어느 원소도 `W n` 을 나누지 않는 `n` 이 무한히 많은가?

* `|S| = 1`: 무조건 참. 연속한 세 항 중 하나는 `q` 로 나누어지지 않는다
  (`not_dvd_of_three_consecutive`, `exists_not_dvd`).
* `|S| = 2`: 소수만의 조건으로 환원된다. 두 소수 `q, r` 가 `N` 이후의 모든 항을 덮으려면 번갈아 나눠야 하고,
  `q` 가 두 칸 간격으로 나누면 `q` 는 그 사이 블록 `B n = 10^{d(p_{n+2})} · p_{n+1} + p_{n+2}` 를 나눈다
  (`dvd_add_two_iff`, `block_dvd_of_cover`). 따라서

      "q ∤ B n 이고 r ∤ B n 인 n 이 무한히 많다"  ⟹  Q1(S = {q, r})          (`avoid_two_of_block`)

  이 가정은 `W` 가 아니라 **연속 소수 쌍의 분포**에 관한 것이다. `q = 3` 이면 `3 ∣ B n ↔ 3 ∣ p_{n+1} + p_{n+2}`
  (`three_dvd_B_iff`), 즉 연속 소수가 mod 3 에서 같은 류에 있으면 `3 ∤ B n` 이다.
* `|S| ≥ 3`: 덮는 패턴이 주기적일 필요가 없어서 같은 환원이 바로 되지 않는다. 미해결.
-/

namespace SW

/-- `n < p_{n+1}`. -/
lemma lt_nth_prime (n : ℕ) : n < Nat.nth Nat.Prime n := by
  induction n with
  | zero => rw [Nat.nth_prime_zero_eq_two]; norm_num
  | succ n ih =>
    have : Nat.nth Nat.Prime n < Nat.nth Nat.Prime (n + 1) :=
      (Nat.nth_strictMono Nat.infinite_setOfPred_prime) (Nat.lt_succ_self n)
    omega

/-- 인접한 두 소수 `p_{n+1}, p_{n+2}` 를 이어 붙인 블록. -/
noncomputable def B (n : ℕ) : ℕ :=
  10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) * Nat.nth Nat.Prime n + Nat.nth Nat.Prime (n + 1)

/-- 두 칸 점화식: `W (n+2) = 10^{d(p_{n+2}) + d(p_{n+1})} · W n + B n`. -/
theorem W_add_two (n : ℕ) :
    W (n + 2)
      = 10 ^ (digitsLen (Nat.nth Nat.Prime (n + 1)) + digitsLen (Nat.nth Nat.Prime n)) * W n + B n := by
  show W (n + 1 + 1) = _
  rw [W_succ, W_succ, B, pow_add]
  ring

/-- `q ∣ W n` 이면, `q ∣ W (n+2)` 는 블록 `B n` 의 가분성과 같다. -/
theorem dvd_add_two_iff {q n : ℕ} (hdvd : q ∣ W n) : q ∣ W (n + 2) ↔ q ∣ B n := by
  rw [W_add_two]
  exact Nat.dvd_add_right (dvd_mul_of_dvd_right hdvd _)

/-! ### |S| = 1 -/

/-- 소수 `q` 에 대해 연속한 세 항 `W (n+1), W (n+2), W (n+3)` 중 하나는 `q` 로 나누어지지 않는다. -/
theorem not_dvd_of_three_consecutive {q : ℕ} (hq : q.Prime) (n : ℕ) :
    ¬ q ∣ W (n + 1) ∨ ¬ q ∣ W (n + 2) ∨ ¬ q ∣ W (n + 3) := by
  by_contra h
  push Not at h
  obtain ⟨h1, h2, h3⟩ := h
  have hq2 : q = Nat.nth Nat.Prime (n + 1) := by
    by_contra hne
    exact not_dvd_succ_of_dvd hq h1 hne h2
  have hq3 : q = Nat.nth Nat.Prime (n + 2) := by
    by_contra hne
    exact not_dvd_succ_of_dvd hq h2 hne h3
  have := (Nat.nth_strictMono Nat.infinite_setOfPred_prime).injective (hq2.symm.trans hq3)
  omega

/-- Q1, `|S| = 1`: 어떤 소수 `q` 도 `W n` 을 결국 항상 나누지는 못한다. -/
theorem exists_not_dvd {q : ℕ} (hq : q.Prime) (N : ℕ) : ∃ n, N < n ∧ ¬ q ∣ W n := by
  rcases not_dvd_of_three_consecutive hq N with h | h | h
  · exact ⟨N + 1, by omega, h⟩
  · exact ⟨N + 2, by omega, h⟩
  · exact ⟨N + 3, by omega, h⟩

/-! ### |S| = 2 : 블록 조건으로 환원 -/

/-- 두 소수 `q, r` 가 `N` 이후의 모든 항을 덮는다면, `q, r ≤ n` 인 모든 `n > N` 에서 `q ∣ B n ∨ r ∣ B n`. -/
theorem block_dvd_of_cover {q r : ℕ} (hq : q.Prime) (hr : r.Prime) {N : ℕ}
    (hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n) {n : ℕ} (hn : N < n) (hnq : q ≤ n) (hnr : r ≤ n) :
    q ∣ B n ∨ r ∣ B n := by
  have h1 := lt_nth_prime n
  have h2 := lt_nth_prime (n + 1)
  have hq1 : q ≠ Nat.nth Nat.Prime n := by omega
  have hq2 : q ≠ Nat.nth Nat.Prime (n + 1) := by omega
  have hr1 : r ≠ Nat.nth Nat.Prime n := by omega
  have hr2 : r ≠ Nat.nth Nat.Prime (n + 1) := by omega
  rcases hcover n hn with hqn | hrn
  · have hnq1 : ¬ q ∣ W (n + 1) := not_dvd_succ_of_dvd hq hqn hq1
    have hrn1 : r ∣ W (n + 1) := (hcover (n + 1) (by omega)).resolve_left hnq1
    have hnr2 : ¬ r ∣ W (n + 2) := not_dvd_succ_of_dvd hr hrn1 hr2
    have hqn2 : q ∣ W (n + 2) := (hcover (n + 2) (by omega)).resolve_right hnr2
    exact Or.inl ((dvd_add_two_iff hqn).mp hqn2)
  · have hnr1 : ¬ r ∣ W (n + 1) := not_dvd_succ_of_dvd hr hrn hr1
    have hqn1 : q ∣ W (n + 1) := (hcover (n + 1) (by omega)).resolve_right hnr1
    have hnq2 : ¬ q ∣ W (n + 2) := not_dvd_succ_of_dvd hq hqn1 hq2
    have hrn2 : r ∣ W (n + 2) := (hcover (n + 2) (by omega)).resolve_left hnq2
    exact Or.inr ((dvd_add_two_iff hrn).mp hrn2)

/-- Q1, `|S| = 2` 의 조건부 형태: `q ∤ B n ∧ r ∤ B n` 인 `n` 이 무한히 많으면
`q ∤ W n ∧ r ∤ W n` 인 `n` 도 무한히 많다. 가정은 연속 소수 쌍 `(p_{n+1}, p_{n+2})` 에 관한 것이다. -/
theorem avoid_two_of_block {q r : ℕ} (hq : q.Prime) (hr : r.Prime)
    (hB : ∀ M, ∃ n, M < n ∧ ¬ q ∣ B n ∧ ¬ r ∣ B n) (N : ℕ) :
    ∃ n, N < n ∧ ¬ q ∣ W n ∧ ¬ r ∣ W n := by
  by_contra hcon
  push Not at hcon
  have hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n := fun n hn => by
    by_cases h : q ∣ W n
    · exact Or.inl h
    · exact Or.inr (hcon n hn h)
  obtain ⟨n, hn, hnq, hnr⟩ := hB (max N (max q r))
  have := block_dvd_of_cover hq hr hcover (by omega : N < n) (by omega : q ≤ n) (by omega : r ≤ n)
  tauto

/-- `q = 3` 일 때 블록 조건은 연속 소수의 합에 관한 조건이다. -/
theorem three_dvd_B_iff (n : ℕ) :
    3 ∣ B n ↔ 3 ∣ Nat.nth Nat.Prime n + Nat.nth Nat.Prime (n + 1) := by
  have h10 : (10 : ℕ) ^ digitsLen (Nat.nth Nat.Prime (n + 1)) ≡ 1 [MOD 3] := by
    simpa using (show (10 : ℕ) ≡ 1 [MOD 3] by decide).pow (digitsLen (Nat.nth Nat.Prime (n + 1)))
  have hB : B n ≡ Nat.nth Nat.Prime n + Nat.nth Nat.Prime (n + 1) [MOD 3] := by
    unfold B
    simpa using (h10.mul_right (Nat.nth Nat.Prime n)).add_right (Nat.nth Nat.Prime (n + 1))
  rw [← Nat.modEq_zero_iff_dvd, ← Nat.modEq_zero_iff_dvd]
  exact ⟨fun h => hB.symm.trans h, fun h => hB.trans h⟩

end SW
