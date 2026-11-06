> 조사: 2026-11-06, 별도 조사 에이전트 작성. 핵심 근거 세 가지는 작성자와 다른 패스에서 1차 출처로 다시 확인했다.
> (1) gh-aw GA 2026-10-28, "generally available on github.com for GitHub Free, Team, and Enterprise", Copilot 엔진은 Copilot 라이선스 필요
> (github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available).
> (2) gh-aw 인증 문서: "CLAUDE_CODE_OAUTH_TOKEN is not supported by GitHub Agentic Workflows", `COPILOT_GITHUB_TOKEN` 은 개인 계정 소유
> fine-grained PAT 의 "Copilot Requests: Read" (github.github.com/gh-aw/reference/auth/).
> (3) claude-code-action: `CLAUDE_CODE_OAUTH_TOKEN` 은 "Pro, Max, Ultra, Team, and Enterprise plans", OAuth 면 구독 사용량으로 과금
> (code.claude.com/docs/en/github-actions).
> 나머지 수치·키 이름은 8절의 미검증 목록을 보라. 저장소는 아직 GitHub 원격이 없으므로 이 문서는 도입 전 판단 자료다.

# GitHub "Continuous AI" 조사 보고서 — Smarandache–Wellin Lean 4 + Mathlib 연구 저장소 적용 검토

- 작성일: 2026-11-06 (모든 상태·가격은 이 날짜에 조회한 1차 출처 기준)
- 조사 방법: GitHub Next, GitHub Docs, GitHub Changelog, gh-aw 공식 문서(github.github.com/gh-aw), githubnext/agentics 저장소, Anthropic Claude Code 문서(code.claude.com), leanprover/lean-action README, Lean Zulip 아카이브를 WebFetch로 직접 읽음. 2차 출처(블로그·뉴스)는 보조로만 사용하고 본문에 표시함.
- 표기: 인용은 원문 그대로(영어). "미검증"은 1차 출처에서 확인하지 못한 항목.

---

## 0. 한 줄 결론과 추천 워크플로 순위

**한 줄 결론.** "Continuous AI"는 제품이 아니라 GitHub Next가 2025-06에 붙인 범주 이름이고, 오늘(2026-11) 그것을 구현하는 중심 제품은 2026-10-28에 GA된 **GitHub Agentic Workflows(gh-aw)** 다. 이 저장소에는 (1) AI가 전혀 없는 순수 CI 게이트(`lake build` + 공리 감사 + `leanblueprint checkdecls` + sorry/axiom 검사 + 원장↔Lean 이름 일관성 스크립트)를 먼저 깔고, (2) 읽기 전용 AI 리뷰어·리포터(코멘트/이슈만 쓰는 safe-outputs)를 올린 뒤, (3) 마지막에 "lemma hunter"처럼 PR을 여는 에이전트를 CI 게이트와 사람 머지 뒤에 두는 순서가 맞다. 1인 개인 계정이면 **공개 저장소 + gh-aw + Claude 엔진(`ANTHROPIC_API_KEY`)** 또는 **Copilot Pro($10/월, 1,500 AI credits)** 가 현실적인 조합이고, Copilot이 없고 Claude 구독만 있다면 `anthropics/claude-code-action` + `CLAUDE_CODE_OAUTH_TOKEN`이 가장 싸다.

**추천 워크플로 순위 (도입 순서 = 순위).**

| 순위 | 워크플로 | 종류 | 트리거 | 허용되는 쓰기 | 엔진 | 판단 |
|---|---|---|---|---|---|---|
| 1 | PR 게이트 CI: `lake build` + 공리 감사 + no-sorry + `checkdecls` + 원장 일관성 스크립트 | 순수 CI (AI 없음) | push, pull_request | 없음 (check만) | 없음 | **필수.** 모든 에이전트의 "독립 검증자" 역할. 공개 저장소면 Actions 무료 |
| 2 | Blueprint 빌드 + GitHub Pages 배포 | 순수 CI | push main | `pages: write` | 없음 | **필수.** leanblueprint가 생성하는 템플릿 그대로 |
| 3 | AI 증명 리뷰어 (diff ↔ 원장/블루프린트 대조, 사용된 가설 H* 표시) | gh-aw 읽기 전용 | pull_request | `add-comment`, `create-pull-request-review-comment` | Claude 또는 Copilot | **강력 추천.** "저자 ≠ 검증자"를 자동화. PR당 수십 센트 수준(추정) |
| 4 | 문헌 감시 (arXiv/OEIS 주간 검색 → 이슈) | gh-aw 스케줄 | weekly | `create-issue` (max 1) | Claude (웹 검색 내장) | **추천.** 저렴. 단 AI 없이 Python+arXiv API로도 가능 |
| 5 | `/ask` 저장소 Q&A | gh-aw slash_command | `/ask` 코멘트 | `add-comment` | 아무거나 | **추천.** 저렴, 블루프린트·원장 탐색 편의 |
| 6 | 주간 연구 일지 요약 | gh-aw 스케줄 | weekly | `update-issue`(러닝 이슈 1개) | 아무거나 | 보통. 1인 저장소에서는 효용 제한적 |
| 7 | 실험 재현기 (`scripts/*.py` 소규모 재실행 ↔ `docs/experiments` 로그 비교) | 순수 CI 먼저, AI는 불일치 설명만 | monthly, workflow_dispatch | `create-issue` (불일치 시) | 아무거나 | 보통. 결정적 비교는 CI 스크립트로, AI는 보류 |
| 8 | Lemma hunter (원장의 "자연어 증명" 항목을 Lean으로 형식화 → `lake build`·공리 검사 통과 시에만 PR) | gh-aw 쓰기 | weekly + workflow_dispatch | `create-pull-request` (max 1, draft) | Claude(Opus) 또는 Copilot | **실험 가치 큼, 비용·위험 큼.** 마지막 단계. 회당 약 $7(Lean Squad 선례) |
| 9 | 문서↔Lean 이름 동기화 제안자 (1번 스크립트가 잡은 불일치를 고치는 PR) | gh-aw 쓰기 | 1번 실패 시 | `create-pull-request` | 아무거나 | 선택. 상태(status) 열은 절대 건드리지 않게 |
| 10 | 이슈 트리아지/라벨링 | gh-aw | issues | `add-labels` | 아무거나 | **불필요.** 외부 이슈가 생길 때까지 보류 |

---

## 1. Continuous AI란 무엇인가

### 1.1 정의 (1차 출처: GitHub Next 프로젝트 페이지, 2025-06 공개)

- 정의 원문: "all uses of automated AI to support software collaboration on any platform". 페이지는 이것이 "a category, rather than any single tool"이며, GitHub가 소유한 용어도 GitHub가 만든 기술도 아니라고 명시한다.
- 강조점: "Continuous AI is about using AI to enhance collaboration in software projects, not just individual productivity." 그리고 "Teams and organisations must be in control of the Continuous AI they use".
- 기대 수명: "We expect Continuous AI to be a story that runs for 30+ years at GitHub".
- Don Syme의 소개 포스트 "Introducing 'Continuous AI'"는 2025-06-19.

### 1.2 "레벨"/분류 체계가 있는가

