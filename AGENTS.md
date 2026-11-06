# 에이전트 작업 규칙

이 저장소는 Smarandache–Wellin 수 (소수를 차례로 이어 붙인 수) 에 관한 Lean 4 + Mathlib 연구 저장소다.
사람과 AI 에이전트 (GitHub Actions 의 Claude 포함) 가 모두 이 규칙을 따른다. 문서와 커밋 메시지는 한국어로 쓴다.

## 빌드와 검사

```bash
lake exe cache get                      # Mathlib 은 반드시 캐시로 받는다. 콜드 빌드는 1 시간 이상 걸린다
lake build                              # SmarandacheWellin/Audit.lean 이 모든 정리의 #print axioms 를 출력한다
lake exe mk_all                         # 새 .lean 파일을 만들었으면 루트 SmarandacheWellin.lean 의 import 를 갱신한다
python3 -I scripts/check_blueprint.py   # 블루프린트 ↔ Lean 소스 ↔ Audit 대응
python3 -I scripts/check_blueprint.py --write-decls /tmp/decls && lake exe checkdecls /tmp/decls
```

## 정책 (CI 가 강제한다)

1. **공리.** 모든 정리는 `propext`, `Classical.choice`, `Quot.sound` 의 부분집합만 쓴다.
   `sorry`, `admit`, `axiom` 선언, `native_decide` 는 라이브러리에 두지 않는다.
2. **증명되지 않은 가정은 이름 붙인 `def ... : Prop` 으로만.** 예: `SW.SameClassTriples3`, `SW.IntervalTriples`.
   조건부 정리는 그 정의를 명시적 인자로 받는다. 가정을 구조체 필드나 생성자에 몰래 묶어 넣지 않는다.
   새 가정 정의는 블루프린트에 `definition` 노드로 올린다.
3. **새 선언은 세 곳에 함께.** `SmarandacheWellin/*.lean` 의 새 `theorem`/`lemma`/`def` 는
   `SmarandacheWellin/Audit.lean` 의 `#print axioms` 줄과 `blueprint/src/content.tex` 의 노드
   (`\lean{SW.이름}`, `\leanok`, `\uses{...}`) 를 함께 갖는다. `scripts/check_blueprint.py` 가 검사한다.
4. **진술은 정확히.** 블루프린트의 자연어 진술은 Lean 진술과 가정·첨자·양화사가 같아야 한다.
   표기: `Nat.nth Nat.Prime n` 은 p_{n+1} (p_1 = 2).

## 저자와 검증자를 나눈다

- 저자 (사람이든 에이전트든) 는 "증명했다" 고 선언하지 않는다. 판정은 CI (Lean 커널, 공리 감사, checkdecls) 와
  별도의 리뷰가 한다.
- **에이전트가 여는 PR 은 다음을 바꾸지 않는다:** `docs/lemma-ledger.md`, `README.md`, `docs/research-plan.md`,
  `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `AGENTS.md`, `CLAUDE.md`, `scripts/check_blueprint.py`,
  `site/`, `.github/`, `.claude/`, `.mcp.json`. 장부의 상태 열은 사람이 머지 뒤에 고친다.
  CI 가 `claude/` 브랜치, 봇이 연 PR, 소유자가 아닌 사람이 연 PR 에 대해 이를 강제한다 (이름 변경 포함).
- main 은 ruleset 으로 보호된다: PR, CI 통과, 승인 1 건이 필요하고 저장소 관리자만 우회한다.
  에이전트는 자기 PR 을 승인하거나 머지할 수 없다.
- 에이전트 PR 은 draft 로 연다. 본문에 `lake build` 결과 요약과 새 정리의 `#print axioms` 출력을 붙인다.

## 수학적 맥락

- 목표 추측 (미해결): Wₙ 이 소수인 n 이 무한히 많다. 현재 연구 단위는 Q1 (유한 소수 집합이 모든 큰 항을 나눌 수
  없다) 이다. |S| = 1 은 무조건, |S| = 2 는 문헌 가정 (H3, IT(q)) 아래 Lean 으로 증명되어 있다.
- 의존 구조는 `blueprint/src/content.tex`, 상태의 세부와 실패 이유는 `docs/lemma-ledger.md`, 계획은
  `docs/research-plan.md` 에 있다. 문헌 근거는 `docs/references.md` 와 `docs/literature/`.
- 계산 실험 (`scripts/sw_*.py`) 은 증명이 아니다. 결과를 근거로 상태를 올리지 않는다.
