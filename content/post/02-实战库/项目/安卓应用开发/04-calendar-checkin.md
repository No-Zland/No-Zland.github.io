# 04 · 行程、日历与打卡

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

行程页合并日历与打卡：月视图（农历、节日、节气）、日程与共享提醒、双方打卡任务、历史记录与迷你出行页。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 日历与日程](#s04-1) | 月视图、日期详情、日程流、倒数日与提醒编辑。 | 4 |
| [2. 打卡任务](#s04-2) | 双方打卡点、完成状态与提醒对方。 | 2 |
| [3. 历史与出行](#s04-3) | 动态记录页与出行页入口。 | 3 |

本篇共 **3 个步骤 / 9 个文件**，按表格顺序写入即可还原对应代码。

<a id="s04-1"></a>

## 步骤 04.1 · 日历与日程

月视图、日期详情、日程流、倒数日与提醒编辑。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarReminders.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarScheduleCards.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarReminders.kt`

> 提醒列表、新建/编辑提醒弹窗与数字滚轮。

````kotlin
package com.shineleong.toughmind.ui.screen.calendar

import android.app.TimePickerDialog
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Alarm
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Today
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.SectionTitle
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.util.ImagePreviewDialog
import com.shineleong.toughmind.util.ImageUtils
import kotlinx.coroutines.launch
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.GoldDark
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.SurfaceSubtle
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.LunarDateUtils
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

@Composable
internal fun UpcomingRemindersCard(
    reminders: List<ReminderEntity>,
    onOpenDate: (ReminderEntity) -> Unit,
) {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "本月提醒",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
            }
            reminders.forEach { reminder ->
                ReminderRow(
                    reminder = reminder,
                    onClick = { onOpenDate(reminder) },
                )
            }
        }
    }
}

@Composable
private fun ReminderRow(
    reminder: ReminderEntity,
    onClick: () -> Unit,
) {
    val english = LocalAppLanguage.current == "en"
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(vertical = 6.dp, horizontal = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text(
            text = "${formatMinutes(reminder.timeMinutes)}",
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = GoldDark,
        )
        Column(Modifier.weight(1f)) {
            Text(
                text = reminder.title,
                style = MaterialTheme.typography.bodyMedium,
                color = TextPrimary,
                maxLines = 1,
            )
            Text(
                text = buildString {
                    append(reminderTypeLabel(reminder.type, english))
                    append(" · ")
                    append(reminder.date)
                    countdownText(reminder)?.let { append(" · ").append(it) }
                },
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
        }
        if (!reminder.enabled) {
            Text("已关闭", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
        }
    }
}

@Composable
internal fun AddReminderDialog(
    date: LocalDate,
    onDismiss: () -> Unit,
    onSave: (LocalDate, Int, Int, String, String, String) -> Unit,
) {
    var title by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var year by remember { mutableIntStateOf(date.year) }
    var month by remember { mutableIntStateOf(date.monthValue) }
    var day by remember { mutableIntStateOf(date.dayOfMonth) }
    var hour by remember { mutableIntStateOf(20) }
    var minute by remember { mutableIntStateOf(0) }
    var type by remember { mutableStateOf(ReminderEntity.TYPE_SCHEDULE) }
    var localError by remember { mutableStateOf<String?>(null) }
    val maxDay = remember(year, month) { java.time.YearMonth.of(year, month).lengthOfMonth() }
    LaunchedEffect(maxDay) {
        if (day > maxDay) day = maxDay
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.surface) {
            Column(Modifier.fillMaxSize()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .statusBarsPadding()
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                    Text(
                        "新建日程",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f),
                    )
                    TextButton(
                        onClick = {
                            if (title.isBlank()) {
                                localError = "先写一个标题"
                            } else {
                                val selected = runCatching {
                                    LocalDate.of(year, month, day)
                                }.getOrElse { date }
                                onSave(selected, hour, minute, title.trim(), note.trim(), type)
                            }
                        },
                    ) { Text("保存") }
                }
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        ReminderEntity.TYPES.forEach { item ->
                            val selected = type == item
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(
                                        if (selected) MaterialTheme.colorScheme.primaryContainer
                                        else Color.Transparent
                                    )
                                    .clickable { type = item }
                                    .padding(vertical = 9.dp),
                                contentAlignment = Alignment.Center,
                            ) {
                                Text(
                                    text = reminderTypeLabel(item, LocalAppLanguage.current == "en"),
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = if (selected) MaterialTheme.colorScheme.onPrimaryContainer
                                    else TextSecondary,
                                )
                            }
                        }
                    }

                    OutlinedTextField(
                        value = title,
                        onValueChange = {
                            title = it
                            localError = null
                        },
                        label = { Text(reminderTitleHint(type, LocalAppLanguage.current == "en")) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = note,
                        onValueChange = { note = it },
                        label = { Text("备注") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )

                    Text("日期与时间", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(2.dp),
                    ) {
                        NumberWheel(
                            label = "年",
                            value = year,
                            range = (date.year - 1)..(date.year + 6),
                            modifier = Modifier.weight(1.35f),
                            onChange = { year = it },
                        )
                        NumberWheel(
                            label = "月",
                            value = month,
                            range = 1..12,
                            modifier = Modifier.weight(0.85f),
                            onChange = { month = it },
                        )
                        NumberWheel(
                            label = "日",
                            value = day,
                            range = 1..maxDay,
                            modifier = Modifier.weight(0.85f),
                            onChange = { day = it },
                        )
                        NumberWheel(
                            label = "时",
                            value = hour,
                            range = 0..23,
                            modifier = Modifier.weight(0.85f),
                            onChange = { hour = it },
                        )
                        NumberWheel(
                            label = "分",
                            value = minute,
                            range = 0..59,
                            modifier = Modifier.weight(0.85f),
                            onChange = { minute = it },
                        )
                    }
                    localError?.let {
                        Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
                    }
                    Spacer(Modifier.height(20.dp))
                }
            }
        }
    }
}

@Composable
private fun NumberWheel(
    label: String,
    value: Int,
    range: IntRange,
    modifier: Modifier = Modifier,
    onChange: (Int) -> Unit,
) {
    val state = rememberLazyListState(
        initialFirstVisibleItemIndex = (value - range.first).coerceIn(0, range.last - range.first)
    )
    LaunchedEffect(value) {
        state.scrollToItem((value - range.first).coerceIn(0, range.last - range.first))
    }
    LaunchedEffect(state.firstVisibleItemIndex) {
        val current = (range.first + state.firstVisibleItemIndex).coerceIn(range.first, range.last)
        if (current != value) onChange(current)
    }
    Column(modifier = modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondary)
        LazyColumn(
            state = state,
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp),
            contentPadding = PaddingValues(vertical = 58.dp),
        ) {
            items(range.last - range.first + 1) { index ->
                val number = range.first + index
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(32.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            if (number == value) MaterialTheme.colorScheme.primaryContainer
                            else Color.Transparent
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = number.toString(),
                        style = MaterialTheme.typography.bodyLarge,
                        color = if (number == value) MaterialTheme.colorScheme.onPrimaryContainer
                        else TextPrimary,
                    )
                }
            }
        }
    }
}

private fun reminderTypeEmoji(type: String): String = when (type) {
    ReminderEntity.TYPE_ANNIVERSARY -> "💜"
    ReminderEntity.TYPE_BIRTHDAY -> "🎂"
    ReminderEntity.TYPE_COUNTDOWN -> "⏳"
    else -> "📅"
}

internal fun reminderTypeLabel(type: String, english: Boolean = false): String {
    if (english) {
        return when (type) {
            ReminderEntity.TYPE_ANNIVERSARY -> "Anniversary"
            ReminderEntity.TYPE_BIRTHDAY -> "Birthday"
            ReminderEntity.TYPE_COUNTDOWN -> "Countdown"
            else -> "Schedule"
        }
    }
    return when (type) {
        ReminderEntity.TYPE_ANNIVERSARY -> "纪念日"
        ReminderEntity.TYPE_BIRTHDAY -> "生日"
        ReminderEntity.TYPE_COUNTDOWN -> "倒数日"
        else -> "日程"
    }
}

private fun reminderTitleHint(type: String, english: Boolean = false): String {
    if (english) {
        return when (type) {
            ReminderEntity.TYPE_ANNIVERSARY -> "Anniversary name (e.g. 100 days together)"
            ReminderEntity.TYPE_BIRTHDAY -> "Birthday person (e.g. Mom's birthday)"
            ReminderEntity.TYPE_COUNTDOWN -> "Countdown event (e.g. going home)"
            else -> "Reminder (e.g. memorize words together)"
        }
    }
    return when (type) {
        ReminderEntity.TYPE_ANNIVERSARY -> "纪念日名称（如：在一起 100 天）"
        ReminderEntity.TYPE_BIRTHDAY -> "生日主角（如：妈妈生日）"
        ReminderEntity.TYPE_COUNTDOWN -> "倒数事件（如：回家倒计时）"
        else -> "提醒内容（如：一起背单词）"
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarScheduleCards.kt`

> 日程流、新建日程与倒数文案。

````kotlin
package com.shineleong.toughmind.ui.screen.calendar

import android.app.TimePickerDialog
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Alarm
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Today
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.SectionTitle
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.util.ImagePreviewDialog
import com.shineleong.toughmind.util.ImageUtils
import kotlinx.coroutines.launch
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.GoldDark
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.SurfaceSubtle
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.LunarDateUtils
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

@Composable
internal fun ScheduleFeedCard(
    date: LocalDate,
    posts: List<SchedulePostEntity>,
    reminders: List<ReminderEntity>,
    selfName: String,
    partnerName: String,
    onAdd: (Int, Int, String, String) -> Unit,
) {
    var showAdd by remember { mutableStateOf(false) }
    var preview by remember { mutableStateOf<String?>(null) }
    var nowMillis by remember { mutableLongStateOf(System.currentTimeMillis()) }

    LaunchedEffect(date) {
        while (true) {
            nowMillis = System.currentTimeMillis()
            kotlinx.coroutines.delay(1_000)
        }
    }

    val nextReminder = remember(reminders, date, nowMillis) {
        if (date != LocalDate.now()) {
            null
        } else {
            reminders.mapNotNull { reminder ->
                val target = date
                    .atTime(reminder.timeMinutes / 60, reminder.timeMinutes % 60)
                    .atZone(java.time.ZoneId.systemDefault())
                    .toInstant()
                    .toEpochMilli()
                if (target > nowMillis) target to reminder else null
            }.minByOrNull { it.first }
        }
    }

    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "今天做了什么",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f),
                )
                IconButton(onClick = { showAdd = true }) {
                    Icon(Icons.Filled.Add, contentDescription = "添加日程")
                }
            }

            posts.forEach { post ->
                    val isSelf = post.authorId == CareRepository.SELF_ID
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = formatMinutes(post.timeMinutes),
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                            modifier = Modifier.width(48.dp),
                        )
                        Column(Modifier.weight(1f)) {
                            Text(
                                text = post.content,
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextPrimary,
                            )
                            Text(
                                text = if (isSelf) selfName else partnerName,
                                style = MaterialTheme.typography.labelSmall,
                                color = TextSecondary,
                            )
                        }
                        if (post.imageBase64.isNotBlank()) {
                            IconButton(onClick = { preview = post.imageBase64 }) {
                                Icon(
                                    Icons.Filled.Link,
                                    contentDescription = "查看照片",
                                    tint = MaterialTheme.colorScheme.primary,
                                )
                            }
                        }
                    }
                    HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.4f))
                }

            nextReminder?.let { (target, reminder) ->
                val remain = (target - nowMillis).coerceAtLeast(0L)
                val hours = remain / 3_600_000
                val minutes = (remain % 3_600_000) / 60_000
                val seconds = (remain % 60_000) / 1_000
                Text(
                    text = "距离「${reminder.title}」还有 %02d:%02d:%02d".format(hours, minutes, seconds),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Medium,
                )
            }
            }
        }

    if (showAdd) {
        AddScheduleDialog(
            onDismiss = { showAdd = false },
            onSave = { hour, minute, content, image ->
                onAdd(hour, minute, content, image)
                showAdd = false
            },
        )
    }

    preview?.let { ImagePreviewDialog(base64 = it, onDismiss = { preview = null }) }
}

