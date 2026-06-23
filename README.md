# 企微随机祝福 H5

手机端随机祝福页 + 企微图文卡片群发。

- **卡片**：统一封面 +「你好，初次见面请多多指教」
- **点开**：无需登录，随机展示一条祝福（工作 / 健康 / 生活）
- **页面**：彩虹动画 + 打字机效果 +「再抽一条」

## 工作原理

```text
群发脚本 ──► 从企微 API 拉取可见成员
              每人收到相同链接 /bless

同事点击 ──► 直接打开 H5
              ──► 随机抽取一条祝福
              ──► 可点击「再抽一条」换一条
```

## 快速开始

```bash
cd ~/Projects/wecom-blessing-h5
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env（本地预览只需 PORT）

python3 scripts/generate_preview.py
python3 scripts/prepare_mascot.py
python3 run.py
```

浏览器打开：

```
http://localhost:8080/bless
```

## 企微后台配置（群发用）

1. 自建应用 → 记录 **CorpID / AgentId / Secret**
2. **可见范围**设为要发送的人
3. 开启 **发送应用消息** 权限
4. `BASE_URL` 填你的 **HTTPS** 公网地址

> 无需配置 OAuth 回调域，无需域名主体校验。

## 常用命令

```bash
# 预览会从企微同步到哪些人
python3 scripts/sync_from_wecom.py

# 先看会发给谁
python3 scripts/send_wecom.py --dry-run

# 测试发 1 人
python3 scripts/send_wecom.py --limit 1

# 正式群发
python3 scripts/send_wecom.py
```

## 用到的企微 API

| API | 用途 |
|-----|------|
| `gettoken` | 鉴权 |
| `user/list` | 拉取可见成员 |
| `message/send` (news) | 发送图文卡片 |

## 目录结构

```
wecom-blessing-h5/
├── public/          # H5 前端
├── server/          # FastAPI
├── scripts/         # 同步名单 & 群发
├── data/            # 封面图
└── run.py
```

## 说明

- 所有人收到**同一个链接**，打开后随机祝福，不涉及用户姓名
- 可在浏览器或企微内直接打开，无 OAuth 限制
- 群发仍需企微应用 Secret；H5 页面本身不调用企微 API
