# 农策微光全项目审查报告（2026-04）

## 审查范围

- 后端：`backend/app/api`、`backend/app/services`、`backend/app/models`、`backend/tests`
- 前端：`frontend/src/views`、`frontend/src/components`、`frontend/src/api`、`frontend/src/router`
- 审查目标：潜在 bug、用户体验问题、功能风险、权限/安全风险、测试缺口
- 说明：本报告为代码静态审查结论（未在生产流量环境压测）

## 一、关键结论

- 当前系统功能完整度较高，但存在若干高优先级风险，集中在**权限边界、异常收口、响应式导航可达性**。
- 后端优先级最高问题是：默认 JWT 密钥风险、部分接口权限过宽、部分计算与解析接口可被滥用。
- 前端优先级最高问题是：窄屏导航入口缺失、聊天发送失败时输入恢复与消息一致性不足。
- 文档层面当前根 README 仍偏“启动手册”，缺少架构、权限模型、排障与整改路线图，已在本次升级补齐。

## 二、问题清单（按严重级别）

### Critical

#### C1. 默认 JWT 密钥可导致认证体系失效

- 证据：`backend/app/core/config.py` 使用 `JWT_SECRET_KEY=dev-insecure-change-me` 作为默认值。
- 影响：如果生产环境未覆盖密钥，可伪造 token，造成账户冒用与越权访问。
- 建议：
  - 生产环境启动前强校验密钥强度与是否仍为默认值。
  - 在 CI/CD 增加密钥检查步骤（阻断部署）。

### High

#### H1. 洞察接口权限边界不清晰

- 证据：`backend/app/api/v1/insights_routes.py` 的 `kpi-summary`、`trend-analysis`、`source-distribution`、`audience-distribution` 无认证依赖。
- 影响：可被匿名抓取运营统计信息，带来业务情报暴露风险。
- 建议：按产品策略二选一并文档化：
  - 仅管理员可访问（推荐）；
  - 若公开展示，至少增加限流与缓存并明确对外数据范围。

#### H2. 爬虫源配置接口暴露目标 URL

- 证据：`backend/app/api/v1/policy_routes.py` 的 `/policies/crawl/sources` 无管理员校验，直接返回 `url`。
- 影响：内部采集源暴露，增加被针对性干扰或外部仿爬风险。
- 建议：改为管理员可见，或对普通调用方隐藏 URL 字段。

#### H3. 异步文件解析任务缺少体量上限

- 证据：`backend/app/api/v1/policy_routes.py` 的 `/policies/parse-file/jobs` 未限制 `data_b64` 大小，而同步接口有大小限制。
- 影响：极端情况下引发内存/存储压力，影响整体可用性。
- 建议：对 `data_b64` 与解码后字节数做硬限制，超限返回 413。

#### H4. 匹配评估接口易被滥用

- 证据：`backend/app/api/v1/policy_routes.py` 的 `/policies/evaluate` 无认证、无限流。
- 影响：可被高频调用消耗 CPU，拖慢合法请求。
- 建议：增加认证与速率限制，并限制 `condition_tree` 深度和节点数。

#### H5. 窄屏导航可达性缺陷（前端）

- 证据：`frontend/src/views/HomePage.vue`、`frontend/src/views/CompassPage.vue`、`frontend/src/views/InsightsPage.vue` 在窄屏用 `.nav-link:not(:last-child){display:none}`。
- 影响：用户在移动端/平板无法访问多数主入口，属于高影响体验问题。
- 建议：改为汉堡菜单/抽屉聚合全部导航项，保留完整可达性。

#### H6. 聊天发送失败时输入与消息状态不一致

- 证据：`frontend/src/components/ChatWindow.vue` 在请求前清空输入，失败路径中用户消息处理不一致。
- 影响：用户可能“内容已丢、消息未成功发送”，重试成本高。
- 建议：失败时恢复输入内容，统一错误分支消息处理策略。

### Medium

#### M1. 流式聊天异常收口不足

- 证据：`backend/app/api/v1/chat_routes.py` 流式生成中缺少完整 `try/finally` 收口。
- 影响：极端情况下助手消息可能长期保持 `streaming` 状态。
- 建议：在异常与断流分支强制写入 `failed` 状态及错误信息。

