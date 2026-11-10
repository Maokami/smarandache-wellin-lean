# H1 문헌 확인 보고서 — 같은 잉여류에 속하는 연속 소수 문자열 (Shiu / BFT / Maynard / Lemke Oliver–Soundararajan)

작성: lit-h1 (2026-11-05). 모든 인용은 arXiv 판 PDF를 `pdftotext`로 추출해 대조했고, 출판본은 Maynard(Compositio, Cambridge Core 오픈액세스 PDF)만 직접 확인했습니다. Shiu 2000 원문은 Wiley 유료 페이지(403)라 **직접 열람하지 못했고**, Cambridge Core 초록(수식은 placeholder로 가려짐)과 5편의 독립 2차 문헌으로 재구성했습니다. 표기 규약:

- **[원문 인용]** = 소스에서 글자 그대로 옮김(기호 깨짐만 복원: `ǫ→ε`, `≫`, `⩽→≤`).
- **[내 요약]** = 소스 내용을 제가 정리한 것.
- **[내 추론]** = 소스에 없는 논리 단계를 제가 보탠 것.
- **[미확인]** = 검증하지 못한 부분.

---

## 0. 결론 요약

| 가설 | 판정 | 근거 |
|---|---|---|
| **(H3)** mod 3으로 같은 잉여류인 연속 소수 3개짜리 런이 무한히 많다 | **성립 (출판된 정리에서 직접 따라옴)** | BFT 2015 Corollary 3 (D=3, m=3) 가 "infinitely many r" 형태로 그대로 줌. Shiu 2000 (임의 길이 k) 및 Maynard 2016 Thm 3.3 (m=2, 양의 비율)에서도 따라옴. |
| **(Hd(q))** 두 자릿수 길이 d, d+1 각각에 같은 잉여류 연속 소수 3개 런이 존재 | **성립하되, "[x,2x] for all large x" 형태를 정리문으로 verbatim 진술한 출판 논문은 없음.** Maynard 2016 Theorem 3.3의 **증명 안의 식 (6.24)** (arXiv v2에서는 (6.26))가 정확히 dyadic 형태이고, Theorem 3.1 자체도 정의 (2.1)에 의해 계수 범위가 `A(x) = {n ∈ A : x ≤ n < 2x}` 로 dyadic임. | 아래 (C)절 참조. BFT·Shiu의 정리문("infinitely many", "p_{n+k} < x인 문자열 존재")만으로는 Hd(q)가 **나오지 않음**. |

보조 사실: 우리 측정치(처음 2·10^5개 소수에서 같은 잉여류 쌍 비율 ≈ 0.424)는 제가 재계산해 **0.4243**으로 확인했고, 10^6개에서는 **0.4321**로 Lemke Oliver–Soundararajan 논문 표의 수치(215,873 + 216,213 = 432,086)와 정확히 일치합니다.

---

## (A) 논문별 정리 진술

### A1. D. K. L. Shiu, "Strings of congruent primes", J. London Math. Soc. (2) 61 (2000), no. 2, 359–373

- DOI: 10.1112/S0024610799007863. MR1760689. 저자 소속(출판 당시): Univ. of Georgia. (Cambridge Core 서지 페이지, Manchester Research Explorer에서 확인.)
- 출처 URL: https://www.cambridge.org/core/journals/journal-of-the-london-mathematical-society/article/abs/strings-of-congruent-primes/72849BC6261272AEC21BBEA94E2CAFBE , https://research.manchester.ac.uk/en/publications/strings-of-congruent-primes/

**초록 [원문 인용, Cambridge Core 페이지; 수식 부분은 페이지에서 "formula here"로 가려져 있어 `[수식]`으로 표시]:**

> "In 1920 Chowla made the following conjecture. Let p_n denote the nth prime; if q ≥ 3, (q, a) = 1 then there are infinitely many pairs of consecutive primes p_n and p_{n+1} such that [수식]. By considering the sum [수식] where χ is the non-principal character modulo 4 or 6, it is possible to prove the conjecture for q = 4 and q = 6 (a = ±1). In this paper we prove Chowla's conjecture for all q and a with (q, a) = 1. Moreover, we shall show that for any k there exist 'strings' of congruent primes such that [수식]. For each modulus q the method used applies best to the following two sets of residue classes: [수식]. Larger values of k in terms of p_{n+1} can be found for residue classes belonging to these sets."

**본문 정리의 형태 — 2차 문헌에 의한 재구성 (원문 [미확인]):**

(i) Thorne, "Bubbles of congruent primes" (arXiv:1201.5400), §1 **[원문 인용]**:
> "In 1997, Shiu [15] proved that if a, q, and k are arbitrary integers with (a, q) = 1, there exists a string of k consecutive primes p_{n+1} ≡ p_{n+2} ≡ ··· ≡ p_{n+k} ≡ a (mod q). (Here p_n denotes the nth prime.) Furthermore, if k is sufficiently large in terms of q, these primes can be chosen to satisfy the bound¹
> (1.1)  (1/φ(q)) · ( log log p_{n+1} · log log log log p_{n+1} / (log log log p_{n+1})² )^{1/φ(q)} ≪ k,
> uniformly in q."
> 각주 1: "In Shiu's statement of his results, the initial 1/φ(q) in (1.1) and the requirement that k be large are omitted, and the implied constant in (1.1) is allowed to depend on q. A careful reading of his proof shows that the dependence on q may be controlled as stated."
> 각주 2: "We describe a simplified version of Shiu's argument which proves (1.1) for all a; Shiu proves a better bound than (1.1) for certain moduli a (mod q)."