- **GitHub Next 페이지에는 단계(level) 분류가 없다.** 대신 두 가지 분류 축만 제시한다.
  - 공통 특성: automatable, repetitive, collaborative, integrated, auditable, many variants, event-triggered.
  - 에이전트와의 관계: "can involve fully autonomous AI agents, but more often centres on scripted 'agent-like' AI workflows" (대개 사람의 감독을 유지).
  - "Horizon 2 and 3" (Three Horizons 프레임워크)를 언급하지만 설명은 없다.
- 웹에서 보이는 "Level 2 Continuous AI" 같은 표현은 제3자 블로그(adwaitx.com)에만 있고 GitHub 출처가 없다 → **미검증, 사용하지 말 것.**

### 1.3 용례 가족(패턴 이름)

Continuous Documentation / Continuous Code Improvement / Continuous Triage / Continuous Summarization / Continuous Fault Analysis / Continuous Quality / Continuous Team Motivation / Continuous Accessibility. 관련 포스트에서 Continuous Test Improvement(2025-08-27), Continuous Performance Improvement(2025-10-12), automated repository maintenance(2026-05-14)가 추가된다.

### 1.4 구현체의 변천

- 초기(2025): GitHub Actions + GitHub Models(`actions/ai-inference`, `gh models`), GenAIScript, `llm` 프레임워크.
- 2026-02-13: GitHub Agentic Workflows를 "the third leg of CI/CD"로 소개(GitHub 블로그; 원문 URL은 현재 404라 GitHub Next 페이지의 인용으로 확인).
- 2026-07-30: GitHub Models 완전 퇴역 → 현재 Continuous AI의 실질적 구현체는 **gh-aw + Copilot CLI(또는 BYO 에이전트)** 로 수렴.
- GitHub Next 프로젝트 페이지(agentic-workflows)의 현재 상태 표기: "is now generally available", stage "Product".

### 1.5 이 저장소와 직접 관련된 GitHub Next 선례: "Lean Squad" (Don Syme, 2026-04-20)

- 내용: Lean 4 형식 검증을 소프트웨어 저장소(raft-rs, quiche, PX4-Autopilot)에 "progressively and optimistically" 적용하는 gh-aw 워크플로. `gh aw add-wizard githubnext/agentics/lean-squad` 두 명령으로 설치.
- 동작: 8시간마다 실행, repo-memory에서 상태 복구, 가중 추첨으로 작업 2개 선택(Research, Informal Spec, Formal Spec, Implementation, Proof, Correspondence Review, Critique, CI, Report, Paper), **에이전트가 Actions 러너 안에서 elan을 설치하고 `lake build`를 돌린 뒤** PR 생성, 상태 이슈 갱신.
- 결과(raft-rs): 34회 실행(약 3주), 443 theorems, 23 Lean 파일. 비용 "approximately $7" per long run (Opus 4.6 기준) → 약 $240.
- 교훈 인용(이 저장소 정책과 정확히 맞닿음):
  - "The proofs are real. Every theorem is machine-checked by Lean's kernel."
  - "I don't, at some level, trust any of this besides the Lean proofs."
  - "Most theorems are glorified testing."
  - "In retrospect the automated 'critique' step I implemented was not strong enough." / "Lesson: repeated critique is needed, and final 'results' may rest on assumptions."
  - 에이전트가 `RaftReachable.step` 생성자에 5개 가설을 "as axioms"로 묶어 결과가 "conditionally correct only"가 된 사례 → **에이전트가 가설을 슬쩍 번들링하는 위험**은 실제로 관찰된 현상이다. 이 저장소의 "미증명 명제는 원장/블루프린트에 명시적 가설로만" 정책을 CI로 강제해야 하는 이유.
- 선행 선례 "Repo Assist"(2026-02-25): 일 1회 실행, safe outputs로 라벨(특정 것만)·코멘트·PR(회당 개수·제목 접두사 제한)·자기 PR에만 push, "never merges a PR". 핵심 문장: "guardrails mean you can automate." / "all AI outputs must be checked carefully for mistakes."

---

## 2. 기능별 표 (상태·플랜·비용·개인 계정 가용성·출처·날짜)

