#!/usr/bin/env bash
# AI 워크플로의 상태를 네 층으로 나눠 보여 준다 (읽기 전용). green Action 은 출력이 아니다.
#   1) 설정 파일   2) 인증 준비   3) Action 결론   4) 실제 출력 (claude[bot] 댓글, lit-watch 이슈, claude/ PR)
# 사용: scripts/ai_status.sh [owner/repo]
set -uo pipefail
R="${1:-Maokami/smarandache-wellin-lean}"
cd "$(dirname "$0")/.." || exit 1
WFS="claude-ask.yml claude-review.yml claude-lit-watch.yml claude-lemma-hunter.yml claude-pr-triage.yml claude-research-planner.yml"

echo "## 1. 설정 파일"
for w in $WFS; do
  if [ -f ".github/workflows/$w" ]; then echo "  $w: 있음"; else echo "  $w: 없음"; fi
done

echo "## 2. 인증 준비"
if names=$(gh secret list --repo "$R" --json name --jq '.[].name' 2>/dev/null); then
  if printf '%s\n' "$names" | grep -qx CLAUDE_CODE_OAUTH_TOKEN; then
    echo "  secret CLAUDE_CODE_OAUTH_TOKEN: 등록됨 (이름만 확인, 값은 보지 않는다)"
  else
    echo "  secret CLAUDE_CODE_OAUTH_TOKEN: 없음  ← 인증 차단"
  fi
else
  echo "  secret CLAUDE_CODE_OAUTH_TOKEN: 조회 실패 (미확인. gh 권한이나 네트워크를 확인)"
fi
echo "  Claude GitHub App 설치: gh 의 OAuth 토큰으로는 조회할 수 없다. 첫 실행 로그의 App 토큰 교환 단계로 판단한다."

echo "## 3. Action 결론 (워크플로별 최근 실행)"
for w in $WFS; do
  gh run list --repo "$R" --workflow "$w" --limit 1 --json status,conclusion,event,createdAt,url \
    --jq "if length == 0 then \"  $w: 실행 없음\" else .[0] | \"  $w: \\(.status)/\\(.conclusion // \"-\") \\(.event) \\(.createdAt) \\(.url)\" end" \
    || echo "  $w: 조회 실패 (미확인)"
done
echo "  (Action 결론은 출력이 아니다. 4 의 완료 표식으로 판단한다)"

echo "## 4. 실제 출력"
echo "  (완료 = 본문에 완료 표식 [sw-done:<run_id>.<attempt>] 가 있는 것. 표식 없는 claude[bot] 댓글은 진행 상태 등으로 관측만 한다)"
# shellcheck disable=SC2016  # $all, $done 는 셸 변수가 아니라 jq 변수다
gh api "repos/$R/issues/comments?sort=created&direction=desc&per_page=100" \
  --jq '[.[] | select(.user.login == "claude[bot]")] as $all
        | [$all[] | select(.body | test("\\[sw-done:[0-9]+\\.[0-9]+\\]"))] as $done
        | "  claude[bot] 댓글 (최근 100 개 중): 완료 \($done | length), 관측만 \(($all | length) - ($done | length))"
          + (if ($done | length) > 0 then ", 최신 완료 \($done[0].html_url)" else "" end)' \
  || echo "  claude[bot] 댓글: 조회 실패 (미확인)"
gh api "repos/$R/pulls/comments?sort=created&direction=desc&per_page=100" \
  --jq '[.[] | select(.user.login == "claude[bot]")] | "  claude[bot] 인라인 리뷰 댓글: \(length) (관측만. 완료 판정은 요약 댓글의 표식으로 한다)"' \
  || echo "  claude[bot] 인라인 댓글: 조회 실패 (미확인)"
gh issue list --repo "$R" --label lit-watch --state all --limit 20 --json number,title,url \
  --jq '"  lit-watch 이슈 (문헌 감시 완료 결과): \(length)" + (if length > 0 then ", 최신 #\(.[0].number) \(.[0].url)" else "" end)' \
  || echo "  lit-watch 이슈: 조회 실패 (미확인)"
gh issue list --repo "$R" --label research-plan/report --state open --limit 20 --json number,url \
  --jq '"  연구 제안 보고서 (검토 전 후보): \(length)" + (if length > 0 then ", 최신 #\(.[0].number) \(.[0].url)" else "" end)' \
  || echo "  연구 제안 보고서: 조회 실패 (미확인)"
# shellcheck disable=SC2016  # $all, $done 는 셸 변수가 아니라 jq 변수다
gh pr list --repo "$R" --state all --limit 50 --json number,headRefName,isDraft,state,body,url \
  --jq '[.[] | select(.headRefName | startswith("claude/"))] as $all
        | [$all[] | select(.body | test("\\[sw-done:[0-9]+\\.[0-9]+\\]"))] as $done
        | "  claude/ PR: 완료 표식 있음 \($done | length), 관측만 \(($all | length) - ($done | length))"
          + (if ($done | length) > 0 then ", 최신 #\($done[0].number) draft=\($done[0].isDraft) \($done[0].state) \($done[0].url)" else "" end)' \
  || echo "  claude/ PR: 조회 실패 (미확인)"
