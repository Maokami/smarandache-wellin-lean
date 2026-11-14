import SmarandacheWellin.Avoid

/-!
# 구간 판 Shiu 가정과 자릿수 (장부 H3, Hd(q), IT(q))

문헌 (Maynard 2016, Theorem 3.3 의 증명 중 식 (6.24); `docs/references.md`) 이 주는 형태는
"충분히 큰 모든 `x` 에 대해 `[x, 3x]` 안에 mod q 같은 류의 연속 소수 세 개가 있다" 이다 (`IntervalTriples q`).
이 파일은 그 가정에서 `Avoid.lean` 의 두 가정 `DigitTriples q` 와 `SameClassTriples3` 을 유도한다.
핵심은 `[10^e, 3·10^e] ⊂ [10^e, 10^{e+1})` 이라 그 안의 수는 모두 `e + 1` 자리라는 것뿐이다.
-/

namespace SW

/-- `10^e ≤ n < 10^{e+1}` 이면 `n` 은 `e + 1` 자리. -/
theorem digitsLen_eq {n e : ℕ} (h1 : 10 ^ e ≤ n) (h2 : n < 10 ^ (e + 1)) : digitsLen n = e + 1 := by
  have a := (Nat.digits_length_le_iff (b := 10) (k := e + 1) (by norm_num) n).mpr h2
  have b := (Nat.lt_digits_length_iff (b := 10) (k := e) (by norm_num) n).mpr h1
  unfold digitsLen
  omega

/-- 가정 IT(q) (구간 판 Shiu): 어떤 `x₀` 가 있어, `x ≥ x₀` 이면 `[x, 3x]` 안에 mod q 같은 류의 연속 소수 세 개
`p_{m+1} ≡ p_{m+2} ≡ p_{m+3}` 이 있다. Maynard (2016) Theorem 3.3 의 증명 중 식 (6.24) 에서 따른다
(`docs/references.md`, `docs/lemma-ledger.md` 의 IT(q)). 이 프로젝트에서는 증명하지 않는다. -/
def IntervalTriples (q : ℕ) : Prop :=
  ∃ x₀ : ℕ, ∀ x, x₀ ≤ x →
    ∃ m, x ≤ Nat.nth Nat.Prime m ∧ Nat.nth Nat.Prime (m + 2) ≤ 3 * x ∧ SameClassTriple q m

/-- `p_{M+1} < p_{m+1}` 이면 `M < m`. -/
lemma lt_of_nth_prime_lt {M m : ℕ} (h : Nat.nth Nat.Prime M < Nat.nth Nat.Prime m) : M < m := by
  by_contra hle
  push Not at hle
  have : Nat.nth Nat.Prime m ≤ Nat.nth Nat.Prime M :=
    (Nat.nth_strictMono Nat.infinite_setOfPred_prime).monotone hle
  omega

/-- IT(3) ⇒ H3. -/
theorem sameClassTriples3_of_intervalTriples (h : IntervalTriples 3) : SameClassTriples3 := by
  obtain ⟨x₀, hx⟩ := h
  intro M
  obtain ⟨m, hm1, _, ht⟩ := hx (x₀ + Nat.nth Nat.Prime M + 1) (by omega)
  exact ⟨m, lt_of_nth_prime_lt (by omega), ht⟩

/-- `[10^e, 3·10^e]` 안에서 시작하는 세 쌍은 `p_{m+2}, p_{m+3}` 가 모두 `e + 1` 자리. -/
lemma digit_triple_of_interval {q m e : ℕ} (hm1 : 10 ^ e ≤ Nat.nth Nat.Prime m)
    (hm2 : Nat.nth Nat.Prime (m + 2) ≤ 3 * 10 ^ e) (ht : SameClassTriple q m) :
    SameClassTriple q m ∧
      digitsLen (Nat.nth Nat.Prime (m + 1)) = e + 1 ∧ digitsLen (Nat.nth Nat.Prime (m + 2)) = e + 1 := by
  have hlt1 : Nat.nth Nat.Prime m < Nat.nth Nat.Prime (m + 1) :=
    (Nat.nth_strictMono Nat.infinite_setOfPred_prime) (by omega)
  have hlt2 : Nat.nth Nat.Prime (m + 1) < Nat.nth Nat.Prime (m + 2) :=
    (Nat.nth_strictMono Nat.infinite_setOfPred_prime) (by omega)
  have hpos : 0 < 10 ^ e := by positivity
  refine ⟨ht, digitsLen_eq (by omega) ?_, digitsLen_eq (by omega) ?_⟩
  · rw [pow_succ]; omega
  · rw [pow_succ]; omega

