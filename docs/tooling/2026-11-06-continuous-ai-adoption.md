# Continuous AI 도입 기록 (2026-11-06)

조사는 `2026-11-06-continuous-ai-survey.md`. 이 문서는 무엇을 정했고 무엇을 실제로 깔았는지 적는다.

## 결정 (저장소 소유자)

| 항목 | 결정 | 이유·대가 |
| --- | --- | --- |
| 저장소 | 공개 (`github.com/Maokami/smarandache-wellin-lean`) | Actions·Pages 무료, 4 vCPU 러너. 커밋 주소는 GitHub noreply 로 바꾼 뒤 공개했다 |
| AI 엔진 | `anthropics/claude-code-action@v1` + Claude 구독 토큰 (`CLAUDE_CODE_OAUTH_TOKEN`) | API 과금이 없다. 대신 gh-aw 의 safe-outputs·방화벽·threat detection 이 없다 |
| 블루프린트 이름 검사 | 공식 `checkdecls` 를 의존성으로 추가 (커밋 고정) | leanblueprint 표준 CI (docgen-action) 와 같은 검사 |

## gh-aw 가드레일을 대신하는 것

claude-code-action 에는 출력 종류·개수 제한이 없으므로 아래로 대신한다.

1. **main 보호 ruleset `protect-main`.** 삭제·force push 금지, PR 필수, 승인 1 건 필수, 상태 검사
   `Lean build and audits` (github-actions 앱이 만든 것만) 필수. 저장소 관리자 (사람) 만 우회한다.
   Claude GitHub App 은 main 에 직접 쓸 수 없고, 자기 PR 을 승인할 수 없으므로 머지도 못 한다.
   승인 필수가 중요한 이유: `pull_request` 실행은 PR 안의 ci.yml 을 쓰므로, ci.yml 을 고친 PR 은 범위 검사를 지운 채
   같은 이름의 검사를 통과시킬 수 있다. 이 경로는 사람 승인만이 막는다.
2. **App 토큰 범위 축소.** 모든 Claude 워크플로에 `additional_permissions` 를 줘서 App 토큰을 좁힌다.
   리뷰어·질의·문헌 감시는 contents 읽기, 사냥꾼은 contents/PR/issues 쓰기 + actions 읽기 (workflows 쓰기 없음).
3. **신뢰할 수 있는 입력.** 사냥꾼은 소유자가 쓴 lemma-hunt 이슈의 제목·본문만 사전 단계에서 파일로 받고, 댓글은 읽지 않는다.
   질의 (`@claude`) 는 소유자 댓글에만 반응한다. 문헌 감시의 WebFetch 는 학술 도메인으로 묶는다.
4. **서브프로세스 환경 정리.** `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`. Bash 와 `lake build` 에서 Anthropic 자격 증명이
   보이지 않는다 (GitHub 토큰은 남는다: Claude Code 문서).
5. **CI 의 에이전트 PR 범위 검사.** `claude/` 브랜치, 봇이 연 PR, 소유자가 아닌 사람이 연 PR 이 보호 파일을 바꾸면
   실패 (`--no-renames` 로 이름 변경도 잡는다).
6. **도구 허용 목록.** 워크플로마다 필요한 명령만 연다. 사냥꾼의 git 은 `claude/` 브랜치 생성·push 로 좁혔다.
   다만 `lake build` 자체가 코드 실행이므로 허용 목록은 실수 방지용이지 보안 경계가 아니다. 경계는 1–4 다.
7. **CI 가 판정한다.** Lean 빌드, 라이브러리 전체 공리 감사 (lean-action `axiom-audit`), `check_blueprint.py`,
   `checkdecls`. 에이전트의 "증명했다" 는 말은 판정이 아니다 (`AGENTS.md`).
8. **사람이 머지하고 장부를 고친다.** 사냥꾼 PR 은 draft 로 열리고, 사람이 Ready 로 바꿀 때 리뷰어가 돈다.

## 깔린 것과 검증 상태 (2026-11-06)

두 층을 나눠 적는다. 보호 장치와 CI 는 실행으로 확인했고, AI 결과는 아직 한 번도 확인하지 못했다.

**보호 장치와 CI (확인됨).**

