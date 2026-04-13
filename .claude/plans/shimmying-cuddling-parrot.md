# 优化导入与爬取页面 UI

## Context

用户之前认为"手动爬虫"功能未实现，实际 `AdminPolicyImport.vue` 已有完整的两个 tab（文件上传 + 手动爬虫），但 UI 风格与项目整体不一致，导致功能被埋没在 tab 中不易被发现。需要将页面重构为与其他管理页面（AdminDashboard、AdminPolicies）一致的设计风格。

## 审查结论（自动爬虫功能）

自动爬虫功能实现完整且链路清晰：
- 手动爬取：`POST /policies/crawl` → 创建 run → 消费执行 → 写入原始表 → 创建审核任务
- 自动爬取：scheduler 定时检查 → 创建 run → 同一消费链路
- 爬虫服务 (`crawler_service.py`) 使用正则解析 HTML，提取链接、元数据、日期等
- 代码质量良好，结构清晰，错误处理到位

## 改动方案

**文件**: `C:\Users\22067\Desktop\农策微光\frontend\src\views\admin\AdminPolicyImport.vue`

### 1. 去掉 tab，改为两个 page-panel 垂直排列

当前用 `el-tabs` 将文件上传和手动爬虫藏在两个标签页中，改为类似 AdminDashboard 的多 panel 布局：

- **Panel 1: 文件上传** - "上传政策文件进行解析"
- **Panel 2: 手动爬虫** - "从政府网站抓取候选政策"

### 2. 替换 `el-card` 为 `section.page-panel`

与其他"好风格"页面一致，使用 `<section class="page-panel">` 替代 `<el-card shadow="never">`。

### 3. 统一配色和文本

- `.hint` 的 `color` 从 `var(--el-text-color-secondary)` 改为 `var(--adm-muted)`
- 每个 panel 使用 `panel-subtitle` 说明功能

### 4. 统一表单布局

- `el-form label-width` 统一为 `120px`（当前值，保持不变）
- 按钮区域使用 `<div class="actions">`（与 AdminPolicyReview 一致）

### 5. 保留现有功能逻辑

所有 API 调用、数据处理、文件上传/解析/送审逻辑保持不变，仅重构模板和样式。

## 具体结构

```
<div class="page-shell">
  <div class="page-head">
    <div class="page-title-group">
      <h3 class="page-title">导入与爬取</h3>
      <p class="page-subtitle">统一政策入库入口...</p>
    </div>
    <div class="page-actions">
      <el-button @click="$router.push('/admin/tasks')">任务中心</el-button>
      <el-button @click="$router.push('/admin/policies/review')">审核台</el-button>
    </div>
  </div>

  <!-- Panel 1: 文件上传 -->
  <section class="page-panel">
    <div class="panel-head">
      <h4>文件上传</h4>
      <p class="panel-subtitle">支持 DOCX/PDF，小文件可同步解析预览</p>
    </div>
    <el-upload drag ... />
    <div class="actions">
      <el-button type="primary" @click="parseSync">同步解析预览</el-button>
      <el-button @click="parseJob">提交后台任务</el-button>
      <el-button type="success" @click="sendToReview">送审</el-button>
    </div>
    <!-- 预览和结果区域 -->
  </section>

  <!-- Panel 2: 手动爬虫 -->
  <section class="page-panel">
    <div class="panel-head">
      <h4>手动爬虫</h4>
      <p class="panel-subtitle">从湖北省农业农村厅网站抓取候选政策</p>
    </div>
    <el-form label-width="120px">
      <!-- 数据源、文件类型、效力状态、每源抓取数、最大文件数 -->
    </el-form>
    <div class="actions">
      <el-button type="primary" @click="doCrawl">开始抓取</el-button>
    </div>
    <!-- 结果表格 -->
  </section>
</div>
```

## 验证

1. 启动前后端开发服务器（如尚未运行）
2. 登录管理端，进入"导入与爬取"页面
3. 确认两个 panel 可见、布局清晰
4. 确认文件上传流程正常（选择文件 → 解析 → 送审）
5. 确认手动爬虫流程正常（配置参数 → 执行 → 结果展示）
6. 确认整体风格与 AdminDashboard、AdminPolicies 等页面一致
