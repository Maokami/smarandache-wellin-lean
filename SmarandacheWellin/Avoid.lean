import SmarandacheWellin.Congruence

/-!
# 유한 소수 집합 회피 (장부 Q1)

Q1: 유한 소수 집합 `S` 에 대해, `S` 의 어느 원소도 `W n` 을 나누지 않는 `n` 이 무한히 많은가?

* `|S| = 1`: 무조건 참. 연속한 세 항 중 하나는 `q` 로 나누어지지 않는다
  (`not_dvd_of_three_consecutive`, `exists_not_dvd`).
* `|S| = 2`: 소수만의 조건으로 환원된다. 두 소수 `q, r` 가 `N` 이후의 모든 항을 덮으려면 번갈아 나눠야 하고,
  `q` 가 두 칸 간격으로 나누면 `q` 는 그 사이 블록 `B n = 10^{d(p_{n+2})} · p_{n+1} + p_{n+2}` 를 나눈다
  (`dvd_add_two_iff`, `block_dvd_of_cover`, `block_dvd_or_succ_of_cover`). 따라서

      "q ∤ B n 이고 r ∤ B n 인 n 이 무한히 많다"      ⟹  Q1(S = {q, r})      (`avoid_two_of_block`)
      "q ∤ B n 이고 q ∤ B (n+1) 인 n 이 무한히 많다"  ⟹  Q1(S = {q, r})      (`avoid_two_of_block_succ`)

  두 번째 형태는 `q` 하나의 조건만 쓴다. 이 가정은 `W` 가 아니라 **연속 소수의 분포**에 관한 것이다.
  - `q = 3`: `3 ∣ B n ↔ 3 ∣ p_{n+1} + p_{n+2}` (`three_dvd_B_iff`) 이므로, mod 3 에서 같은 류인 연속 소수
    세 쌍 `p_{m+1} ≡ p_{m+2} ≡ p_{m+3}` 이 무한히 많다는 가정 `SameClassTriples3` (Shiu 2000 형) 아래서
    임의의 `r` 에 대해 Q1(S = {3, r}) 이 성립한다 (`avoid_three_of_triples`).
  - 일반 `q`: 같은 류의 연속 소수 `p_{n+1} ≡ p_{n+2} (mod q)` 에 대해 `q ∣ B n ↔ q ∣ 10^{d(p_{n+2})} + 1`
    (`dvd_pow_add_one_of_dvd_B`). 소수 `q` 는 `10^d + 1` 과 `10^{d+1} + 1` 을 동시에 나눌 수 없으므로
    (`not_dvd_pow_add_one_both`), 같은 류의 세 쌍이 `d` 자리와 `d+1` 자리 안에 각각 나타난다는 가정
    `DigitTriples q` (구간 `[x, 2x]` 판 Shiu 정리에서 따름) 아래서 Q1(S = {q, r}) 이 성립한다
    (`avoid_two_of_digit_triples`).
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

/-! ### |S| = 2 : 한 소수의 블록 조건만으로 충분 -/