#### M2. 聊天消息长度缺少硬性约束

- 证据：`backend/app/api/v1/schemas_chat.py` 的 `message` 无 `max_length`。
- 影响：大消息可引发性能与存储压力。
- 建议：增加统一上限（如 4k/8k）并返回可读错误文案。

#### M3. Insights 查询存在全表扫描

- 证据：`backend/app/services/insights_service.py` 多处 `select(...).all()`。
- 影响：数据量增长后接口耗时和内存占用线性上升。
- 建议：改 SQL 聚合与窗口化查询，叠加短期缓存。

#### M4. 前端 API 鉴权调用方式不一致

- 证据：`frontend/src/components/ChatWindow.vue` 对 `/policies`、`/policies/count` 使用 `api.get`，而其他用户接口常使用 `api.withUser`。
- 影响：后端策略变更时容易出现 401 行为不一致与刷新失败体验。
- 建议：统一策略并在 README 中明确“公开接口 vs 用户接口”边界。

#### M5. Markdown 重复渲染导致长会话性能风险

- 证据：`frontend/src/components/chat/ChatMessagePane.vue` 在模板中对每条消息重复执行 markdown + sanitize。
- 影响：长会话中滚动与重渲染可能卡顿。
- 建议：按消息缓存渲染结果或拆分子组件局部计算。

### Low

#### L1. 刷新失败错误透传可诊断性不足

- 证据：`frontend/src/api/client.js` 的 refresh 失败路径抛回初始错误，不利于定位真实失败原因。
- 建议：包装错误来源（refresh_failed）并统一前端提示。

#### L2. 路由滚动行为未统一

- 证据：`frontend/src/router/index.js` 未配置 `scrollBehavior`。
- 影响：跨页可能保留旧滚动位置。
- 建议：默认滚动到顶部（保留 hash 例外）。

#### L3. 可访问性细节可继续完善

- 证据：部分导航元素仍使用无 `href` 的 `<a @click>`；个别按钮缺少 `aria-label`。
- 建议：跳转改 `RouterLink`，补齐基础 ARIA 属性。

## 三、功能与体验重点复现场景

1. 将浏览器宽度缩小到 900px 以下，检查首页/洞察/风向页主导航入口是否可达。
2. 在聊天页发送消息后模拟后端 5xx 或断网，验证输入内容是否可恢复、消息状态是否一致。
3. 连续高频请求洞察接口与 evaluate 接口，观察响应时间和 CPU 使用增长趋势。
4. 导入超大文件触发异步解析，验证是否存在限流与体量保护。

## 四、测试缺口与补测建议

### 后端

- 权限回归：`/insights/*`、`/policies/crawl/sources`、`/policies/evaluate`
- 稳定性回归：流式聊天中断/异常场景下消息状态收口
- 边界测试：`parse-file/jobs` 大小上限、`message` 长度上限
- 性能回归：insights 聚合查询在大样本下的响应时间

### 前端

- E2E：窄屏导航可达性（375/768/900px）
- E2E：聊天发送失败恢复（输入框与消息列表一致性）
- 组件性能：长会话 markdown 渲染与滚动性能
- 会话管理：退出全部会话后的重定向与终态提示

## 五、整改优先级路线图（P0 / P1 / P2）

### P0（本周建议完成）

- 强制生产密钥策略（C1）
- 修正洞察/爬虫源/评估接口权限与限流（H1/H2/H4）
- 修复窄屏导航可达性与聊天失败恢复（H5/H6）

### P1（下个迭代）

- 流式聊天异常收口与消息状态一致性（M1）
- 异步解析大小限制与消息长度限制（H3/M2）
- Insights 聚合查询优化（M3）

### P2（持续优化）

- 前端渲染性能优化（M5）
- 认证错误提示可诊断性提升（L1）
- 可访问性与滚动行为统一（L2/L3）

## 六、建议落地方式

- 先建立“安全与权限”专项分支（P0），避免功能迭代继续叠加风险。
- 每个修复项必须绑定最小回归用例（API 测试或 E2E）。
- 将本报告中的 P0/P1/P2 直接映射到任务系统，按影响面和回归风险排序执行。