(ii) Ethan Yang, 해설 노트 "On strings of congruent primes" (Euler Circle, 비심사 자료, https://simonrs.com/eulercircle/analyticnt/ethan-shiustrings.pdf) — Shiu의 Theorem 1, 2를 다음과 같이 재진술 **[원문 인용]**:
> "Theorem 1.1. (1) For each q and a ∈ A± and large x, there exists a string of primes p_{n+1} ≡ p_{n+2} ≡ ··· ≡ p_{n+k} ≡ a (mod q), where p_{n+k} < x and k ≫ (log log x / log log log x)^{1/φ(q)}.
> (2) For each q and a with (q, a) = 1 and large x, there exists a string of primes p_{n+1} ≡ ··· ≡ p_{n+k} ≡ a (mod q), where p_{n+k} < x and k ≫ ( log log x · log log log log x / (log log log x)² )^{1/φ(q)}."
> 여기서 "A+ = {a : ∀p | q, a ≡ 1 mod p}, A− = {a : ∀p | q, a ≡ −1 mod p}, A± = A+ ∪ A−."
> "Shiu also provided an estimate for the number of such strings in his paper through Theorem 2 ... Theorem 4.1. Define ε₁(x) = C(q) k (log log log x / log log x)^{1/φ(q)} and ε₂(x) = C′(q) k ((log log log x)² / (log log x · log log log log x))^{1/φ(q)}. (1) Given q, k, a ∈ A±, the number B of strings of primes of the form p_{n+1} ≡ ··· ≡ p_{n+k} ≡ a (mod q), where p_{n+k} < x, has the asymptotic bound B ≫ x^{1−ε₁(x)}. (2) Given q, k, a, where q and a are relatively prime, the number B of strings ... where p_{n+k} < x, has the asymptotic bound B ≫ x^{1−ε₂(x)}."

(iii) Maynard, Compositio 152 (2016) p. 1520 **[원문 인용]**:
> "Theorem 3.3 extends a result of Shiu [Shi00] who showed the same result but with a lower bound ≫ x^{1−ε(x)} for ε(x) ≈ C_q m (log log x)^{−1/φ(q)} in the shorter range m ≪ (log log x)^{1/φ(q)−ε} and without the constraint p_{n+m} − p_n ≤ ε log x."

(iv) BFT 2015 p. 3 **[원문 인용]**: "Shiu [9] attributes to Chowla the conjecture that there are infinitely many pairs of consecutive primes p_r and p_{r+1} with p_r ≡ p_{r+1} ≡ a mod D (see also [4, A4]), and proved the above result without the constraint p_{r+m} − p_{r+1} ≤ D C_m." (여기서 "the above result" = Corollary 3: "infinitely many r ∈ N such that p_{r+1} ≡ ··· ≡ p_{r+m} ≡ a mod D".)

(v) Lemke Oliver–Soundararajan 2016 p. 1 **[원문 인용]**: "The main significant result in this direction is due to D. Shiu [16] who established that for any q ≥ 3, a reduced residue class a (mod q), and any r ≥ 2, the pattern (a, a, . . . , a) occurs infinitely often."

(vi) Lau 2024 (arXiv:2409.12819) **[원문 인용]**: "Theorem 1.2 (Shiu). For any m, q ∈ N with q ≥ 2 and a ∈ (Z/qZ)^×, let a = (a, . . . , a) ∈ ∏_{i=1}^m (Z/qZ)^×. Then, π(x; q, a) → ∞ as x → ∞." (π(x; q, a) := #{p_n ≤ x : p_{n+i−1} ≡ a_i (mod q) ∀ 1 ≤ i ≤ m}.)

(vii) Monks–Peluse–Ye 2013 (arXiv:1407.1290) **[원문 인용]**: "a recent theorem of Shiu proves that there exist arbitrarily long strings of consecutive primes that lie in any arithmetic progression that contains infinitely many primes." / "Using this, he obtains a lower bound on the length of the longest such string of primes within some row of the matrix, a bound which approaches infinity as the matrix grows."

**Shiu 정리의 형태에 대한 제 판단 [내 요약]:**
- 정리문의 1차 형태는 "**모든 k에 대해** k개 연속 소수 ≡ a (mod q)인 문자열이 **존재**한다" + "그 문자열의 길이 k를 가장 큰 소수 p_{n+k}(또는 상한 x)의 함수로 아래에서 잡을 수 있다"(Theorem 1) 이고, 그 위에 "**x 이하에서 그런 문자열의 개수 ≫ x^{1−ε(x)}**"(Theorem 2)가 있습니다. Thorne, Yang, Maynard 세 소스가 서로 독립적으로 같은 모양을 전하며, Yang의 "for ... large x ... p_{n+k} < x" 표현은 Thorne의 "p_{n+1}의 함수로 k 하한"과 Maynard의 "lower bound ≫ x^{1−ε(x)}"와 정합적입니다. 따라서 Shiu의 결과는 사실상 "**충분히 큰 모든 x에 대해, x 이하의 소수 중에 길이 ≫ f(x)인 문자열이 존재하고 그런 문자열 개수가 ≫ x^{1−ε(x)}**"라는 '모든 큰 x' 형태를 포함합니다.
- **"[x, 2x] 안에 문자열이 있다"는 dyadic 형태는 어떤 2차 문헌도 Shiu에게 귀속시키지 않습니다.** 개수 하한 x^{1−ε(x)}은 x^{1−o(1)}이지만 π(x)에 비해 작아서, 정리문만으로는 [x,2x]로 좁힐 수 없습니다(아래 (C) 참조). Maier 행렬 증명 구조상 행(짧은 구간)이 [Q^D, 2Q^D] 같은 범위에 놓이므로 증명을 손보면 dyadic 형태가 나올 가능성이 높지만, 이는 [내 추론]이며 원문을 못 봤으므로 [미확인]입니다.
- 팀 프롬프트에 적힌 "(log log log log x / log log log log log x)^{1/φ(q)}" 형태는 **어느 소스에도 없습니다.** 소스들이 전하는 형태는 위 (1.1)/(Yang Thm 1.1(2)): `((log log x · log log log log x)/(log log log x)²)^{1/φ(q)}`, A± 류에서는 `(log log x / log log log x)^{1/φ(q)}` 입니다.
- 연도: Thorne은 "In 1997, Shiu proved"라고 쓰는데 이는 Shiu의 Oxford 학위논문(1997)을 가리키는 것으로 보이며, 저널 출판은 2000년입니다 [내 추론].

### A2. W. D. Banks, T. Freiberg, C. L. Turnage-Butterbaugh, "Consecutive primes in tuples", Acta Arith. 167 (2015), no. 3, 261–266; arXiv:1311.7003v3 (2014-10-19)

- URL: https://arxiv.org/abs/1311.7003 , DOI 10.4064/aa167-3-4. 아래 인용은 arXiv v3 전문에서. (출판본과 정리 번호 일치 여부는 [미확인]이나, v3가 최종판이고 LO-S, Maynard 모두 같은 번호 체계로 인용.)

**[원문 인용] Theorem 1:**
> "Theorem 1. Let m, k ∈ N with m ≥ 2 and k ≥ k_m, where k_m is as in the Maynard–Tao theorem. Let b_1, . . . , b_k be distinct integers such that {x + b_j}_{j=1}^k is admissible, and let g be any positive integer coprime with b_1 ··· b_k. Then, for some subset {h_1, . . . , h_m} ⊆ {b_1, . . . , b_k}, there are infinitely many n ∈ N such that gn + h_1, . . . , gn + h_m are consecutive primes."

**[원문 인용] Corollary 3 (Shiu 확장):**
> "Corollary 3. Let a and D ≥ 3 be coprime integers. For every m ≥ 2, there are infinitely many r ∈ N such that p_{r+1} ≡ p_{r+2} ≡ ··· ≡ p_{r+m} ≡ a mod D and p_{r+m} − p_{r+1} ≤ D C_m, where C_m is a constant depending only on m."

**[원문 인용] Corollary 3의 증명 (전문):**
> "Proof of Corollary 3. Let m ≥ 2, and let k ≥ k_m. Let {x + a_j}_{j=1}^k be any admissible k-tuple with a_1 < ··· < a_k, and put b_j = D a_j + a for 1 ≤ j ≤ k; then {x + b_j}_{j=1}^k is also admissible. Since gcd(D, b_j) = gcd(D, a) = 1 for each j, we can apply Theorem 1 with g = D to conclude that there is a subset {h_1, . . . , h_m} ⊆ {b_1, . . . , b_k} such that Dn + h_1, . . . , Dn + h_m are consecutive primes for infinitely many n ∈ N; as such primes lie in the arithmetic progression a mod D and are contained in an interval of length b_k − b_1 = D(a_k − a_1), the corollary follows."

**[원문 인용] Theorem 1 증명의 핵심 단계 (dyadic/정량 정보가 소실되는 지점):**
> "Let m′ be the largest integer for which there exists a subset {h_1, . . . , h_{m′}} ⊆ {b_1, . . . , b_k} with the property that the numbers g(QN + a) + h_i (1 ≤ i ≤ m′) are simultaneously prime for infinitely many N ∈ N. Since k ≥ k_m we can apply the Maynard–Tao theorem with A(x) to deduce that m′ ≥ m. By the maximal property of m′, it must be the case that for all sufficiently large N ∈ N, if the numbers in (4) are all prime, then g(QN + a) + b_j is composite for every b_j ∈ {b_1, . . . , b_k} \ {h_1, . . . , h_{m′}}. Hence, for infinitely many N ∈ N, the interval [g(QN + a) + b_1, g(QN + a) + b_k] contains precisely m′ primes ..."

**형태 정리 [내 요약]:**
- Theorem 1, Corollary 3 모두 "**infinitely many n (resp. r)**" 형태. "for all large N, N < n ≤ 2N" 형태도, 개수 하한 N/(log N)^k도 **없음**.
- 증명이 "무한히 많은 N에 대해 동시에 소수가 되는 최대 부분집합 m′"을 잡는 **극대성 논법**이라 Maynard–Tao의 dyadic 개수 하한이 결과로 전달되지 않습니다. 따라서 BFT에서 Hd(q)의 [x,2x] 형태를 끌어낼 수 없습니다.
- 잉여류 처방: Theorem 1의 `g`와 `h_j`가 소수 gn + h_j의 잉여류를 g mod로 고정하므로(Cor. 3는 g = D, h_j ≡ a mod D), "소수들을 잉여류 a mod D에 넣는 것"은 가능. 그러나 "n ≡ ν (mod q)"를 명시적으로 처방하는 진술은 없음(증명 내부에서 n = QN + a 꼴의 잉여류를 쓰긴 함).
- **서로 다른 잉여류 패턴 (a_1, …, a_m)에 관한 결과는 BFT에 없음.** 논문의 다른 응용은 Erdős–Turán 문제(증가/감소/나눗셈 조건의 연속 간격, Corollary 1, 2)입니다.
- 주의: Corollary 3는 **D ≥ 3** 요구. q = 3은 해당.

### A3. J. Maynard, "Dense clusters of primes in subsets", Compositio Math. 152 (2016), no. 7, 1517–1554; arXiv:1405.2593v2

- URL: https://arxiv.org/abs/1405.2593 , DOI 10.1112/S0010437X16007296 (Cambridge Core 오픈액세스 PDF 확인). 정리 번호는 arXiv v2와 출판본이 **동일**(Theorem 3.1–3.5). 증명 내 식 번호는 다름: arXiv v2의 (6.26), (6.27) = 출판본의 (6.24), (6.25).

**[원문 인용] 정의 (2.1), 출판본 p. 1518:**
> "Given a set of integers A, a set of primes P, and a linear function L(n) = l_1 n + l_2, we define A(x) = {n ∈ A : x ≤ n < 2x}, A(x; q, a) = {n ∈ A(x), n ≡ a (mod q)}, L(A) = {L(n) : n ∈ A}, ϕ_L(q) = ϕ(|l_1|q)/ϕ(|l_1|), P_{L,A}(x) = L(A(x)) ∩ P, P_{L,A}(x; q, a) = L(A(x; q, a)) ∩ P."

**[원문 인용] Theorem 3.1 (출판본 pp. 1518–1519):**
> "Theorem 3.1. Let α > 0 and 0 < θ < 1. Let A be a set of integers, P a set of primes, L = {L_1, . . . , L_k} an admissible set of k linear functions, and B, x integers. Let the coefficients L_i(n) = a_i n + b_i ∈ L satisfy 0 ≤ a_i, b_i ≤ x^α for all 1 ≤ i ≤ k, and let k ≤ (log x)^α and 1 ≤ B ≤ x^α. There is a constant C depending only on α and θ such that the following holds. If k ≥ C and (A, L, P, B, x, θ) satisfy Hypothesis 1, and if δ > (log k)^{−1} is such that (1/k)(ϕ(B)/B) Σ_{L∈L} (ϕ(a_i)/a_i) #P_{L,A}(x) ≥ δ #A(x)/log x, then
> #{n ∈ A(x) : #({L_1(n), . . . , L_k(n)} ∩ P) ≥ C^{−1} δ log k} ≫ #A(x) / ((log x)^k exp(Ck)).
> Moreover, if P = P, k ≤ (log x)^{1/5} and all L ∈ L have the form an + b_i with |b_i| ≤ (log x) k^{−2} and a ≪ 1, then the primes counted above can be restricted to be consecutive, at the cost of replacing exp(Ck) with exp(Ck^5) in the bound."

**[원문 인용] Theorem 3.3 (출판본 p. 1519 = arXiv v2 p. 3):**
> "Theorem 3.3. Fix ε > 0 and let x > x_0(ε, q). There is a constant c_ε > 0 (depending only on ε) such that uniformly for m ≤ c_ε log log x, q ≤ (log x)^{1−ε} and (a, q) = 1 we have
> #{p_n ≤ x : p_n ≡ ··· ≡ p_{n+m} ≡ a (mod q), p_{n+m} − p_n ≤ ε log x} ≫_ε π(x) / (2q)^{exp(Cm)}.
> Here C > 0 is a fixed constant."

**[원문 인용] Theorem 3.3 직후 해설 (출판본 p. 1520):**
> "We see that for fixed m, q, Theorem 3.3 shows a positive proportion of primes p_n are counted (and so our lower bound is of the correct order of magnitude). In particular, for a positive proportion of primes p_n we have p_n ≡ p_{n+1} ≡ ··· ≡ p_{n+m} ≡ a (mod q) and p_{n+m} − p_n ≤ ε log p_n. This disproves the conjecture of Knapowski and Turán [KT77] that #{p_n ≤ x : p_n ≡ p_{n+1} ≡ 1 (mod 4)} = o(π(x))."

**[원문 인용] Theorem 3.3 증명의 dyadic 중간 결과 (출판본 p. 1535, 식 (6.24); arXiv v2 식 (6.26)):**
> "Putting this all together, we obtain the number N of integers n with x ≤ n ≤ 2x such that there are ≫ log k consecutive primes all congruent to a (mod q) in the interval [qn, qn + η log x] satisfies
> (6.24)  N ≫ x / (q^k exp(C_6 k^5)).
> We see that the initial prime in each such interval is counted by at most log x values of n. Therefore, changing the count to be over the initial prime, recalling k = ⌈exp(m/c_1)⌉, recalling that η ≤ ε, and replacing x with x/3q gives
> (6.25)  #{p_n ≤ x : p_n ≡ ··· ≡ p_{n+m} ≡ a (mod q), p_{n+m} − p_n ≤ ε log x} ≫_ε π(x)/(2q)^{exp(Cm)}, for a suitable constant C > 0, as required."

**[원문 인용] 증명 설정 (Theorem 3.2 증명, 3.3이 그대로 차용):** "We take θ = 1/3, P = P, A = N, L = {L_1, . . . , L_k} ..." 그리고 Landau–Page 예외 modulus q_0가 있으면 "we take B to be the largest prime factor of q_0, and otherwise we take B = 1" ; "Hypothesis 1 holds for (A, L, P, B, x, 1/3) for any k ≤ (log x)^{1/5} provided k is sufficiently large". Theorem 3.3 증명에서는 "L = {L_1,…,L_k} contains functions of the form L_i(n) = qn + a + qb_i with qb_i ≤ η log x" 전체에 대해 평균을 취함.

**형태 정리 [내 요약]:**
- Theorem 3.3의 **정리문**은 "x > x_0(ε, q)인 모든 x에 대해, p_n ≤ x 인 시작 소수의 개수 ≫ π(x)/(2q)^{exp(Cm)}" — 즉 "for all large x, count among primes ≤ x ≥ c·π(x)" 형태. "[x,2x]" 형태는 정리문에 없음.
- 그러나 **증명 내부 식 (6.24)** 는 정확히 "x ≤ n ≤ 2x 인 n 중, [qn, qn + η log x] 안에 ≫ log k 개의 연속 소수가 모두 ≡ a (mod q)인 n의 개수 ≫ x/(q^k exp(C_6 k^5))" 이며, 이는 x > x_0(ε,q)인 모든 x에 대해 성립(정리의 가정 그대로). 또 Theorem 3.1 자체가 정의 (2.1)에 의해 n ∈ [x, 2x) 위에서 세므로, A = ℕ 로 두면 Theorem 3.1 + "Moreover"(연속성) 절이 곧 dyadic 진술입니다. Hypothesis 1 검증은 Theorem 3.2/3.3 증명(Bombieri–Vinogradov + Landau–Page)에 들어 있습니다.

### A4. R. J. Lemke Oliver, K. Soundararajan, "Unexpected biases in the distribution of consecutive primes", Proc. Natl. Acad. Sci. USA 113 (2016), no. 31, E4446–E4454; arXiv:1603.03720v4

- URL: https://arxiv.org/abs/1603.03720 , DOI 10.1073/pnas.1605366113.

**[원문 인용] 서론에서 '알려진 것' (p. 1):**
> "Let r ≥ 1 be an integer, and let a = (a_1, a_2, . . . , a_r) denote an r-tuple of reduced residue classes (mod q). Define π(x; q, a) := #{p_n ≤ x : p_{n+i−1} ≡ a_i (mod q) for each 1 ≤ i ≤ r}, which counts the number of occurrences of the pattern a (mod q) among r consecutive primes the least of which is below x. When r ≥ 2, little is known about the distribution of such patterns among the primes. When r = 2 and φ(q) = 2 (thus q = 3, 4, or 6), Knapowski and Turán [9] observed that all the four possible patterns of length 2 appear infinitely many times. The main significant result in this direction is due to D. Shiu [16] who established that for any q ≥ 3, a reduced residue class a (mod q), and any r ≥ 2, the pattern (a, a, . . . , a) occurs infinitely often. Recent progress in sieve theory has led to a new proof of Shiu's result (see [2]), and moreover in this particular situation Maynard [11] has shown that π(x; q, (a, . . . , a)) ≫ π(x)."
> ([2] = BFT, [11] = Maynard "Dense clusters", [16] = Shiu, [9] = Knapowski–Turán 1977.)

**[원문 인용] mod 3 수치 (p. 2):**
> "among the first million primes (for convenience restricting to those greater than 3) we find π(x_0; 3, (1, 1)) = 215,873, π(x_0; 3, (1, 2)) = 283,957, π(x_0; 3, (2, 1)) = 283,957, π(x_0; 3, (2, 2)) = 216,213."

**[원문 인용] Main Conjecture (p. 2):**
> "π(x; q, a) = (li(x)/φ(q)^r) ( 1 + c_1(q; a) (log log x / log x) + c_2(q; a) (1/log x) + O((log x)^{−7/4}) ), where c_1(q; a) = (φ(q)/2) ( (r − 1)/φ(q) − #{1 ≤ i < r : a_i ≡ a_{i+1} (mod q)} )".
> 그리고 Conjecture 1.2: "Let q = 3 or 4, and let a be either 1 (mod q) or −1 (mod q). Then for all x ≥ 5, we have π(x; q, (a, −a)) > π(x; q, (a, a))."

**수치 대조 [내 계산, 작성 당시의 임시 스크립트, 저장소에 없음]:**

| 범위 (3 초과 소수) | 같은 류 쌍 | 다른 류 쌍 | 같은 류 비율 | 3개 모두 같은 류 비율 |
|---|---|---|---|---|
| 처음 2·10^5개 (p_N = 2,750,159) | 84,857 | 115,140 | **0.4243** | 0.1687 |
| 처음 10^6개 (p_N = 15,485,863) | 432,086 | 567,911 | **0.4321** | 0.1765 |

- 팀 측정치 0.424 재현됨. 10^6개 수치는 LO-S 표의 215,873 + 216,213 = 432,086과 정확히 일치.
- Main Conjecture에서 q = 3, r = 2, a = (a,a): c_1 = (2/2)(1/2 − 1) = −1/2 이므로 같은 류 비율 ≈ ½(1 − ½·log log x/log x + …)로 ½에 **아주 느리게** 수렴. 0.424 → 0.432 로 x가 커질수록 올라가는 것이 이 예측과 부합 [내 요약].

### A5. 기타 직접 관련 문헌

**(a) T. Freiberg, "Strings of congruent primes in short intervals", J. Lond. Math. Soc. (2) 84 (2011), 344–364; arXiv:1005.4703** — [원문 인용] "In [9], Shiu proved an old conjecture of Chowla that there are infinitely many pairs of consecutive primes p_r, p_{r+1} which are both ≡ a mod q. Indeed he was even able to extend this to k consecutive primes." / "Theorem 1.1. Let q ≥ 3 and a be integers with (q, a) = 1, and fix any ε > 0. There exist infinitely many pairs of consecutive primes p_r, p_{r+1} such that p_r ≡ p_{r+1} ≡ a mod q and p_{r+1} − p_r < ε log p_r." (pairs만, "infinitely many" 형태.)

**(b) T. Freiberg, "A note on the theorem of Maynard and Tao", arXiv:1311.5319** — Yang 노트의 Theorem 1.3으로 재진술 [원문 인용(Yang)]: "Let q ≥ 3 and a be a coprime pair of integers, and let m ≥ 2 be an integer. There exists a constant B = B(q, a, m) ... There exist infinitely many n such that p_{n+1} ≡ ··· ≡ p_{n+m} ≡ a mod q and p_{n+m} − p_{n+1} ≤ B." BFT Cor. 3과 같은 내용의 독립 증명. (원문 [미확인].)

**(c) F. Thorne, "Bubbles of congruent primes", arXiv:1201.5400** — Shiu 정리의 정량형 (1.1)과 각주(A1 참조); 허수 이차체로 일반화.

**(d) K. Monks, S. Peluse, L. Ye, "Strings of special primes in arithmetic progressions", Arch. Math. 101 (2013), 219–234; arXiv:1407.1290** — [원문 인용] "Theorem 1.1. If the set of primes A is well-distributed (see Section 2 for the definition,) then there exist arbitrarily long strings of consecutive primes in A all of which lie in any given progression {a + qn} with (q, a) = 1." Shiu의 Maier 행렬 방법을 부분집합으로 확장. dyadic 형태 없음.

**(e) C. F. (Joshua) Lau, "Residue class patterns of consecutive primes", arXiv:2409.12819 (v2, 2026-07-13), Oxford** — **서로 다른 잉여류 패턴에 관한 현재 상태를 가장 명확히 서술**. [원문 인용, 초록]: "Dickson's conjecture and the Hardy–Littlewood prime tuple conjecture predict that every pattern of reduced residue classes modulo q is attained by infinitely many strings of m consecutive primes. At present, however, even proving that a single non-constant residue class pattern of length m occurs infinitely often is beyond the reach of existing methods. Combining Dirichlet's theorem on primes in arithmetic progressions with a theorem of Shiu (2000) shows that, for any m, q ∈ N with q ≥ 3, at least mφ(q) residue class patterns of length m are attained by infinitely many consecutive primes."
[원문 인용, Prop. 1.3 증명]: "For each a ∈ (Z/qZ)^×, Shiu's theorem states π(x; q, (a, . . . , a)) → ∞ as x → ∞. By Dirichlet's theorem, we know that each string of consecutive primes all congruent to a (mod q) must terminate. Since φ(q) ≥ 2, by the pigeonhole principle there must exist a′ ∈ (Z/qZ)^× with a′ ≠ a such that π(x; q, (a, . . . , a, a′)) → ∞ as x → ∞."
Lau의 주정리(Theorem 1.5)는 q squarefree일 때 "처방된 잉여류 열 안에서 **블록 패턴**(각 상수 블록 길이 ≤ ⌈log m⌉)이 무한히 자주 나타난다"는 것으로, **특정 비상수 패턴 (a,b) 하나를 보장하지는 않음**. 기술적 보조정리 중에 "for all sufficiently large N in terms of m, q, k, ε, there is n ∈ [N, 2N] with n ≡ b (mod W) ..."(p. 15)처럼 dyadic 형태가 등장하나 이는 패턴-블록 문맥의 중간 결과.

**(f) S. Knapowski, P. Turán, "On prime numbers ≡ 1 resp. 3 mod 4", Number theory and algebra, Academic Press 1977, 157–165** — φ(q) = 2 (q = 3, 4, 6)에서 길이 2 패턴 4종 모두 무한히 등장(LO-S 인용). [내 추론] 이 고전 논법(Littlewood의 Ω± 진동 결과: 같은 류 쌍이 유한하다면 두 류의 개수 차가 유계가 되어 모순)은 **길이 3 동일 류 런으로는 확장되지 않음** — 길이 3이 없다고 가정해도 π(x;3,1) ≤ 2π(x;3,2) + O(1)이라는 약한 결론밖에 안 나오므로 모순이 없음. 따라서 (H3)에는 Shiu급 결과가 실제로 필요.

**(g) "every pattern (a_1, …, a_m) is realized" 류 정리:** **존재하지 않음.** LO-S("little is known"), Lau("even ... a single non-constant residue class pattern ... is beyond the reach of existing methods") 모두 명시적으로 부정. Chebyshev's bias 계열 문헌(Rubinstein–Sarnak 등)은 π(x;q,a) 단일 류의 편향에 관한 것이고 연속 소수 패턴의 무한성을 주지 않음.

### A6. Lean 4 Mathlib 상황

- **Dirichlet 정리는 Mathlib에 있음**: `Mathlib/NumberTheory/LSeries/PrimesInAP.lean`. 선언: `Nat.infinite_setOfPred_prime_and_eq_mod` (구 이름 `Nat.infinite_setOf_prime_and_eq_mod`, 2026-07-09 deprecated), `Nat.forall_exists_prime_gt_and_eq_mod`, `Nat.forall_exists_prime_gt_and_zmodEq`, `Nat.forall_exists_prime_gt_and_modEq`, `Nat.frequently_atTop_prime_and_modEq`, `Nat.infinite_setOfPred_prime_and_modEq`. (https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/LSeries/PrimesInAP.html)
- **Shiu / 연속 소수 문자열 / Maier 행렬 / Maynard–Tao 체는 없음.** GitHub 코드 검색(`repo:leanprover-community/mathlib4`)에서 "consecutive primes" 0건, "Shiu" 0건, "Maier matrix" 0건. ("Chowla" 1건은 `docs/1000.yaml`의 무관한 항목.) Bombieri–Vinogradov, Selberg sieve 역시 Mathlib에 없음 [내 요약; 검색 결과 기반].
- 결론: (H3), (Hd(q)) 모두 Mathlib에서 증명 불가. 공리(axiom)나 `sorry`로 두고 문헌 근거를 주석으로 달아야 함.

---

## (B) (H3) 판정

**(H3)**: 모든 M에 대해 m > M이 존재하여 p_{m+1} ≡ p_{m+2} ≡ p_{m+3} (mod 3).

**판정: 성립. 세 갈래 독립 근거.**

1. **BFT 2015 Corollary 3 (가장 직접적).** D = 3, a ∈ {1, 2}, m = 3을 대입하면 verbatim으로 "there are infinitely many r ∈ N such that p_{r+1} ≡ p_{r+2} ≡ p_{r+3} ≡ a mod 3 (and p_{r+3} − p_{r+1} ≤ 3C_3)". "infinitely many r" ⟺ "∀M ∃r > M" 이므로 추가 논리 없이 (H3). 조건 D ≥ 3, gcd(a, 3) = 1 충족. (세 소수가 **서로** 합동이면 되므로 a = 1 하나만 써도 충분.)

2. **Shiu 2000 (임의 길이 문자열) + 간단한 논리.** Shiu: 모든 k에 대해 어떤 n이 있어 p_{n+1} ≡ ··· ≡ p_{n+k} ≡ a (mod 3). [내 추론 — 논리 점검] 길이 k 문자열은 k − 2개의 연속 3-런을 포함하며, 그 시작 인덱스는 n+1, …, n+k−2. 주어진 M에 대해 k = M + 3을 택하면 마지막 3-런의 시작 인덱스 n + k − 2 ≥ k − 2 = M + 1 > M. 따라서 "∀M ∃m > M". 팀이 적은 "a string of length k contains k−2 triples"는 맞고, 추가로 필요한 것은 "k를 M보다 크게 잡아 인덱스를 M 너머로 밀어낸다"는 한 줄뿐입니다(n ≥ 0이므로 n + k − 2 ≥ k − 2). Thorne/Yang 형태("for large x, string with p_{n+k} < x and k ≫ f(x) → ∞")를 써도 동일.

3. **Maynard 2016 Theorem 3.3.** m = 2, q = 3, ε = 1/2로 고정한다. 원문의 범위 조건 3 ≤ (log x)^{1/2}, 2 ≤ c_{1/2} log log x는 x가 충분히 크면 모두 성립한다. 이 범위와 x > x_0에서 #{p_n ≤ x : p_n ≡ p_{n+1} ≡ p_{n+2} ≡ a (mod 3), p_{n+2} − p_n ≤ (1/2) log x} ≫ π(x)/6^{exp(2C)}. 우변 → ∞ 이므로 그런 n이 무한히 많음(→ (H3)). 이것은 (H3)보다 훨씬 강한 "양의 비율" 진술. 이전의 ε = 1 예시는 q ≤ (log x)^{1−ε}를 만족하지 않아 잘못이었다.

보조: Lemke Oliver–Soundararajan 서론이 Shiu [16]→BFT [2]→Maynard [11]로 이 결과의 계보를 그대로 확인해 줌(A4 인용). 수치적으로도 처음 2·10^5개 소수 중 3개 연속 동일 류 런의 비율이 0.1687(약 33,700개)로 풍부.

---

## (C) (Hd(q)) 판정

**(Hd(q))**: 고정 소수 q (≠ 2, 5), 모든 M에 대해 자릿수 d가 존재하여, 인덱스 M 너머에 (i) 연속 소수 3개가 모두 ≡ a (mod q)이고 마지막 둘이 정확히 d자리인 런, (ii) 같은 조건에 마지막 둘이 정확히 d+1자리인 런이 존재. 충분조건: "충분히 큰 모든 x에 대해 [x, 2x]가 같은 류 a (mod q)의 연속 소수 3개를 포함".

**판정:**

**(C1) "[x, 2x] for all large x" 형태를 정리문으로 verbatim 진술한 출판 논문: 없음.** 확인한 정리문의 형태는 다음과 같습니다.

| 소스 | 정리문의 형태 | Hd(q)에 충분? |
|---|---|---|
| Shiu 2000 Thm 1 (2차 문헌 재구성) | ∀k ∃ 문자열; 큰 x마다 p_{n+k} < x인 길이 ≫ f(x) 문자열 존재 | 아니오 (위치를 [x,2x]로 못 좁힘) |
| Shiu 2000 Thm 2 | x 이하 문자열 개수 ≫ x^{1−ε(x)} | 아니오 (아래 설명) |
| BFT 2015 Thm 1 / Cor 3 | infinitely many n / r | 아니오 |
| Freiberg 2011 Thm 1.1, Freiberg 2013 note | infinitely many | 아니오 |
| Maynard 2016 Thm 3.3 (정리문) | ∀x > x_0: #{p_n ≤ x : …} ≫ π(x)/(2q)^{exp(Cm)} | **정리문만으로는 아니오**, 단 [x, Tx] (T 상수)까지는 됨 |
| Maynard 2016 Thm 3.1 + 정의 (2.1) + "Moreover" 절 | #{n ∈ [x,2x) : ≥ C^{-1}δ log k개의 L_i(n)이 **연속** 소수} ≫ x/((log x)^k exp(Ck^5)), Hypothesis 1 하에 | **예** (Hypothesis 1 검증은 Thm 3.2/3.3 증명에 있음) |
| Maynard 2016 Thm 3.3 **증명 내 식 (6.24)** [arXiv (6.26)] | #{x ≤ n ≤ 2x : [qn, qn+η log x]에 ≫ log k개의 연속 소수 모두 ≡ a (mod q)} ≫ x/(q^k exp(C_6 k^5)), ∀x > x_0(ε,q) | **예 — 가장 가까운 verbatim 진술** |

**(C2) 왜 정리문(Thm 3.3)만으로는 부족한가 [내 추론].** f(x) := Thm 3.3의 좌변, g(x) := #{p_n ≤ x : p_n ≡ ··· ≡ p_{n+m} ≡ a} ≥ f(x), g는 단조, g(x) ≤ π(x). 시작 소수가 (x, Tx]에 있는 문자열이 존재하려면 f(Tx) > g(x)이면 충분하고, f(Tx) ≥ c_ε π(Tx)/(2q)^{exp(Cm)} ≈ c_ε T π(x)/(2q)^{exp(Cm)} 이므로 **T > (2q)^{exp(Cm)}/c_ε** 이면 충분. 즉 정리문은 "[x, Tx] for all large x"를 상수 T = T(q, m, ε)에 대해 줍니다. 하지만 T ≤ 10(한 자릿수 길이)로 줄일 수 없고, 하한 c_ε π(x)/(2q)^{exp(Cm)}만으로는 count가 특정 십진 구간들에만 몰려 있는 상황을 배제할 수 없습니다. Shiu Thm 2의 x^{1−ε(x)}는 π(x)보다 작으므로 더더욱 안 됩니다.

**(C3) (6.24)에서 Hd(q)로 [내 추론; 2026-11-11 매개변수·올림 경계 수정].** q ≥ 3, a ∈ (Z/qZ)^×를 고정하고 ε = 1/2, m = 2(연속 소수 3개 = p_n, p_{n+1}, p_{n+2})로 둔다. q ≤ (log x)^{1/2}, 2 ≤ c_{1/2} log log x 등 원문의 범위 조건은 x가 충분히 크면 성립한다. k도 고정한 뒤 문턱을 키우면 모든 큰 x에서 필요한 세 소수를 얻는 n의 개수가 양수다. 자릿수 d에 대해 U := 10^{d−1}, x := ⌈U/q⌉로 두면 n ∈ [x, 2x]에 대해 U ≤ qn ≤ 2U + 2q이고 η ≤ ε < 1이다. 따라서 해당 소수들은 [U, 2U + 2q + log x] 안에 있다. q가 고정이고 log ⌈U/q⌉ = o(U)이므로, 충분히 큰 d에서는 2q + log x ≤ U이고 이 구간은 [U, 3U] ⊂ [U, 10U)에 들어간다. 이전의 상계 2U + q는 일반적으로 성립하지 않는다. 따라서 **충분히 큰 모든 d에 대해, 정확히 d자리인 연속 소수 3개가 모두 ≡ a (mod q)인 런이 존재**(마지막 둘뿐 아니라 셋 다 d자리). 주어진 M에 대해 d ≥ d_0이고 10^{d−1} > p_M이 되게 잡으면 d와 d+1 모두에서 인덱스 M 너머의 런을 얻으므로 Hd(q)다. q는 소수일 필요가 없으며, q ≠ 2, 5 제약은 이 문헌 정리의 조건이 아니다. 일반 길이 런과 Q1의 연결은 `2026-11-11-maynard-general-q1.md`에서 별도로 검토한다.

**(C4) Theorem 3.1 경로 (증명 안이 아니라 '정리문'에서 출발하고 싶을 때) [내 추론].** A = ℕ(⇒ A(x) = [x, 2x)), P = 모든 소수, L = {qn + a + q b_i}_{i≤k} (b_i를 ≤ k인 소수의 곱의 배수로 잡아 admissible), a_i = q ≪ 1, |b_i'| = a + q b_i ≤ (log x) k^{−2} (x 큼), θ = 1/3, B = Landau–Page 예외 modulus의 최대 소인수(없으면 1). Hypothesis 1 (1),(3)은 자명, (2)는 Bombieri–Vinogradov + Landau–Page — Maynard가 Thm 3.2 증명 pp. 1533–1534에서 정확히 이 (A, P, B, θ)에 대해 검증. δ = 1 + o(1). 그러면 Theorem 3.1의 "Moreover" 절이 "n ∈ [x, 2x) 중 ≥ C^{−1} log k개의 L_i(n)이 **연속** 소수(모두 ≡ a mod q)인 n의 개수 ≫ x/((log x)^k exp(Ck^5))"를 모든 큰 x에 대해 줌. 이 경로는 정리문 + 논문 안의 Hypothesis 1 검증만 인용하면 되므로 보고서/주석용으로 깔끔합니다. 다만 "a ≪ 1"의 암시 상수와 x_0의 q-의존을 명시적으로 따져야 함.

**2026-11-11 적용 시의 여유:** 원문의 선형식은 `qn+a+qb_i`이므로, 일반 a에 대해서는 창을 여유 있게 `[qn,qn+a+η log x]`로 잡는다. `η≤1/2`이고 a가 고정이면 충분히 큰 x에서 `a+η log x≤log x`이므로 (C3)의 최종 상계는 유지된다. 원하는 런 길이 K에 대해 논문의 문자열 매개변수를 K로 잡으면, (6.20)의 양수성에서 필요한 개수를 확보할 수 있다. 시작 인덱스 비교는 `U > Nat.nth Nat.Prime M` (1-based로는 `U > p_(M+1)`)로 읽는다.

**(C5) 권고 인용 문구(한국어 주석용).** Maynard [Compositio 152 (2016), Thm 3.3 및 증명의 (6.24); arXiv v2 (6.26)]를 ε = 1/2에 적용한다. q ≥ 3, (a,q)=1과 필요한 런 길이를 먼저 고정하면, 충분히 큰 모든 x에서 [x,2x] 안의 어떤 n에 대해 [qn, qn + log x] 안에 원하는 길이의 전역 연속 소수들이 모두 a (mod q)로 놓인다. x = ⌈10^{d−1}/q⌉와 문턱을 키우는 논증을 통해 충분히 큰 모든 d에서 정확히 d자리인 런을 얻는다. 이는 정리문 자체가 아닌 증명 내부 결과에서 유도한 따름정리이며 Lean 밖의 문헌 연결이다.

---

## (D) 참고문헌 (BibTeX 스타일)

```bibtex
@article{Shiu2000,
  author  = {Shiu, D. K. L.},
  title   = {Strings of congruent primes},
  journal = {J. London Math. Soc. (2)},
  volume  = {61}, number = {2}, pages = {359--373}, year = {2000},
  doi     = {10.1112/S0024610799007863}, mrnumber = {1760689}
}
@article{BanksFreibergTurnageButterbaugh2015,
  author  = {Banks, William D. and Freiberg, Tristan and Turnage-Butterbaugh, Caroline L.},
  title   = {Consecutive primes in tuples},
  journal = {Acta Arith.}, volume = {167}, number = {3}, pages = {261--266}, year = {2015},
  doi     = {10.4064/aa167-3-4}, eprint = {1311.7003}, archivePrefix = {arXiv}
}
@article{Maynard2016,
  author  = {Maynard, James},
  title   = {Dense clusters of primes in subsets},
  journal = {Compos. Math.}, volume = {152}, number = {7}, pages = {1517--1554}, year = {2016},
  doi     = {10.1112/S0010437X16007296}, eprint = {1405.2593}, archivePrefix = {arXiv}
}
@article{LemkeOliverSoundararajan2016,
  author  = {Lemke Oliver, Robert J. and Soundararajan, Kannan},
  title   = {Unexpected biases in the distribution of consecutive primes},
  journal = {Proc. Natl. Acad. Sci. USA}, volume = {113}, number = {31}, pages = {E4446--E4454}, year = {2016},
  doi     = {10.1073/pnas.1605366113}, eprint = {1603.03720}, archivePrefix = {arXiv}
}
@article{Freiberg2011,
  author  = {Freiberg, Tristan},
  title   = {Strings of congruent primes in short intervals},
  journal = {J. Lond. Math. Soc. (2)}, volume = {84}, number = {2}, pages = {344--364}, year = {2011},
  eprint  = {1005.4703}, archivePrefix = {arXiv}
}
@misc{Freiberg2013,
  author = {Freiberg, Tristan}, title = {A note on the theorem of Maynard and Tao},
  year = {2013}, eprint = {1311.5319}, archivePrefix = {arXiv}
}
@misc{Thorne2012,
  author = {Thorne, Frank}, title = {Bubbles of congruent primes},
  year = {2012}, eprint = {1201.5400}, archivePrefix = {arXiv}
}
@article{MonksPeluseYe2013,
  author  = {Monks, Keenan and Peluse, Sarah and Ye, Lynnelle},
  title   = {Strings of special primes in arithmetic progressions},
  journal = {Arch. Math. (Basel)}, volume = {101}, pages = {219--234}, year = {2013},
  doi     = {10.1007/s00013-013-0544-x}, eprint = {1407.1290}, archivePrefix = {arXiv}
}
@misc{Lau2024,
  author = {Lau, Cheuk Fung (Joshua)}, title = {Residue class patterns of consecutive primes},
  year = {2024}, note = {v2, 2026-07-13}, eprint = {2409.12819}, archivePrefix = {arXiv}
}
@incollection{KnapowskiTuran1977,
  author = {Knapowski, S. and Tur\'an, P.},
  title = {On prime numbers $\equiv 1$ resp. $3 \bmod 4$},
  booktitle = {Number theory and algebra}, pages = {157--165}, publisher = {Academic Press}, address = {New York}, year = {1977}
}
@misc{Yang_ShiuNote,
  author = {Yang, Ethan}, title = {On strings of congruent primes},
  howpublished = {Euler Circle expository note, \url{https://simonrs.com/eulercircle/analyticnt/ethan-shiustrings.pdf}},
  note = {비심사 해설 자료; Shiu Thm 1, 2의 재진술 출처로만 사용}
}
@misc{Mathlib_PrimesInAP,
  title = {Mathlib.NumberTheory.LSeries.PrimesInAP (Dirichlet's theorem on primes in AP)},
  howpublished = {\url{https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/LSeries/PrimesInAP.html}}
}
```

---

## (E) 미해결 / 불확실 사항

1. **Shiu 2000 원문 미열람.** Wiley(JLMS) 페이지는 403, Cambridge Core 초록은 수식이 placeholder, ResearchGate·zbMATH 403, Semantic Scholar는 초록 null. 브라우저 UA 위장은 봇 차단 우회에 해당하여 시도하지 않았습니다. Shiu의 Theorem 1/2의 **정확한 번호와 문구**는 Thorne(각주 포함), Yang, Maynard, BFT, LO-S, Lau 6개 2차 소스의 교차 확인에 의존합니다. 이들은 형태("∀k ∃ string", "p_{n+k} < x, k ≫ f(x)", "개수 ≫ x^{1−ε(x)}")에서 서로 일치하지만, 상수의 q-의존/"k large" 조건은 Thorne 각주대로 Shiu 원문과 Thorne 재진술이 다릅니다. 원문이 필요하면 MathSciNet(MR1760689) 리뷰나 도서관 접근을 권합니다.
2. **팀 프롬프트의 지수 형태 불일치.** "(log log log log x / log log log log log x)^{1/φ(q)}"는 어느 소스에도 없고, 소스들은 "((log log x · log log log log x)/(log log log x)²)^{1/φ(q)}" (일반 a) 및 "(log log x / log log log x)^{1/φ(q)}" (a ∈ A±)를 전합니다. 팀 내부 문서에 전자가 적혀 있다면 수정 권장.
3. **BFT 출판본(Acta Arith.)의 정리 번호**는 arXiv v3과 같다고 가정했습니다(LO-S와 Maynard가 같은 번호로 인용). 직접 대조는 [미확인].
4. **Maynard Theorem 3.1 "Moreover" 절의 조건 "|b_i| ≤ (log x) k^{−2}"**: pdftotext 출력이 "(log x)k −2"로 나와 (log x)·k^{−2}로 읽었습니다(증명의 η = c_4/(k log k)와 정합). 다른 읽기((log x)^{k−2})는 증명과 맞지 않아 배제 [내 추론].
5. **Hd(q)의 Lean 공리화 시 권고 형태.** 문헌이 직접 주는 가장 강하고 깔끔한 문장은 (6.24)형입니다: `∀ q ≥ 3, ∀ a coprime q, ∀ m, ∃ x₀, ∀ x > x₀, ∃ n ∈ [x, 2x], (m+1)개의 연속 소수가 [qn, qn + log x]에 있고 모두 ≡ a (mod q)`. 이것을 공리로 두면 (Hd(q))와 (H3) 둘 다 Lean 안에서 순수 조합 논증으로 유도됩니다. 다만 "증명 안의 식"을 공리의 출처로 삼는 것이 불편하다면 (C4)의 Theorem 3.1 경로를 주석에 병기하십시오.
6. **서로 다른 잉여류 패턴**은 현재 어떤 단일 비상수 패턴도 무한성이 증명되어 있지 않습니다(Lau 2024 초록, LO-S 서론). 프로젝트가 이런 패턴에 의존한다면 그 가설은 문헌으로 뒷받침되지 않습니다.
7. Thorne의 "Bubbles of congruent primes" 출판 서지(저널/연도)는 확인하지 않았습니다(arXiv만 인용).

### 부록: 사용한 로컬 파일
- 추출 텍스트: 작성 당시 내려받은 PDF 의 pdftotext 추출본 (저장소에 없음): `{bft,maynard,maynard_pub,los,freiberg,thorne,yang,mpy,lau}.txt`
- 수치 검증 스크립트: 작성 당시의 임시 스크립트 `mod3.py` (저장소에 없음; 같은 계산은 `scripts/sw_triples.py` 가 한다) (`python3 -I mod3.py 200000`, `python3 -I mod3.py 1000000`)