/-- 두 소수 `q, r` 가 `N` 이후의 모든 항을 덮는다면, `q, r ≤ n` 인 모든 `n > N` 에서 `q ∣ B n ∨ q ∣ B (n+1)`.
번갈아 나누므로 `q` 는 `n` 또는 `n+1` 에서 두 칸 간격으로 나눈다. -/
theorem block_dvd_or_succ_of_cover {q r : ℕ} (hq : q.Prime) (hr : r.Prime) {N : ℕ}
    (hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n) {n : ℕ} (hn : N < n) (hnq : q ≤ n) (hnr : r ≤ n) :
    q ∣ B n ∨ q ∣ B (n + 1) := by
  have h1 := lt_nth_prime n
  have h2 := lt_nth_prime (n + 1)
  have h3 := lt_nth_prime (n + 2)
  have hq1 : q ≠ Nat.nth Nat.Prime n := by omega
  have hq2 : q ≠ Nat.nth Nat.Prime (n + 1) := by omega
  have hr1 : r ≠ Nat.nth Nat.Prime n := by omega
  have hr2 : r ≠ Nat.nth Nat.Prime (n + 1) := by omega
  have hr3 : r ≠ Nat.nth Nat.Prime (n + 2) := by omega
  rcases hcover n hn with hqn | hrn
  · -- q ∣ W n, r ∣ W (n+1), q ∣ W (n+2)
    have hnq1 : ¬ q ∣ W (n + 1) := not_dvd_succ_of_dvd hq hqn hq1
    have hrn1 : r ∣ W (n + 1) := (hcover (n + 1) (by omega)).resolve_left hnq1
    have hnr2 : ¬ r ∣ W (n + 2) := not_dvd_succ_of_dvd hr hrn1 hr2
    have hqn2 : q ∣ W (n + 2) := (hcover (n + 2) (by omega)).resolve_right hnr2
    exact Or.inl ((dvd_add_two_iff hqn).mp hqn2)
  · -- r ∣ W n, q ∣ W (n+1), r ∣ W (n+2), q ∣ W (n+3)
    have hnr1 : ¬ r ∣ W (n + 1) := not_dvd_succ_of_dvd hr hrn hr1
    have hqn1 : q ∣ W (n + 1) := (hcover (n + 1) (by omega)).resolve_right hnr1
    have hnq2 : ¬ q ∣ W (n + 2) := not_dvd_succ_of_dvd hq hqn1 hq2
    have hrn2 : r ∣ W (n + 2) := (hcover (n + 2) (by omega)).resolve_left hnq2
    have hnr3 : ¬ r ∣ W (n + 3) := not_dvd_succ_of_dvd hr hrn2 hr3
    have hqn3 : q ∣ W (n + 3) := (hcover (n + 3) (by omega)).resolve_right hnr3
    exact Or.inr ((dvd_add_two_iff hqn1).mp hqn3)

/-- Q1, `|S| = 2` 의 조건부 형태 (한 소수의 조건만 사용): `q ∤ B n ∧ q ∤ B (n+1)` 인 `n` 이 무한히 많으면
임의의 소수 `r` 에 대해 `q ∤ W n ∧ r ∤ W n` 인 `n` 도 무한히 많다. -/
theorem avoid_two_of_block_succ {q r : ℕ} (hq : q.Prime) (hr : r.Prime)
    (hB : ∀ M, ∃ n, M < n ∧ ¬ q ∣ B n ∧ ¬ q ∣ B (n + 1)) (N : ℕ) :
    ∃ n, N < n ∧ ¬ q ∣ W n ∧ ¬ r ∣ W n := by
  by_contra hcon
  push Not at hcon
  have hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n := fun n hn => by
    by_cases h : q ∣ W n
    · exact Or.inl h
    · exact Or.inr (hcon n hn h)
  obtain ⟨n, hn, hn1, hn2⟩ := hB (max N (max q r))
  have := block_dvd_or_succ_of_cover hq hr hcover (by omega : N < n) (by omega : q ≤ n) (by omega : r ≤ n)
  tauto

/-- `q ≤ n` 이면 소수 `q` 는 `p_{n+1}` 을 나누지 않는다. -/
lemma not_dvd_nth_prime_of_le {q n : ℕ} (hq : q.Prime) (hqn : q ≤ n) : ¬ q ∣ Nat.nth Nat.Prime n := by
  intro h
  have := (Nat.prime_dvd_prime_iff_eq hq (nth_prime_prime n)).mp h
  have := lt_nth_prime n
  omega

/-- `p_{m+1} ≡ p_{m+2} ≡ p_{m+3} (mod q)`: 같은 류의 연속 소수 세 쌍. -/
def SameClassTriple (q m : ℕ) : Prop :=
  Nat.nth Nat.Prime m ≡ Nat.nth Nat.Prime (m + 1) [MOD q] ∧
  Nat.nth Nat.Prime (m + 1) ≡ Nat.nth Nat.Prime (m + 2) [MOD q]

/-! ### S = {3, r} : Shiu 형 가정 H3 로 환원 -/

/-- `3 ∤ 10^d + 1`. -/
lemma not_three_dvd_pow_add_one (d : ℕ) : ¬ 3 ∣ 10 ^ d + 1 := by
  have h10 : (10 : ℕ) ^ d ≡ 1 [MOD 3] := by
    simpa using (show (10 : ℕ) ≡ 1 [MOD 3] by decide).pow d
  unfold Nat.ModEq at h10
  omega

