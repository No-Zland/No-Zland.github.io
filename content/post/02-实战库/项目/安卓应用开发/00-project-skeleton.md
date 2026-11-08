# 00 · 工程骨架：Gradle、清单与资源

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

本篇从空目录开始，建立可被 Android Studio 直接打开的工程：Gradle 版本目录、应用模块构建脚本、`AndroidManifest.xml`、主题与颜色、字符串与备份规则。完成本篇后 `./gradlew :app:assembleDebug` 已有完整配置，只差 Kotlin 源码。

**二进制资源**：`res/**/*.png`（`app_logo.png`、`default_avatar.png`、各密度 `ic_launcher*.png` 与前景图）以及 `gradle/wrapper/gradle-wrapper.jar` 不进入文档，需从仓库原样复制；复现时也可先用同名占位图替换，不影响编译。`local.properties` 由 Android Studio 自动生成（写入本机 `sdk.dir`），无需手写。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. Gradle 工程配置](#s00-1) | 根工程只声明插件版本与仓库；依赖版本集中在 `gradle/libs.versions.toml`，避免在多处硬编码版本号。 | 5 |
| [2. 应用模块构建脚本与清单](#s00-2) | `app/build.gradle.kts` 决定 `applicationId`、`versionCode/versionName`、`BuildConfig` 注入的后端地址与密钥；`AndroidManifest.xml` 声明权限、Activity、前台服务与提醒广播。 | 3 |
| [3. 资源、主题与字符串](#s00-3) | XML 资源按分辨率与语言分目录；`values-night` 提供深色主题，`values-en` 提供英文回退文案。 | 16 |

本篇共 **3 个步骤 / 24 个文件**，按表格顺序写入即可还原对应代码。

<a id="s00-1"></a>

## 步骤 00.1 · Gradle 工程配置

根工程只声明插件版本与仓库；依赖版本集中在 `gradle/libs.versions.toml`，避免在多处硬编码版本号。

本步骤涉及的文件：

- `settings.gradle.kts`
- `build.gradle.kts`
- `gradle.properties`
- `gradle/libs.versions.toml`
- `gradle/wrapper/gradle-wrapper.properties`

### `settings.gradle.kts`

> 仓库地址与 `:app` 模块声明；依赖版本集中在 `gradle/libs.versions.toml`。

````kotlin
pluginManagement {
    repositories {
        maven(url = "https://maven.aliyun.com/repository/gradle-plugin")
        maven(url = "https://maven.aliyun.com/repository/google")
        maven(url = "https://maven.aliyun.com/repository/central")
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven(url = "https://maven.aliyun.com/repository/google")
        maven(url = "https://maven.aliyun.com/repository/central")
        google()
        mavenCentral()
        maven(url = "https://maven.lbsyun.baidu.com/repository/maven-releases/")
    }
}

rootProject.name = "TOUCHMIND"
include(":app")
 
````

### `build.gradle.kts`

> 根构建脚本，只声明插件版本（AGP / Kotlin / KSP）。

````kotlin
// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
````

### `gradle.properties`

> Gradle JVM 参数、configuration cache、AGP 9 的 Kotlin sourceSets 开关与 JDK 安装路径。

````properties
# Project-wide Gradle settings.
# IDE (e.g. Android Studio) users:
# Gradle settings configured through the IDE *will override*
# any settings specified in this file.
# For more details on how to configure your build environment visit
# http://www.gradle.org/docs/current/userguide/build_environment.html
# Specifies the JVM arguments used for the daemon process.
# The setting is particularly useful for tweaking memory settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
# When configured, Gradle will run in incubating parallel mode.
# This option should only be used with decoupled projects. For more details, visit
# https://developer.android.com/r/tools/gradle-multi-project-decoupled-projects
# org.gradle.parallel=true
# When enabled, the Configuration Cache allows Gradle to skip the configuration
# phase entirely if nothing that affects the build configuration (such as build scripts)
# has changed. Additionally, Gradle applies performance optimizations to task execution.
org.gradle.configuration-cache=true
# Kotlin code style for this project: "official" or "obsolete":
kotlin.code.style=official
# 允许 KSP 通过 kotlin.sourceSets 注入生成源码（AGP 9 内置 Kotlin 兼容）
android.disallowKotlinSourceSets=false
# 指定 JDK 安装路径，避免 AGP 误用不含 jlink 的 JRE（VS Code Java 扩展自带 JRE）
org.gradle.java.installations.paths=C:/Users/ziwuk/.jdks/openjdk-25.0.1
````

### `gradle/libs.versions.toml`

> 版本目录：所有依赖与插件的唯一版本来源。

````toml
[versions]
agp = "9.2.1"
kotlin = "2.2.10"
ksp = "2.2.10-2.0.2"
coreKtx = "1.15.0"
junit = "4.13.2"
junitVersion = "1.2.1"
espressoCore = "3.6.1"
lifecycle = "2.8.7"
activityCompose = "1.9.3"
composeBom = "2025.12.00"
materialIcons = "1.7.8"
navigationCompose = "2.8.5"
room = "2.7.1"
datastore = "1.1.1"
moshi = "1.15.1"
retrofit = "2.11.0"
okhttp = "4.12.0"
coroutines = "1.9.0"
paho = "1.2.5"
osmdroid = "6.1.20"

[libraries]
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version.ref = "coreKtx" }
androidx-lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version.ref = "lifecycle" }
androidx-lifecycle-viewmodel-compose = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }
androidx-lifecycle-runtime-compose = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycle" }
androidx-activity-compose = { group = "androidx.activity", name = "activity-compose", version.ref = "activityCompose" }
androidx-compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }
androidx-compose-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-compose-ui-graphics = { group = "androidx.compose.ui", name = "ui-graphics" }
androidx-compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
androidx-compose-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
androidx-compose-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }
androidx-compose-ui-test-junit4 = { group = "androidx.compose.ui", name = "ui-test-junit4" }
androidx-compose-material3 = { group = "androidx.compose.material3", name = "material3" }
androidx-compose-material-icons-core = { group = "androidx.compose.material", name = "material-icons-core", version.ref = "materialIcons" }
androidx-compose-material-icons-extended = { group = "androidx.compose.material", name = "material-icons-extended", version.ref = "materialIcons" }
androidx-navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigationCompose" }
androidx-room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
androidx-room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
androidx-room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
androidx-datastore-preferences = { group = "androidx.datastore", name = "datastore-preferences", version.ref = "datastore" }
moshi = { group = "com.squareup.moshi", name = "moshi", version.ref = "moshi" }
moshi-kotlin = { group = "com.squareup.moshi", name = "moshi-kotlin", version.ref = "moshi" }
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-converter-moshi = { group = "com.squareup.retrofit2", name = "converter-moshi", version.ref = "retrofit" }
okhttp = { group = "com.squareup.okhttp3", name = "okhttp", version.ref = "okhttp" }
okhttp-logging = { group = "com.squareup.okhttp3", name = "logging-interceptor", version.ref = "okhttp" }
kotlinx-coroutines-android = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }
paho-mqtt = { group = "org.eclipse.paho", name = "org.eclipse.paho.client.mqttv3", version.ref = "paho" }
osmdroid-android = { group = "org.osmdroid", name = "osmdroid-android", version.ref = "osmdroid" }
junit = { group = "junit", name = "junit", version.ref = "junit" }
androidx-junit = { group = "androidx.test.ext", name = "junit", version.ref = "junitVersion" }
androidx-espresso-core = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
````