| # | 기능 | 상태 (날짜) | 필요 플랜 / 자격 | 개인 계정(조직 없음) | 공개/비공개 | 비용 | 핵심 출처 |
|---|---|---|---|---|---|---|---|
| 1 | **GitHub Agentic Workflows (gh-aw)** — `.github/workflows/*.md` → `gh aw compile` → `*.lock.yml` | Technical preview 2026-02-13 → Public preview 2026-06-11 → **GA 2026-10-28**: "generally available on github.com for GitHub Free, Team, and Enterprise" | Copilot 엔진: "Using the default GitHub Copilot CLI engine to power a workflow requires a Copilot license". BYO 엔진 가능: "You can use GitHub Copilot or bring your own coding agent" | **가능.** 인증 문서가 PAT 경로를 "personal repositories or when org billing is unavailable" 용도로 명시. `COPILOT_GITHUB_TOKEN`은 fine-grained PAT, Account permissions → "Copilot Requests: Read", 소유자는 user account여야 함. "OAuth user tokens are intentionally rejected", GitHub App 토큰도 불가 | 둘 다. FAQ: 비공개 "Yes."; 공개 저장소는 `min-integrity: approved` 자동 적용 | gh-aw 자체 무료 OSS("gh-aw itself is free and open source"). 비용 = Actions 분 + 추론. 추론은 AI Credits(AIC)로 집계, "One AIC equals $0.01 USD". 기본 상한 `max-ai-credits` 1,000/run, `max-daily-ai-credits` 5,000/day, threat detection 기본 400 AIC | 변경로그 2026-10-28; gh-aw docs reference/auth, reference/cost-management, reference/faq |
| 1a | gh-aw 엔진 목록 | Copilot(기본), Claude Code, Codex, Gemini CLI("deprecated"), Pi, Agy("experimental"), custom | Claude: `ANTHROPIC_API_KEY` 또는 Anthropic Workload Identity Federation. **"A Claude subscription OAuth login is not supported"** (`CLAUDE_CODE_OAUTH_TOKEN` 불가). 대안: `model: copilot/auto` + `permissions: { copilot-requests: write }`로 Copilot에 과금(조직 중앙 과금 필요). Codex: `OPENAI_API_KEY`/`CODEX_API_KEY`. Gemini: `GEMINI_API_KEY` | 개인: Claude API 키 또는 Copilot PAT | — | 엔진별 공급자 요금. 네이티브 웹 검색: Claude·Codex만("Copilot rejects `web-search:`") | gh-aw engines/claude, reference/engines, reference/auth |
| 2 | **Copilot cloud agent** (구 coding agent; 이슈를 Copilot에 assign → draft PR) | GA. "Copilot in the cloud" 경험은 2026-10-28부터 "available to users with a paid Copilot plan, subject to applicable organization and enterprise policies" | 모든 유료 Copilot 플랜("Copilot cloud agent is available for all paid Copilot plans"). Free 제외 | 가능 (Pro 이상) | 둘 다 (Actions 러너 기반). 쓰기 권한 없으면 읽기 전용 세션 | AI credits + Actions compute("cloud and GitHub Actions compute draw on the same monthly GitHub account allowance, separate from AI credits"). Actions 기반 세션 "maximum execution time of 59 minutes" | docs: concepts/agents/coding-agent/about-coding-agent; 검색 스니펫 docs cloud-agent-access |
| 2a | Copilot cloud agent 환경 커스터마이즈 | GA | — | — | — | `.github/workflows/copilot-setup-steps.yml`: "must contain a single `copilot-setup-steps` job", 적용되는 키는 `steps`, `permissions`, `runs-on`, `services`, `snapshot`, `timeout-minutes`(최대 59). 기본 브랜치에 있어야 동작. 방화벽 기본 허용목록 커스터마이즈 가능 | docs customize-the-agent-environment |
| 2b | 커스텀 지시 파일 | AGENTS.md 지원 2025-08-28 (coding agent) | — | — | — | 읽는 파일: 루트/중첩 `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/**.instructions.md`, `CLAUDE.md`, `GEMINI.md`. 우선순위는 문서에 없음 | changelog 2025-08-28 |
| 3 | **Copilot automations** (Agents 탭에서 스케줄/이벤트 자동화; Universe 2026 발표) | 발표 2026-10-28; 문서에 GA/preview 표기 없음 | Pro, Pro+, Max, Business, Enterprise (Free 없음) | 가능 (Pro 이상) | **비공개/내부만**: "Automations are not available in public repositories" | AI credits + Actions 분. 회당 최소 30 AIC 등 한도 설정 가능. 저장소 밖에 저장되어 Git 버전관리·PR 리뷰 불가("stored outside your repository") → 코드로 관리하려면 gh-aw | docs about-automations |
| 4 | **Agent HQ / 서드파티 코딩 에이전트 (Claude by Anthropic, OpenAI Codex)** — 이슈 Assignees에서 선택, PR에서 `@claude` | 발표 2025-10-28(Universe 2025, "mission control"); Public preview 2026-02-04 (Pro+, Enterprise) → **2026-02-26 Pro, Business 확대**. 플랜 페이지(2026-11 조회)에 여전히 "Third-party Agents (public preview)" | Pro 이상. "Access to Claude and Codex is fully included with your existing Copilot subscription" | 가능 (Pro: "Copilot coding agent settings"에서 Claude/Codex 토글) | 둘 다(미확인; cloud agent와 동일 인프라로 추정) | Preview 기간 "Each coding agent session consumes one premium request". 2026-06-01 AI credits 전환 후 환산은 **미확인** | changelog 2026-02-04, 2026-02-26; blog welcome-home-agents |
| 5 | Copilot custom agents (프로필 markdown + frontmatter) | GA (JetBrains/Xcode만 public preview) | 플랜 표기 없음 | — | — | — | docs about-custom-agents |
| 6 | **Copilot code review** | GA; Max 리뷰 레벨은 public preview | **Free 제외**("users on the Copilot Free plan, which does not include Copilot code review"). 자동 리뷰는 Pro/Pro+/Max | 가능. "In personal repositories, only the repository owner or a direct collaborator can request a review" | 둘 다 | AI credits + **2026-06-01부터 Actions 분** (비공개 저장소; 공개는 Actions 무료). 평균 Lite ≈ $0.25, Balanced(기본) ≈ $1.50, Max ≈ $10. 지시 파일: `.github/copilot-instructions.md`, `.github/instructions/`, `AGENTS.md` | docs concepts/agents/code-review; changelog 2026-04-27 |
| 7 | **GitHub Models / `actions/ai-inference`** | **퇴역.** 신규 중단 2026-06-16, 완전 퇴역 2026-07-30: "The playground, model catalog, inference API, and bring your own key (BYOK) are no longer available" | — | — | — | `actions/ai-inference`는 현재 "provider: Only `copilot` is supported" — Copilot CLI를 러너에 설치하고 `COPILOT_GITHUB_TOKEN` 필요. 사실상 Copilot CLI 래퍼 | changelog 2026-07-30; actions/ai-inference README |
| 8 | **Copilot CLI in Actions** (`copilot -p`) | GA | "All plans include Copilot CLI and the Copilot app"(Free 포함). PAT "Copilot Requests" 필요 | 가능 | 둘 다 | AI credits + Actions 분. GitHub 문서 자체가 "Agentic workflows ... include additional guardrails suited for automated environments"라며 대부분의 자동화에 gh-aw 권장 | docs automate-with-actions |
| 9 | **`anthropics/claude-code-action@v1`** (Anthropic 측 대응물) | v1 GA (beta에서 마이그레이션 안내 존재) | Claude API 키, 또는 **`CLAUDE_CODE_OAUTH_TOKEN`: "available on Pro, Max, Ultra, Team, and Enterprise plans"** (`claude setup-token`), WIF, Bedrock/Vertex/Foundry | 가능 (저장소 admin 필요) | 둘 다. 공개 저장소에서 fork PR에는 secrets 미제공 | Actions 분 + API 토큰("If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing"). `--max-turns`로 제한 | code.claude.com/docs/en/github-actions; claude-code-action docs/security.md |
| 10 | Claude Code **Code Review** (Anthropic 호스팅, 워크플로 파일 불필요) | GA | **Team, Enterprise 전용** | 불가 (개인 플랜은 로컬 `/code-review`) | — | 리뷰는 Anthropic 인프라에서, 코드를 빌드하지 않음("without building or running your code") → Lean 검증 불가 | code.claude.com/docs/en/code-review |
| 11 | Claude Code **scheduled tasks (구 routines)** | research preview | Pro, Max, Ultra, Team, Enterprise | 가능 (개인 claude.ai 계정 소속; 커밋이 사용자 이름으로 남음) | — | 구독 사용량. 시간당 100 scheduled runs/계정 등. GitHub 이벤트 트리거(PR opened 등) 지원 | code.claude.com/docs/en/routines |
| 12 | **Copilot 개인 플랜** (2026-11 조회 docs plans) | 사용량 기반 과금 2026-06-01. 가입 일시 중단 2026-04-20 → **2026-06-17부터 점진 재개** | Free: AI Credits 할당 있음(수치 미표기), CLI 포함, cloud agent·code review 없음. **Pro $10/월, 1,500 AIC(1,000 base + 500 flex)**, Pro+ $39/7,000, Max $100/20,000, Business $19/seat/1,900, Enterprise $39/seat/3,900 | — | — | 1 AIC = $0.01. 코드 완성은 무과금. Opus 모델은 2026-04-20부터 Pro에서 제외("Opus models are no longer available on Copilot Pro") | docs copilot/get-started/plans; changelog 2026-04-20, 2026-06-01, 2026-06-17 |
| 13 | **GitHub Actions 한도** | — | — | — | **공개 저장소 표준 러너 무료**. 비공개: Free $12/월 포함(Linux 2-core $0.006/분 → 약 2,000분; 내 환산), Pro $18(약 3,000분) | 캐시 10 GB/repo, 아티팩트 Free 500 MB, job 6시간, 동시 job Free 20. 러너 사양: **공개 4 vCPU/16 GB/14 GB SSD, 비공개 2 vCPU/8 GB/14 GB SSD**. Larger runners는 Team/Enterprise 조직 전용 | docs about-billing-for-github-actions, reference/limits, reference/runners |

---

## 3. 이 저장소를 위한 후보 워크플로와 판단

공통 전제: 저장소 규모(53 정리, 1인)와 정책(공리 propext/Classical.choice/Quot.sound만, sorry·axiom·native_decide 금지, 저자≠검증자, 가설은 원장/블루프린트에만)을 기준으로 판단. 비용 추정치는 토큰 단가에서 계산한 내 추정이고 측정값이 아니다.