| 항목 | 상태 |
| --- | --- |
| `ci.yml` | main 녹색 (예: 실행 42183868930). 공리 감사가 선언 128 개를 허용 목록 안에서 확인 |
| `blueprint.yml` | main 녹색 (예: 실행 42183868995). https://maokami.github.io/smarandache-wellin-lean/ 배포 |
| ruleset `protect-main` | PR, 승인 1, 마지막 push 승인, `Lean build and audits` (github-actions 앱) 필수. 관리자만 우회 |
| 에이전트 PR 범위 검사, Dependabot 검사 | CI 에 있음. Dependabot 검사는 로컬에서 순수 고정 변경 통과·섞인 변경 차단을 시험 |
| 사냥꾼 사전 단계 (신뢰 입력) | 로컬에서 이슈 #1 통과, 다른 소유자 거부를 시험 |

**AI 결과 (미확인, 인증 차단).** 네 워크플로 파일은 있다. 저장소에 `CLAUDE_CODE_OAUTH_TOKEN` secret 이 없어
실제 Claude 실행은 0 회다. 예전에 Dependabot PR 에서 돈 리뷰 실행 하나는 출력 없이 녹색으로 끝났다.
그래서 각 워크플로에 두 단계를 넣었다.

- 실행 전: secret 이 비었으면 실패 (값은 출력하지 않는다).
- 실행 후: 완료된 출력이 없으면 실패. 진행 상태 댓글을 결과로 세지 않도록, 최종 답변·리뷰 요약·PR 본문·실패 보고에
  이번 실행의 완료 표식 `[sw-done:<run_id>.<run_attempt>]` 를 요구하고 `claude[bot]` 이 쓴 본문에서 확인한다.
  - 질의·리뷰: 표식이 든 `claude[bot]` 댓글.
  - 사냥꾼: 이번 실행 이후 만든 `claude/` 브랜치의 draft PR 로 본문에 `Refs #이슈` 와 표식이 있는 것 (draft 가 아니면 실패),
    또는 PR 이 없을 때 이슈에 표식이 든 실패 보고.
  - 문헌 감시: `jq -e` 로 `create` 가 boolean 인지, `create = true` 면 공백을 뺀 `body` 가 비지 않았는지, 이슈 URL 이 나왔는지.
  - 검증 스크립트는 `set -euo pipefail` 과 숫자 확인으로 API·jq 실패 때 통과하지 않는다 (fail closed).
  - 음성 시험: 워크플로의 실제 `run:` 스크립트를 꺼내 가짜 `gh` 로 돌렸다. 진행 댓글만, 다른 실행·attempt 의 표식, 사람이 쓴 표식,
    다른 이슈의 PR, draft 아닌 PR, 시작 전 PR, 공백뿐인 body, boolean 아닌 create, API 실패는 거부하고, 정상 결과는 통과했다
    (26 사례).

`scripts/ai_status.sh` 가 설정 파일, 인증 준비 (등록됨 / 없음 / 조회 실패), Action 결론, 실제 출력을 따로 보여 준다.
실제 출력은 완료 표식이 있는 것만 완료로 세고, 표식 없는 `claude[bot]` 댓글은 관측만 한다.

## 재개 순서 (저장소 소유자)

1. Claude GitHub App 을 이 저장소에 설치한다: https://github.com/apps/claude (이 저장소만 선택).
2. 로컬에서 `claude setup-token` 으로 구독 토큰을 만들고, `gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo Maokami/smarandache-wellin-lean`
   을 실행해 프롬프트에 붙여 넣는다. 토큰을 명령줄 인자나 파일, 대화에 남기지 않는다.
3. 가장 작은 smoke: 이슈 #1 에 소유자 댓글 `@claude 이 이슈가 블루프린트의 어느 노드를 형식화하라는 것인지 한 문장으로 답해 줘`.
   `Claude ask` 실행이 녹색이고 `claude[bot]` 답글이 달렸는지 `scripts/ai_status.sh` 로 확인한다.
4. Actions 에서 `Claude literature watch` 를 수동 실행한다. 구조화 출력이 있고, 새 항목이 있으면 `lit-watch` 이슈가 열려야 한다.
5. `Claude lemma hunter` 를 이슈 1 로 수동 실행한다. draft PR 또는 이슈의 실패 보고가 있어야 한다.
6. 사냥꾼 PR 이 생기면 Ready for review 로 바꿔 `Claude proof review` 를 돌린다. PR 에 `claude[bot]` 리뷰 댓글이 있어야 한다.
   머지는 사람이 승인한다.

각 단계에서 녹색 Action 만으로 완료라고 보지 않는다. 출력이 있어야 완료다.

