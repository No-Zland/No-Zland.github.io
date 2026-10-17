---
tags:
  - C/概念
  - Cpp
---
- 核心定位：开源跨平台 C/C++ IDE，兼顾轻量性与功能性的 "全能型工具"。
- 核心特性：
    - 支持 Windows、Linux、macOS 三大系统，可直接识别 Dev-C++ 和早期 VS 工程文件；
    - 兼容多种编译器（GCC、MinGW、MSVC 等），可根据需求灵活切换；
    - 具备代码自动补全、类浏览器、插件扩展等进阶功能，比 Dev-C++ 更适合复杂项目。
- 适配场景：从新手入门到中小型项目开发，尤其适合需要跨平台编程的场景。


- 官方网址：Code::Blocks 官网
- 下载页面：Code::Blocks 发行版下载
- 安装要点：
    - 选择 "codeblocks-XX.XXmingw-setup.exe" 版本（含 MinGW 编译器，新手首选）；
    - 跨平台用户可下载 Linux/macOS 对应版本，需自行配置系统已安装的 GCC 编译器；
    - 首次启动会自动检测编译器，若提示 "未找到" 需手动指定 MinGW 的 bin 目录。