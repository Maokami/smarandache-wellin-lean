#!/usr/bin/env python3
"""블루프린트와 Lean 소스의 대응을 검사한다 (leanblueprint checkdecls 의 자체 구현 + 역방향 점검).

외부 패키지(checkdecls)를 의존성에 넣지 않기 위해 같은 일을 직접 한다.

(1) blueprint/lean_decls (leanblueprint web 이 만든다) 의 모든 이름이 Lean 에 존재하는지:
    `#check @이름` 을 모은 임시 Lean 파일을 `lake env lean` 으로 돌린다. (--lean 을 줄 때만. 수 분 걸린다)
(2) 소스에 선언된 모든 theorem/lemma/def 가 블루프린트의 어떤 \\lean{...} 에 나오는지 (역방향).
(3) 블루프린트에 나오는 theorem/lemma 가 Audit.lean 에서 #print axioms 되는지.
(4) \\leanok 이 붙은 정리형 환경은 \\lean{...} 을 가져야 한다.

사용:  python3 -I scripts/check_blueprint.py           # (2)–(4) 만, 즉시
       python3 -I scripts/check_blueprint.py --lean    # (1) 까지
       python3 -I scripts/check_blueprint.py --write-decls PATH
                                                       # \lean 이름 목록을 PATH 에 써서 `lake exe checkdecls PATH`
                                                       # (공식 checkdecls) 로 넘긴다. plasTeX 없이 CI 에서 쓴다.
종료 코드 0 = 모두 통과.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "SmarandacheWellin"
BP = ROOT / "blueprint"
MODULES = ["Defs", "Basic", "Congruence", "Avoid", "Interval"]
DECL = re.compile(r"^(?:noncomputable\s+)?(theorem|lemma|def)\s+([A-Za-z_][A-Za-z0-9_'.]*)", re.M)
ENV = re.compile(r"\\begin\{(definition|lemma|theorem|proposition|corollary)\}(.*?)\\end\{\1\}", re.S)


def source_decls() -> dict[str, str]:
    out = {}
    for m in MODULES:
        for kind, name in DECL.findall((SRC / f"{m}.lean").read_text(encoding="utf-8")):
            out["SW." + name] = kind
    return out


def blueprint_names(tex: str) -> list[str]:
    names = []
    for body in re.findall(r"\\lean\{([^}]*)\}", tex):
        names += [x.strip() for x in body.split(",") if x.strip()]
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lean", action="store_true", help="lake env lean 으로 존재 확인 (느림)")
    ap.add_argument("--write-decls", metavar="PATH", help="\\lean 이름을 한 줄에 하나씩 PATH 에 쓴다")
    args = ap.parse_args()
    raw = (BP / "src" / "content.tex").read_text(encoding="utf-8")
    tex = re.sub(r"(?<!\\)%.*", "", raw)  # 주석 제거
    bp = blueprint_names(tex)
    src = source_decls()
    audit = set(re.findall(r"#print axioms\s+(\S+)", (SRC / "Audit.lean").read_text(encoding="utf-8")))
    fails = 0

    dup = sorted({n for n in bp if bp.count(n) > 1})
    if dup:
        print("[중복] 블루프린트에 두 번 이상 나오는 이름:", ", ".join(dup)); fails += 1

    missing_in_src = [n for n in bp if n not in src]
    if missing_in_src:
        print("[1a] 블루프린트에 있으나 소스에서 찾지 못한 이름:", ", ".join(missing_in_src)); fails += 1

    not_in_bp = sorted(set(src) - set(bp))
    if not_in_bp:
        print("[2] 소스에 있으나 블루프린트에 없는 선언:", ", ".join(not_in_bp)); fails += 1

    unaudited = sorted(n for n in set(bp) if src.get(n) in ("theorem", "lemma") and n not in audit)
    if unaudited:
        print("[3] Audit.lean 에서 감사하지 않는 정리:", ", ".join(unaudited)); fails += 1

    for env, body in ENV.findall(tex):
        head = body.split("\\begin{proof}")[0]
        if "\\leanok" in head and "\\lean{" not in head:
            label = re.search(r"\\label\{([^}]*)\}", head)
            print(f"[4] \\leanok 인데 \\lean 없음: {env} {label.group(1) if label else '?'}"); fails += 1

    print(f"블루프린트 이름 {len(bp)} 개, 소스 선언 {len(src)} 개, 감사 {len(audit)} 개")

    if args.write_decls:
        pathlib.Path(args.write_decls).write_text("".join(n + "\n" for n in bp), encoding="utf-8")
        print(f"{args.write_decls} 에 {len(bp)} 개 이름을 씀")

    if args.lean:
        decls = (BP / "lean_decls").read_text(encoding="utf-8").split()
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "BlueprintCheck.lean"
            f.write_text("import SmarandacheWellin\n" + "".join(f"#check @{n}\n" for n in decls), encoding="utf-8")
            r = subprocess.run(["lake", "env", "lean", str(f)], cwd=ROOT, capture_output=True, text=True)
        errs = [l for l in (r.stdout + r.stderr).splitlines() if "error" in l]
        if r.returncode != 0 or errs:
            print("[1] lake env lean 실패:"); print("\n".join(errs[:30])); fails += 1
        else:
            print(f"[1] lean_decls 의 {len(decls)} 개 이름이 모두 Lean 환경에 존재")

    print("통과" if fails == 0 else f"실패 {fails} 건")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