### (a) PR 게이트 CI — 순수 CI, 1순위, 필수

- 트리거: `push`(main), `pull_request`.
- 하는 일: `jlumbroso/free-disk-space` → `actions/checkout` → `leanprover/lean-action` (`build: true`, `use-mathlib-cache: auto` → `lake exe cache get`, `.lake` GitHub 캐시) → **공리 감사**: lean-action의 `axiom-audit` 입력(허용목록 옵션 있음; 정확한 키 철자는 README에서 재확인 필요) 또는 자체 스크립트가 `#print axioms`를 전수 실행해 허용 집합 외 공리 발견 시 실패 → `grep -rnE "sorry|native_decide|^\s*axiom "` 라이브러리 디렉터리(주석 제외 처리) → `leanblueprint checkdecls` (docgen-action이 수행) → **원장 일관성 스크립트** `scripts/check_ledger.py`: `docs/lemma-ledger.md`에서 상태가 "Lean 검증"인 행의 Lean 이름이 실제 선언으로 존재하는지, README 상태표의 이름이 존재하는지, 블루프린트의 `\lean{}`/`\leanok`와 일치하는지 검사.
- 엔진: 없음. 쓰기: 없음(check run만).
- 저자≠검증자: 이 워크플로 자체가 모든 사람·에이전트 저자에 대한 **독립 검증자**다. 이후 모든 AI 워크플로는 "CI가 통과해야만 의미 있음"을 전제로 설계한다.
- 비용: 공개 저장소면 Actions 무료. 비공개면 회당 약 5~15분 × 월 실행 횟수(Free $12 ≈ 2,000분이면 월 100회 이상 가능).
- 판단: **필수.** AI 이전에 이것이 없으면 아래 어느 것도 안전하지 않다.

### (b) AI 증명 리뷰어 — gh-aw 읽기 전용, 2순위(AI 중 1순위), 강력 추천

- 트리거: `pull_request` (`opened`, `synchronize`, `ready_for_review`). 기본값으로 fork PR 차단("`pull_request` workflows block forks by default").
- 하는 일: `.lean` diff와 `docs/lemma-ledger.md`, `blueprint/`를 읽고 (1) 정리 서술이 원장/블루프린트의 문장과 같은지(**statement drift** 검출), (2) 사용된 가설(H3 등)을 열거하고 그것이 블루프린트에 명시적 가설로 등록돼 있는지, (3) `sorry`/`axiom`/`native_decide`/비정상적 `maxHeartbeats`/큰 `decide` 사용 여부, (4) 문서(README 표, 원장 상태)가 Lean 이름과 일치하는지 점검해 **체크리스트 코멘트**를 단다. "verified"라는 단어를 쓰지 않고 "CI 결과를 확인하라"고만 말하도록 프롬프트에 명시.
- 엔진: Claude(`engine: claude`, 모델 sonnet) 또는 Copilot. 저자 에이전트(h)가 Claude Opus면 리뷰어는 다른 모델(예: Copilot의 GPT 계열)을 쓰는 것이 "저자≠검증자"의 취지에 더 맞다.
- 허용 쓰기(safe-outputs): `add-comment: {max: 1}`, `create-pull-request-review-comment: {max: 10}`. `edit`·`create-pull-request` 없음. `permissions: read-all`. bash는 읽기 명령만(`cat`, `grep`, `git diff`, `git log`).
- 저자≠검증자: 리뷰어는 코드를 못 바꾼다. 리뷰는 참고 의견이고 머지 결정은 사람이 한다(threat detection 문서: "a warning marker or label alone is not a platform approval gate" → 머지 보호는 ruleset으로).
- 비용·위험: 회당 수십 센트 추정(Sonnet, diff 수 KB). `max-ai-credits: 200`($2)로 상한. 위험은 PR 본문 주입이지만 같은 저장소 PR만 허용되고 공개 저장소면 `min-integrity: approved` 자동.
- 판단: **강력 추천.** 1인 연구 저장소에서 가장 부족한 것이 "두 번째 눈"이다.

### (c) Lemma hunter — gh-aw 쓰기, 8순위(마지막 단계), 실험 가치 큼

- 트리거: `schedule: weekly` + `workflow_dispatch`. (`stop-after: +30d`로 실험 기간 제한 가능.)
- 하는 일: 원장에서 상태 "자연어 증명"(또는 "계산상 지지"면서 진술이 작은 것) 중 하나를 고르고(repo-memory에 시도 이력 저장, 같은 항목 반복 금지), 새 파일(예: `SW/Agent/<Name>.lean`)에 Lean 증명을 쓰고, `lake build`와 공리 검사 스크립트를 돌린 뒤 **둘 다 통과할 때만** PR을 연다. PR 본문에 `#print axioms` 출력과 빌드 로그 요약을 반드시 포함. **`docs/lemma-ledger.md`의 상태 열과 README 표는 절대 수정하지 않는다**(상태 변경은 사람이 머지 후 별도 커밋으로). 실패 시 PR을 열지 않고 repo-memory에 기록(또는 `noop`).
- 엔진: Claude(Opus) 권장 — Lean Squad도 Opus 4.6 기준 비용을 썼고 Pro 플랜 Copilot에는 Opus가 없다. Copilot Pro+면 Copilot도 가능.
- 허용 쓰기: `create-pull-request: {max: 1, draft: true, title-prefix: "[lemma-hunter] ", labels: [agent]}`. `max-patch-size` 제한. `threat-detection: {continue-on-error: false}`(strict).
- 저자≠검증자: 에이전트=저자. 검증은 (a) CI 게이트 + (b) AI 리뷰어 + 사람 머지. 원장 상태 갱신은 머지 뒤 사람이(또는 (i) 워크플로가 PR로) 수행 → 에이전트가 "증명했다"고 선언할 경로가 없다.
- 비용·위험: Lean Squad 선례 "approximately $7" per long run(Opus) → 주 1회면 월 약 $30. Actions 러너 시간 30~90분/회(Mathlib 캐시 포함). 위험: (1) 서술 변형(쉬운 명제로 바꿔 증명) → 리뷰어 (b)와 `check_ledger.py`가 진술 일치 검사, (2) 가설 번들링(Lean Squad의 `RaftReachable.step` 사례) → "메인 라이브러리 네임스페이스의 정리는 H* 가설을 인자로 받을 수 없고, 조건부 결과는 `SW/Conditional/` 아래에만" 같은 규칙을 CI로 강제, (3) 비용 폭주 → `max-ai-credits: 800`, `max-daily-ai-credits`, `timeout-minutes: 120`, `concurrency`.
- 판단: **실험으로서 가치가 가장 크다**(저장소의 연구 질문 자체가 "얼마나 자동 형식화되나"). 그러나 (a)(b)와 ruleset 없이 켜면 안 된다.

### (d) 문헌 감시 — gh-aw 스케줄, 4순위, 추천