@Composable
private fun AddScheduleDialog(
    onDismiss: () -> Unit,
    onSave: (Int, Int, String, String) -> Unit,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var content by remember { mutableStateOf("") }
    var imageBase64 by remember { mutableStateOf("") }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        if (uri != null) {
            scope.launch {
                val encoded = ImageUtils.encode(context, uri)
                if (encoded == null) Toast.makeText(context, "图片读取失败", Toast.LENGTH_SHORT).show()
                else imageBase64 = encoded
            }
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("记录一件事") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(
                    value = content,
                    onValueChange = { content = it },
                    label = { Text("例如：去图书馆看了会儿书") },
                    maxLines = 3,
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedButton(
                    onClick = { picker.launch("image/*") },
                    modifier = Modifier.height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                ) {
                    Text(if (imageBase64.isBlank()) "加照片" else "换照片")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                if (content.isNotBlank()) {
                    val now = java.time.LocalTime.now()
                    onSave(now.hour, now.minute, content.trim(), imageBase64)
                }
            }) { Text("保存") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } },
    )
}

internal fun countdownText(reminder: ReminderEntity): String? {
    if (reminder.type != ReminderEntity.TYPE_COUNTDOWN) return null
    return runCatching {
        val days = ChronoUnit.DAYS.between(LocalDate.now(), LocalDate.parse(reminder.date))
        when {
            days > 0 -> "还有 $days 天"
            days == 0L -> "就是今天"
            else -> "已过去 ${-days} 天"
        }
    }.getOrNull()
}