/-- IT(q) ⇒ Hd(q). `e` 를 `10^e ≥ x₀`, `10^e > p_{M+1}` 이 되게 잡고 `x = 10^e, 10^{e+1}` 에 적용한다. -/
theorem digitTriples_of_intervalTriples {q : ℕ} (h : IntervalTriples q) : DigitTriples q := by
  obtain ⟨x₀, hx⟩ := h
  intro M
  have he : x₀ + Nat.nth Nat.Prime M < 10 ^ (x₀ + Nat.nth Nat.Prime M) :=
    Nat.lt_pow_self (by norm_num)
  set e := x₀ + Nat.nth Nat.Prime M with he_def
  refine ⟨e + 1, ?_, ?_⟩
  · obtain ⟨m, hm1, hm2, ht⟩ := hx (10 ^ e) (by omega)
    exact ⟨m, lt_of_nth_prime_lt (by omega), digit_triple_of_interval hm1 hm2 ht⟩
  · obtain ⟨m, hm1, hm2, ht⟩ := hx (10 ^ (e + 1)) (by rw [pow_succ]; omega)
    exact ⟨m, lt_of_nth_prime_lt (by rw [pow_succ] at hm1; omega), digit_triple_of_interval hm1 hm2 ht⟩

/-- Q1, `S = {q, r}`: IT(q) 아래서 임의의 소수 `r` 에 대해 `q ∤ W n ∧ r ∤ W n` 인 `n` 이 무한히 많다. -/
theorem avoid_two_of_interval_triples {q r : ℕ} (hq : q.Prime) (hr : r.Prime) (h : IntervalTriples q)
    (N : ℕ) : ∃ n, N < n ∧ ¬ q ∣ W n ∧ ¬ r ∣ W n :=
  avoid_two_of_digit_triples hq hr (digitTriples_of_intervalTriples h) N

/-- Q1, `S = {3, r}` 를 IT(3) 에서 (H3 를 거쳐) 얻는 판. -/
theorem avoid_three_of_interval_triples {r : ℕ} (hr : r.Prime) (h : IntervalTriples 3) (N : ℕ) :
    ∃ n, N < n ∧ ¬ 3 ∣ W n ∧ ¬ r ∣ W n :=
  avoid_three_of_triples hr (sameClassTriples3_of_intervalTriples h) N

/-- 가정: 모든 소수 `q ≥ 3` 에 대해 IT(q). Maynard (2016) Theorem 3.3 의 증명 중 식 (6.24) 에서 따른다
(Lean 밖, `docs/references.md`). 이 프로젝트에서는 증명하지 않는다. -/
def IntervalTriplesAll : Prop := ∀ q : ℕ, q.Prime → 3 ≤ q → IntervalTriples q