/-- 연속 소수 `p_{n+1}, p_{n+2}` 가 mod 3 에서 같은 류이면 (`n ≥ 3`) `3 ∤ B n`. -/
theorem not_three_dvd_B_of_modEq {n : ℕ} (hn : 3 ≤ n)
    (h : Nat.nth Nat.Prime n ≡ Nat.nth Nat.Prime (n + 1) [MOD 3]) : ¬ 3 ∣ B n := by
  rw [three_dvd_B_iff]
  have h3 := not_dvd_nth_prime_of_le Nat.prime_three hn
  unfold Nat.ModEq at h
  omega

/-- 가정 H3: mod 3 에서 같은 류인 연속 소수 세 쌍이 무한히 많다. 소수만의 명제이며 `W` 와 무관하다.
Shiu (2000) 의 정리 (임의 길이의 같은 류 연속 소수 문자열) 에서 따른다. 이 프로젝트에서는 증명하지 않는다. -/
def SameClassTriples3 : Prop := ∀ M : ℕ, ∃ m : ℕ, M < m ∧ SameClassTriple 3 m

/-- Q1, `S = {3, r}`: H3 아래서 임의의 소수 `r` 에 대해 `3 ∤ W n ∧ r ∤ W n` 인 `n` 이 무한히 많다. -/
theorem avoid_three_of_triples {r : ℕ} (hr : r.Prime) (h3 : SameClassTriples3) (N : ℕ) :
    ∃ n, N < n ∧ ¬ 3 ∣ W n ∧ ¬ r ∣ W n := by
  refine avoid_two_of_block_succ Nat.prime_three hr ?_ N
  intro M
  obtain ⟨m, hm, h1, h2⟩ := h3 (max M 3)
  exact ⟨m, by omega, not_three_dvd_B_of_modEq (by omega) h1,
    not_three_dvd_B_of_modEq (by omega) h2⟩

/-! ### 일반 쌍 {q, r} : 두 자릿수 구간의 Shiu 형 가정으로 환원 -/

