# 故事线可视化与分享平台

**在线演示**：https://storyline-share.app.workbuddy.host/?sharecode=DGZQ7ERPN7
（完整复制整条链接打开；演示账号 `testuser_wr` / `Test123456`）

把两个人的经历、互动与关键时间点结构化记录，并渲染成可交互的动画时间轴；支持配图、人物筛选、公开分享。面向 CP 粉 / 剧粉 / 书粉这类"想梳理并分享两人故事"的内容爱好者。

---

## 功能

- **故事线管理**：多条故事线 = 多对 CP，可增删改、设置双方真名（A / B）
- **事件时间轴**：单人事件（A / B）与两人互动（AB）按时间混排，SVG 手绘时间轴 + 入场动画
- **人物筛选**：只看 A / 只看 B / 全部；互动事件在两侧都可见
- **事件详情**：日期、描述、标签、配图；图片可上传 / 移除
- **账号系统**：注册、登录、JWT 鉴权；每张故事线有 owner，接口层校验权限
- **公开分享**：一键公开 → 出现在首页发现页 → 生成沉浸式分享页 `/share/:id`（星空背景、左右交替动画时间轴，可复制链接发给朋友）
- **权限校验**：公开内容匿名可读，私密内容仅作者本人可读（服务端强制 403，不是只靠前端隐藏）

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + vue-router 4，组合式 API，`localStorage`→API 的数据仓库 |
| 后端 | Python / FastAPI + SQLAlchemy + Pydantic，JWT 登录鉴权，可选认证依赖 |
| 数据库 | 本地开发 MySQL 8；线上部署 SQLite —— 同一套 ORM，两套配置 |
| 部署 | FastAPI 单端口同时托管 API 与前端静态产物，SPA 路由回退处理刷新 |
| 安全 | bcrypt 密码哈希、环境变量隔离密钥、服务端 owner 校验与公开性校验 |

## 关键设计决策

1. **本地 MySQL、线上 SQLite 的数据层适配**：部署环境不支持 MySQL，因此把数据访问收敛到 SQLAlchemy ORM，本地与线上只切换连接串，业务代码无需改动。
2. **可选认证兼顾两种访问身份**：公开分享页允许匿名访问，工作台则需要读取用户自己的私有内容。服务端通过可选认证依赖（`get_optional_user`）配合 403 响应区分处理，而不是对所有请求统一要求登录。
3. **单端口部署 + SPA 回退**：线上仅提供一个 HTTP 端口，由 FastAPI 托管 `dist/`；刷新 `/share/2` 这类前端路由时回退到 `index.html`，避免 404。
4. **图片存储演进**：图片以 base64 存入 `LONGTEXT`；从 V1 的 localStorage 迁移到后端时复用字段适配器，保证 camelCase ↔ snake_case 转换一致。

## 本地启动

**前端**（Node.js）：

```bash
npm install
npm run dev
# 打开 http://127.0.0.1:5173
```

**后端**（本地 MySQL 版）：

```bash
cd server
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入自己的数据库密码与 JWT 密钥
python -m uvicorn main:app --reload --port 8000
```

**线上部署版**（SQLite，无需外部数据库）：

```bash
cd deploy
pip install -r requirements.txt
python main.py   # 监听 PORT 环境变量，默认 8000
```

> `deploy/data/storyline.db` 含演示数据且含密码哈希，按安全约定不纳入版本库；首次运行会自动建空库，可用自己的账号注册体验。线上演示环境另有一份独立数据。

## 项目结构

```
src/                前端 Vue 应用
  components/      时间轴、事件编辑器、故事线管理
  views/           首页发现、登录、工作台、详情、沉浸式分享页
  api/             请求客户端 + 字段适配器
  composables/     localStorage 时期的数据仓库（历史演进保留）
  stores/          全局登录状态
server/            本地开发后端（MySQL）
deploy/            线上部署后端（SQLite）+ 前端静态产物
```

## 开发历程

V1 localStorage 单机版 → V2 接入 FastAPI + MySQL 与账号系统 → 权限与公开校验 → 分享页改版为沉浸式页面 → V1 数据迁移入 MySQL → SQLite 适配并上线。完整提交历史见 `git log`。
