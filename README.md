# 企微个性化祝福 H5

手机端祝福页 + 企微图文卡片群发。

- **卡片**：统一封面 +「你好，初次见面请多多指教」
- **点开**：企微 OAuth 自动识别当前用户，从通讯录读取**实名姓名**和部门
- **页面**：开场无姓名 → 工作祝福（带姓名）→ 身体祝福（带姓名）

## 工作原理

```text
群发脚本 ──► 从企微 API 自动拉取可见成员（无需部门 ID、无需 CSV）
              每人收到相同链接 /bless

同事点击 ──► 企微 OAuth 静默授权 ──► 获取 userid
              ──► user/get 读取姓名、部门
              ──► 展示个性化祝福
```

## 快速开始

```bash
cd ~/Projects/wecom-blessing-h5
python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

cp .env.example .env
# 编辑 .env

python3 scripts/generate_preview.py
python3 run.py
```

本地预览（需 `DEV_BYPASS=true`）：

```
http://localhost:8080/bless
```

## 企微后台配置

1. 自建应用 → 记录 **CorpID / AgentId / Secret**
2. **可见范围**设为要发送的 60 人（或他们所在部门）
3. 开启 **通讯录只读** 权限
4. **网页授权及 JS-SDK** → 设置 OAuth 回调域为你的域名（如 `bless.example.com`）
5. `BASE_URL` 必须是 **HTTPS** 公网地址

## 常用命令

```bash
# 预览会从企微同步到哪些人（无需部门 ID）
python3 scripts/sync_from_wecom.py

# 先看会发给谁
python3 scripts/send_wecom.py --dry-run

# 测试发 1 人
python3 scripts/send_wecom.py --limit 1

# 正式群发（自动同步 + 发送）
python3 scripts/send_wecom.py
```

## 用到的企微 API

| API | 用途 |
|-----|------|
| `gettoken` | 鉴权 |
| `user/list` (department_id=1, fetch_child=1) | 自动拉取全部可见成员 |
| `user/getuserinfo` | OAuth 换 userid |
| `user/get` | 读取姓名、部门 |
| `department/get` | 部门 ID 转名称 |
| `message/send` (news) | 发送图文卡片 |

## 目录结构

```
wecom-blessing-h5/
├── public/          # H5 前端
├── server/          # FastAPI + 企微 OAuth
├── scripts/         # 同步名单 & 群发
├── data/            # 封面图
└── run.py
```

## 说明

- 不再需要 `users.json` 和手动维护姓名
- 所有人收到**同一个链接**，姓名在打开页面时自动获取
- 必须在**企业微信内**打开链接（OAuth 静默授权）
- 本地开发用 `DEV_BYPASS=true`；上线前改为 `false`
