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

end SW
