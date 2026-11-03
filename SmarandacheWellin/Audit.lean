import SmarandacheWellin.Congruence

/-!
# 공리 감사

`lake build` 시 각 정리의 공리 의존성을 출력한다.
허용: `propext`, `Classical.choice`, `Quot.sound`. `sorryAx` 나 새로 선언한 공리가 보이면 안 된다.
-/

#print axioms SW.W_four_prime
#print axioms SW.W_strictMono
#print axioms SW.W_succ_mod
#print axioms SW.W_succ_modEq_ten
#print axioms SW.swInfinitude_iff_image
#print axioms SW.W_modEq_sum_of_ten_modEq_one
#print axioms SW.not_dvd_succ_of_dvd
#print axioms SW.coprime_ten_of_three_le
