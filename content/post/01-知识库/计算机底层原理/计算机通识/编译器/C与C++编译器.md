# 1. GCC、MinGW 是什么？

- GCC：全称 GNU Compiler Collection（GNU 编译器集合），是一套由 GNU 项目开发的开源编译器工具链，支持 C、C++、Java、Fortran 等多种编程语言。
    
- 它最初为类 Unix 系统（如 Linux、macOS）设计，是 Linux 系统下最常用的编译器，也是很多开源项目的默认编译工具。
    
- MinGW：全称 Minimalist GNU for Windows，是 GCC 在 Windows 平台上的 “移植版本”。
    
- 它的核心是将 GCC 编译器和相关工具适配到 Windows 系统，让开发者能在 Windows 环境下使用 GNU 工具链编译出原生的 Windows 可执行程序（.exe 文件），而无需依赖类 Unix 环境。
    

# 2. 核心区别

| 对比维度 | GCC                                 | MinGW                                  |
| ---- | ----------------------------------- | -------------------------------------- |
| 适用平台 | 主要用于 Linux、macOS 等类 Unix 系统         | 专为 Windows 系统设计                        |
| 编译目标 | 生成类 Unix 系统的可执行文件（如 Linux 的 ELF 格式） | 生成 Windows 原生可执行文件（.exe 格式）            |
| 系统依赖 | 依赖类 Unix 系统的底层库（如 glibc）            | 依赖 Windows 系统库（如 msvcrt.dll），无需额外运行时环境 |
| 功能侧重 | 完整支持类 Unix 系统的开发，工具链更全面             | 精简适配 Windows，专注生成 Windows 兼容程序         |

# 3. 下载与获取方式

1. GCC
    
    GCC 本身没有单独的 “安装包”，通常通过系统的包管理器获取（类 Unix 系统预装或一键安装）：

- Linux 系统：
    - Ubuntu/Debian：sudo apt install gcc（安装 C 编译器）、sudo apt install g++（安装 C++ 编译器）。
    - Fedora/RHEL：sudo dnf install gcc。
- macOS 系统：
    - 安装 Xcode Command Line Tools：xcode-select --install，内置 GCC（或 clang，与 GCC 兼容）。
- 官方参考：GNU 官网仅提供源码（需自行编译，不推荐新手），地址：[https://gcc.gnu.org/](https://gcc.gnu.org/)

2. MinGW（推荐 MinGW-w64）
    
    传统 MinGW 仅支持 32 位系统，现在更常用的是 MinGW-w64（支持 32 位和 64 位 Windows，功能更全）：

- 下载地址：
    - 官方网站：[https://www.mingw-w64.org/](https://www.mingw-w64.org/)
    - 直接下载安装器（推荐）：通过 SourceForge 下载预编译版本，地址：[https://sourceforge.net/projects/mingw-w64/](https://sourceforge.net/projects/mingw-w64/)
- 安装说明：
    - 下载后选择 “Architecture”（x86_64 对应 64 位，i686 对应 32 位），安装完成后将 bin 目录（如 C:\mingw64\bin）添加到系统环境变量，即可在命令行使用 gcc、g++ 命令。

简单说：如果在 Linux/macOS 上写 C 程序，直接用系统自带的 GCC；如果在 Windows 上开发，安装 MinGW-w64 即可使用 GCC 的编译功能。