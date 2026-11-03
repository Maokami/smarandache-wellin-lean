import SmarandacheWellin.Defs

/-!
# 기본 성질

* 초기값 `W 1 = 2`, `W 2 = 23`, `W 3 = 235`, `W 4 = 2357` 와 그 소수성.
* 엄격 증가, 단사.
* 나머지 점화식: 거대한 `W n` 을 만들지 않고도 `W n mod m` 을 추적할 수 있다.
* `W (n+1) ≡ p_{n+1} (mod 10)`: 끝자리는 마지막에 붙인 소수의 끝자리다.
* 목표 명제의 세 가지 동치 서술.
-/

namespace SW

lemma nth_prime_prime (n : ℕ) : (Nat.nth Nat.Prime n).Prime :=
  Nat.nth_mem_of_infinite Nat.infinite_setOfPred_prime n

lemma digitsLen_pos {m : ℕ} (hm : m ≠ 0) : 0 < digitsLen m :=
  List.length_pos_of_ne_nil (Nat.digits_ne_nil_iff_ne_zero.mpr hm)

theorem W_zero : W 0 = 0 := rfl

theorem W_succ (n : ℕ) :
    W (n + 1) = 10 ^ digitsLen (Nat.nth Nat.Prime n) * W n + Nat.nth Nat.Prime n := rfl

/-! ### 초기값 -/

theorem W_one : W 1 = 2 := by
  simp [W, digitsLen, Nat.nth_prime_zero_eq_two]

theorem W_two : W 2 = 23 := by
  simp [W, digitsLen, Nat.nth_prime_zero_eq_two, Nat.nth_prime_one_eq_three]

theorem W_three : W 3 = 235 := by
  simp [W, digitsLen, Nat.nth_prime_zero_eq_two, Nat.nth_prime_one_eq_three,
    Nat.nth_prime_two_eq_five]

theorem W_four : W 4 = 2357 := by
  simp [W, digitsLen, Nat.nth_prime_zero_eq_two, Nat.nth_prime_one_eq_three,
    Nat.nth_prime_two_eq_five, Nat.nth_prime_three_eq_seven]

theorem W_one_prime : (W 1).Prime := by rw [W_one]; norm_num
theorem W_two_prime : (W 2).Prime := by rw [W_two]; norm_num
theorem W_three_not_prime : ¬ (W 3).Prime := by rw [W_three]; norm_num
theorem W_four_prime : (W 4).Prime := by rw [W_four]; norm_num

/-! ### 증가 -/

theorem W_lt_succ (n : ℕ) : W n < W (n + 1) := by
  rw [W]
  have hp : 0 < Nat.nth Nat.Prime n := (nth_prime_prime n).pos
  have h10 : 1 ≤ 10 ^ digitsLen (Nat.nth Nat.Prime n) := Nat.one_le_pow _ _ (by norm_num)
  nlinarith

theorem W_strictMono : StrictMono W := strictMono_nat_of_lt_succ W_lt_succ

theorem W_injective : Function.Injective W := W_strictMono.injective

theorem W_pos {n : ℕ} (hn : 1 ≤ n) : 0 < W n := by
  have := W_strictMono.monotone hn
  rw [W_one] at this
  omega

/-! ### 나머지 점화식 -/

/-- 임의의 모듈러스 `m` 에 대한 나머지 점화식. -/
theorem W_succ_mod (n m : ℕ) :
    W (n + 1) % m
      = (10 ^ digitsLen (Nat.nth Nat.Prime n) % m * (W n % m) + Nat.nth Nat.Prime n % m) % m := by
  rw [W, Nat.add_mod, Nat.mul_mod, Nat.mod_add_mod]

/-- `W (n+1)` 의 끝자리는 `p_{n+1}` 의 끝자리다. -/
theorem W_succ_modEq_ten (n : ℕ) : W (n + 1) ≡ Nat.nth Nat.Prime n [MOD 10] := by
  rw [W]
  have h10 : (10 : ℕ) ^ digitsLen (Nat.nth Nat.Prime n) ≡ 0 [MOD 10] :=
    Nat.modEq_zero_iff_dvd.mpr (dvd_pow_self 10 (digitsLen_pos (nth_prime_prime n).ne_zero).ne')
  simpa using (h10.mul_right (W n)).add_right (Nat.nth Nat.Prime n)

/-! ### 목표 명제의 동치 서술 -/

/-- "소수인 인덱스가 끝없이 나온다" ↔ "소수인 인덱스의 집합이 무한하다". -/
theorem swInfinitude_iff_infinite : SWInfinitude ↔ {n | (W n).Prime}.Infinite :=
  Filter.frequently_atTop'.symm.trans Nat.frequently_atTop_iff_infinite

/-- … ↔ "서로 다른 Smarandache–Wellin 소수가 무한히 많다". `W` 가 단사이므로 같다. -/
theorem swInfinitude_iff_image : SWInfinitude ↔ (W '' {n | (W n).Prime}).Infinite := by
  rw [swInfinitude_iff_infinite, Set.infinite_image_iff W_injective.injOn]

end SW
