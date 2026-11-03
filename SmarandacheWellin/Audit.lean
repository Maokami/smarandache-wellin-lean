import SmarandacheWellin.Congruence

/-!
# 공리 감사

`lake build` 시 각 정리의 공리 의존성을 출력한다.
허용: `propext`, `Classical.choice`, `Quot.sound`. `sorryAx` 나 새로 선언한 공리가 보이면 안 된다.
새 정리를 추가하면 여기에도 한 줄 추가한다.
-/

-- Basic
#print axioms SW.nth_prime_prime
#print axioms SW.digitsLen_pos
#print axioms SW.W_one
#print axioms SW.W_two
#print axioms SW.W_three
#print axioms SW.W_four
#print axioms SW.W_one_prime
#print axioms SW.W_two_prime
#print axioms SW.W_three_not_prime
#print axioms SW.W_four_prime
#print axioms SW.W_lt_succ
#print axioms SW.W_strictMono
#print axioms SW.W_injective
#print axioms SW.W_pos
#print axioms SW.W_succ_mod
#print axioms SW.W_succ_modEq_ten
#print axioms SW.swInfinitude_iff_infinite
#print axioms SW.swInfinitude_iff_image

-- Congruence
#print axioms SW.W_modEq_sum_of_ten_modEq_one
#print axioms SW.W_modEq_sum_three
#print axioms SW.W_modEq_sum_nine
#print axioms SW.not_dvd_succ_of_dvd
#print axioms SW.not_dvd_succ_of_dvd_of_lt
#print axioms SW.seven_le_nth_prime
#print axioms SW.nth_prime_coprime_ten
#print axioms SW.coprime_ten_of_three_le
