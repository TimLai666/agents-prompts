# agents-prompts

統一管理給 AI agent 的全域指令檔，用 `sync.py` 一鍵同步到 Codex 和 Claude 的全域設定位置。

## 檔案結構

```
AGENTS-content.md   ← agent 指令內容（sync.py 的唯一來源）
CHAT-content.md     ← chat 用個人化 prompt，貼進 ChatGPT、Claude 等聊天服務
sync.py             ← 同步工具
```

## 安装

```bash
git clone https://github.com/TimLai666/agents-prompts.git
cd agents-prompts
python sync.py
```

同步後：

| 目標位置 | 適用工具 |
|---|---|
| `~/.codex/AGENTS.md` | Codex |
| `~/.claude/CLAUDE.md` | Claude Code |

## 用法

```bash
python sync.py              # 同步
python sync.py --dry-run    # 預覽，不動檔案
python sync.py --diff       # 顯示差異
```

## 備份

同步前會自動把既有檔案備份到各自目錄下的 `backups/`，檔名帶時間戳。

## 修改指令

直接編輯 `AGENTS-content.md`，再跑 `sync.py` 即可。所有變更集中管理，不用分別改兩個位置。

`CHAT-content.md` 從 `AGENTS-content.md` 濃縮而來，不經 `sync.py`。原檔更新後要手動檢查這份要不要跟著改，貼進聊天服務的個人化欄位也要重貼。