첫 사냥 과제는 이슈 #1 (`cor:Q1-two` 를 IT(q) 전체 가정 아래 형식화).

## 보안 검토 (2026-11-06)

독립 보안 검토가 첫 설정을 FAIL 로 판정했다. 심각 1 건: 승인 0 인 ruleset 과 넓은 App 토큰 때문에 에이전트가 사람 없이
main 을 바꿀 수 있었다. 중간 4 건: 사냥꾼이 공개 이슈 댓글을 읽을 수 있었고, `@claude` 질의가 tag 모드의 git 쓰기 도구로
커밋할 수 있었고, 범위 검사가 이름 변경과 브랜치 이름 우회에 약했고, 문헌 감시의 WebFetch 가 열려 있었다.
위 1–6 이 그 수정이다. 그 밖에 블루프린트의 Pages 권한을 main push 의 배포 job 으로만 옮겼고, 체크아웃 자격 증명을 남기지 않으며,
lean-action 을 SHA 로 고정하고 Dependabot 을 켰다. 외부 기여자의 포크 PR 은 매번 승인을 받아야 실행된다.

재검토 (같은 날) 는 보안 심각 0 건을 확인하고 다음을 더 지적했다. 모두 반영했다.
사냥꾼의 git 허용 패턴 `claude/:*` 이 실제 명령을 막았다 (`:*` 는 뒤에 공백을 요구한다). `claude/*` 로 고쳤다.
App 이 남의 PR (Dependabot 등) 에 push 한 뒤 승인할 수 있었다. ruleset 에 마지막 push 승인 (`require_last_push_approval`) 을 켜고,
Dependabot PR 은 예외 대신 "`uses:` 고정 줄만 바꿨는가" 를 검사한다. 사냥꾼의 사전 단계는 이슈 본문을 소유자 말고 누가 고쳤는지
(`editor`) 도 본다. 문헌 감시는 Claude 에게서 Bash 를 빼고 구조화 출력 (`--json-schema`) 을 받아 다음 단계가 이슈를 연다.
리뷰어·사냥꾼은 `gh` 의 `--body-file`, `-F` 를 금지했다. 토큰 변수 (`$GH_TOKEN`) 금지 패턴도 넣었다가 뺐다:
action 이 `claude_args` 를 셸 규칙으로 토큰화하면서 변수가 빈 문자열이 되어 `Bash(* *)` 로 바뀌었고, 모든 Bash 명령을 막았다
(2 차 재검토). 변수 이름 나열은 원래 막을 수 없는 경로라 경계로 삼지 않는다.

남은 위험 (받아들임): `lake build` 는 Lean 코드 실행이므로 사냥꾼은 사실상 임의 코드를 돌린다. Anthropic 자격 증명은
서브프로세스 환경에서 지워지지만, 프로세스 격리 (bubblewrap) 가 없어 `/proc` 경유 노출 가능성은 남는다. 입력이 소유자 이슈 본문뿐이라
촉발 경로가 좁다.

남은 선택 사항: 관리자 우회를 `pull_request` 모드로 바꾸면 이 PC 의 로컬 에이전트 (Claude Code) 도 PR 을 거친다.
지금은 소유자의 직접 push 작업 방식을 유지한다.

## 시행착오

- lean-action 의 `mk_all-check` 는 루트 파일의 import 를 알파벳 순으로 요구한다. `lake exe mk_all` 로 맞췄다.
- lean-action 의 `axiom-audit-root` 는 namespace 가 아니라 모듈 접두사다. 기본값 (라이브러리 이름) 을 쓴다.
- 짧은 간격으로 push 하면 블루프린트 실행이 `concurrency` 로 취소된다. 한 번에 모아서 push 한다.

## 다음에 볼 것

- 사냥꾼을 몇 번 수동으로 돌려 비용 (구독 사용량)·성공률·리뷰어의 지적을 기록한 뒤 주간 schedule 을 켤지 정한다.
- 가드레일이 부족하다고 느끼면 gh-aw 로 옮기는 것을 검토한다 (조사 문서 6 절). gh-aw 의 Claude 엔진은 구독 OAuth 토큰을 받지 않지만,
  Anthropic API 키나 WIF 외에 Copilot 추론 경로 (`copilot/` 모델, `copilot-requests: write` 또는 `COPILOT_GITHUB_TOKEN`) 로도 쓸 수 있다
  (gh-aw engines/claude 문서, 2026-11-06 확인). 이번 구현은 claude-code-action + 구독 토큰을 유지한다.
