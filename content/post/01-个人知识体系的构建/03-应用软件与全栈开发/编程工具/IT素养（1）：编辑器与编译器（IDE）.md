---
tags:
  - "#IT素养"
updated: 2026-11-14 23:53
---
## 一、定义

- **编辑器**：用来编写和修改源代码的工具，提供语法高亮、代码补全、文件管理等功能。它本身不负责把代码变成可执行程序。

- **编译器**：把源代码翻译成目标程序或可执行文件的工具。例如 GCC 把 C/C++ 源码编译为可执行文件；MinGW 是 GCC 在 Windows 上的移植版本，用于生成 `.exe`。

- **IDE（集成开发环境）**：把编辑器、编译器、调试器、工程管理集成在一起。Dev-C++、Code::Blocks、Visual Studio 都属于 IDE；GCC、MinGW 属于编译器/工具链。

---

## 二、主流类型对比

### 1. 主流 IDE 对比

| 工具 | 定位 | 平台 | 编译器支持 | 占用与调试 | 维护与适用规模 |
|---|---|---|---|---|---|
| **Dev-C++（Orwell 维护版）** | 纯新手入门 | 仅 Windows | 仅集成 MinGW | 几十兆；基础断点调试 | 更新停滞，最新 5.11（2015）；适合单文件/小型工程、NOIP 入门 |
| **Code::Blocks** | 新手到进阶的全能工具 | Windows/Linux/macOS | GCC、MinGW、MSVC、Clang 等 | 百兆级；完整调试，支持插件扩展 | 持续更新；适合中小型工程、跨平台学习 |
| **Visual Studio 2022 社区版** | 专业级开发套件 | 主要 Windows，macOS 版功能受限 | 内置 MSVC，可扩展 GCC/Clang | 安装后约 20–30GB；高级调试、性能分析、团队协作 | 微软长期维护；适合大型项目/企业级应用 |

### 2. 编译器/工具链对比：GCC 与 MinGW

| 对比项 | GCC | MinGW（推荐 MinGW-w64） |
|---|---|---|
| 适用平台 | Linux、macOS 等类 Unix 系统 | Windows |
| 编译目标 | 类 Unix 可执行文件，如 ELF | Windows 原生 `.exe` |
| 系统依赖 | 依赖 glibc 等类 Unix 底层库 | 依赖 Windows 系统库，如 `msvcrt.dll` |
| 获取方式 | Linux 用 `apt`/`dnf` 安装；macOS 用 `xcode-select --install` | 从 MinGW-w64 官网或 SourceForge 下载安装器，将 `bin` 目录加入 PATH |
| 功能侧重 | 工具链完整，类 Unix 开发常用 | 精简适配 Windows，专注生成 Windows 兼容程序 |