- 트리거: `schedule: weekly`.
- 하는 일: arXiv API(`export.arxiv.org`)·OEIS(`oeis.org`)를 "Smarandache–Wellin", "consecutive primes" + "residue classes"/"same class mod", "Banks Freiberg Turnage-Butterbaugh", "prime concatenation" 등으로 검색, `docs/references.md`와 repo-memory의 본 목록과 대조해 새 항목만 이슈 1개로 보고.
- 엔진: Claude(네이티브 웹 검색·`web-fetch` 지원; Copilot은 `web-search:` 거부).
- 허용 쓰기: `create-issue: {max: 1, title-prefix: "[lit-watch] ", deduplicate-by-title: true}`. `network.allowed`: `export.arxiv.org`, `arxiv.org`, `oeis.org`(+ 필요 시 `api.semanticscholar.org`).
- 저자≠검증자: 쓰기는 이슈뿐. 참고문헌 반영은 사람이.
- 비용: 회당 $0.2~1 추정. 위험: 낮음(외부 페이지 내용이 프롬프트 주입원이 될 수 있으나 쓰기가 이슈 1개로 제한).
- 판단: **추천.** 단, 결정적 부분(API 질의·신규 ID 판별)은 Python 스크립트로, AI는 "관련성 요약"만 맡기면 더 싸고 재현 가능하다.

### (e) 실험 재현기 — 순수 CI 먼저, 7순위

- 트리거: `schedule: monthly` 또는 `workflow_dispatch`, 그리고 `scripts/**` 변경 PR.
- 하는 일: `python -I scripts/<x>.py --n <small>`을 돌려 `docs/experiments/` 로그의 소규모 구간과 수치 비교(결정적). 불일치 시 실패/이슈. AI는 불일치의 원인 설명에만 쓰고 처음엔 생략.
- 판단: **보통.** 가치는 있으나 AI가 필요 없다. (a)에 포함하거나 별도 CI로.

### (f) Blueprint 빌드·Pages 배포 — 순수 CI, 2순위, 필수

