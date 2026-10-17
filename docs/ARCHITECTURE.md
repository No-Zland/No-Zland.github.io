# 项目架构

## 数据流

```
content/post/*.md
      │
      ▼
build_blog.py  ──读取 src/*.css / src/*.js──▶  site/
                                                │
                                                ▼
                                    Hugo server / layouts
                                    staticDir = site/
                                                │
                                                ▼
                                             public/
```

- `content/post/`：Obsidian 笔记库，唯一内容源。
- `src/`：生成器使用的样式和脚本（日历、搜索、软导航、阅读目录、媒体查看、音乐、名言、防爬）。
- `music/`：播放列表、音频与 LRC 歌词；构建时复制到 `site/assets/music/`。
- `build_blog.py`：扫描笔记、渲染 Markdown、复制图片/PDF、生成 `site/` 与搜索索引。
- `layouts/index.html`：Hugo 首页模板，直接读取 `site/index.html`。
- `hugo.toml`：把 `site/` 设为静态目录，避免 Hugo 二次渲染内容。
- `site/`：生成器输出，Hugo 直接服务；GitHub Pages 也部署这个目录。
- `public/`：Hugo 预览/发布输出，首页渲染需要它，因此保留但不入库。
- `docs/previews/`：界面预览图，供 README 和项目说明使用。

## 页面层级

```
首页（名言警句 + 大板块）
  └─ 板块页（板块下的分类）
       └─ 分类页（子分类，或文章阅读页）
            └─ 阅读页（一篇文章一页；左侧目录 + 上一篇/下一篇）
```

板块是 **`content/post` 的顶层物理目录**，板块下的子目录就是分类；例如 `content/post/竞赛经历/202609...`、`content/post/技能学习/C++/`。这样不再有“虚拟板块 + 同名分类”的重复层级。`build_blog.py` 的 `SECTION_SPECS` 只负责板块顺序、标题、描述和颜色：

```python
{
    "slug": "科研经历",
    "title": "科研经历",
    "desc": "...",
    "color": "#db2777",
}
```

新增板块时在 `content/post` 建顶层目录并同步 `SECTION_SPECS`；新增分类时直接在板块目录下建子目录。板块下没有分类时，板块首页本身就是阅读页。

## 阅读页

- 一次只显示一篇文章，完整显示，不再按长度或章节截断。
- 左侧「文章列表」列出当前分类的全部文章，可直接切换。
- 左侧「本篇目录」从当前文章的 h2/h3 生成，点击可跳转。
- 左侧「文章」卡片是独立的上一篇/下一篇组件，使用 `⏮` / `⏭` 符号。
- 打开带 `#doc-...` 的链接（例如搜索结果）会直接定位到对应文章。
- 目录、文章列表、翻页、音乐播放器、层级导航都是独立卡片，堆叠在 `.side-column` 中。

## 软导航与全局音乐

- `src/spa.js` 拦截同源站内链接，`fetch` 目标页后用 `DOMParser` 解析。
- 只替换 `main` 中的布局内容与 `.side-column` 里播放器以外的卡片；播放器 DOM 及 `<audio>` 节点保持原位，因此音乐不中断。
- 顶栏、搜索浮层、抽屉、日历、歌词、PDF/图片查看器都是公共组件，不随导航重建。
- 阅读页与首页名言提供 `window.BlogReading.init()` / `window.BlogQuotes.init()`，软导航后重新初始化。
- 支持 `pushState` 与 `popstate`，浏览器前进/后退也能保持播放器。
- 搜索索引使用根路径 `/assets/search-index.json`，搜索浮层在所有页面通用。
- 整页刷新或直接从外部进入时，`sessionStorage` 仍会恢复曲目、进度、模式和播放状态作为兜底。

## 版权与防爬