/-- Q1, `|S| = 2`: 모든 소수 `q ≥ 3` 에 대해 IT(q) 이면, 임의의 소수 `q, r` 에 대해
`q ∤ W n ∧ r ∤ W n` 인 `n` 이 무한히 많다. `q = 2` 는 `n ≥ 4` 에서 `W n` 이 홀수라서 `|S| = 1` 로 줄어든다. -/
theorem avoid_two_of_intervalTriplesAll (h : IntervalTriplesAll) {q r : ℕ}
    (hq : q.Prime) (hr : r.Prime) (N : ℕ) :
    ∃ n, N < n ∧ ¬ q ∣ W n ∧ ¬ r ∣ W n := by
  by_cases h3 : 3 ≤ q
  · exact avoid_two_of_interval_triples hq hr (h q hq h3) N
  · have hq2 : q = 2 := by
      have := hq.two_le
      omega
    subst hq2
    obtain ⟨n, hn, hrn⟩ := exists_not_dvd hr (max N 3)
    refine ⟨n, by omega, ?_, hrn⟩
    obtain ⟨k, rfl⟩ : ∃ k, n = k + 1 := ⟨n - 1, by omega⟩
    have hcop : Nat.Coprime (W (k + 1)) 10 := coprime_ten_of_three_le (by omega)
    intro h2
    have : 2 ∣ Nat.gcd (W (k + 1)) 10 := Nat.dvd_gcd h2 (by norm_num)
    rw [hcop] at this
    omega

/-! ### 류 1 의 구간 소수 런에서 일반 Q1

가정 `IntervalOneRuns m`: 충분히 큰 모든 `x` 에 대해 `[x, 3x]` 안에 연속 소수 `m` 개가 모두 `≡ 1 (mod m)`.
`10^d ≡ 1 (mod m)` 인 `d` 자리 소수가 `1 (mod m)` 이면, 그 소수를 붙이는 단계는 mod `m` 에서 `+1` 이다.
`m` 단계 동안 `W` 의 나머지는 모든 류를 지나므로 그중 `1` 인 항이 있고, 그 항은 `m` 의 어느 소인수로도 나뉘지 않는다.
-/

/-- 가정 (류 1 의 구간 런): 어떤 `x₀` 가 있어 `x ≥ x₀` 이면 `x ≤ p_{n+1}, …, p_{n+m} ≤ 3x` 이고
모두 `≡ 1 (mod m)` 인 `n` 이 있다. Maynard (2016) 에서 따르는 것으로 보는 외부 가정이며
(`docs/literature/2026-11-11-maynard-general-q1.md`), 이 프로젝트에서는 증명하지 않는다. -/
def IntervalOneRuns (m : ℕ) : Prop :=
  ∃ x₀ : ℕ, ∀ x : ℕ, x₀ ≤ x →
    ∃ n : ℕ, ∀ j : ℕ, j < m →
      x ≤ Nat.nth Nat.Prime (n + j) ∧
      Nat.nth Nat.Prime (n + j) ≤ 3 * x ∧
      Nat.nth Nat.Prime (n + j) ≡ 1 [MOD m]

/-- 가정: `10` 과 서로소인 모든 `m ≥ 2` 에 대해 `IntervalOneRuns m`. 증명하지 않는다. -/
def IntervalOneRunsAll : Prop :=
  ∀ m : ℕ, 2 ≤ m → m.Coprime 10 → IntervalOneRuns m