- leanblueprint가 생성하는 템플릿(조회한 부분): `jlumbroso/free-disk-space` → `actions/checkout`(`fetch-depth: 0`) → `leanprover/lean-action`(`build`, `lint`, `mk_all-check`) → `leanprover-community/docgen-action`(`blueprint: true`)이 PDF/HTML/의존성 그래프/`checkdecls`/Pages 배포를 담당. permissions: `contents: read`, `pages: write`, `id-token: write`. 커뮤니티 사례(vidick/MIPRE-formalization PR #330)에서 `checkdecls` 단계가 실패하면 사이트가 stale 상태로 남는 문제가 보고됨 → PR에서도 build+checkdecls만 돌리고 배포는 main에서만.
- 주의: **GitHub Free 플랜에서 Pages는 공개 저장소에서만** 가능(일반 지식, 오늘 재검증하지 않음) → 비공개로 가면 Pro($4/월) 필요.
- 판단: **필수.** 블루프린트 도입 작업과 함께 간다.

### (g) 주간 연구 일지 — gh-aw 스케줄, 6순위

- 커밋·PR·원장 diff·실험 로그 변경을 읽어 러닝 이슈 1개를 `update-issue`로 갱신(Repo Assist의 월간 리포트 패턴). 비용 저렴. 1인 저장소에서는 "연구 노트 자동 초안" 정도의 가치.
- 판단: 보통. Phase 2 후반 선택.

### (h) `/ask` 저장소 Q&A — gh-aw slash_command, 5순위, 추천

- `slash_command: ask`, `roles` 기본값 `[admin, maintainer, write]`(1인 저장소면 본인만). 블루프린트·원장·Lean 소스를 읽고 코멘트로 답("H3를 쓰는 정리 목록은?", "이 보조정리는 어디서 쓰이나?"). `add-comment: {max: 1}`.
- 판단: 추천. 저렴하고 즉시 효용.

### (i) 문서↔Lean 동기화 제안자 — 9순위, 선택

- (a)의 `check_ledger.py`가 실패하면 이름 불일치만 고치는 PR을 제안. 상태 열은 금지. 판단: 선택.

### (j) 이슈 트리아지 — 10순위, 불필요

- 외부 기여자가 없는 동안은 가치 없음. 공개 전환 후 스팸/이슈가 생기면 `githubnext/agentics/issue-triage`를 그대로 추가.

### 보조 수단: Copilot cloud agent / Claude(Agent HQ)에 이슈 assign

- "Continuous"는 아니지만 **수동 on-demand lemma hunter**로 유용. `copilot-setup-steps.yml`에 elan 설치 + `lake exe cache get`을 넣으면 에이전트가 `lake build`를 돌릴 수 있다. 세션 최대 59분, 유료 Copilot 필요. Pro 플랜이면 Claude 에이전트도 같은 방식으로 assign 가능(2026-02-26부터).

### gh-aw 프론트매터 스케치 (키 이름은 2026-11 문서 기준; `gh aw compile --verbose`로 검증 필요)

(b) 증명 리뷰어:

```markdown
---
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
permissions: read-all
engine: claude
timeout-minutes: 15
max-ai-credits: 200
tools:
  github:
    toolsets: [default]
  bash: ["cat", "grep", "git diff:*", "git log:*", "ls", "head", "wc"]
safe-outputs:
  add-comment:
    max: 1
  create-pull-request-review-comment:
    max: 10
---
You are a verifier, not an author. Read the .lean diff, docs/lemma-ledger.md and blueprint/src/*.tex ...
Never say "verified"; say what CI must confirm. List every hypothesis (H1, H2, H3 ...) the diff uses ...
```

(c) Lemma hunter:

```markdown
---
on:
  schedule: weekly
  workflow_dispatch:
  stop-after: +30d
permissions: read-all
engine:
  id: claude
  model: opus
timeout-minutes: 120
max-ai-credits: 800
network:
  allowed: [defaults, github, lean, "cache.mathlib.org", "lakecache.blob.core.windows.net"]
tools:
  edit:
  bash: [":*"]
  github:
    toolsets: [default]
  repo-memory:
steps:
  - name: Install Lean and warm Mathlib cache
    run: |
      curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
      echo "$HOME/.elan/bin" >> "$GITHUB_PATH"
      lake exe cache get
      lake build
cache:
  key: lake-${{ runner.os }}-${{ hashFiles('lake-manifest.json') }}
  path: .lake/build
safe-outputs:
  create-pull-request:
    max: 1
    draft: true
    title-prefix: "[lemma-hunter] "
    labels: [agent]
  threat-detection:
    continue-on-error: false
---
Pick ONE ledger item with status 자연어 증명 ... Run `lake build` and the axiom check ...
Create a pull request ONLY if both pass. NEVER edit docs/lemma-ledger.md status or README tables ...
```

(`steps:`의 사전 단계가 에이전트 전에 결정적으로 실행된다는 점은 frontmatter 문서의 "pre-steps, steps, pre-agent-steps, post-steps ... run deterministic work before or after agentic execution"에 근거. Lean Squad는 에이전트 본문 안에서 elan을 설치하지만, 사전 단계로 빼는 편이 재현성과 비용 면에서 낫다.)

---

## 4. Actions에서 Lean을 돌릴 때의 제약

### 4.1 Mathlib 캐시 패턴 (`leanprover/lean-action`)

- README: "lean-action runs `lake exe cache get` with `MATHLIB_CACHE_GET_URL` set to `https://cache.mathlib.org/mathlib4`." 기본 `use-mathlib-cache: auto`(Mathlib 의존성 자동 감지). "Project must be downstream of Mathlib to use the Mathlib cache."
- `.lake` 전체를 `actions/cache`로 캐시(키: OS/arch/lake manifest/commit hash, 폴백 키는 commit 제외). "The GitHub cache is separate from the Mathlib cache." `use-github-cache: false`로 끌 수 있음.
- 추가 검사 입력: `mk_all-check`, `leanchecker`, `nanoda`, `axiom-audit`(허용목록·루트 옵션). 경고: Mathlib 의존 프로젝트에서 leanchecker는 "can exhaust the memory of a GitHub-hosted runner" → `LEAN_NUM_THREADS: "1"`.

### 4.2 크기·시간 수치 (Lean Zulip "Cache on GitHub Actions", 2025-11-16, SnO2WMaN 보고)

| 항목 | 값 |
|---|---|
| `.lake` 전체 | 8.2 GB (packages 6.4 GB, 그중 mathlib 5.7 GB; build 1.8 GB; bin 1.2 GB) |
| 압축된 GitHub 캐시 항목 | 약 4 GB → 10 GB 할당량에 2~3개만 들어감 |
| 러너 디스크 | 14 GB SSD → "zstd: error 70 ... No space left on device" 발생 |
| 캐시 없는 전체 빌드 | 약 50분 (해당 프로젝트; 네이티브 `.o` 컴파일은 캐시 대상 아님) |
| 캐시 있는 빌드 | 제3자 액션 README의 주장 "turns a ~1h cold build into ~5 minutes" (독립 측정 아님) |

- 결론: **콜드 빌드는 사실상 불가능**(2-core 비공개 러너면 더 느림). `lake exe cache get`은 필수이고, 디스크 확보(`jlumbroso/free-disk-space`, leanblueprint 템플릿에 이미 포함)와 캐시 범위 축소(`.lake/build`만 GitHub 캐시, Mathlib은 매번 cache get)가 필요하다.
- 알려진 실패 모드: 툴체인 다운로드 타임아웃(2025-08 Zulip: "That download is the one failing"), 네트워크 오류 → NNG4 저장소의 재시도 패턴(`lake exe cache get || (sleep; retry)`), 2026-01 Zulip에서 캐시 백엔드 전환 논의(`MATHLIB_CACHE_USE_CLOUDFLARE`) → **방화벽 허용목록의 호스트명은 첫 실행 후 `gh aw audit`로 확인해 조정**.

### 4.3 gh-aw 에이전트가 `lake`를 돌릴 수 있는가 — 예

- 실행 위치: 에이전트 job은 Actions 러너 위의 AWF 컨테이너. "$HOME, $GITHUB_WORKSPACE, and /tmp" 읽기·쓰기 가능, 호스트 바이너리와 setup-action 런타임 사용 가능(PATH 복원). Docker 소켓은 숨김(필요 없음).
- 도구: `bash: [":*"]`가 있어야 `lake`·`elan` 실행 가능(기본 안전 집합은 `echo, printf, ls, pwd, cat, head, tail, grep, wc, sort, uniq, date, yq`뿐). `edit:`로 파일 수정.
- 네트워크: 기본 `network: defaults`는 패키지 소스가 막힘. `lean` 생태계 식별자가 존재("Lean packages (`lean-lang.org`, `reservoir.lean-lang.org`)"), elan 설치 스크립트는 `raw.githubusercontent.com`/`github.com` → `github` 식별자, Mathlib 캐시는 `cache.mathlib.org`(lean-action 기본) 추가. Lean Squad 워크플로의 실제 허용목록: `defaults, github, rust, lean, latex, ocaml, arxiv.org, leanprover-community.github.io, leanlang.org, lakecache.blob.core.windows.net, reservoir.leancache.cloud`.
- 시간: `timeout-minutes` 기본 20분(에이전트 job 60분) → 90~120으로 상향(Lean Squad: 120). 메모리 초과는 exit 137.
- 사전 단계(`steps:`)와 `cache:`(actions/cache 문법)로 elan 설치·cache get·`.lake/build` 캐시를 결정적으로 처리 가능.
- 선례: Lean Squad 본문이 "The Lean toolchain MUST be successfully installed before you write, modify, or submit any `.lean` files."라 하고 `elan-init.sh`로 설치 후 `lake build 2>&1 | tee ...`를 실행 → 동작 증명.

### 4.4 다른 경로

- `anthropics/claude-code-action`: 일반 step이므로 **그 앞에 lean-action(또는 수동 elan + cache get)을 두면** Claude가 `lake build`를 쓸 수 있다. gh-aw보다 가드레일은 적지만 설정이 가장 단순.
- Copilot cloud agent: `copilot-setup-steps.yml`에서 설치(최대 59분 제한에 cache get 시간 포함).
- 공개 저장소의 schedule 워크플로는 60일간 저장소 활동이 없으면 자동 비활성화(Claude 문서 언급; GitHub 일반 규칙).

---

## 5. 위험과 가드레일

| 위험 | gh-aw 가드레일 (문서 인용) | claude-code-action 가드레일 | 이 저장소에서 추가로 할 것 |
|---|---|---|---|
| 이슈/PR 본문을 통한 프롬프트 주입 | integrity filtering: 공개 저장소는 "the runtime automatically applies `min-integrity: approved`"; 콘텐츠 정화(@mention 무력화, URI 필터, 제어문자 제거); `on.roles` 기본 `[admin, maintainer, write]`; `pull_request`는 fork 기본 차단; 구 `lockdown: true`는 "Replace `lockdown: true` with `min-integrity: approved`"로 대체됨 | "The action can only be triggered by users with write access"; 봇 기본 차단(`allowed_bots`); HTML 주석·보이지 않는 문자 제거; `include_comments_by_actor` | 1인 저장소라 트리거 주체가 본인뿐. 공개 전환 후에도 roles 기본값 유지 |
| 에이전트가 원장/README를 고쳐 "증명됨"이라 주장 | 에이전트 job은 "read-only GitHub permissions and receives no repository secrets automatically"; 쓰기는 safe-outputs → 별도 job → PR; threat detection(warn 기본, `continue-on-error: false`면 strict) | 기본값 "Claude does not create pull requests automatically"(브랜치 + 링크) | (1) main ruleset: PR 필수 + 상태 검사 필수 + force push 금지, (2) CODEOWNERS로 `docs/lemma-ledger.md`, `README.md`, `blueprint/` 보호, (3) `check_ledger.py`가 "Lean 검증" 상태 ↔ 실제 선언·공리 검사 결과를 대조, (4) 프롬프트에 상태 열 수정 금지, (5) 조건부 정리의 네임스페이스 규칙 |
| 비밀 유출 | 비밀은 safe-output job에만; AWF egress 허용목록; "Detection is defense in depth, not proof" | `show_full_output` 기본 off("These logs are publicly visible in GitHub Actions for public repositories!"); `allowed_non_write_users`와 PAT 조합 금지 | `COPILOT_GITHUB_TOKEN` PAT는 "Copilot Requests: Read"만; `ANTHROPIC_API_KEY`는 월 한도 설정한 워크스페이스 키 |
| 비용 폭주 | `max-ai-credits`(기본 1,000), `max-daily-ai-credits`(5,000), `stop-after`, `max-turns`(기본 500), `timeout-minutes`, `concurrency`, `gh aw forecast`; 권고 "Prefer schedules or `workflow_dispatch` over high-frequency triggers like `push`" | `--max-turns`, job timeout, concurrency | 공개 저장소로 Actions 비용 0. 리뷰어 200 AIC, hunter 800 AIC 상한. Copilot이면 플랜 budget 설정 |
| 서술 변형·가설 번들링·"glorified testing" (Lean Squad 교훈) | 없음(도메인 문제) | 없음 | 리뷰어(b)가 진술을 원장과 축자 대조; `#print axioms` + `axiom`/`sorry` grep; 블루프린트 `\uses` 그래프에서 H* 노드 의존을 표시; 반복 critique |
| threat detection의 한계 | "a warning marker or label alone is not a platform approval gate"; 큰 패치는 타임아웃·오탐 | — | 머지 보호는 ruleset으로만 |
| gh-aw 자체의 빠른 변화 | 주간 릴리스(2026-09 v0.89.x), 키 이름 변경 이력(lockdown → min-integrity, MCP 설정 위치 변경), 취약점으로 `>= 0.83.3, < 0.85.4` 회수 | — | `gh aw upgrade`/`gh aw update`를 수동으로, `.lock.yml`을 PR로 리뷰 |

---

## 6. 3단계 도입 계획과 파일 목록

### Phase 1 — 기반 CI (AI 없음, 비용 0, 1~2일)

추가 파일:
- `.github/workflows/ci.yml` — free-disk-space → checkout → `leanprover/lean-action`(build, mathlib cache, `axiom-audit` 허용목록 `propext`, `Classical.choice`, `Quot.sound`) → no-sorry/axiom/native_decide grep → `python -I scripts/check_ledger.py` → (선택) 소규모 실험 재현.
- `.github/workflows/blueprint.yml` — leanblueprint 생성 템플릿(lean-action + docgen-action, Pages 배포는 main만).
- `scripts/check_ledger.py` — 원장·README·블루프린트의 Lean 이름 존재·상태 일관성 검사(블루프린트 `checkdecls`와 역할 분담).
- `AGENTS.md` (루트) — 공리 정책, sorry 금지, 원장 상태 열 규칙, 빌드 명령, "저자≠검증자" 프로토콜, 조건부 정리 네임스페이스 규칙. `CLAUDE.md`는 `AGENTS.md`를 참조하는 한 줄 파일(또는 심링크). Copilot용 `.github/copilot-instructions.md`는 중복이므로 생략 가능(cloud agent·code review 모두 `AGENTS.md`를 읽음).
- `CODEOWNERS`, main 브랜치 ruleset(PR 필수, 상태 검사 `ci` 필수, 승인 1 — 1인 저장소에선 자기 승인 불가하므로 "상태 검사 필수"가 실질 게이트).

결정 사항: **공개 vs 비공개.** 추천은 공개 — Actions 무료, 러너 4 vCPU/16 GB, Pages 무료, gh-aw 무결성 필터 자동, Copilot automations만 불가(필요 없음). 비공개를 택하면 GitHub Pro($4/월) + Actions 2,000분/월 안에서 운영(Mathlib 캐시 포함 회당 10~15분 → 월 100회 남짓).

### Phase 2 — 읽기 전용 AI (코멘트·이슈만)

추가 파일(gh-aw 경로):
- `.github/workflows/proof-reviewer.md` + `.lock.yml`
- `.github/workflows/lit-watch.md` + `.lock.yml`
- `.github/workflows/ask.md` + `.lock.yml`
- (선택) `.github/workflows/research-journal.md`
- `.github/mcp.json`(MCP를 쓸 때만)
- 저장소 secret: `ANTHROPIC_API_KEY` 또는 `COPILOT_GITHUB_TOKEN`(fine-grained PAT, Copilot Requests: Read).

대안(gh-aw 없이, Claude 구독만 있을 때):
- `.github/workflows/claude-review.yml` — `anthropics/claude-code-action@v1`, `on: pull_request`, permissions `contents: read`, `pull-requests: read`, `issues: read`, `id-token: write`, secret `CLAUDE_CODE_OAUTH_TOKEN`(`claude setup-token`, Pro/Max 가능). 앞에 lean-action을 두면 Claude가 빌드도 확인할 수 있다. 가드레일(safe outputs, 방화벽, threat detection)은 없으므로 쓰기 권한을 주지 말 것.

결정 사항: **엔진과 구독.**
- Claude API 키(종량제): gh-aw의 모든 가드레일 + 웹 검색 + Opus 선택 가능. 월 수 달러~수십 달러.
- Copilot Pro($10, 1,500 AIC): PAT 경로. Opus 없음(2026-04-20부터), 웹 검색 없음. 리뷰어·/ask·일지에는 충분.
- Claude 구독 OAuth: gh-aw에서는 불가, claude-code-action에서만 가능.

### Phase 3 — 쓰기 가능 에이전트 (PR 게이트 뒤)

추가 파일:
- `.github/workflows/lemma-hunter.md` + `.lock.yml` (3절 스케치; strict threat detection, draft PR, 상한).
- (선택) `.github/workflows/copilot-setup-steps.yml` — Copilot cloud agent/Claude 에이전트에 이슈를 assign해 수동으로 돌릴 때.
- (선택) `.github/workflows/ledger-sync.md`.
- 원장 상태 갱신 절차 문서화: "머지 → 사람이 `#print axioms` 재확인 → 상태 열 변경 커밋"(또는 Phase 1 스크립트가 상태를 자동 산출하도록 전환해 상태 열 자체를 생성물로 만드는 것도 방법).

결정 사항: 실험 기간(`stop-after`), 주간 예산 상한, 조건부 정리 네임스페이스 규칙의 구체적 형태, Opus 사용 여부.

---

## 7. 출처 (조회일 2026-11-06)

GitHub Next / 연구 포스트
- Continuous AI 프로젝트 페이지: https://githubnext.com/projects/continuous-ai/ (published Jun 2025)
- Introducing "Continuous AI" (2025-06-19): https://githubnext.com/posts/dsyme-introducing-continuous-ai/
- Agentic Workflows 프로젝트 페이지(GA 표기): https://githubnext.com/projects/agentic-workflows/
- Lean Squad (2026-04-20): https://dsyme.net/2026/04/20/lean-squad-automated-software-verification-with-near-zero-human-labour/ , 워크플로 문서 https://github.com/githubnext/agentics/blob/main/docs/lean-squad.md , 소스 https://raw.githubusercontent.com/githubnext/agentics/main/workflows/lean-squad.md
- Repo Assist (2026-02-25): https://dsyme.net/2026/02/25/repo-assist-a-repository-assistant/
- Agentics 예제 모음: https://github.com/githubnext/agentics

GitHub Changelog / Blog
- Agentic Workflows GA (2026-10-28): https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/
- Agentic Workflows public preview (2026-06-11): https://github.blog/changelog/2026-06-11-github-agentic-workflows-is-now-in-public-preview/
- Universe 2026 (2026-10-28): https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/
- Agent HQ 발표 (2025-10-28): https://github.blog/news-insights/company-news/welcome-home-agents/
- Claude/Codex public preview (2026-02-04): https://github.blog/changelog/2026-02-04-claude-and-codex-are-now-available-in-public-preview-on-github/
- Claude/Codex → Pro, Business (2026-02-26): https://github.blog/changelog/2026-02-26-claude-and-codex-now-available-for-copilot-business-pro-users/
- 개인 플랜 변경·가입 중단 (2026-04-20): https://github.blog/changelog/2026-04-20-changes-to-github-copilot-plans-for-individuals/
- Code review가 Actions 분 소모 (2026-04-27): https://github.blog/changelog/2026-04-27-github-copilot-code-review-will-start-consuming-github-actions-minutes-on-june-1-2026/
- 사용량 기반 과금 (2026-06-01): https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/
- 개인 플랜 가입 재개 (2026-06-17): https://github.blog/changelog/2026-06-17-copilot-individual-plan-sign-ups-are-reopening/
- GitHub Models 퇴역 (2026-07-30): https://github.blog/changelog/2026-07-30-github-models-is-now-retired/
- AGENTS.md 지원 (2025-08-28): https://github.blog/changelog/2026-06-23-copilot-coding-agent-now-supports-agents-md-custom-instructions/ (페이지 본문 날짜는 2025-08-28)

GitHub Docs
- Copilot 플랜 비교: https://docs.github.com/en/copilot/get-started/plans
- 모델·가격(AI credits, 코드 리뷰 비용): https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
- 레거시 premium requests: https://docs.github.com/en/billing/concepts/product-billing/github-copilot-premium-requests
- About GitHub Agentic Workflows: https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows
- Copilot automations: https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations
- Copilot cloud agent 개요: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent
- Cloud agent 환경 커스터마이즈: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-environment
- Copilot code review: https://docs.github.com/en/copilot/concepts/agents/code-review
- Custom agents: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents
- Copilot CLI in Actions: https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions
- Actions 과금: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions
- Actions 한도: https://docs.github.com/en/actions/reference/limits
- 러너 사양: https://docs.github.com/en/actions/reference/runners/github-hosted-runners

gh-aw 문서
- 인덱스: https://github.github.com/gh-aw/
- 아키텍처: https://github.github.com/gh-aw/introduction/architecture/
- Quick start: https://github.github.com/gh-aw/setup/quick-start/
- 인증: https://github.github.com/gh-aw/reference/auth/
- 엔진 비교: https://github.github.com/gh-aw/reference/engines/ , Claude 엔진: https://github.github.com/gh-aw/engines/claude/ , Copilot 엔진: https://github.github.com/gh-aw/engines/copilot/
- Safe outputs: https://github.github.com/gh-aw/reference/safe-outputs/
- Frontmatter: https://github.github.com/gh-aw/reference/frontmatter/
- Triggers: https://github.github.com/gh-aw/reference/triggers/
- Integrity(lockdown 대체): https://github.github.com/gh-aw/reference/integrity/
- Sandbox: https://github.github.com/gh-aw/reference/sandbox/
- Network: https://github.github.com/gh-aw/reference/network/
- Tools: https://github.github.com/gh-aw/reference/tools/
- Threat detection: https://github.github.com/gh-aw/reference/threat-detection/
- Cost management: https://github.github.com/gh-aw/reference/cost-management/
- FAQ: https://github.github.com/gh-aw/reference/faq/
- 저장소: https://github.com/githubnext/gh-aw (취약 버전 회수 공지 포함)

Anthropic
- Claude Code GitHub Actions: https://code.claude.com/docs/en/github-actions
- claude-code-action security: https://github.com/anthropics/claude-code-action/blob/main/docs/security.md , setup: https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md
- Claude Code Review: https://code.claude.com/docs/en/code-review
- Scheduled tasks(routines): https://code.claude.com/docs/en/routines

기타
- `actions/ai-inference` README: https://github.com/actions/ai-inference
- `leanprover/lean-action` README: https://github.com/leanprover/lean-action/blob/main/README.md
- leanblueprint README·템플릿: https://github.com/PatrickMassot/leanblueprint , https://raw.githubusercontent.com/PatrickMassot/leanblueprint/master/leanblueprint/templates/blueprint.yml
- Lean Zulip "Cache on GitHub Actions" (2025-11-16): https://leanprover-community.github.io/archive/stream/113488-general/topic/Cache.20on.20GitHub.20Actions.html
- Lean Zulip cache get 관련: https://leanprover-community.github.io/archive/stream/287929-mathlib4/topic/lake.20exe.20cache.20get.20very.20slow.html , https://leanprover-community.github.io/archive/stream/270676-lean4/topic/Increase.20lake.20exe.20cache.20get.20timeout.html
- 2차 출처(참고만): The New Stack, DEV Community Universe 2026 정리, tenki.cloud(코드 리뷰 비용), coproduct-opensource/lean-mathlib-cache(5분 주장)

---

## 8. 검증하지 못한 것 / 불확실성

1. **Copilot Free로 gh-aw Copilot 엔진을 쓸 수 있는가.** GA 공지는 "requires a Copilot license"라고만 하고, 플랜 페이지는 Free에도 CLI와 AI Credits 할당이 있다고 한다. Free 계정이 "Copilot Requests" PAT를 만들어 gh-aw를 돌릴 수 있는지는 1차 출처에서 확인 못 함. Free의 AIC 수치도 못 찾음.
2. **Agent HQ 서드파티 에이전트의 현재 과금 단위.** 2026-02 공지는 "one premium request" per session(preview). 2026-06-01 AI credits 전환 후의 환산은 미확인. 플랜 페이지는 여전히 "public preview".
3. **Mathlib 캐시 호스트명.** lean-action은 `cache.mathlib.org`를 기본으로 설정. Lean Squad 허용목록은 `lakecache.blob.core.windows.net`, `reservoir.leancache.cloud`. 2026-01 Zulip에 Cloudflare 백엔드 전환 논의가 있어 실제 호스트가 바뀌었을 수 있음 → 첫 실행 뒤 `gh aw audit`의 Firewall Analysis로 확정.
4. **`lake exe cache get` 소요 시간.** 2026년 공식 벤치마크 없음. "약 5분"은 제3자 주장, "50분 빌드"는 캐시 불일치 사례.
5. **GitHub 블로그 2026-02-13 포스트**("third leg of CI/CD")는 URL이 404. 내용은 GitHub Next 페이지의 요약으로 확인.
6. **leanblueprint 템플릿 전문**은 일부만 읽힘(docgen-action이 checkdecls·Pages 배포를 담당한다는 것은 커뮤니티 PR에서 간접 확인).
7. **lean-action `axiom-audit` 입력의 정확한 키 이름·허용목록 문법**은 README 요약에서만 확인. 실제 사용 전 README 원문 재확인 필요.
8. **gh-aw 프론트매터 키의 안정성.** 주간 릴리스로 키가 바뀐 이력(lockdown → min-integrity, `.github/mcp.json`). 3절 스케치는 `gh aw compile`로 검증해야 함. 공식 docs 일부는 아직 preview 표기.
9. **Copilot cloud agent의 공개 저장소 지원.** automations는 "not available in public repositories"가 명시돼 있으나 cloud agent 자체의 공개 저장소 지원 여부는 문서에서 직접 확인 못 함(동작한다고 보는 게 합리적이나 미검증).
10. **GitHub Pages의 Free 플랜 공개 저장소 제한**은 일반 지식이며 오늘 재검증하지 않음.
11. **리뷰어·문헌 감시의 회당 비용**은 토큰 단가로 추정한 값. 실측은 `gh aw logs`의 AIC 열로.
12. **Lean Squad의 Mathlib 사용 여부**는 포스트에 명시되지 않음("with no Mathlib"이라는 한 사례만 언급). 이 저장소처럼 Mathlib 전체를 의존하는 환경에서 gh-aw 샌드박스의 디스크(14 GB)·메모리 한도가 충분한지는 실제로 돌려봐야 안다.
