# THE FROM_DESIGN_SKILL
더프롬 철학을 기반으로 한 UI/UX 디자인 스킬

## thefrom-method

더프롬 디자인 방법론과, 그것을 실행하는 Claude 스킬 `thefrom-ux`의 사내 저장소입니다.
이 저장소 자체가 Claude **플러그인 마켓플레이스**라서, 저장소 주소만 알면 각자 Claude에 설치할 수 있습니다.

## 설치 — 직원용

### Claude 데스크톱 앱 (Cowork)
1. 왼쪽 **Customize → Plugins**
2. **Add marketplace** → `FROM-i/thefrom_design_Skill` 입력
3. 목록에 뜬 **thefrom-ux** → **Install**
4. 마켓플레이스에서 **Sync automatically** 켜기 — 이후 수정본이 자동 반영됩니다

한 번 설치하면 계정에 저장되어 채팅·Claude Code에서도 같은 스킬을 씁니다.

### Claude Code
```
/plugin marketplace add FROM-i/thefrom_design_Skill
/plugin install thefrom-ux@thefrom
```
비공개 저장소라면 먼저 `gh auth login` → `gh auth setup-git`으로 GitHub 인증을 저장해 두세요.
자동 업데이트는 `/plugin` → Marketplaces → thefrom → **Enable auto-update**.

### 쓰는 법
"더프롬 방식으로 ○○ 앱의 결과 화면을 설계해줘"처럼 요청하면 스킬이 S0부터 진행합니다.
브리프 템플릿: [`templates/brief.md`](templates/brief.md)

## 구조

```
method/                      방법론 원본 — 여기만 고친다
  0_CORE_철학과_판단기준.md   L0 철학·1U·게이트·금지
  1_PIPELINE_실행절차.md      L1 S0~S5 절차
  2_CATALOG_기성의_관점.md    L2 사조·조형 어휘·UI 패턴
  3_QNA_질문노드.md           L1 부속 질문 노드
plugins/thefrom-ux/
  .claude-plugin/plugin.json  버전
  skills/thefrom-ux/
    SKILL.md                  실행기 (직접 작성)
    references/               method/에서 자동 생성 — 직접 고치지 않는다
    assets/proto-base.html    375px 프로토타입 베이스
scripts/build_references.py  method/ → references/ 빌드
.claude-plugin/marketplace.json
```

## 방법론을 고칠 때 — 관리자용

1. `method/`의 문서를 고친다. L0는 합의를 거치고 개정 이력을 남긴다.
2. `python3 scripts/build_references.py` 로 스킬 참조본을 다시 만든다.
3. `plugins/thefrom-ux/.claude-plugin/plugin.json`의 `version`을 올린다. **버전을 올리지 않으면 직원들에게 반영되지 않는다.**
4. 커밋·푸시. `ci/check-references.yml`을 `.github/workflows/`로 옮겨 두면 GitHub Actions가 `references/`와 `method/`가 어긋났는지 검사한다. (워크플로 파일은 `workflow` 권한이 있는 계정으로 한 번만 올리면 된다.)

SKILL.md를 고칠 때도 3번(버전)을 잊지 않는다.

## 조직 배포 (Team·Enterprise 플랜)
관리자가 claude.ai **Organization settings → Plugins & skills**에서 이 저장소를 연결하면, 직원 개인의 GitHub 계정 없이 전원에게 배포하거나 필수 설치로 지정할 수 있습니다. 이때 저장소는 비공개여야 합니다.