internal fun formatMinutes(minutes: Int): String {
    val safe = minutes.coerceIn(0, 24 * 60 - 1)
    return "%02d:%02d".format(safe / 60, safe % 60)
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarScreen.kt`

> 月视图日历、日期详情与打卡行。

````kotlin
package com.shineleong.toughmind.ui.screen.calendar

import android.app.TimePickerDialog
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Alarm
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Today
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.SectionTitle
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.util.ImagePreviewDialog
import com.shineleong.toughmind.util.ImageUtils
import kotlinx.coroutines.launch
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.GoldDark
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.SurfaceSubtle
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.LunarDateUtils
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

private fun monthFormatter(english: Boolean) = DateTimeFormatter.ofPattern(
    if (english) "MMMM yyyy" else "yyyy年M月",
    if (english) Locale.ENGLISH else Locale.CHINA,
)

private fun dayFormatter(english: Boolean) = DateTimeFormatter.ofPattern(
    if (english) "MMMM d, EEEE" else "M月d日 EEEE",
    if (english) Locale.ENGLISH else Locale.CHINA,
)

/** 月视图格子很窄，英文用短名；点开日期后在详情里显示完整名。 */
private val EN_CALENDAR_SHORT = mapOf(
    "元旦" to "New Year",
    "情人节" to "Valentine",
    "妇女节" to "Women's Day",
    "劳动节" to "Labour Day",
    "儿童节" to "Children's",
    "国庆节" to "National Day",
    "圣诞节" to "Christmas",
    "植树节" to "Arbor Day",
    "青年节" to "Youth Day",
    "教师节" to "Teachers",
    "春节" to "Spring Fest",
    "元宵" to "Lantern",
    "龙抬头" to "Longtaitou",
    "端午" to "Dragon Boat",
    "七夕" to "Qixi",
    "中元" to "Zhongyuan",
    "中秋" to "Mid-Autumn",
    "重阳" to "Chongyang",
    "寒衣" to "Winter Wear",
    "下元" to "Xiayuan",
    "腊八" to "Laba",
    "小年" to "Little Yr",
    "除夕" to "NY Eve",
    "小寒" to "Minor Cold",
    "大寒" to "Major Cold",
    "立春" to "Spring",
    "雨水" to "Rain Water",
    "惊蛰" to "Insects",
    "春分" to "Equinox",
    "清明" to "Qingming",
    "谷雨" to "Grain Rain",
    "立夏" to "Summer",
    "小满" to "Grain Buds",
    "芒种" to "Grain Ear",
    "夏至" to "Solstice",
    "小暑" to "Minor Heat",
    "大暑" to "Major Heat",
    "立秋" to "Autumn",
    "处暑" to "End Heat",
    "白露" to "White Dew",
    "秋分" to "Equinox",
    "寒露" to "Cold Dew",
    "霜降" to "Frost",
    "立冬" to "Winter",
    "小雪" to "Minor Snow",
    "大雪" to "Major Snow",
    "冬至" to "Solstice",
)

private fun englishShortLabel(name: String): String = EN_CALENDAR_SHORT[name] ?: name

/**
 * 日程页：月视图里双方都打卡的日期显示为红色；
 * 点击日期可以分别为"我 / TA"打卡，并为该日期添加定时提醒。
 */
@Composable
fun CalendarScreen(
    addRequest: Int = 0,
    onAddRequestConsumed: () -> Unit = {},
    viewModel: CalendarViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val yearMonth by viewModel.yearMonth.collectAsStateWithLifecycle()
    val monthCheckIns by viewModel.monthCheckIns.collectAsStateWithLifecycle()
    val monthReminders by viewModel.monthReminders.collectAsStateWithLifecycle()
    val todayCheckIns by viewModel.todayCheckIns.collectAsStateWithLifecycle()
    val todayReminders by viewModel.todayReminders.collectAsStateWithLifecycle()
    val selectedDate by viewModel.selectedDate.collectAsStateWithLifecycle()
    val schedulePosts by viewModel.selectedSchedulePosts.collectAsStateWithLifecycle()
    val companion by viewModel.companion.collectAsStateWithLifecycle()
    val selfName by viewModel.selfName.collectAsStateWithLifecycle()
    val message = viewModel.message
    val context = LocalContext.current
    var showQuickAdd by remember { mutableStateOf(false) }

    LaunchedEffect(addRequest) {
        if (addRequest > 0) {
            showQuickAdd = true
            onAddRequestConsumed()
        }
    }

    LaunchedEffect(selectedDate, yearMonth) {
        viewModel.refreshSchedule()
    }

    LaunchedEffect(message) {
        message?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            viewModel.clearMessage()
        }
    }

    val checkInMap = remember(monthCheckIns) {
        monthCheckIns.groupBy { LocalDate.parse(it.date) }
    }
    val reminderMap = remember(monthReminders) {
        monthReminders.groupBy { LocalDate.parse(it.date) }
    }
    val today = LocalDate.now()
    val partnerName = companion.nickname.ifBlank { "TA" }

    val bothDays = remember(monthCheckIns) {
        monthCheckIns.groupBy { it.date }.count { (_, records) ->
            records.any { it.personId == CareRepository.SELF_ID } &&
                records.any { it.personId == CareRepository.PARTNER_ID }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 10.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        CalendarHeader(
            yearMonth = yearMonth,
            onPrevious = viewModel::previousMonth,
            onNext = viewModel::nextMonth,
            onToday = viewModel::goToToday,
        )

        MonthGrid(
            yearMonth = yearMonth,
            reminderMap = reminderMap,
            today = today,
            onSelectDate = viewModel::selectDate,
        )

        val upcoming = monthReminders
            .filter { it.date >= today.toString() }
            .sortedWith(compareBy({ it.date }, { it.timeMinutes }))
            .take(4)
        if (upcoming.isNotEmpty()) {
            UpcomingRemindersCard(
                reminders = upcoming,
                onOpenDate = { reminder -> viewModel.selectDate(LocalDate.parse(reminder.date)) },
            )
        }

        ScheduleFeedCard(
            date = selectedDate ?: today,
            posts = schedulePosts,
            reminders = if ((selectedDate ?: today) == today) todayReminders else reminderMap[selectedDate ?: today].orEmpty(),
            selfName = selfName.ifBlank { "我" },
            partnerName = partnerName,
            onAdd = { hour, minute, content, image ->
                viewModel.addSchedule(selectedDate ?: today, hour, minute, content, image)
            },
        )

        Spacer(Modifier.height(8.dp))
    }

    if (showQuickAdd) {
        AddReminderDialog(
            date = selectedDate ?: today,
            onDismiss = { showQuickAdd = false },
            onSave = { selectedDateValue, hour, minute, title, note, type ->
                viewModel.addReminder(selectedDateValue, hour, minute, title, note, type)
                showQuickAdd = false
            },
        )
    }

    selectedDate?.let { date ->
        DayDetailSheet(
            date = date,
            reminders = if (date == today) todayReminders else reminderMap[date].orEmpty(),
            onDismiss = viewModel::dismissSelectedDate,
            onAddReminder = { selectedDateValue, hour, minute, title, note, type ->
                viewModel.addReminder(selectedDateValue, hour, minute, title, note, type)
            },
            onToggleReminder = viewModel::setReminderEnabled,
            onDeleteReminder = viewModel::deleteReminder,
        )
    }
}

@Composable
private fun CalendarHeader(
    yearMonth: YearMonth,
    onPrevious: () -> Unit,
    onNext: () -> Unit,
    onToday: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(
                text = yearMonth.format(monthFormatter(LocalAppLanguage.current == "en")),
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
        }
        IconButton(onClick = onPrevious) {
            Icon(Icons.Filled.ChevronLeft, contentDescription = "上个月")
        }
        IconButton(onClick = onNext) {
            Icon(Icons.Filled.ChevronRight, contentDescription = "下个月")
        }
        IconButton(onClick = onToday) {
            Icon(Icons.Filled.Today, contentDescription = "回到今天")
        }
    }
}

@Composable
private fun MonthGrid(
    yearMonth: YearMonth,
    reminderMap: Map<LocalDate, List<ReminderEntity>>,
    today: LocalDate,
    onSelectDate: (LocalDate) -> Unit,
) {
    val weekLabels = if (LocalAppLanguage.current == "en") {
        listOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    } else {
        listOf("一", "二", "三", "四", "五", "六", "日")
    }
    val leading = yearMonth.atDay(1).dayOfWeek.value - 1
    val cells = buildList<LocalDate?> {
        repeat(leading) { add(null) }
        for (day in 1..yearMonth.lengthOfMonth()) add(yearMonth.atDay(day))
        while (size % 7 != 0) add(null)
    }

    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Row(Modifier.fillMaxWidth()) {
            weekLabels.forEach { label ->
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.weight(1f),
                )
            }
        }
        cells.chunked(7).forEach { week ->
            Row(Modifier.fillMaxWidth()) {
                week.forEach { date ->
                    if (date == null) {
                        Spacer(Modifier.weight(1f).aspectRatio(1f))
                    } else {
                        DayCell(
                            date = date,
                            reminderCount = reminderMap[date].orEmpty().size,
                            isToday = date == today,
                            modifier = Modifier.weight(1f),
                            onClick = { onSelectDate(date) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DayCell(
    date: LocalDate,
    reminderCount: Int,
    isToday: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(12.dp)
    Box(
        modifier = modifier
            .padding(2.dp)
            .aspectRatio(1f)
            .clip(shape)
            .then(if (isToday) Modifier.border(1.5.dp, MaterialTheme.colorScheme.primary, shape) else Modifier)
            .clickable(onClick = onClick),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(top = 5.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = date.dayOfMonth.toString(),
                style = MaterialTheme.typography.bodySmall,
                fontWeight = if (isToday) FontWeight.Bold else FontWeight.Medium,
                color = TextPrimary,
            )
            val lunar = remember(date) { LunarDateUtils.lunarLabel(date) }
            val special = remember(date) { LunarDateUtils.festivalOrTerm(date) }
            val compact = LocalDensity.current.fontScale > 1.15f
            if (LocalAppLanguage.current == "en") {
                if (special != null) {
                    Text(
                        text = englishShortLabel(special),
                        fontSize = if (compact) 7.sp else 8.sp,
                        color = MaterialTheme.colorScheme.primary,
                        maxLines = 1,
                    )
                }
            } else {
                Text(
                    text = special ?: lunar,
                    fontSize = 9.sp,
                    color = if (special != null) MaterialTheme.colorScheme.primary else TextSecondary,
                    maxLines = 1,
                )
            }
        }
        if (reminderCount > 0) {
            Icon(
                Icons.Filled.Alarm,
                contentDescription = "有 $reminderCount 条提醒",
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(3.dp)
                    .size(9.dp),
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DayDetailSheet(
    date: LocalDate,
    reminders: List<ReminderEntity>,
    onDismiss: () -> Unit,
    onAddReminder: (LocalDate, Int, Int, String, String, String) -> Unit,
    onToggleReminder: (ReminderEntity, Boolean) -> Unit,
    onDeleteReminder: (ReminderEntity) -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var showAddDialog by remember { mutableStateOf(false) }
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = SurfaceWhite,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(
                        text = date.format(dayFormatter(LocalAppLanguage.current == "en")),
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                    )
                    val lunar = LunarDateUtils.lunarLabel(date)
                    val special = LunarDateUtils.festivalOrTerm(date)
                    if (LocalAppLanguage.current == "en") {
                        if (special != null) {
                            Text(
                                text = special,
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary,
                            )
                        }
                    } else {
                        Text(
                            text = listOfNotNull(lunar, special).joinToString(" · "),
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                    }
                }
            }


            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.5f))

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "当天提醒",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
                IconButton(onClick = { showAddDialog = true }) {
                    Icon(Icons.Filled.Add, contentDescription = "添加提醒")
                }
            }

            reminders.forEach { reminder ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                        Column(Modifier.weight(1f)) {
                            Text(
                                text = "${formatMinutes(reminder.timeMinutes)}  ${reminder.title}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Medium,
                                color = TextPrimary,
                            )
                            Text(
                                text = buildString {
                                    append(reminderTypeLabel(reminder.type, LocalAppLanguage.current == "en"))
                                    countdownText(reminder)?.let { append(" · ").append(it) }
                                    if (reminder.note.isNotBlank()) {
                                        append(" · ").append(reminder.note)
                                    }
                                },
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary,
                            )
                        }
                        Switch(
                            checked = reminder.enabled,
                            onCheckedChange = { onToggleReminder(reminder, it) },
                        )
                        IconButton(onClick = { onDeleteReminder(reminder) }) {
                            Icon(
                                Icons.Filled.Delete,
                                contentDescription = "删除提醒",
                                tint = TextSecondary,
                            )
                        }
                    }
                }
        }
    }

    if (showAddDialog) {
        AddReminderDialog(
            date = date,
            onDismiss = { showAddDialog = false },
            onSave = { selectedDate, hour, minute, title, note, type ->
                onAddReminder(selectedDate, hour, minute, title, note, type)
                showAddDialog = false
            },
        )
    }
}

@Composable
private fun CheckInSheetRow(
    name: String,
    checked: Boolean,
    accent: Color,
    onToggle: (Boolean) -> Unit,
) {
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = if (checked) accent.copy(alpha = 0.14f) else SurfaceSubtle,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Avatar(nickname = name, size = 34.dp)
            Column(Modifier.weight(1f)) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )
                Text(
                    text = if (checked) "今天已打卡" else "今天还没有打卡",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (checked) accent else TextSecondary,
                )
            }
            if (checked) {
                OutlinedButton(
                    onClick = { onToggle(false) },
                    modifier = Modifier.height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                ) { Text("取消打卡") }
            } else {
                Button(
                    onClick = { onToggle(true) },
                    modifier = Modifier.height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                ) { Text("打卡") }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/calendar/CalendarViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.calendar

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.CheckInRepository
import com.shineleong.toughmind.data.repository.CompanionRepository
import com.shineleong.toughmind.data.repository.ReminderRepository
import com.shineleong.toughmind.data.repository.SchedulePostRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.YearMonth

@OptIn(ExperimentalCoroutinesApi::class)
class CalendarViewModel(
    private val checkInRepository: CheckInRepository,
    private val reminderRepository: ReminderRepository,
    private val schedulePostRepository: SchedulePostRepository,
    companionRepository: CompanionRepository,
    preferences: Preferences,
    private val careSyncRepository: CareSyncRepository,
    careRepository: CareRepository,
) : ViewModel() {

    private val _yearMonth = MutableStateFlow(YearMonth.now())
    val yearMonth: StateFlow<YearMonth> = _yearMonth.asStateFlow()

    private val _selectedDate = MutableStateFlow<LocalDate?>(null)
    val selectedDate: StateFlow<LocalDate?> = _selectedDate.asStateFlow()

    val groupActive: StateFlow<Boolean> = careSyncRepository.groupActive

    val monthCheckIns: StateFlow<List<CheckInEntity>> = _yearMonth
        .flatMapLatest { month ->
            checkInRepository.observeBetween(
                start = month.atDay(1).toString(),
                end = month.atEndOfMonth().toString(),
            )
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val monthReminders: StateFlow<List<ReminderEntity>> = _yearMonth
        .flatMapLatest { month ->
            reminderRepository.observeBetween(
                start = month.atDay(1).toString(),
                end = month.atEndOfMonth().toString(),
            )
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val todayCheckIns: StateFlow<List<CheckInEntity>> = checkInRepository
        .observeDate(LocalDate.now().toString())
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val todayReminders: StateFlow<List<ReminderEntity>> = reminderRepository
        .observeDate(LocalDate.now().toString())
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val selectedSchedulePosts: StateFlow<List<SchedulePostEntity>> = _selectedDate
        .flatMapLatest { date ->
            schedulePostRepository.observeDate((date ?: LocalDate.now()).toString())
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init {
        viewModelScope.launch {
            groupActive.collectLatest { active ->
                if (active) {
                    val month = _yearMonth.value
                    careSyncRepository.syncSchedule(month.atDay(1), month.atEndOfMonth())
                }
            }
        }
    }

    val companion: StateFlow<CarePartner> = careRepository.companion

    val selfName: StateFlow<String> = preferences.nickname
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "我")

    var reminderError by mutableStateOf<String?>(null)
        private set
    var message by mutableStateOf<String?>(null)
        private set

    init {
        viewModelScope.launch {
            combine(_yearMonth, careSyncRepository.groupActive) { month, active ->
                month to active
            }.collectLatest { (month, active) ->
                if (active) careSyncRepository.syncMonth(month)
            }
        }
    }

    fun previousMonth() {
        _yearMonth.value = _yearMonth.value.minusMonths(1)
    }

    fun nextMonth() {
        _yearMonth.value = _yearMonth.value.plusMonths(1)
    }

    fun goToToday() {
        _yearMonth.value = YearMonth.now()
        _selectedDate.value = LocalDate.now()
    }

    fun selectDate(date: LocalDate) {
        _selectedDate.value = date
    }

    fun dismissSelectedDate() {
        _selectedDate.value = null
    }

    fun toggleCheckIn(date: LocalDate, personId: String, checked: Boolean) {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                if (personId == CareRepository.PARTNER_ID) {
                    message = "需要 TA 在自己的念安里打卡，双方日程才会一起变红"
                    return@launch
                }
                val result = careSyncRepository.toggleSelfCheckIn(date, checked)
                if (result.isFailure) {
                    checkInRepository.toggle(date.toString(), personId, checked)
                    message = "云端暂未同步，已先记录在本机"
                }
            } else {
                checkInRepository.toggle(date.toString(), personId, checked)
            }
        }
    }

    fun addReminder(
        date: LocalDate,
        hour: Int,
        minute: Int,
        title: String,
        note: String,
        type: String = ReminderEntity.TYPE_SCHEDULE,
    ) {
        if (title.isBlank()) {
            reminderError = "给提醒起个名字吧"
            return
        }
        reminderError = null
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                val result = careSyncRepository.addRemoteReminder(
                    date, hour, minute, title, note, type,
                )
                if (result.isFailure) {
                    reminderRepository.add(
                        date = date.toString(),
                        timeMinutes = hour * 60 + minute,
                        title = title.trim(),
                        note = note.trim(),
                        type = type,
                    )
                    reminderError = "云端同步失败，已保存到本机"
                }
            } else {
                reminderRepository.add(
                    date = date.toString(),
                    timeMinutes = hour * 60 + minute,
                    title = title.trim(),
                    note = note.trim(),
                    type = type,
                )
            }
        }
    }

    fun addSchedule(
        date: LocalDate,
        hour: Int,
        minute: Int,
        content: String,
        imageBase64: String,
    ) {
        if (content.isBlank()) {
            reminderError = "写点什么再分享吧"
            return
        }
        reminderError = null
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                val result = careSyncRepository.addRemoteSchedule(
                    date, hour, minute, content, imageBase64,
                )
                if (result.isFailure) {
                    schedulePostRepository.add(
                        date = date.toString(),
                        timeMinutes = hour * 60 + minute,
                        content = content.trim(),
                        imageBase64 = imageBase64,
                        authorId = CareRepository.SELF_ID,
                    )
                    reminderError = "云端同步失败，已保存到本机"
                }
            } else {
                schedulePostRepository.add(
                    date = date.toString(),
                    timeMinutes = hour * 60 + minute,
                    content = content.trim(),
                    imageBase64 = imageBase64,
                    authorId = CareRepository.SELF_ID,
                )
            }
        }
    }

    fun refreshSchedule() {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                val month = _yearMonth.value
                careSyncRepository.syncSchedule(month.atDay(1), month.atEndOfMonth())
            }
        }
    }

    fun clearReminderError() {
        reminderError = null
    }

    fun clearMessage() {
        message = null
    }

    fun setReminderEnabled(reminder: ReminderEntity, enabled: Boolean) {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value && reminder.remoteId > 0) {
                careSyncRepository.updateRemoteReminder(reminder, enabled)
            }
            reminderRepository.setEnabled(reminder, enabled)
        }
    }

    fun deleteReminder(reminder: ReminderEntity) {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value && reminder.remoteId > 0) {
                careSyncRepository.deleteRemoteReminder(reminder)
            }
            reminderRepository.delete(reminder)
        }
    }
}
````

<a id="s04-2"></a>

## 步骤 04.2 · 打卡任务

双方打卡点、完成状态与提醒对方。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/checkin/CheckInScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/checkin/CheckInViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/checkin/CheckInScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.checkin

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Checkbox
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.screen.chat.DanmakuWall
import com.shineleong.toughmind.ui.screen.chat.WallEntry
import com.shineleong.toughmind.ui.screen.chat.buildTimeline
import com.shineleong.toughmind.ui.screen.chat.buildWallEntries
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.VoiceRecorder
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun CheckInScreen(
    addRequest: Int = 0,
    onAddRequestConsumed: () -> Unit = {},
    showTasks: Boolean = true,
    showWall: Boolean = true,
    viewModel: CheckInViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val tasks by viewModel.tasks.collectAsStateWithLifecycle()
    val self by viewModel.self.collectAsStateWithLifecycle()
    val partner by viewModel.partner.collectAsStateWithLifecycle()
    val message by viewModel.message.collectAsStateWithLifecycle()
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    val posts by viewModel.posts.collectAsStateWithLifecycle()
    var draft by remember { mutableStateOf("") }
    val wallEntries = remember(messages, posts, partner) {
        buildWallEntries(
            timeline = buildTimeline(messages, posts),
            partnerName = partner?.name,
        )
    }
    var showAdd by remember { mutableStateOf(false) }
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        viewModel.refreshTasks()
    }

    LaunchedEffect(addRequest) {
        if (addRequest > 0) {
            showAdd = true
            onAddRequestConsumed()
        }
    }

    LaunchedEffect(message) {
        message?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            viewModel.consumeMessage()
        }
    }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        if (showWall) {
            CheckInWallCard(
                entries = wallEntries,
                draft = draft,
                onDraftChange = { draft = it },
                onSend = {
                    viewModel.sendMessage(draft)
                    draft = ""
                },
                onSendVoice = viewModel::sendVoice,
            )
        }

        if (showTasks) {
            if (tasks.isEmpty()) {
                TechCard(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = "还没有今天的任务，点右上角加号写下要一起完成的事。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary,
                    )
                }
            } else {
                tasks.forEach { task ->
                    TaskBox(
                        task = task,
                        partnerIsDemo = partner?.isDemo == true,
                        onSelfDone = { viewModel.setSelfDone(task, it) },
                        onRemind = viewModel::remindPartner,
                        onPartnerDoneDemo = { viewModel.setPartnerDoneDemo(task) },
                    )
                }
            }
        }
        Spacer(Modifier.height(8.dp))
    }

    if (showAdd) {
        AddTaskDialog(
            onDismiss = { showAdd = false },
            onSave = { title ->
                viewModel.addTask(title)
                showAdd = false
            },
        )
    }

}

@Composable
private fun TaskBox(
    task: CheckInTaskEntity,
    partnerIsDemo: Boolean,
    onSelfDone: (Boolean) -> Unit,
    onRemind: () -> Unit,
    onPartnerDoneDemo: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val bothDone = task.selfDone && task.partnerDone
    TechCard(modifier = modifier.fillMaxWidth()) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Checkbox(
                checked = task.selfDone,
                onCheckedChange = { onSelfDone(it) },
                enabled = !task.selfDone,
            )
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(
                    text = task.title,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary,
                )
                Text(
                    text = when {
                        bothDone -> "该项已完成"
                        task.selfDone -> "你已完成，TA 还没完成"
                        task.partnerDone -> "TA 已完成，等你了"
                        else -> "待完成"
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = if (bothDone) CareRed else TextSecondary,
                )
            }
        }
        if (task.selfDone && !task.partnerDone) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                TextButton(onClick = onRemind) { Text("提醒对方完成") }
                if (partnerIsDemo) {
                    TextButton(onClick = onPartnerDoneDemo) { Text("演示：TA 已完成") }
                }
            }
        }
    }
}

@Composable
private fun AddTaskDialog(
    onDismiss: () -> Unit,
    onSave: (String) -> Unit,
) {
    var title by remember { mutableStateOf("") }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加任务") },
        text = {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("例如：背 30 个单词 / 喝 8 杯水") },
                modifier = Modifier.fillMaxWidth(),
            )
        },
        confirmButton = {
            TextButton(onClick = { if (title.isNotBlank()) onSave(title.trim()) }) {
                Text("保存")
            }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } },
    )
}

@Composable
private fun CheckInWallCard(
    entries: List<WallEntry>,
    draft: String,
    onDraftChange: (String) -> Unit,
    onSend: () -> Unit,
    onSendVoice: (String, Long) -> Unit,
) {
    val context = LocalContext.current
    val recorder = remember { VoiceRecorder(context) }
    var recording by remember { mutableStateOf(false) }
    var recordSeconds by remember { mutableStateOf(0) }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        if (granted) {
            recording = recorder.start()
            if (!recording) {
                Toast.makeText(context, "没有可用的麦克风", Toast.LENGTH_SHORT).show()
            }
        }
    }
    LaunchedEffect(recording) {
        if (!recording) return@LaunchedEffect
        recordSeconds = 0
        while (true) {
            delay(1_000L)
            recordSeconds++
        }
    }
    DisposableEffect(Unit) {
        onDispose { recorder.cancel() }
    }

    fun toggleRecording() {
        if (recording) {
            recording = false
            recorder.stop()?.let { (path, duration) -> onSendVoice(path, duration) }
        } else {
            val granted = ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO,
            ) == PackageManager.PERMISSION_GRANTED
            if (granted) {
                recording = recorder.start()
                if (!recording) {
                    Toast.makeText(context, "没有可用的麦克风", Toast.LENGTH_SHORT).show()
                }
            } else {
                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }

    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "留言墙",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                )
                Spacer(Modifier.weight(1f))
                Text(
                    "${entries.size} 条",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(164.dp)
                    .clip(RoundedCornerShape(16.dp)),
            ) {
                DanmakuWall(
                    entries = entries,
                    modifier = Modifier.fillMaxSize(),
                )
            }
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                IconButton(onClick = ::toggleRecording) {
                    Icon(
                        imageVector = if (recording) Icons.Filled.Stop else Icons.Filled.Mic,
                        contentDescription = if (recording) "停止并发送语音" else "录制语音留言",
                        tint = if (recording) {
                            MaterialTheme.colorScheme.error
                        } else {
                            MaterialTheme.colorScheme.primary
                        },
                    )
                }
                if (recording) {
                    Row(
                        modifier = Modifier.weight(1f),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(MaterialTheme.colorScheme.error),
                        )
                        Text(
                            text = "正在录音 %d:%02d · 点麦克风发送".format(
                                recordSeconds / 60,
                                recordSeconds % 60,
                            ),
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                    }
                } else {
                    OutlinedTextField(
                        value = draft,
                        onValueChange = onDraftChange,
                        placeholder = { Text("给 TA 留一句话…") },
                        maxLines = 3,
                        modifier = Modifier.weight(1f),
                    )
                }
                IconButton(onClick = onSend, enabled = draft.isNotBlank() && !recording) {
                    Icon(
                        Icons.AutoMirrored.Filled.Send,
                        contentDescription = "发送留言",
                        tint = if (draft.isNotBlank()) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            TextSecondary
                        },
                    )
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/checkin/CheckInViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.checkin

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.ChatMessageRepository
import com.shineleong.toughmind.data.repository.CheckInRepository
import com.shineleong.toughmind.data.repository.CheckInTaskRepository
import com.shineleong.toughmind.data.repository.CompanionRepository
import com.shineleong.toughmind.data.repository.SchedulePostRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.LocalDate

class CheckInViewModel(
    private val checkInTaskRepository: CheckInTaskRepository,
    private val checkInRepository: CheckInRepository,
    private val careRepository: CareRepository,
    private val careSyncRepository: CareSyncRepository,
    companionRepository: CompanionRepository,
    private val preferences: Preferences,
    private val chatMessageRepository: ChatMessageRepository,
    schedulePostRepository: SchedulePostRepository,
) : ViewModel() {

    val today: LocalDate = LocalDate.now()
    val self = careRepository.selfPresence.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
    val partner = careRepository.partnerPresence.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
    val companion = companionRepository.companion.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        com.shineleong.toughmind.data.model.CarePartner(),
    )

    val tasks: StateFlow<List<CheckInTaskEntity>> = checkInTaskRepository
        .observeDate(today.toString())
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    /** 留言墙与地图对话共用同一份留言 / 记录数据。 */
    val messages = chatMessageRepository.messages
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
    val posts = schedulePostRepository.observeDate(today.toString())
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val moodEmoji: StateFlow<String> = preferences.moodEmoji
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "🙂")
    val moodMessage: StateFlow<String> = preferences.moodMessage
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "")

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message

    init {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                careSyncRepository.syncTasks(today, today)
            }
        }
    }

    fun refreshTasks() {
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                careSyncRepository.syncTasks(today, today)
            }
        }
    }

    fun addTask(title: String, imageBase64: String = "") {
        if (title.isBlank()) {
            _message.value = "先写一条任务吧"
            return
        }
        viewModelScope.launch {
            if (careSyncRepository.groupActive.value) {
                val result = careSyncRepository.addRemoteTask(today, title.trim(), imageBase64)
                if (result.isFailure) {
                    checkInTaskRepository.add(today.toString(), title.trim(), imageBase64)
                    _message.value = "云端同步失败，已先记录在本机"
                }
            } else {
                checkInTaskRepository.add(today.toString(), title.trim(), imageBase64)
            }
        }
    }

    fun setSelfDone(task: CheckInTaskEntity, done: Boolean) {
        viewModelScope.launch {
            checkInTaskRepository.setSelfDone(task, done)
            if (done && careSyncRepository.groupActive.value && task.remoteId > 0) {
                careSyncRepository.toggleRemoteTask(task.remoteId, true)
            }
        }
    }

    fun remindPartner() {
        viewModelScope.launch {
            careSyncRepository.sendNudge("今天的任务还差一点，记得完成哦。")
            _message.value = "已提醒 TA 完成任务"
        }
    }

    fun setPartnerDoneDemo(task: CheckInTaskEntity) {
        viewModelScope.launch {
            checkInTaskRepository.setPartnerDone(task, true)
        }
    }

    /** 从打卡页的留言墙发一条文字留言；优先走云端，失败时留在本机。 */
    fun sendMessage(text: String) {
        val trimmed = text.trim()
        if (trimmed.isBlank()) return
        viewModelScope.launch {
            val remote = careSyncRepository.sendChatMessage(trimmed).getOrNull()
            if (remote != null) {
                chatMessageRepository.insertRemote(
                    remoteId = remote.id,
                    text = remote.message,
                    fromSelf = true,
                    senderName = remote.fromNickname,
                    createdAt = remote.createdAt,
                )
            } else {
                chatMessageRepository.send(text = trimmed)
            }
        }
    }

    /** 语音留言：录制在应用私有目录，先保存到本机留言；文本/图片/语音共用同一条墙。 */
    fun sendVoice(path: String, durationMs: Long) {
        if (path.isBlank()) return
        viewModelScope.launch {
            chatMessageRepository.send(
                audioPath = path,
                audioDurationMs = durationMs,
            )
        }
    }

    fun consumeMessage() {
        _message.value = null
    }
}
````

<a id="s04-3"></a>

## 步骤 04.3 · 历史与出行

动态记录页与出行页入口。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/history/HistoryScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/history/HistoryViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/trip/TripScreen.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/history/HistoryScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.history

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import com.shineleong.toughmind.data.model.FatigueLevel
import com.shineleong.toughmind.data.model.MedicalType
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.formatDate
import com.shineleong.toughmind.ui.component.formatDateTime
import com.shineleong.toughmind.ui.component.formatTime
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun HistoryScreen(
    viewModel: HistoryViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val events by viewModel.events.collectAsStateWithLifecycle()

    Column(Modifier.fillMaxSize()) {
        if (events.isEmpty()) {
            Text(
                text = "暂无动态记录",
                color = TextSecondary,
                modifier = Modifier.padding(16.dp),
            )
        } else {
            val grouped = events.groupBy { formatDate(it.timestamp) }
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                grouped.forEach { (date, list) ->
                    item(key = "header_$date") {
                        Text(
                            text = date,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.secondary,
                            modifier = Modifier.padding(top = 8.dp, bottom = 4.dp),
                        )
                    }
                    items(list, key = { it.id }) { event ->
                        EventItem(event = event, onClick = { viewModel.select(event) })
                    }
                }
            }
        }
    }

    viewModel.selectedEvent?.let { event ->
        EventDetailDialog(event = event, onDismiss = viewModel::dismissDetail)
    }
}

@Composable
private fun EventItem(event: EventEntity, onClick: () -> Unit) {
    val level = FatigueLevel.fromCode(event.level)
    TechCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        accent = level.toColor().copy(alpha = 0.4f),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column {
                Text(
                    text = level.label,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = level.toColor(),
                )
                Text(
                    text = typeLabel(event),
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }
            Text(
                text = formatTime(event.timestamp),
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
            )
        }
    }
}

@Composable
private fun EventDetailDialog(event: EventEntity, onDismiss: () -> Unit) {
    val level = FatigueLevel.fromCode(event.level)
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("关闭") }
        },
        title = { Text("事件详情") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                DetailRow("类型", typeLabel(event))
                DetailRow("疲劳等级", level.label)
                DetailRow("疲劳分数", "%.1f".format(event.fatigueScore))
                DetailRow("PERCLOS", "%.2f".format(event.perclos))
                DetailRow("哈欠次数", "${event.yawnTotal}")
                DetailRow("分心状态", if (event.headDistracted) "是" else "否")
                DetailRow("经度", "%.5f".format(event.lon))
                DetailRow("纬度", "%.5f".format(event.lat))
                DetailRow("车速", "${event.speed.toInt()} km/h")
                DetailRow("车内温度", "${event.temperature.toInt()} ℃")
                if (event.medicalLevel >= 1) {
                    DetailRow("医学类型", MedicalType.fromCode(event.medicalType).label)
                }
                if (event.message.isNotBlank()) {
                    DetailRow("告警信息", event.message)
                }
                DetailRow("时间", formatDateTime(event.timestamp))
            }
        },
    )
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth()) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f),
        )
        Text(text = value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
    }
    HorizontalDivider()
}

private fun typeLabel(event: EventEntity): String = when (event.type) {
    "alarm" -> "关心提醒"
    "medical" -> "紧急求助"
    else -> "状态记录"
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/history/HistoryViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.history

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import com.shineleong.toughmind.data.repository.EventRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.stateIn

@OptIn(ExperimentalCoroutinesApi::class)
class HistoryViewModel(
    eventRepository: EventRepository,
    preferences: Preferences,
) : ViewModel() {

    val events: StateFlow<List<EventEntity>> = preferences.currentDeviceId
        .flatMapLatest { id ->
            if (id.isBlank()) flowOf(emptyList())
            else eventRepository.observeEvents(id, 0L, Long.MAX_VALUE)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    var selectedEvent by mutableStateOf<EventEntity?>(null)
        private set

    fun select(event: EventEntity) {
        selectedEvent = event
    }

    fun dismissDetail() {
        selectedEvent = null
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/trip/TripScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.trip

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.shineleong.toughmind.ui.screen.calendar.CalendarScreen
import com.shineleong.toughmind.ui.screen.checkin.CheckInScreen

/** 「行程」= 日历 + 打卡任务；留言墙在「亲友」里。 */
@Composable
fun TripScreen(
    calendarAddRequest: Int,
    onCalendarAddConsumed: () -> Unit,
    taskAddRequest: Int,
    onTaskAddConsumed: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var tab by rememberSaveable { mutableIntStateOf(0) }
    Column(modifier = modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = tab, containerColor = MaterialTheme.colorScheme.surface) {
            listOf("日历", "打卡任务").forEachIndexed { index, label ->
                Tab(
                    selected = tab == index,
                    onClick = { tab = index },
                    text = { Text(label) },
                )
            }
        }
        Box(modifier = Modifier.weight(1f)) {
            when (tab) {
                0 -> CalendarScreen(
                    addRequest = calendarAddRequest,
                    onAddRequestConsumed = onCalendarAddConsumed,
                )
                else -> CheckInScreen(
                    addRequest = taskAddRequest,
                    onAddRequestConsumed = onTaskAddConsumed,
                    showWall = false,
                    showTasks = true,
                )
            }
        }
    }
}
````

---

返回索引：[README.md](README.md)
