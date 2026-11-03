# 念安 TOUCHMIND · 开发文档（全量代码复现版）

本套文档把 `TOUGHMIND/` 仓库中的全部源码**逐文件、按可复现顺序**写入 Markdown：每个代码块上方标注仓库相对路径，复制到对应位置即可还原工程。文档由 `tools/gen_devdoc.py` 从源码直接生成，可用 `--check` 校验“清单与仓库源码一一对应”，因此不存在文档与代码不一致的问题。

适用范围：Android 客户端（Kotlin + Jetpack Compose + Room + DataStore + Retrofit + Paho MQTT + 百度地图/定位）、FastAPI 服务端（SQLite + EMQX + Ollama 转发）、以及单元测试与辅助脚本。二进制资源（PNG、APK、数据库、Gradle wrapper jar）不在文档内，仓库中直接保留原文件。

## 文档构成

| 篇 | 主题 | 文件数 | 代码行数 |
|---|---|---|---|
| [00](00-project-skeleton.md) | 工程骨架：Gradle、清单与资源 | 24 | 459 |
| [01](01-client-data.md) | 客户端数据层：Room、DataStore、网络与仓库 | 55 | 6388 |
| [02](02-app-shell-and-ui-kit.md) | 应用骨架与通用 UI | 26 | 6672 |
| [03](03-map-and-home.md) | 地图与首页 | 15 | 4314 |
| [04](04-calendar-checkin.md) | 行程、日历与打卡 | 9 | 2399 |
| [05](05-care-and-chat.md) | 亲友、关心与留言 | 20 | 5363 |
| [06](06-device-pet-agent.md) | 设备、宠物与智能体 | 10 | 4327 |
| [07](07-services-and-utils.md) | 后台服务与工具类 | 17 | 1374 |
| [08](08-server.md) | 服务端：FastAPI、SQLite 与部署 | 27 | 3159 |
| [09](09-tests-and-tools.md) | 客户端测试与工程脚本 | 10 | 1066 |
| 合计 | — | **213** | **35521** |

## 复现总览

1. **准备环境**：JDK 25、Android SDK（compileSdk 37 / buildTools 37.0.0）、Android Studio；服务端 Python 3.12+。
2. **按 00 篇创建工程骨架**：Gradle 配置、`AndroidManifest.xml`、`res/` 资源与主题。
3. **按 01–07 篇写入客户端代码**：数据层 → 应用骨架与通用组件 → 地图与首页 → 行程打卡 → 亲友关心 → 设备/宠物/智能体 → 后台服务与工具类。
4. **按 08 篇写入服务端**：`app/` 各模块、Dockerfile、compose 与部署脚本。
5. **按 09 篇写入测试与脚本**，然后执行构建与测试：

```powershell
$env:JAVA_HOME='<JDK 25 安装目录>'
.\gradlew.bat :app:assembleDebug "-Dorg.gradle.java.home=$env:JAVA_HOME"
.\gradlew.bat :app:testDebugUnitTest

cd server
.\.venv\Scripts\python.exe -m pytest tests -q
```

构建产物：`app/build/outputs/apk/debug/app-debug.apk`。

## 阅读与维护约定

- 路径一律相对仓库根目录 `TOUGHMIND/`，例如 `app/src/main/java/com/shineleong/toughmind/MainActivity.kt`。
- 代码块为源文件原文（仅统一换行符），注释、中文文案、资源名均未改写。
- 同一文件在整套文档中只出现一次；`--check` 会拒绝重复引用、漏写与多余条目。
- 修改代码后请重新执行 `python tools/gen_devdoc.py`，文档自动同步。
- 二进制资源（`res/**/*.png`、`*.apk`、`*.db`、wrapper jar）不进入文档，需从仓库原样获取。

## 校验

```bash
python tools/gen_devdoc.py --check   # 校验清单是否覆盖仓库全部源码
python tools/gen_devdoc.py           # 重新生成全部篇目
```