### `gradle/wrapper/gradle-wrapper.properties`

> Gradle Wrapper 版本与分发地址（wrapper jar 为二进制，按仓库原样保留）。

````properties
#Wed Sep 09 08:39:23 CST 2026
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-9.4.1-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
````

<a id="s00-2"></a>

## 步骤 00.2 · 应用模块构建脚本与清单

`app/build.gradle.kts` 决定 `applicationId`、`versionCode/versionName`、`BuildConfig` 注入的后端地址与密钥；`AndroidManifest.xml` 声明权限、Activity、前台服务与提醒广播。

本步骤涉及的文件：

- `app/build.gradle.kts`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/keepRules/rules.keep`

### `app/build.gradle.kts`

> 应用模块：applicationId、versionCode 25 / 5.0.1、compileSdk 37，并通过 BuildConfig 注入后端地址、MQTT Broker、HMAC 与设备码密钥。

````kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.shineleong.toughmind"
    compileSdk {
        version = release(37)
    }
    buildToolsVersion = "37.0.0"

    defaultConfig {
        applicationId = "com.shineleong.toughmind"
        minSdk = 26
        targetSdk = 37
        versionCode = 25
        versionName = "5.0.1"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // MQTT 私有 Broker 与 HMAC 密钥（与设备端 config.py 对齐）
        buildConfigField("String", "MQTT_BROKER_URL", "\"tcp://47.93.173.214:1883\"")
        buildConfigField("String", "HMAC_SECRET_KEY", "\"toughmind_dms_hmac_key_2025\"")
        buildConfigField("String", "DEVICE_CODE_KEY", "\"toughmind-device-code-2026\"")
        // 后端服务（鉴权 + 关心组同步 + 大模型代理），部署于云服务器
        val localBackend = providers.gradleProperty("localBackend").orNull == "true"
        val backendBaseUrl = if (localBackend) {
            "http://127.0.0.1:8010/"
        } else {
            "http://47.93.173.214:8000/"
        }
        buildConfigField("String", "AUTH_BASE_URL", "\"$backendBaseUrl\"")
        buildConfigField("String", "LLM_BASE_URL", "\"$backendBaseUrl\"")
        buildConfigField("String", "LLM_API_KEY", "\"toughmind\"")
        buildConfigField("String", "LLM_MODEL", "\"qwen2.5:3b\"")
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons.core)
    implementation(libs.androidx.compose.material.icons.extended)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.room.runtime)
    implementation(libs.androidx.room.ktx)
    ksp(libs.androidx.room.compiler)
    implementation(libs.androidx.datastore.preferences)
    implementation(libs.moshi)
    implementation(libs.moshi.kotlin)
    implementation(libs.retrofit)
    implementation(libs.retrofit.converter.moshi)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.paho.mqtt)
    implementation(libs.osmdroid.android)
    implementation("com.baidu.lbsyun:BaiduMapSDK_Map:8.2.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Search:8.2.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Util:8.2.0")
    implementation("com.baidu.lbsyun:BaiduMapSDK_Location:9.6.4")
    testImplementation(libs.junit)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
    debugImplementation(libs.androidx.compose.ui.tooling)
}
````

### `app/src/main/AndroidManifest.xml`

> 权限、单 Activity、前台服务、提醒广播与备份规则。

````xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
    <!-- 亲属端（本机）定位权限：用于获取并展示亲属当前位置，计算与驾驶员的距离/方位 -->
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <queries>
        <package android:name="com.baidu.BaiduMap" />
        <package android:name="com.autonavi.minimap" />
        <package android:name="com.google.android.apps.maps" />
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>

    <application
        android:name=".ToughmindApplication"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.TOUGHMIND"
        android:usesCleartextTraffic="true">
        <meta-data
            android:name="com.baidu.lbsapi.API_KEY"
            android:value="jw7scgpExjSswMAWVhgie0pj8tDJfJcN" />

        <!-- 百度定位服务（独立进程做融合定位） -->
        <service
            android:name="com.baidu.location.f"
            android:enabled="true"
            android:process=":remote" />

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/app_name"
            android:theme="@style/Theme.TOUGHMIND"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

'        <service
            android:name=".service.CareBackgroundService"
            android:exported="false"
            android:foregroundServiceType="dataSync" />

        <!-- 日历提醒：到点通知 + 开机后恢复调度 -->'
        <receiver
            android:name=".service.ReminderReceiver"
            android:exported="false" />
        <receiver
            android:name=".service.ReminderBootReceiver"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
            </intent-filter>
        </receiver>
    </application>

</manifest>
````

### `app/src/main/keepRules/rules.keep`

> R8 保留规则，避免反射与序列化类被裁剪。

````text
# Add project specific R8 rules here.
# AGP will combine all keep rule files in src/main/keepRules to pass to R8
#
# For more details, see
#   https://d.android.com/r/tools/r8/keep-rules

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}
````

<a id="s00-3"></a>

## 步骤 00.3 · 资源、主题与字符串

XML 资源按分辨率与语言分目录；`values-night` 提供深色主题，`values-en` 提供英文回退文案。

本步骤涉及的文件：

- `app/src/main/res/drawable/ic_account_box.xml`
- `app/src/main/res/drawable/ic_favorite.xml`
- `app/src/main/res/drawable/ic_home.xml`
- `app/src/main/res/drawable/ic_launcher_background.xml`
- `app/src/main/res/drawable/ic_link.xml`
- `app/src/main/res/drawable/ic_my_location.xml`
- `app/src/main/res/mipmap-anydpi/ic_launcher.xml`
- `app/src/main/res/mipmap-anydpi/ic_launcher_round.xml`
- `app/src/main/res/values/colors.xml`
- `app/src/main/res/values/strings.xml`
- `app/src/main/res/values/themes.xml`
- `app/src/main/res/values-en/strings.xml`
- `app/src/main/res/values-night/colors.xml`
- `app/src/main/res/values-night/themes.xml`
- `app/src/main/res/xml/backup_rules.xml`
- `app/src/main/res/xml/data_extraction_rules.xml`

### `app/src/main/res/drawable/ic_account_box.xml`

````xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="960"
    android:viewportHeight="960">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M180,743Q240,687 315.9,652.5Q391.79,618 479.9,618Q568,618 644,652.5Q720,687 780,743L780,180Q780,180 780,180Q780,180 780,180L180,180Q180,180 180,180Q180,180 180,180L180,743ZM482,539Q540,539 580,499Q620,459 620,401Q620,343 580,303Q540,263 482,263Q424,263 384,303Q344,343 344,401Q344,459 384,499Q424,539 482,539ZM180,840Q156,840 138,822Q120,804 120,780L120,180Q120,156 138,138Q156,120 180,120L780,120Q804,120 822,138Q840,156 840,180L840,780Q840,804 822,822Q804,840 780,840L180,840ZM223,780L736,780Q736,780 736,780Q736,780 736,780Q674,727 610.5,702.5Q547,678 480,678Q413,678 349.5,702.5Q286,727 223,780Q223,780 223,780Q223,780 223,780ZM482,479Q449.5,479 426.75,456.25Q404,433.5 404,401Q404,368.5 426.75,345.75Q449.5,323 482,323Q514.5,323 537.25,345.75Q560,368.5 560,401Q560,433.5 537.25,456.25Q514.5,479 482,479ZM480,461L480,461Q480,461 480,461Q480,461 480,461L480,461Q480,461 480,461Q480,461 480,461L480,461Q480,461 480,461Q480,461 480,461Q480,461 480,461Q480,461 480,461Z" />
</vector>
````

### `app/src/main/res/drawable/ic_favorite.xml`

````xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="960"
    android:viewportHeight="960">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M480,839L439,802Q333.23,704.88 264.12,634.44Q195,564 154,508.5Q113,453 96.5,408Q80,363 80,317Q80,226.85 140.5,166.42Q201,106 290,106Q347,106 395.5,133Q444,160 480,211Q522,157 569,131.5Q616,106 670,106Q759,106 819.5,166.42Q880,226.85 880,317Q880,363 863.5,408Q847,453 806,508.5Q765,564 695.88,634.44Q626.77,704.88 521,802L480,839ZM480,760Q581.24,667 646.62,600.5Q712,534 750.5,484Q789,434 804.5,394.86Q820,355.73 820,317.14Q820,251 778,208.5Q736,166 670.22,166Q618.7,166 574.85,197.5Q531,229 504,286L504,286L455,286L455,286Q429,230 385.15,198Q341.3,166 289.78,166Q224,166 182,208.5Q140,251 140,317.32Q140,356 155.5,395.5Q171,435 209.5,485.5Q248,536 314,602Q380,668 480,760ZM480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463L480,463L480,463L480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Q480,463 480,463Z" />
</vector>
````

### `app/src/main/res/drawable/ic_home.xml`

````xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="960"
    android:viewportHeight="960">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M240,760L360,760L360,520L600,520L600,760L720,760L720,400L480,220L240,400L240,760ZM160,840L160,360L480,120L800,360L800,840L520,840L520,600L440,600L440,840L160,840ZM480,490L480,490L480,490L480,490L480,490L480,490L480,490L480,490L480,490Z" />
</vector>
````

### `app/src/main/res/drawable/ic_launcher_background.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M0,0h108v108h-108z" />
</vector>
````

