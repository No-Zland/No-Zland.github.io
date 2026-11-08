# 02 · 应用骨架与通用 UI

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

本篇建立单 Activity 的 Compose 架构：`ToughmindApplication` → `AppContainer`（手动 DI）→ `MainActivity` → `MainScreen` 四入口导航（地图 / 行程 / 亲友 / 设备），并放入登录页、主题、语言表与复用组件。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 应用入口与依赖容器](#s02-1) | `AppContainer` 在 Application 启动时创建数据库、Retrofit、MQTT 与各仓库；ViewModel 通过 `AppViewModelProvider` 取得依赖，替代 Hilt。 | 5 |
| [2. 登录与账号](#s02-2) | 账号密码走 FastAPI `/api/auth/*`，成功后把 token 写入 DataStore，杀进程后可恢复登录态。 | 2 |
| [3. 主题与尺寸](#s02-3) | 浅色紫、深色暗金两套色板；关怀模式通过字号倍率与滑杆影响全局排版。 | 4 |
| [4. 语言与本地化](#s02-4) | 中文原文作为 key，英文翻译表与正则替换处理动态文案；`tr()`、`translate()` 与自定义 `Text` 让界面自动跟随语言设置。 | 1 |
| [5. 通用组件](#s02-5) | 状态选择器、悬浮桌宠、Live2D 宠物渲染、导航弹窗、朗读按钮等共享组件。 | 14 |

本篇共 **5 个步骤 / 26 个文件**，按表格顺序写入即可还原对应代码。

<a id="s02-1"></a>

## 步骤 02.1 · 应用入口与依赖容器

`AppContainer` 在 Application 启动时创建数据库、Retrofit、MQTT 与各仓库；ViewModel 通过 `AppViewModelProvider` 取得依赖，替代 Hilt。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ToughmindApplication.kt`
- `app/src/main/java/com/shineleong/toughmind/MainActivity.kt`
- `app/src/main/java/com/shineleong/toughmind/di/AppContainer.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/AppViewModelProvider.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/MainScreen.kt`

### `app/src/main/java/com/shineleong/toughmind/ToughmindApplication.kt`

> 应用级初始化：创建 AppContainer、通知渠道并恢复提醒。

````kotlin
package com.shineleong.toughmind

import android.app.Application
import com.baidu.location.LocationClient
import com.baidu.mapapi.SDKInitializer
import com.shineleong.toughmind.di.AppContainer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import org.osmdroid.config.Configuration
import java.io.File

class ToughmindApplication : Application() {

    lateinit var container: AppContainer
        private set

    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        initBaiduMap()
        initOsmdroid()
        container = AppContainer(this)
        runCatching {
            androidx.core.content.ContextCompat.startForegroundService(
                this,
                android.content.Intent(this, com.shineleong.toughmind.service.CareBackgroundService::class.java),
            )
        }
        appScope.launch {
            runCatching { container.preferences.clearLegacyDemoCompanion() }
            runCatching { container.reminderRepository.rescheduleAll() }
        }
    }

    /** 初始化百度地图 SDK，须先同意隐私协议再 initialize；同时同意定位 SDK 隐私合规。 */
    private fun initBaiduMap() {
        SDKInitializer.setAgreePrivacy(this, true)
        SDKInitializer.initialize(this)
        LocationClient.setAgreePrivacy(true)
    }

    /**
     * 初始化 osmdroid（备用开源引擎，MapConfig.USE_BAIDU=false 时启用）。
     * 设置 User-Agent 并指定缓存目录，避免依赖外部存储写入权限。
     */
    private fun initOsmdroid() {
        val config = Configuration.getInstance()
        config.load(this, getSharedPreferences("osmdroid", MODE_PRIVATE))
        config.userAgentValue = packageName
        config.osmdroidBasePath = File(cacheDir, "osmdroid")
        config.osmdroidTileCache = File(cacheDir, "osmdroid/tiles")
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/MainActivity.kt`

> 单 Activity 入口：设置 Compose 内容、系统栏与登录态判断。

````kotlin
package com.shineleong.toughmind

import android.Manifest
import android.content.pm.PackageManager
import android.content.res.Configuration
import android.os.Build
import android.os.Bundle
import android.view.WindowInsetsController
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.shineleong.toughmind.ui.MainScreen
import com.shineleong.toughmind.ui.component.LocalTextReader
import com.shineleong.toughmind.ui.component.LocalTtsMode
import com.shineleong.toughmind.ui.component.LocalTtsPreset
import com.shineleong.toughmind.ui.component.LocalTtsRate
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.screen.login.LoginScreen
import com.shineleong.toughmind.ui.theme.TOUGHMINDTheme
import com.shineleong.toughmind.util.TextReader
import com.shineleong.toughmind.util.TtsMode
import com.shineleong.toughmind.util.TtsPreset

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val isDark = isNightMode()
        enableEdgeToEdge(
            statusBarStyle = if (isDark) {
                SystemBarStyle.dark(android.graphics.Color.TRANSPARENT)
            } else {
                SystemBarStyle.light(
                    android.graphics.Color.TRANSPARENT,
                    android.graphics.Color.TRANSPARENT,
                )
            },
            navigationBarStyle = if (isDark) {
                SystemBarStyle.dark(android.graphics.Color.TRANSPARENT)
            } else {
                SystemBarStyle.light(
                    android.graphics.Color.TRANSPARENT,
                    android.graphics.Color.TRANSPARENT,
                )
            },
        )
        setContent {
            ToughmindRoot()
        }
    }

    override fun onResume() {
        super.onResume()
        val isDark = isNightMode()
        WindowCompat.getInsetsController(window, window.decorView).apply {
            isAppearanceLightStatusBars = !isDark
            isAppearanceLightNavigationBars = !isDark
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.insetsController?.setSystemBarsAppearance(
                if (isDark) 0 else WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS,
                WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS,
            )
        }
    }

    private fun isNightMode(): Boolean =
        (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) ==
            Configuration.UI_MODE_NIGHT_YES
}

@Composable
fun ToughmindRoot() {
    val app = LocalContext.current.applicationContext as ToughmindApplication
    val themeMode by app.container.preferences.themeMode
        .collectAsStateWithLifecycle(initialValue = "system")
    val language by app.container.preferences.language
        .collectAsStateWithLifecycle(initialValue = "zh")
    val elderMode by app.container.preferences.elderMode
        .collectAsStateWithLifecycle(initialValue = false)
    val fontScale by app.container.preferences.fontScale
        .collectAsStateWithLifecycle(initialValue = 1f)
    val speechRate by app.container.preferences.speechRate
        .collectAsStateWithLifecycle(initialValue = 1f)
    val ttsModeKey by app.container.preferences.ttsMode
        .collectAsStateWithLifecycle(initialValue = "offline")
    val ttsPresetKey by app.container.preferences.ttsPreset
        .collectAsStateWithLifecycle(initialValue = "auto")
    val textReader = remember { TextReader(app) }
    DisposableEffect(textReader) {
        onDispose { textReader.release() }
    }
    val darkTheme = when (themeMode) {
        "light" -> false
        "dark" -> true
        else -> isSystemInDarkTheme()
    }
    val baseDensity = LocalDensity.current
    val appliedFontScale = when {
        elderMode && fontScale <= 1.01f -> 1.25f
        else -> fontScale.coerceIn(1f, 1.5f)
    }
    TOUGHMINDTheme(darkTheme = darkTheme) {
        CompositionLocalProvider(
            LocalAppLanguage provides language,
            LocalDensity provides Density(
                density = baseDensity.density,
                fontScale = baseDensity.fontScale * appliedFontScale,
            ),
            LocalTextReader provides textReader,
            LocalTtsPreset provides TtsPreset.fromKey(ttsPresetKey),
            LocalTtsMode provides TtsMode.fromKey(ttsModeKey),
            LocalTtsRate provides speechRate.coerceIn(0.7f, 1.3f),
        ) {
            ToughmindApp()
        }
    }
}

@Composable
fun ToughmindApp() {
    val app = LocalContext.current.applicationContext as ToughmindApplication
    val user by app.container.authRepository.currentUser.collectAsStateWithLifecycle(initialValue = null)

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { }

    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val granted = ContextCompat.checkSelfPermission(
                app,
                Manifest.permission.POST_NOTIFICATIONS,
            ) == PackageManager.PERMISSION_GRANTED
            if (!granted) {
                permissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    if (user == null) {
        LoginScreen(onLoginSuccess = {})
    } else {
        MainScreen(onLogout = {})
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/di/AppContainer.kt`

> 手动依赖容器：数据库、Retrofit、MQTT、定位与各仓库的唯一装配点。

````kotlin
package com.shineleong.toughmind.di

import android.content.Context
import com.shineleong.toughmind.BuildConfig
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.AppDatabase
import com.shineleong.toughmind.data.remote.LlmServiceProvider
import com.shineleong.toughmind.data.remote.MqttClientManager
import com.shineleong.toughmind.data.remote.MqttConfig
import com.shineleong.toughmind.data.remote.MqttTopics
import com.shineleong.toughmind.data.remote.CareApiProvider
import com.shineleong.toughmind.data.remote.WeatherApi
import com.shineleong.toughmind.data.remote.XiaozhiChatService
import com.shineleong.toughmind.data.repository.AdviceRepository
import com.shineleong.toughmind.data.repository.AuthRepository
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.ChatMessageRepository
import com.shineleong.toughmind.data.repository.CheckInRepository
import com.shineleong.toughmind.data.repository.CheckInTaskRepository
import com.shineleong.toughmind.data.repository.CompanionRepository
import com.shineleong.toughmind.data.repository.DeviceRepository
import com.shineleong.toughmind.data.repository.EventRepository
import com.shineleong.toughmind.data.repository.LocationRepository
import com.shineleong.toughmind.data.repository.MqttRepository
import com.shineleong.toughmind.data.repository.ReminderRepository
import com.shineleong.toughmind.data.repository.SchedulePostRepository
import com.shineleong.toughmind.data.repository.WeatherRepository
import com.shineleong.toughmind.data.repository.XiaozhiRepository
import com.shineleong.toughmind.service.NotificationHelper
import com.shineleong.toughmind.service.ReminderScheduler
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

/**
 * 手动依赖注入容器（替代 Hilt，避免与 AGP 9 内置 Kotlin 的兼容风险）。
 */
class AppContainer(context: Context) {

    private val appContext = context.applicationContext

    val database: AppDatabase = AppDatabase.getInstance(appContext)
    val preferences = Preferences(appContext)

    val moshi: Moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()

    val notificationHelper = NotificationHelper(appContext)

    val mqttClientManager = MqttClientManager(
        MqttConfig(
            brokerUrl = BuildConfig.MQTT_BROKER_URL,
            clientId = "toughmind_app_${System.currentTimeMillis()}",
            topics = MqttTopics.SUBSCRIBE,
        )
    )

    val authRepository = AuthRepository(appContext, preferences, BuildConfig.AUTH_BASE_URL)
    val deviceRepository = DeviceRepository(database.deviceDao(), preferences)
    val eventRepository = EventRepository(database.eventDao())
    val adviceRepository = AdviceRepository(database.adviceDao())
    val locationRepository = LocationRepository(appContext)

    val mqttRepository = MqttRepository(
        mqttClientManager = mqttClientManager,
        moshi = moshi,
        hmacKey = BuildConfig.HMAC_SECRET_KEY,
        eventRepository = eventRepository,
        adviceRepository = adviceRepository,
        deviceRepository = deviceRepository,
        notificationHelper = notificationHelper,
        preferences = preferences,
    )

    val llmService = LlmServiceProvider.create()

    // AI 小智：对话服务 + 本地兜底
    val xiaozhiRepository = XiaozhiRepository(
        dao = database.xiaozhiMessageDao(),
        chatService = XiaozhiChatService(),
    )

    // ── "念安"亲友互相关心能力 ─────────────────────────────

    val companionRepository = CompanionRepository(preferences)

    private val weatherApi: WeatherApi = Retrofit.Builder()
        .baseUrl(WEATHER_BASE_URL)
        .addConverterFactory(MoshiConverterFactory.create(moshi))
        .build()
        .create(WeatherApi::class.java)

    val weatherRepository = WeatherRepository(weatherApi)

    val careRepository = CareRepository(
        context = appContext,
        preferences = preferences,
        companionRepository = companionRepository,
        mqttRepository = mqttRepository,
        locationRepository = locationRepository,
        weatherRepository = weatherRepository,
    )

    val checkInRepository = CheckInRepository(database.checkInDao())
    val chatMessageRepository = ChatMessageRepository(database.chatMessageDao())
    val checkInTaskRepository = CheckInTaskRepository(database.checkInTaskDao())
    val schedulePostRepository = SchedulePostRepository(database.schedulePostDao())

    val reminderScheduler = ReminderScheduler(appContext)
    val reminderRepository = ReminderRepository(database.reminderDao(), reminderScheduler)

    private val careApi = CareApiProvider.create(BuildConfig.AUTH_BASE_URL, moshi)

    val careSyncRepository = CareSyncRepository(
        api = careApi,
        preferences = preferences,
        careRepository = careRepository,
        checkInRepository = checkInRepository,
        reminderRepository = reminderRepository,
        schedulePostRepository = schedulePostRepository,
        checkInTaskRepository = checkInTaskRepository,
        notificationHelper = notificationHelper,
        mqttRepository = mqttRepository,
        deviceRepository = deviceRepository,
    )

    private companion object {
        const val WEATHER_BASE_URL = "https://api.open-meteo.com/"
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/AppViewModelProvider.kt`

> ViewModel 工厂：统一从 AppContainer 取仓库，替代 Hilt。

````kotlin
package com.shineleong.toughmind.ui

import androidx.lifecycle.ViewModelProvider.AndroidViewModelFactory.Companion.APPLICATION_KEY
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.shineleong.toughmind.ToughmindApplication
import com.shineleong.toughmind.ui.screen.advice.AdviceViewModel
import com.shineleong.toughmind.ui.screen.calendar.CalendarViewModel
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.screen.chat.ChatViewModel
import com.shineleong.toughmind.ui.screen.checkin.CheckInViewModel
import com.shineleong.toughmind.ui.screen.companion.CompanionViewModel
import com.shineleong.toughmind.ui.screen.device.DeviceViewModel
import com.shineleong.toughmind.ui.screen.history.HistoryViewModel
import com.shineleong.toughmind.ui.screen.home.HomeViewModel
import com.shineleong.toughmind.ui.screen.login.LoginViewModel
import com.shineleong.toughmind.ui.screen.profile.ProfileViewModel
import com.shineleong.toughmind.ui.screen.romance.RomanceViewModel
import com.shineleong.toughmind.ui.screen.xiaozhi.XiaozhiViewModel

object AppViewModelProvider {

    val Factory = viewModelFactory {
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            LoginViewModel(
                authRepository = app.container.authRepository,
                mqttRepository = app.container.mqttRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            ChatViewModel(
                chatRepository = app.container.chatMessageRepository,
                careSyncRepository = app.container.careSyncRepository,
                schedulePostRepository = app.container.schedulePostRepository,
                careRepository = app.container.careRepository,
                companionRepository = app.container.companionRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            HomeViewModel(
                careRepository = app.container.careRepository,
                careSyncRepository = app.container.careSyncRepository,
                mqttRepository = app.container.mqttRepository,
                deviceRepository = app.container.deviceRepository,
                preferences = app.container.preferences,
                locationRepository = app.container.locationRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            CareViewModel(
                careRepository = app.container.careRepository,
                adviceRepository = app.container.adviceRepository,
                llmService = app.container.llmService,
                checkInRepository = app.container.checkInRepository,
                preferences = app.container.preferences,
                careSyncRepository = app.container.careSyncRepository,
                weatherRepository = app.container.weatherRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            CalendarViewModel(
                checkInRepository = app.container.checkInRepository,
                preferences = app.container.preferences,
                reminderRepository = app.container.reminderRepository,
                schedulePostRepository = app.container.schedulePostRepository,
                companionRepository = app.container.companionRepository,
                careSyncRepository = app.container.careSyncRepository,
                careRepository = app.container.careRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            CheckInViewModel(
                checkInTaskRepository = app.container.checkInTaskRepository,
                checkInRepository = app.container.checkInRepository,
                preferences = app.container.preferences,
                careRepository = app.container.careRepository,
                careSyncRepository = app.container.careSyncRepository,
                companionRepository = app.container.companionRepository,
                chatMessageRepository = app.container.chatMessageRepository,
                schedulePostRepository = app.container.schedulePostRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            CompanionViewModel(
                app.container.companionRepository,
                app.container.careSyncRepository,
                app.container.careRepository,
                app.container.deviceRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            DeviceViewModel(
                app.container.deviceRepository,
                app.container.careSyncRepository,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            HistoryViewModel(app.container.eventRepository, app.container.preferences)
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            AdviceViewModel(app.container.adviceRepository, app.container.preferences)
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            RomanceViewModel(app.container.preferences)
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            XiaozhiViewModel(
                repository = app.container.xiaozhiRepository,
                careRepository = app.container.careRepository,
                preferences = app.container.preferences,
            )
        }
        initializer {
            val app = this[APPLICATION_KEY] as ToughmindApplication
            ProfileViewModel(
                app,
                app.container.authRepository,
                app.container.mqttRepository,
                app.container.preferences,
                app.container.careSyncRepository,
                app.container.xiaozhiRepository,
                app.container.careRepository,
            )
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/MainScreen.kt`

> 四入口 Scaffold：地图 / 行程 / 亲友 / 设备，抽屉与二级页面导航。

````kotlin
package com.shineleong.toughmind.ui

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBars
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Router
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.activity.compose.BackHandler
import android.app.Activity
import android.widget.Toast
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.User
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.FloatingPet
import com.shineleong.toughmind.ui.component.SelfStatusDialog
import com.shineleong.toughmind.ui.component.SelfStatusLine
import com.shineleong.toughmind.ui.component.selfStatusLabel
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.screen.friends.FriendsScreen
import com.shineleong.toughmind.ui.screen.pet.PetScreen
import com.shineleong.toughmind.ui.screen.trip.TripScreen
import com.shineleong.toughmind.ui.screen.romance.RomanceScreen
import com.shineleong.toughmind.ui.screen.companion.CompanionScreen
import com.shineleong.toughmind.ui.screen.companion.RelativeSettingsScreen
import com.shineleong.toughmind.ui.screen.device.DeviceScreen
import com.shineleong.toughmind.ui.screen.history.HistoryScreen
import com.shineleong.toughmind.ui.screen.home.HomeScreen
import com.shineleong.toughmind.ui.screen.profile.AboutScreen
import com.shineleong.toughmind.ui.screen.profile.ProfileScreen
import com.shineleong.toughmind.ui.screen.profile.ProfileViewModel
import com.shineleong.toughmind.ui.screen.profile.SettingsScreen
import com.shineleong.toughmind.ui.screen.xiaozhi.XiaozhiScreen
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.GoldDark
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.NavyDeep
import com.shineleong.toughmind.ui.theme.NavyOutline
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import kotlinx.coroutines.launch

enum class MainTab(val label: String, val icon: ImageVector) {
    MAP("地图", Icons.Filled.Map),
    TRIP("行程", Icons.Filled.CalendarMonth),
    FRIENDS("亲友", Icons.Filled.FavoriteBorder),
    DEVICE("设备", Icons.Filled.Router),
}

private enum class Screen(val title: String) {
    MAP(""),
    TRIP(""),
    FRIENDS(""),
    XIAOZHI("智能宠物"),
    PET("宠物小窝"),
    RELATIVE("亲友设置"),
    PROFILE("个人中心"),
    COMPANION("亲友与设备"),
    DEVICE("设备管理"),
    HISTORY("动态记录"),
    SETTINGS("设置"),
    ABOUT("关于念安"),
    ROMANCE("浪漫清单"),
}

private fun MainTab.toScreen(): Screen = when (this) {
    MainTab.MAP -> Screen.MAP
    MainTab.TRIP -> Screen.TRIP
    MainTab.FRIENDS -> Screen.FRIENDS
    MainTab.DEVICE -> Screen.DEVICE
}

private fun Screen.displayTitle(): String = when (this) {
    Screen.MAP -> "念安"
    Screen.TRIP -> "行程"
    Screen.FRIENDS -> "亲友"
    Screen.DEVICE -> "设备"
    Screen.XIAOZHI -> "智能宠物"
    else -> title
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(onLogout: () -> Unit) {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    var screen by rememberSaveable { mutableStateOf(Screen.MAP) }
    var previousScreen by rememberSaveable { mutableStateOf(Screen.MAP) }
    var focusPersonId by rememberSaveable { mutableStateOf<String?>(null) }
    var showHelp by rememberSaveable { mutableStateOf(false) }
    var mapNavigationActive by remember { mutableStateOf(false) }

    val profileViewModel: ProfileViewModel = viewModel(factory = AppViewModelProvider.Factory)
    val user by profileViewModel.user.collectAsStateWithLifecycle()
    val themeMode by profileViewModel.themeMode.collectAsStateWithLifecycle()
    val isDark = themeMode == "dark" || (themeMode == "system" && isSystemInDarkTheme())
    val imeVisible = WindowInsets.ime.getBottom(LocalDensity.current) > 0
    val avatarPath by profileViewModel.avatarPath.collectAsStateWithLifecycle()
    val petViewModel: CareViewModel = viewModel(factory = AppViewModelProvider.Factory)
    val pet by petViewModel.pet.collectAsStateWithLifecycle()
    val petLoaded by petViewModel.petLoaded.collectAsStateWithLifecycle()
    val appContext = LocalContext.current.applicationContext as com.shineleong.toughmind.ToughmindApplication
    val selfMood by appContext.container.preferences.moodEmoji
        .collectAsStateWithLifecycle(initialValue = "🙂")
    val selfMoodMessage by appContext.container.preferences.moodMessage
        .collectAsStateWithLifecycle(initialValue = "今天也要好好生活")

    // 定位在登录后的主界面期间保持运行；应用退到后台时停止，避免耗电。
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val repository = appContext.container.locationRepository
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_START -> if (repository.hasPermission()) repository.start()
                Lifecycle.Event.ON_STOP -> repository.stop()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        if (repository.hasPermission()) repository.start()
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            repository.stop()
        }
    }

    val avatarBitmap = remember(avatarPath) {
        if (avatarPath.isBlank()) null
        else runCatching { BitmapFactory.decodeFile(avatarPath)?.asImageBitmap() }.getOrNull()
    }

    val isSubScreen = screen != Screen.MAP && screen != Screen.TRIP &&
        screen != Screen.FRIENDS && screen != Screen.DEVICE && screen != Screen.XIAOZHI
    val isTabScreen = !isSubScreen
    var taskAddRequest by remember { mutableStateOf(0) }
    var calendarAddRequest by remember { mutableStateOf(0) }

    val uiContext = LocalContext.current
    var lastBackAt by remember { mutableStateOf(0L) }
    BackHandler {
        when {
            drawerState.isOpen -> scope.launch { drawerState.close() }
            isSubScreen -> screen = previousScreen
            screen != Screen.MAP -> screen = Screen.MAP
            else -> {
                val now = System.currentTimeMillis()
                if (now - lastBackAt <= 2_000L) {
                    (uiContext as? Activity)?.finish()
                } else {
                    lastBackAt = now
                    Toast.makeText(uiContext, "再按一次返回退出念安", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = drawerState.isOpen,
        drawerContent = {
            AppDrawerContent(
                user = user,
                avatarBitmap = avatarBitmap,
                selfMood = selfMood,
                selfMoodMessage = selfMoodMessage,
                isDark = isDark,
                onSetMood = { emoji, message ->
                    scope.launch {
                        appContext.container.preferences.setMood(emoji, message)
                    }
                },
                onToggleTheme = {
                    profileViewModel.setThemeMode(if (isDark) "light" else "dark")
                },
                onNavigate = { target ->
                    previousScreen = screen
                    screen = target
                    scope.launch { drawerState.close() }
                },
                onClose = { scope.launch { drawerState.close() } },
                onUpdateNickname = profileViewModel::updateNickname,
                onUpdateAvatar = profileViewModel::updateAvatar,
            )
        },
    ) {
        Scaffold(
            containerColor = SurfaceWhite,
            contentWindowInsets = if (screen == Screen.MAP) {
                WindowInsets(0, 0, 0, 0)
            } else {
                WindowInsets.systemBars
            },
            topBar = {
                if (screen != Screen.MAP) {
                    TopAppBar(
                        title = {
                            Text(
                                text = screen.displayTitle(),
                                fontWeight = FontWeight.Bold,
                            )
                        },
                        navigationIcon = {
                            if (isSubScreen) {
                                IconButton(onClick = { screen = previousScreen }) {
                                    Icon(
                                        Icons.AutoMirrored.Filled.ArrowBack,
                                        contentDescription = "返回",
                                        modifier = Modifier.size(AppDimens.IconSize),
                                    )
                                }
                            } else {
                                IconButton(onClick = { scope.launch { drawerState.open() } }) {
                                    Avatar(
                                        nickname = user?.nickname,
                                        size = 40.dp,
                                        imageBitmap = avatarBitmap,
                                        online = true,
                                        moodEmoji = selfMood,
                                        showStatusBadge = false,
                                    )
                                }
                            }
                        },
                        actions = {
                            if (screen == Screen.TRIP) {
                                IconButton(onClick = { taskAddRequest++ }) {
                                    Icon(
                                        Icons.Filled.Add,
                                        contentDescription = "添加任务",
                                        modifier = Modifier.size(AppDimens.IconSize),
                                    )
                                }
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = SurfaceWhite,
                            titleContentColor = TextPrimary,
                        ),
                    )
                }
            },
            bottomBar = {
                if (isTabScreen && !isSubScreen) {
                    NavigationBar(containerColor = SurfaceWhite) {
                        MainTab.entries.forEach { tab ->
                            NavigationBarItem(
                                selected = tab.toScreen() == screen,
                                onClick = { screen = tab.toScreen() },
                                icon = {
                                    Icon(
                                        tab.icon,
                                        contentDescription = tab.label,
                                        modifier = Modifier.size(AppDimens.IconSize),
                                    )
                                },
                                label = { Text(tab.label, maxLines = 1) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = MaterialTheme.colorScheme.onPrimaryContainer,
                                    selectedTextColor = MaterialTheme.colorScheme.primary,
                                    indicatorColor = MaterialTheme.colorScheme.primaryContainer,
                                    unselectedIconColor = TextSecondary,
                                    unselectedTextColor = TextSecondary,
                                ),
                            )
                        }
                    }
                }
            },
        ) { innerPadding ->
            Box(Modifier.fillMaxSize()) {
            if (screen == Screen.MAP) {
                HomeScreen(
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                    focusPersonId = focusPersonId,
                    onFocusConsumed = { focusPersonId = null },
                    onNavigationActiveChange = { mapNavigationActive = it },
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(bottom = innerPadding.calculateBottomPadding()),
                )
            } else {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                ) {
                    when (screen) {
                        Screen.TRIP -> TripScreen(
                            calendarAddRequest = calendarAddRequest,
                            onCalendarAddConsumed = { calendarAddRequest = 0 },
                            taskAddRequest = taskAddRequest,
                            onTaskAddConsumed = { taskAddRequest = 0 },
                        )
                        Screen.FRIENDS -> FriendsScreen(
                            onOpenMap = { personId ->
                                focusPersonId = personId
                                screen = Screen.MAP
                            },
                            onOpenCalendar = { screen = Screen.TRIP },
                            onOpenCompanion = {
                                previousScreen = screen
                                screen = Screen.RELATIVE
                            },
                            onOpenRomance = {
                                previousScreen = screen
                                screen = Screen.ROMANCE
                            },
                        )
                        Screen.XIAOZHI -> XiaozhiScreen()
                        Screen.PET -> PetScreen()
                        Screen.RELATIVE -> RelativeSettingsScreen()
                        Screen.PROFILE -> ProfileScreen()
                        Screen.COMPANION -> CompanionScreen()
                        Screen.DEVICE -> DeviceScreen()
                        Screen.HISTORY -> HistoryScreen()
                        Screen.SETTINGS -> SettingsScreen(
                            onLogout = onLogout,
                            onOpenAbout = {
                                previousScreen = screen
                                screen = Screen.ABOUT
                            },
                        )
                        Screen.ABOUT -> AboutScreen()
                        Screen.ROMANCE -> RomanceScreen()
                        else -> Unit
                    }
                }
            }
            if (petLoaded && pet.adopted && screen != Screen.PET && screen != Screen.XIAOZHI && !imeVisible && !mapNavigationActive) {
                FloatingPet(
                    pet = pet,
                    reaction = petViewModel.petReaction,
                    reactionToken = petViewModel.petReactionToken,
                    onClick = { screen = Screen.PET },
                    modifier = Modifier.fillMaxSize(),
                )
            }
            }
        }
    }
}

@Composable
private fun AppDrawerContent(
    user: User?,
    avatarBitmap: ImageBitmap?,
    selfMood: String,
    selfMoodMessage: String,
    isDark: Boolean,
    onToggleTheme: () -> Unit,
    onNavigate: (Screen) -> Unit,
    onClose: () -> Unit,
    onUpdateNickname: (String) -> Unit,
    onUpdateAvatar: (Bitmap) -> Unit,
    onSetMood: (String, String) -> Unit,
) {
    val context = LocalContext.current

    var showNicknameDialog by remember { mutableStateOf(false) }
    var nicknameInput by remember { mutableStateOf(user?.nickname.orEmpty()) }
    var showAvatarSheet by remember { mutableStateOf(false) }
    var showStatusDialog by remember { mutableStateOf(false) }

    val cameraLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicturePreview(),
    ) { bitmap -> if (bitmap != null) onUpdateAvatar(bitmap) }

    val galleryLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent(),
    ) { uri ->
        if (uri != null) {
            val bitmap = runCatching {
                context.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it) }
            }.getOrNull()
            if (bitmap != null) onUpdateAvatar(bitmap)
        }
    }

    ModalDrawerSheet(drawerContainerColor = SurfaceWhite) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
        ) {
            Column(Modifier.fillMaxWidth().padding(end = 36.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Avatar(
                        nickname = user?.nickname,
                        size = 52.dp,
                        imageBitmap = avatarBitmap,
                        online = true,
                        showStatusBadge = false,
                        modifier = Modifier.clickable { showAvatarSheet = true },
                    )
                    Spacer(Modifier.width(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text(
                            text = user?.nickname ?: "未登录",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary,
                            modifier = Modifier.clickable {
                                nicknameInput = user?.nickname.orEmpty()
                                showNicknameDialog = true
                            },
                        )
                        Text(
                            text = "账号：${user?.account ?: "--"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                        Spacer(Modifier.height(2.dp))
                        SelfStatusLine(
                            emoji = selfMood,
                            status = selfStatusLabel(selfMood, selfMoodMessage),
                            onClick = { showStatusDialog = true },
                        )
                    }
                }
                Spacer(Modifier.height(14.dp))
                Text(
                    text = "念安 · 把牵挂放在看得见的地方",
                    style = MaterialTheme.typography.bodySmall,
                    color = GoldDark,
                )
            }
            IconButton(
                onClick = onClose,
                modifier = Modifier.align(Alignment.TopEnd),
            ) {
                Icon(
                    Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "关闭抽屉",
                    modifier = Modifier.size(AppDimens.IconSize),
                )
            }
        }

        HorizontalDivider(color = NavyOutline)

        DrawerItem("个人中心", icon = Icons.Filled.Person) { onNavigate(Screen.PROFILE) }
        DrawerItem("智能宠物", icon = Icons.Filled.SmartToy) { onNavigate(Screen.XIAOZHI) }
        DrawerItem("宠物小窝", icon = Icons.Filled.FavoriteBorder) { onNavigate(Screen.PET) }
        DrawerItem("亲友与设备", icon = Icons.Filled.Link) { onNavigate(Screen.COMPANION) }
        DrawerItem("动态记录", icon = Icons.Filled.History) { onNavigate(Screen.HISTORY) }

        Spacer(Modifier.weight(1f))

        HorizontalDivider(color = NavyOutline)
        DrawerItem(
            label = "设置",
            icon = Icons.Filled.Settings,
            onClick = { onNavigate(Screen.SETTINGS) },
            trailing = {
                IconButton(onClick = onToggleTheme) {
                    Icon(
                        if (isDark) Icons.Filled.LightMode else Icons.Filled.DarkMode,
                        contentDescription = "切换明暗模式",
                        tint = Gold,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                }
            },
        )
    }


    if (showNicknameDialog) {
        AlertDialog(
            onDismissRequest = { showNicknameDialog = false },
            title = { Text("修改昵称") },
            text = {
                OutlinedTextField(
                    value = nicknameInput,
                    onValueChange = { nicknameInput = it },
                    singleLine = true,
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        val name = nicknameInput.trim()
                        if (name.isNotEmpty()) onUpdateNickname(name)
                        showNicknameDialog = false
                    },
                ) { Text("保存") }
            },
            dismissButton = {
                TextButton(onClick = { showNicknameDialog = false }) { Text("取消") }
            },
        )
    }

    if (showStatusDialog) {
        SelfStatusDialog(
            initialEmoji = selfMood,
            initialMessage = selfMoodMessage,
            onDismiss = { showStatusDialog = false },
            onSave = { emoji, message ->
                onSetMood(emoji, message)
                showStatusDialog = false
            },
        )
    }

    if (showAvatarSheet) {
        AlertDialog(
            onDismissRequest = { showAvatarSheet = false },
            title = { Text("更换头像") },
            text = {
                Column {
                    TextButton(
                        onClick = {
                            showAvatarSheet = false
                            cameraLauncher.launch(null)
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("拍照") }
                    TextButton(
                        onClick = {
                            showAvatarSheet = false
                            galleryLauncher.launch("image/*")
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("从相册选择") }
                }
            },
            confirmButton = {},
            dismissButton = {
                TextButton(onClick = { showAvatarSheet = false }) { Text("取消") }
            },
        )
    }
}

@Composable
private fun DrawerItem(
    label: String,
    icon: ImageVector? = null,
    painter: Painter? = null,
    trailing: (@Composable () -> Unit)? = null,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 20.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (painter != null) {
            Icon(
                painter = painter,
                contentDescription = label,
                tint = Gold,
                modifier = Modifier.size(AppDimens.IconSize),
            )
        } else if (icon != null) {
            Icon(
                icon,
                contentDescription = label,
                tint = Gold,
                modifier = Modifier.size(AppDimens.IconSize),
            )
        }
        Text(label, style = MaterialTheme.typography.bodyLarge, color = TextPrimary)
        if (trailing != null) {
            Spacer(Modifier.weight(1f))
            trailing()
        }
    }
}
````

<a id="s02-2"></a>

## 步骤 02.2 · 登录与账号

账号密码走 FastAPI `/api/auth/*`，成功后把 token 写入 DataStore，杀进程后可恢复登录态。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/login/LoginScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/login/LoginViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/login/LoginScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.login

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.R
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.SurfaceTint
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    viewModel: LoginViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    var isRegister by rememberSaveable { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.verticalGradient(listOf(SurfaceWhite, SurfaceTint))),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 28.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Image(
                painter = painterResource(R.drawable.app_logo),
                contentDescription = "logo",
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(20.dp)),
                contentScale = ContentScale.Crop,
            )
            Spacer(Modifier.height(20.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(width = 5.dp, height = 30.dp)
                        .clip(RoundedCornerShape(3.dp))
                        .background(Gold)
                )
                Spacer(Modifier.width(12.dp))
                Text(
                    text = "念安",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                )
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text = "把牵挂放在看得见的地方",
                style = MaterialTheme.typography.bodyLarge,
                color = TextSecondary,
            )
            Spacer(Modifier.height(40.dp))

            OutlinedTextField(
                value = viewModel.account,
                onValueChange = viewModel::onAccountChange,
                label = { Text("账号 / 手机号") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = viewModel.password,
                onValueChange = viewModel::onPasswordChange,
                label = { Text("密码") },
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
            )

            viewModel.error?.let {
                Spacer(Modifier.height(12.dp))
                Text(
                    text = it,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            Spacer(Modifier.height(24.dp))
            TechButton(
                text = if (isRegister) "注册并登录" else "登录",
                onClick = {
                    if (isRegister) viewModel.register(onLoginSuccess) else viewModel.login(onLoginSuccess)
                },
                enabled = !viewModel.loading,
                loading = viewModel.loading,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
            )
            Spacer(Modifier.height(8.dp))
            TextButton(onClick = { isRegister = !isRegister }) {
                Text(
                    text = if (isRegister) "已有账号？去登录" else "没有账号？去注册",
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/login/LoginViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.login

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.repository.AuthRepository
import com.shineleong.toughmind.data.repository.MqttRepository
import kotlinx.coroutines.launch

class LoginViewModel(
    private val authRepository: AuthRepository,
    private val mqttRepository: MqttRepository,
) : ViewModel() {

    var account by mutableStateOf("")
    var password by mutableStateOf("")
    var loading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    fun onAccountChange(value: String) {
        account = value
    }

    fun onPasswordChange(value: String) {
        password = value
    }

    fun login(onSuccess: () -> Unit) {
        if (!validate()) return
        viewModelScope.launch {
            loading = true
            error = null
            authRepository.login(account.trim(), password)
                .onSuccess {
                    mqttRepository.start()
                    onSuccess()
                }
                .onFailure { error = it.message ?: "登录失败" }
            loading = false
        }
    }

    fun register(onSuccess: () -> Unit) {
        if (!validate()) return
        viewModelScope.launch {
            loading = true
            error = null
            authRepository.register(account.trim(), password)
                .onSuccess {
                    mqttRepository.start()
                    onSuccess()
                }
                .onFailure { error = it.message ?: "注册失败" }
            loading = false
        }
    }

    private fun validate(): Boolean {
        if (account.isBlank() || password.isBlank()) {
            error = "请输入账号和密码"
            return false
        }
        if (password.length < 6) {
            error = "密码长度至少 6 位"
            return false
        }
        return true
    }
}
````

<a id="s02-3"></a>

## 步骤 02.3 · 主题与尺寸

浅色紫、深色暗金两套色板；关怀模式通过字号倍率与滑杆影响全局排版。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/theme/AppDimens.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/theme/Color.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/theme/Theme.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/theme/Type.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/theme/AppDimens.kt`

````kotlin
package com.shineleong.toughmind.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.unit.dp

/** 全 App 统一的操作尺寸，避免每个页面各写一套。 */
object AppDimens {
    /** 所有胶囊/椭圆按键统一高度。 */
    val ButtonHeight = 44.dp

    /** 按键圆角：5pt，不再使用完整胶囊。 */
    val ButtonCorner = 5.dp

    val ButtonShape = RoundedCornerShape(ButtonCorner)

    /** 图标统一 20pt。 */
    val IconSize = 20.dp

    /** 图标 / 文字到按键或卡片边缘的统一留白。 */
    val ContentPaddingHorizontal = 16.dp
    val ContentPaddingVertical = 12.dp

    /** 页面与卡片之间的常用间距。 */
    val ScreenPadding = 16.dp
    val CardCorner = 12.dp
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/theme/Color.kt`

````kotlin
package com.shineleong.toughmind.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

// ═══════════════════════════════════════════════════════════════
// 原始色板
// 浅色：白色主调 + 紫色 / 青色 / 绿色辅助
// 深色：藏蓝主调 + 黑金 / 墨绿 / 暗紫辅助
// ═══════════════════════════════════════════════════════════════

// 浅色
val LightSurface = Color(0xFFFFFFFF)
val LightSurfaceSoft = Color(0xFFF8F6FF)
val LightSurfaceTint = Color(0xFFF1EDFF)
val LightSurfaceSubtle = Color(0xFFEEF7F9)
val LightOnSurface = Color(0xFF141A2E)
val LightOnSurfaceVariant = Color(0xFF5E667A)
val LightPrimary = Color(0xFF6C4DF6)          // 紫
val LightPrimaryContainer = Color(0xFFEDE8FF)
val LightOnPrimaryContainer = Color(0xFF2A1A5E)
val LightSecondary = Color(0xFF0891B2)        // 青
val LightSecondaryContainer = Color(0xFFDDF7FA)
val LightOnSecondaryContainer = Color(0xFF003A43)
val LightTertiary = Color(0xFF16A36A)         // 绿
val LightTertiaryContainer = Color(0xFFDDF6E9)
val LightOnTertiaryContainer = Color(0xFF053B24)
val LightOutline = Color(0xFFD9E2EC)
val LightError = Color(0xFFD92D20)

// 深色
val DarkSurface = Color(0xFF0A1B33)            // 藏蓝
val DarkSurfaceSoft = Color(0xFF102946)
val DarkSurfaceTint = Color(0xFF142F52)
val DarkSurfaceSubtle = Color(0xFF16355A)
val DarkOnSurface = Color(0xFFF1F5FB)
val DarkOnSurfaceVariant = Color(0xFFA9B7CC)
val DarkPrimary = Color(0xFFD4AF37)           // 黑金
val DarkPrimaryContainer = Color(0xFF3A2E0C)
val DarkOnPrimaryContainer = Color(0xFFF5DF95)
val DarkSecondary = Color(0xFF4E9B7A)         // 墨绿
val DarkSecondaryContainer = Color(0xFF163B2D)
val DarkOnSecondaryContainer = Color(0xFFBFE8D6)
val DarkTertiary = Color(0xFF9B7BD4)          // 暗紫
val DarkTertiaryContainer = Color(0xFF2C1F45)
val DarkOnTertiaryContainer = Color(0xFFE0D2FA)
val DarkOutline = Color(0xFF2C4A6E)
val DarkError = Color(0xFFFF6B6B)

// ═══════════════════════════════════════════════════════════════
// 自定义语义色（主题切换时自动变化）
// ═══════════════════════════════════════════════════════════════

@Immutable
data class CareColors(
    val isDark: Boolean,
    val cardGradient: List<Color>,
    val accentGradient: List<Color>,
    val heroGradient: List<Color>,
    val checkInBoth: Color,
    val checkInSelf: Color,
    val checkInPartner: Color,
    val mapOverlay: Color,
    val cyan: Color,
    val green: Color,
    val purple: Color,
    val gold: Color,
    val mapBackground: Color,
)

val LightCareColors = CareColors(
    isDark = false,
    cardGradient = listOf(LightSurface, LightSurfaceSoft, LightSurfaceTint),
    accentGradient = listOf(LightPrimary, LightSecondary),
    heroGradient = listOf(LightPrimary, Color(0xFF5B7CFA), LightSecondary),
    checkInBoth = Color(0xFFE5484D),
    checkInSelf = LightPrimary,
    checkInPartner = LightSecondary,
    mapOverlay = Color.White.copy(alpha = 0.94f),
    cyan = LightSecondary,
    green = LightTertiary,
    purple = LightPrimary,
    gold = LightPrimary,
    mapBackground = Color(0xFFE8EDF4),
)

val DarkCareColors = CareColors(
    isDark = true,
    cardGradient = listOf(DarkSurfaceSoft, DarkSurface, DarkSurfaceTint),
    accentGradient = listOf(DarkPrimary, DarkTertiary),
    heroGradient = listOf(Color(0xFF241B3D), DarkSurface, Color(0xFF123A31)),
    checkInBoth = Color(0xFFFF6B6B),
    checkInSelf = DarkPrimary,
    checkInPartner = DarkSecondary,
    mapOverlay = DarkSurface.copy(alpha = 0.94f),
    cyan = Color(0xFF4FC3D9),
    green = DarkSecondary,
    purple = DarkTertiary,
    gold = DarkPrimary,
    mapBackground = DarkSurface,
)

val LocalCareColors = staticCompositionLocalOf { LightCareColors }

// ═══════════════════════════════════════════════════════════════
// 兼容旧代码的语义色：直接映射到 MaterialTheme
// ═══════════════════════════════════════════════════════════════

val SurfaceWhite: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.surface

val SurfaceLight: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.surface

val SurfaceTint: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.surfaceVariant

val SurfaceSubtle: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.surfaceVariant

val NavyDeep: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.onSurface

val NavyPrimary: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.primary

val NavyPrimaryLight: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.secondary

val NavyPrimaryDark: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.scrim

val NavyOutline: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.outline

val Gold: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.primary

val GoldLight: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.primaryContainer

val GoldDark: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.primary

val GoldDeep: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.onPrimaryContainer

val TextPrimary: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.onSurface

val TextSecondary: Color
    @Composable @ReadOnlyComposable get() = MaterialTheme.colorScheme.onSurfaceVariant

// ═══════════════════════════════════════════════════════════════
// 状态分级色（在浅色 / 深色下都保持可读）
// ═══════════════════════════════════════════════════════════════

val LevelNormal = Color(0xFF16A36A)      // 绿
val LevelMild = Color(0xFFE0A800)        // 黄
val LevelModerate = Color(0xFFF08A24)    // 橙
val LevelSevere = Color(0xFFE5484D)      // 红
val LevelMedical = Color(0xFF9B7BD4)     // 紫

// ── 双人打卡 / 关心 ──
val CareRed = Color(0xFFE5484D)          // 双方都打卡：红
val CareRedDark = Color(0xFFC93631)
val CareBlue = Color(0xFF0891B2)         // TA 的打卡点：青
val CareGreen = Color(0xFF16A36A)
````

### `app/src/main/java/com/shineleong/toughmind/ui/theme/Theme.kt`

````kotlin
package com.shineleong.toughmind.ui.theme

import android.app.Activity
import android.content.Context
import android.content.ContextWrapper
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// 浅色：白色主调 + 紫色 / 青色 / 绿色辅助
private val LightColorScheme = lightColorScheme(
    primary = LightPrimary,
    onPrimary = Color.White,
    primaryContainer = LightPrimaryContainer,
    onPrimaryContainer = LightOnPrimaryContainer,
    secondary = LightSecondary,
    onSecondary = Color.White,
    secondaryContainer = LightSecondaryContainer,
    onSecondaryContainer = LightOnSecondaryContainer,
    tertiary = LightTertiary,
    onTertiary = Color.White,
    tertiaryContainer = LightTertiaryContainer,
    onTertiaryContainer = LightOnTertiaryContainer,
    background = LightSurface,
    onBackground = LightOnSurface,
    surface = LightSurface,
    onSurface = LightOnSurface,
    surfaceVariant = LightSurfaceSubtle,
    onSurfaceVariant = LightOnSurfaceVariant,
    outline = LightOutline,
    error = LightError,
    onError = Color.White,
    scrim = Color(0xFF0A1B33),
)

// 深色：藏蓝主调 + 黑金 / 墨绿 / 暗紫辅助
private val DarkColorScheme = darkColorScheme(
    primary = DarkPrimary,
    onPrimary = Color(0xFF1A1405),
    primaryContainer = DarkPrimaryContainer,
    onPrimaryContainer = DarkOnPrimaryContainer,
    secondary = DarkSecondary,
    onSecondary = Color(0xFF06140F),
    secondaryContainer = DarkSecondaryContainer,
    onSecondaryContainer = DarkOnSecondaryContainer,
    tertiary = DarkTertiary,
    onTertiary = Color(0xFF1B1030),
    tertiaryContainer = DarkTertiaryContainer,
    onTertiaryContainer = DarkOnTertiaryContainer,
    background = DarkSurface,
    onBackground = DarkOnSurface,
    surface = DarkSurface,
    onSurface = DarkOnSurface,
    surfaceVariant = DarkSurfaceSubtle,
    onSurfaceVariant = DarkOnSurfaceVariant,
    outline = DarkOutline,
    error = DarkError,
    onError = Color(0xFF2A0000),
    scrim = Color(0xFF000000),
)

@Composable
fun TOUGHMINDTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val careColors = if (darkTheme) DarkCareColors else LightCareColors

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = view.context.findActivity()?.window ?: return@SideEffect
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = !darkTheme
                isAppearanceLightNavigationBars = !darkTheme
            }
        }
    }

    CompositionLocalProvider(LocalCareColors provides careColors) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            content = content
        )
    }
}

private fun Context.findActivity(): Activity? {
    var context = this
    while (context is ContextWrapper) {
        if (context is Activity) return context
        context = context.baseContext
    }
    return null
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/theme/Type.kt`

````kotlin
package com.shineleong.toughmind.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// 科技感排版：标题加粗、正文略收紧字距
val Typography = Typography(
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 30.sp,
        lineHeight = 38.sp,
        letterSpacing = 0.5.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        lineHeight = 30.sp,
        letterSpacing = 0.3.sp
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.2.sp
    ),
    titleMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.2.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.3.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.3.sp
    ),
    bodySmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.3.sp
    ),
    labelLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.5.sp
    )
)
````

<a id="s02-4"></a>

## 步骤 02.4 · 语言与本地化

中文原文作为 key，英文翻译表与正则替换处理动态文案；`tr()`、`translate()` 与自定义 `Text` 让界面自动跟随语言设置。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/i18n/Language.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/i18n/Language.kt`

````kotlin
package com.shineleong.toughmind.ui.i18n

import androidx.compose.runtime.compositionLocalOf

/** 当前界面语言：zh / en。 */
val LocalAppLanguage = compositionLocalOf { "zh" }

const val LANG_ZH = "zh"
const val LANG_EN = "en"
````

<a id="s02-5"></a>

## 步骤 02.5 · 通用组件

状态选择器、悬浮桌宠、Live2D 宠物渲染、导航弹窗、朗读按钮等共享组件。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/component/CareComponents.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/CompanionAnimals.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/CompanionScene.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/Components.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/FloatingPet.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/LocalizedText.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/LocalizedTextTable.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/NavigationDialog.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/OwlLive2D.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/OwlParts.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/OwlScene.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/PetLive2D.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/ReadAloudButton.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/component/StatusPicker.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/component/CareComponents.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** 状态色板：在浅色 / 深色下都保持足够对比度。 */
fun CareStatus.toColor(): Color = when (this) {
    CareStatus.ONLINE -> Color(0xFF16A36A)
    CareStatus.STUDYING -> Color(0xFF7C5CFF)
    CareStatus.WORKING -> Color(0xFF2F80ED)
    CareStatus.COMMUTE -> Color(0xFF0891B2)
    CareStatus.DRIVING -> Color(0xFFD4AF37)
    CareStatus.RESTING -> Color(0xFF16A36A)
    CareStatus.SLEEPING -> Color(0xFF8A9BB3)
    CareStatus.EXERCISING -> Color(0xFFF08A24)
    CareStatus.TIRED -> Color(0xFFE0A800)
    CareStatus.SOS -> Color(0xFFE5484D)
    CareStatus.UNKNOWN -> Color(0xFF94A3B8)
}

fun DeviceType.iconLabel(): String = when (this) {
    DeviceType.PHONE -> "📱 手机"
    DeviceType.ESP32 -> "设备"
}

/** 圆形状态胶囊，如"📚 学习中"。 */
@Composable
fun CareStatusBadge(
    status: CareStatus,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    val color = status.toColor()
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(50),
        color = color.copy(alpha = 0.16f),
        contentColor = color,
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(5.dp),
            modifier = Modifier.padding(horizontal = 10.dp, vertical = if (compact) 4.dp else 6.dp),
        ) {
            StatusGridBadge(
                color = color,
                online = status != CareStatus.UNKNOWN,
                modifier = Modifier.size(13.dp),
            )
            Text(
                text = statusEnglish(status),
                style = if (compact) MaterialTheme.typography.bodySmall else MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

@Composable
fun statusEnglish(status: CareStatus): String = tr(
    status.label,
    when (status) {
        CareStatus.ONLINE -> "Online"
        CareStatus.STUDYING -> "Studying"
        CareStatus.WORKING -> "Working"
        CareStatus.COMMUTE -> "Commuting"
        CareStatus.DRIVING -> "Driving"
        CareStatus.RESTING -> "Resting"
        CareStatus.SLEEPING -> "Sleeping"
        CareStatus.EXERCISING -> "Exercising"
        CareStatus.TIRED -> "Tired"
        CareStatus.SOS -> "SOS"
        CareStatus.UNKNOWN -> "Unknown"
    },
)

/** 地图上的天气小胶囊：表情 + 温度 + 城市/称呼。 */
@Composable
fun WeatherPill(
    label: String,
    weather: WeatherInfo?,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(50),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.94f),
        contentColor = MaterialTheme.colorScheme.onSurface,
        shadowElevation = 6.dp,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(text = weather?.emoji ?: "🌡️", style = MaterialTheme.typography.bodyLarge)
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = weather?.let { "${it.temperatureC.toInt()}°" } ?: "--",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
            )
            if (weather != null) {
                Text(
                    text = translateText(weather.label, LocalAppLanguage.current),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

/** 天气详情卡：用于头像详情与关心页的"双方天气"。 */
@Composable
fun WeatherInfoCard(
    title: String,
    weather: WeatherInfo?,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 0.dp,
        shadowElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (weather == null) {
                Text(
                    text = "天气获取中…",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(weather.emoji, style = MaterialTheme.typography.headlineSmall)
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = "${weather.temperatureC.toInt()}℃",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = translateText(weather.label, LocalAppLanguage.current),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Text(
                    text = if (LocalAppLanguage.current == "en") {
                        "Feels ${weather.apparentC.toInt()}℃ · Humidity ${weather.humidity}% · Wind ${weather.windKmh.toInt()} km/h"
                    } else {
                        "体感 ${weather.apparentC.toInt()}℃ · 湿度 ${weather.humidity}% · 风速 ${weather.windKmh.toInt()} km/h"
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

/** 距离格式化。 */
fun formatDistance(meters: Double?): String {
    if (meters == null) return "距离未知"
    return if (meters < 1000) {
        "${meters.toInt()} m"
    } else {
        "%.2f km".format(meters / 1000)
    }
}

/** "刚刚 / 3 分钟前 / 昨天 12:00" 之类的时间显示。 */
fun formatRelativeTime(millis: Long): String {
    if (millis <= 0) return "--"
    val diff = System.currentTimeMillis() - millis
    return when {
        diff < 60_000 -> "刚刚"
        diff < 60 * 60_000 -> "${diff / 60_000} 分钟前"
        diff < 24 * 60 * 60_000 -> "${diff / 3_600_000} 小时前"
        else -> SimpleDateFormat("MM-dd HH:mm", Locale.getDefault()).format(Date(millis))
    }
}

/** 设置页 / 详情页常用的一行信息。 */
@Composable
fun InfoLine(label: String, value: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = MaterialTheme.colorScheme.onSurface,
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/CompanionAnimals.kt`

> 墨猫、田园犬、仓鼠的绘制与爱心/碎屑动效。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

internal fun DrawScope.drawInkCat(
    tail: Float,
    blink: Float,
    gazeX: Float,
    gazeY: Float,
    earTwitch: Float,
    step: Float,
    groom: Float,
    asleep: Boolean,
    sleepy: Boolean,
    scene: CompanionScene,
) {
    val wag = sin(tail * PI * 2).toFloat()
    val stepA = if (step > 0f) sin(step * PI * 2).toFloat() * 3.5f else 0f
    val stepB = if (step > 0f) sin(step * PI * 2 + PI).toFloat() * 3.5f else 0f
    val lick = if (groom > 0f) abs(sin(groom * PI * 3).toFloat()) else 0f
    val headDip = lick * 7f
    // 尾巴
    val tailPath = Path().apply {
        moveTo(238f, 218f)
        cubicTo(286f, 226f + wag * 8f, 306f, 184f + wag * 10f, 286f, 156f + wag * 6f)
    }
    drawPath(
        tailPath,
        color = scene.fur,
        style = Stroke(width = 18f, cap = StrokeCap.Round),
    )

    // 身体
    drawOval(scene.fur, Offset(112f, 158f), Size(136f, 108f))
    drawOval(scene.belly.copy(alpha = 0.55f), Offset(146f, 188f), Size(68f, 70f))

    // 前爪（走路时交替抬起）
    drawOval(scene.belly, Offset(132f, 246f + stepA), Size(38f, 18f))
    drawOval(scene.belly, Offset(190f, 246f + stepB), Size(38f, 18f))

    // 耳朵（先画，再压住头部轮廓）
    val earLift = sin(earTwitch * PI).toFloat() * 4f
    val leftEar = Path().apply {
        moveTo(140f, 102f)
        lineTo(122f, 54f - earLift)
        lineTo(170f, 86f)
        close()
    }
    val rightEar = Path().apply {
        moveTo(220f, 102f)
        lineTo(240f, 54f - earLift)
        lineTo(192f, 86f)
        close()
    }
    drawPath(leftEar, scene.fur)
    drawPath(rightEar, scene.fur)
    drawPath(
        Path().apply {
            moveTo(142f, 96f)
            lineTo(132f, 68f - earLift)
            lineTo(160f, 86f)
            close()
        },
        scene.innerEar,
    )
    drawPath(
        Path().apply {
            moveTo(218f, 96f)
            lineTo(230f, 68f - earLift)
            lineTo(200f, 86f)
            close()
        },
        scene.innerEar,
    )

    // 头（打理毛发时低头凑向爪子）
    translate(top = headDip) {
        drawCircle(scene.fur, 56f, Offset(180f, 138f))

        // 眼睛（舔毛时眯起眼）
        drawCatEyes(
            center = Offset(180f, 138f),
            blink = blink * (1f - lick * 0.55f),
            asleep = asleep,
            gazeX = gazeX,
            gazeY = gazeY,
            scene = scene,
        )

        // 口鼻
        drawCircle(scene.belly.copy(alpha = 0.8f), 16f, Offset(170f, 160f))
        drawCircle(scene.belly.copy(alpha = 0.8f), 16f, Offset(190f, 160f))
        drawPath(
            Path().apply {
                moveTo(174f, 156f)
                lineTo(186f, 156f)
                lineTo(180f, 163f)
                close()
            },
            scene.nose,
        )
        drawLine(scene.fur, Offset(180f, 163f), Offset(180f, 169f), strokeWidth = 2f)
        drawLine(scene.fur, Offset(180f, 169f), Offset(174f, 173f), strokeWidth = 2f)
        drawLine(scene.fur, Offset(180f, 169f), Offset(186f, 173f), strokeWidth = 2f)

        // 胡须
        val whisker = Color(0x88FFFFFF)
        listOf(-8f, 0f, 8f).forEach { dy ->
            drawLine(whisker, Offset(160f, 160f + dy), Offset(126f, 156f + dy * 1.6f), strokeWidth = 1.4f)
            drawLine(whisker, Offset(200f, 160f + dy), Offset(234f, 156f + dy * 1.6f), strokeWidth = 1.4f)
        }
    }

    // 打理毛发：抬起右前爪凑到嘴边。
    if (lick > 0.01f) {
        drawOval(
            color = scene.belly,
            topLeft = Offset(186f - lick * 4f, 246f - lick * 76f),
            size = Size(30f, 16f),
        )
    }

    if (sleepy) {
        drawCircle(Color(0x33FFFFFF), 5f, Offset(216f, 112f))
    }
}

private fun DrawScope.drawCatEyes(
    center: Offset,
    blink: Float,
    asleep: Boolean,
    gazeX: Float,
    gazeY: Float,
    scene: CompanionScene,
) {
    val eyeY = center.y - 4f
    val half = 10f
    val open = if (asleep) 0f else blink
    listOf(center.x - 22f, center.x + 22f).forEach { x ->
        if (open < 0.14f) {
            drawArc(
                color = scene.eye.copy(alpha = 0.85f),
                startAngle = 200f,
                sweepAngle = 140f,
                useCenter = false,
                topLeft = Offset(x - 11f, eyeY - 7f),
                size = Size(22f, 14f),
                style = Stroke(width = 2.4f),
            )
        } else {
            drawOval(
                color = scene.eye,
                topLeft = Offset(x - 10f, eyeY - 9f * open),
                size = Size(20f, 18f * open),
            )
            drawOval(
                color = Color(0xFF15110F),
                topLeft = Offset(
                    x - 2.6f + gazeX * 4f,
                    eyeY - 7f * open + gazeY * 3f,
                ),
                size = Size(5.2f, 14f * open),
            )
            drawCircle(
                color = Color.White.copy(alpha = 0.8f),
                radius = 2.2f,
                center = Offset(x - 4f + gazeX * 4f, eyeY - 4f + gazeY * 3f),
            )
        }
    }
}

internal fun DrawScope.drawRuralDog(
    tail: Float,
    blink: Float,
    gazeX: Float,
    gazeY: Float,
    earTwitch: Float,
    step: Float,
    groom: Float,
    asleep: Boolean,
    sleepy: Boolean,
    scene: CompanionScene,
) {
    val wag = sin(tail * PI * 2 * 1.7).toFloat()
    val stepA = if (step > 0f) sin(step * PI * 2).toFloat() * 4f else 0f
    val stepB = if (step > 0f) sin(step * PI * 2 + PI).toFloat() * 4f else 0f
    val lick = if (groom > 0f) abs(sin(groom * PI * 3).toFloat()) else 0f
    val headDip = lick * 7f
    // 尾巴
    val tailPath = Path().apply {
        moveTo(246f, 204f)
        cubicTo(286f, 196f + wag * 6f, 300f, 160f, 282f, 136f)
    }
    drawPath(
        tailPath,
        color = scene.fur,
        style = Stroke(width = 15f, cap = StrokeCap.Round),
    )

    // 身体
    drawOval(scene.fur, Offset(108f, 160f), Size(144f, 106f))
    drawOval(scene.belly, Offset(140f, 192f), Size(80f, 66f))

    // 后腿与前爪（走路时交替抬起）
    drawOval(scene.belly, Offset(126f, 246f + stepA), Size(42f, 18f))
    drawOval(scene.belly, Offset(194f, 246f + stepB), Size(42f, 18f))

    // 耷拉的耳朵
    val earLift = sin(earTwitch * PI).toFloat() * 5f
    val leftEar = Path().apply {
        moveTo(136f, 96f)
        cubicTo(104f, 122f, 100f, 176f - earLift, 126f, 196f - earLift)
        cubicTo(146f, 178f, 148f, 132f, 158f, 108f)
        close()
    }
    val rightEar = Path().apply {
        moveTo(224f, 96f)
        cubicTo(256f, 122f, 260f, 176f - earLift, 234f, 196f - earLift)
        cubicTo(214f, 178f, 212f, 132f, 202f, 108f)
        close()
    }
    drawPath(leftEar, scene.innerEar)
    drawPath(rightEar, scene.innerEar)

    // 头（打理毛发时低头凑向爪子）
    translate(top = headDip) {
        drawCircle(scene.fur, 56f, Offset(180f, 134f))
        // 口鼻
        drawOval(scene.belly, Offset(146f, 150f), Size(68f, 48f))
        drawCircle(scene.nose, 9f, Offset(180f, 156f))
        drawLine(scene.fur.copy(alpha = 0.8f), Offset(180f, 163f), Offset(180f, 170f), strokeWidth = 2f)
        // 舌头（舔毛时伸出来一点）
        if (!asleep) {
            drawOval(
                color = Color(0xFFE7808C),
                topLeft = Offset(172f, 170f + lick * 2f),
                size = Size(16f, 12f + lick * 3f),
            )
        }

        // 眼睛（舔毛时眯起眼）
        val eyeY = 128f
        val open = if (asleep) 0f else blink * (1f - lick * 0.55f)
        listOf(158f, 202f).forEach { x ->
            if (open < 0.14f) {
                drawLine(
                    color = scene.eye,
                    start = Offset(x - 8f, eyeY),
                    end = Offset(x + 8f, eyeY),
                    strokeWidth = 2.6f,
                    cap = StrokeCap.Round,
                )
            } else {
                drawCircle(scene.eye, 7.5f * open, Offset(x, eyeY))
                drawCircle(
                    Color.White.copy(alpha = 0.85f),
                    radius = 2.4f,
                    center = Offset(x - 2.4f + gazeX * 3f, eyeY - 2.4f + gazeY * 2f),
                )
            }
        }
    }

    // 打理毛发：抬起左前爪凑到嘴边。
    if (lick > 0.01f) {
        drawOval(
            color = scene.belly,
            topLeft = Offset(176f - lick * 4f, 246f - lick * 76f),
            size = Size(34f, 18f),
        )
    }

    if (sleepy) {
        drawCircle(Color(0x33FFFFFF), 5f, Offset(220f, 104f))
    }
}

internal fun DrawScope.drawHamster(
    tail: Float,
    blink: Float,
    gazeX: Float,
    gazeY: Float,
    earTwitch: Float,
    step: Float,
    groom: Float,
    asleep: Boolean,
    sleepy: Boolean,
    scene: CompanionScene,
) {
    val wobble = sin(tail * PI * 2).toFloat() * 2f
    val stepA = if (step > 0f) sin(step * PI * 2).toFloat() * 2.5f else 0f
    val stepB = if (step > 0f) sin(step * PI * 2 + PI).toFloat() * 2.5f else 0f
    val wash = if (groom > 0f) abs(sin(groom * PI * 3).toFloat()) else 0f
    val outline = Color(0xFFC89A64).copy(alpha = 0.45f)
    // 小尾巴
    drawCircle(scene.innerEar, 7f, Offset(250f + wobble, 232f))

    // 身体：圆滚滚
    drawOval(scene.fur, Offset(104f, 150f), Size(152f, 116f))
    drawOval(
        color = outline,
        topLeft = Offset(104f, 150f),
        size = Size(152f, 116f),
        style = Stroke(width = 1.6f),
    )
    drawOval(scene.belly, Offset(126f, 184f), Size(108f, 72f))

    // 耳朵：先画，压在头部后面
    val earLift = sin(earTwitch * PI).toFloat() * 3f
    listOf(142f, 218f).forEach { x ->
        drawCircle(scene.fur, 20f, Offset(x, 96f - earLift))
        drawCircle(
            color = outline,
            radius = 20f,
            center = Offset(x, 96f - earLift),
            style = Stroke(width = 1.6f),
        )
        drawCircle(scene.innerEar, 11f, Offset(x, 96f - earLift))
    }

    // 头：和身体分开一点点，脸才不会长在肚子上
    drawCircle(scene.fur, 56f, Offset(180f, 146f))
    drawCircle(
        color = outline,
        radius = 56f,
        center = Offset(180f, 146f),
        style = Stroke(width = 1.6f),
    )

    // 鼓鼓的腮帮子
    drawCircle(scene.belly.copy(alpha = 0.9f), 24f, Offset(144f, 164f))
    drawCircle(scene.belly.copy(alpha = 0.9f), 24f, Offset(216f, 164f))

    // 眼睛（洗脸时眯起眼）
    val eyeY = 138f
    val open = if (asleep) 0f else blink * (1f - wash * 0.5f)
    listOf(158f, 202f).forEach { x ->
        if (open < 0.14f) {
            drawArc(
                color = scene.eye,
                startAngle = 200f,
                sweepAngle = 140f,
                useCenter = false,
                topLeft = Offset(x - 7f, eyeY - 5f),
                size = Size(14f, 10f),
                style = Stroke(width = 2.2f),
            )
        } else {
            drawCircle(scene.eye, 6.5f * open, Offset(x, eyeY))
            drawCircle(
                Color.White.copy(alpha = 0.9f),
                radius = 2.3f,
                center = Offset(x - 2f + gazeX * 3f, eyeY - 2f + gazeY * 2f),
            )
        }
    }

    // 鼻子与嘴
    drawPath(
        Path().apply {
            moveTo(175f, 158f)
            lineTo(185f, 158f)
            lineTo(180f, 164f)
            close()
        },
        scene.nose,
    )
    drawLine(scene.eye.copy(alpha = 0.7f), Offset(180f, 164f), Offset(180f, 169f), strokeWidth = 1.6f)
    drawLine(scene.eye.copy(alpha = 0.7f), Offset(180f, 169f), Offset(174f, 172f), strokeWidth = 1.6f)
    drawLine(scene.eye.copy(alpha = 0.7f), Offset(180f, 169f), Offset(186f, 172f), strokeWidth = 1.6f)

    // 小脚（走路时交替抬起）
    drawOval(scene.innerEar, Offset(146f, 250f + stepA), Size(28f, 13f))
    drawOval(scene.innerEar, Offset(186f, 250f + stepB), Size(28f, 13f))

    // 洗脸：两只小爪子凑到腮帮子来回搓。
    if (wash > 0.01f) {
        val rub = sin(groom * PI * 6).toFloat() * 4f
        drawOval(
            color = scene.belly.copy(alpha = 0.95f),
            topLeft = Offset(140f + rub, 180f - wash * 22f),
            size = Size(16f, 11f),
        )
        drawOval(
            color = scene.belly.copy(alpha = 0.95f),
            topLeft = Offset(204f - rub, 180f - wash * 22f),
            size = Size(16f, 11f),
        )
    }

    // 一颗小瓜子
    if (!asleep) {
        drawOval(
            color = Color(0xFF6B4A2B),
            topLeft = Offset(194f, 236f),
            size = Size(12f, 7f),
        )
    }

    if (sleepy) {
        drawCircle(Color(0x33FFFFFF), 5f, Offset(220f, 122f))
    }
}

internal fun DrawScope.drawHearts(progress: Float, cx: Float, cy: Float) {
    val color = Color(0xFFFF7CA8).copy(alpha = (1f - progress).coerceIn(0f, 1f))
    repeat(3) { index ->
        val lift = progress * (46f + index * 12f)
        val x = cx + (index - 1) * 24f + sin(progress * PI * 2 + index).toFloat() * 5f
        val y = cy - lift
        val r = 5f + index * 1.2f
        drawCircle(color, r, Offset(x - r * 0.6f, y))
        drawCircle(color, r, Offset(x + r * 0.6f, y))
        val heart = Path().apply {
            moveTo(x, y + r * 1.9f)
            lineTo(x - r * 1.5f, y + r * 0.4f)
            lineTo(x + r * 1.5f, y + r * 0.4f)
            close()
        }
        drawPath(heart, color)
    }
}

internal fun DrawScope.drawCompanionCrumbs(progress: Float) {
    val color = Color(0xFFE2A45F).copy(alpha = (1f - progress).coerceIn(0f, 1f))
    repeat(4) { index ->
        val t = (progress + index * 0.12f) % 1f
        drawCircle(
            color = color,
            radius = 2.2f,
            center = Offset(160f + index * 14f, 196f + t * 34f),
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/CompanionScene.kt`

> 三种伙伴共用场景：天空、地面配色与场景细节。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

internal fun DrawScope.drawCompanionScene(
    species: OwlSpecies,
    phase: PetDayPhase,
    breath: Float,
    sway: Float,
    tail: Float,
    twinkle: Float,
    blink: Float,
    gazeX: Float,
    gazeY: Float,
    earTwitch: Float,
    hop: Float,
    walkOffsetX: Float,
    walkBob: Float,
    step: Float,
    groom: Float,
    reaction: PetReaction,
    reactionProgress: Float,
    asleep: Boolean,
    sleepy: Boolean,
    backdrop: Boolean,
) {
    val scene = companionScene(species, phase)
    if (backdrop) {
        drawRect(
            brush = Brush.verticalGradient(
                colors = scene.sky,
                startY = 0f,
                endY = 300f,
            ),
            size = Size(360f, 300f),
        )
        drawSceneDetails(species, scene, twinkle, phase)

        // 地面固定在地板上，宠物跳起时影子留在地上。
        drawOval(
            color = scene.floor,
            topLeft = Offset(8f, 238f),
            size = Size(344f, 58f),
        )
    }
    drawOval(
        color = Color(0x33000000),
        topLeft = Offset(112f, 246f),
        size = Size(136f, 24f),
    )

    val hopOffset = -sin(hop * PI).toFloat() * 6f
    val active = reaction != PetReaction.NONE && reactionProgress > 0f
    val shake = if (active && reaction == PetReaction.REFUSE) {
        sin(reactionProgress * PI * 7).toFloat() * 4f
    } else {
        0f
    }
    val lean = if (active && (reaction == PetReaction.FEED || reaction == PetReaction.PET)) {
        sin(reactionProgress * PI).toFloat() * 4f
    } else {
        0f
    }

    translate(left = shake + walkOffsetX, top = hopOffset + lean + walkBob) {
        scale(
            scaleX = 1f + breath * 0.012f,
            scaleY = 1f + breath * 0.018f,
            pivot = Offset(180f, 244f),
        ) {
            rotate(
                degrees = (sway * 2f - 1f) * 1.4f,
                pivot = Offset(180f, 244f),
            ) {
                when (species) {
                    OwlSpecies.INK_CAT -> drawInkCat(
                        tail = tail,
                        blink = blink,
                        gazeX = gazeX,
                        gazeY = gazeY,
                        earTwitch = earTwitch,
                        step = step,
                        groom = groom,
                        asleep = asleep,
                        sleepy = sleepy,
                        scene = scene,
                    )
                    OwlSpecies.RURAL_DOG -> drawRuralDog(
                        tail = tail,
                        blink = blink,
                        gazeX = gazeX,
                        gazeY = gazeY,
                        earTwitch = earTwitch,
                        step = step,
                        groom = groom,
                        asleep = asleep,
                        sleepy = sleepy,
                        scene = scene,
                    )
                    else -> drawHamster(
                        tail = tail,
                        blink = blink,
                        gazeX = gazeX,
                        gazeY = gazeY,
                        earTwitch = earTwitch,
                        step = step,
                        groom = groom,
                        asleep = asleep,
                        sleepy = sleepy,
                        scene = scene,
                    )
                }
            }
        }
    }

    if (active && (reaction == PetReaction.FEED || reaction == PetReaction.PET)) {
        drawHearts(reactionProgress, 180f, 120f)
    }
    if (active && reaction == PetReaction.FEED) {
        drawCompanionCrumbs(reactionProgress)
    }
}

internal data class CompanionScene(
    val sky: List<Color>,
    val floor: Color,
    val fur: Color,
    val belly: Color,
    val innerEar: Color,
    val eye: Color,
    val nose: Color,
    val accent: Color,
)

private fun companionScene(species: OwlSpecies, phase: PetDayPhase): CompanionScene {
    val base = when (species) {
        OwlSpecies.INK_CAT -> CompanionScene(
            sky = listOf(Color(0xFF0C1630), Color(0xFF1B2C4E)),
            floor = Color(0xFF15233C),
            fur = Color(0xFF23212B),
            belly = Color(0xFF35313E),
            innerEar = Color(0xFF5A4658),
            eye = Color(0xFFA8E66B),
            nose = Color(0xFFE7A6B8),
            accent = Color(0xFF8C7BD8),
        )
        OwlSpecies.RURAL_DOG -> CompanionScene(
            sky = listOf(Color(0xFFFFE7C9), Color(0xFFFFC98F)),
            floor = Color(0xFFE9B77E),
            fur = Color(0xFFC98A4B),
            belly = Color(0xFFF3DCB8),
            innerEar = Color(0xFF8A552C),
            eye = Color(0xFF2A211C),
            nose = Color(0xFF3B2A20),
            accent = Color(0xFFD95B43),
        )
        else -> CompanionScene(
            sky = listOf(Color(0xFFF7EAD7), Color(0xFFE9CDA9)),
            floor = Color(0xFFDDBD91),
            fur = Color(0xFFE9C9A3),
            belly = Color(0xFFF8E8D5),
            innerEar = Color(0xFFE8A7A0),
            eye = Color(0xFF2A211C),
            nose = Color(0xFFD98C93),
            accent = Color(0xFFB98B57),
        )
    }
    return base.copy(
        sky = phaseSky(species, phase),
        floor = phaseFloor(species, phase),
    )
}

/** 背景天空跟随系统时间：清晨 / 白天 / 黄昏 / 夜晚。 */
private fun phaseSky(species: OwlSpecies, phase: PetDayPhase): List<Color> =
    when (species) {
        OwlSpecies.INK_CAT -> when (phase) {
            PetDayPhase.DAWN -> listOf(Color(0xFF3B3566), Color(0xFFB58AA8), Color(0xFFF0B48C))
            PetDayPhase.DAY -> listOf(Color(0xFF4E88C6), Color(0xFF98C6E8), Color(0xFFE2EFF7))
            PetDayPhase.DUSK -> listOf(Color(0xFF2C2A56), Color(0xFF725078), Color(0xFFE08A6A))
            PetDayPhase.NIGHT -> listOf(Color(0xFF0C1630), Color(0xFF16233C), Color(0xFF1B2C4E))
        }
        OwlSpecies.RURAL_DOG -> when (phase) {
            PetDayPhase.DAWN -> listOf(Color(0xFFFFE3C4), Color(0xFFFFC99A), Color(0xFFFFB98A))
            PetDayPhase.DAY -> listOf(Color(0xFFDFF3FF), Color(0xFFFFEAC2), Color(0xFFFFE3B0))
            PetDayPhase.DUSK -> listOf(Color(0xFFFFD0A0), Color(0xFFE89A6A), Color(0xFFD9785F))
            PetDayPhase.NIGHT -> listOf(Color(0xFF2E2A45), Color(0xFF3A3350), Color(0xFF4A4058))
        }
        else -> when (phase) {
            PetDayPhase.DAWN -> listOf(Color(0xFFF7E2C8), Color(0xFFEFC9A2), Color(0xFFE8B48E))
            PetDayPhase.DAY -> listOf(Color(0xFFFFF7E6), Color(0xFFF9E6C8), Color(0xFFF0D6AC))
            PetDayPhase.DUSK -> listOf(Color(0xFFF0D2B0), Color(0xFFE2B48E), Color(0xFFD8A47A))
            PetDayPhase.NIGHT -> listOf(Color(0xFF3B3148), Color(0xFF4A3A4E), Color(0xFF5A4A55))
        }
    }

private fun phaseFloor(species: OwlSpecies, phase: PetDayPhase): Color =
    when (species) {
        OwlSpecies.INK_CAT -> when (phase) {
            PetDayPhase.DAWN -> Color(0xFF6A4A5A)
            PetDayPhase.DAY -> Color(0xFF6A8FA8)
            PetDayPhase.DUSK -> Color(0xFF5A3A4A)
            PetDayPhase.NIGHT -> Color(0xFF15233C)
        }
        OwlSpecies.RURAL_DOG -> when (phase) {
            PetDayPhase.DAWN -> Color(0xFFD99A6A)
            PetDayPhase.DAY -> Color(0xFFE9B77E)
            PetDayPhase.DUSK -> Color(0xFFB86A4A)
            PetDayPhase.NIGHT -> Color(0xFF3A3350)
        }
        else -> when (phase) {
            PetDayPhase.DAWN -> Color(0xFFC99C74)
            PetDayPhase.DAY -> Color(0xFFDDBD91)
            PetDayPhase.DUSK -> Color(0xFFB98B6A)
            PetDayPhase.NIGHT -> Color(0xFF3B3148)
        }
    }

private fun DrawScope.drawSceneDetails(
    species: OwlSpecies,
    scene: CompanionScene,
    twinkle: Float,
    phase: PetDayPhase,
) {
    if (phase == PetDayPhase.NIGHT) {
        drawCircle(
            color = Color(0xFFFFE7A8),
            radius = 24f,
            center = Offset(286f, 58f),
        )
        drawCircle(
            color = Color(0x33FFE7A8),
            radius = 34f,
            center = Offset(286f, 58f),
        )
    } else {
        val sunCenter = when (phase) {
            PetDayPhase.DAY -> Offset(292f, 62f)
            PetDayPhase.DAWN -> Offset(292f, 116f)
            else -> Offset(292f, 132f)
        }
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0x55FFD27A), Color(0x00FFD27A)),
                center = sunCenter,
                radius = 64f,
            ),
            radius = 64f,
            center = sunCenter,
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0xFFFFF3C4), Color(0xFFFFC65A)),
                center = sunCenter,
                radius = 36f,
            ),
            radius = 26f,
            center = sunCenter,
        )
    }

    if (phase != PetDayPhase.DAY) {
        val stars = listOf(
            Offset(42f, 42f), Offset(86f, 70f), Offset(124f, 36f),
            Offset(208f, 52f), Offset(246f, 92f), Offset(320f, 110f),
            Offset(62f, 112f), Offset(160f, 82f),
        )
        val dim = if (phase == PetDayPhase.NIGHT) 1f else 0.4f
        stars.forEachIndexed { index, point ->
            val alpha = (0.25f + ((twinkle + index * 0.17f) % 1f) * 0.55f) * dim
            drawCircle(
                color = Color.White.copy(alpha = alpha),
                radius = if (index % 3 == 0) 2.2f else 1.4f,
                center = point,
            )
        }
    }

    when (species) {
        OwlSpecies.RURAL_DOG -> {
            // 远处的两座小山
            val hill = Path().apply {
                moveTo(0f, 220f)
                cubicTo(70f, 170f, 120f, 180f, 180f, 212f)
                cubicTo(240f, 178f, 300f, 168f, 360f, 208f)
                lineTo(360f, 300f)
                lineTo(0f, 300f)
                close()
            }
            drawPath(hill, Color(0x332E7D4F))
        }
        OwlSpecies.HAMSTER -> {
            // 仓鼠的窝：木屑
            repeat(7) { index ->
                val y = 224f + index * 9f
                drawLine(
                    color = Color(0x33A9773F),
                    start = Offset(36f + index * 9f, y),
                    end = Offset(96f + index * 9f, y - 4f),
                    strokeWidth = 2f,
                    cap = StrokeCap.Round,
                )
            }
        }
        else -> Unit
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/Components.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shineleong.toughmind.R
import com.shineleong.toughmind.data.model.FatigueLevel
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMedical
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelModerate
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.LevelSevere
import com.shineleong.toughmind.ui.theme.LocalCareColors
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

fun FatigueLevel.toColor(): Color = when (this) {
    FatigueLevel.NORMAL -> LevelNormal
    FatigueLevel.MILD -> LevelMild
    FatigueLevel.MODERATE -> LevelModerate
    FatigueLevel.SEVERE -> LevelSevere
    FatigueLevel.MEDICAL -> LevelMedical
}

fun formatTime(millis: Long): String {
    if (millis <= 0) return "--"
    return SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date(millis))
}

fun formatDate(millis: Long): String {
    if (millis <= 0) return "--"
    return SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date(millis))
}

fun formatDateTime(millis: Long): String {
    if (millis <= 0) return "--"
    return SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date(millis))
}

/** 扁平分区：不再使用圆角卡片外框，只保留内容、标题和底部分隔线。 */
@Composable
fun TechCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(18.dp),
    accent: Color? = null,
    contentPadding: PaddingValues = PaddingValues(16.dp),
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(vertical = 12.dp),
            content = content,
        )
        HorizontalDivider(
            color = (accent ?: MaterialTheme.colorScheme.outline).copy(alpha = 0.35f),
        )
    }
}

/** 标题 + 主色小色块。 */
@Composable
fun SectionTitle(text: String, modifier: Modifier = Modifier) {
    Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(width = 4.dp, height = 20.dp)
                .clip(RoundedCornerShape(2.dp))
                .background(MaterialTheme.colorScheme.primary)
        )
        Spacer(Modifier.width(10.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
        )
    }
}

/** 主色小色块（独立点缀，可用于状态标识等）。 */
@Composable
fun GoldDot(modifier: Modifier = Modifier, size: Int = 10) {
    Box(
        modifier = modifier
            .size(size.dp)
            .clip(RoundedCornerShape(size.dp / 2))
            .background(Brush.linearGradient(LocalCareColors.current.accentGradient))
    )
}

/** 圆形头像：优先显示图片，否则默认笑脸头像；心情 emoji 单独浮在头像右下角外侧。 */
@Composable
fun Avatar(
    nickname: String?,
    modifier: Modifier = Modifier,
    size: Dp = 40.dp,
    imageBitmap: ImageBitmap? = null,
    moodEmoji: String? = null,
    statusEmoji: String? = null,
    statusColor: Color = MaterialTheme.colorScheme.outline,
    badgeText: String? = null,
    online: Boolean = false,
    showStatusBadge: Boolean = true,
    onMoodClick: (() -> Unit)? = null,
) {
    Box(modifier = modifier.size(size)) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .border(2.dp, MaterialTheme.colorScheme.primary, CircleShape)
                .padding(3.dp),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            listOf(
                                MaterialTheme.colorScheme.primaryContainer,
                                MaterialTheme.colorScheme.primary,
                            )
                        )
                    )
                    .then(
                        if (online) {
                            Modifier.border(2.dp, Color(0xFF16A36A), CircleShape)
                        } else {
                            Modifier.border(2.dp, MaterialTheme.colorScheme.outline, CircleShape)
                        }
                    ),
                contentAlignment = Alignment.Center,
            ) {
                if (imageBitmap != null) {
                    Image(
                        bitmap = imageBitmap,
                        contentDescription = "头像",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop,
                    )
                } else {
                    Image(
                        painter = painterResource(R.drawable.default_avatar),
                        contentDescription = "默认头像",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop,
                    )
                }
            }
        }
        if (showStatusBadge || !moodEmoji.isNullOrBlank()) {
            val badgeSize = if (size < 52.dp) 20.dp else size * 0.42f
            Box(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .offset(x = 3.dp, y = 3.dp)
                    .size(badgeSize)
                    .shadow(3.dp, CircleShape)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.surface)
                    .then(if (onMoodClick != null) Modifier.clickable(onClick = onMoodClick) else Modifier),
                contentAlignment = Alignment.Center,
            ) {
                if (showStatusBadge) {
                    StatusGridBadge(
                        color = if (online) statusColor else MaterialTheme.colorScheme.outline,
                        online = online,
                        modifier = Modifier.fillMaxSize().padding(3.dp),
                    )
                } else {
                    Text(
                        text = moodEmoji.orEmpty(),
                        fontSize = (badgeSize.value * 0.56f).sp,
                        lineHeight = (badgeSize.value * 0.62f).sp,
                    )
                }
            }
        }
    }
}

/** 右下角的在线状态：用 3×3 栅格绘制，不使用 emoji。 */
@Composable
fun StatusGridBadge(
    color: Color,
    online: Boolean,
    modifier: Modifier = Modifier,
) {
    Canvas(modifier = modifier) {
        val gap = size.minDimension * 0.10f
        val cell = (size.minDimension - gap * 4f) / 3f
        val radius = CornerRadius(cell * 0.25f, cell * 0.25f)
        for (row in 0..2) {
            for (col in 0..2) {
                val x = gap + col * (cell + gap)
                val y = gap + row * (cell + gap)
                drawRoundRect(
                    color = color.copy(alpha = if (online) 0.95f else 0.45f),
                    topLeft = androidx.compose.ui.geometry.Offset(x, y),
                    size = androidx.compose.ui.geometry.Size(cell, cell),
                    cornerRadius = radius,
                )
            }
        }
    }
}

/** 3D 主题渐变按钮。 */
@Composable
fun TechButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    loading: Boolean = false,
) {
    val shape = RoundedCornerShape(AppDimens.ButtonCorner)
    val careColors = LocalCareColors.current
    Surface(
        onClick = onClick,
        enabled = enabled,
        shape = shape,
        color = Color.Transparent,
        contentColor = MaterialTheme.colorScheme.onPrimary,
        shadowElevation = 6.dp,
        modifier = modifier
            .height(AppDimens.ButtonHeight)
            .shadow(
                elevation = 8.dp,
                shape = shape,
                spotColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.35f),
                ambientColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.20f),
            ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .clip(shape)
                .background(Brush.linearGradient(careColors.accentGradient))
                .padding(horizontal = AppDimens.ContentPaddingHorizontal),
            contentAlignment = Alignment.Center,
        ) {
            if (loading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(AppDimens.IconSize),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            } else {
                Text(
                    text = text,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
        }
    }
}

/** 3D 指标卡：主题渐变底 + 描边 + 主色数值。 */
@Composable
fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    val shape = RoundedCornerShape(14.dp)
    Column(
        modifier = modifier
            .shadow(
                elevation = 8.dp,
                shape = shape,
                spotColor = MaterialTheme.colorScheme.scrim.copy(alpha = 0.16f),
                ambientColor = MaterialTheme.colorScheme.scrim.copy(alpha = 0.10f),
            )
            .clip(shape)
            .background(Brush.verticalGradient(LocalCareColors.current.cardGradient))
            .border(BorderStroke(1.dp, MaterialTheme.colorScheme.outline), shape)
            .padding(12.dp),
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.primary,
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/FloatingPet.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlin.random.Random

/**
 * 桌面宠物：可以自己在屏幕上走几步，也能被拖到任意位置。
 *
 * 走动频率很低，而且只沿着当前高度横向移动，不会满屏乱跑、也不会每次移动都向屏幕上方滑。
 */
@Composable
fun FloatingPet(
    pet: PetState,
    reaction: PetReaction,
    reactionToken: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    BoxWithConstraints(modifier = modifier.fillMaxSize()) {
        val density = LocalDensity.current
        val petSizePx = with(density) { 96.dp.toPx() }
        val edgePx = with(density) { 10.dp.toPx() }
        // 顶部避开标题栏，底部避开导航栏；拖动时仍然可以放到任意高度。
        val topInsetPx = with(density) { 96.dp.toPx() }
        val bottomInsetPx = with(density) { 96.dp.toPx() }

        val areaWidth = with(density) { maxWidth.toPx() }
        val areaHeight = with(density) { maxHeight.toPx() }
        val minX = edgePx
        val maxX = (areaWidth - petSizePx - edgePx).coerceAtLeast(minX)
        val minY = topInsetPx
        val maxY = (areaHeight - petSizePx - bottomInsetPx).coerceAtLeast(minY)

        // 默认停在屏幕下方靠右，像站在地面上；走动时只沿这个高度左右移动。
        var posX by remember { mutableFloatStateOf(minX + (maxX - minX) * 0.78f) }
        var posY by remember { mutableFloatStateOf(minY + (maxY - minY) * 0.80f) }
        var dragging by remember { mutableStateOf(false) }

        // 自由走动：隔很久才走一小段，而且只沿着当前高度左右移动。
        LaunchedEffect(minX, maxX) {
            while (true) {
                delay(Random.nextLong(15_000L, 30_000L))
                if (dragging) continue
                // 大多数时候只是原地待着，不再高频乱走。
                if (Random.nextInt(100) < 45) continue
                val span = maxX - minX
                if (span < with(density) { 40.dp.toPx() }) continue
                val fromX = posX
                val direction = if (Random.nextBoolean()) 1f else -1f
                val step = with(density) { 52.dp.toPx() } + Random.nextFloat() * span * 0.18f
                var toX = fromX + direction * step
                if (toX < minX || toX > maxX) {
                    toX = (fromX - direction * step).coerceIn(minX, maxX)
                }
                val distance = abs(toX - fromX)
                if (distance < with(density) { 36.dp.toPx() }) continue
                val durationMs = ((distance / with(density) { 42.dp.toPx() }) * 1_000f)
                    .toInt()
                    .coerceIn(900, 3_000)
                val startNanos = withFrameNanos { it }
                while (true) {
                    val nowNanos = withFrameNanos { it }
                    if (dragging) break
                    val t = ((nowNanos - startNanos) / 1_000_000f / durationMs).coerceIn(0f, 1f)
                    // smoothstep：起步和停下都更柔和。
                    val eased = t * t * (3f - 2f * t)
                    posX = fromX + (toX - fromX) * eased
                    if (t >= 1f) break
                }
            }
        }

        Box(
            modifier = Modifier
                .offset { IntOffset(posX.roundToInt(), posY.roundToInt()) }
                .size(96.dp)
                .pointerInput(minX, maxX, minY, maxY) {
                    detectDragGestures(
                        onDragStart = { dragging = true },
                        onDragEnd = { dragging = false },
                        onDragCancel = { dragging = false },
                    ) { change, dragAmount ->
                        change.consume()
                        posX = (posX + dragAmount.x).coerceIn(minX, maxX)
                        posY = (posY + dragAmount.y).coerceIn(minY, maxY)
                    }
                },
        ) {
            PetLive2D(
                state = pet,
                reaction = reaction,
                reactionToken = reactionToken,
                phase = PetDayPhase.at(System.currentTimeMillis()),
                modifier = Modifier.size(96.dp),
                contentDescription = "桌面宠物，点一下进入宠物小窝",
                onTap = onClick,
                backdrop = false,
                focus = 1.15f,
            )
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/LocalizedText.kt`

> 中英切换入口：`tr()`、`translate()` 与自动翻译的 `Text` 重载。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.text.InlineTextContent
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Text as MaterialText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.TextUnit
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage

/**
 * 轻量翻译层：英文模式下翻译常见静态文案，未收录的动态内容保持原文。
 * 通过替换 Material3 的 Text 使用，改动面小、可随语言开关即时重组。
 */
@Composable
@ReadOnlyComposable
fun tr(zh: String, en: String): String =
    if (LocalAppLanguage.current == "en") en else zh

@Composable
@ReadOnlyComposable
fun translate(text: String): String = translateText(text, LocalAppLanguage.current)

fun translateText(text: String, language: String): String {
    if (language != "en" || text.isBlank()) return text
    EN[text]?.let { return it }
    for ((regex, replacement) in EN_PATTERNS) {
        val match = regex.matchEntire(text) ?: continue
        return regex.replace(text, replacement)
    }
    return text
}

@Composable
fun Text(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    onTextLayout: ((TextLayoutResult) -> Unit)? = null,
    style: TextStyle = LocalTextStyle.current,
) {
    MaterialText(
        text = translate(text),
        modifier = modifier,
        color = color,
        fontSize = fontSize,
        fontStyle = fontStyle,
        fontWeight = fontWeight,
        fontFamily = fontFamily,
        letterSpacing = letterSpacing,
        textDecoration = textDecoration,
        textAlign = textAlign,
        lineHeight = lineHeight,
        overflow = overflow,
        softWrap = softWrap,
        maxLines = maxLines,
        minLines = minLines,
        onTextLayout = onTextLayout,
        style = style,
    )
}

@Composable
fun Text(
    text: AnnotatedString,
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    inlineContent: Map<String, InlineTextContent> = mapOf(),
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyle.current,
) {
    MaterialText(
        text = text,
        modifier = modifier,
        color = color,
        fontSize = fontSize,
        fontStyle = fontStyle,
        fontWeight = fontWeight,
        fontFamily = fontFamily,
        letterSpacing = letterSpacing,
        textDecoration = textDecoration,
        textAlign = textAlign,
        lineHeight = lineHeight,
        overflow = overflow,
        softWrap = softWrap,
        maxLines = maxLines,
        minLines = minLines,
        inlineContent = inlineContent,
        onTextLayout = onTextLayout,
        style = style,
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/LocalizedTextTable.kt`

> 英文翻译表与正则替换规则（中文原文作为 key，动态距离/时长/转向走正则）。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.text.InlineTextContent
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Text as MaterialText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.TextUnit
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage

internal val EN_PATTERNS: List<Pair<Regex, String>> = listOf(
    Regex("^相距 (.+)$") to "Distance $1",
    Regex("^距离未知$") to "Distance unknown",
    Regex("^(\\d+) 分钟前$") to "$1 min ago",
    Regex("^(\\d+) 小时前$") to "$1 h ago",
    Regex("^本月一起打卡 (\\d+) 天 ❤️$") to "Together $1 day(s) this month ❤️",
    Regex("^有 (\\d+) 条提醒$") to "$1 reminders",
    Regex("^版本 (.+)$") to "Version $1",
    Regex("^已和 (.+)（(.+)）配对$") to "Paired with $1 ($2)",
    Regex("^你好，(.+)$") to "Hello, $1",
    Regex("^(.+) 那里的天气$") to "Weather for $1",
    Regex("^还有 (\\d+) 天$") to "$1 days left",
    Regex("^已过去 (\\d+) 天$") to "$1 days ago",
    Regex("^(.+) 现在 (.+)$") to "$1 is now $2",
    Regex("^纪念日 · (.+)$") to "Anniversary · $1",
    Regex("^日程 · (.+)$") to "Schedule · $1",
    Regex("^生日 · (.+)$") to "Birthday · $1",
    Regex("^倒数日 · (.+)$") to "Countdown · $1",
    Regex("^你已经打卡了，等 (.+) 也完成今天的小目标$") to "You're checked in—waiting for $1 to finish today's goal.",
    Regex("^添加提醒 · (.+)$") to "Add reminder · $1",
    Regex("^提醒时间：(.+)$") to "Reminder time: $1",
    Regex("^导航到 (.+)$") to "Navigate to $1",
    Regex("^账号：(.+)$") to "Account: $1",
    Regex("^朝向 北$") to "Facing N",
    Regex("^朝向 东北$") to "Facing NE",
    Regex("^朝向 东$") to "Facing E",
    Regex("^朝向 东南$") to "Facing SE",
    Regex("^朝向 南$") to "Facing S",
    Regex("^朝向 西南$") to "Facing SW",
    Regex("^朝向 西$") to "Facing W",
    Regex("^朝向 西北$") to "Facing NW",
    Regex("^全程 ([\\d.]+) 公里$") to "Total $1 km",
    Regex("^预计 (\\d+) 分钟 · (\\d+) 段道路$") to "About $1 min · $2 segments",
    Regex("^TA 预计 (\\d+) 分钟后到达 · ([\\d.]+) 公里$") to "They arrive in $1 min · $2 km",
    Regex("^([\\d.]+) 公里$") to "$1 km",
    Regex("^(\\d+) 米$") to "$1 m",
    Regex("^(\\d+) 小时 (\\d+) 分钟$") to "$1 h $2 min",
    Regex("^(\\d+) 分钟$") to "$1 min",
    Regex("^(\\d+) 秒$") to "$1 s",
    Regex("^沿当前道路前往 (.+)$") to "Continue on the current road to $1",
    Regex("^导航模式 · (.+)$") to "Navigation · $1",
    Regex("^有 (\\d+) 条提醒$") to "$1 reminders",
    Regex("^(\\d+) 人 · (\\d+) 台设备$") to "$1 people · $2 devices",
    Regex("^已有 (\\d+) 人$") to "$1 people so far",
    Regex("^邀请码 (.+)$") to "Invite code $1",
    Regex("^(\\d+) 条$") to "$1 messages",
    Regex("^今天 (\\d{1,2}:\\d{2})$") to "Today $1",
    Regex("^昨天 (\\d{1,2}:\\d{2})$") to "Yesterday $1",
    Regex("^松开发送 · (\\d+)s$") to "Release to send · $1s",
    Regex("^正在录音 (\\d+:\\d+) · 点麦克风发送$") to "Recording $1 · tap the mic to send",
    Regex("^字体大小 (\\d+)%$") to "Font size $1%",
    Regex("^朗读速度 ([\\d.]+)x$") to "Speech rate $1x",
    Regex("^跟(.+)说点什么…$") to "Say something to $1…",
    Regex("^清空和(.+)的对话？$") to "Clear the chat with $1?",
    Regex("^设备 ID：(.+)$") to "Device ID: $1",
    Regex("^设备码：(.+)$") to "Device code: $1",
    Regex("^最后上报：(.+)$") to "Last seen: $1",
    Regex("^已生成设备，设备码：(.+)$") to "Demo device created. Code: $1",
    Regex("^(.+) 已绑定并加入当前关心组$") to "$1 bound and joined the current group",
    Regex("^(.+) 已加入云端关心组$") to "$1 joined the cloud care group",
    Regex("^(.+) 已移出云端关心组$") to "$1 removed from the cloud care group",
    Regex("^设备已保存，但加入关心组失败：(.+)$") to "Device saved, but joining the group failed: $1",
    Regex("^已切换到「(.+)」$") to "Switched to \"$1\"",
    Regex("^疲劳等级：(.+)$") to "Fatigue: $1",
    Regex("^疲劳分数 ([\\d.]+) · 哈欠 (\\d+) 次$") to "Fatigue score $1 · $2 yawns",
    Regex("^(.+) 正在驾驶，疲劳等级：(.+)$") to "$1 is driving · fatigue: $2",
    Regex("^浪漫清单 (\\d+)/100$") to "Romance list $1/100",
    Regex("^已完成 (\\d+) / 100 件 · 目标 (\\d+) 件$") to "$1 / 100 done · goal $2",
    Regex("^今日已喂 (\\d+)/(\\d+) 顿$") to "Fed $1/$2 today",
    Regex("^今日投喂 (\\d+)/(\\d+) 顿$") to "Fed $1/$2 today",
    Regex("^消化 (.+)$") to "Digesting $1",
    Regex("^上次：(.+)$") to "Last: $1",
    Regex("^体感 (\\d+)℃ · 湿度 (\\d+)% · 风速 (\\d+) km/h$") to "Feels $1℃ · humidity $2% · wind $3 km/h",
    Regex("^(.+) 现在 (.+)$") to "$1 is now $2",
)

internal val EN: Map<String, String> = mapOf(
    // 品牌与导航
    "念安" to "TOUCHMIND",
    "念安 · 今天也要好好关心" to "TOUCHMIND · Take good care today",
    "念安 · 把牵挂放在看得见的地方" to "TOUCHMIND · Keep care in sight",
    "把牵挂放在看得见的地方" to "Keep care in sight",
    "亲属与亲属之间互相关心的 App" to "An app for family and loved ones to care for each other",
    "地图" to "Map",
    "日历" to "Calendar",
    "关心" to "Care",
    "个人中心" to "Profile",
    "设备管理" to "Devices",
    "亲友与设备" to "Loved ones & devices",
    "亲友管理" to "Loved ones & devices",
    "设置" to "Settings",
    "关于APP" to "About",
    "关于产品" to "About the product",
    "关于念安" to "About TOUCHMIND",
    "版本信息" to "Version",
    "动态记录" to "Activity",
    "关心建议" to "Care tips",
    "浪漫清单" to "Romance list",
    "一起做的一万件浪漫小事" to "10,000 little romantic things",
    "情侣模式 · 今天的情话" to "Couple mode · Today's sweet line",
    "亲友设置" to "Loved one settings",
    "智能建议" to "Smart tips",
    "状态记录" to "Status history",
    "事件详情" to "Event details",

    // 通用动作
    "返回" to "Back",
    "关闭" to "Close",
    "关闭抽屉" to "Close drawer",
    "取消" to "Cancel",
    "保存" to "Save",
    "删除" to "Delete",
    "添加" to "Add",
    "添加提醒" to "Add reminder",
    "知道了" to "Got it",
    "换一个" to "Change",
    "更新" to "Updated",
    "查看地图" to "View map",
    "打开日历" to "Open calendar",
    "查看当天" to "View day",
    "生成一条" to "Generate one",
    "生成中…" to "Generating…",
    "复制" to "Copy",
    "创建" to "Create",
    "加入" to "Join",
    "绑定" to "Bind",
    "解绑" to "Unbind",
    "设为当前" to "Set as current",
    "保存亲友信息" to "Save loved one info",
    "修改昵称" to "Edit nickname",
    "更换头像" to "Change avatar",
    "拍照" to "Camera",
    "从相册选择" to "Choose from gallery",
    "轻轻提醒" to "Send a nudge",
    "轻轻提醒 TA" to "Send a gentle nudge",
    "提醒 TA" to "Nudge them",
    "退出登录" to "Sign out",
    "重新获取位置" to "Retry location",
    "开启定位" to "Enable location",

    // 登录 / 账号
    "登录" to "Sign in",
    "注册并登录" to "Sign up & sign in",
    "账号 / 手机号" to "Account / phone",
    "密码" to "Password",
    "已有账号？去登录" to "Already have an account? Sign in",
    "没有账号？去注册" to "No account? Sign up",
    "请输入账号和密码" to "Enter account and password",
    "登录失败" to "Sign-in failed",
    "注册失败" to "Sign-up failed",
    "账号或密码错误" to "Wrong account or password",
    "密码长度至少 6 位" to "Password must be at least 6 characters",
    "账号或密码格式不正确" to "Invalid account or password",
    "账号已存在" to "Account already exists",
    "服务器错误" to "Server error",
    "无法连接服务器，请检查网络" to "Cannot reach the server. Check your network.",
    "未配置服务器地址" to "Server address not configured",
    "未登录" to "Not signed in",

    // 状态
    "在线" to "Online",
    "离线" to "Offline",
    "未知" to "Unknown",
    "状态未知" to "Status unknown",
    "工作中" to "Working",
    "学习中" to "Studying",
    "休息中" to "Resting",
    "运动中" to "Exercising",
    "睡觉中" to "Sleeping",
    "通勤中" to "Commuting",
    "驾驶中" to "Driving",
    "正在路上" to "On the way",
    "正在忙工作" to "Working",
    "正在通勤路上" to "Commuting",
    "正在专注学习" to "Studying",
    "正在休息 · 喝口水吧" to "Resting · drink some water",
    "正在运动 · 状态不错" to "Exercising · looking good",
    "已经睡下 · 晚安" to "Asleep · good night",
    "正常" to "Normal",
    "轻度疲劳" to "Mild fatigue",
    "中度疲劳" to "Moderate fatigue",
    "重度疲劳" to "Severe fatigue",
    "需要帮助" to "Needs help",
    "需要你的帮助" to "Needs your help",
    "需要休息" to "Needs rest",
    "看起来有点累" to "Looks tired",
    "紧急求助" to "SOS",
    "医学异常" to "Medical alert",
    "跌倒" to "Fall",
    "抽搐" to "Seizure",
    "意识丧失" to "Unconscious",
    "分心" to "Distraction",
    "驾驶安全" to "Driving safety",
    "驾驶安全 · 设备正在关注" to "Driving safety · device is watching",
    "驾驶安全（设备功能之一）" to "Driving safety (a device feature)",
    "驾驶员监测" to "Driver monitoring",
    "驾驶" to "Driving",
    "疲劳等级" to "Fatigue level",
    "疲劳分数" to "Fatigue score",
    "哈欠次数" to "Yawns",
    "车速" to "Speed",
    "车内温度" to "Cabin temp",
    "告警信息" to "Alerts",
    "医学类型" to "Medical type",

    // 人物与设备
    "我" to "Me",
    "我的手机" to "My phone",
    "我这里的天气" to "My weather",
    "📱 手机" to "📱 Phone",
    "刚刚" to "Just now",
    "我的心情" to "My mood",
    "TA 的心情" to "Their mood",
    "TA 的称呼" to "Their name",
    "你们的关系" to "Your relationship",
    "TA 使用的设备" to "Their device",
    "手机" to "Phone",
    "手机在线" to "Phone online",
    "家人" to "Family",
    "长辈" to "Elder",
    "伴侣" to "Partner",
    "朋友" to "Friend",
    "其他" to "Other",
    "设备" to "Device",
    "设备类型" to "Device type",
    "设备已连接" to "Device connected",
    "当前设备" to "Current device",
    "绑定新设备" to "Bind a new device",
    "暂无绑定设备。绑定后，TA 的状态会出现在地图与关心页。" to "No devices bound. Bind one to see their status on the map and Care page.",
    "共享位置、电量、学习与休息状态，适合家人和情侣。" to "Share location, battery, study and rest status—great for family and couples.",
    "适合驾驶 / 居家监测，可上报疲劳、跌倒与车辆位置。" to "For driving and home monitoring; reports fatigue, falls and vehicle location.",
    "设备" to "Device",
    "设备适合驾驶/居家监测；手机适合位置共享、学习状态与日常关心。" to "Devices are for driving/home monitoring; phones are for location sharing, study status and everyday care.",
    "电量" to "Battery",
    "最近更新" to "Last update",
    "状态" to "Status",
    "相距" to "Distance",
    "方向" to "Direction",
    "纬度" to "Latitude",
    "经度" to "Longitude",
    "时间" to "Time",
    "类型" to "Type",
    "设备 ID" to "Device ID",
    "设备名称" to "Device name",
    "请填写 TA 的称呼" to "Please enter their name",
    "比如：小念、妈妈、阿哲" to "e.g. An, Mom, Alex",
    "已保存，TA 的信息会同步到地图与日历" to "Saved. Their info will sync to the map and calendar.",

    // 日历
    "今天" to "Today",
    "回到今天" to "Back to today",
    "上个月" to "Previous month",
    "下个月" to "Next month",
    "纪念日" to "Anniversary",
    "日程" to "Schedule",
    "生日" to "Birthday",
    "倒数日" to "Countdown",
    "提醒" to "Reminder",
    "提醒内容" to "Reminder",
    "备注" to "Note",
    "提醒时间" to "Reminder time",
    "提醒提示音" to "Reminder sound",
    "有提醒" to "Alarm",
    "当天提醒" to "Reminders that day",
    "本月提醒" to "This month's reminders",
    "删除提醒" to "Delete reminder",
    "已关闭" to "Off",
    "打卡" to "Check-in",
    "今天一起打卡" to "Check in together today",
    "打卡 · 两个人的小约定" to "Check-in · our little promise",
    "各自完成今天的小目标，再一起点亮这一天。" to "Finish today's small goals, then light up the day together.",
    "今天两个人都打卡了，日历已经变成红色 ❤️" to "Both checked in today—the calendar is red ❤️",
    "最近 7 天" to "Last 7 days",
    "给 TA 留言" to "Leave them a message",
    "会显示在你的头像上方" to "Shows in a bubble above your avatar",
    "发送留言" to "Send",
    "取消今天的打卡" to "Undo today's check-in",
    "完成今天的打卡" to "Check in today",
    "已打卡 · 取消" to "Checked in · undo",
    "等 TA 打卡" to "Waiting for them",
    "红色 = 双方都打卡；紫色 = 我；青色 = TA。" to "Red = both checked in; purple = me; cyan = them.",
    "双方这天都打卡了，日历已点亮为红色 ❤️" to "Both checked in this day—the calendar is red ❤️",
    "你已打卡，等 TA 也在「打卡」页完成。" to "You're checked in—waiting for them on the Check-in page.",
    "TA 已打卡，去「打卡」页完成你的部分吧。" to "They checked in—finish your part on the Check-in page.",
    "这天还没有打卡。打卡互动已集中到「打卡」页。" to "No check-in yet. All check-ins now live on the Check-in page.",
    "导航到 TA" to "Navigate to them",
    "选择出行方式，将打开手机里的地图 App。" to "Choose a travel mode; this opens your maps app.",
    "驾车" to "Driving",
    "步行" to "Walking",
    "公共交通" to "Public transit",
    "电动车" to "E-bike",
    "今天做了什么" to "What happened today",
    "还没有记录。写下今天什么时候做了什么，分享给 TA。" to "No entries yet. Write down what you did and when, then share it.",
    "加照片" to "Add photo",
    "换照片" to "Change photo",
    "分享" to "Share",
    "例如：14:00 去图书馆看了会儿书" to "e.g. 14:00 read at the library",
    "今天一起完成" to "Today's shared goal",
    "例如：背 30 个单词 / 喝 8 杯水" to "e.g. 30 words / 8 glasses of water",
    "上传今日照片" to "Upload today's photo",
    "更换照片" to "Change photo",
    "移除" to "Remove",
    "保存目标和照片" to "Save goal & photo",
    "设置状态" to "Set status",
    "我的状态" to "My status",
    "TA 的状态" to "Their status",
    "平静" to "Calm",
    "开心" to "Happy",
    "想你" to "Missing you",
    "累了" to "Tired",
    "困了" to "Sleepy",
    "在忙" to "Busy",
    "吃饭" to "Eating",
    "在路上" to "On the way",
    "还没有状态，点右侧说一句吧" to "No status yet — say something",
    "要说点什么" to "Say something",
    "取消打卡" to "Undo check-in",
    "点击打卡" to "Tap to check in",
    "已打卡" to "Checked in",
    "今天已打卡" to "Checked in today",
    "今天还没有打卡" to "Not checked in yet",
    "双方都打卡" to "Both checked in",
    "我打卡" to "I checked in",
    "TA 打卡" to "They checked in",
    "本月还没有一起打卡" to "No joint check-ins this month",
    "今日一起打卡" to "Check in together today",
    "今天一起打卡" to "Check in together today",
    "双方天气" to "Weather for both",
    "天气" to "Weather",
    "天气获取中…" to "Loading weather…",
    "为彼此留一个打卡的位置" to "Leave a check-in spot for each other",
    "已经有一个人打卡，等 TA 一起点亮红色" to "One person checked in—waiting for the other to light it red",
    "两个人都打卡了，今天在日历上是一颗红心 ❤️" to "Both checked in—today is a red heart on the calendar ❤️",
    "需要 TA 在自己的念安里打卡，双方日历才会一起变红" to "They need to check in on their TOUCHMIND too before the day turns red",
    "各自完成今天的小目标，然后一起打卡吧" to "Finish today's small goals, then check in together",
    "完成今天的小目标后，分别打卡，让这一天变成红色吧" to "Finish today's goals and check in separately to turn this day red.",
    "给提醒起个名字吧" to "Give this reminder a name",
    "提醒内容（如：一起背单词）" to "Reminder (e.g. memorize words together)",
    "备注（可选）" to "Note (optional)",
    "纪念日名称（如：在一起 100 天）" to "Anniversary name (e.g. 100 days together)",
    "生日主角（如：妈妈生日）" to "Birthday person (e.g. Mom's birthday)",
    "倒数事件（如：回家倒计时）" to "Countdown event (e.g. going home)",
    "这一天还没有提醒。可以设置学习、吃药、喝水或纪念日。" to "No reminders this day. Add study, medicine, water or an anniversary.",
    "这两天还没有提醒。可以设置学习、吃药、喝水或纪念日。" to "No reminders this day. Add study, medicine, water or an anniversary.",
    "就是今天" to "Today",
    "今天也要好好关心" to "Take good care today",
    "今天也要好好生活" to "Live well today",
    "在想你，记得照顾好自己。" to "Thinking of you—take care.",
    "晚安，早点休息" to "Good night, rest early.",
    "还没有留言，点右侧写一句吧" to "No message yet—leave one",
    "头像右下角会显示这个 emoji，TA 点开你的头像就能看到留言。" to "This emoji appears at the bottom-right of your avatar; tap it to leave a message for them.",
    "选一个 emoji 表示今天的状态，会显示在账号下方；留言仍会同步给 TA。" to "Pick an emoji for today's status; it shows under your account and your note is still shared with them.",
    "设置心情" to "Set mood",
    "留一句话" to "Leave a message",
    "通过设备下行主题发送一条不带打扰的关心提醒" to "Send a quiet care nudge through the device downlink topic",

    // 天气
    "晴" to "Sunny",
    "多云" to "Cloudy",
    "阴" to "Overcast",
    "小雨" to "Light rain",
    "中雨" to "Moderate rain",
    "大雨" to "Heavy rain",
    "雷阵雨" to "Thunderstorm",
    "阵雨" to "Showers",
    "小雪" to "Light snow",
    "中雪" to "Moderate snow",
    "大雪" to "Heavy snow",
    "雨" to "Rain",
    "有雾" to "Foggy",
    "少云" to "Mostly clear",
    "晴夜" to "Clear night",

    // 设置
    "外观与语言" to "Appearance & language",
    "主题" to "Theme",
    "跟随系统" to "Follow system",
    "浅色" to "Light",
    "深色" to "Dark",
    "消息通知设置" to "Notifications",
    "关心提醒推送" to "Care reminder push",
    "提醒提示音" to "Reminder sound",
    "语言 / Language" to "Language",
    "中文" to "中文",
    "还没有收到 TA 的位置。绑定亲友或让 TA 的设备上线后，就能在这里看到彼此。" to "No location from them yet. Bind a loved one or bring their device online to see each other here.",
    "还没有关心建议。点“生成一条”，根据 TA 当前的状态与两地天气，得到一句今天就能用上的话。" to "No care tips yet. Tap Generate to get something useful for today based on their status and both weathers.",
    "正在根据 TA 的状态想一句合适的关心…" to "Thinking of the right thing to say…",
    "关心建议暂时生成失败，请稍后再试" to "Couldn't generate a tip. Try again later.",
    "暂无动态记录" to "No activity yet",
    "暂无关心建议，等待云端生成" to "No care tips yet; waiting for the cloud",
    "暂无建议" to "No tips yet",
    "还没有收到 TA 的动态" to "No activity from them yet",
    "还没有日程提醒。可以把学习、吃药、纪念日放进日历，到点会收到通知。" to "No reminders yet. Add study, medicine or an anniversary; we'll notify you on time.",

    // 云端 / 配对
    "云端关心组" to "Cloud care group",
    "创建关心组" to "Create care group",
    "加入关心组" to "Join care group",
    "退出关心组" to "Leave care group",
    "邀请码" to "Invite code",
    "输入邀请码" to "Enter invite code",
    "请输入 6 位邀请码" to "Enter the 6-digit invite code",
    "输入 TA 发来的 6 位邀请码，加入后即可看到对方的真实位置与状态。" to "Enter the 6-digit invite code from them to see their real location and status.",
    "把邀请码发给另一位家人，也可以邀请 TA 加入同一个关心组。" to "Share the invite code with a loved one so they can join the same care group.",
    "创建关心组或输入邀请码，和 TA 的手机 / 设备同步真实位置、状态、打卡与提醒。" to "Create a group or enter an invite code to sync location, status, check-ins and reminders with their phone or device.",
    "把关心的人放进地图" to "Put the people you care about on the map",
    "念安不只是一款驾驶监测 App。对方可以是使用手机的家人、伴侣，也可以是车上或家里的设备。驾驶安全只是其中一种关心方式，学习、休息、位置与天气都会出现在这里。" to "TOUCHMIND is more than a driver-monitoring app. The other person can be family, a partner on their phone, or a device at home or in the car. Driving safety is just one way to care; study, rest, location and weather all show up here.",
    "当前为本地演示模式，请先登录云端账号" to "Local demo mode. Sign in to a cloud account first.",
    "当前为演示数据，接入 TA 的手机 / ESP32 后自动切换为真实状态。" to "Demo data. It switches to real status once their phone or device is connected.",
    "已加入关心组，TA 的状态会开始同步" to "Joined the care group. Their status will start syncing.",
    "已退出关心组，回到本地演示模式" to "Left the care group. Back to local demo mode.",
    "关心组已创建，把邀请码发给 TA" to "Care group created. Share the invite code.",
    "关心组已创建，等待 TA 输入邀请码加入。" to "Care group created. Waiting for them to join.",
    "创建失败，请检查服务器连接" to "Create failed. Check the server connection.",
    "加入失败，请检查邀请码" to "Join failed. Check the invite code.",
    "退出失败" to "Leave failed",
    "已连接" to "Connected",
    "连接中" to "Connecting…",
    "演示" to "Demo",
    "演示模式" to "Demo mode",
    "本地演示" to "Local demo",
    "正在连接云端…" to "Connecting to the cloud…",
    "云端同步失败（保持本地模式）" to "Cloud sync failed (staying local)",
    "云端同步失败，已保存到本机" to "Cloud sync failed; saved locally",
    "云端暂未同步，已先记录在本机" to "Not synced yet; saved locally",
    "上报自身状态失败" to "Failed to report status",
    "未接入真实设备时，生成一份稳定的示例位置与生活状态，方便体验地图、打卡和天气。" to "Without a real device, stable demo location and status let you try the map, check-ins and weather.",
    "还没有绑定设备或手机，演示模式会先生成示例状态。" to "No device or phone bound yet; demo mode will generate sample status.",

    // 地图 / 定位
    "正在获取你的位置" to "Getting your location",
    "定位还在路上。稍等片刻，或点击下方按钮重新获取。" to "Location is on the way. Wait a moment or tap below to retry.",
    "需要定位权限" to "Location permission needed",
    "允许定位后，地图才会显示你和 TA 的位置、距离与天气" to "Allow location to see both of your positions, distance and weather",
    "回到我的位置" to "Recenter",
    "对方位置" to "Their location",
    "地图" to "Map",

    // 底部导航 / 抽屉
    "行程" to "Trips",
    "亲友" to "Loved ones",
    "智能体" to "Smart Pet",
    "智能宠物" to "Smart Pet",
    "宠物小窝" to "Pet nook",
    "再按一次返回退出念安" to "Press back again to exit TOUCHMIND",
    "添加任务" to "Add task",
    "切换明暗模式" to "Toggle theme",

    // 地图页 / 导航面板
    "会合点" to "Meetup point",
    "地图选点" to "Map pin",
    "地图地点" to "Map place",
    "对象" to "Person",
    "切换对象" to "Switch person",
    "骑行" to "Cycling",
    "公交" to "Transit",
    "到达目的地" to "Arrived at destination",
    "静音" to "Mute",
    "取消静音" to "Unmute",
    "退出导航" to "Exit navigation",
    "播报" to "Announce",
    "结束导航" to "End navigation",
    "用百度地图导航（会关闭念安语音）" to "Navigate with Baidu Maps (turns off TOUCHMIND voice)",
    "还没有获取到当前位置，暂时无法规划路线" to "No current location yet; can't plan a route",
    "路线规划失败，请检查网络后重试" to "Route planning failed. Check the network and retry.",
    "导航" to "Navigation",
    "正在沿道路规划路线…" to "Planning a road route…",
    "重新规划" to "Re-plan",
    "正在规划路线…" to "Planning route…",
    "开始导航" to "Start navigation",
    "TA 还未上线，暂时没有对方的导航时间" to "They're offline; no ETA from them yet",
    "附近" to "Nearby",
    "没有找到相关地点" to "No places found",
    "全国" to "Nationwide",
    "搜索范围" to "Search area",
    "默认优先搜索当前位置附近 10 公里。也可以切换城市或全国。" to "Searches within 10 km by default. You can switch to a city or nationwide.",
    "城市，例如：杭州" to "City, e.g. Hangzhou",
    "确定" to "OK",
    "搜索地点" to "Search places",
    "输入地点名称，结果会像百度地图一样即时出现" to "Type a place name; results appear instantly",
    "双人会合" to "Meetup",
    "关闭会合点" to "Clear meetup point",
    "预计时间按直线距离估算：步行 5km/h，驾车 30km/h。" to "ETAs are estimated from straight-line distance: walking 5 km/h, driving 30 km/h.",
    "导航到会合点" to "Navigate to meetup point",
    "位置未知" to "Location unknown",
    "未连接" to "Offline",
    "语音留言" to "Voice message",
    "说点什么…" to "Say something…",
    "表情" to "Emoji",
    "更多" to "More",
    "分心状态" to "Distraction",
    "沿当前道路继续前行" to "Continue along the current road",

    // 对话 / 留言
    "对话" to "Chat",
    "个人模式" to "Personal mode",
    " · 只显示对话消息" to " · Chat messages only",
    "还没有对话，说点什么吧。" to "No messages yet. Say something.",
    "按住 说话" to "Hold to talk",
    "发送" to "Send",
    "添加照片" to "Add photo",
    "留言图片" to "Message image",
    "查看照片" to "View photo",
    "播放语音" to "Play voice",
    "留言墙" to "Message wall",
    "最新留言会从右边滑进来" to "New messages slide in from the right",
    "今天还没有留言" to "No messages today yet",
    "从下面发出第一条，它会从右边滑进来。" to "Send the first one below; it slides in from the right.",
    "发了一张照片" to "sent a photo",
    "发来一张照片" to "sent you a photo",
    "发了一段语音" to "sent a voice message",
    "发来一段语音" to "sent you a voice message",
    "记录了一张照片" to "logged a photo",

    // 打卡
    "还没有今天的任务，点右上角加号写下要一起完成的事。" to "No tasks today. Tap + to write something to finish together.",
    "该项已完成" to "Done",
    "你已完成，TA 还没完成" to "You're done; they aren't yet",
    "TA 已完成，等你了" to "They're done; waiting for you",
    "待完成" to "To do",
    "提醒对方完成" to "Remind them",
    "演示：TA 已完成" to "Demo: they're done",
    "没有可用的麦克风" to "No microphone available",
    "停止并发送语音" to "Stop and send voice",
    "录制语音留言" to "Record a voice message",
    "给 TA 留一句话…" to "Leave them a message…",
    "打卡任务" to "Check-in tasks",
    "先写一条任务吧" to "Write a task first",
    "云端同步失败，已先记录在本机" to "Cloud sync failed; saved locally",
    "今天的任务还差一点，记得完成哦。" to "Today's task is almost there—remember to finish it.",
    "已提醒 TA 完成任务" to "Reminded them to finish the task",

    // 状态
    "今天心情不错" to "Feeling good today",
    "有点想你了" to "Missing you a little",
    "忙完想歇一会儿" to "Want to rest after this",
    "准备早点休息" to "Heading to bed early",
    "正在处理事情，晚点回" to "Busy now, will reply later",
    "先去吃点东西" to "Getting something to eat",
    "正在路上，注意安全" to "On the way, drive safe",
    "切换状态" to "Switch status",
    "状态留言" to "Status note",

    // 设备
    "绑定设备" to "Bind device",
    "输入设备标签/屏幕上显示的一串设备码；设备码已加密并带校验位，不包含项目名或开发板型号。" to "Enter the device code shown on the device screen. It's encrypted with a checksum and contains no project or board name.",
    "设备码" to "Device code",
    "设备名称（可选，如：TA 的车载设备）" to "Device name (optional, e.g. their car device)",
    "没有设备？生成一个本地演示设备" to "No device? Generate a local demo device",
    "暂无绑定设备。输入设备码后，设备会出现在这里并同步到当前关心组。" to "No devices bound. Enter a device code and it will appear here and sync to the current group.",
    "关心组设备" to "Group devices",
    "已加入当前云端关心组的 ESP32 设备，它们的在线状态、位置与驾驶信息会同步到关心页。" to "ESP32 devices in the current cloud group; their online status, location and driving info sync to the Care page.",
    "复制设备码" to "Copy device code",
    "请输入设备码" to "Enter a device code",
    "设备码无效，请检查是否完整复制" to "Invalid device code. Make sure it was copied completely.",
    "设备已保存；创建/加入关心组后可在设备页重新绑定入组。" to "Device saved. After creating or joining a care group, bind it to the group again from the Devices page.",
    "新设备" to "New device",
    "加入关心组失败，请检查登录与网络" to "Couldn't join the care group. Check your sign-in and network.",
    "移出关心组失败，请稍后再试" to "Couldn't remove from the care group. Try again later.",

    // 关心组
    "创建 / 加入关心组后，双方的位置、状态、打卡与提醒会通过云端同步；未加入、未登录或服务器不可用时仍可使用个人模式。设备上报的定位与驾驶状态仍会优先覆盖云端数据。" to "After creating or joining a care group, location, status, check-ins and reminders sync through the cloud. Personal mode stays available offline or when signed out. Device-reported location and driving status still take priority.",
    "组长设置的验证密码" to "Password set by the group owner",
    "提交申请" to "Submit request",
    "给关心组起个名字，并设置验证密码；组员申请后需要你通过。" to "Name the group and set a password; you approve members after they apply.",
    "组名，例如：家庭组" to "Group name, e.g. Family",
    "验证密码（至少 4 位）" to "Password (4+ characters)",
    "我的关心组" to "My care groups",
    "关心组" to "Care group",
    "当前关心组" to "Current group",
    "切换到此组" to "Switch to this group",
    "手机通过邀请码加入关心组。" to "Phones join a care group with an invite code.",
    "关心组已创建，等待成员加入。" to "Care group created. Waiting for members.",
    "待审批的加入申请" to "Pending requests",
    "通过" to "Approve",
    "拒绝" to "Decline",
    "组员" to "Members",
    "解散关心组" to "Dissolve care group",
    "已保存，TA 的信息会同步到地图与日程" to "Saved. Their info will sync to the map and calendar.",
    "请设置至少 4 位验证密码" to "Set a password of at least 4 characters",
    "关心组已创建，把邀请码和验证密码发给 TA" to "Care group created. Share the invite code and password.",
    "已提交加入申请，等待组长确认" to "Request sent. Waiting for the owner's approval.",
    "加入失败，请检查邀请码或密码" to "Join failed. Check the invite code or password.",
    "切换关心组失败" to "Couldn't switch care group",
    "已通过加入申请" to "Request approved",
    "审批失败" to "Approval failed",
    "已拒绝加入申请" to "Request declined",
    "处理失败" to "Action failed",
    "已移除组员" to "Member removed",
    "移除失败" to "Couldn't remove member",
    "关心组已解散，所有组员已退出" to "Care group dissolved; all members have left.",
    "操作失败" to "Action failed",
    "亲友已删除，已回到个人模式" to "Loved one removed. Back to personal mode.",

    // 亲友设置 / 天气
    "称呼" to "Nickname",
    "比如：妈妈、阿哲" to "e.g. Mom, Alex",
    "删除亲友" to "Remove loved one",
    "距离未知" to "Distance unknown",
    "当地天气" to "Local weather",
    "对方还没有共享位置" to "They haven't shared location yet",
    "左右滑动看下一位亲属" to "Swipe for the next loved one",
    "亲属" to "Loved one",
    "情侣" to "Couple",
    "爱人" to "Partner",
    "编辑" to "Edit",
    "看位置" to "View location",
    "去看一看 ›" to "Take a look ›",
    "去看看 ›" to "Take a look ›",
    "今天的情话" to "Today's sweet line",
    "换一句" to "Another line",
    "发送中…" to "Sending…",
    "发给 TA" to "Send to them",
    "提醒对方" to "Nudge them",
    "建议：发一条语音或提醒 TA 在安全的地方休息，不要连续驾驶。" to "Tip: send a voice message or ask them to rest somewhere safe; don't drive continuously.",
    "再想几条" to "More ideas",
    "生成四条" to "Generate four",
    "生成三条" to "Generate three",
    "智能体会结合 TA 的状态与两地天气，一次给出行动、表达、小惊喜和一句情话。" to "Smart Pet combines their status and both weathers to give an action, a message, a small surprise and a sweet line.",
    "智能体会结合 TA 的状态与两地天气，一次给出行动、表达和小惊喜三个角度。" to "Smart Pet combines their status and both weathers to give an action, a message and a small surprise.",
    "生成后仅展示 3 分钟，随后自动释放。" to "Shown for 3 minutes, then released.",
    "正在想 4 条不同角度的关心，其中一条是情话…" to "Thinking of 4 care ideas, one of them a sweet line…",
    "正在想 3 条不同角度的关心…" to "Thinking of 3 care ideas…",
    "还没有关心建议。点「生成」，让智能体根据 TA 此刻的状态，给出今天就能用上的话。" to "No care tips yet. Tap Generate and Smart Pet will suggest something useful for today based on their status.",
    "马上做" to "Do now",
    "说句话" to "Say something",
    "小惊喜" to "Small surprise",
    "情话" to "Sweet line",

    // 日历
    "添加日程" to "Add event",
    "图片读取失败" to "Couldn't load image",
    "记录一件事" to "Log something",
    "例如：去图书馆看了会儿书" to "e.g. Read at the library",
    "新建日程" to "New event",
    "先写一个标题" to "Write a title first",
    "日期与时间" to "Date & time",
    "年" to "Year",
    "月" to "Month",
    "时" to "Hour",
    "分" to "Minute",
    "写点什么再分享吧" to "Write something before sharing",
    "需要 TA 在自己的念安里打卡，双方日程才会一起变红" to "They need to check in on their TOUCHMIND before the day turns red",

    // 浪漫清单
    "先从这一百件开始。完成的每一件，都会累计进你们的一万件。" to "Start with these 100. Every finished one counts toward your 10,000.",
    "随机抽一件" to "Pick one at random",
    "全部" to "All",
    "已完成" to "Done",
    "未完成" to "Not done",
    "今天做这一件" to "Do this one today",
    "就做这件" to "Let's do this one",
    "再抽一次" to "Pick again",

    // 动态记录
    "是" to "Yes",
    "否" to "No",
    "关心提醒" to "Care nudge",

    // 设置 / 关于
    "在地图上显示关心的人" to "Show loved ones on the map",
    "会说话的小智" to "Talkative Xiaozhi",
    "小智是念安里的 AI 陪伴助手：可以陪你说说话、提醒你休息，也能帮你看 TA 的状态和天气。它会用嘴型和音律条回应你的每一句话，语音可以随时关掉；对话只保存在本机，不会同步给对方。" to "Xiaozhi is TOUCHMIND's AI companion: it chats with you, reminds you to rest, and can check their status and weather. Its mouth and sound bars respond to every line; voice can be turned off anytime. Chats stay on this device and are never synced to them.",
    "念安是一款面向亲属、伴侣与家人的互相关心 App。设备既可以是专用硬件，也可以是我们每天随身携带的手机：在地图上看见彼此的位置，了解 TA 正在学习、工作、休息还是开车；一起在日程里打卡，双方都完成时那一天会亮起红色；也可以为彼此设置定时提醒，并查看两地天气。\n\n驾驶疲劳检测是念安的能力之一：当对方使用车载设备时，疲劳、分心与紧急状态会作为关心提醒出现，而不是 App 的全部主题。" to "TOUCHMIND is a mutual-care app for family, partners and loved ones. A device can be dedicated hardware or the phone we carry every day: see each other on the map, know whether they're studying, working, resting or driving; check in together on the calendar, and the day turns red when both finish; set reminders and see the weather in both places.\n\nDriver fatigue detection is one of TOUCHMIND's capabilities: when they use a car device, fatigue, distraction and emergencies appear as care alerts, not as the app's whole theme.",

    // 通用内容描述
    "头像" to "Avatar",
    "默认头像" to "Default avatar",
    "桌面宠物，点一下进入宠物小窝" to "Desktop pet — tap to open the pet nook",
    "猫头鹰宠物，点一下摸摸它" to "Owl pet — tap to pet it",
    "宠物，点一下摸摸它" to "Pet — tap to pet it",
    "卫星" to "Satellite",
    "放大地图" to "Zoom in",
    "缩小地图" to "Zoom out",
    "设为会合点" to "Set as meetup point",

    // 状态 / 设备类型 / 疲劳
    "在线" to "Online",
    "学习中" to "Studying",
    "工作中" to "Working",
    "通勤中" to "Commuting",
    "驾驶中" to "Driving",
    "休息中" to "Resting",
    "睡觉中" to "Sleeping",
    "运动中" to "Exercising",
    "需要休息" to "Needs rest",
    "需要帮助" to "Needs help",
    "状态未知" to "Status unknown",
    "手机" to "Phone",
    "设备" to "Device",
    "正常" to "Normal",
    "轻度疲劳" to "Mild fatigue",
    "中度疲劳" to "Moderate fatigue",
    "重度疲劳" to "Severe fatigue",
    "医学异常" to "Medical alert",
    "无" to "None",
    "跌倒" to "Fall",
    "抽搐" to "Seizure",
    "意识丧失" to "Unconscious",

    // 宠物：外观 / 状态 / 场景
    "林鸮" to "Tawny owl",
    "雪鸮" to "Snowy owl",
    "墨猫" to "Ink cat",
    "田园犬" to "Rural dog",
    "仓鼠" to "Hamster",
    "雪团" to "Snowball",
    "墨墨" to "Inky",
    "阿黄" to "Sunny",
    "团子" to "Mochi",
    "鸮鸮" to "Hoot",
    "正在打开宠物小窝…" to "Opening the pet nook…",
    "正在唤醒小室友…" to "Waking your companion…",
    "稍等…" to "One moment…",
    "睡着中" to "Sleeping",
    "吃不下" to "Not hungry",
    "今日吃饱" to "Full today",
    "投喂" to "Feed",
    "加粮" to "Add food",
    "先叫醒它" to "Wake it first",
    "它吃饱了" to "It's full",
    "极夜小室友" to "Polar-night companion",
    "夜巡小室友" to "Night-watch companion",
    "看家小室友" to "Home-guard companion",
    "囤粮小室友" to "Hoarder companion",
    "夜班小室友" to "Night-shift companion",
    "夜巡性" to "Nocturnal wanderer",
    "白天活跃" to "Daytime active",
    "夜间活跃" to "Night active",
    "夜行性" to "Nocturnal",
    "✏️ 改名" to "✏️ Rename",
    "猫头鹰的习性" to "Owl habits",
    "睡着了" to "Asleep",
    "有点积食" to "A little overfed",
    "点一下叫醒它" to "Tap to wake it",
    "点它摸摸" to "Tap to pet",
    "饱腹" to "Fullness",
    "精力" to "Energy",
    "心情" to "Mood",
    "还没人喂过" to "Not fed yet",
    "叫醒" to "Wake",
    "摸摸" to "Pet",
    "抚摸" to "Pet",
    "名字" to "Name",
    "名字（可选）" to "Name (optional)",
    "它会回到夜空，当前的饱腹、精力、心情和亲密会清空；以后还可以重新领养。名字和外观选择会保留。" to "It will return to the night sky. Fullness, energy, mood and bond reset; you can adopt again later. Name and look are kept.",
    "放归" to "Release",
    "放归它" to "Release it",
    "再想想" to "Not yet",
    "还没有领养宠物" to "No pet yet",
    "想养的时候，随时可以领养一只小宠物。" to "Adopt a little companion whenever you're ready.",
    "领养一只" to "Adopt one",
    "LIVE 2D · 宠物待领养" to "LIVE 2D · Awaiting adoption",
    "领养一只小宠物" to "Adopt a little companion",
    "领养一只小室友" to "Adopt a little companion",
    "它会在关心页陪着你们。可以自己挑一只，也可以随机领养。" to "It will keep you company on the Care page. Pick one or adopt at random.",
    "待领养" to "Awaiting adoption",
    "随机领养" to "Adopt at random",
    "随机领养一只" to "Adopt at random",
    "领养它" to "Adopt",
    "暂不领养" to "Not now",
    "先领养雪鸮「雪团」" to "Adopt the snowy owl \"Snowball\"",
    "小窝" to "Nook",
    "院子" to "Yard",
    "在窝里打盹" to "Napping in the nook",
    "在小窝休息" to "Resting in the nook",
    "在院子活动" to "Out in the yard",
    "它会按自己的作息，在小窝和院子之间活动。" to "It moves between the nook and the yard on its own schedule.",
    "它跟着你回到小窝，把爪子收进了软垫。" to "It follows you back and tucks its paws into the cushion.",
    "它推开门，先去院子里转一圈。" to "It pushes the door open and wanders into the yard.",
    "自动喂食机、饮水机会作为订阅服务开放，可远程补粮、换水。" to "Auto feeders and waterers will be available as a subscription for remote refills.",
    "自动喂食机 / 饮水机" to "Auto feeder / waterer",
    "订阅服务筹备中" to "Subscription coming soon",
    "了解" to "Learn more",
    "它睡着了，先摸摸把它叫醒吧。" to "It's asleep—pet it awake first.",
    "它已经吃饱了，晚一点再喂也不迟。" to "It's already full; feeding can wait.",
    "清晨" to "Dawn",
    "白天" to "Day",
    "黄昏" to "Dusk",
    "深夜" to "Late night",
    "黄昏最精神" to "Most alert at dusk",
    "夜间精神" to "Alert at night",
    "白天打盹" to "Naps by day",
    "夜巡性：清晨和傍晚最精神，白天喜欢找地方打盹。" to "Nocturnal wanderer: most alert at dawn and dusk; naps during the day.",
    "白天活跃：喜欢有人陪，精力好的时候会围着你转。" to "Daytime active: loves company and follows you around when energetic.",
    "夜间活跃：白天躲着睡，晚上开始囤粮、跑轮。" to "Night active: sleeps by day, hoards food and runs at night.",
    "夜行性：清晨、黄昏和深夜最精神，白天会犯困。" to "Nocturnal: most alert at dawn, dusk and late night; sleepy by day.",
    "不能一直喂：刚吃过要消化 2 分钟，每天最多 6 顿；太饱会拒绝，硬喂会积食。" to "Don't feed constantly: digestion takes 2 minutes, max 6 meals a day; it refuses when full and overeats if forced.",
    "精力太低会自己睡着。睡着时先摸摸叫醒，再喂它。" to "When energy is low it falls asleep. Pet it awake before feeding.",
    "慢慢摸会加亲密；连续戳它会被嫌弃，甚至会掉心情。" to "Gentle petting builds bond; repeated pokes annoy it and lower mood.",
    "饱腹、精力和心情会随真实时间变化，离开 App 也一样。" to "Fullness, energy and mood change with real time, even when the app is closed.",
    "嘘——它缩成一团睡着了。" to "Shh—it's curled up asleep.",
    "肚子空空的…有吃的吗？" to "Hungry… any food?",
    "眼皮好重，想缩成一团。" to "Eyelids heavy… wants to curl up.",
    "吃太撑了，动都不想动…" to "Too full to move…",
    "咕——雪夜很安静，你也在。" to "Hoo—the snowy night is quiet, and you're here.",
    "呼噜呼噜——你在，它就安心了。" to "Purr… it feels safe with you.",
    "汪！尾巴摇得停不下来。" to "Woof! Its tail won't stop wagging.",
    "吱吱，它把一颗瓜子推到你面前。" to "Squeak—it pushes a seed toward you.",
    "咕——今晚月色不错，你也在。" to "Hoo—lovely moon tonight, and you're here.",
    "它眯着眼，尾巴一下一下地拍着地面。" to "Eyes half-closed, tail tapping the floor.",
    "它歪着头，把下巴搁在你手边。" to "It tilts its head and rests its chin by your hand.",
    "它鼓着腮帮子，认真地看着你。" to "Cheeks puffed, it looks at you earnestly.",
    "它蓬起雪白的羽毛，像一团会呼吸的雪。" to "It fluffs its white feathers like breathing snow.",
    "咕咕。它歪着头看你。" to "Hoo. It tilts its head at you.",
    "它叼走食物，一口吞下，满足地眯起眼。" to "It takes the food in one bite, eyes content.",
    "吃太急了…肚子鼓鼓的，它需要缓一会儿。" to "Ate too fast… tummy round, it needs a moment.",
    "它睡着了。先摸摸叫醒它，再喂也不迟。" to "It's asleep. Pet it awake before feeding.",
    "它眯起眼睛，把脑袋往你手心蹭了蹭。" to "It closes its eyes and nuzzles your palm.",
    "别一直戳啦——它抖了抖毛，往旁边挪了一步。" to "Stop poking—it shakes its fur and steps aside.",
    "唔…被你戳醒了，眼睛还没聚焦。" to "Mm… woken up, eyes still unfocused.",
    "蜷在软垫里，呼吸慢慢变匀了。" to "Curled on the cushion, breathing slowly.",
    "食盆空了一会儿，它时不时抬头看你。" to "The bowl has been empty for a while; it keeps looking up at you.",
    "它打了个哈欠，眼皮快要撑不住了。" to "It yawns, eyelids heavy.",
    "吃得有点撑，正趴着慢慢消化。" to "A little full, lying down to digest.",
    "心情很好，尾巴尖轻轻晃着。" to "Feeling good, tail tip swaying.",
    "在窝里转了一圈，又回到你脚边。" to "It circles the nook and comes back to your feet.",
    "在院子里追一片落叶，玩得很专注。" to "Chasing a leaf in the yard, fully focused.",
    "好吃！它把粮吃得干干净净。" to "Yum! It cleans the bowl.",
    "吃得有点撑，它想慢慢消化一会儿。" to "A bit full; it wants to digest slowly.",
    "它眯起眼睛，往你手心里蹭了蹭。" to "It closes its eyes and nuzzles your palm.",
    "摸得太急啦，它甩了甩耳朵。" to "Too much petting—it flicks its ears.",
    "它被你叫醒了，伸了个懒腰。" to "It wakes up and stretches.",
    "羽毛" to "feathers",
    "毛" to "fur",
    "手机 · 亲属组" to "Phone · care group",
    "已发给 TA" to "Sent to them",
    "发送失败，稍后再试" to "Send failed, try again later",
    "元旦" to "New Year's Day",
    "情人节" to "Valentine's Day",
    "妇女节" to "Women's Day",
    "劳动节" to "Labour Day",
    "儿童节" to "Children's Day",
    "国庆节" to "National Day",
    "圣诞节" to "Christmas",
    "植树节" to "Arbor Day",
    "青年节" to "Youth Day",
    "教师节" to "Teachers' Day",
    "春节" to "Spring Festival",
    "元宵" to "Lantern Festival",
    "龙抬头" to "Longtaitou",
    "端午" to "Dragon Boat Festival",
    "七夕" to "Qixi Festival",
    "中元" to "Zhongyuan Festival",
    "中秋" to "Mid-Autumn Festival",
    "重阳" to "Double Ninth Festival",
    "寒衣" to "Winter Clothing Festival",
    "下元" to "Xiayuan Festival",
    "腊八" to "Laba Festival",
    "小年" to "Little New Year",
    "除夕" to "New Year's Eve",
    "小寒" to "Minor Cold",
    "大寒" to "Major Cold",
    "立春" to "Start of Spring",
    "雨水" to "Rain Water",
    "惊蛰" to "Awakening of Insects",
    "春分" to "Spring Equinox",
    "清明" to "Qingming",
    "谷雨" to "Grain Rain",
    "立夏" to "Start of Summer",
    "小满" to "Grain Buds",
    "芒种" to "Grain in Ear",
    "夏至" to "Summer Solstice",
    "小暑" to "Minor Heat",
    "大暑" to "Major Heat",
    "立秋" to "Start of Autumn",
    "处暑" to "End of Heat",
    "白露" to "White Dew",
    "秋分" to "Autumn Equinox",
    "寒露" to "Cold Dew",
    "霜降" to "Frost's Descent",
    "立冬" to "Start of Winter",
    "小雪" to "Minor Snow",
    "大雪" to "Major Snow",
    "冬至" to "Winter Solstice",
    "关怀模式" to "Care mode",
    "放大全局字号，方便长辈阅读；布局会随字号自动换行。" to "Larger text for easier reading; layouts wrap automatically.",
    "开启后字号放大到 1.25 倍；下方也可以单独微调字体和朗读速度。" to "Turns text up to 1.25x; you can fine-tune font size and speech rate below.",
    "朗读音色" to "Reading voice",
    "朗读模式" to "Reading mode",
    "云端" to "Cloud",
    "离线" to "Offline",
    "云端优先使用系统网络音色；没有网络音色时自动回退离线音色。" to "Cloud prefers the system network voice and falls back to offline when unavailable.",
    "离线优先使用已下载的音色；方言音色需要先在系统中安装。" to "Offline prefers downloaded voices; dialect voices must be installed in the system first.",
    "下载离线音色" to "Download offline voice",
    "普通话" to "Mandarin",
    "粤语" to "Cantonese",
    "英语" to "English",
    "方言音色取决于系统 TTS 是否安装；没有对应音色时会提示。" to "Dialect voices depend on the system TTS engine; you'll be notified if one is missing.",
    "当前系统没有该方言音色，请先在系统设置中安装。" to "This dialect voice isn't installed. Please add it in system settings.",
    "先去宠物小窝领养一只宠物，再让它成为小智的形象。" to "Adopt a pet in the Pet nook first, then it can become Xiaozhi's look.",
    "形象：宠物" to "Look: Pet",
    "形象：光核" to "Look: Orb",
    "给智能宠物改名" to "Rename your Smart Pet",
    "默认叫小智" to "Default: Xiaozhi",
    "这台设备没有可用的语音引擎，仍可以文字聊天。" to "No voice engine is available on this device; you can still chat by text.",
    "没有可用的语音引擎" to "No voice engine available",
    "语音引擎还在准备，稍等一下" to "The voice engine is still preparing, one moment",
    "你不用很厉害，你只要是你，剩下的我来。" to "You don't have to be great—just be you, and I'll handle the rest.",
    "我喜欢的不是完美的你，是每个早上还没睡醒的你。" to "I don't love the perfect you; I love the half-asleep you every morning.",
    "今天也没有特别的事，只是又比昨天多喜欢你一点。" to "Nothing special today—I just like you a little more than yesterday.",
    "世界很大，但我只想和你挤在同一把伞下。" to "The world is big, but I only want to share one umbrella with you.",
    "你负责平安抵达，我负责一直等你。" to "You focus on arriving safely; I'll focus on waiting for you.",
    "累了就往我这边靠一会儿，世界可以等，我先等你。" to "When you're tired, lean on me. The world can wait—I'll wait for you.",
    "天气变凉了，我对你的喜欢没有。" to "The weather turns cold; my fondness for you doesn't.",
    "想和你吃很多顿饭，从今天到很老。" to "I want to share countless meals with you, from today until we're old.",
    "今晚的月亮替我抱抱你，晚安。" to "Tonight the moon hugs you for me. Good night.",
    "你认真做事的样子我也喜欢，包括没空回我消息的样子。" to "I love the way you focus—even when you're too busy to reply.",
    "我攒了很多小事，想一件一件和你做完。" to "I've saved up so many little things; I want to finish them with you one by one.",
    "不用急着变好，我们可以一起慢慢来。" to "No rush to become better; we can take our time together.",
    "你出现以后，普通的日子开始有了值得记住的细节。" to "Since you appeared, ordinary days have details worth remembering.",
    "如果今天不开心，就把今天借给我，我替你收着。" to "If today isn't happy, lend it to me—I'll keep it for you.",
    "我想要的浪漫，是和你把日子过成习惯。" to "The romance I want is making a habit of our days together.",
    "你不用回头看，我一直在你看得见的地方。" to "No need to look back; I'm always somewhere you can see.",
    "想和你一起浪费很多个下午，什么都不做。" to "I want to waste many afternoons with you, doing nothing.",
    "你是我所有计划里，唯一不想改的那一项。" to "You're the only item in all my plans I never want to change.",
    "就算什么都不说，和你待在一起也很好。" to "Even saying nothing, being with you is good.",
    "我把“以后”想了很多遍，每一遍都有你。" to "I've imagined the future many times; every version has you.",
    "你一笑，我就觉得今天没有白过。" to "When you smile, I feel today wasn't wasted.",
    "我们不用每天都很好，只要每天都还在。" to "We don't have to be great every day—just still here every day.",
    "想和你一起变老，然后继续为小事吵架又和好。" to "I want to grow old with you, still arguing over small things and making up.",
    "这世界偶尔很吵，但你在我身边的时候很安静。" to "The world is noisy sometimes, but it's quiet when you're beside me.",

    // 小智
    "我有点累" to "I'm a bit tired",
    "TA 在哪？" to "Where are they?",
    "今天天气" to "Today's weather",
    "陪我聊聊" to "Chat with me",
    "嗯？我在呢。" to "Hm? I'm here.",
    "你叫我啦？" to "You called?",
    "我一直都在，你说。" to "I'm always here. Go ahead.",
    "刚刚在发呆，现在专心听你。" to "I was spacing out; now I'm all ears.",
    "这台设备没有可用的中文语音引擎，仍可以文字聊天。" to "No Chinese TTS engine on this device; you can still chat by text.",
    "没有可用的中文语音引擎" to "No Chinese TTS engine available",
    "语音引擎还在准备，稍等一下" to "Voice engine is still preparing; one moment",
    "让我想想…" to "Let me think…",
    "正在说话" to "Speaking",
    "我在听" to "Listening",
    "随时都在" to "Always here",
    "点一下小智，它会回你一句" to "Tap Xiaozhi and it will reply",
    "正在组织一句不敷衍的话" to "Thinking of a real reply",
    "正在朗读回复" to "Reading the reply aloud",
    "跟小智说点什么…" to "Say something to Xiaozhi…",
    "清空和小智的对话？" to "Clear the chat with Xiaozhi?",
    "对话只保存在本机，清空后无法恢复。" to "Chats are stored only on this device and can't be restored.",
    "清空" to "Clear",
    "小智" to "Xiaozhi",
    "关闭语音播报" to "Turn voice off",
    "开启语音播报" to "Turn voice on",
    "清空对话" to "Clear chat",
    "我是小智" to "I'm Xiaozhi",
    "住在念安里的小机器人。可以陪你聊聊、提醒你休息，也能帮你看 TA 的位置和天气。" to "A little robot living in TOUCHMIND. I can chat, remind you to rest, and check their location and weather.",
    "对话只保存在本机；语音由系统 TTS 朗读，不会上传录音。" to "Chats stay on this device; voice uses system TTS and recordings are never uploaded.",
    " · 本地" to " · Local",
    "朗读这条回复" to "Read this reply aloud",
    "小智正在想" to "Xiaozhi is thinking",
    "小智，点一下和它打招呼" to "Xiaozhi — tap to say hello",
    "对方" to "Them",
    "我这边刚刚走神了，没接上。你再说一遍好吗？" to "I spaced out and missed that. Could you say it again?",
    "周一" to "Mon",
    "周二" to "Tue",
    "周三" to "Wed",
    "周四" to "Thu",
    "周五" to "Fri",
    "周六" to "Sat",
    "周日" to "Sun",
)
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/NavigationDialog.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.util.NavMode

@Composable
fun NavigationModeDialog(
    targetName: String,
    onDismiss: () -> Unit,
    onSelect: (NavMode) -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("导航到 $targetName") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "选择出行方式，将打开手机里的地图 App。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                NavMode.entries.forEach { mode ->
                    Surface(
                        onClick = { onSelect(mode) },
                        shape = RoundedCornerShape(14.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 14.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            Text(mode.emoji, style = MaterialTheme.typography.headlineSmall)
                            Text(
                                text = mode.label,
                                style = MaterialTheme.typography.bodyLarge,
                                fontWeight = FontWeight.Medium,
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("取消") }
        },
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/OwlLive2D.kt`

> 林鸮 / 雪鸮外壳与睡眠动效入口。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

/** 猫头鹰的待机动作，符合猛禽习性：飞行、梳理羽毛、枝头小跳。 */
private enum class OwlIdleAction { IDLE, FLY, PREEN, SHUFFLE }

/**
 * 一只用 Compose Canvas 画的"Live2D 风格"猫头鹰。
 *
 * 没有引入 Cubism 运行时和外部模型包，而是把身体拆成头、眼、喙、翅、尾、脚，
 * 用呼吸、眨眼、视线跟随、歪头、抖羽、张嘴等分层动画模拟 Live2D 的"活着"的感觉。
 * 所有动作都由 [state] 和最近一次 [reaction]/[reactionToken] 驱动，可直接嵌入卡片。
 */
@Composable
fun OwlLive2D(
    state: PetState,
    reaction: PetReaction,
    reactionToken: Int,
    phase: PetDayPhase = PetDayPhase.NIGHT,
    modifier: Modifier = Modifier,
    contentDescription: String = "猫头鹰宠物，点一下摸摸它",
    onTap: () -> Unit = {},
    backdrop: Boolean = true,
    focus: Float = 1f,
) {
    val haptic = LocalHapticFeedback.current
    val scope = rememberCoroutineScope()
    val idle = rememberInfiniteTransition(label = "owl-idle")
    val breath by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2_700, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "breath",
    )
    val sway by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(5_600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "sway",
    )
    val twinkle by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(3_400, easing = LinearOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "twinkle",
    )
    val snowDrift by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(14_000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "snow",
    )
    val look = remember(state.species, phase) { owlPalette(state.species).withPhase(phase) }

    val blink = remember { Animatable(1f) }
    LaunchedEffect(state.asleep) {
        if (state.asleep) {
            blink.snapTo(0f)
            return@LaunchedEffect
        }
        blink.snapTo(1f)
        while (true) {
            delay(Random.nextLong(2_400L, 5_600L))
            blink.animateTo(0.06f, tween(80))
            blink.animateTo(1f, tween(140))
            if (Random.nextInt(100) < 22) {
                delay(130)
                blink.animateTo(0.06f, tween(70))
                blink.animateTo(1f, tween(130))
            }
        }
    }

    val gazeX = remember { Animatable(0f) }
    val gazeY = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        while (true) {
            delay(Random.nextLong(3_200L, 6_800L))
            gazeX.animateTo(Random.nextFloat() * 1.3f - 0.65f, tween(850))
            gazeY.animateTo(Random.nextFloat() * 0.7f - 0.35f, tween(850))
        }
    }

    var activeReaction by remember { mutableStateOf(PetReaction.NONE) }
    val reactionProgress = remember { Animatable(0f) }
    var consumedReactionToken by remember { mutableIntStateOf(reactionToken) }
    LaunchedEffect(reactionToken) {
        if (reactionToken <= consumedReactionToken) return@LaunchedEffect
        consumedReactionToken = reactionToken
        activeReaction = reaction
        reactionProgress.snapTo(0f)
        reactionProgress.animateTo(
            1f,
            tween(1_350, easing = LinearOutSlowInEasing),
        )
        reactionProgress.snapTo(0f)
        activeReaction = PetReaction.NONE
    }

    val hootProgress = remember { Animatable(0f) }
    LaunchedEffect(state.asleep) {
        if (state.asleep) {
            hootProgress.snapTo(0f)
            return@LaunchedEffect
        }
        while (true) {
            delay(Random.nextLong(9_000L, 17_000L))
            hootProgress.snapTo(0f)
            hootProgress.animateTo(1f, tween(1_100, easing = LinearOutSlowInEasing))
            hootProgress.snapTo(0f)
        }
    }

    // 符合猛禽习性的待机动作：起飞绕一圈、梳理羽毛、枝头小跳。
    var owlIdleAction by remember { mutableStateOf(OwlIdleAction.IDLE) }
    val owlActionProgress = remember { Animatable(0f) }
    LaunchedEffect(state.asleep) {
        if (state.asleep) {
            owlIdleAction = OwlIdleAction.IDLE
            owlActionProgress.snapTo(0f)
            return@LaunchedEffect
        }
        while (true) {
            delay(Random.nextLong(7_000L, 14_000L))
            owlIdleAction = listOf(
                OwlIdleAction.FLY,
                OwlIdleAction.PREEN,
                OwlIdleAction.SHUFFLE,
            ).random()
            owlActionProgress.snapTo(0f)
            val (duration, easing) = when (owlIdleAction) {
                OwlIdleAction.FLY -> 6_400 to LinearEasing
                OwlIdleAction.PREEN -> 3_800 to FastOutSlowInEasing
                OwlIdleAction.SHUFFLE -> 900 to FastOutSlowInEasing
                OwlIdleAction.IDLE -> 1_000 to FastOutSlowInEasing
            }
            owlActionProgress.animateTo(1f, tween(duration, easing = easing))
            owlActionProgress.snapTo(0f)
            owlIdleAction = OwlIdleAction.IDLE
        }
    }

    val owlActionValue = owlActionProgress.value
    val fly = if (owlIdleAction == OwlIdleAction.FLY) owlActionValue else 0f
    val preen = if (owlIdleAction == OwlIdleAction.PREEN) owlActionValue else 0f
    val shuffle = if (owlIdleAction == OwlIdleAction.SHUFFLE) owlActionValue else 0f

    Box(
        modifier = modifier.semantics {
            this.contentDescription = contentDescription
        },
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTapGestures { offset ->
                        val nx = (offset.x / size.width - 0.5f) * 2f
                        val ny = (offset.y / size.height - 0.5f) * 2f
                        scope.launch {
                            gazeX.snapTo(nx.coerceIn(-1f, 1f))
                            gazeY.snapTo(ny.coerceIn(-0.7f, 0.7f))
                            delay(850)
                            gazeX.animateTo(0f, tween(700))
                            gazeY.animateTo(0f, tween(700))
                        }
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onTap()
                    }
                },
        ) {
            val sceneScale = min(size.width / 360f, size.height / 300f)
            withTransform({
                translate(
                    left = (size.width - 360f * sceneScale) / 2f,
                    top = (size.height - 300f * sceneScale) / 2f,
                )
                scale(sceneScale, sceneScale, pivot = Offset.Zero)
                scale(focus, focus, pivot = Offset(180f, 190f))
            }) {
                drawOwlScene(
                    phase = phase,
                    breath = breath,
                    sway = sway,
                    twinkle = twinkle,
                    snowDrift = snowDrift,
                    blink = blink.value,
                    gazeX = gazeX.value,
                    gazeY = gazeY.value,
                    fly = fly,
                    preen = preen,
                    shuffle = shuffle,
                    reaction = activeReaction,
                    reactionProgress = reactionProgress.value,
                    hootProgress = hootProgress.value,
                    asleep = state.asleep,
                    sleepy = state.energy <= 26,
                    look = look,
                    backdrop = backdrop,
                )
            }
        }
        if (state.asleep) {
            SleepingZzz()
        }
    }
}

@Composable
private fun SleepingZzz() {
    val transition = rememberInfiniteTransition(label = "owl-zzz")
    val float by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2_200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "zzz",
    )
    val color = Color(0xFFFFE3A3)
    Box(Modifier.fillMaxSize()) {
        Text(
            text = "z",
            color = color.copy(alpha = 0.26f + float * 0.28f),
            fontSize = 14.sp,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 84.dp, end = 96.dp)
                .graphicsLayer { translationY = -float * 5f },
        )
        Text(
            text = "Z",
            color = color.copy(alpha = 0.36f + float * 0.34f),
            fontSize = 18.sp,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 62.dp, end = 68.dp)
                .graphicsLayer { translationY = -float * 9f },
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/OwlParts.kt`

> 林鸮部件：头、翅、脚、叶片与爱心/碎屑/怒气粒子。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

internal fun DrawScope.drawWing(left: Boolean, look: OwlPalette) {
    val x = if (left) 116f else 214f
    drawOval(
        brush = Brush.verticalGradient(
            colors = listOf(look.wingLight, look.wingDark),
            startY = 148f,
            endY = 245f,
        ),
        topLeft = Offset(x, 146f),
        size = Size(30f, 102f),
    )
    drawOval(
        color = look.outline.copy(alpha = 0.55f),
        topLeft = Offset(x, 146f),
        size = Size(30f, 102f),
        style = Stroke(width = 1.6f),
    )
    for (i in 0..2) {
        drawLine(
            color = look.sideFeather.copy(alpha = 0.65f),
            start = Offset(x + 8f + i * 4f, 212f),
            end = Offset(x + 15f + i * 4f, 240f),
            strokeWidth = 1.3f,
            cap = StrokeCap.Round,
        )
    }
    if (look.snowy) {
        for (i in 0..2) {
            drawArc(
                color = look.sideFeather.copy(alpha = 0.42f),
                startAngle = 20f,
                sweepAngle = 140f,
                useCenter = false,
                topLeft = Offset(x + 4f, 166f + i * 17f),
                size = Size(16f, 9f),
                style = Stroke(width = 1.1f, cap = StrokeCap.Round),
            )
        }
    }
}

internal fun DrawScope.drawOwlHead(
    eyeOpen: Float,
    gazeX: Float,
    gazeY: Float,
    beakOpen: Float,
    asleep: Boolean,
    isPet: Boolean,
    isFeed: Boolean,
    isRefuse: Boolean,
    isWake: Boolean,
    rp: Float,
    sway: Float,
    living: Float,
    look: OwlPalette,
) {
    val tuftSway = sin(sway * 2.0 * PI).toFloat() * 2.2f * living

    // 林地褐鸮有三簇耳羽；雪鸮是圆头，不画耳羽。
    if (!look.snowy) {
        drawPath(
            path = Path().apply {
                moveTo(137f, 107f)
                cubicTo(131f, 92f, 124f, 76f, 122f + tuftSway, 58f)
                lineTo(130f, 69f)
                lineTo(127f + tuftSway * 0.6f, 49f)
                lineTo(137f, 70f)
                lineTo(140f + tuftSway * 0.4f, 55f)
                lineTo(148f, 84f)
                cubicTo(151f, 94f, 155f, 101f, 160f, 105f)
                close()
            },
            brush = Brush.verticalGradient(
                colors = listOf(look.tuftLight, look.tuftDark),
                startY = 48f,
                endY = 110f,
            ),
        )
        drawPath(
            path = Path().apply {
                moveTo(223f, 107f)
                cubicTo(229f, 92f, 236f, 76f, 238f - tuftSway, 58f)
                lineTo(230f, 69f)
                lineTo(233f - tuftSway * 0.6f, 49f)
                lineTo(223f, 70f)
                lineTo(220f - tuftSway * 0.4f, 55f)
                lineTo(212f, 84f)
                cubicTo(209f, 94f, 205f, 101f, 200f, 105f)
                close()
            },
            brush = Brush.verticalGradient(
                colors = listOf(look.tuftLight, look.tuftDark),
                startY = 48f,
                endY = 110f,
            ),
        )
        drawPath(
            path = Path().apply {
                moveTo(134f, 99f)
                lineTo(129f, 69f)
                lineTo(139f, 87f)
                close()
            },
            color = look.tuftInner.copy(alpha = 0.52f),
        )
        drawPath(
            path = Path().apply {
                moveTo(226f, 99f)
                lineTo(231f, 69f)
                lineTo(221f, 87f)
                close()
            },
            color = look.tuftInner.copy(alpha = 0.52f),
        )
    }

    // 头部。
    drawOval(
        brush = Brush.verticalGradient(
            colors = listOf(look.bodyLight, look.bodyMid, look.bodyDark),
            startY = 68f,
            endY = 190f,
        ),
        topLeft = Offset(111f, 70f),
        size = Size(138f, 120f),
    )
    drawOval(
        color = look.outline.copy(alpha = 0.76f),
        topLeft = Offset(111f, 70f),
        size = Size(138f, 120f),
        style = Stroke(width = 2.5f),
    )
    // 头顶羽毛的小尖。
    if (!look.snowy) {
        drawPath(
            path = Path().apply {
                moveTo(160f, 73f)
                lineTo(169f, 82f)
                lineTo(176f, 72f)
                lineTo(185f, 82f)
                lineTo(195f, 74f)
                lineTo(188f, 88f)
                lineTo(164f, 88f)
                close()
            },
            color = look.tuftDark.copy(alpha = 0.8f),
        )
    } else {
        // 雪鸮头顶细碎的灰色羽斑。
        for (i in 0..4) {
            drawCircle(
                color = look.sideFeather.copy(alpha = 0.38f),
                radius = 1.2f + (i % 2) * 0.5f,
                center = Offset(150f + i * 15f, 83f - (i % 2) * 4f),
            )
        }
    }

    // 心形面盘。
    val facePath = Path().apply {
        moveTo(180f, 183f)
        cubicTo(154f, 171f, 126f, 151f, 129f, 121f)
        cubicTo(132f, 96f, 161f, 93f, 180f, 118f)
        cubicTo(199f, 93f, 228f, 96f, 231f, 121f)
        cubicTo(234f, 151f, 206f, 171f, 180f, 183f)
        close()
    }
    drawPath(
        path = facePath,
        brush = Brush.verticalGradient(
            colors = listOf(look.faceLight, look.faceDark),
            startY = 95f,
            endY = 184f,
        ),
    )
    drawPath(
        path = facePath,
        color = look.faceLine.copy(alpha = 0.7f),
        style = Stroke(width = 1.5f),
    )

    val closed = asleep || isPet || isFeed

    // 眉羽。闭眼开心时收起，避免看起来像在生气。
    if (!closed) {
        drawPath(
            path = Path().apply {
                moveTo(138f, 112f)
                lineTo(150f, 106f)
                lineTo(144f, 119f)
                close()
            },
            color = look.brow.copy(alpha = 0.9f),
        )
        drawPath(
            path = Path().apply {
                moveTo(222f, 112f)
                lineTo(210f, 106f)
                lineTo(216f, 119f)
                close()
            },
            color = look.brow.copy(alpha = 0.9f),
        )
    }

    val pupils = if (isWake) 6.4f else if (isRefuse) 9.4f else 8.4f
    val irisRadius = if (look.snowy) 20.2f else 19f
    val pupilOffsetX = gazeX * 3.3f + if (isRefuse) sin(rp * PI * 8f).toFloat() * 1.6f else 0f
    val pupilOffsetY = gazeY * 2.9f

    listOf(158f, 202f).forEach { cx ->
        if (closed) {
            drawArc(
                color = Color(0xFF2B1A15),
                startAngle = 200f,
                sweepAngle = 140f,
                useCenter = false,
                topLeft = Offset(cx - 18f, 113f),
                size = Size(36f, 32f),
                style = Stroke(width = 3.1f, cap = StrokeCap.Round),
            )
        } else {
            drawCircle(color = look.eyeSocket, radius = 24f, center = Offset(cx, 130f))
            if (eyeOpen > 0.16f) {
                withTransform({
                    scale(1f, eyeOpen.coerceIn(0f, 1.24f), pivot = Offset(cx, 130f))
                }) {
                    drawCircle(
                        brush = Brush.radialGradient(
                            colors = listOf(Color(0xFFFFD66B), Color(0xFFF2AE35)),
                            center = Offset(cx - 4f, 124f),
                            radius = 22f,
                        ),
                        radius = irisRadius,
                        center = Offset(cx, 130f),
                    )
                    drawCircle(
                        color = Color(0xFF1A100E),
                        radius = pupils,
                        center = Offset(cx + pupilOffsetX, 130f + pupilOffsetY),
                    )
                    drawCircle(
                        color = Color(0xFFFFF8E0).copy(alpha = 0.95f),
                        radius = 2.7f,
                        center = Offset(cx + pupilOffsetX - 3.4f, 124.5f + pupilOffsetY),
                    )
                    drawCircle(
                        color = Color(0xFFFFF8E0).copy(alpha = 0.45f),
                        radius = 1.4f,
                        center = Offset(cx + pupilOffsetX + 3.2f, 134f + pupilOffsetY),
                    )
                }
            } else {
                drawArc(
                    color = Color(0xFF2B1A15),
                    startAngle = 200f,
                    sweepAngle = 140f,
                    useCenter = false,
                    topLeft = Offset(cx - 17f, 122f),
                    size = Size(34f, 18f),
                    style = Stroke(width = 2.6f, cap = StrokeCap.Round),
                )
            }
        }
    }

    // 喙：带一点钩的猫头鹰喙，比小猫的鼻子更醒目。
    val beakPath = Path().apply {
        moveTo(180f, 139f)
        cubicTo(188f, 144f, 193f, 151f, 190f, 157f)
        cubicTo(187f, 163f, 183f, 167f, 180f, 170f)
        cubicTo(177f, 166f, 172f, 162f, 169f, 156f)
        cubicTo(166f, 150f, 172f, 143f, 180f, 139f)
        close()
    }
    drawPath(
        path = beakPath,
        brush = Brush.verticalGradient(
            colors = listOf(look.beakLight, look.beakDark),
            startY = 139f,
            endY = 170f,
        ),
    )
    drawPath(
        path = beakPath,
        color = look.beakLine.copy(alpha = 0.85f),
        style = Stroke(width = 1.3f),
    )
    drawLine(
        color = look.beakLight.copy(alpha = 0.7f),
        start = Offset(180f, 143f),
        end = Offset(180f, 154f),
        strokeWidth = 1.2f,
        cap = StrokeCap.Round,
    )
    drawCircle(
        color = look.beakLine.copy(alpha = 0.55f),
        radius = 1.1f,
        center = Offset(175f, 149f),
    )
    drawCircle(
        color = look.beakLine.copy(alpha = 0.55f),
        radius = 1.1f,
        center = Offset(185f, 149f),
    )
    if (beakOpen > 0.02f) {
        val open = beakOpen * 8f
        drawPath(
            path = Path().apply {
                moveTo(171f, 157f)
                lineTo(189f, 157f)
                lineTo(180f, 168f + open)
                close()
            },
            color = look.beakDark,
        )
        drawCircle(
            color = look.beakLine,
            radius = 2.3f + beakOpen * 2.3f,
            center = Offset(180f, 160f + open * 0.35f),
        )
    }
    // 喙下的小绒毛。
    drawArc(
        color = look.faceLine.copy(alpha = 0.7f),
        startAngle = 20f,
        sweepAngle = 140f,
        useCenter = false,
        topLeft = Offset(166f, 159f),
        size = Size(28f, 16f),
        style = Stroke(width = 1.2f, cap = StrokeCap.Round),
    )
}

internal fun DrawScope.drawFoot(x: Float, look: OwlPalette) {
    val light = look.footLight
    val dark = look.footDark
    drawLine(
        color = light,
        start = Offset(x, 241f),
        end = Offset(x, 257f),
        strokeWidth = 4f,
        cap = StrokeCap.Round,
    )
    drawLine(
        color = light,
        start = Offset(x, 255f),
        end = Offset(x - 8f, 263f),
        strokeWidth = 3.2f,
        cap = StrokeCap.Round,
    )
    drawLine(
        color = light,
        start = Offset(x, 255f),
        end = Offset(x + 1f, 265f),
        strokeWidth = 3.2f,
        cap = StrokeCap.Round,
    )
    drawLine(
        color = light,
        start = Offset(x, 255f),
        end = Offset(x + 9f, 262f),
        strokeWidth = 3.2f,
        cap = StrokeCap.Round,
    )
    drawCircle(color = dark, radius = 1.2f, center = Offset(x - 8f, 263f))
    drawCircle(color = dark, radius = 1.2f, center = Offset(x + 1f, 265f))
    drawCircle(color = dark, radius = 1.2f, center = Offset(x + 9f, 262f))
}

internal fun DrawScope.drawLeaf(center: Offset, w: Float, h: Float, angle: Float) {
    rotate(angle, pivot = center) {
        drawOval(
            brush = Brush.linearGradient(
                colors = listOf(Color(0xFF4E7D5B), Color(0xFF2E5943)),
                start = Offset(center.x - w, center.y - h),
                end = Offset(center.x + w, center.y + h),
            ),
            topLeft = Offset(center.x - w, center.y - h),
            size = Size(w * 2f, h * 2f),
        )
    }
}

internal fun DrawScope.drawHappyHearts(rp: Float) {
    val alpha = sin(rp * PI).toFloat().coerceIn(0f, 1f)
    val rise = rp * 26f
    val originX = 180f
    val originY = 82f - rise
    drawHeart(Offset(originX - 42f, originY), 6.5f, Color(0xFFFF8FB3), alpha * 0.85f)
    drawHeart(Offset(originX + 44f, originY + 7f), 5.4f, Color(0xFFFFB5C9), alpha * 0.75f)
    drawHeart(Offset(originX - 9f, originY - 13f), 4.4f, Color(0xFFFFD1DD), alpha * 0.65f)
    drawHeart(Offset(originX + 17f, originY - 4f), 3.6f, Color(0xFFFF8FB3), alpha * 0.55f)
}

internal fun DrawScope.drawOwlCrumbs(rp: Float) {
    val alpha = sin(rp * PI).toFloat().coerceIn(0f, 1f)
    val fall = rp * 15f
    listOf(
        Triple(164f, 170f, 2.2f),
        Triple(196f, 174f, 1.7f),
        Triple(178f, 180f, 1.4f),
    ).forEachIndexed { i, (x, y, r) ->
        drawCircle(
            color = Color(0xFFFFCF72).copy(alpha = alpha * 0.8f),
            radius = r,
            center = Offset(x + if (i % 2 == 0) -2f else 2f, y + fall),
        )
    }
}

internal fun DrawScope.drawAnnoyedMark(rp: Float) {
    val alpha = sin(rp * PI).toFloat().coerceIn(0f, 1f)
    val c = Offset(251f, 92f)
    val color = Color(0xFFFF7A7A).copy(alpha = alpha)
    drawLine(color, Offset(c.x - 7f, c.y - 7f), Offset(c.x - 2f, c.y - 2f), 2.6f, StrokeCap.Round)
    drawLine(color, Offset(c.x + 7f, c.y - 7f), Offset(c.x + 2f, c.y - 2f), 2.6f, StrokeCap.Round)
    drawLine(color, Offset(c.x - 9f, c.y + 1f), Offset(c.x - 3f, c.y + 1f), 2.6f, StrokeCap.Round)
    drawLine(color, Offset(c.x + 9f, c.y + 1f), Offset(c.x + 3f, c.y + 1f), 2.6f, StrokeCap.Round)
}

internal fun DrawScope.drawWakeMark(rp: Float) {
    val alpha = sin(rp * PI).toFloat().coerceIn(0f, 1f)
    val top = Offset(251f, 66f)
    drawLine(
        color = Color(0xFFFFE08A).copy(alpha = alpha),
        start = top,
        end = Offset(251f, 82f),
        strokeWidth = 4f,
        cap = StrokeCap.Round,
    )
    drawCircle(
        color = Color(0xFFFFE08A).copy(alpha = alpha),
        radius = 2.8f,
        center = Offset(251f, 89f),
    )
}

internal fun DrawScope.drawHootWaves(progress: Float, asleep: Boolean) {
    if (asleep) return
    val alpha = sin(progress * PI).toFloat().coerceIn(0f, 1f)
    listOf(28f, 40f, 52f).forEachIndexed { index, radius ->
        drawArc(
            color = Color(0xFFFFE3A3).copy(alpha = alpha * (0.55f - index * 0.12f)),
            startAngle = -52f,
            sweepAngle = 104f,
            useCenter = false,
            topLeft = Offset(196f - radius, 156f - radius),
            size = Size(radius * 2f, radius * 2f),
            style = Stroke(width = 2.2f, cap = StrokeCap.Round),
        )
    }
}

private fun DrawScope.drawHeart(center: Offset, size: Float, color: Color, alpha: Float) {
    if (alpha <= 0.01f) return
    drawPath(
        path = Path().apply {
            moveTo(center.x, center.y + size * 0.55f)
            cubicTo(
                center.x - size * 1.1f,
                center.y - size * 0.25f,
                center.x - size * 0.55f,
                center.y - size,
                center.x,
                center.y - size * 0.35f,
            )
            cubicTo(
                center.x + size * 0.55f,
                center.y - size,
                center.x + size * 1.1f,
                center.y - size * 0.25f,
                center.x,
                center.y + size * 0.55f,
            )
            close()
        },
        color = color.copy(alpha = alpha),
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/OwlScene.kt`

> 林鸮场景：调色板、极光、雪景与栖息枝绘制。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

private data class Star(val x: Float, val y: Float, val r: Float, val phase: Float)

private val stars = listOf(
    Star(28f, 36f, 1.3f, 0.2f),
    Star(62f, 76f, 1.0f, 1.7f),
    Star(96f, 28f, 1.6f, 2.6f),
    Star(124f, 58f, 0.9f, 3.9f),
    Star(154f, 24f, 1.2f, 0.8f),
    Star(192f, 48f, 1.0f, 2.1f),
    Star(228f, 22f, 1.4f, 4.2f),
    Star(258f, 66f, 1.0f, 5.1f),
    Star(284f, 108f, 1.2f, 1.2f),
    Star(338f, 92f, 1.0f, 3.1f),
    Star(318f, 132f, 1.4f, 5.6f),
    Star(44f, 122f, 1.1f, 4.7f),
    Star(12f, 92f, 0.8f, 2.9f),
    Star(72f, 152f, 0.9f, 5.9f),
    Star(344f, 166f, 0.8f, 0.5f),
)

private data class Snowflake(
    val x: Float,
    val y: Float,
    val r: Float,
    val speed: Float,
    val phase: Float,
)

private val snowflakes = listOf(
    Snowflake(24f, 8f, 1.1f, 0.9f, 0.05f),
    Snowflake(58f, 92f, 0.8f, 1.1f, 0.31f),
    Snowflake(88f, 34f, 1.3f, 0.8f, 0.57f),
    Snowflake(118f, 142f, 0.9f, 1.2f, 0.12f),
    Snowflake(148f, 68f, 1.0f, 1.0f, 0.83f),
    Snowflake(182f, 18f, 0.8f, 1.3f, 0.44f),
    Snowflake(212f, 116f, 1.2f, 0.9f, 0.66f),
    Snowflake(244f, 52f, 0.9f, 1.1f, 0.25f),
    Snowflake(276f, 154f, 1.1f, 1.0f, 0.73f),
    Snowflake(306f, 88f, 0.8f, 1.2f, 0.39f),
    Snowflake(334f, 28f, 1.2f, 0.8f, 0.92f),
    Snowflake(352f, 128f, 0.9f, 1.1f, 0.16f),
)

internal data class OwlPalette(
    val snowy: Boolean,
    val skyTop: Color,
    val skyMid: Color,
    val skyBottom: Color,
    val mountainTop: Color,
    val mountainMid: Color,
    val mountainBottom: Color,
    val branchDark: Color,
    val branchLight: Color,
    val branchHighlight: Color,
    val bodyLight: Color,
    val bodyMid: Color,
    val bodyDark: Color,
    val outline: Color,
    val wingLight: Color,
    val wingDark: Color,
    val bellyLight: Color,
    val bellyDark: Color,
    val bellyLine: Color,
    val faceLight: Color,
    val faceDark: Color,
    val faceLine: Color,
    val tuftLight: Color,
    val tuftDark: Color,
    val tuftInner: Color,
    val beakLight: Color,
    val beakDark: Color,
    val beakLine: Color,
    val footLight: Color,
    val footDark: Color,
    val brow: Color,
    val sideFeather: Color,
    val eyeSocket: Color,
    val moonLight: Color,
    val moonDark: Color,
)

private val brownOwlPalette = OwlPalette(
    snowy = false,
    skyTop = Color(0xFF07132B),
    skyMid = Color(0xFF111F42),
    skyBottom = Color(0xFF28234D),
    mountainTop = Color(0xFF3E4A78),
    mountainMid = Color(0xFF404A76),
    mountainBottom = Color(0xFF1B1A39),
    branchDark = Color(0xFF231A1B),
    branchLight = Color(0xFF6B4B3C),
    branchHighlight = Color(0xFF8A6752),
    bodyLight = Color(0xFF8A6246),
    bodyMid = Color(0xFF6A4735),
    bodyDark = Color(0xFF513528),
    outline = Color(0xFF2A1914),
    wingLight = Color(0xFF6F4C38),
    wingDark = Color(0xFF4A3126),
    bellyLight = Color(0xFFF2DFBE),
    bellyDark = Color(0xFFDFC49E),
    bellyLine = Color(0xFFC39A6C),
    faceLight = Color(0xFFE6C69A),
    faceDark = Color(0xFFD1A87B),
    faceLine = Color(0xFFB68B60),
    tuftLight = Color(0xFF4A3125),
    tuftDark = Color(0xFF6F4B36),
    tuftInner = Color(0xFFC09267),
    beakLight = Color(0xFFFFCA65),
    beakDark = Color(0xFFE8962F),
    beakLine = Color(0xFF8C4E1C),
    footLight = Color(0xFFE09A42),
    footDark = Color(0xFF9B5B1E),
    brow = Color(0xFF4C3023),
    sideFeather = Color(0xFF3C281F),
    eyeSocket = Color(0xFF2A1812),
    moonLight = Color(0xFFFFF0BE),
    moonDark = Color(0xFFFFD77E),
)

private val snowyOwlPalette = OwlPalette(
    snowy = true,
    skyTop = Color(0xFF04101F),
    skyMid = Color(0xFF0A2940),
    skyBottom = Color(0xFF1F4E5E),
    mountainTop = Color(0xFF456B79),
    mountainMid = Color(0xFF315564),
    mountainBottom = Color(0xFF0E2A3B),
    branchDark = Color(0xFF1A262C),
    branchLight = Color(0xFF5D6E70),
    branchHighlight = Color(0xFFEAF4F5),
    bodyLight = Color(0xFFFBF8EF),
    bodyMid = Color(0xFFEFEBDF),
    bodyDark = Color(0xFFD9D4C8),
    outline = Color(0xFF8D8980),
    wingLight = Color(0xFFF3F0E7),
    wingDark = Color(0xFFDDD8CC),
    bellyLight = Color(0xFFFFFEF8),
    bellyDark = Color(0xFFF2EEE2),
    bellyLine = Color(0xFFA8A49A),
    faceLight = Color(0xFFFFFFFF),
    faceDark = Color(0xFFF4F0E4),
    faceLine = Color(0xFFC9C4B8),
    tuftLight = Color(0xFFE8E4D8),
    tuftDark = Color(0xFFD3CEC2),
    tuftInner = Color(0xFFFFFFFF),
    beakLight = Color(0xFF5A5B60),
    beakDark = Color(0xFF2A2B2F),
    beakLine = Color(0xFF141519),
    footLight = Color(0xFFE7E1D5),
    footDark = Color(0xFF303136),
    brow = Color(0xFF928E85),
    sideFeather = Color(0xFFB9B5AA),
    eyeSocket = Color(0xFF8D8980),
    moonLight = Color(0xFFF2FAFF),
    moonDark = Color(0xFFCFE9F7),
)

internal fun owlPalette(species: OwlSpecies): OwlPalette =
    if (species == OwlSpecies.SNOWY) snowyOwlPalette else brownOwlPalette

/** 按系统时间替换天空 / 远山 / 光源颜色，身体羽色保持不变。 */
internal fun OwlPalette.withPhase(phase: PetDayPhase): OwlPalette = when (phase) {
    PetDayPhase.NIGHT -> this
    PetDayPhase.DAWN -> copy(
        skyTop = Color(0xFF3B3566),
        skyMid = Color(0xFF7C6A9C),
        skyBottom = Color(0xFFF0B48C),
        mountainTop = Color(0xFF7A739C),
        mountainMid = Color(0xFF645A80),
        mountainBottom = Color(0xFF342C4C),
        moonLight = Color(0xFFFFE8BE),
        moonDark = Color(0xFFFFC27A),
    )
    PetDayPhase.DAY -> copy(
        skyTop = Color(0xFF4E88C6),
        skyMid = Color(0xFF98C6E8),
        skyBottom = Color(0xFFE2EFF7),
        mountainTop = Color(0xFF8AA8BC),
        mountainMid = Color(0xFF708CA2),
        mountainBottom = Color(0xFF466074),
        moonLight = Color(0xFFFFF6D8),
        moonDark = Color(0xFFFFD98A),
    )
    PetDayPhase.DUSK -> copy(
        skyTop = Color(0xFF2C2A56),
        skyMid = Color(0xFF725078),
        skyBottom = Color(0xFFE08A6A),
        mountainTop = Color(0xFF6E607E),
        mountainMid = Color(0xFF5A4A66),
        mountainBottom = Color(0xFF2E2440),
        moonLight = Color(0xFFFFD9A0),
        moonDark = Color(0xFFFFA85C),
    )
}

internal fun DrawScope.drawOwlScene(
    phase: PetDayPhase,
    breath: Float,
    sway: Float,
    twinkle: Float,
    snowDrift: Float,
    blink: Float,
    gazeX: Float,
    gazeY: Float,
    fly: Float,
    preen: Float,
    shuffle: Float,
    reaction: PetReaction,
    reactionProgress: Float,
    hootProgress: Float,
    asleep: Boolean,
    sleepy: Boolean,
    look: OwlPalette,
    backdrop: Boolean,
) {
    val living = if (asleep) 0.3f else 1f
    val flying = fly > 0f && fly < 1f
    val flyX = sin(fly * PI).toFloat() * 80f
    val flyY = -sin(fly * PI).toFloat() * 60f + sin(fly * PI * 6).toFloat() * 2.5f
    val preenBend = if (preen > 0f) sin(preen * PI * 3).toFloat().coerceIn(0f, 1f) * 11f else 0f
    val preenTilt = if (preen > 0f) sin(preen * PI * 3).toFloat().coerceIn(-1f, 1f) * 7f else 0f
    val shuffleBob = if (shuffle > 0f) -sin(shuffle * PI).toFloat() * 7f else 0f
    val rp = reactionProgress
    val active = reaction != PetReaction.NONE && rp > 0f
    val isFeed = active && reaction == PetReaction.FEED
    val isPet = active && reaction == PetReaction.PET
    val isRefuse = active && reaction == PetReaction.REFUSE
    val isWake = active && reaction == PetReaction.WAKE
    val isHoot = (active && reaction == PetReaction.HOOT) || hootProgress > 0f
    val hoot = if (active && reaction == PetReaction.HOOT) rp else hootProgress

    if (backdrop) {
    drawRect(
        brush = Brush.verticalGradient(
            colors = listOf(
                look.skyTop,
                look.skyMid,
                look.skyBottom,
            ),
        ),
    )
    if (look.snowy && (phase == PetDayPhase.NIGHT || phase == PetDayPhase.DUSK)) {
        drawAurora(twinkle, sway)
    }
    if (look.snowy) {
        drawSnowfall(snowDrift)
    }

    // 天空：夜晚月亮与星、黄昏落日、白天太阳。
    if (phase == PetDayPhase.NIGHT || phase == PetDayPhase.DUSK || phase == PetDayPhase.DAWN) {
        val starAlpha = when (phase) {
            PetDayPhase.NIGHT -> 1f
            else -> 0.45f
        }
        stars.forEachIndexed { index, star ->
            val wave = (sin((twinkle * 2.0 * PI + star.phase + index * 0.13)).toFloat() + 1f) / 2f
            drawCircle(
                color = Color(0xFFFFF4CE).copy(alpha = (0.22f + wave * 0.58f) * starAlpha),
                radius = star.r * (0.8f + wave * 0.45f),
                center = Offset(star.x, star.y),
            )
        }
    }
    if (phase == PetDayPhase.NIGHT) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    look.moonLight.copy(alpha = 0.27f),
                    look.moonLight.copy(alpha = 0f),
                ),
                center = Offset(306f, 58f),
                radius = 62f,
            ),
            radius = 62f,
            center = Offset(306f, 58f),
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(look.moonLight, look.moonDark),
                center = Offset(301f, 53f),
                radius = 38f,
            ),
            radius = 31f,
            center = Offset(306f, 58f),
        )
        drawCircle(
            color = look.moonDark.copy(alpha = 0.35f),
            radius = 5f,
            center = Offset(316f, 48f),
        )
        drawCircle(
            color = look.moonDark.copy(alpha = 0.24f),
            radius = 3.4f,
            center = Offset(297f, 70f),
        )
    } else {
        val sunCenter = if (phase == PetDayPhase.DUSK) Offset(300f, 148f) else Offset(306f, 58f)
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    Color(0x55FFD27A),
                    Color(0x00FFD27A),
                ),
                center = sunCenter,
                radius = 72f,
            ),
            radius = 72f,
            center = sunCenter,
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0xFFFFF3C4), Color(0xFFFFC65A)),
                center = sunCenter,
                radius = 42f,
            ),
            radius = 30f,
            center = sunCenter,
        )
    }

    drawPath(
        path = Path().apply {
            moveTo(0f, 196f)
            cubicTo(72f, 172f, 116f, 204f, 182f, 194f)
            cubicTo(244f, 184f, 296f, 205f, 360f, 190f)
            lineTo(360f, 300f)
            lineTo(0f, 300f)
            close()
        },
        brush = Brush.verticalGradient(
            colors = listOf(
                look.mountainTop.copy(alpha = 0.13f),
                look.mountainMid.copy(alpha = 0.40f),
                look.mountainBottom.copy(alpha = 0.67f),
            ),
            startY = 180f,
            endY = 300f,
        ),
    )
    }

    if (backdrop) {
    // 树枝。
    drawPath(
        path = Path().apply {
            moveTo(-6f, 258f)
            cubicTo(68f, 248f, 114f, 267f, 186f, 259f)
            cubicTo(248f, 252f, 304f, 267f, 366f, 250f)
        },
        color = look.branchDark,
        style = Stroke(width = 17f, cap = StrokeCap.Round),
    )
    drawPath(
        path = Path().apply {
            moveTo(-6f, 255f)
            cubicTo(68f, 245f, 114f, 264f, 186f, 256f)
            cubicTo(248f, 249f, 304f, 264f, 366f, 247f)
        },
        brush = Brush.verticalGradient(
            colors = listOf(look.branchLight, look.branchDark),
            startY = 244f,
            endY = 268f,
        ),
        style = Stroke(width = 10f, cap = StrokeCap.Round),
    )
    drawLine(
        color = look.branchHighlight.copy(alpha = 0.55f),
        start = Offset(24f, 251f),
        end = Offset(114f, 257f),
        strokeWidth = 1.6f,
        cap = StrokeCap.Round,
    )
    if (look.snowy) {
        // 雪鸮场景：树枝上积了一层雪。
        drawPath(
            path = Path().apply {
                moveTo(-6f, 250f)
                cubicTo(68f, 240f, 114f, 259f, 186f, 251f)
                cubicTo(248f, 244f, 304f, 259f, 366f, 242f)
            },
            color = look.branchHighlight.copy(alpha = 0.9f),
            style = Stroke(width = 3.4f, cap = StrokeCap.Round),
        )
        drawOval(
            color = look.branchHighlight.copy(alpha = 0.9f),
            topLeft = Offset(96f, 244f),
            size = Size(34f, 7f),
        )
        drawOval(
            color = look.branchHighlight.copy(alpha = 0.75f),
            topLeft = Offset(278f, 247f),
            size = Size(26f, 6f),
        )
    }
    // 小枝与叶子。
    drawLine(
        color = look.branchLight,
        start = Offset(300f, 254f),
        end = Offset(324f, 230f),
        strokeWidth = 4.5f,
        cap = StrokeCap.Round,
    )
    if (look.snowy) {
        drawPath(
            path = Path().apply {
                moveTo(300f, 252f)
                lineTo(322f, 229f)
            },
            color = look.branchHighlight.copy(alpha = 0.85f),
            style = Stroke(width = 2.2f, cap = StrokeCap.Round),
        )
        drawCircle(
            color = look.branchHighlight.copy(alpha = 0.9f),
            radius = 3.4f,
            center = Offset(323f, 229f),
        )
    } else {
        drawLeaf(Offset(323f, 229f), 14f, 6f, -32f)
        drawLeaf(Offset(332f, 238f), 11f, 5f, 18f)
        drawLeaf(Offset(42f, 252f), 10f, 4.5f, 20f)
    }

    // 树影。
    drawOval(
        color = Color.Black.copy(alpha = 0.24f),
        topLeft = Offset(118f, 245f),
        size = Size(126f, 14f),
    )
    } else {
        drawShortPerch(look)
    }

    val bodyScale = 1f + breath * 0.012f * living + if (isPet) sin(rp * PI).toFloat() * 0.008f else 0f
    val headTilt = (sway - 0.5f) * 6.5f * living +
        if (isPet) sin(rp * PI).toFloat() * 8f else 0f +
        preenTilt
    val headShake = if (isRefuse) sin(rp * PI * 8f).toFloat() * 5f * (1f - rp) else 0f
    val headBob = -breath * 2.1f * living + if (asleep) 6f else 0f +
        if (isFeed) sin(rp * PI * 6f).toFloat() * 1.1f else 0f +
        preenBend
    val eyeOpen = when {
        asleep -> 0f
        isPet || isFeed -> 0f
        isWake -> 1.18f
        isRefuse -> 0.54f
        preenBend > 1f -> blink * 0.42f
        sleepy && !active -> min(blink, 0.72f)
        else -> blink
    }
    val wingFlap = when {
        flying -> sin(fly * PI * 10).toFloat() * 24f
        isRefuse -> sin(rp * PI * 8f).toFloat() * 13f * (1f - rp)
        isPet -> sin(rp * PI).toFloat() * 7f
        asleep -> 0f
        else -> sin(breath * PI).toFloat() * 1.8f
    }
    val beakOpen = when {
        isFeed -> (abs(sin(rp * PI * 5f)) * 0.75f).toFloat()
        isHoot -> sin(hoot * PI).toFloat()
        isWake -> 0.35f * sin(rp * PI).toFloat()
        preenBend > 0f -> (preenBend / 11f) * 0.45f
        else -> 0f
    }

    // 尾羽、身体、脚爪与头整体跟随飞行 / 小跳平移，栖木和影子留在原地。
    withTransform({
        translate(left = flyX, top = flyY + shuffleBob)
    }) {
    // 尾羽。
    drawPath(
        path = Path().apply {
            moveTo(164f, 225f)
            lineTo(148f, 277f)
            lineTo(172f, 260f)
            lineTo(182f, 281f)
            lineTo(194f, 257f)
            lineTo(199f, 226f)
            close()
        },
        brush = Brush.verticalGradient(
            colors = listOf(look.wingDark, look.outline),
            startY = 220f,
            endY = 282f,
        ),
    )
    drawLine(
        color = look.outline.copy(alpha = 0.6f),
        start = Offset(180f, 238f),
        end = Offset(180f, 274f),
        strokeWidth = 1.4f,
    )

    withTransform({
        scale(bodyScale, bodyScale, pivot = Offset(180f, 254f))
    }) {
        // 翅膀。
        rotate(-8f - wingFlap, pivot = Offset(136f, 190f)) {
            drawWing(left = true, look = look)
        }
        rotate(8f + wingFlap, pivot = Offset(224f, 190f)) {
            drawWing(left = false, look = look)
        }

        // 身体。
        drawOval(
            brush = Brush.verticalGradient(
                colors = listOf(look.bodyLight, look.bodyMid, look.bodyDark),
                startY = 130f,
                endY = 258f,
            ),
            topLeft = Offset(121f, 126f),
            size = Size(118f, 128f),
        )
        drawOval(
            color = look.outline.copy(alpha = 0.72f),
            topLeft = Offset(121f, 126f),
            size = Size(118f, 128f),
            style = Stroke(width = 2.4f),
        )
        // 胸腹。
        drawOval(
            brush = Brush.verticalGradient(
                colors = listOf(look.bellyLight, look.bellyDark),
                startY = 162f,
                endY = 250f,
            ),
            topLeft = Offset(146f, 160f),
            size = Size(68f, 88f),
        )
        drawOval(
            color = look.bellyLine.copy(alpha = 0.55f),
            topLeft = Offset(146f, 160f),
            size = Size(68f, 88f),
            style = Stroke(width = 1.4f),
        )
        // 胸羽的弧形纹理。
        for (row in 0..3) {
            val y = 178f + row * 15f
            val offset = if (row % 2 == 0) 0f else 9f
            for (col in 0..2) {
                val x = 158f + col * 18f + offset
                drawArc(
                    color = look.bellyLine.copy(alpha = 0.7f),
                    startAngle = 18f,
                    sweepAngle = 144f,
                    useCenter = false,
                    topLeft = Offset(x - 6f, y - 4f),
                    size = Size(12f, 10f),
                    style = Stroke(width = 1.4f, cap = StrokeCap.Round),
                )
            }
        }
        // 身体侧面的小羽毛。
        for (i in 0..2) {
            drawLine(
                color = look.sideFeather.copy(alpha = 0.5f),
                start = Offset(132f + i * 3f, 174f + i * 14f),
                end = Offset(142f + i * 3f, 183f + i * 14f),
                strokeWidth = 1.3f,
                cap = StrokeCap.Round,
            )
            drawLine(
                color = look.sideFeather.copy(alpha = 0.5f),
                start = Offset(228f - i * 3f, 174f + i * 14f),
                end = Offset(218f - i * 3f, 183f + i * 14f),
                strokeWidth = 1.3f,
                cap = StrokeCap.Round,
            )
        }
        if (look.snowy) {
            // 雪鸮的灰色横斑。
            for (i in 0..3) {
                drawArc(
                    color = look.sideFeather.copy(alpha = 0.38f),
                    startAngle = 12f,
                    sweepAngle = 156f,
                    useCenter = false,
                    topLeft = Offset(146f + i * 12f, 216f),
                    size = Size(14f, 8f),
                    style = Stroke(width = 1.2f, cap = StrokeCap.Round),
                )
            }
        }
    }

    // 脚爪抓住树枝。
    drawFoot(164f, look)
    drawFoot(196f, look)

    withTransform({
        translate(left = 0f, top = headBob)
        rotate(headTilt + headShake, pivot = Offset(180f, 186f))
    }) {
        drawOwlHead(
            eyeOpen = eyeOpen,
            gazeX = gazeX,
            gazeY = gazeY,
            beakOpen = beakOpen,
            asleep = asleep,
            isPet = isPet,
            isFeed = isFeed,
            isRefuse = isRefuse,
            isWake = isWake,
            rp = rp,
            sway = sway,
            living = living,
            look = look,
        )
    }
    }

    if (isPet || isFeed) drawHappyHearts(rp)
    if (isFeed) drawOwlCrumbs(rp)
    if (isRefuse) drawAnnoyedMark(rp)
    if (isWake) drawWakeMark(rp)
    if (isHoot) drawHootWaves(hoot, asleep)
}

/** 透明场景里给猫头鹰一小截栖木，避免整只鸟悬空。 */
private fun DrawScope.drawShortPerch(look: OwlPalette) {
    drawOval(
        color = Color.Black.copy(alpha = 0.22f),
        topLeft = Offset(94f, 264f),
        size = Size(172f, 16f),
    )
    drawRoundRect(
        color = look.branchDark,
        topLeft = Offset(84f, 246f),
        size = Size(192f, 23f),
        cornerRadius = CornerRadius(11f, 11f),
    )
    drawRoundRect(
        color = look.branchLight,
        topLeft = Offset(84f, 246f),
        size = Size(192f, 11f),
        cornerRadius = CornerRadius(8f, 8f),
    )
    drawLine(
        color = look.branchHighlight.copy(alpha = 0.55f),
        start = Offset(104f, 250f),
        end = Offset(246f, 250f),
        strokeWidth = 1.6f,
        cap = StrokeCap.Round,
    )
    drawLeaf(Offset(260f, 244f), 13f, 5.5f, -28f)
}

private fun DrawScope.drawAurora(twinkle: Float, sway: Float) {
    val shift = (sway - 0.5f) * 9f
    val pulse = 0.65f + sin(twinkle * 2.0 * PI).toFloat() * 0.12f
    for (band in 0..2) {
        val y = 42f + band * 19f + shift
        val path = Path().apply {
            moveTo(-30f, y + 24f)
            cubicTo(52f, y - 20f, 122f, y + 10f, 190f, y - 13f)
            cubicTo(252f, y - 32f, 310f, y - 2f, 390f, y - 26f)
            lineTo(390f, y + 8f)
            cubicTo(312f, y + 24f, 250f, y + 14f, 190f, y + 28f)
            cubicTo(120f, y + 44f, 52f, y + 20f, -30f, y + 42f)
            close()
        }
        drawPath(
            path = path,
            brush = Brush.linearGradient(
                colors = listOf(
                    Color(0x0022D3A0),
                    Color(0x5522D3A0),
                    Color(0x402F6FE0),
                    Color(0x002F6FE0),
                ),
                start = Offset(0f, y - 24f),
                end = Offset(360f, y + 36f),
            ),
            alpha = pulse,
        )
    }
    // 极光边缘的细亮线。
    drawPath(
        path = Path().apply {
            moveTo(-20f, 82f + shift)
            cubicTo(80f, 42f + shift, 150f, 74f + shift, 220f, 38f + shift)
            cubicTo(280f, 8f + shift, 330f, 34f + shift, 380f, 18f + shift)
        },
        color = Color(0x3345E8C4),
        style = Stroke(width = 2f, cap = StrokeCap.Round),
    )
}

private fun DrawScope.drawSnowfall(progress: Float) {
    snowflakes.forEachIndexed { index, flake ->
        val t = (progress * flake.speed + flake.phase) % 1f
        val y = (flake.y + t * 300f) % 300f
        val x = flake.x + sin((t * 2.0 * PI + index).toFloat()) * 7f
        val alpha = (0.24f + sin(t * PI).toFloat() * 0.55f).coerceIn(0.12f, 0.8f)
        drawCircle(
            color = Color(0xFFEFFBFF).copy(alpha = alpha),
            radius = flake.r,
            center = Offset(x, y),
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/PetLive2D.kt`

> 猫 / 犬 / 仓鼠伙伴外壳与睡眠动效入口。

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

/** 同伴宠物（墨猫 / 田园犬 / 仓鼠）的待机动作，符合各自习性。 */
private enum class CompanionIdleAction { IDLE, WALK, GROOM, HOP }

/**
 * 宠物渲染入口：猫头鹰沿用 [OwlLive2D]，墨猫 / 田园犬 / 仓鼠走 [CompanionLive2D]。
 * 两者共享同一套呼吸、眨眼、视线、待机小动作和喂食 / 摸摸反馈。
 *
 * @param backdrop 为 false 时只画宠物和它的影子，不画自带天空 / 地面，便于嵌进连续场景。
 * @param focus 宠物主体放大倍率。
 */
@Composable
fun PetLive2D(
    state: PetState,
    reaction: PetReaction,
    reactionToken: Int,
    phase: PetDayPhase = PetDayPhase.NIGHT,
    modifier: Modifier = Modifier,
    contentDescription: String = "宠物，点一下摸摸它",
    onTap: () -> Unit = {},
    backdrop: Boolean = true,
    focus: Float = 1f,
) {
    if (state.species.isOwl) {
        OwlLive2D(
            state = state,
            reaction = reaction,
            reactionToken = reactionToken,
            phase = phase,
            modifier = modifier,
            contentDescription = contentDescription,
            onTap = onTap,
            backdrop = backdrop,
            focus = focus,
        )
    } else {
        CompanionLive2D(
            state = state,
            reaction = reaction,
            reactionToken = reactionToken,
            phase = phase,
            modifier = modifier,
            contentDescription = contentDescription,
            onTap = onTap,
            backdrop = backdrop,
            focus = focus,
        )
    }
}

@Composable
private fun CompanionLive2D(
    state: PetState,
    reaction: PetReaction,
    reactionToken: Int,
    phase: PetDayPhase,
    modifier: Modifier = Modifier,
    contentDescription: String,
    onTap: () -> Unit,
    backdrop: Boolean,
    focus: Float,
) {
    val haptic = LocalHapticFeedback.current
    val scope = rememberCoroutineScope()
    val idle = rememberInfiniteTransition(label = "companion-idle")
    val breath by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2_600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "breath",
    )
    val sway by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(5_800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "sway",
    )
    val tail by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1_500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "tail",
    )
    val twinkle by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(3_600, easing = LinearOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "twinkle",
    )

    val blink = remember { Animatable(1f) }
    LaunchedEffect(state.asleep) {
        if (state.asleep) {
            blink.snapTo(0f)
            return@LaunchedEffect
        }
        blink.snapTo(1f)
        while (true) {
            delay(Random.nextLong(2_600L, 5_800L))
            blink.animateTo(0.06f, tween(80))
            blink.animateTo(1f, tween(140))
            if (Random.nextInt(100) < 20) {
                delay(130)
                blink.animateTo(0.06f, tween(70))
                blink.animateTo(1f, tween(130))
            }
        }
    }

    val gazeX = remember { Animatable(0f) }
    val gazeY = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        while (true) {
            delay(Random.nextLong(3_000L, 6_500L))
            gazeX.animateTo(Random.nextFloat() * 1.2f - 0.6f, tween(800))
            gazeY.animateTo(Random.nextFloat() * 0.6f - 0.3f, tween(800))
        }
    }

    // 待机小动作：偶尔抖一下耳朵。
    val earTwitch = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        while (true) {
            delay(Random.nextLong(3_500L, 7_500L))
            earTwitch.animateTo(1f, tween(90))
            earTwitch.animateTo(0f, tween(170))
        }
    }

    // 符合动物习性的待机动作：走动、打理毛发、轻轻蹦一下。
    // 由一个状态机驱动，动作之间留一段普通待机（呼吸 / 摇摆 / 眨眼）。
    var idleAction by remember { mutableStateOf(CompanionIdleAction.IDLE) }
    val actionProgress = remember { Animatable(0f) }
    LaunchedEffect(state.asleep) {
        if (state.asleep) {
            idleAction = CompanionIdleAction.IDLE
            actionProgress.snapTo(0f)
            return@LaunchedEffect
        }
        while (true) {
            delay(Random.nextLong(5_500L, 11_000L))
            idleAction = listOf(
                CompanionIdleAction.WALK,
                CompanionIdleAction.GROOM,
                CompanionIdleAction.HOP,
            ).random()
            actionProgress.snapTo(0f)
            val duration = when (idleAction) {
                CompanionIdleAction.WALK -> 5_400
                CompanionIdleAction.GROOM -> 3_600
                CompanionIdleAction.HOP -> 520
                CompanionIdleAction.IDLE -> 1_000
            }
            actionProgress.animateTo(1f, tween(duration, easing = FastOutSlowInEasing))
            actionProgress.snapTo(0f)
            idleAction = CompanionIdleAction.IDLE
        }
    }

    val actionValue = actionProgress.value
    val walkOffsetX = if (idleAction == CompanionIdleAction.WALK) {
        sin(actionValue * PI).toFloat() * 72f
    } else {
        0f
    }
    val step = if (idleAction == CompanionIdleAction.WALK) actionValue * 12f else 0f
    val walkBob = if (idleAction == CompanionIdleAction.WALK) {
        abs(sin(step * PI).toFloat()) * 4f
    } else {
        0f
    }
    val groom = if (idleAction == CompanionIdleAction.GROOM) actionValue else 0f
    val hop = if (idleAction == CompanionIdleAction.HOP) actionValue else 0f

    var activeReaction by remember { mutableStateOf(PetReaction.NONE) }
    val reactionProgress = remember { Animatable(0f) }
    var consumedReactionToken by remember { mutableIntStateOf(reactionToken) }
    LaunchedEffect(reactionToken) {
        if (reactionToken <= consumedReactionToken) return@LaunchedEffect
        consumedReactionToken = reactionToken
        activeReaction = reaction
        reactionProgress.snapTo(0f)
        reactionProgress.animateTo(1f, tween(1_300, easing = LinearOutSlowInEasing))
        reactionProgress.snapTo(0f)
        activeReaction = PetReaction.NONE
    }

    Box(
        modifier = modifier.semantics {
            this.contentDescription = contentDescription
        },
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTapGestures { offset ->
                        val nx = (offset.x / size.width - 0.5f) * 2f
                        val ny = (offset.y / size.height - 0.5f) * 2f
                        scope.launch {
                            gazeX.snapTo(nx.coerceIn(-1f, 1f))
                            gazeY.snapTo(ny.coerceIn(-0.7f, 0.7f))
                            delay(850)
                            gazeX.animateTo(0f, tween(700))
                            gazeY.animateTo(0f, tween(700))
                        }
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onTap()
                    }
                },
        ) {
            val sceneScale = min(size.width / 360f, size.height / 300f)
            withTransform({
                translate(
                    left = (size.width - 360f * sceneScale) / 2f,
                    top = (size.height - 300f * sceneScale) / 2f,
                )
                scale(sceneScale, sceneScale, pivot = Offset.Zero)
                scale(focus, focus, pivot = Offset(180f, 180f))
            }) {
                drawCompanionScene(
                    species = state.species,
                    phase = phase,
                    breath = breath,
                    sway = sway,
                    tail = tail,
                    twinkle = twinkle,
                    blink = blink.value,
                    gazeX = gazeX.value,
                    gazeY = gazeY.value,
                    earTwitch = earTwitch.value,
                    hop = hop,
                    walkOffsetX = walkOffsetX,
                    walkBob = walkBob,
                    step = step,
                    groom = groom,
                    reaction = activeReaction,
                    reactionProgress = reactionProgress.value,
                    asleep = state.asleep,
                    sleepy = state.energy <= 26,
                    backdrop = backdrop,
                )
            }
        }
        if (state.asleep) {
            CompanionZzz()
        }
    }
}

@Composable
private fun CompanionZzz() {
    val transition = rememberInfiniteTransition(label = "companion-zzz")
    val float by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2_200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "zzz",
    )
    val color = Color(0xFFFFE3A3)
    Box(Modifier.fillMaxSize()) {
        Text(
            text = "z",
            color = color.copy(alpha = 0.26f + float * 0.28f),
            fontSize = 14.sp,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 92.dp, end = 96.dp)
                .graphicsLayer { translationY = -float * 5f },
        )
        Text(
            text = "Z",
            color = color.copy(alpha = 0.36f + float * 0.34f),
            fontSize = 18.sp,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 70.dp, end = 68.dp)
                .graphicsLayer { translationY = -float * 9f },
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/ReadAloudButton.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import android.widget.Toast
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LocalContentColor
import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.util.TextReader
import com.shineleong.toughmind.util.TtsMode
import com.shineleong.toughmind.util.TtsPreset

val LocalTextReader = staticCompositionLocalOf<TextReader?> { null }
val LocalTtsPreset = staticCompositionLocalOf { TtsPreset.AUTO }
val LocalTtsMode = staticCompositionLocalOf { TtsMode.OFFLINE }
val LocalTtsRate = staticCompositionLocalOf { 1f }

/** 文本旁的小喇叭：按设置里的音色 / 方言朗读。 */
@Composable
fun ReadAloudButton(
    text: String,
    modifier: Modifier = Modifier,
    tint: Color = LocalContentColor.current,
) {
    val reader = LocalTextReader.current
    val preset = LocalTtsPreset.current
    val mode = LocalTtsMode.current
    val rate = LocalTtsRate.current
    val context = LocalContext.current
    val missingMessage = tr(
        "当前系统没有该方言音色，请先在系统设置中安装。",
        "This dialect voice isn't installed. Please add it in system settings.",
    )
    IconButton(
        onClick = {
            if (reader == null || !reader.speak(text, preset, mode, rate)) {
                Toast.makeText(context, missingMessage, Toast.LENGTH_SHORT).show()
            }
        },
        modifier = modifier.size(34.dp),
    ) {
        Icon(
            Icons.AutoMirrored.Filled.VolumeUp,
            contentDescription = "朗读",
            tint = tint,
            modifier = Modifier.size(18.dp),
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/component/StatusPicker.kt`

````kotlin
package com.shineleong.toughmind.ui.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shineleong.toughmind.ui.theme.AppDimens

data class SelfStatusOption(
    val emoji: String,
    val label: String,
    val message: String,
)

val SelfStatusOptions = listOf(
    SelfStatusOption("🙂", "平静", "今天也要好好生活"),
    SelfStatusOption("😊", "开心", "今天心情不错"),
    SelfStatusOption("🥰", "想你", "有点想你了"),
    SelfStatusOption("😮‍💨", "累了", "忙完想歇一会儿"),
    SelfStatusOption("😴", "困了", "准备早点休息"),
    SelfStatusOption("🧑‍💻", "在忙", "正在处理事情，晚点回"),
    SelfStatusOption("🍚", "吃饭", "先去吃点东西"),
    SelfStatusOption("🚗", "在路上", "正在路上，注意安全"),
)

/** 状态词：优先按 emoji 取内置状态，自定义 emoji 时退回留言。 */
fun selfStatusLabel(emoji: String, fallback: String): String =
    SelfStatusOptions.firstOrNull { it.emoji == emoji }?.label
        ?: fallback.ifBlank { "平静" }

/** 账号下面的一行状态：emoji + 状态词，整行可点，点一下切换状态。 */
@Composable
fun SelfStatusLine(
    emoji: String,
    status: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .heightIn(min = 32.dp)
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick)
            .padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(
            text = emoji.ifBlank { "🙂" },
            fontSize = 16.sp,
        )
        Text(
            text = status.ifBlank { "平静" },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
        Icon(
            Icons.AutoMirrored.Filled.KeyboardArrowRight,
            contentDescription = "切换状态",
            tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.75f),
            modifier = Modifier.size(18.dp),
        )
    }
}

@Composable
fun SelfStatusDialog(
    initialEmoji: String,
    initialMessage: String,
    onDismiss: () -> Unit,
    onSave: (String, String) -> Unit,
) {
    var emoji by remember(initialEmoji) {
        mutableStateOf(initialEmoji.ifBlank { "🙂" })
    }
    var message by remember(initialMessage) {
        mutableStateOf(initialMessage.ifBlank { "今天也要好好生活" })
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("我的状态") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = "选一个 emoji 表示今天的状态，会显示在账号下方；留言仍会同步给 TA。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                SelfStatusOptions.chunked(2).forEach { rowOptions ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        rowOptions.forEach { option ->
                            val selected = emoji == option.emoji
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .heightIn(min = AppDimens.ButtonHeight)
                                    .clip(RoundedCornerShape(AppDimens.ButtonCorner))
                                    .clickable {
                                        emoji = option.emoji
                                        message = option.message
                                    },
                                shape = RoundedCornerShape(AppDimens.ButtonCorner),
                                color = if (selected) {
                                    MaterialTheme.colorScheme.primaryContainer
                                } else {
                                    MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f)
                                },
                                border = if (selected) {
                                    BorderStroke(1.dp, MaterialTheme.colorScheme.primary)
                                } else {
                                    null
                                },
                            ) {
                                Row(
                                    modifier = Modifier.padding(
                                        horizontal = 10.dp,
                                        vertical = 10.dp,
                                    ),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                ) {
                                    Text(option.emoji, fontSize = 18.sp)
                                    Text(
                                        option.label,
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                                    )
                                }
                            }
                        }
                        if (rowOptions.size == 1) {
                            Box(Modifier.weight(1f))
                        }
                    }
                }
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it.take(40) },
                    singleLine = true,
                    label = { Text("状态留言") },
                    shape = RoundedCornerShape(AppDimens.ButtonCorner),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        },
        confirmButton = {
            TextButton(onClick = { onSave(emoji, message.trim()) }) {
                Text("保存")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("取消") }
        },
    )
}
````

---

返回索引：[README.md](02-实战库/项目/安卓应用开发/README.md)
