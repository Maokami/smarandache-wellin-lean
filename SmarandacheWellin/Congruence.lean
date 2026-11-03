import SmarandacheWellin.Basic

/-!
# 합동식 구조

* `10 ≡ 1 (mod m)` 이면 `W n ≡ Σ_{k<n} p_{k+1} (mod m)`. 특히 `m = 3, 9`.
* 소수 `q` 가 `W n` 을 나누고 `q ≠ p_{n+1}` 이면 `q ∤ W (n+1)`:
  고정된 소수 하나는 연속한 두 항을 모두 나눌 수 없다.
  **주의**: 서로 다른 소수들이 번갈아 나누는 가능성은 배제하지 못한다.
  예컨대 3 | W n, 7 | W (n+1), 3 | W (n+2), … 를 이 보조정리만으로는 막을 수 없다.
* `n ≥ 4` 이면 `gcd (W n) 10 = 1`: 네 번째 항부터 소인수 2, 5 는 자동으로 배제된다.
-/

namespace SW

/-- `10 ≡ 1 (mod m)` 이면 이어 붙이기는 mod `m` 에서 덧셈이 된다. -/
theorem W_modEq_sum_of_ten_modEq_one {m : ℕ} (hm : (10 : ℕ) ≡ 1 [MOD m]) (n : ℕ) :
    W n ≡ ∑ k ∈ Finset.range n, Nat.nth Nat.Prime k [MOD m] := by
  induction n with
  | zero => simp [W, Nat.ModEq]
  | succ n ih =>
    rw [W, Finset.sum_range_succ]
    have h10 : (10 : ℕ) ^ digitsLen (Nat.nth Nat.Prime n) ≡ 1 [MOD m] := by
      simpa using hm.pow (digitsLen (Nat.nth Nat.Prime n))
    simpa using (h10.mul ih).add_right (Nat.nth Nat.Prime n)

theorem W_modEq_sum_three (n : ℕ) :
    W n ≡ ∑ k ∈ Finset.range n, Nat.nth Nat.Prime k [MOD 3] :=
  W_modEq_sum_of_ten_modEq_one (by decide) n

theorem W_modEq_sum_nine (n : ℕ) :
    W n ≡ ∑ k ∈ Finset.range n, Nat.nth Nat.Prime k [MOD 9] :=
  W_modEq_sum_of_ten_modEq_one (by decide) n

/-- 핵심 보조정리: 소수 `q ∣ W n` 이고 `q ≠ p_{n+1}` 이면 `q ∤ W (n+1)`. -/
theorem not_dvd_succ_of_dvd {q n : ℕ} (hq : q.Prime) (hdvd : q ∣ W n)
    (hne : q ≠ Nat.nth Nat.Prime n) : ¬ q ∣ W (n + 1) := by
  intro h
  rw [W] at h
  have h1 : q ∣ 10 ^ digitsLen (Nat.nth Nat.Prime n) * W n := dvd_mul_of_dvd_right hdvd _
  have h2 : q ∣ Nat.nth Nat.Prime n := (Nat.dvd_add_right h1).mp h
  rcases (Nat.dvd_prime (nth_prime_prime n)).mp h2 with h | h
  · exact hq.one_lt.ne' h
  · exact hne h

/-- 같은 내용의 부등식 형태: `q < p_{n+1}` 이면 충분하다. -/
theorem not_dvd_succ_of_dvd_of_lt {q n : ℕ} (hq : q.Prime) (hdvd : q ∣ W n)
    (hlt : q < Nat.nth Nat.Prime n) : ¬ q ∣ W (n + 1) :=
  not_dvd_succ_of_dvd hq hdvd hlt.ne

/-- `n ≥ 3` 이면 `p_{n+1} ≥ 7`. -/
lemma seven_le_nth_prime {n : ℕ} (hn : 3 ≤ n) : 7 ≤ Nat.nth Nat.Prime n :=
  calc 7 = Nat.nth Nat.Prime 3 := Nat.nth_prime_three_eq_seven.symm
    _ ≤ Nat.nth Nat.Prime n := (Nat.nth_strictMono Nat.infinite_setOfPred_prime).monotone hn

/-- `n ≥ 3` 이면 `p_{n+1}` 은 10 과 서로소다. -/
lemma nth_prime_coprime_ten {n : ℕ} (hn : 3 ≤ n) : Nat.Coprime (Nat.nth Nat.Prime n) 10 := by
  have hp := nth_prime_prime n
  have h7 := seven_le_nth_prime hn
  rw [show (10 : ℕ) = 2 * 5 by norm_num, Nat.coprime_mul_iff_right]
  exact ⟨(Nat.coprime_primes hp Nat.prime_two).mpr (by omega),
    (Nat.coprime_primes hp (by norm_num)).mpr (by omega)⟩

/-- `n ≥ 3` 이면 `W (n+1)` 은 10 과 서로소다. 즉 네 번째 항부터 2, 5 는 자동으로 배제된다. -/
theorem coprime_ten_of_three_le {n : ℕ} (hn : 3 ≤ n) : Nat.Coprime (W (n + 1)) 10 := by
  have hmod : W (n + 1) % 10 = Nat.nth Nat.Prime n % 10 := W_succ_modEq_ten n
  have hcop := nth_prime_coprime_ten hn
  show Nat.gcd (W (n + 1)) 10 = 1
  rw [Nat.gcd_comm, Nat.gcd_rec, hmod, ← Nat.gcd_rec, Nat.gcd_comm]
  exact hcop

end SW