### `app/src/main/res/drawable/ic_link.xml`

````xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M3.9,12c0,-1.71 1.39,-3.1 3.1,-3.1h4L11,7L7,7c-2.76,0 -5,2.24 -5,5s2.24,5 5,5h4v-1.9L7,15.1c-1.71,0 -3.1,-1.39 -3.1,-3.1zM8,13h8v-2L8,11v2zM17,7h-4v1.9h4c1.71,0 3.1,1.39 3.1,3.1s-1.39,3.1 -3.1,3.1h-4L13,17h4c2.76,0 5,-2.24 5,-5s-2.24,-5 -5,-5z" />
</vector>
````

### `app/src/main/res/drawable/ic_my_location.xml`

````xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="48"
    android:viewportHeight="48">
    <!-- 外圈光晕 -->
    <path
        android:fillColor="#3342A5F5"
        android:pathData="M24,0 a24,24 0 1,0 48,0 a24,24 0 1,0 -48,0" />
    <!-- 实心圆 -->
    <path
        android:fillColor="#FF1E88E5"
        android:pathData="M24,12 a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0" />
    <!-- 中心白点 -->
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M24,19 a5,5 0 1,0 10,0 a5,5 0 1,0 -10,0" />
</vector>
````

### `app/src/main/res/mipmap-anydpi/ic_launcher.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
````

