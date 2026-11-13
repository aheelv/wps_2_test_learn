# 模板来源、许可证与改造清单

## 模板信息

| 项 | 内容 |
|---|---|
| 模板名称 | **Start Bootstrap — Blog Home** |
| 仓库地址 | <https://github.com/StartBootstrap/startbootstrap-blog-home> |
| 官方介绍 | <https://startbootstrap.com/template/blog-home> |
| 获取分支 | `master`，取 `dist/` 构建产物 |
| 技术栈 | HTML + Bootstrap 5.2.3 + 原生 JS（无构建依赖） |
| 许可证 | **MIT License** |
| 版权声明 | Copyright (c) 2013-2023 Start Bootstrap LLC |
| 许可证全文 | 本目录 `LICENSE-TEMPLATE.txt`，以及 `assets/template/` 内保留的原始文件 |

模板所用 Bootstrap 5.2.3 同为 MIT 许可（Copyright 2011-2022 The Bootstrap Authors），
其压缩版 JS 已随站点部署至 `assets/vendor/bootstrap.bundle.min.js`，文件头保留原始版权注释。

## 下载方式

GitHub 主站直连不稳定，本次通过 GitHub API 与 `raw.githubusercontent.com` 逐文件获取：

```
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/css/styles.css
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/js/scripts.js
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/assets/favicon.ico
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/index.html
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/LICENSE
```

实际复用并保持未改动的原始文件保存在 `assets/template/`：

- `styles.css` — 模板核心 CSS，内含 Bootstrap 5.2.3
- `scripts.js` — 模板核心 JS（版本与许可注释）
- `favicon.ico` — 站点图标

模板原始首页与说明文件仅含示例占位图、社交链接与徽章外链，不属于站点运行所需，已从交付物中移除；
如需核对模板结构，请访问上方官方仓库地址。

## 改造清单

| 原始模板 | 本站改造 |
|---|---|
| 单个 `index.html` 博客首页 | 首页 / 分类总览 / 6 个分类页 / 35 个详情页 / 检索页 / 备考指南 / 关于页 |
| 顶部 4 个静态导航项 | 分类下拉导航（6 类直达）+ 全站搜索框 + 当前页高亮 |
| 模板示例外链占位图 | 全部移除，替换为站点自绘的内联 SVG 图标（另在 `assets/img/` 保留独立 SVG 文件）与 CSS 渐变装饰 |
| CDN 引入 `bootstrap.bundle.min.js` | 下载到 `assets/vendor/` 站内引用 |
| 博客文章卡片 | 资源卡片：分类色条、推荐度星级、标签、三维评价、详情链接 |
| 侧栏「Search / Categories」静态占位 | 全站检索页 + 分类页的关键词 / 标签 / 推荐度筛选（客户端实时过滤） |
| 固定假内容分页 | 由 `data/resources.json` 驱动的语义化分类与相关资源链接 |
| 深灰导航 + 浅色正文 | 深蓝品牌渐变导航、Hero 区、统一卡片与说明页排版 |
| 英文占位文案 | 全中文内容，按「文档教程 / 视频课程 / 开源项目 / 模板素材 / 工具服务 / 设计参考」归类 |

## 新增文件（非模板内容）

- `assets/css/site.css` — 定制样式层，不修改模板 `styles.css`
- `assets/js/site.js` — 客户端检索与筛选
- `assets/img/*.svg` — 6 个分类图标 + 首页装饰图（站点自绘）
- `assets/vendor/bootstrap.bundle.min.js` — 站内的 Bootstrap JS
- `assets/files/*.pdf` — 官方大纲与样题的站内副本
- `data/` `content/` `tools/` — 资源内容与生成脚本
- 根目录全部业务页面与说明文档

## MIT 许可要求说明

依 MIT 许可证，本站在交付物中保留了模板原始版权声明与许可全文（`LICENSE-TEMPLATE.txt`），
并在页脚与「关于」页注明模板名称、仓库地址与许可证。模板原始文件以未改动形式保存于 `assets/template/`，
便于核对。本站新增内容与整理文档不受模板许可限制。
