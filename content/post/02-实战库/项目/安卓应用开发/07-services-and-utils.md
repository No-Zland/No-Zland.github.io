# 07 · 后台服务与工具类

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

前台/后台服务负责轮询、通知与提醒调度；工具类覆盖地图路线、坐标转换、农历、图片、TTS 与录音。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 服务与通知](#s07-1) | `CareBackgroundService` 前台轮询；`ReminderScheduler` 与 `ReminderReceiver` 处理精确/非精确闹钟；`NotificationHelper` 统一通知渠道。 | 5 |
| [2. 工具类](#s07-2) | 地理计算、百度地点搜索与路线、OSRM 兜底、农历节日、图片压缩、文本朗读与录音。 | 12 |

本篇共 **2 个步骤 / 17 个文件**，按表格顺序写入即可还原对应代码。

<a id="s07-1"></a>

## 步骤 07.1 · 服务与通知

`CareBackgroundService` 前台轮询；`ReminderScheduler` 与 `ReminderReceiver` 处理精确/非精确闹钟；`NotificationHelper` 统一通知渠道。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/service/CareBackgroundService.kt`
- `app/src/main/java/com/shineleong/toughmind/service/NotificationHelper.kt`
- `app/src/main/java/com/shineleong/toughmind/service/ReminderBootReceiver.kt`
- `app/src/main/java/com/shineleong/toughmind/service/ReminderReceiver.kt`
- `app/src/main/java/com/shineleong/toughmind/service/ReminderScheduler.kt`

### `app/src/main/java/com/shineleong/toughmind/service/CareBackgroundService.kt`

> 前台服务轮询位置与消息，尽量维持锁屏后的同步。

````kotlin
﻿package com.shineleong.toughmind.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import com.shineleong.toughmind.MainActivity
import com.shineleong.toughmind.ToughmindApplication
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/** 保持关心消息轮询，App 退到后台也能收到提醒。 */
class CareBackgroundService : Service() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var loop: Job? = null

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIFICATION_ID, buildNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (loop?.isActive != true) {
            loop = scope.launch {
                val app = application as ToughmindApplication
                while (isActive) {
                    runCatching { app.container.careSyncRepository.refreshNow() }
                    runCatching {
                        val since = app.container.chatMessageRepository.maxRemoteId()
                        val messages = app.container.careSyncRepository.fetchChatMessages(since).getOrThrow()
                        messages.forEach { dto ->
                            app.container.chatMessageRepository.insertRemote(
                                remoteId = dto.id,
                                text = dto.message,
                                fromSelf = dto.isMine,
                                senderName = dto.fromNickname,
                                createdAt = dto.createdAt,
                            )
                            if (!dto.isMine) {
                                app.container.notificationHelper.notifyCareMessage(
                                    dto.fromNickname.ifBlank { "亲友" },
                                    dto.message,
                                )
                            }
                        }
                    }
                    delay(30_000)
                }
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        loop?.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID,
                "念安后台消息",
                NotificationManager.IMPORTANCE_LOW,
            )
        )
    }

    private fun buildNotification(): Notification {
        val intent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("念安")
            .setContentText("正在接收关心消息")
            .setContentIntent(intent)
            .setOngoing(true)
            .build()
    }

    private companion object {
        const val CHANNEL_ID = "care_background"
        const val NOTIFICATION_ID = 7001
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/service/NotificationHelper.kt`

> 通知渠道、提醒通知与权限兼容。

````kotlin
package com.shineleong.toughmind.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.shineleong.toughmind.MainActivity
import com.shineleong.toughmind.data.model.AlarmEvent
import com.shineleong.toughmind.data.model.FatigueLevel

/** 分级告警 + 日历提醒通知。 */
class NotificationHelper(private val context: Context) {

    private val manager = NotificationManagerCompat.from(context)

    init {
        createChannels()
    }

    private fun createChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channels = listOf(
            CHANNEL_REMINDER to ("打卡与日程提醒" to NotificationManager.IMPORTANCE_HIGH),
            CHANNEL_CARE_MESSAGE to ("关心消息" to NotificationManager.IMPORTANCE_DEFAULT),
            "alarm_mild" to ("轻度提醒" to NotificationManager.IMPORTANCE_DEFAULT),
            "alarm_moderate" to ("中度提醒" to NotificationManager.IMPORTANCE_HIGH),
            "alarm_severe" to ("重度提醒" to NotificationManager.IMPORTANCE_HIGH),
            "alarm_medical" to ("紧急求助" to NotificationManager.IMPORTANCE_MAX),
        )
        channels.forEach { (id, pair) ->
            nm.createNotificationChannel(NotificationChannel(id, pair.first, pair.second))
        }
    }

    fun notifyAlarm(event: AlarmEvent) {
        val channelId = when (event.level) {
            FatigueLevel.MILD -> "alarm_mild"
            FatigueLevel.MODERATE -> "alarm_moderate"
            FatigueLevel.SEVERE -> "alarm_severe"
            else -> "alarm_medical"
        }
        val title = when {
            event.medicalLevel >= 1 -> "紧急求助：${event.medicalType.label}"
            else -> "关心提醒：${event.level.label}"
        }
        val content = event.message.ifBlank { "请及时关注 TA 的状态" }
        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(content)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .build()
        try {
            manager.notify(event.timestamp.hashCode(), notification)
        } catch (e: SecurityException) {
            // 未授予通知权限时忽略
        }
    }

    /** 日历定时任务到点提醒。 */
    fun notifyReminder(id: Int, title: String, content: String) {
        val openApp = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentIntent = PendingIntent.getActivity(
            context,
            id + REMINDER_REQUEST_OFFSET,
            openApp,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(context, CHANNEL_REMINDER)
            .setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle(title)
            .setContentText(content)
            .setStyle(NotificationCompat.BigTextStyle().bigText(content))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setContentIntent(contentIntent)
            .setAutoCancel(true)
            .build()
        try {
            manager.notify(id + REMINDER_REQUEST_OFFSET, notification)
        } catch (e: SecurityException) {
            // 未授予通知权限时忽略
        }
    }

    /** 对方从地图 / 关心页发来的"轻轻提醒"。 */
    fun notifyCareMessage(fromNickname: String, message: String) {
        val openApp = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentIntent = PendingIntent.getActivity(
            context,
            MESSAGE_REQUEST_CODE,
            openApp,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(context, CHANNEL_CARE_MESSAGE)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("${fromNickname.ifBlank { "TA" }} 的关心")
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setContentIntent(contentIntent)
            .setAutoCancel(true)
            .build()
        try {
            manager.notify(MESSAGE_REQUEST_CODE, notification)
        } catch (e: SecurityException) {
            // 未授予通知权限时忽略
        }
    }

    companion object {
        const val CHANNEL_REMINDER = "care_reminder"
        const val CHANNEL_CARE_MESSAGE = "care_message"
        private const val REMINDER_REQUEST_OFFSET = 10_000
        private const val MESSAGE_REQUEST_CODE = 20_001
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/service/ReminderBootReceiver.kt`

````kotlin
package com.shineleong.toughmind.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.shineleong.toughmind.data.local.db.AppDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.time.LocalDate

/** 开机 / 应用更新后恢复尚未触发的提醒（AlarmManager 的登记会随重启丢失）。 */
class ReminderBootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action
        if (action != Intent.ACTION_BOOT_COMPLETED && action != Intent.ACTION_MY_PACKAGE_REPLACED) {
            return
        }
        val pendingResult = goAsync()
        val appContext = context.applicationContext
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val dao = AppDatabase.getInstance(appContext).reminderDao()
                val scheduler = ReminderScheduler(appContext)
                val today = LocalDate.now().toString()
                dao.enabledFrom(today).forEach { scheduler.schedule(it) }
            } finally {
                pendingResult.finish()
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/service/ReminderReceiver.kt`

````kotlin
package com.shineleong.toughmind.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/** 日历提醒到点：弹出通知。 */
class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val id = intent.getIntExtra(ReminderScheduler.EXTRA_ID, 0)
        val title = intent.getStringExtra(ReminderScheduler.EXTRA_TITLE).orEmpty()
        val note = intent.getStringExtra(ReminderScheduler.EXTRA_NOTE).orEmpty()
        NotificationHelper(context).notifyReminder(
            id = id,
            title = title.ifBlank { "念安提醒" },
            content = note.ifBlank { "这是你为彼此设置的日程，别忘了完成约定。" },
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/service/ReminderScheduler.kt`

> 精确 / 非精确闹钟调度与取消。

````kotlin
package com.shineleong.toughmind.service

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import java.time.LocalDate
import java.time.ZoneId

/** 把日历提醒写入 AlarmManager；到点由 [ReminderReceiver] 发通知。 */
class ReminderScheduler(private val context: Context) {

    fun schedule(reminder: ReminderEntity) {
        if (!reminder.enabled) return
        val triggerAt = triggerAtMillis(reminder) ?: return
        if (triggerAt <= System.currentTimeMillis()) return

        val alarmManager = context.getSystemService(AlarmManager::class.java) ?: return
        val pendingIntent = buildPendingIntent(reminder)

        val canExact = Build.VERSION.SDK_INT < Build.VERSION_CODES.S ||
            alarmManager.canScheduleExactAlarms()
        if (canExact) {
            alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent)
        } else {
            alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent)
        }
    }

    fun cancel(reminderId: Long) {
        val alarmManager = context.getSystemService(AlarmManager::class.java) ?: return
        alarmManager.cancel(buildPendingIntent(reminderId, "", ""))
    }

    private fun triggerAtMillis(reminder: ReminderEntity): Long? = runCatching {
        LocalDate.parse(reminder.date)
            .atStartOfDay()
            .plusMinutes(reminder.timeMinutes.toLong())
            .atZone(ZoneId.systemDefault())
            .toInstant()
            .toEpochMilli()
    }.getOrNull()

    private fun buildPendingIntent(reminder: ReminderEntity): PendingIntent =
        buildPendingIntent(reminder.id, reminder.title, reminder.note)

    private fun buildPendingIntent(id: Long, title: String, note: String): PendingIntent {
        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(EXTRA_ID, id.toInt())
            putExtra(EXTRA_TITLE, title)
            putExtra(EXTRA_NOTE, note)
        }
        return PendingIntent.getBroadcast(
            context,
            id.toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }

    companion object {
        const val EXTRA_ID = "reminder_id"
        const val EXTRA_TITLE = "reminder_title"
        const val EXTRA_NOTE = "reminder_note"
    }
}
````

<a id="s07-2"></a>

## 步骤 07.2 · 工具类

地理计算、百度地点搜索与路线、OSRM 兜底、农历节日、图片压缩、文本朗读与录音。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/util/BaiduPlaceSearch.kt`
- `app/src/main/java/com/shineleong/toughmind/util/BaiduRoutePlanner.kt`
- `app/src/main/java/com/shineleong/toughmind/util/CoordinateTransform.kt`
- `app/src/main/java/com/shineleong/toughmind/util/GeoMath.kt`
- `app/src/main/java/com/shineleong/toughmind/util/ImageUtils.kt`
- `app/src/main/java/com/shineleong/toughmind/util/LunarDateUtils.kt`
- `app/src/main/java/com/shineleong/toughmind/util/NavigationHelper.kt`
- `app/src/main/java/com/shineleong/toughmind/util/OsrmRouteClient.kt`
- `app/src/main/java/com/shineleong/toughmind/util/TextReader.kt`
- `app/src/main/java/com/shineleong/toughmind/util/TtsMode.kt`
- `app/src/main/java/com/shineleong/toughmind/util/TtsPreset.kt`
- `app/src/main/java/com/shineleong/toughmind/util/VoiceRecorder.kt`

### `app/src/main/java/com/shineleong/toughmind/util/BaiduPlaceSearch.kt`

````kotlin
package com.shineleong.toughmind.util

import com.baidu.mapapi.model.LatLng
import com.baidu.mapapi.search.core.SearchResult
import com.baidu.mapapi.search.poi.OnGetPoiSearchResultListener
import com.baidu.mapapi.search.poi.PoiCitySearchOption
import com.baidu.mapapi.search.poi.PoiDetailResult
import com.baidu.mapapi.search.poi.PoiDetailSearchResult
import com.baidu.mapapi.search.poi.PoiIndoorResult
import com.baidu.mapapi.search.poi.PoiNearbySearchOption
import com.baidu.mapapi.search.poi.PoiResult
import com.baidu.mapapi.search.poi.PoiSearch

data class PlaceSuggestion(
    val name: String,
    val address: String,
    val lat: Double,
    val lon: Double,
)

/** 优先按当前位置附近搜索地点；也可切换到指定城市搜索。 */
class BaiduPlaceSearch(
    private val onResult: (List<PlaceSuggestion>) -> Unit,
    private val onError: (String) -> Unit,
) {
    private val search = PoiSearch.newInstance()

    init {
        search.setOnGetPoiSearchResultListener(object : OnGetPoiSearchResultListener {
            override fun onGetPoiResult(result: PoiResult?) {
                if (result == null || result.error != SearchResult.ERRORNO.NO_ERROR) {
                    onError("没有找到相关地点，换个关键词试试")
                    return
                }
                val list = result.allPoi.orEmpty().mapNotNull { info ->
                    val point = info.location ?: return@mapNotNull null
                    PlaceSuggestion(
                        name = info.name.orEmpty(),
                        address = listOfNotNull(info.city, info.area, info.address)
                            .filter { it.isNotBlank() }
                            .joinToString(" "),
                        lat = point.latitude,
                        lon = point.longitude,
                    )
                }.distinctBy { "${it.name}@${it.lat},${it.lon}" }
                onResult(list)
            }

            override fun onGetPoiDetailResult(result: PoiDetailResult?) = Unit

            override fun onGetPoiDetailResult(result: PoiDetailSearchResult?) = Unit

            override fun onGetPoiIndoorResult(result: PoiIndoorResult?) = Unit
        })
    }

    fun searchNearby(query: String, lat: Double, lon: Double) {
        if (query.isBlank()) {
            onResult(emptyList())
            return
        }
        search.searchNearby(
            PoiNearbySearchOption()
                .keyword(query.trim())
                .location(LatLng(lat, lon))
                .radius(10_000)
                .pageCapacity(20)
                .pageNum(0)
        )
    }

    fun searchCity(query: String, city: String) {
        if (query.isBlank()) {
            onResult(emptyList())
            return
        }
        search.searchInCity(
            PoiCitySearchOption()
                .city(city.ifBlank { "全国" })
                .keyword(query.trim())
                .pageCapacity(20)
                .pageNum(0)
        )
    }

    fun destroy() {
        search.destroy()
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/BaiduRoutePlanner.kt`

````kotlin
package com.shineleong.toughmind.util

import com.baidu.mapapi.model.LatLng
import com.baidu.mapapi.search.core.RouteLine
import com.baidu.mapapi.search.core.RouteStep
import com.baidu.mapapi.search.core.SearchResult
import com.baidu.mapapi.search.route.BikingRoutePlanOption
import com.baidu.mapapi.search.route.BikingRouteResult
import com.baidu.mapapi.search.route.BikingRouteLine
import com.baidu.mapapi.search.route.DrivingRoutePlanOption
import com.baidu.mapapi.search.route.DrivingRouteResult
import com.baidu.mapapi.search.route.DrivingRouteLine
import com.baidu.mapapi.search.route.IndoorRouteResult
import com.baidu.mapapi.search.route.IntegralRouteResult
import com.baidu.mapapi.search.route.MassTransitRouteResult
import com.baidu.mapapi.search.route.OnGetRoutePlanResultListener
import com.baidu.mapapi.search.route.PlanNode
import com.baidu.mapapi.search.route.RoutePlanSearch
import com.baidu.mapapi.search.route.TransitRoutePlanOption
import com.baidu.mapapi.search.route.TransitRouteResult
import com.baidu.mapapi.search.route.TransitRouteLine
import com.baidu.mapapi.search.route.WalkingRoutePlanOption
import com.baidu.mapapi.search.route.WalkingRouteResult
import com.baidu.mapapi.search.route.WalkingRouteLine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

/** 一段可播报的路线步骤；points 是该步骤实际经过的坐标。 */
data class BaiduRouteStep(
    val instruction: String,
    val distanceMeters: Int,
    val durationSeconds: Int,
    val points: List<LatLng>,
)

data class BaiduRoute(
    val distanceMeters: Int,
    val durationSeconds: Int,
    val points: List<LatLng> = emptyList(),
    val steps: List<BaiduRouteStep> = emptyList(),
)

/** APP 内的百度路线规划，不跳转外部地图。 */
class BaiduRoutePlanner(
    private val onResult: (BaiduRoute) -> Unit,
    private val onError: (String) -> Unit,
) {
    private val search = RoutePlanSearch.newInstance()

    init {
        search.setOnGetRoutePlanResultListener(object : OnGetRoutePlanResultListener {
            override fun onGetDrivingRouteResult(result: DrivingRouteResult?) {
                if (result == null || result.error != SearchResult.ERRORNO.NO_ERROR) {
                    onError("暂时无法规划路线")
                    return
                }
                val line = result.routeLines?.firstOrNull()
                if (line == null) onError("没有可用路线")
                else onResult(line.toBaiduRoute())
            }

            override fun onGetWalkingRouteResult(result: WalkingRouteResult?) {
                val line = result?.routeLines?.firstOrNull()
                if (line == null) onError("暂时无法规划步行路线")
                else onResult(line.toBaiduRoute())
            }

            override fun onGetTransitRouteResult(result: TransitRouteResult?) {
                val line = result?.routeLines?.firstOrNull()
                if (line == null) onError("暂时无法规划公交路线")
                else onResult(line.toBaiduRoute())
            }

            override fun onGetBikingRouteResult(result: BikingRouteResult?) {
                val line = result?.routeLines?.firstOrNull()
                if (line == null) onError("暂时无法规划骑行路线")
                else onResult(line.toBaiduRoute())
            }

            override fun onGetMassTransitRouteResult(result: MassTransitRouteResult?) = Unit
            override fun onGetIndoorRouteResult(result: IndoorRouteResult?) = Unit
            override fun onGetIntegralRouteResult(result: IntegralRouteResult?) = Unit
        })
    }

    fun route(
        mode: NavMode,
        fromLat: Double,
        fromLon: Double,
        toLat: Double,
        toLon: Double,
    ) {
        val from = PlanNode.withLocation(LatLng(fromLat, fromLon))
        val to = PlanNode.withLocation(LatLng(toLat, toLon))
        when (mode) {
            NavMode.DRIVING -> search.drivingSearch(DrivingRoutePlanOption().from(from).to(to))
            NavMode.WALKING -> search.walkingSearch(WalkingRoutePlanOption().from(from).to(to))
            NavMode.EBIKE -> search.bikingSearch(BikingRoutePlanOption().from(from).to(to))
            NavMode.TRANSIT -> search.transitSearch(
                TransitRoutePlanOption().from(from).to(to).city("杭州")
            )
        }
    }

    fun destroy() {
        search.destroy()
    }
}

/** 把百度回调式规划包成 suspend，方便和 OSRM 兜底串起来。 */
suspend fun planBaiduRoute(
    mode: NavMode,
    fromLat: Double,
    fromLon: Double,
    toLat: Double,
    toLon: Double,
): BaiduRoute = suspendCancellableCoroutine { continuation ->
    var planner: BaiduRoutePlanner? = null
    planner = BaiduRoutePlanner(
        onResult = { route ->
            planner?.destroy()
            if (continuation.isActive) continuation.resume(route)
        },
        onError = { message ->
            planner?.destroy()
            if (continuation.isActive) {
                continuation.resumeWithException(IllegalStateException(message))
            }
        },
    )
    continuation.invokeOnCancellation { planner?.destroy() }
    runCatching {
        planner.route(mode, fromLat, fromLon, toLat, toLon)
    }.onFailure { error ->
        planner.destroy()
        if (continuation.isActive) {
            continuation.resumeWithException(error)
        }
    }
}

private fun <T : RouteStep> RouteLine<T>.toBaiduRoute(): BaiduRoute {    val steps = allStep.orEmpty().map { step ->
        val points = step.wayPoints.orEmpty()
        BaiduRouteStep(
            instruction = step.playableInstruction(),
            distanceMeters = step.distance.coerceAtLeast(0),
            durationSeconds = step.duration.coerceAtLeast(0),
            points = points,
        )
    }
    val points = steps
        .flatMap { it.points }
        .distinctBy { "${it.latitude},${it.longitude}" }
    return BaiduRoute(
        distanceMeters = distance.coerceAtLeast(0),
        durationSeconds = duration.coerceAtLeast(0),
        points = points,
        steps = steps,
    )
}

/** 不同出行方式的步骤类型不同，但都有可读的 instructions。 */
private fun RouteStep.playableInstruction(): String = when (this) {
    is DrivingRouteLine.DrivingStep -> instructions.orEmpty()
    is WalkingRouteLine.WalkingStep -> instructions.orEmpty()
    is BikingRouteLine.BikingStep -> instructions.orEmpty()
    is TransitRouteLine.TransitStep -> instructions.orEmpty()
    else -> name.orEmpty()
}.trim()
````

### `app/src/main/java/com/shineleong/toughmind/util/CoordinateTransform.kt`

````kotlin
package com.shineleong.toughmind.util

import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * 百度地图使用 BD-09，OSRM / 大部分开放路线服务使用 WGS-84。
 * 这里做 BD-09 → WGS-84 与反向转换，避免“路线画在马路边上”。
 */
object CoordinateTransform {
    private const val PI = Math.PI
    private const val X_PI = PI * 3000.0 / 180.0
    private const val A = 6378245.0
    private const val EE = 0.00669342162296594323

    fun bd09ToWgs84(lon: Double, lat: Double): Pair<Double, Double> {
        if (outOfChina(lon, lat)) return lon to lat
        val gcj = bd09ToGcj02(lon, lat)
        return gcjToWgs84(gcj.first, gcj.second)
    }

    fun wgs84ToBd09(lon: Double, lat: Double): Pair<Double, Double> {
        if (outOfChina(lon, lat)) return lon to lat
        val gcj = wgs84ToGcj02(lon, lat)
        return gcj02ToBd09(gcj.first, gcj.second)
    }

    private fun outOfChina(lon: Double, lat: Double): Boolean =
        lon < 72.004 || lon > 137.8347 || lat < 0.8293 || lat > 55.8271

    private fun bd09ToGcj02(lon: Double, lat: Double): Pair<Double, Double> {
        val x = lon - 0.0065
        val y = lat - 0.006
        val z = sqrt(x * x + y * y) - 0.00002 * sin(y * X_PI)
        val theta = kotlin.math.atan2(y, x) - 0.000003 * cos(x * X_PI)
        return z * cos(theta) to z * sin(theta)
    }

    private fun gcj02ToBd09(lon: Double, lat: Double): Pair<Double, Double> {
        val z = sqrt(lon * lon + lat * lat) + 0.00002 * sin(lat * X_PI)
        val theta = kotlin.math.atan2(lat, lon) + 0.000003 * cos(lon * X_PI)
        return z * cos(theta) + 0.0065 to z * sin(theta) + 0.006
    }

    private fun gcjToWgs84(lon: Double, lat: Double): Pair<Double, Double> {
        var wgsLon = lon
        var wgsLat = lat
        repeat(3) {
            val gcj = wgs84ToGcj02(wgsLon, wgsLat)
            wgsLon -= gcj.first - lon
            wgsLat -= gcj.second - lat
        }
        return wgsLon to wgsLat
    }

    private fun wgs84ToGcj02(lon: Double, lat: Double): Pair<Double, Double> {
        var dLat = transformLat(lon - 105.0, lat - 35.0)
        var dLon = transformLon(lon - 105.0, lat - 35.0)
        val radLat = lat / 180.0 * PI
        var magic = sin(radLat)
        magic = 1 - EE * magic * magic
        val sqrtMagic = sqrt(magic)
        dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI)
        dLon = (dLon * 180.0) / (A / sqrtMagic * cos(radLat) * PI)
        return lon + dLon to lat + dLat
    }

    private fun transformLat(x: Double, y: Double): Double {
        var ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
        ret += (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
        ret += (160.0 * sin(y / 12.0 * PI) + 320 * sin(y * PI / 30.0)) * 2.0 / 3.0
        return ret
    }

    private fun transformLon(x: Double, y: Double): Double {
        var ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
        ret += (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
        ret += (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x / 30.0 * PI)) * 2.0 / 3.0
        return ret
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/GeoMath.kt`

````kotlin
package com.shineleong.toughmind.util

import com.shineleong.toughmind.data.model.LocationRelation
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * 经纬度几何计算：Haversine 直线距离 + 初始方位角。
 * 用于计算驾驶员与亲属端之间的位置关系。
 */
object GeoMath {

    private const val EARTH_RADIUS_M = 6_371_000.0

    /** 判断经纬度是否为有效位置（任一坐标非 0 即视为有效）。 */
    fun hasValidPosition(lat: Double, lon: Double): Boolean = lat != 0.0 || lon != 0.0

    /** Haversine 公式计算两点直线距离（米）。 */
    fun distanceMeters(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val radLat1 = Math.toRadians(lat1)
        val radLat2 = Math.toRadians(lat2)
        val a = sin(dLat / 2) * sin(dLat / 2) +
            cos(radLat1) * cos(radLat2) * sin(dLon / 2) * sin(dLon / 2)
        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return EARTH_RADIUS_M * c
    }

    /** 计算从 point1 指向 point2 的初始方位角（0~360 度，北为 0）。 */
    fun bearingDegrees(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val radLat1 = Math.toRadians(lat1)
        val radLat2 = Math.toRadians(lat2)
        val dLon = Math.toRadians(lon2 - lon1)
        val y = sin(dLon) * cos(radLat2)
        val x = cos(radLat1) * sin(radLat2) - sin(radLat1) * cos(radLat2) * cos(dLon)
        val theta = Math.toDegrees(atan2(y, x))
        return (theta + 360.0) % 360.0
    }

    /** 将方位角转换为八方位中文描述（北/东北/东/...）。 */
    fun directionLabel(bearing: Double): String = when {
        bearing >= 337.5 || bearing < 22.5 -> "北"
        bearing < 67.5 -> "东北"
        bearing < 112.5 -> "东"
        bearing < 157.5 -> "东南"
        bearing < 202.5 -> "南"
        bearing < 247.5 -> "西南"
        bearing < 292.5 -> "西"
        else -> "西北"
    }

    /**
     * 把朝向归一化到 [0, 360)。定位 SDK 在无法判断方向时会给 0 / 负数 / NaN，
     * 这里统一返回 0，界面据此不画方向扇形。
     */
    fun normalizeHeading(degrees: Float): Float {
        if (!degrees.isFinite() || degrees < 0f) return 0f
        val normalized = ((degrees % 360f) + 360f) % 360f
        return if (normalized >= 359.5f) 0f else normalized
    }

    /** 罗盘方位：0° 就是正北，负角也能正确回绕；与 GPS 航向不同，0 是有效值。 */
    fun normalizeCompass(degrees: Float): Float {
        if (!degrees.isFinite()) return 0f
        return ((degrees % 360f) + 360f) % 360f
    }

    /**
     * 朝向的圆周平滑：避免 359° → 1° 时绕一大圈，也避免每次定位都抖动。
     * next 为 0（未知方向）时沿用 previous。
     */
    fun smoothHeading(previous: Float, next: Float, alpha: Float = 0.35f): Float {
        val target = normalizeHeading(next)
        if (target <= 0f) return normalizeHeading(previous)
        val from = normalizeHeading(previous)
        if (from <= 0f) return target
        val delta = ((target - from + 540f) % 360f) - 180f
        return normalizeHeading(from + delta * alpha)
    }

    /** 可空朝向的圆周平滑：null 表示暂时没有方向（没有罗盘 / 静止且无 GPS 航向）。 */
    fun smoothHeadingOrNull(previous: Float?, next: Float?, alpha: Float = 0.4f): Float? {
        if (next == null || !next.isFinite()) return previous
        val target = normalizeCompass(next)
        val from = previous ?: return target
        val delta = ((target - from + 540f) % 360f) - 180f
        return normalizeCompass(from + delta * alpha)
    }

    /** 计算 point1（驾驶员）相对 point2（亲属端）的距离与方位。 */
    fun relation(lat1: Double, lon1: Double, lat2: Double, lon2: Double): LocationRelation {
        val bearing = bearingDegrees(lat1, lon1, lat2, lon2)
        return LocationRelation(
            distanceMeters = distanceMeters(lat1, lon1, lat2, lon2),
            bearingDegrees = bearing.toFloat(),
            directionLabel = directionLabel(bearing),
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/ImageUtils.kt`

````kotlin
package com.shineleong.toughmind.util

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Base64
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream

object ImageUtils {

    suspend fun encode(context: Context, uri: Uri, maxSide: Int = 1024, quality: Int = 68): String? =
        withContext(Dispatchers.IO) {
            runCatching {
                val input = context.contentResolver.openInputStream(uri) ?: return@runCatching null
                val original = input.use { BitmapFactory.decodeStream(it) } ?: return@runCatching null
                val scale = minOf(1f, maxSide.toFloat() / maxOf(original.width, original.height))
                val bitmap = if (scale < 1f) {
                    Bitmap.createScaledBitmap(
                        original,
                        (original.width * scale).toInt().coerceAtLeast(1),
                        (original.height * scale).toInt().coerceAtLeast(1),
                        true,
                    )
                } else {
                    original
                }
                val output = ByteArrayOutputStream()
                bitmap.compress(Bitmap.CompressFormat.JPEG, quality, output)
                Base64.encodeToString(output.toByteArray(), Base64.NO_WRAP)
            }.getOrNull()
        }

    fun decode(base64: String?): ImageBitmap? {
        if (base64.isNullOrBlank()) return null
        return runCatching {
            val bytes = Base64.decode(base64, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)?.asImageBitmap()
        }.getOrNull()
    }
}

@Composable
fun ImagePreviewDialog(base64: String, onDismiss: () -> Unit) {
    val bitmap = remember(base64) { ImageUtils.decode(base64) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("查看照片") },
        text = {
            if (bitmap != null) {
                Image(
                    bitmap = bitmap,
                    contentDescription = "照片",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(4.dp)
                        .clip(RoundedCornerShape(12.dp)),
                    contentScale = ContentScale.Fit,
                )
            } else {
                Text("照片加载失败")
            }
        },
        confirmButton = { TextButton(onClick = onDismiss) { Text("关闭") } },
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/util/LunarDateUtils.kt`

````kotlin
package com.shineleong.toughmind.util

import android.icu.util.ChineseCalendar
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.Calendar

/** 农历、节日与二十四节气，用于日程日历的日期副标题。 */
object LunarDateUtils {

    private val monthNames = listOf(
        "正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊",
    )
    private val dayNames = listOf(
        "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
        "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
        "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
    )
    private val solarFestivals = mapOf(
        "01-01" to "元旦",
        "02-14" to "情人节",
        "03-08" to "妇女节",
        "05-01" to "劳动节",
        "06-01" to "儿童节",
        "09-10" to "教师节",
        "10-01" to "国庆节",
        "12-25" to "圣诞节",
        "03-12" to "植树节",
        "05-04" to "青年节",
    )
    private val lunarFestivals = mapOf(
        101 to "春节",
        115 to "元宵",
        202 to "龙抬头",
        505 to "端午",
        707 to "七夕",
        715 to "中元",
        815 to "中秋",
        909 to "重阳",
        1001 to "寒衣",
        1015 to "下元",
        1208 to "腊八",
        1223 to "小年",
    )

    private val termNames = listOf(
        "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
        "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
        "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
        "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
    )
    private val termInfo = longArrayOf(
        0, 21208, 42467, 63836, 85337, 107014, 128867, 150921,
        173149, 195551, 218072, 240693, 263343, 285989, 308563, 331033,
        353350, 375494, 397447, 419210, 440795, 462224, 483532, 504758,
    )

    fun lunarLabel(date: LocalDate): String {
        val lunar = lunarParts(date) ?: return ""
        return if (lunar.second == 1) {
            (if (lunar.third) "闰" else "") + monthNames[lunar.first - 1] + "月"
        } else {
            dayNames[(lunar.second - 1).coerceIn(0, dayNames.lastIndex)]
        }
    }

    fun festivalOrTerm(date: LocalDate): String? {
        solarFestivals[date.format(java.time.format.DateTimeFormatter.ofPattern("MM-dd"))]
            ?.let { return it }
        val lunar = lunarParts(date)
        if (lunar != null) {
            lunarFestivals[lunar.first * 100 + lunar.second]?.let { return it }
            // 除夕是腊月最后一天：第二天就是正月初一。
            if (lunar.first == 12) {
                val next = lunarParts(date.plusDays(1))
                if (next != null && next.first == 1 && next.second == 1) return "除夕"
            }
        }
        return solarTerm(date)
    }

    private fun lunarParts(date: LocalDate): Triple<Int, Int, Boolean>? {
        return runCatching {
            val calendar = ChineseCalendar().apply {
                timeInMillis = date.atTime(12, 0)
                    .atZone(ZoneId.systemDefault())
                    .toInstant()
                    .toEpochMilli()
            }
            val month = calendar.get(Calendar.MONTH) + 1
            val day = calendar.get(Calendar.DAY_OF_MONTH)
            val leap = calendar.get(ChineseCalendar.IS_LEAP_MONTH) == 1
            Triple(month, day, leap)
        }.getOrNull()
    }

    private fun solarTerm(date: LocalDate): String? {
        val zone = ZoneId.of("Asia/Shanghai")
        val base = -2208549300000L
        for (index in termInfo.indices) {
            val millis = 31556925974.7 * (date.year - 1900) + termInfo[index] * 60000L
            val termDate = Instant.ofEpochMilli(base + millis.toLong())
                .atZone(zone)
                .toLocalDate()
            if (termDate == date) return termNames[index]
        }
        return null
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/NavigationHelper.kt`

````kotlin
package com.shineleong.toughmind.util

import android.content.Context
import android.content.Intent
import android.net.Uri

enum class NavMode(
    val label: String,
    val emoji: String,
    val baiduMode: String,
    val amapType: String,
    val webMode: String,
) {
    DRIVING("驾车", "🚗", "driving", "0", "car"),
    WALKING("步行", "🚶", "walking", "2", "walk"),
    TRANSIT("公共交通", "🚌", "transit", "1", "bus"),
    EBIKE("电动车", "🛵", "riding", "3", "ride"),
}

object NavigationHelper {

    fun open(
        context: Context,
        lat: Double,
        lon: Double,
        name: String,
        mode: NavMode,
    ): Boolean {
        val label = name.ifBlank { "TA" }
        val encoded = Uri.encode(label)
        val candidates = listOf(
            Uri.parse(
                "baidumap://map/direction?destination=latlng:$lat,$lon|name:$encoded" +
                    "&mode=${mode.baiduMode}&src=android.toughmind"
            ),
            Uri.parse(
                "androidamap://route?sourceApplication=TOUCHMIND" +
                    "&dlat=$lat&dlon=$lon&dname=$encoded&dev=0&t=${mode.amapType}"
            ),
            Uri.parse(
                "https://uri.amap.com/navigation?to=$lon,$lat,$encoded" +
                    "&mode=${mode.webMode}&policy=1&src=TOUCHMIND"
            ),
            Uri.parse("https://www.google.com/maps/dir/?api=1&destination=$lat,$lon&travelmode=${mode.webMode}"),
        )
        candidates.forEach { uri ->
            val intent = Intent(Intent.ACTION_VIEW, uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            if (intent.resolveActivity(context.packageManager) != null) {
                return runCatching {
                    context.startActivity(intent)
                    true
                }.getOrDefault(false)
            }
        }
        return false
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/OsrmRouteClient.kt`

````kotlin
package com.shineleong.toughmind.util

import com.baidu.mapapi.model.LatLng
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.io.IOException
import java.util.Locale
import java.util.concurrent.TimeUnit

/**
 * 百度路线接口不可用时的道路级兜底：OSRM 返回真实道路几何与分段动作，
 * 而不是把起终点连成一条直线。
 *
 * 百度坐标是 BD-09，OSRM 用 WGS-84；请求前转换，返回后再转回 BD-09 交给百度地图绘制。
 */
object OsrmRouteClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(12, TimeUnit.SECONDS)
        .callTimeout(15, TimeUnit.SECONDS)
        .build()

    suspend fun route(
        mode: NavMode,
        fromLat: Double,
        fromLon: Double,
        toLat: Double,
        toLon: Double,
    ): BaiduRoute = withContext(Dispatchers.IO) {
        val profile = when (mode) {
            NavMode.DRIVING -> "driving"
            NavMode.WALKING -> "walking"
            NavMode.EBIKE -> "cycling"
            NavMode.TRANSIT -> throw IOException("公交路线暂不可用，请选择驾车或步行")
        }
        val from = CoordinateTransform.bd09ToWgs84(fromLon, fromLat)
        val to = CoordinateTransform.bd09ToWgs84(toLon, toLat)
        val url = buildString {
            append("https://router.project-osrm.org/route/v1/")
            append(profile)
            append("/")
            append(String.format(Locale.US, "%.6f,%.6f", from.first, from.second))
            append(";")
            append(String.format(Locale.US, "%.6f,%.6f", to.first, to.second))
            append("?overview=full&geometries=geojson&steps=true&alternatives=false")
        }
        val request = Request.Builder()
            .url(url)
            .header("User-Agent", "Toughmind/1.0 (Android)")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("路线服务返回 ${response.code}")
            }
            val body = response.body?.string() ?: throw IOException("路线服务没有返回内容")
            parse(body)
        }
    }

    private fun parse(body: String): BaiduRoute {
        val root = JSONObject(body)
        if (root.optString("code") != "Ok") {
            throw IOException("路线规划失败：${root.optString("message").ifBlank { root.optString("code") }}")
        }
        val routes = root.optJSONArray("routes") ?: throw IOException("没有可用路线")
        if (routes.length() == 0) throw IOException("没有可用路线")
        val route = routes.getJSONObject(0)
        val distance = route.optDouble("distance", 0.0).toInt()
        val duration = route.optDouble("duration", 0.0).toInt()
        if (distance <= 0) throw IOException("路线距离为 0")

        val points = route.optJSONObject("geometry")
            ?.optJSONArray("coordinates")
            ?.let(::parseCoordinates)
            .orEmpty()

        val legs = route.optJSONArray("legs")
        val stepsJson = if (legs != null && legs.length() > 0) {
            legs.getJSONObject(0).optJSONArray("steps")
        } else {
            null
        }
        val steps = buildList {
            if (stepsJson != null) {
                for (index in 0 until stepsJson.length()) {
                    val json = stepsJson.optJSONObject(index) ?: continue
                    val stepPoints = json.optJSONObject("geometry")
                        ?.optJSONArray("coordinates")
                        ?.let(::parseCoordinates)
                        .orEmpty()
                    if (stepPoints.isEmpty()) continue
                    add(
                        BaiduRouteStep(
                            instruction = instructionOf(json),
                            distanceMeters = json.optDouble("distance", 0.0).toInt(),
                            durationSeconds = json.optDouble("duration", 0.0).toInt(),
                            points = stepPoints,
                        ),
                    )
                }
            }
        }

        return BaiduRoute(
            distanceMeters = distance,
            durationSeconds = duration,
            points = if (points.isNotEmpty()) points else steps.flatMap { it.points },
            steps = steps,
        )
    }

    /** GeoJSON 是 [lon, lat]，转成百度 BD-09 的 LatLng。 */
    private fun parseCoordinates(array: org.json.JSONArray): List<LatLng> = buildList {
        for (index in 0 until array.length()) {
            val pair = array.optJSONArray(index) ?: continue
            val lon = pair.optDouble(0, Double.NaN)
            val lat = pair.optDouble(1, Double.NaN)
            if (!lon.isFinite() || !lat.isFinite()) continue
            val bd = CoordinateTransform.wgs84ToBd09(lon, lat)
            add(LatLng(bd.second, bd.first))
        }
    }

    private fun instructionOf(step: JSONObject): String {
        val name = step.optString("name").trim()
        val maneuver = step.optJSONObject("maneuver")
        val type = maneuver?.optString("type").orEmpty()
        val modifier = maneuver?.optString("modifier").orEmpty()
        val turn = when (modifier) {
            "left" -> "左转"
            "right" -> "右转"
            "slight left" -> "向左前方行驶"
            "slight right" -> "向右前方行驶"
            "sharp left" -> "向左急转"
            "sharp right" -> "向右急转"
            "uturn" -> "掉头"
            "straight" -> "直行"
            else -> ""
        }
        fun withRoad(action: String, suffix: String = "进入"): String = when {
            name.isBlank() && action.isBlank() -> "继续前行"
            name.isBlank() -> action
            action.isBlank() -> "$suffix $name"
            else -> "$action，$suffix $name"
        }
        return when (type) {
            "depart" -> if (name.isBlank()) "从当前位置出发" else "沿 $name 出发"
            "arrive" -> "到达目的地"
            "turn", "end of road" -> withRoad(turn)
            "new name", "continue" -> if (name.isBlank()) "继续前行" else "继续沿 $name 前行"
            "merge" -> if (name.isBlank()) "汇入主路" else "汇入 $name"
            "fork" -> withRoad(turn.ifBlank { "沿岔路行驶" })
            "roundabout", "rotary" -> if (name.isBlank()) "进入环岛" else "进入环岛，驶入 $name"
            "on ramp" -> if (name.isBlank()) "驶入匝道" else "驶入匝道 $name"
            "off ramp" -> if (name.isBlank()) "驶出匝道" else "驶出匝道 $name"
            else -> withRoad(turn)
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/TextReader.kt`

````kotlin
package com.shineleong.toughmind.util

import android.content.Context
import android.speech.tts.TextToSpeech

/**
 * 通用文本朗读器：不依赖具体页面，供聊天、关心建议等文本复用。
 * 方言是否可用由系统 TTS 引擎决定；没有对应音色时 [speak] 返回 false。
 */
class TextReader(context: Context) {

    private var ready = false
    private var tts: TextToSpeech? = TextToSpeech(context.applicationContext) { status ->
        ready = status == TextToSpeech.SUCCESS
    }

    fun speak(
        text: String,
        preset: TtsPreset,
        mode: TtsMode = TtsMode.OFFLINE,
        rate: Float = 1f,
    ): Boolean {
        val engine = tts ?: return false
        if (!ready || text.isBlank()) return false
        val locale = preset.resolveLocale(text)
        val available = engine.isLanguageAvailable(locale)
        if (available < 0) return false
        val candidates = engine.voices.orEmpty().filter { voice ->
            voice.locale.language == locale.language &&
                (locale.country.isBlank() || voice.locale.country == locale.country)
        }
        val chosen = when (mode) {
            TtsMode.CLOUD -> candidates.firstOrNull { it.isNetworkConnectionRequired }
                ?: candidates.firstOrNull()
            TtsMode.OFFLINE -> candidates.firstOrNull { !it.isNetworkConnectionRequired }
                ?: candidates.firstOrNull()
        }
        if (chosen != null) {
            engine.voice = chosen
        } else {
            engine.language = locale
        }
        engine.setSpeechRate(rate.coerceIn(0.7f, 1.3f))
        return engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, "read-aloud") == TextToSpeech.SUCCESS
    }

    fun stop() {
        tts?.stop()
    }

    fun release() {
        ready = false
        tts?.stop()
        tts?.shutdown()
        tts = null
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/TtsMode.kt`

````kotlin
package com.shineleong.toughmind.util

/** 朗读模式：云端音色（系统网络音色）/ 离线音色（已下载的系统或本地模型）。 */
enum class TtsMode(
    val key: String,
    val labelZh: String,
    val labelEn: String,
) {
    CLOUD("cloud", "云端", "Cloud"),
    OFFLINE("offline", "离线", "Offline"),
    ;

    companion object {
        fun fromKey(key: String): TtsMode = entries.firstOrNull { it.key == key } ?: OFFLINE
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/TtsPreset.kt`

````kotlin
package com.shineleong.toughmind.util

import java.util.Locale

/** 朗读音色 / 方言预设。真正的方言发音取决于系统是否安装了对应 TTS 音色。 */
enum class TtsPreset(
    val key: String,
    val labelZh: String,
    val labelEn: String,
    val locale: Locale?,
) {
    AUTO("auto", "跟随系统", "Auto", null),
    MANDARIN("mandarin", "普通话", "Mandarin", Locale.SIMPLIFIED_CHINESE),
    CANTONESE("cantonese", "粤语", "Cantonese", Locale.forLanguageTag("zh-HK")),
    ENGLISH("english", "英语", "English", Locale.US),
    ;

    fun resolveLocale(text: String): Locale = locale ?: if (text.any { it in '\u4e00'..'\u9fff' }) {
        Locale.SIMPLIFIED_CHINESE
    } else {
        Locale.US
    }

    /** 界面级音色：AUTO 按 App 语言，其余用预设。 */
    fun uiLocale(english: Boolean): Locale =
        locale ?: if (english) Locale.US else Locale.SIMPLIFIED_CHINESE

    companion object {
        fun fromKey(key: String): TtsPreset = entries.firstOrNull { it.key == key } ?: AUTO
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/util/VoiceRecorder.kt`

````kotlin
﻿package com.shineleong.toughmind.util

import android.content.Context
import android.media.MediaRecorder
import java.io.File

/** 简易语音留言录制，保存到应用私有目录。 */
class VoiceRecorder(private val context: Context) {
    private var recorder: MediaRecorder? = null
    private var file: File? = null
    private var startedAt = 0L

    fun start(): Boolean {
        runCatching {
            val target = File(context.filesDir, "voice_${System.currentTimeMillis()}.m4a")
            val r = if (android.os.Build.VERSION.SDK_INT >= 31) {
                MediaRecorder(context)
            } else {
                @Suppress("DEPRECATION")
                MediaRecorder()
            }
            r.setAudioSource(MediaRecorder.AudioSource.MIC)
            r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            r.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            r.setOutputFile(target.absolutePath)
            r.prepare()
            r.start()
            recorder = r
            file = target
            startedAt = System.currentTimeMillis()
        }.onFailure {
            recorder?.release()
            recorder = null
            file = null
        }
        return recorder != null
    }

    fun stop(): Pair<String, Long>? {
        val r = recorder ?: return null
        val target = file
        val duration = System.currentTimeMillis() - startedAt
        runCatching { r.stop() }
        r.release()
        recorder = null
        file = null
        return if (target != null && target.exists() && target.length() > 0) {
            target.absolutePath to duration
        } else null
    }

    fun cancel() {
        runCatching { recorder?.stop() }
        recorder?.release()
        recorder = null
        file?.delete()
        file = null
    }
}
````

---

返回索引：[README.md](README.md)