/-- 연속 소수가 mod q 에서 같은 류이고 `q ∤ p_{n+1}` 일 때, `q ∣ B n` 이면 `q ∣ 10^{d} + 1`
(`d = d(p_{n+2})`). `B n ≡ p_{n+1} · (10^d + 1)` 이기 때문이다. -/
theorem dvd_pow_add_one_of_dvd_B {q n d : ℕ} (hq : q.Prime)
    (h : Nat.nth Nat.Prime n ≡ Nat.nth Nat.Prime (n + 1) [MOD q])
    (hp : ¬ q ∣ Nat.nth Nat.Prime n) (hB : q ∣ B n)
    (hd : digitsLen (Nat.nth Nat.Prime (n + 1)) = d) : q ∣ 10 ^ d + 1 := by
  subst hd
  have hB' : B n ≡ Nat.nth Nat.Prime n * (10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) + 1) [MOD q] := by
    unfold B
    calc 10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) * Nat.nth Nat.Prime n + Nat.nth Nat.Prime (n + 1)
        ≡ 10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) * Nat.nth Nat.Prime n + Nat.nth Nat.Prime n [MOD q] :=
          Nat.ModEq.add_left _ h.symm
      _ = Nat.nth Nat.Prime n * (10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) + 1) := by ring
  have hdvd : q ∣ Nat.nth Nat.Prime n * (10 ^ digitsLen (Nat.nth Nat.Prime (n + 1)) + 1) :=
    Nat.modEq_zero_iff_dvd.mp (hB'.symm.trans (Nat.modEq_zero_iff_dvd.mpr hB))
  rcases (Nat.Prime.dvd_mul hq).mp hdvd with h' | h'
  · exact absurd h' hp
  · exact h'

/-- 소수 `q` 는 `10^d + 1` 과 `10^{d+1} + 1` 을 동시에 나누지 못한다:
둘로부터 `q ∣ 9` 이므로 `q = 3` 인데 `3 ∤ 10^d + 1`. -/
theorem not_dvd_pow_add_one_both {q d : ℕ} (hq : q.Prime)
    (h1 : q ∣ 10 ^ d + 1) (h2 : q ∣ 10 ^ (d + 1) + 1) : False := by
  rw [pow_succ] at h2
  have h9 : q ∣ 9 := by
    have := Nat.dvd_sub (dvd_mul_of_dvd_right h1 10) h2
    have e : 10 * (10 ^ d + 1) - (10 ^ d * 10 + 1) = 9 := by omega
    rwa [e] at this
  have h9' : q ∣ 3 ^ 2 := by simpa using h9
  have hq3 : q = 3 := (Nat.prime_dvd_prime_iff_eq hq Nat.prime_three).mp (hq.dvd_of_dvd_pow h9')
  subst hq3
  exact not_three_dvd_pow_add_one d h1

/-- 덮개 아래서, `q, r ≤ m`, `m > N` 이고 mod q 같은 류의 세 쌍이 `m` 에서 시작하며
`p_{m+2}, p_{m+3}` 가 모두 `d` 자리이면 `q ∣ 10^d + 1`. -/
theorem dvd_pow_add_one_of_cover {q r : ℕ} (hq : q.Prime) (hr : r.Prime) {N : ℕ}
    (hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n) {m d : ℕ} (hm : N < m) (hmq : q ≤ m) (hmr : r ≤ m)
    (ht : SameClassTriple q m)
    (hd1 : digitsLen (Nat.nth Nat.Prime (m + 1)) = d) (hd2 : digitsLen (Nat.nth Nat.Prime (m + 2)) = d) :
    q ∣ 10 ^ d + 1 := by
  rcases block_dvd_or_succ_of_cover hq hr hcover hm hmq hmr with hB | hB
  · exact dvd_pow_add_one_of_dvd_B hq ht.1 (not_dvd_nth_prime_of_le hq hmq) hB hd1
  · exact dvd_pow_add_one_of_dvd_B hq ht.2 (not_dvd_nth_prime_of_le hq (by omega)) hB hd2

/-- 가정 Hd(q): 임의로 큰 `M` 에 대해 어떤 자릿수 `d` 가 있어, `M` 이후에 mod q 같은 류의 연속 소수 세 쌍이
`p_{m+2}, p_{m+3}` 가 `d` 자리인 것과 `d+1` 자리인 것 각각 하나씩 존재한다.
"충분히 큰 모든 `x` 에 대해 `[x, 2x]` 에 같은 류의 연속 소수 세 개가 있다" 는 구간 판 Shiu 정리에서 따른다
(`x = 10^{d-1}, 10^d`). 이 프로젝트에서는 증명하지 않는다. -/
def DigitTriples (q : ℕ) : Prop :=
  ∀ M : ℕ, ∃ d : ℕ,
    (∃ m, M < m ∧ SameClassTriple q m ∧
      digitsLen (Nat.nth Nat.Prime (m + 1)) = d ∧ digitsLen (Nat.nth Nat.Prime (m + 2)) = d) ∧
    (∃ m, M < m ∧ SameClassTriple q m ∧
      digitsLen (Nat.nth Nat.Prime (m + 1)) = d + 1 ∧ digitsLen (Nat.nth Nat.Prime (m + 2)) = d + 1)

/-- Q1, `S = {q, r}`: Hd(q) 아래서 임의의 소수 `r` 에 대해 `q ∤ W n ∧ r ∤ W n` 인 `n` 이 무한히 많다. -/
theorem avoid_two_of_digit_triples {q r : ℕ} (hq : q.Prime) (hr : r.Prime) (hT : DigitTriples q)
    (N : ℕ) : ∃ n, N < n ∧ ¬ q ∣ W n ∧ ¬ r ∣ W n := by
  by_contra hcon
  push Not at hcon
  have hcover : ∀ n, N < n → q ∣ W n ∨ r ∣ W n := fun n hn => by
    by_cases h : q ∣ W n
    · exact Or.inl h
    · exact Or.inr (hcon n hn h)
  obtain ⟨d, ⟨m, hm, ht, hd1, hd2⟩, ⟨m', hm', ht', hd1', hd2'⟩⟩ := hT (max N (max q r))
  have h1 := dvd_pow_add_one_of_cover hq hr hcover (by omega : N < m) (by omega : q ≤ m)
    (by omega : r ≤ m) ht hd1 hd2
  have h2 := dvd_pow_add_one_of_cover hq hr hcover (by omega : N < m') (by omega : q ≤ m')
    (by omega : r ≤ m') ht' hd1' hd2'
  exact not_dvd_pow_add_one_both hq h1 h2

end SW