/-- 런 위의 합동 전이: `10^d ≡ 1 (mod m)` 이고 `p_{n+1}, …, p_{n+k}` 가 모두 `d` 자리이며
`≡ 1 (mod m)` 이면 `W (n + k) ≡ W n + k (mod m)`. -/
theorem W_add_modEq_of_run {m d n k : ℕ} (h10 : 10 ^ d ≡ 1 [MOD m])
    (hrun : ∀ i, i < k →
      digitsLen (Nat.nth Nat.Prime (n + i)) = d ∧ Nat.nth Nat.Prime (n + i) ≡ 1 [MOD m]) :
    W (n + k) ≡ W n + k [MOD m] := by
  induction k with
  | zero => simp [Nat.ModEq]
  | succ k ih =>
    have ih' := ih (fun i hi => hrun i (by omega))
    obtain ⟨hd, hp⟩ := hrun k (by omega)
    rw [← add_assoc, W_succ, hd]
    have := (h10.mul ih').add hp
    simpa [add_assoc] using this

/-- `m ≥ 2` 이면 임의의 `a` 에 대해 `(a + j) mod m = 1` 인 `j < m` 이 있다. -/
theorem exists_add_mod_eq_one (a : ℕ) {m : ℕ} (hm : 2 ≤ m) : ∃ j, j < m ∧ (a + j) % m = 1 := by
  have hr := Nat.mod_lt a (by omega : 0 < m)
  have ha := Nat.div_add_mod a m
  by_cases h1 : a % m ≤ 1
  · refine ⟨1 - a % m, by omega, ?_⟩
    have : a + (1 - a % m) = 1 + m * (a / m) := by omega
    rw [this, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt (by omega)]
  · refine ⟨m + 1 - a % m, by omega, ?_⟩
    have : a + (m + 1 - a % m) = 1 + m * (a / m + 1) := by
      rw [Nat.mul_add, mul_one]; omega
    rw [this, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt (by omega)]

/-- 소수 `q ∣ m` 이고 `a mod m = 1` 이면 `q ∤ a`. -/
theorem not_dvd_of_mod_eq_one {q m a : ℕ} (hq : q.Prime) (hqm : q ∣ m) (ha : a % m = 1) :
    ¬ q ∣ a := by
  intro hqa
  have : q ∣ a % m := (Nat.dvd_mod_iff hqm).mpr hqa
  rw [ha] at this
  exact hq.one_lt.ne' (Nat.dvd_one.mp this)

/-- `n ≥ 4` 이면 `2 ∤ W n` 이고 `5 ∤ W n`. -/
theorem not_dvd_W_of_two_or_five {q n : ℕ} (hq : q = 2 ∨ q = 5) (hn : 4 ≤ n) : ¬ q ∣ W n := by
  obtain ⟨k, rfl⟩ : ∃ k, n = k + 1 := ⟨n - 1, by omega⟩
  have hcop : Nat.Coprime (W (k + 1)) 10 := coprime_ten_of_three_le (by omega)
  intro h
  have h10 : q ∣ 10 := by rcases hq with rfl | rfl <;> norm_num
  have : q ∣ Nat.gcd (W (k + 1)) 10 := Nat.dvd_gcd h h10
  rw [hcop] at this
  rcases hq with rfl | rfl <;> omega

/-- Q1, 일반 유한 집합 (외부 가정 조건부): `IntervalOneRunsAll` 이면 임의의 유한 소수 집합 `S` 와 `N` 에 대해
`N < n` 이고 `S` 의 어느 원소도 `W n` 을 나누지 않는 `n` 이 있다.
`m = 3 · ∏_{q ∈ S \ {2,5}} q` 로 잡는다 (`3` 을 곱해 `m ≥ 3` 을 보장한다). -/
theorem avoid_finset_of_intervalOneRunsAll
    (h : IntervalOneRunsAll) (S : Finset ℕ)
    (hS : ∀ q ∈ S, q.Prime) (N : ℕ) :
    ∃ n : ℕ, N < n ∧ ∀ q ∈ S, ¬ q ∣ W n := by
  classical
  set T := S.filter (fun q => q ≠ 2 ∧ q ≠ 5) with hT
  set m := 3 * ∏ q ∈ T, q with hm
  have hTcop : Nat.Coprime (∏ q ∈ T, q) 10 := by
    apply Nat.Coprime.prod_left
    intro q hq
    rw [hT, Finset.mem_filter] at hq
    obtain ⟨hqS, h2, h5⟩ := hq
    have hp := hS q hqS
    rw [show (10 : ℕ) = 2 * 5 by norm_num, Nat.coprime_mul_iff_right]
    exact ⟨(Nat.coprime_primes hp Nat.prime_two).mpr h2,
      (Nat.coprime_primes hp (by norm_num)).mpr h5⟩
  have hmcop : Nat.Coprime m 10 := Nat.coprime_mul_iff_left.mpr ⟨by norm_num, hTcop⟩
  have hprod_pos : 0 < ∏ q ∈ T, q := by
    apply Finset.prod_pos
    intro q hq
    exact (hS q (Finset.mem_filter.mp hq).1).pos
  have hm3 : 3 ≤ m := by rw [hm]; omega
  obtain ⟨x₀, hx⟩ := h m (by omega) hmcop
  set L := Nat.totient m with hL
  have hLpos : 0 < L := Nat.totient_pos.mpr (by omega)
  have hpow : 10 ^ L ≡ 1 [MOD m] := Nat.ModEq.pow_totient hmcop.symm
  set K := x₀ + Nat.nth Nat.Prime (max N 3) + 1 with hK
  set e := L * (K + 1) - 1 with he
  have hd : e + 1 = L * (K + 1) := by
    have : 1 ≤ L * (K + 1) := Nat.one_le_iff_ne_zero.mpr (by positivity)
    omega
  have hKe : K ≤ e := by
    have : K + 1 ≤ L * (K + 1) := Nat.le_mul_of_pos_left _ hLpos
    omega
  have hKlt : K < 10 ^ e :=
    lt_of_lt_of_le (Nat.lt_pow_self (by norm_num)) (Nat.pow_le_pow_right (by norm_num) hKe)
  have h10d : 10 ^ (e + 1) ≡ 1 [MOD m] := by
    rw [hd, pow_mul]
    simpa using hpow.pow (K + 1)
  obtain ⟨n, hn⟩ := hx (10 ^ e) (by omega)
  have hrun : ∀ i, i < m →
      digitsLen (Nat.nth Nat.Prime (n + i)) = e + 1 ∧ Nat.nth Nat.Prime (n + i) ≡ 1 [MOD m] := by
    intro i hi
    obtain ⟨h1, h2, h3⟩ := hn i hi
    refine ⟨digitsLen_eq h1 ?_, h3⟩
    have : 0 < 10 ^ e := by positivity
    rw [pow_succ]; omega
  have hnlt : max N 3 < n := by
    obtain ⟨h1, -, -⟩ := hn 0 (by omega)
    exact lt_of_nth_prime_lt (by simp only [add_zero] at h1; omega)
  obtain ⟨j, hjm, hj⟩ := exists_add_mod_eq_one (W n) (by omega : 2 ≤ m)
  have hW : W (n + j) % m = 1 := by
    have := W_add_modEq_of_run (k := j) h10d (fun i hi => hrun i (by omega))
    rw [Nat.ModEq] at this
    rw [this, hj]
  refine ⟨n + j, by omega, ?_⟩
  intro q hqS
  have hq := hS q hqS
  by_cases h25 : q = 2 ∨ q = 5
  · exact not_dvd_W_of_two_or_five h25 (by omega)
  · have hqT : q ∈ T := by
      rw [hT, Finset.mem_filter]
      exact ⟨hqS, by tauto, by tauto⟩
    have hqm : q ∣ m := Dvd.dvd.mul_left (Finset.dvd_prod_of_mem _ hqT) 3
    exact not_dvd_of_mod_eq_one hq hqm hW

/-- 고정된 작은 소인수 회피 (외부 가정 조건부): `IntervalOneRunsAll` 이면 임의의 `B`, `N` 에 대해
`N < n` 이고 `B` 이하의 어느 소수도 `W n` 을 나누지 않는 `n` 이 있다.
`S = {q ≤ B : q 소수}` 에 `avoid_finset_of_intervalOneRunsAll` 을 적용한다. -/
theorem avoid_le_of_intervalOneRunsAll
    (h : IntervalOneRunsAll) (B N : ℕ) :
    ∃ n : ℕ, N < n ∧ ∀ q : ℕ, q.Prime → q ≤ B → ¬ q ∣ W n := by
  classical
  obtain ⟨n, hNn, hn⟩ := avoid_finset_of_intervalOneRunsAll h
    ((Finset.range (B + 1)).filter Nat.Prime)
    (fun q hq => (Finset.mem_filter.mp hq).2) N
  refine ⟨n, hNn, fun q hq hqB => hn q ?_⟩
  exact Finset.mem_filter.mpr ⟨Finset.mem_range.mpr (Nat.lt_succ_of_le hqB), hq⟩

end SW