### `app/src/main/res/mipmap-anydpi/ic_launcher_round.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
````

### `app/src/main/res/values/colors.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="window_background">#FFFFFFFF</color>
</resources>
````

### `app/src/main/res/values/strings.xml`

````xml
<resources>
    <string name="app_name">念安</string>
</resources>
````

### `app/src/main/res/values/themes.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.TOUGHMIND" parent="android:Theme.Material.Light.NoActionBar">
        <item name="android:windowBackground">@color/window_background</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">true</item>
        <item name="android:windowLightNavigationBar">true</item>
    </style>
</resources>
````

### `app/src/main/res/values-en/strings.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">TOUCHMIND</string>
</resources>
````

### `app/src/main/res/values-night/colors.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="window_background">#FF0A1B33</color>
</resources>
````

### `app/src/main/res/values-night/themes.xml`

````xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.TOUGHMIND" parent="android:Theme.Material.NoActionBar">
        <item name="android:windowBackground">@color/window_background</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowLightNavigationBar">false</item>
    </style>
</resources>
````

### `app/src/main/res/xml/backup_rules.xml`

````xml
<?xml version="1.0" encoding="utf-8"?><!--
   Sample backup rules file; uncomment and customize as necessary.
   See https://developer.android.com/guide/topics/data/autobackup
   for details.
   Note: This file is ignored for devices older than API 31
   See https://developer.android.com/about/versions/12/backup-restore
-->
<full-backup-content>
    <!--
   <include domain="sharedpref" path="."/>
   <exclude domain="sharedpref" path="device.xml"/>
-->
</full-backup-content>
````

### `app/src/main/res/xml/data_extraction_rules.xml`

````xml
<?xml version="1.0" encoding="utf-8"?><!--
   Sample data extraction rules file; uncomment and customize as necessary.
   See https://developer.android.com/about/versions/12/backup-restore#xml-changes
   for details.
-->
<data-extraction-rules>
    <cloud-backup>
        <!-- TODO: Use <include> and <exclude> to control what is backed up.
        <include .../>
        <exclude .../>
        -->
    </cloud-backup>
    <!--
    <device-transfer>
        <include .../>
        <exclude .../>
    </device-transfer>
    -->
</data-extraction-rules>
````

---

返回索引：[README.md](02-实战库/项目/安卓应用开发/README.md)