- 每篇文章由 `doc_copyright()` 生成底部版权块，包含作者、CC BY-NC-SA 4.0 许可、原文 URL 和更新时间。
- `build_blog.py` 生成 `site/robots.txt`，对常见 AI 训练/批量抓取器设置 `Disallow: /`，并保护 PDF、音频和搜索索引。
- 页面 `<head>` 带 `noai, noimageai, noarchive` 提示；`src/anti-crawler.js` 对已声明爬虫 UA 隐藏正文，并在复制正文时自动追加出处。
- GitHub Pages 是纯静态托管，无法做真正的服务端鉴权或限流；上述机制是声明、版权提示和客户端层面的门槛，不能替代登录/服务端访问控制。

## 媒体与音乐

- `build_blog.py` 扫描 `content/post` 下的 PDF，单文件 ≤10MB 时复制到 `site/assets/files/pdf/`，并生成 `资料库/index.html`。
- 超过 10MB 的 PDF 只显示“本地”卡片，不复制、不部署；这是 GitHub Pages 体积限制下的取舍。
- 文章图片由 `src/media.js` 接管：点击打开全屏弹层，Esc / 点击背景关闭。
- 音乐播放器读取 `music/playlist.json`，构建时把 `music/` 复制到 `site/assets/music/`。
- 播放模式（顺序/随机/单曲循环）保存在 localStorage；悬浮歌词由 `.lrc` 时间轴驱动，拖动位置也保存在 localStorage。
- 播放器在每页都是独立卡片；软导航时 `<audio>` 节点不重建，整页刷新时用 `sessionStorage` 恢复曲目、进度和播放状态。
- 顺序播放到最后一首后会回到第一首，随机与单曲循环分别保持各自行为。
- 首页名言从 `content/post/阅读经历/书籍资料/名人名言.md` 读取，每行格式 `- 句子｜作者`；`src/quotes.js` 用当前分钟 + 随机数抽取，按钮可立即换一句。

## 任务状态与主人模式

- 任务只保存在浏览器 `localStorage` 的 `blogCalendarTasks.v1`，不需要服务器。
- 默认访客模式：任务列表、任务圆点、提醒全部隐藏；更新日历仍然公开。
- 首次使用设置主人密码，密码用 PBKDF2-SHA256 + 随机盐哈希后保存在 localStorage。
- 密码只保护界面，不加密数据；localStorage 仍可被本机开发者工具读取。不要把高风险信息放进去。
- 主人模式可导出/导入 JSON 备份；换设备需要手动导入，跨设备自动同步才需要服务器。
- 认证逻辑在 `src/calendar.js`，没有后端、没有账号系统、没有远程请求。

## 生成与预览

```bash
pip install -r requirements.txt
python build_blog.py
hugo server
```

- 仅重新生成站点：`python build_blog.py`
- 全量清理后重建：`python build_blog.py --clean`
- 预览地址：`http://localhost:1313/`

## GitHub Pages

- `.github/workflows/pages.yml` 在 push 到 `main` / `master` 时构建 `site/`，用官方 Pages Actions 发布。
- 仓库 Settings → Pages → Source 选择 **GitHub Actions**。
- 访问地址：`https://<用户名>.github.io/<仓库名>/`（若是 `<用户名>.github.io` 仓库则没有仓库名路径）。
- 所有站内链接都是相对路径，因此部署在子路径下也能工作。
- 大体积 PDF、PPTX、模型文件通过 `.gitignore` 排除，避免超过 GitHub 单文件 100MB / 仓库体积限制。

## GitHub 维护约定

- 不提交 `site/`、`public/`、`__pycache__/`、`.hugo_build.lock` 等生成物；见 `.gitignore`。
- 依赖写入 `requirements.txt`，不要依赖本机隐式安装。
- `.github/workflows/build.yml` 会在 push / pull request 时安装依赖并执行 `python build_blog.py --clean`，用来验证生成流程。
- `.github/workflows/pages.yml` 负责部署 GitHub Pages。
- 新功能放在 `src/`，不要把脚本散落在根目录。
- 预览图放在 `docs/previews/`，README 只引用必要图片。
- 源码入口保持为根目录 `build_blog.py`，方便 `python build_blog.py` 直接运行。
- 当前项目没有 `LICENSE` 文件；如果公开到 GitHub，请按需要补充许可证。
