# 05 · 亲友、关心与留言

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

亲友页合并关心与留言墙：亲属卡横向滑动、天气与位置、关心建议、情话、共同宠物入口，以及文字/语音留言与弹幕墙。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 关心页](#s05-1) | `CareScreen` 组装亲属卡片轮播、天气页、宠物卡、关心建议与情话角落。 | 4 |
| [2. 亲友设置与亲友列表](#s05-2) | 称呼/关系独立成页；亲友列表作为入口。 | 4 |
| [3. 留言与弹幕墙](#s05-3) | 文字与语音留言、消息气泡与弹幕展示。 | 4 |
| [4. 个人中心、设置与关于](#s05-4) | 账号、头像、主题、语言、朗读、关怀模式与关于页。 | 4 |
| [5. 关心建议与浪漫清单](#s05-5) | 建议卡片与 100 条浪漫清单的抽取、完成进度。 | 4 |

本篇共 **5 个步骤 / 20 个文件**，按表格顺序写入即可还原对应代码。

<a id="s05-1"></a>

## 步骤 05.1 · 关心页

`CareScreen` 组装亲属卡片轮播、天气页、宠物卡、关心建议与情话角落。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareAdviceCard.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CarePetCard.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareAdviceCard.kt`

> 关心建议、驾驶关怀与情话角落卡片。

````kotlin
package com.shineleong.toughmind.ui.screen.care

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.NightlightRound
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.component.translateText
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.model.AdviceKind
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlRhythm
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.data.model.RelativeSummary
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.ReadAloudButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.statusEnglish
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.ceil

@Composable
internal fun DriverCareCard(
    partnerName: String,
    driver: com.shineleong.toughmind.data.model.DriverState,
    onOpenMap: () -> Unit,
) {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.DirectionsCar,
                    contentDescription = null,
                    tint = Gold,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    text = "驾驶安全（设备功能之一）",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
                TextButton(onClick = onOpenMap) { Text("看位置") }
            }
            Text(
                text = "$partnerName 正在驾驶，疲劳等级：${driver.fatigueLevel.label}",
                style = MaterialTheme.typography.bodyMedium,
                color = TextPrimary,
            )
            Text(
                text = "疲劳分数 ${"%.1f".format(driver.fatigueScore)} · PERCLOS ${"%.2f".format(driver.perclos)} · 哈欠 ${driver.yawnTotal} 次",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            if (driver.fatigueLevel != com.shineleong.toughmind.data.model.FatigueLevel.NORMAL) {
                Text(
                    text = "建议：发一条语音或提醒 TA 在安全的地方休息，不要连续驾驶。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
        }
    }
}

@Composable
internal fun AdviceCard(
    advices: List<AdviceEntity>,
    loading: Boolean,
    error: String?,
    coupleMode: Boolean,
    onGenerate: () -> Unit,
) {
    val visible = advices
        .filter { coupleMode || it.kind != AdviceKind.LOVE.key }
        .take(if (coupleMode) 4 else 3)
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.AutoAwesome,
                    contentDescription = null,
                    tint = Gold,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    text = "关心建议",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
                TextButton(onClick = onGenerate, enabled = !loading) {
                    Text(
                        text = when {
                            loading -> "生成中…"
                            visible.isNotEmpty() -> "再想几条"
                            coupleMode -> "生成四条"
                            else -> "生成三条"
                        }
                    )
                }
            }
            Text(
                text = if (coupleMode) {
                    "智能体会结合 TA 的状态与两地天气，一次给出行动、表达、小惊喜和一句情话。"
                } else {
                    "智能体会结合 TA 的状态与两地天气，一次给出行动、表达和小惊喜三个角度。"
                },
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            if (visible.isNotEmpty()) {
                Text(
                    text = "生成后仅展示 3 分钟，随后自动释放。",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
            if (loading) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = Gold,
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = if (coupleMode) {
                            "正在想 4 条不同角度的关心，其中一条是情话…"
                        } else {
                            "正在想 3 条不同角度的关心…"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
            }
            error?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
            if (visible.isEmpty() && !loading) {
                Text(
                    text = "还没有关心建议。点「生成」，让智能体根据 TA 此刻的状态，给出今天就能用上的话。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }
            visible.forEach { advice ->
                AdviceTipItem(advice)
            }
        }
    }
}

@Composable
private fun AdviceTipItem(advice: AdviceEntity) {
    val kind = AdviceKind.fromKey(advice.kind)
    val accent = adviceKindColor(kind)
    Column(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    color = accent.copy(alpha = 0.16f),
                    shape = RoundedCornerShape(6.dp),
                ) {
                    Text(
                        text = adviceKindLabel(kind),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = accent,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                    )
                }
                Spacer(Modifier.weight(1f))
                Text(
                    text = formatRelativeTime(advice.timestamp),
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
                ReadAloudButton(text = advice.content)
            }
            Text(
                text = advice.content,
                style = MaterialTheme.typography.bodyMedium,
                color = TextPrimary,
            )
        }
        HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.25f))
    }
}

@Composable
private fun adviceKindLabel(kind: AdviceKind): String = when (kind) {
    AdviceKind.ACTION -> tr("马上做", "Do now")
    AdviceKind.WORDS -> tr("说句话", "Say it")
    AdviceKind.SURPRISE -> tr("小惊喜", "Surprise")
    AdviceKind.LOVE -> tr("情话", "Sweet talk")
}

@Composable
private fun adviceKindColor(kind: AdviceKind): Color = when (kind) {
    AdviceKind.ACTION -> MaterialTheme.colorScheme.primary
    AdviceKind.WORDS -> MaterialTheme.colorScheme.secondary
    AdviceKind.SURPRISE -> MaterialTheme.colorScheme.tertiary
    AdviceKind.LOVE -> CareRed
}

@Composable
private fun CoupleCornerCard(
    loveLine: String,
    feedback: String?,
    sending: Boolean,
    doneCount: Int,
    onShuffle: () -> Unit,
    onSend: () -> Unit,
    onOpenRomance: () -> Unit,
) {
    val progress = (doneCount / 100f).coerceIn(0f, 1f)
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.Favorite,
                    contentDescription = null,
                    tint = CareRed,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    text = "情侣模式 · 今天的情话",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
            }
            Surface(
                color = CareRed.copy(alpha = 0.08f),
                shape = RoundedCornerShape(14.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = "“$loveLine”",
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextPrimary,
                    modifier = Modifier.padding(14.dp),
                )
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                TextButton(onClick = onShuffle) {
                    Text("换一句")
                }
                TextButton(onClick = onSend, enabled = !sending) {
                    Text(if (sending) "发送中…" else "发给 TA")
                }
                Spacer(Modifier.weight(1f))
                feedback?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                    )
                }
            }
            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.35f))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .clickable(onClick = onOpenRomance)
                    .padding(vertical = 4.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "一起做的一万件浪漫小事",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        modifier = Modifier.weight(1f),
                    )
                    Text(
                        text = "去看看 ›",
                        style = MaterialTheme.typography.bodySmall,
                        color = Gold,
                    )
                }
                Text(
                    text = "已完成 $doneCount / 100 件 · 目标 ${RomanceCatalog.TOTAL_GOAL} 件",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(6.dp)
                        .clip(RoundedCornerShape(3.dp))
                        .background(MaterialTheme.colorScheme.surfaceVariant),
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth(progress)
                            .height(6.dp)
                            .clip(RoundedCornerShape(3.dp))
                            .background(
                                Brush.horizontalGradient(
                                    listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.secondary)
                                )
                            ),
                    )
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CarePetCard.kt`

> 宠物卡与领养卡、习性弹窗、心情与节奏文案。

````kotlin
package com.shineleong.toughmind.ui.screen.care

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.NightlightRound
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.component.translateText
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.model.AdviceKind
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlRhythm
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.data.model.RelativeSummary
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.ReadAloudButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.statusEnglish
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.ceil

@Composable
private fun PetCardLoading() {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("🐾", style = MaterialTheme.typography.headlineSmall)
            Spacer(Modifier.width(9.dp))
            Text(
                text = tr("正在唤醒小室友…", "Waking your companion…"),
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
        }
    }
}

@Composable
fun OwlPetCard(
    pet: PetState,
    partnerName: String,
    message: PetResultCode?,
    messageSeconds: Int,
    reaction: PetReaction,
    reactionToken: Int,
    busy: Boolean,
    onFeed: () -> Unit,
    onPet: () -> Unit,
    onSpecies: (OwlSpecies) -> Unit,
    onAdopt: (OwlSpecies, String) -> Unit,
    onAdoptRandom: (String) -> Unit,
    onRelease: () -> Unit,
    onRename: (String) -> Unit,
) {
    if (!pet.adopted) {
        AdoptionPetCard(
            pet = pet,
            busy = busy,
            onSpecies = onSpecies,
            onAdopt = onAdopt,
            onAdoptRandom = onAdoptRandom,
        )
        return
    }

    var showHabits by remember { mutableStateOf(false) }
    var showNameDialog by remember { mutableStateOf(false) }
    var showReleaseConfirm by remember { mutableStateOf(false) }
    var nameDraft by remember { mutableStateOf("") }
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }
    LaunchedEffect(Unit) {
        while (true) {
            now = System.currentTimeMillis()
            delay(1_000L)
        }
    }
    var messageVisible by remember(message, reactionToken) {
        mutableStateOf(message != null)
    }
    LaunchedEffect(message, reactionToken) {
        if (message != null) {
            delay(7_000L)
            messageVisible = false
        }
    }

    val cooldownMs = OwlHabits.feedCooldownRemaining(pet, now)
    val cooldownSec = ceil(cooldownMs / 1_000.0).toInt()
    val rhythm = OwlHabits.rhythmAt(now)
    val dayPhase = PetDayPhase.at(now)
    val mood = OwlHabits.moodOf(pet)
    val canFeed = !busy &&
        !pet.asleep &&
        !pet.isFull &&
        pet.feedCountToday < OwlHabits.DAILY_FEED_LIMIT &&
        cooldownMs <= 0L
    val feedLabel = when {
        busy -> tr("稍等…", "One sec…")
        pet.asleep -> tr("睡着中", "Asleep")
        pet.isFull -> tr("吃不下", "Too full")
        pet.feedCountToday >= OwlHabits.DAILY_FEED_LIMIT -> tr("今日吃饱", "Done today")
        cooldownMs > 0L -> tr("消化 ${formatCooldown(cooldownSec)}", "Digest ${formatCooldown(cooldownSec)}")
        else -> tr("投喂", "Feed")
    }
    val displayedMessage = if (messageVisible) message else null
    val speech = if (displayedMessage != null) {
        petResultSpeech(displayedMessage, pet, maxOf(messageSeconds, cooldownSec))
    } else {
        petIdleSpeech(pet)
    }
    val defaultName = petDefaultName(pet.species)
    val displayName = pet.name.ifBlank { defaultName }
    val roommate = when (pet.species) {
        OwlSpecies.SNOWY -> tr("极夜小室友", "polar-night roommate")
        OwlSpecies.INK_CAT -> tr("夜巡小室友", "night-patrol roommate")
        OwlSpecies.RURAL_DOG -> tr("看家小室友", "little guardian")
        OwlSpecies.HAMSTER -> tr("囤粮小室友", "tiny hoarder")
        else -> tr("夜班小室友", "night-shift roommate")
    }
    val habitTag = when (pet.species) {
        OwlSpecies.INK_CAT -> tr("夜巡性", "Crepuscular")
        OwlSpecies.RURAL_DOG -> tr("白天活跃", "Daytime active")
        OwlSpecies.HAMSTER -> tr("夜间活跃", "Nocturnal")
        else -> tr("夜行性", "Nocturnal")
    }

    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(11.dp)) {
            Row(verticalAlignment = Alignment.Top) {
                Column(Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(RoundedCornerShape(50))
                                .background(Color(0xFF4ADE80)),
                        )
                        Spacer(Modifier.width(5.dp))
                        Text(
                            text = tr(
                                "LIVE 2D · ${pet.species.label}",
                                "LIVE 2D · ${pet.species.englishLabel}",
                            ),
                            style = MaterialTheme.typography.labelSmall,
                            color = Gold,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                    Spacer(Modifier.height(2.dp))
                    Text(
                        text = "$displayName · $roommate",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                    )
                    Spacer(Modifier.height(3.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = tr(
                                "${petMoodEmoji(mood)} 心情 ${pet.mood} · 亲密 Lv.${pet.bondLevel}",
                                "${petMoodEmoji(mood)} Mood ${pet.mood} · Bond Lv.${pet.bondLevel}",
                            ),
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                        Spacer(Modifier.weight(1f))
                        Text(
                            text = tr("✏️ 改名", "✏️ Rename"),
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier
                                .clip(RoundedCornerShape(50))
                                .clickable {
                                    nameDraft = pet.name
                                    showNameDialog = true
                                }
                                .padding(horizontal = 7.dp, vertical = 3.dp),
                        )
                    }
                }
                IconButton(onClick = { showHabits = true }) {
                    Icon(
                        Icons.Filled.Info,
                        contentDescription = tr("猫头鹰的习性", "Owl habits"),
                        tint = TextSecondary,
                    )
                }
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(274.dp)
                    .clip(RoundedCornerShape(16.dp)),
            ) {
                PetLive2D(
                    state = pet,
                    reaction = reaction,
                    reactionToken = reactionToken,
                    phase = dayPhase,
                    modifier = Modifier.fillMaxSize(),
                    contentDescription = tr(
                        "${pet.species.label}宠物，点一下摸摸它",
                        "${pet.species.englishLabel} pet. Tap to pet it.",
                    ),
                    onTap = onPet,
                )
                Row(
                    modifier = Modifier
                        .align(Alignment.TopStart)
                        .padding(11.dp),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    SceneChip(
                        icon = if (pet.asleep) "💤" else rhythmEmoji(rhythm),
                        text = if (pet.asleep) {
                            tr("睡着了", "Asleep")
                        } else {
                            rhythmText(rhythm)
                        },
                    )
                    if (pet.overfed) {
                        SceneChip(icon = "🤢", text = tr("有点积食", "A bit overfed"))
                    }
                }
                Text(
                    text = if (pet.asleep) tr("点一下叫醒它", "Tap to wake") else tr("点它摸摸", "Tap to pet"),
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.White.copy(alpha = 0.55f),
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .padding(12.dp),
                )
            }

            Surface(
                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.08f),
                shape = RoundedCornerShape(12.dp),
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 11.dp, vertical = 9.dp),
                    verticalAlignment = Alignment.Top,
                ) {
                    Text(pet.species.emoji, style = MaterialTheme.typography.bodyMedium)
                    Spacer(Modifier.width(7.dp))
                    Text(
                        text = speech,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextPrimary,
                    )
                }
            }

            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                PetStat(
                    label = tr("饱腹", "Fullness"),
                    value = pet.satiety,
                    color = Color(0xFFF2B84B),
                    modifier = Modifier.weight(1f),
                )
                PetStat(
                    label = tr("精力", "Energy"),
                    value = pet.energy,
                    color = Color(0xFF4FC3D9),
                    modifier = Modifier.weight(1f),
                )
                PetStat(
                    label = tr("心情", "Mood"),
                    value = pet.mood,
                    color = Color(0xFFFF7CA8),
                    modifier = Modifier.weight(1f),
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = tr(
                        "今日投喂 ${pet.feedCountToday}/${OwlHabits.DAILY_FEED_LIMIT} 顿",
                        "Meals today ${pet.feedCountToday}/${OwlHabits.DAILY_FEED_LIMIT}",
                    ),
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Spacer(Modifier.weight(1f))
                Text(
                    text = if (pet.lastFedBy.isBlank()) {
                        tr("还没人喂过", "No meals yet")
                    } else {
                        val fedBy = when (pet.lastFedBy) {
                            "self", "我", "Me" -> tr("我", "Me")
                            else -> pet.lastFedBy
                        }
                        tr("上次：$fedBy", "Last: $fedBy")
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }

            Row(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                Button(
                    onClick = onFeed,
                    enabled = canFeed,
                    modifier = Modifier
                        .weight(1f)
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Icon(
                        Icons.Filled.Restaurant,
                        contentDescription = null,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                    Spacer(Modifier.width(5.dp))
                    Text(feedLabel, maxLines = 1)
                }
                OutlinedButton(
                    onClick = onPet,
                    enabled = !busy,
                    modifier = Modifier
                        .weight(1f)
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Icon(
                        if (pet.asleep) Icons.Filled.WbSunny else Icons.Filled.PanTool,
                        contentDescription = null,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                    Spacer(Modifier.width(5.dp))
                    Text(if (pet.asleep) tr("叫醒", "Wake") else tr("摸摸", "Pet"), maxLines = 1)
                }
            }

            Text(
                text = tr(
                    "$habitTag · 每 2 分钟消化一餐 · 每天最多 6 顿 · 睡着时不能硬喂",
                    "$habitTag · 2 min to digest · max 6 meals a day · don't feed while asleep",
                ),
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary,
            )
            Text(
                text = tr(
                    "你和 $partnerName 都能在这台设备上陪它；它也会随真实时间饿、困、想你。",
                    "You and $partnerName can both look after it here; it gets hungry and sleepy in real time.",
                ),
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary.copy(alpha = 0.82f),
            )
        }
    }

    if (showHabits) {
        OwlHabitsDialog(
            species = pet.species,
            onDismiss = { showHabits = false },
            onRelease = {
                showHabits = false
                showReleaseConfirm = true
            },
        )
    }

    if (showNameDialog) {
        AlertDialog(
            onDismissRequest = { showNameDialog = false },
            title = {
                Text(
                    text = tr("给 $displayName 起个名字", "Name $displayName"),
                    fontWeight = FontWeight.Bold,
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(
                        value = nameDraft,
                        onValueChange = {
                            if (it.length <= OwlHabits.MAX_NAME_LENGTH) {
                                nameDraft = it
                            }
                        },
                        singleLine = true,
                        label = { Text(tr("名字", "Name")) },
                        placeholder = { Text(defaultName) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Text(
                        text = tr(
                            "最多 ${OwlHabits.MAX_NAME_LENGTH} 个字符；留空则使用默认名「$defaultName」。",
                            "Up to ${OwlHabits.MAX_NAME_LENGTH} characters; leave blank to use \"$defaultName\".",
                        ),
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        onRename(nameDraft)
                        showNameDialog = false
                    },
                    enabled = !busy,
                ) {
                    Text(tr("保存", "Save"))
                }
            },
            dismissButton = {
                TextButton(onClick = { showNameDialog = false }) {
                    Text(tr("取消", "Cancel"))
                }
            },
        )
    }

    if (showReleaseConfirm) {
        AlertDialog(
            onDismissRequest = { showReleaseConfirm = false },
            title = {
                Text(
                    text = tr("放归 $displayName？", "Release $displayName?"),
                    fontWeight = FontWeight.Bold,
                )
            },
            text = {
                Text(
                    text = tr(
                        "它会回到夜空，当前的饱腹、精力、心情和亲密会清空；以后还可以重新领养。名字和外观选择会保留。",
                        "It will return to the night sky. Its fullness, energy, mood and bond will reset; you can adopt again later. Its name and look will be kept.",
                    ),
                    style = MaterialTheme.typography.bodyMedium,
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showReleaseConfirm = false
                        onRelease()
                    },
                ) {
                    Text(tr("放归", "Release"), color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showReleaseConfirm = false }) {
                    Text(tr("再想想", "Not now"))
                }
            },
        )
    }
}

@Composable
private fun AdoptionPetCard(
    pet: PetState,
    busy: Boolean,
    onSpecies: (OwlSpecies) -> Unit,
    onAdopt: (OwlSpecies, String) -> Unit,
    onAdoptRandom: (String) -> Unit,
) {
    var formOpen by remember { mutableStateOf(false) }
    var selectedSpecies by remember(pet.species) { mutableStateOf(pet.species) }
    var nameDraft by remember(pet.name) { mutableStateOf(pet.name) }
    val defaultName = petDefaultName(selectedSpecies)
    val previewPet = remember(selectedSpecies) {
        PetState(species = selectedSpecies, satiety = 70, energy = 72, mood = 80)
    }
    val previewPhase = PetDayPhase.at(System.currentTimeMillis())

    if (!formOpen) {
        TechCard(modifier = Modifier.fillMaxWidth()) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("🐾", style = MaterialTheme.typography.headlineSmall)
                Spacer(Modifier.width(9.dp))
                Column(Modifier.weight(1f)) {
                    Text(
                        text = tr("还没有领养宠物", "No pet adopted yet"),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                    )
                    Text(
                        text = tr(
                            "想养的时候，随时可以领养一只小宠物。",
                            "Adopt a little companion whenever you're ready.",
                        ),
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
                TextButton(onClick = { formOpen = true }) {
                    Text(tr("领养一只", "Adopt"))
                }
            }
        }
        return
    }

    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(11.dp)) {
            Column {
                Text(
                    text = tr("LIVE 2D · 宠物待领养", "LIVE 2D · WAITING FOR A HOME"),
                    style = MaterialTheme.typography.labelSmall,
                    color = Gold,
                    fontWeight = FontWeight.SemiBold,
                )
                Spacer(Modifier.height(2.dp))
                Text(
                    text = tr("领养一只小宠物", "Adopt a companion"),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                )
                Text(
                    text = tr(
                        "它会在关心页陪着你们。可以自己挑一只，也可以随机领养。",
                        "It will live on the Care page with you. Pick one yourself or adopt at random.",
                    ),
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(220.dp)
                    .clip(RoundedCornerShape(16.dp)),
            ) {
                PetLive2D(
                    state = previewPet,
                    reaction = PetReaction.NONE,
                    reactionToken = 0,
                    phase = previewPhase,
                    modifier = Modifier.fillMaxSize(),
                    contentDescription = tr(
                        "待领养的${selectedSpecies.label}",
                        "A ${selectedSpecies.englishLabel} waiting to be adopted",
                    ),
                )
                SceneChip(
                    icon = "🏡",
                    text = tr("待领养", "Waiting for a home"),
                    modifier = Modifier
                        .align(Alignment.TopStart)
                        .padding(11.dp),
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                listOf(OwlSpecies.entries.take(3), OwlSpecies.entries.drop(3)).forEach { row ->
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        row.forEach { species ->
                            SpeciesPill(
                                emoji = species.emoji,
                                label = tr(species.label, species.englishLabel),
                                selected = selectedSpecies == species,
                                onClick = {
                                    selectedSpecies = species
                                    onSpecies(species)
                                },
                            )
                        }
                    }
                }
            }

            OutlinedTextField(
                value = nameDraft,
                onValueChange = {
                    if (it.length <= OwlHabits.MAX_NAME_LENGTH) {
                        nameDraft = it
                    }
                },
                singleLine = true,
                label = { Text(tr("名字（可选）", "Name (optional)")) },
                placeholder = { Text(defaultName) },
                modifier = Modifier.fillMaxWidth(),
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(
                    onClick = { onAdoptRandom(nameDraft) },
                    enabled = !busy,
                    modifier = Modifier
                        .weight(1f)
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Text(tr("随机领养", "Surprise me"))
                }
                Button(
                    onClick = { onAdopt(selectedSpecies, nameDraft) },
                    enabled = !busy,
                    modifier = Modifier
                        .weight(1f)
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Text(tr("领养它", "Adopt"))
                }
            }
            TextButton(
                onClick = { formOpen = false },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(tr("暂不领养", "Not now"))
            }

            Text(
                text = tr(
                    "留空会自动使用「$defaultName」。随机领养会从全部外观里抽一只；领养后可以随时改名、切换外观或放归。",
                    "Leave the name blank to use \"$defaultName\". Surprise me picks a random look; you can rename, switch looks or release it later.",
                ),
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary,
            )
        }
    }
}

@Composable
private fun petDefaultName(species: OwlSpecies): String = when (species) {
    OwlSpecies.SNOWY -> tr("雪团", "Snowball")
    OwlSpecies.INK_CAT -> tr("墨墨", "Inky")
    OwlSpecies.RURAL_DOG -> tr("阿黄", "Rusty")
    OwlSpecies.HAMSTER -> tr("团子", "Mochi")
    else -> tr("鸮鸮", "Hoo")
}

@Composable
private fun SpeciesPill(
    emoji: String,
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(50)
    Surface(
        onClick = onClick,
        shape = shape,
        color = if (selected) {
            MaterialTheme.colorScheme.primaryContainer
        } else {
            MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f)
        },
        contentColor = if (selected) {
            MaterialTheme.colorScheme.onPrimaryContainer
        } else {
            TextSecondary
        },
        border = BorderStroke(
            width = 1.dp,
            color = if (selected) {
                MaterialTheme.colorScheme.primary.copy(alpha = 0.35f)
            } else {
                MaterialTheme.colorScheme.outline.copy(alpha = 0.65f)
            },
        ),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 9.dp, vertical = 3.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(emoji, style = MaterialTheme.typography.labelSmall)
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
            )
        }
    }
}

@Composable
private fun SceneChip(
    icon: String,
    text: String,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        color = Color(0xCC07122A),
        contentColor = Color(0xFFFFE3A3),
        shape = RoundedCornerShape(50),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 9.dp, vertical = 5.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(icon, style = MaterialTheme.typography.labelSmall)
            Text(
                text = text,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Medium,
            )
        }
    }
}

@Composable
private fun PetStat(
    label: String,
    value: Int,
    color: Color,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary,
            )
            Spacer(Modifier.weight(1f))
            Text(
                text = value.toString(),
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
        }
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(color.copy(alpha = 0.16f)),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(value.coerceIn(0, 100) / 100f)
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(color),
            )
        }
    }
}

@Composable
private fun OwlHabitsDialog(
    species: OwlSpecies,
    onDismiss: () -> Unit,
    onRelease: () -> Unit,
) {
    val rhythmLine = when (species) {
        OwlSpecies.INK_CAT -> tr(
            "夜巡性：清晨和傍晚最精神，白天喜欢找地方打盹。",
            "Crepuscular: sharpest at dawn and dusk, naps through the day.",
        )
        OwlSpecies.RURAL_DOG -> tr(
            "白天活跃：喜欢有人陪，精力好的时候会围着你转。",
            "Daytime active: loves company and bounces around when energetic.",
        )
        OwlSpecies.HAMSTER -> tr(
            "夜间活跃：白天躲着睡，晚上开始囤粮、跑轮。",
            "Nocturnal: hides and sleeps by day, hoards and runs at night.",
        )
        else -> tr(
            "夜行性：清晨、黄昏和深夜最精神，白天会犯困。",
            "Nocturnal: sharpest at dawn, dusk and late night; drowsy by day.",
        )
    }
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                Icons.Filled.NightlightRound,
                contentDescription = null,
                tint = Gold,
            )
        },
        title = {
            Text(
                text = tr("${species.label}的习性", "How your pet lives"),
                fontWeight = FontWeight.Bold,
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(9.dp)) {
                HabitLine(emoji = "🌙", text = rhythmLine)
                HabitLine(
                    emoji = "🍖",
                    text = tr(
                        "不能一直喂：刚吃过要消化 2 分钟，每天最多 6 顿；太饱会拒绝，硬喂会积食。",
                        "No constant feeding: 2 minutes to digest, max 6 meals a day; it refuses when full, and overfeeding upsets its stomach.",
                    ),
                )
                HabitLine(
                    emoji = "😴",
                    text = tr(
                        "精力太低会自己睡着。睡着时先摸摸叫醒，再喂它。",
                        "Low energy makes it fall asleep. Wake it with a gentle pet before feeding.",
                    ),
                )
                HabitLine(
                    emoji = "🪶",
                    text = tr(
                        "慢慢摸会加亲密；连续戳它会被嫌弃，甚至会掉心情。",
                        "Gentle pets build bond; poking it repeatedly annoys it and lowers its mood.",
                    ),
                )
                HabitLine(
                    emoji = "⏳",
                    text = tr(
                        "饱腹、精力和心情会随真实时间变化，离开 App 也一样。",
                        "Fullness, energy and mood change with real time, even while the app is closed.",
                    ),
                )
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(tr("知道了", "Got it"))
            }
        },
        dismissButton = {
            TextButton(onClick = onRelease) {
                Text(tr("放归它", "Release"), color = MaterialTheme.colorScheme.error)
            }
        },
    )
}

@Composable
private fun HabitLine(emoji: String, text: String) {
    Row(verticalAlignment = Alignment.Top) {
        Text(emoji, style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.width(7.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = TextPrimary,
        )
    }
}

@Composable
private fun petIdleSpeech(pet: PetState): String {
    val fur = if (pet.species.isOwl) "羽毛" else "毛"
    return when (OwlHabits.moodOf(pet)) {
        OwlMood.ASLEEP -> tr("嘘——它缩成一团睡着了。", "Shh—it's curled up asleep.")
        OwlMood.HUNGRY -> tr("肚子空空的…有吃的吗？", "My tummy is empty… any food?")
        OwlMood.SLEEPY -> tr("眼皮好重，想缩成一团。", "My eyelids are heavy. I want to curl up.")
        OwlMood.OVERFED -> tr("吃太撑了，动都不想动…", "Too full… I don't even want to move.")
        OwlMood.ANNOYED -> tr("${fur}都被摸乱了，让我静一静。", "My coat is all ruffled. Give me a moment.")
        OwlMood.HAPPY -> when (pet.species) {
            OwlSpecies.SNOWY -> tr("咕——雪夜很安静，你也在。", "Hoo—the snow night is quiet, and you're here.")
            OwlSpecies.INK_CAT -> tr("呼噜呼噜——你在，它就安心了。", "Purr… it feels safe with you here.")
            OwlSpecies.RURAL_DOG -> tr("汪！尾巴摇得停不下来。", "Woof! Its tail won't stop wagging.")
            OwlSpecies.HAMSTER -> tr("吱吱，它把一颗瓜子推到你面前。", "Squeak—it nudges a seed toward you.")
            else -> tr("咕——今晚月色不错，你也在。", "Hoo—lovely moon tonight, and you're here.")
        }
        OwlMood.CONTENT -> when (pet.species) {
            OwlSpecies.INK_CAT -> tr("它眯着眼，尾巴一下一下地拍着地面。", "It squints, tail tapping the floor.")
            OwlSpecies.RURAL_DOG -> tr("它歪着头，把下巴搁在你手边。", "It tilts its head and rests its chin by your hand.")
            OwlSpecies.HAMSTER -> tr("它鼓着腮帮子，认真地看着你。", "It puffs its cheeks and stares at you.")
            OwlSpecies.SNOWY -> tr("它蓬起雪白的羽毛，像一团会呼吸的雪。", "It fluffs its white feathers like a breathing snowball.")
            else -> tr("咕咕。它歪着头看你。", "Hoo. It tilts its head at you.")
        }
    }
}

@Composable
private fun petResultSpeech(
    code: PetResultCode,
    pet: PetState,
    seconds: Int,
): String = when (code) {
    PetResultCode.FED ->
        tr("它叼走食物，一口吞下，满足地眯起眼。", "It snaps up the food, swallows, and squints happily.")
    PetResultCode.FED_OVER ->
        tr("吃太急了…肚子鼓鼓的，它需要缓一会儿。", "Too fast… its tummy is bulging. It needs a moment.")
    PetResultCode.REFUSED_SLEEPING ->
        tr("它睡着了。先摸摸叫醒它，再喂也不迟。", "It's asleep. Wake it with a gentle pet first.")
    PetResultCode.REFUSED_FULL ->
        tr("已经很饱了（${pet.satiety}%），再喂要积食啦。", "Already full (${pet.satiety}%). More would upset its stomach.")
    PetResultCode.REFUSED_COOLDOWN ->
        tr("刚吃过，肚子还没空。再等 ${formatCooldown(seconds)} 吧。", "Still digesting. Give it ${formatCooldown(seconds)} more.")
    PetResultCode.REFUSED_DAILY_LIMIT ->
        tr(
            "今天已经吃了 ${OwlHabits.DAILY_FEED_LIMIT} 顿，小家伙也要控制体重。",
            "That's ${OwlHabits.DAILY_FEED_LIMIT} meals today—little ones watch their weight too.",
        )
    PetResultCode.PETTED ->
        tr("它眯起眼睛，把脑袋往你手心蹭了蹭。", "It closes its eyes and leans its head into your hand.")
    PetResultCode.PET_ANNOYED ->
        tr("别一直戳啦——它抖了抖毛，往旁边挪了一步。", "Stop poking—it shakes its coat and sidesteps.")
    PetResultCode.WOKEN ->
        tr("唔…被你戳醒了，眼睛还没聚焦。", "Mmm… you woke it up. Its eyes haven't focused yet.")
}

private fun formatCooldown(seconds: Int): String {
    val safe = seconds.coerceAtLeast(0)
    return "%d:%02d".format(safe / 60, safe % 60)
}

/** 关系属性决定卡片里是否出现情侣功能，不再用单独的全局模式开关。 */
internal fun String.isCoupleRelation(): Boolean =
    contains("伴侣") || contains("情侣") || contains("爱人") || equals("couple", ignoreCase = true)

private fun rhythmEmoji(rhythm: OwlRhythm): String = when (rhythm) {
    OwlRhythm.DUSK -> "🌆"
    OwlRhythm.NIGHT -> "🌙"
    OwlRhythm.DAY_REST -> "☀️"
}

@Composable
private fun rhythmText(rhythm: OwlRhythm): String = when (rhythm) {
    OwlRhythm.DUSK -> tr("黄昏最精神", "Dusk — wide awake")
    OwlRhythm.NIGHT -> tr("夜间精神", "Night owl")
    OwlRhythm.DAY_REST -> tr("白天打盹", "Daytime doze")
}

private fun petMoodEmoji(mood: OwlMood): String = when (mood) {
    OwlMood.ASLEEP -> "😴"
    OwlMood.HUNGRY -> "🥺"
    OwlMood.SLEEPY -> "😪"
    OwlMood.OVERFED -> "🤢"
    OwlMood.ANNOYED -> "😤"
    OwlMood.HAPPY -> "😊"
    OwlMood.CONTENT -> "🙂"
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareScreen.kt`

> 关心页装配：亲属卡轮播、天气页与各卡片的组织者。

````kotlin
package com.shineleong.toughmind.ui.screen.care

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.NightlightRound
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.component.translateText
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.model.AdviceKind
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlRhythm
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.data.model.RelativeSummary
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.ReadAloudButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.statusEnglish
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.ceil

/**
 * 关心页：TA 的此刻、双方天气、今日打卡、驾驶安全与关心建议。
 * 不把"驾驶员监测"当作唯一主题，而是作为关心方式之一。
 */
@Composable
fun CareScreen(
    onOpenMap: (String) -> Unit,
    onOpenCalendar: () -> Unit,
    onOpenCompanion: () -> Unit,
    onOpenRomance: () -> Unit,
    viewModel: CareViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val self by viewModel.selfPresence.collectAsStateWithLifecycle()
    val partner by viewModel.partnerPresence.collectAsStateWithLifecycle()
    val partnerWeather by viewModel.partnerWeather.collectAsStateWithLifecycle()
    val companion by viewModel.companion.collectAsStateWithLifecycle()
    val todayCheckIns by viewModel.todayCheckIns.collectAsStateWithLifecycle()
    val advices by viewModel.advices.collectAsStateWithLifecycle()
    val pet by viewModel.pet.collectAsStateWithLifecycle()
    val petLoaded by viewModel.petLoaded.collectAsStateWithLifecycle()
    val relatives by viewModel.relatives.collectAsStateWithLifecycle()
    val relativeWeather by viewModel.relativeWeather.collectAsStateWithLifecycle()
    val romanceDone by viewModel.romanceDone.collectAsStateWithLifecycle()

    val partnerName = companion.nickname.ifBlank { "TA" }
    val bothChecked = todayCheckIns.any { it.personId == CareRepository.SELF_ID } &&
        todayCheckIns.any { it.personId == CareRepository.PARTNER_ID }
    var selectedRelative by remember { mutableStateOf<RelativeSummary?>(null) }
    val coupleMode = selectedRelative?.relation?.isCoupleRelation() == true

    LaunchedEffect(relatives) {
        viewModel.loadRelativeWeathers(relatives)
        if (selectedRelative == null || relatives.none { it.key == selectedRelative?.key }) {
            selectedRelative = relatives.firstOrNull()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        RelativeCarouselCard(
            relatives = relatives,
            weatherFor = { relative ->
                relativeWeather[relative.key] ?: if (relative.key == "local") partnerWeather else null
            },
            onOpenCompanion = onOpenCompanion,
            onOpenMap = { isPrimary ->
                onOpenMap(
                    if (isPrimary) partner?.id ?: CareRepository.SELF_ID else CareRepository.SELF_ID,
                )
            },
            onRelativeSelected = { selectedRelative = it },
            loveLine = viewModel.loveLine,
            loveFeedback = viewModel.loveFeedback,
            loveSending = viewModel.loveSending,
            romanceDoneCount = romanceDone.size,
            onShuffleLove = viewModel::shuffleLoveLine,
            onSendLove = viewModel::sendLoveLine,
            onOpenRomance = onOpenRomance,
        )

        partner?.let { partnerValue ->
            partnerValue.driverState?.let { driver ->
                DriverCareCard(
                    partnerName = partnerName,
                    driver = driver,
                    onOpenMap = { onOpenMap(partnerValue.id) },
                )
            }
        }

        AdviceCard(
            advices = advices,
            loading = viewModel.adviceLoading,
            error = viewModel.adviceError,
            coupleMode = coupleMode,
            onGenerate = { viewModel.generateAdvice(coupleMode) },
        )

        Spacer(Modifier.height(6.dp))
    }
}

@Composable
private fun RelativeCarouselCard(
    relatives: List<RelativeSummary>,
    weatherFor: (RelativeSummary) -> WeatherInfo?,
    onOpenCompanion: () -> Unit,
    onOpenMap: (Boolean) -> Unit,
    onRelativeSelected: (RelativeSummary) -> Unit,
    loveLine: String,
    loveFeedback: String?,
    loveSending: Boolean,
    romanceDoneCount: Int,
    onShuffleLove: () -> Unit,
    onSendLove: () -> Unit,
    onOpenRomance: () -> Unit,
) {
    if (relatives.isEmpty()) return
    val pagerState = rememberPagerState(pageCount = { relatives.size })
    val currentRelative = relatives.getOrNull(pagerState.currentPage) ?: relatives.first()
    val currentHasLocation = currentRelative.lat != null && currentRelative.lon != null &&
        (currentRelative.lat != 0.0 || currentRelative.lon != 0.0)
    val currentIsCouple = currentRelative.relation.isCoupleRelation()
    val pagerHeight = when {
        currentIsCouple && currentHasLocation -> 430.dp
        currentIsCouple -> 300.dp
        currentHasLocation -> 330.dp
        else -> 200.dp
    }
    LaunchedEffect(pagerState.currentPage, relatives) {
        relatives.getOrNull(pagerState.currentPage)?.let(onRelativeSelected)
    }
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "亲属",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                )
                Spacer(Modifier.weight(1f))
                if (relatives.size > 1) {
                    Text(
                        text = "${pagerState.currentPage + 1}/${relatives.size}",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                    )
                }
            }
            HorizontalPager(
                state = pagerState,
                pageSpacing = 12.dp,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(pagerHeight),
            ) { page ->
                RelativeWeatherPage(
                    relative = relatives[page],
                    weather = weatherFor(relatives[page]),
                    isPrimary = page == 0,
                    onOpenCompanion = onOpenCompanion,
                    onOpenMap = { onOpenMap(page == 0) },
                    loveLine = loveLine,
                    loveFeedback = loveFeedback,
                    loveSending = loveSending,
                    romanceDoneCount = romanceDoneCount,
                    onShuffleLove = onShuffleLove,
                    onSendLove = onSendLove,
                    onOpenRomance = onOpenRomance,
                )
            }
            if (relatives.size > 1) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    repeat(relatives.size) { index ->
                        val selected = pagerState.currentPage == index
                        Box(
                            modifier = Modifier
                                .padding(horizontal = 3.dp)
                                .size(if (selected) 7.dp else 5.dp)
                                .clip(CircleShape)
                                .background(
                                    if (selected) {
                                        MaterialTheme.colorScheme.primary
                                    } else {
                                        MaterialTheme.colorScheme.outline
                                    },
                                ),
                        )
                    }
                }
                Text(
                    text = "左右滑动看下一位亲属",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
        }
    }
}

@Composable
private fun RelativeWeatherPage(
    relative: RelativeSummary,
    weather: WeatherInfo?,
    isPrimary: Boolean,
    onOpenCompanion: () -> Unit,
    onOpenMap: () -> Unit,
    loveLine: String,
    loveFeedback: String?,
    loveSending: Boolean,
    romanceDoneCount: Int,
    onShuffleLove: () -> Unit,
    onSendLove: () -> Unit,
    onOpenRomance: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .padding(12.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(9.dp),
            ) {
                Box(
                    modifier = Modifier
                        .size(42.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = relative.name.take(1).ifBlank { "?" },
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
                Column(Modifier.weight(1f)) {
                    Text(
                        text = relative.name,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                    )
                    // 状态栏：显示 TA 当前的在线状态，离线时默认显示「离线」。
                    val statusLabel = statusEnglish(relative.status)
                    Text(
                        text = when {
                            !relative.online -> "离线"
                            relative.status == CareStatus.UNKNOWN -> "在线"
                            else -> "${relative.status.emoji} $statusLabel"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = when {
                            !relative.online -> TextSecondary
                            relative.status == CareStatus.UNKNOWN -> CareStatus.ONLINE.toColor()
                            else -> relative.status.toColor()
                        },
                    )
                }
                Text(
                    text = "编辑",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier
                        .clip(RoundedCornerShape(50))
                        .clickable(onClick = onOpenCompanion)
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                )
            }
            if (relative.activityNote.isNotBlank()) {
                Text(
                    text = relative.activityNote,
                    style = MaterialTheme.typography.bodySmall,
                    color = relative.status.toColor(),
                )
            }
            Row(modifier = Modifier.fillMaxWidth()) {
                InfoLine(
                    label = "电量",
                    value = if (relative.battery in 0..100) "${relative.battery}%" else "未知",
                    modifier = Modifier.weight(1f),
                )
                Spacer(Modifier.width(10.dp))
                InfoLine(
                    label = "更新",
                    value = if (relative.lastSeen > 0) formatRelativeTime(relative.lastSeen) else "未知",
                    modifier = Modifier.weight(1f),
                )
            }
            val hasLocation = relative.lat != null && relative.lon != null &&
                (relative.lat != 0.0 || relative.lon != 0.0)
            if (hasLocation) {
                WeatherInfoCard(
                    title = "当地天气",
                    weather = weather,
                    modifier = Modifier.fillMaxWidth(),
                )
            } else {
                Text(
                    text = "对方还没有共享位置",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    modifier = Modifier.padding(vertical = 10.dp),
                )
            }
            if (relative.relation.isCoupleRelation()) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column(
                        modifier = Modifier.padding(vertical = 6.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Filled.Favorite,
                                contentDescription = null,
                                tint = CareRed,
                                modifier = Modifier.size(18.dp),
                            )
                            Spacer(Modifier.width(5.dp))
                            Text(
                                text = "今天的情话",
                                style = MaterialTheme.typography.labelLarge,
                                fontWeight = FontWeight.SemiBold,
                                color = TextPrimary,
                                modifier = Modifier.weight(1f),
                            )
                            Text(
                                text = "换一句",
                                style = MaterialTheme.typography.labelSmall,
                                color = CareRed,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(5.dp))
                                    .clickable(onClick = onShuffleLove)
                                    .padding(horizontal = 6.dp, vertical = 4.dp),
                            )
                        }
                        val english = LocalAppLanguage.current == "en"
                        val shownLoveLine = translateText(loveLine, if (english) "en" else "zh")
                        Text(
                            text = if (english) "\"$shownLoveLine\"" else "“$shownLoveLine”",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextPrimary,
                            maxLines = 2,
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "浪漫清单 $romanceDoneCount/100",
                                style = MaterialTheme.typography.labelSmall,
                                color = TextSecondary,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(5.dp))
                                    .clickable(onClick = onOpenRomance)
                                    .padding(vertical = 3.dp),
                            )
                            Spacer(Modifier.weight(1f))
                            Text(
                                text = if (loveSending) "发送中…" else "发给 TA",
                                style = MaterialTheme.typography.labelSmall,
                                color = CareRed,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(5.dp))
                                    .clickable(enabled = !loveSending, onClick = onSendLove)
                                    .padding(horizontal = 6.dp, vertical = 3.dp),
                            )
                        }
                        loveFeedback?.let {
                            Text(
                                text = it,
                                style = MaterialTheme.typography.labelSmall,
                                color = TextSecondary,
                            )
                        }
                    }
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/care/CareViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.care

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.PetActionResult
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.data.model.RelativeSummary
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.LlmService
import com.shineleong.toughmind.data.repository.AdviceRepository
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.repository.CheckInRepository
import com.shineleong.toughmind.data.repository.WeatherRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.time.LocalDate

/** 关心页：TA 的状态、双方天气、今日打卡、关心建议。 */
class CareViewModel(
    careRepository: CareRepository,
    private val adviceRepository: AdviceRepository,
    private val llmService: LlmService,
    private val checkInRepository: CheckInRepository,
    private val preferences: Preferences,
    private val careSyncRepository: CareSyncRepository,
    private val weatherRepository: WeatherRepository,
) : ViewModel() {

    val selfPresence: StateFlow<PersonPresence?> = careRepository.selfPresence
    val partnerPresence: StateFlow<PersonPresence?> = careRepository.partnerPresence
    val selfWeather: StateFlow<WeatherInfo?> = careRepository.selfWeather
    val partnerWeather: StateFlow<WeatherInfo?> = careRepository.partnerWeather
    val companion: StateFlow<CarePartner> = careRepository.companion

    /** 关心页可左右滑动的亲属：云端有多位时用云端成员，否则退回本地单亲友。 */
    val relatives: StateFlow<List<RelativeSummary>> = combine(
        careSyncRepository.members,
        careRepository.companion,
        careRepository.partnerPresence,
    ) { members, companion, partner ->
        // ESP32 设备不算「亲友」，设备信息统一放到「设备」页展示。
        val people = members.filter {
            !it.isDevice && it.deviceType != com.shineleong.toughmind.data.model.DeviceType.ESP32
        }
        if (people.isNotEmpty()) {
            people.map { member ->
                val presence = member.presence
                RelativeSummary(
                    key = member.account,
                    name = member.nickname.ifBlank { "TA" },
                    relation = member.relation.ifBlank { "家人" },
                    deviceLabel = if (member.isDevice || member.deviceType == com.shineleong.toughmind.data.model.DeviceType.ESP32) {
                        "设备"
                    } else {
                        "手机 · 亲属组"
                    },
                    online = presence?.online == true,
                    lat = presence?.lat,
                    lon = presence?.lon,
                    status = runCatching { CareStatus.valueOf(presence?.status.orEmpty()) }
                        .getOrDefault(CareStatus.UNKNOWN),
                    activityNote = presence?.activityNote.orEmpty(),
                    battery = presence?.battery ?: -1,
                    lastSeen = (presence?.updatedAt ?: 0L) * 1000L,
                )
            }
        } else {
            listOf(
                RelativeSummary(
                    key = "local",
                    name = companion.nickname.ifBlank { "TA" },
                    relation = companion.relation.ifBlank { "家人" },
                    deviceLabel = if (companion.deviceType == com.shineleong.toughmind.data.model.DeviceType.ESP32) {
                        "设备"
                    } else {
                        "手机 · 亲属组"
                    },
                    online = partner?.online == true,
                    lat = partner?.lat,
                    lon = partner?.lon,
                    status = partner?.status ?: CareStatus.UNKNOWN,
                    activityNote = partner?.activityNote.orEmpty(),
                    battery = partner?.battery ?: -1,
                    lastSeen = partner?.lastSeen ?: 0L,
                )
            )
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    private val _relativeWeather = MutableStateFlow<Map<String, WeatherInfo>>(emptyMap())
    val relativeWeather: StateFlow<Map<String, WeatherInfo>> = _relativeWeather
    private val weatherRequested = mutableSetOf<String>()

    /** 按每位亲属的位置拉天气；WeatherRepository 自带约 10 分钟缓存。 */
    fun loadRelativeWeathers(list: List<RelativeSummary>) {
        list.forEach { relative ->
            val lat = relative.lat ?: return@forEach
            val lon = relative.lon ?: return@forEach
            if (!weatherRequested.add(relative.key)) return@forEach
            viewModelScope.launch {
                val weather = runCatching { weatherRepository.weatherAt(lat, lon) }.getOrNull()
                if (weather != null) {
                    _relativeWeather.value = _relativeWeather.value + (relative.key to weather)
                } else {
                    weatherRequested.remove(relative.key)
                }
            }
        }
    }

    private val petClock: Flow<Long> = flow {
        while (true) {
            emit(System.currentTimeMillis())
            delay(30_000L)
        }
    }

    private val _petLoaded = MutableStateFlow(false)

    /** 宠物存档是否已经从 DataStore 读出来；读出来之前不显示“未领养”，避免卡片闪一下。 */
    val petLoaded: StateFlow<Boolean> = _petLoaded

    val pet: StateFlow<PetState> = combine(
        preferences.owlPet,
        petClock,
    ) { raw, now ->
        OwlHabits.advance(raw, now)
    }.onEach {
        _petLoaded.value = true
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), PetState())

    /** 最近一次互动的结果，界面据此显示气泡。 */
    var petMessage by mutableStateOf<PetResultCode?>(null)
        private set
    var petMessageSeconds by mutableStateOf(0)
        private set
    var petReaction by mutableStateOf(PetReaction.NONE)
        private set
    var petReactionToken by mutableStateOf(0)
        private set
    var petBusy by mutableStateOf(false)
        private set

    private val petMutex = Mutex()

    val todayCheckIns: StateFlow<List<CheckInEntity>> = checkInRepository
        .observeDate(LocalDate.now().toString())
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val advices: StateFlow<List<AdviceEntity>> = adviceRepository
        .observeAdvice(CARE_DEVICE_ID)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    /** 关系模式：couple / family，决定是否展示情话与浪漫清单。 */
    val careMode: StateFlow<String> = preferences.careMode
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "couple")

    val language: StateFlow<String> = preferences.language
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "zh")

    val romanceDone: StateFlow<Set<Int>> = preferences.romanceDoneIds
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptySet())

    /** 每日情话；「换一句」只改当前展示，不写入云端。 */
    var loveLine by mutableStateOf(RomanceCatalog.dailyLoveLine())
        private set
    var loveFeedback by mutableStateOf<String?>(null)
        private set
    var loveSending by mutableStateOf(false)
        private set

    var adviceLoading by mutableStateOf(false)
        private set
    var adviceError by mutableStateOf<String?>(null)
        private set

    fun feedPet(by: String) {
        runPetAction { now ->
            OwlHabits.feed(preferences.owlPet.first(), by, now)
        }
    }

    fun petOwl() {
        runPetAction { now ->
            OwlHabits.pet(preferences.owlPet.first(), now)
        }
    }

    /** 只切换羽色/外观，不重置饥饿、精力和亲密。 */
    fun setOwlSpecies(species: OwlSpecies) {
        if (petBusy) return
        petBusy = true
        viewModelScope.launch {
            try {
                petMutex.withLock {
                    val now = System.currentTimeMillis()
                    val current = OwlHabits.advance(preferences.owlPet.first(), now)
                    if (current.species == species) return@withLock
                    preferences.setOwlPet(current.copy(species = species, updatedAt = now))
                    if (!current.asleep) {
                        petReaction = if (species == OwlSpecies.SNOWY) {
                            PetReaction.WAKE
                        } else {
                            PetReaction.PET
                        }
                        petReactionToken += 1
                    }
                }
            } finally {
                petBusy = false
            }
        }
    }

    /** 领养会从一只新宠物开始：清空旧饥饿、精力和亲密，但保留选择的外观与名字。 */
    fun adoptOwl(species: OwlSpecies, name: String) {
        if (petBusy) return
        petBusy = true
        viewModelScope.launch {
            try {
                petMutex.withLock {
                    val now = System.currentTimeMillis()
                    preferences.setOwlPet(
                        PetState(
                            adopted = true,
                            species = species,
                            name = OwlHabits.normalizeName(name),
                            updatedAt = now,
                            feedDay = LocalDate.now().toString(),
                        )
                    )
                    petMessage = null
                    petMessageSeconds = 0
                    petReaction = PetReaction.WAKE
                    petReactionToken += 1
                }
            } finally {
                petBusy = false
            }
        }
    }

    /** 随机领养：从全部宠物里抽一只，名字留空就用默认名。 */
    fun adoptRandom(name: String) = adoptOwl(OwlSpecies.random(), name)

    /** 放归后保留名字和外观选择，下次领养会重新从幼年状态开始。 */
    fun releaseOwl() {
        if (petBusy) return
        petBusy = true
        viewModelScope.launch {
            try {
                petMutex.withLock {
                    val now = System.currentTimeMillis()
                    val current = OwlHabits.advance(preferences.owlPet.first(), now)
                    preferences.setOwlPet(current.copy(adopted = false, updatedAt = now))
                    petMessage = null
                    petMessageSeconds = 0
                }
            } finally {
                petBusy = false
            }
        }
    }

    fun renameOwl(name: String) {
        if (petBusy) return
        petBusy = true
        viewModelScope.launch {
            try {
                petMutex.withLock {
                    val now = System.currentTimeMillis()
                    val current = OwlHabits.advance(preferences.owlPet.first(), now)
                    val cleaned = OwlHabits.normalizeName(name)
                    if (current.name == cleaned) return@withLock
                    preferences.setOwlPet(current.copy(name = cleaned, updatedAt = now))
                    petReaction = PetReaction.PET
                    petReactionToken += 1
                }
            } finally {
                petBusy = false
            }
        }
    }

    private fun runPetAction(action: suspend (now: Long) -> PetActionResult) {
        if (petBusy) return
        petBusy = true
        viewModelScope.launch {
            try {
                petMutex.withLock {
                    val now = System.currentTimeMillis()
                    val result = runCatching { action(now) }.getOrNull()
                    if (result == null) {
                        petMessage = PetResultCode.PET_ANNOYED
                        petReaction = PetReaction.REFUSE
                        petReactionToken += 1
                        return@withLock
                    }
                    preferences.setOwlPet(result.state)
                    petMessage = result.code
                    petMessageSeconds = result.secondsRemaining
                    petReaction = result.reaction
                    petReactionToken += 1
                }
            } finally {
                petBusy = false
            }
        }
    }

    fun toggleTodayCheckIn(personId: String, checked: Boolean) {
        viewModelScope.launch {
            checkInRepository.toggle(LocalDate.now().toString(), personId, checked)
        }
    }

    fun shuffleLoveLine() {
        loveLine = RomanceCatalog.anotherLoveLine(loveLine)
    }

    /** 把当前情话通过关心消息发给 TA；失败时保留文案，提示稍后再试。 */
    fun sendLoveLine() {
        if (loveSending) return
        loveSending = true
        viewModelScope.launch {
            val outgoing = if (language.value == "en") {
                com.shineleong.toughmind.ui.component.translateText(loveLine, "en")
            } else {
                loveLine
            }
            val result = careSyncRepository.sendNudge(outgoing)
            loveFeedback = result.fold(
                onSuccess = { "已发给 TA" },
                onFailure = { "发送失败，稍后再试" },
            )
            loveSending = false
            delay(2_500)
            loveFeedback = null
        }
    }

    fun generateAdvice(coupleMode: Boolean = careMode.value == "couple") {
        if (adviceLoading) return
        adviceLoading = true
        adviceError = null
        viewModelScope.launch {
            runCatching {
                llmService.requestCareAdvices(
                    scene = buildScene(coupleMode),
                    coupleMode = coupleMode,
                    english = language.value == "en",
                )
            }.onSuccess { advices ->
                if (advices.isEmpty()) {
                    adviceError = "关心建议暂时生成失败，请稍后再试"
                } else {
                    adviceRepository.insertAll(
                        advices.map { advice ->
                            AdviceEntity(
                                deviceId = CARE_DEVICE_ID,
                                content = advice.content,
                                timestamp = advice.timestamp,
                                kind = advice.kind,
                            )
                        }
                    )
                    // 关心建议只在生成后展示 3 分钟，随后释放，避免长期堆积。
                    viewModelScope.launch {
                        delay(180_000)
                        adviceRepository.clear(CARE_DEVICE_ID)
                    }
                }
            }.onFailure {
                adviceError = "关心建议暂时生成失败，请稍后再试"
            }
            adviceLoading = false
        }
    }

    private fun buildScene(coupleMode: Boolean): String {
        val partner = partnerPresence.value
        val self = selfPresence.value
        val companionValue = companion.value
        val selfWeatherValue = selfWeather.value
        val partnerWeatherValue = partnerWeather.value
        return buildString {
            append("关系：${companionValue.relation}；")
            append("关系模式：${if (coupleMode) "情侣" else "家人"}；")
            append("TA 当前状态：${partner?.status?.label ?: "未知"}；")
            partner?.activityNote?.takeIf { it.isNotBlank() }?.let { append("TA 的动态：$it；") }
            partner?.distanceMeters?.let { append("我们相距约 ${(it / 1000).format(1)} km；") }
            partner?.battery?.takeIf { it in 0..100 }?.let { append("TA 设备电量 $it%；") }
            partner?.driverState?.let { driver ->
                append("TA 的疲劳等级：${driver.fatigueLevel.label}；")
                append("疲劳分数：${driver.fatigueScore.format(0)}；")
                append("PERCLOS：${driver.perclos.format(2)}；")
            }
            selfWeatherValue?.let {
                append("我这里 ${it.label} ${it.temperatureC.format(0)}℃；")
            }
            partnerWeatherValue?.let {
                append("TA 那里 ${it.label} ${it.temperatureC.format(0)}℃；")
            }
            self?.name?.let { append("我是${it}。") }
            append("请结合这些信息，给出今天就能去做的关心行动。")
        }
    }

    private fun Double.format(digits: Int): String = "%.${digits}f".format(this)

    private companion object {
        const val CARE_DEVICE_ID = "care"
    }
}
````

<a id="s05-2"></a>

## 步骤 05.2 · 亲友设置与亲友列表

称呼/关系独立成页；亲友列表作为入口。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/CompanionScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/CompanionViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/RelativeSettingsScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/friends/FriendsScreen.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/CompanionScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.companion

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.remote.CareGroupResponse
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.CareBlue
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.GoldDark
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

/** 亲友绑定：称呼、关系、设备类型（手机 / ESP32）与演示模式。 */
@Composable
fun CompanionScreen(
    viewModel: CompanionViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val group by viewModel.group.collectAsStateWithLifecycle()
    val groups by viewModel.groups.collectAsStateWithLifecycle()
    val groupActive by viewModel.groupActive.collectAsStateWithLifecycle()

    var showJoinDialog by rememberSaveable { mutableStateOf(false) }
    var showCreateDialog by rememberSaveable { mutableStateOf(false) }
    var inviteCode by rememberSaveable { mutableStateOf("") }
    var joinPassword by rememberSaveable { mutableStateOf("") }
    var groupName by rememberSaveable { mutableStateOf("") }
    var groupPassword by rememberSaveable { mutableStateOf("") }

    val clipboard = LocalClipboardManager.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        GroupPagerCard(
            groups = groups,
            activeGroupId = group?.group?.id ?: 0L,
            onActivate = viewModel::activateGroup,
        )

        CloudPairingCard(
            group = group,
            groupActive = groupActive,
            loading = viewModel.pairingLoading,
            error = viewModel.pairingError,
            message = viewModel.pairingMessage,
            onCreate = { showCreateDialog = true },
            onJoin = { showJoinDialog = true },
            onLeave = viewModel::leaveGroup,
            onApprove = viewModel::approveRequest,
            onReject = viewModel::rejectRequest,
            onRemoveMember = viewModel::removeMember,
            onCopyCode = { code ->
                clipboard.setText(AnnotatedString(code))
            },
        )



        Text(
            text = "创建 / 加入关心组后，双方的位置、状态、打卡与提醒会通过云端同步；未加入、未登录或服务器不可用时仍可使用个人模式。设备上报的定位与驾驶状态仍会优先覆盖云端数据。",
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary,
            modifier = Modifier.padding(horizontal = 4.dp),
        )

        Spacer(Modifier.height(8.dp))
    }

    if (showJoinDialog) {
        AlertDialog(
            onDismissRequest = { showJoinDialog = false },
            title = { Text("加入关心组") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "输入 TA 发来的 6 位邀请码，加入后即可看到对方的真实位置与状态。",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    OutlinedTextField(
                        value = inviteCode,
                        onValueChange = { value ->
                            inviteCode = value.uppercase()
                                .filter { it.isLetterOrDigit() }
                                .take(6)
                        },
                        label = { Text("邀请码") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = joinPassword,
                        onValueChange = { joinPassword = it },
                        label = { Text("组长设置的验证密码") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.joinGroup(inviteCode, viewModel.companion.value.relation, joinPassword)
                        showJoinDialog = false
                    },
                ) { Text("提交申请") }
            },
            dismissButton = {
                TextButton(onClick = { showJoinDialog = false }) { Text("取消") }
            },
        )
    }
    if (showCreateDialog) {
        AlertDialog(
            onDismissRequest = { showCreateDialog = false },
            title = { Text("创建关心组") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "给关心组起个名字，并设置验证密码；组员申请后需要你通过。",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    OutlinedTextField(
                        value = groupName,
                        onValueChange = { groupName = it.take(24) },
                        label = { Text("组名，例如：家庭组") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = groupPassword,
                        onValueChange = { groupPassword = it.take(32) },
                        label = { Text("验证密码（至少 4 位）") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.createGroup(groupName, groupPassword)
                        showCreateDialog = false
                    },
                ) { Text("创建") }
            },
            dismissButton = {
                TextButton(onClick = { showCreateDialog = false }) { Text("取消") }
            },
        )
    }
}

@Composable
private fun GroupPagerCard(
    groups: List<CareGroupResponse>,
    activeGroupId: Long,
    onActivate: (Long) -> Unit,
) {
    if (groups.size < 2) return
    val pager = rememberPagerState(pageCount = { groups.size })
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "我的关心组",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = "${pager.currentPage + 1}/${groups.size}",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
            HorizontalPager(
                state = pager,
                pageSpacing = 10.dp,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(126.dp),
            ) { page ->
                val item = groups[page]
                val active = item.group?.id == activeGroupId
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    shape = RoundedCornerShape(14.dp),
                    color = if (active) {
                        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.75f)
                    } else {
                        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)
                    },
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Text(
                            text = item.group?.name ?: "关心组",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary,
                        )
                        Text(
                            text = "${item.group?.memberCount ?: 0} 人 · ${item.group?.deviceCount ?: 0} 台设备",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                        Text(
                            text = "邀请码 ${item.group?.inviteCode.orEmpty()}",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextSecondary,
                        )
                        if (active) {
                            Text(
                                text = "当前关心组",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.primary,
                            )
                        } else {
                            TextButton(
                                onClick = { onActivate(item.group?.id ?: 0L) },
                                contentPadding = PaddingValues(0.dp),
                            ) { Text("切换到此组") }
                        }
                    }
                }
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
            ) {
                repeat(groups.size) { index ->
                    Box(
                        modifier = Modifier
                            .padding(horizontal = 3.dp)
                            .size(if (pager.currentPage == index) 7.dp else 5.dp)
                            .clip(CircleShape)
                            .background(
                                if (pager.currentPage == index) {
                                    MaterialTheme.colorScheme.primary
                                } else {
                                    MaterialTheme.colorScheme.outline
                                }
                            ),
                    )
                }
            }
        }
    }
}

@Composable
private fun CloudPairingCard(
    group: CareGroupResponse?,
    groupActive: Boolean,
    loading: Boolean,
    error: String?,
    message: String?,
    onCreate: () -> Unit,
    onJoin: () -> Unit,
    onLeave: () -> Unit,
    onApprove: (Long) -> Unit,
    onReject: (Long) -> Unit,
    onRemoveMember: (String) -> Unit,
    onCopyCode: (String) -> Unit,
) {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "云端关心组",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = if (groupActive) "已连接" else "本地演示",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (groupActive) LevelNormal else TextSecondary,
                )
            }

            if (groupActive && group != null) {
                val inviteCode = group.group?.inviteCode.orEmpty()
                Text(
                    text = "邀请码",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = MaterialTheme.colorScheme.primaryContainer,
                    ) {
                        Text(
                            text = inviteCode,
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer,
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                        )
                    }
                    TextButton(onClick = { onCopyCode(inviteCode) }) {
                        Icon(
                            Icons.Filled.ContentCopy,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                        )
                        Spacer(Modifier.width(4.dp))
                        Text("复制")
                    }
                }
                val people = group.members.count { it.role != "device" }
                if (people > 0) {
                    Text(
                        text = "已有 $people 人",
                        style = MaterialTheme.typography.bodyMedium,
                        color = LevelNormal,
                    )
                    Text(
                        text = "手机通过邀请码加入关心组。",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                } else {
                    Text(
                        text = "关心组已创建，等待成员加入。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary,
                    )
                }
                val owner = group.group?.role == "owner"
                if (owner && group.requests.isNotEmpty()) {
                    Text(
                        text = "待审批的加入申请",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    group.requests.forEach { request ->
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "${request.nickname} · ${request.relation}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextPrimary,
                                modifier = Modifier.weight(1f),
                            )
                            TextButton(onClick = { onApprove(request.id) }) { Text("通过") }
                            TextButton(onClick = { onReject(request.id) }) {
                                Text("拒绝", color = CareRed)
                            }
                        }
                    }
                }
                if (owner) {
                    val others = group.members.filter {
                        !it.isSelf && !it.isDevice && it.account.isNotBlank()
                    }
                    if (others.isNotEmpty()) {
                        Text(
                            text = "组员",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                        )
                        others.forEach { member ->
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "${member.nickname} · ${member.relation}",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = TextPrimary,
                                    modifier = Modifier.weight(1f),
                                )
                                TextButton(onClick = { onRemoveMember(member.account) }) {
                                    Text("移除", color = CareRed)
                                }
                            }
                        }
                    }
                }
                TextButton(onClick = onLeave) {
                    Text(
                        text = if (group.group?.role == "owner") "解散关心组" else "退出关心组",
                        color = CareRed,
                    )
                }
            } else {
                Text(
                    text = "创建关心组或输入邀请码，和 TA 的手机 / 设备同步真实位置、状态、打卡与提醒。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    TechButton(
                        text = "创建关心组",
                        onClick = onCreate,
                        enabled = !loading,
                        modifier = Modifier
                            .weight(1f)
                            .height(AppDimens.ButtonHeight),
                    )
                    OutlinedButton(
                        onClick = onJoin,
                        enabled = !loading,
                        modifier = Modifier
                            .weight(1f)
                            .height(AppDimens.ButtonHeight),
                        shape = AppDimens.ButtonShape,
                    ) {
                        Text("输入邀请码")
                    }
                }
            }

            if (loading) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp,
                        color = Gold,
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = "正在连接云端…",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
            }
            error?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
            message?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = LevelNormal,
                )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/CompanionViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.companion

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.remote.CareGroupResponse
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.CompanionRepository
import com.shineleong.toughmind.data.repository.DeviceRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class CompanionViewModel(
    private val companionRepository: CompanionRepository,
    private val careSyncRepository: CareSyncRepository,
    careRepository: CareRepository,
    deviceRepository: DeviceRepository,
) : ViewModel() {

    val companion: StateFlow<CarePartner> = careRepository.companion

    val group: StateFlow<CareGroupResponse?> = careSyncRepository.group
    val groups: StateFlow<List<CareGroupResponse>> = careSyncRepository.groups
    val groupActive: StateFlow<Boolean> = careSyncRepository.groupActive

    /** 设备管理里绑定的 ESP32；有设备时，亲友设置里的设备显示为 ESP32。 */
    val devices = deviceRepository.devices
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    /** 云端关心组里的 ESP32 设备成员。 */
    val groupDevices = careSyncRepository.devices

    var savedMessage by mutableStateOf<String?>(null)
        private set
    var pairingLoading by mutableStateOf(false)
        private set
    var pairingMessage by mutableStateOf<String?>(null)
        private set
    var pairingError by mutableStateOf<String?>(null)
        private set

    init {
        viewModelScope.launch { careSyncRepository.refreshNow() }
    }

    fun save(nickname: String, relation: String, deviceType: DeviceType, demoMode: Boolean): Boolean {
        if (nickname.isBlank()) {
            savedMessage = "请填写 TA 的称呼"
            return false
        }
        viewModelScope.launch {
            companionRepository.save(
                CarePartner(
                    nickname = nickname.trim(),
                    relation = relation,
                    deviceType = deviceType,
                    demoMode = demoMode,
                )
            )
            savedMessage = "已保存，TA 的信息会同步到地图与日程"
        }
        return true
    }

    fun createGroup(name: String, password: String) {
        if (pairingLoading) return
        if (password.trim().length < 4) {
            pairingError = "请设置至少 4 位验证密码"
            return
        }
        pairingLoading = true
        pairingError = null
        viewModelScope.launch {
            careSyncRepository.createGroup(name.trim().ifBlank { "关心组" }, password.trim())
                .onSuccess {
                    pairingMessage = "关心组已创建，把邀请码和验证密码发给 TA"
                    savedMessage = null
                    careSyncRepository.refreshNow()
                }
                .onFailure { pairingError = it.message ?: "创建失败，请检查服务器连接" }
            pairingLoading = false
        }
    }

    fun joinGroup(inviteCode: String, relation: String, password: String) {
        if (pairingLoading) return
        if (inviteCode.isBlank()) {
            pairingError = "请输入 6 位邀请码"
            return
        }
        pairingLoading = true
        pairingError = null
        viewModelScope.launch {
            careSyncRepository.joinGroup(inviteCode.trim().uppercase(), relation, password.trim())
                .onSuccess { response ->
                    pairingMessage = if (response.pending) {
                        response.message.ifBlank { "已提交加入申请，等待组长确认" }
                    } else {
                        "已加入关心组，TA 的状态会开始同步"
                    }
                }
                .onFailure { pairingError = it.message ?: "加入失败，请检查邀请码或密码" }
            pairingLoading = false
        }
    }

    fun activateGroup(groupId: Long) {
        if (pairingLoading) return
        pairingLoading = true
        viewModelScope.launch {
            careSyncRepository.activateGroup(groupId)
                .onSuccess {
                    pairingMessage = "已切换到「${it.group?.name ?: "关心组"}」"
                    careSyncRepository.refreshNow()
                }
                .onFailure { pairingError = it.message ?: "切换关心组失败" }
            pairingLoading = false
        }
    }

    fun approveRequest(requestId: Long) {
        viewModelScope.launch {
            careSyncRepository.approveJoinRequest(requestId)
                .onSuccess { pairingMessage = "已通过加入申请" }
                .onFailure { pairingError = it.message ?: "审批失败" }
        }
    }

    fun rejectRequest(requestId: Long) {
        viewModelScope.launch {
            careSyncRepository.rejectJoinRequest(requestId)
                .onSuccess { pairingMessage = "已拒绝加入申请" }
                .onFailure { pairingError = it.message ?: "处理失败" }
        }
    }

    fun removeMember(account: String) {
        viewModelScope.launch {
            careSyncRepository.removeGroupMember(account)
                .onSuccess { pairingMessage = "已移除组员" }
                .onFailure { pairingError = it.message ?: "移除失败" }
        }
    }

    fun leaveGroup() {
        pairingLoading = true
        pairingError = null
        viewModelScope.launch {
            val current = group.value
            val groupId = current?.group?.id ?: 0L
            val result = if (current?.me?.role == "owner" && groupId > 0L) {
                careSyncRepository.dissolveGroup(groupId)
            } else {
                careSyncRepository.leaveGroup()
            }
            result
                .onSuccess {
                    pairingMessage = if (current?.me?.role == "owner") {
                        "关心组已解散，所有组员已退出"
                    } else {
                        "已退出关心组，回到本地演示模式"
                    }
                }
                .onFailure { pairingError = it.message ?: "操作失败" }
            pairingLoading = false
        }
    }

    fun deleteCompanion() {
        viewModelScope.launch {
            if (groupActive.value) {
                runCatching { careSyncRepository.leaveGroup() }
            }
            companionRepository.clear()
            savedMessage = "亲友已删除，已回到个人模式"
        }
    }

    fun clearPairingMessage() {
        pairingMessage = null
        pairingError = null
    }

    fun clearMessage() {
        savedMessage = null
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/companion/RelativeSettingsScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.companion

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.theme.CareRed
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

/** 亲属卡里的「亲友设置」：只改称呼、关系，不出现云端关心组/设备绑定。 */
@Composable
fun RelativeSettingsScreen(
    viewModel: CompanionViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val companion by viewModel.companion.collectAsStateWithLifecycle()
    val devices by viewModel.devices.collectAsStateWithLifecycle()
    val groupActive by viewModel.groupActive.collectAsStateWithLifecycle()
    val relations = listOf("家人", "长辈", "伴侣", "朋友", "其他")

    var name by rememberSaveable(companion.nickname) { mutableStateOf(companion.nickname) }
    var relation by rememberSaveable(companion.relation) { mutableStateOf(companion.relation) }
    var relationIndex by rememberSaveable(companion.relation) {
        mutableStateOf(relations.indexOf(companion.relation).coerceAtLeast(0))
    }
    val bindingType = when {
        groupActive -> DeviceType.PHONE
        devices.isNotEmpty() -> DeviceType.ESP32
        else -> companion.deviceType
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text(
                    text = "称呼",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    placeholder = { Text("比如：妈妈、阿哲") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )

                Text(
                    text = "你们的关系",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )
                ScrollableTabRow(
                    selectedTabIndex = relationIndex,
                    edgePadding = 0.dp,
                    containerColor = MaterialTheme.colorScheme.surface,
                ) {
                    relations.forEachIndexed { index, label ->
                        Tab(
                            selected = relationIndex == index,
                            onClick = {
                                relationIndex = index
                                relation = label
                            },
                            text = { Text(label) },
                        )
                    }
                }

                TechButton(
                    text = "保存亲友信息",
                    onClick = { viewModel.save(name, relation, bindingType, false) },
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedButton(
                    onClick = { viewModel.deleteCompanion() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                ) {
                    Text("删除亲友", color = CareRed)
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/friends/FriendsScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.friends

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
import com.shineleong.toughmind.ui.screen.care.CareScreen
import com.shineleong.toughmind.ui.screen.checkin.CheckInScreen

/** 「亲友」= 关心卡 + 留言墙；打卡任务在「行程」里。 */
@Composable
fun FriendsScreen(
    onOpenMap: (String) -> Unit,
    onOpenCalendar: () -> Unit,
    onOpenCompanion: () -> Unit,
    onOpenRomance: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var tab by rememberSaveable { mutableIntStateOf(0) }
    Column(modifier = modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = tab, containerColor = MaterialTheme.colorScheme.surface) {
            listOf("关心", "留言墙").forEachIndexed { index, label ->
                Tab(
                    selected = tab == index,
                    onClick = { tab = index },
                    text = { Text(label) },
                )
            }
        }
        Box(modifier = Modifier.weight(1f)) {
            when (tab) {
                0 -> CareScreen(
                    onOpenMap = onOpenMap,
                    onOpenCalendar = onOpenCalendar,
                    onOpenCompanion = onOpenCompanion,
                    onOpenRomance = onOpenRomance,
                )
                else -> CheckInScreen(
                    showTasks = false,
                    showWall = true,
                )
            }
        }
    }
}
````

<a id="s05-3"></a>

## 步骤 05.3 · 留言与弹幕墙

文字与语音留言、消息气泡与弹幕展示。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatSheet.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatWall.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/DanmakuWall.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatSheet.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.chat

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaPlayer
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import androidx.compose.material3.rememberModalBottomSheetState
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.ReadAloudButton
import com.shineleong.toughmind.util.ImagePreviewDialog
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.ImageUtils
import com.shineleong.toughmind.util.VoiceRecorder
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
fun ChatSheet(
    onDismiss: () -> Unit,
    viewModel: ChatViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    val self by viewModel.self.collectAsStateWithLifecycle()
    val partner by viewModel.partner.collectAsStateWithLifecycle()
    val companion by viewModel.companion.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var text by remember { mutableStateOf("") }
    var showEmoji by remember { mutableStateOf(false) }
    var imagePreview by remember { mutableStateOf<String?>(null) }
    var recording by remember { mutableStateOf(false) }
    var recordSeconds by remember { mutableStateOf(0) }
    var voiceMode by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    val recorder = remember { VoiceRecorder(context) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) voiceMode = true
    }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        if (uri != null) scope.launch {
            ImageUtils.encode(context, uri)?.let { viewModel.sendImage(it) }
        }
    }

    LaunchedEffect(recording) {
        if (recording) {
            recordSeconds = 0
            while (recording) {
                kotlinx.coroutines.delay(1000)
                recordSeconds++
            }
        }
    }
    DisposableEffect(Unit) { onDispose { recorder.cancel() } }
    LaunchedEffect(Unit) {
        while (true) {
            viewModel.syncRemote()
            kotlinx.coroutines.delay(2_000)
        }
    }

    val timeline = remember(messages) {
        buildTimeline(messages, emptyList())
    }

    // 对话始终把最新一条放在底部，并在新消息到达时滚到底部。
    LaunchedEffect(timeline.size) {
        if (timeline.isNotEmpty()) {
            listState.animateScrollToItem(timeline.lastIndex)
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = MaterialTheme.colorScheme.surface,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .fillMaxHeight(0.88f)
                .imePadding(),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 18.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Avatar(
                    nickname = partner?.name ?: "我",
                    size = 34.dp,
                    moodEmoji = partner?.moodEmoji,
                    online = partner?.online == true,
                )
                Spacer(Modifier.width(10.dp))
                Column(Modifier.weight(1f)) {
                    Text(
                        "对话",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    val chatTitle = partner?.name ?: tr("个人模式", "Personal mode")
                    val chatHint = tr(" · 只显示对话消息", " · Chat messages only")
                    val chatCount = tr("${timeline.size} 条", "${timeline.size} messages")
                    Text(
                        text = "$chatTitle$chatHint · $chatCount",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
                val lastReadableText = remember(timeline) {
                    timeline.asReversed()
                        .firstOrNull { it is TimelineItem.Message }
                        ?.let { (it as TimelineItem.Message).value.text }
                        ?.takeIf { it.isNotBlank() }
                }
                if (lastReadableText != null) {
                    ReadAloudButton(text = lastReadableText)
                }
            }
            Spacer(Modifier.height(8.dp))
            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.35f))

            LazyColumn(
                modifier = Modifier.weight(1f).fillMaxWidth(),
                state = listState,
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(timeline, key = {
                    when (it) {
                        is TimelineItem.Message -> "m${it.value.id}"
                        is TimelineItem.Record -> "r${it.value.id}"
                    }
                }) { item ->
                    when (item) {
                        is TimelineItem.Message -> MessageBubble(
                            item.value,
                            onPreview = { imagePreview = it },
                        )
                        is TimelineItem.Record -> RecordBubble(
                            item.value,
                            onPreview = { imagePreview = it },
                        )
                    }
                }
                if (timeline.isEmpty()) {
                    item {
                        Text(
                            "还没有对话，说点什么吧。",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                            modifier = Modifier.padding(vertical = 30.dp),
                        )
                    }
                }
            }

            if (showEmoji) {
                val emojis = listOf("😊", "🥰", "😌", "😴", "🥳", "❤️", "🌙", "✨")
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    emojis.forEach { emoji ->
                        Text(
                            emoji,
                            modifier = Modifier
                                .clip(CircleShape)
                                .clickable {
                                    text += emoji
                                    showEmoji = false
                                }
                                .padding(6.dp),
                        )
                    }
                }
            }

            Surface(color = MaterialTheme.colorScheme.surface) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 10.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.Bottom,
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    IconButton(onClick = {
                        if (voiceMode) {
                            voiceMode = false
                        } else if (ContextCompat.checkSelfPermission(
                                context,
                                Manifest.permission.RECORD_AUDIO,
                            ) == PackageManager.PERMISSION_GRANTED
                        ) {
                            voiceMode = true
                        } else {
                            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }) {
                        Icon(
                            Icons.Filled.Mic,
                            contentDescription = "语音留言",
                            tint = if (voiceMode) MaterialTheme.colorScheme.primary else TextSecondary,
                        )
                    }
                    if (voiceMode) {
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(48.dp)
                                .clip(RoundedCornerShape(22.dp))
                                .background(MaterialTheme.colorScheme.surfaceVariant)
                                .pointerInput(Unit) {
                                    detectTapGestures(
                                        onPress = {
                                            if (!recording) recording = recorder.start()
                                            tryAwaitRelease()
                                            if (recording) {
                                                recording = false
                                                recorder.stop()?.let { (path, duration) ->
                                                    viewModel.sendVoice(path, duration)
                                                }
                                            }
                                        }
                                    )
                                },
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                if (recording) "松开发送 · ${recordSeconds}s" else "按住 说话",
                                style = MaterialTheme.typography.bodyMedium,
                                color = if (recording) MaterialTheme.colorScheme.primary else TextSecondary,
                            )
                        }
                    } else {
                        OutlinedTextField(
                            value = text,
                            onValueChange = { text = it },
                            placeholder = { Text("说点什么…") },
                            maxLines = 4,
                            shape = RoundedCornerShape(22.dp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = Color.Transparent,
                                unfocusedBorderColor = Color.Transparent,
                                disabledBorderColor = Color.Transparent,
                                focusedContainerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f),
                                unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f),
                            ),
                            modifier = Modifier.weight(1f).heightIn(min = 48.dp, max = 120.dp),
                        )
                        if (text.isNotBlank()) {
                            IconButton(onClick = {
                                viewModel.sendText(text)
                                text = ""
                            }) {
                                Icon(Icons.Filled.Send, contentDescription = "发送", tint = MaterialTheme.colorScheme.primary)
                            }
                        } else {
                            IconButton(onClick = { showEmoji = !showEmoji }) {
                                Icon(Icons.Filled.EmojiEmotions, contentDescription = "表情", tint = TextSecondary)
                            }
                            IconButton(onClick = { picker.launch("image/*") }) {
                                Icon(Icons.Filled.Add, contentDescription = "添加照片", tint = TextSecondary)
                            }
                        }
                    }
                }
            }
        }
    }

    imagePreview?.let { ImagePreviewDialog(base64 = it, onDismiss = { imagePreview = null }) }
}

@Composable
private fun WallMessageCard(message: ChatMessageEntity, onPreview: (String) -> Unit) {
    val mine = message.fromSelf
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = if (mine) MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.7f)
        else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                MiniAvatar(label = if (mine) "我" else message.senderName.ifBlank { "TA" })
                Spacer(Modifier.width(8.dp))
                Text(
                    if (mine) "我" else message.senderName.ifBlank { "TA" },
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                )
                Spacer(Modifier.weight(1f))
                Text(timestampLabel(message.date, message.timeMinutes), style = MaterialTheme.typography.labelSmall, color = TextSecondary)
            }
            if (message.text.isNotBlank()) {
                Text(message.text, style = MaterialTheme.typography.bodyLarge, color = TextPrimary)
            }
            if (message.imageBase64.isNotBlank()) {
                val bitmap = remember(message.imageBase64) { ImageUtils.decode(message.imageBase64) }
                if (bitmap != null) {
                    Image(
                        bitmap = bitmap,
                        contentDescription = "留言图片",
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 220.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .clickable { onPreview(message.imageBase64) },
                        contentScale = ContentScale.FillWidth,
                    )
                }
            }
            if (message.audioPath.isNotBlank()) {
                VoiceBubble(message.audioPath, message.audioDurationMs)
            }
        }
    }
}

@Composable
private fun MessageBubble(message: ChatMessageEntity, onPreview: (String) -> Unit) {
    val mine = message.fromSelf
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (mine) Arrangement.End else Arrangement.Start,
        verticalAlignment = Alignment.Bottom,
    ) {
        if (!mine) {
            MiniAvatar(label = message.senderName.ifBlank { "TA" })
            Spacer(Modifier.width(6.dp))
        }
        Column(
            horizontalAlignment = if (mine) Alignment.End else Alignment.Start,
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            if (message.text.isNotBlank()) {
                Surface(
                    color = if (mine) MaterialTheme.colorScheme.primaryContainer
                    else MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (mine) 16.dp else 4.dp,
                        bottomEnd = if (mine) 4.dp else 16.dp,
                    ),
                ) {
                    Text(
                        message.text,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                        color = if (mine) MaterialTheme.colorScheme.onPrimaryContainer else TextPrimary,
                    )
                }
            }
            if (message.imageBase64.isNotBlank()) {
                val bitmap = remember(message.imageBase64) { ImageUtils.decode(message.imageBase64) }
                if (bitmap != null) {
                    Image(
                        bitmap = bitmap,
                        contentDescription = "留言图片",
                        modifier = Modifier
                            .size(150.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .clickable { onPreview(message.imageBase64) },
                        contentScale = ContentScale.Crop,
                    )
                }
            }
            if (message.audioPath.isNotBlank()) {
                VoiceBubble(message.audioPath, message.audioDurationMs)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    timestampLabel(message.date, message.timeMinutes),
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
                if (message.text.isNotBlank()) {
                    ReadAloudButton(text = message.text)
                }
            }
        }
        if (mine) {
            Spacer(Modifier.width(6.dp))
            MiniAvatar(label = "我")
        }
    }
}

@Composable
private fun RecordBubble(record: SchedulePostEntity, onPreview: (String) -> Unit) {
    val mine = record.authorId == CareRepository.SELF_ID
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (mine) Arrangement.End else Arrangement.Start,
    ) {
        Surface(
            color = if (mine) MaterialTheme.colorScheme.primaryContainer
            else MaterialTheme.colorScheme.surfaceVariant,
            shape = RoundedCornerShape(
                topStart = 14.dp,
                topEnd = 14.dp,
                bottomStart = if (mine) 14.dp else 4.dp,
                bottomEnd = if (mine) 4.dp else 14.dp,
            ),
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "${timestampLabel(record.date, record.timeMinutes)}  ${record.content}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (mine) MaterialTheme.colorScheme.onPrimaryContainer else TextPrimary,
                )
                if (record.imageBase64.isNotBlank()) {
                    IconButton(onClick = { onPreview(record.imageBase64) }) {
                        Icon(
                            Icons.Filled.Link,
                            contentDescription = "查看照片",
                            tint = if (mine) MaterialTheme.colorScheme.onPrimaryContainer
                            else MaterialTheme.colorScheme.primary,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun VoiceBubble(path: String, durationMs: Long) {
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var playing by remember { mutableStateOf(false) }
    DisposableEffect(Unit) { onDispose { player?.release() } }
    Surface(
        color = MaterialTheme.colorScheme.primaryContainer,
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.clickable {
            if (playing) {
                player?.stop()
                player?.release()
                player = null
                playing = false
            } else {
                runCatching {
                    player = MediaPlayer().apply {
                        setDataSource(path)
                        prepare()
                        start()
                        setOnCompletionListener {
                            playing = false
                            it.release()
                            player = null
                        }
                    }
                    playing = true
                }
            }
        },
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                if (playing) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                contentDescription = "播放语音",
                tint = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            Spacer(Modifier.width(6.dp))
            Text(
                "${(durationMs / 1000).coerceAtLeast(1)}″",
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
        }
    }
}

private fun formatTime(minutes: Int): String =
    String.format(Locale.getDefault(), "%02d:%02d", minutes / 60, minutes % 60)

@Composable
private fun MiniAvatar(label: String) {
    Box(
        modifier = Modifier
            .size(28.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label.take(1),
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
        )
    }
}
private fun timestampLabel(date: String, minutes: Int): String {
    val hm = String.format(Locale.getDefault(), "%02d:%02d", minutes / 60, minutes % 60)
    val today = java.time.LocalDate.now().toString()
    return when {
        date.isBlank() || date == today -> "今天 $hm"
        date.length >= 10 -> "${date.substring(5, 10).replace("-", "/")} $hm"
        else -> hm
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.ChatMessageRepository
import com.shineleong.toughmind.data.repository.CompanionRepository
import com.shineleong.toughmind.data.repository.SchedulePostRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.LocalDate

class ChatViewModel(
    private val chatRepository: ChatMessageRepository,
    private val careSyncRepository: com.shineleong.toughmind.data.repository.CareSyncRepository,
    schedulePostRepository: SchedulePostRepository,
    careRepository: CareRepository,
    companionRepository: CompanionRepository,
) : ViewModel() {
    val messages: StateFlow<List<ChatMessageEntity>> =
        chatRepository.messages.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val schedulePosts: StateFlow<List<SchedulePostEntity>> =
        schedulePostRepository.observeDate(LocalDate.now().toString())
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val self = careRepository.selfPresence.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
    val partner = careRepository.partnerPresence.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
    val companion = companionRepository.companion.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        com.shineleong.toughmind.data.model.CarePartner(),
    )

    fun sendText(text: String) {
        if (text.isBlank()) return
        viewModelScope.launch {
            val remote = careSyncRepository.sendChatMessage(text.trim()).getOrNull()
            if (remote != null) {
                chatRepository.insertRemote(
                    remoteId = remote.id,
                    text = remote.message,
                    fromSelf = true,
                    senderName = remote.fromNickname,
                    createdAt = remote.createdAt,
                )
            } else {
                chatRepository.send(text = text.trim())
            }
        }
    }

    fun syncRemote() {
        viewModelScope.launch {
            runCatching {
                val since = chatRepository.maxRemoteId()
                careSyncRepository.fetchChatMessages(since).getOrThrow().forEach { dto ->
                    chatRepository.insertRemote(
                        remoteId = dto.id,
                        text = dto.message,
                        fromSelf = dto.isMine,
                        senderName = dto.fromNickname,
                        createdAt = dto.createdAt,
                    )
                }
            }
        }
    }

    fun sendImage(base64: String) {
        if (base64.isBlank()) return
        viewModelScope.launch { chatRepository.send(imageBase64 = base64) }
    }

    fun sendVoice(path: String, durationMs: Long) {
        if (path.isBlank()) return
        viewModelScope.launch { chatRepository.send(audioPath = path, audioDurationMs = durationMs) }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/ChatWall.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.chat

import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.repository.CareRepository

/** 对话 / 留言墙共用的时间线条目。 */
internal sealed class TimelineItem {
    data class Message(val value: ChatMessageEntity) : TimelineItem()
    data class Record(val value: SchedulePostEntity) : TimelineItem()
}

/**
 * 把留言和“今天做了什么”合并成一条时间线：
 * 先按日期、再按分钟、最后按创建时间升序，保证最新的在最后（列表底部）。
 */
internal fun buildTimeline(
    messages: List<ChatMessageEntity>,
    posts: List<SchedulePostEntity>,
): List<TimelineItem> = buildList {
    messages.forEach { add(TimelineItem.Message(it)) }
    posts.forEach { add(TimelineItem.Record(it)) }
}.sortedWith(
    compareBy<TimelineItem>(
        {
            when (it) {
                is TimelineItem.Message -> it.value.date
                is TimelineItem.Record -> it.value.date
            }
        },
        {
            when (it) {
                is TimelineItem.Message -> it.value.timeMinutes
                is TimelineItem.Record -> it.value.timeMinutes
            }
        },
        {
            when (it) {
                is TimelineItem.Message -> it.value.createdAt
                is TimelineItem.Record -> it.value.createdAt
            }
        },
    )
)

/** 把时间线压成留言墙上的一条条弹幕；空文本会被跳过。 */
internal fun buildWallEntries(
    timeline: List<TimelineItem>,
    partnerName: String?,
): List<WallEntry> = timeline.mapNotNull { item ->
    when (item) {
        is TimelineItem.Message -> {
            val message = item.value
            val text = message.text.ifBlank {
                when {
                    message.imageBase64.isNotBlank() ->
                        if (message.fromSelf) "发了一张照片" else "发来一张照片"
                    message.audioPath.isNotBlank() ->
                        if (message.fromSelf) "发了一段语音" else "发来一段语音"
                    else -> ""
                }
            }
            if (text.isBlank()) {
                null
            } else {
                WallEntry(
                    key = "m${message.id}",
                    author = if (message.fromSelf) {
                        "我"
                    } else {
                        message.senderName.ifBlank { partnerName?.ifBlank { "TA" } ?: "TA" }
                    },
                    fromSelf = message.fromSelf,
                    text = text,
                    hasImage = message.imageBase64.isNotBlank(),
                    hasAudio = message.audioPath.isNotBlank(),
                    date = message.date,
                )
            }
        }

        is TimelineItem.Record -> {
            val record = item.value
            val text = record.content.ifBlank {
                if (record.imageBase64.isNotBlank()) "记录了一张照片" else ""
            }
            if (text.isBlank()) {
                null
            } else {
                WallEntry(
                    key = "r${record.id}",
                    author = if (record.authorId == CareRepository.SELF_ID) {
                        "我"
                    } else {
                        partnerName?.ifBlank { "TA" } ?: "TA"
                    },
                    fromSelf = record.authorId == CareRepository.SELF_ID,
                    text = "记录：$text",
                    hasImage = record.imageBase64.isNotBlank(),
                    date = record.date,
                )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/chat/DanmakuWall.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

/** 弹幕墙上的一条留言：文字、图片、语音、日期和发送者。 */
data class WallEntry(
    val key: String,
    val author: String,
    val fromSelf: Boolean,
    val text: String,
    val hasImage: Boolean = false,
    val hasAudio: Boolean = false,
    val date: String = "",
)

/**
 * 弹幕墙：展示今天最新的留言。
 *
 * 原实现使用横向轨道动画；这里保留同一份数据与视觉层级，用静态列表呈现，
 * 避免低端设备持续动画耗电，也保证英文模式下文案可翻译。
 */
@Composable
fun DanmakuWall(
    entries: List<WallEntry>,
    modifier: Modifier = Modifier,
) {
    val today = remember { java.time.LocalDate.now().toString() }
    val todayEntries = remember(entries, today) {
        entries.filter { it.date == today }
    }
    if (todayEntries.isEmpty()) {
        EmptyWall(modifier)
        return
    }

    val recent = remember(todayEntries) { todayEntries.takeLast(8).reversed() }
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(20.dp))
            .background(
                Brush.verticalGradient(
                    listOf(
                        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.35f),
                        MaterialTheme.colorScheme.surface.copy(alpha = 0.15f),
                    )
                )
            )
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        recent.forEach { entry ->
            WallEntryRow(entry)
        }
        if (todayEntries.size > recent.size) {
            Text(
                text = tr("更早的留言在「对话」里", "Earlier messages are in Chat"),
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary,
            )
        }
    }
}

@Composable
private fun WallEntryRow(entry: WallEntry) {
    val accent = if (entry.fromSelf) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.secondary
    }
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = if (entry.fromSelf) {
            MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.55f)
        } else {
            MaterialTheme.colorScheme.surface.copy(alpha = 0.92f)
        },
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Box(
                    modifier = Modifier
                        .size(24.dp)
                        .clip(CircleShape)
                        .background(accent.copy(alpha = 0.16f)),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = entry.author.take(1).ifBlank { "🙂" },
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = accent,
                    )
                }
                Text(
                    text = entry.author,
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = accent,
                    maxLines = 1,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = entry.date,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
            Text(
                text = entry.text.ifBlank {
                    when {
                        entry.hasImage && entry.hasAudio -> tr("图片和语音", "Photo and voice")
                        entry.hasImage -> tr("图片", "Photo")
                        entry.hasAudio -> tr("语音", "Voice")
                        else -> ""
                    }
                },
                style = MaterialTheme.typography.bodySmall,
                color = TextPrimary,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.padding(top = 4.dp),
            )
        }
    }
}

@Composable
private fun EmptyWall(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(
                        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.30f),
                        MaterialTheme.colorScheme.surface.copy(alpha = 0.10f),
                    )
                )
            ),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = tr("最新留言会从右边滑进来", "New messages slide in from the right"),
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary.copy(alpha = 0.6f),
            )
            Text(
                text = tr("今天还没有留言", "No messages today"),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
            Text(
                text = tr("从下面发出第一条，它会从右边滑进来。", "Send the first one below; it slides in from the right."),
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
                modifier = Modifier.padding(top = 4.dp),
            )
        }
    }
}
````

<a id="s05-4"></a>

## 步骤 05.4 · 个人中心、设置与关于

账号、头像、主题、语言、朗读、关怀模式与关于页。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/AboutScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/ProfileScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/ProfileViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/SettingsScreen.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/AboutScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.profile

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material3.MaterialTheme
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.shineleong.toughmind.BuildConfig
import com.shineleong.toughmind.R
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun AboutScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Spacer(Modifier.height(24.dp))

        Image(
            painter = painterResource(R.drawable.app_logo),
            contentDescription = "logo",
            modifier = Modifier
                .size(80.dp)
                .clip(RoundedCornerShape(20.dp)),
            contentScale = ContentScale.Crop,
        )

        Text(
            text = "念安",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = TextPrimary,
        )
        Text(
            text = "亲属与亲属之间互相关心的 App",
            style = MaterialTheme.typography.bodyLarge,
            color = TextSecondary,
        )

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("版本信息", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "版本 ${BuildConfig.VERSION_NAME}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                )
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("把关心的人放进地图", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "念安不只是一款驾驶监测 App。对方可以是使用手机的家人、伴侣，也可以是车上或家里的设备。驾驶安全只是其中一种关心方式，学习、休息、位置与天气都会出现在这里。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("会说话的小智", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "小智是念安里的 AI 陪伴助手：可以陪你说说话、提醒你休息，也能帮你看 TA 的状态和天气。它会用嘴型和音律条回应你的每一句话，语音可以随时关掉；对话只保存在本机，不会同步给对方。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("关于产品", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "念安是一款面向亲属、伴侣与家人的互相关心 App。设备既可以是专用硬件，也可以是我们每天随身携带的手机：在地图上看见彼此的位置，了解 TA 正在学习、工作、休息还是开车；一起在日程里打卡，双方都完成时那一天会亮起红色；也可以为彼此设置定时提醒，并查看两地天气。\n\n驾驶疲劳检测是念安的能力之一：当对方使用车载设备时，疲劳、分心与紧急状态会作为关心提醒出现，而不是 App 的全部主题。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/ProfileScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.profile

import android.graphics.BitmapFactory
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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.SelfStatusDialog
import com.shineleong.toughmind.ui.component.SelfStatusLine
import com.shineleong.toughmind.ui.component.selfStatusLabel
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val user by viewModel.user.collectAsStateWithLifecycle()
    val avatarPath by viewModel.avatarPath.collectAsStateWithLifecycle()
    val moodEmoji by viewModel.moodEmoji.collectAsStateWithLifecycle()
    val moodMessage by viewModel.moodMessage.collectAsStateWithLifecycle()
    val selfPresence by viewModel.selfPresence.collectAsStateWithLifecycle()
    var showStatusDialog by remember { mutableStateOf(false) }

    // 有在线数据时按数据判断；没有数据时，只要还登录着就视为在线。
    val online = selfPresence?.online ?: (user != null)
    val onlineColor = Color(0xFF16A36A)

    val avatarBitmap = remember(avatarPath) {
        if (avatarPath.isBlank()) null
        else runCatching { BitmapFactory.decodeFile(avatarPath)?.asImageBitmap() }.getOrNull()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        TechCard(modifier = Modifier.fillMaxWidth()) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Avatar(
                    nickname = user?.nickname,
                    size = 64.dp,
                    imageBitmap = avatarBitmap,
                    online = true,
                    moodEmoji = moodEmoji,
                    showStatusBadge = false,
                )
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(
                        text = user?.nickname ?: "未登录",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = "账号：${user?.account ?: "--"}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary,
                    )
                    Spacer(Modifier.height(4.dp))
                    // 「在线」状态放在「我的状态」这里；未上线时默认显示离线。
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(if (online) onlineColor else TextSecondary),
                        )
                        Text(
                            text = if (online) "在线" else "离线",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (online) onlineColor else TextSecondary,
                            fontWeight = FontWeight.Medium,
                        )
                    }
                    SelfStatusLine(
                        emoji = moodEmoji,
                        status = selfStatusLabel(moodEmoji, moodMessage),
                        onClick = { showStatusDialog = true },
                    )
                }
            }
        }
    }

    if (showStatusDialog) {
        SelfStatusDialog(
            initialEmoji = moodEmoji,
            initialMessage = moodMessage,
            onDismiss = { showStatusDialog = false },
            onSave = { emoji, message ->
                viewModel.setMood(emoji, message)
                showStatusDialog = false
            },
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/ProfileViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.profile

import android.content.Context
import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.User
import com.shineleong.toughmind.data.repository.AuthRepository
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.MqttRepository
import com.shineleong.toughmind.data.repository.XiaozhiRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class ProfileViewModel(
    private val appContext: Context,
    private val authRepository: AuthRepository,
    private val mqttRepository: MqttRepository,
    private val preferences: Preferences,
    private val careSyncRepository: CareSyncRepository,
    private val xiaozhiRepository: XiaozhiRepository,
    private val careRepository: CareRepository,
) : ViewModel() {

    val user: StateFlow<User?> =
        authRepository.currentUser.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    /** 自己的在线状态：有位置/在线数据时在线，否则默认离线。 */
    val selfPresence: StateFlow<PersonPresence?> = careRepository.selfPresence

    val avatarPath: StateFlow<String> =
        preferences.avatarPath.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "")

    val moodEmoji: StateFlow<String> =
        preferences.moodEmoji.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "🙂")

    val moodMessage: StateFlow<String> =
        preferences.moodMessage.stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5_000),
            "今天也要好好生活",
        )

    val notificationEnabled: StateFlow<Boolean> =
        preferences.notificationEnabled.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), true)

    val soundEnabled: StateFlow<Boolean> =
        preferences.soundEnabled.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), true)

    val themeMode: StateFlow<String> =
        preferences.themeMode.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "system")

    val language: StateFlow<String> =
        preferences.language.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "zh")

    val showPartnerOnMap: StateFlow<Boolean> =
        preferences.showPartnerOnMap.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), true)
    val careMode: StateFlow<String> =
        preferences.careMode.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "couple")

    val elderMode: StateFlow<Boolean> =
        preferences.elderMode.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), false)

    val ttsPreset: StateFlow<String> =
        preferences.ttsPreset.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "auto")

    val ttsMode: StateFlow<String> =
        preferences.ttsMode.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "offline")

    val fontScale: StateFlow<Float> =
        preferences.fontScale.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 1f)

    val speechRate: StateFlow<Float> =
        preferences.speechRate.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 1f)

    val xiaozhiName: StateFlow<String> =
        preferences.xiaozhiName.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "小智")

    fun setShowPartnerOnMap(show: Boolean) {
        viewModelScope.launch { preferences.setShowPartnerOnMap(show) }
    }

    fun setCareMode(mode: String) {
        viewModelScope.launch { preferences.setCareMode(mode) }
    }

    fun setElderMode(enabled: Boolean) {
        viewModelScope.launch { preferences.setElderMode(enabled) }
    }

    fun setTtsPreset(preset: String) {
        viewModelScope.launch { preferences.setTtsPreset(preset) }
    }

    fun setTtsMode(mode: String) {
        viewModelScope.launch { preferences.setTtsMode(mode) }
    }

    fun setFontScale(scale: Float) {
        viewModelScope.launch {
            preferences.setFontScale(scale)
            preferences.setElderMode(scale >= 1.2f)
        }
    }

    fun setSpeechRate(rate: Float) {
        viewModelScope.launch { preferences.setSpeechRate(rate) }
    }

    fun setXiaozhiName(name: String) {
        viewModelScope.launch { preferences.setXiaozhiName(name) }
    }

    fun setThemeMode(mode: String) {
        viewModelScope.launch { preferences.setThemeMode(mode) }
    }

    fun setMood(emoji: String, message: String) {
        viewModelScope.launch { preferences.setMood(emoji, message) }
    }

    fun setLanguage(language: String) {
        viewModelScope.launch { preferences.setLanguage(language) }
    }

    fun setNotificationEnabled(enabled: Boolean) {
        viewModelScope.launch { preferences.setNotificationEnabled(enabled) }
    }

    fun setSoundEnabled(enabled: Boolean) {
        viewModelScope.launch { preferences.setSoundEnabled(enabled) }
    }

    fun updateNickname(nickname: String) {
        viewModelScope.launch {
            authRepository.updateNickname(nickname)
            careSyncRepository.updateSelfNickname(nickname)
        }
    }

    fun updateAvatar(bitmap: Bitmap) {
        viewModelScope.launch {
            // 每次换头像写新文件名：DataStore 的路径值变化后 UI 才会立即重新解码。
            val file = withContext(Dispatchers.IO) {
                val target = File(appContext.filesDir, "avatar_${System.currentTimeMillis()}.png")
                FileOutputStream(target).use { out ->
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
                }
                appContext.filesDir
                    .listFiles { f -> f.name.startsWith("avatar") && f.name.endsWith(".png") }
                    ?.filter { it.absolutePath != target.absolutePath }
                    ?.forEach { it.delete() }
                target
            }
            preferences.setAvatarPath(file.absolutePath)
        }
    }

    fun logout(onDone: () -> Unit) {
        viewModelScope.launch {
            mqttRepository.stop()
            // 小智对话只属于当前登录的人：退出时清掉，避免下一个账号看到。
            runCatching { xiaozhiRepository.clear() }
            authRepository.logout()
            onDone()
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/profile/SettingsScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.profile

import android.content.Intent
import android.speech.tts.TextToSpeech
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.TextButton
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.TextSecondary
import com.shineleong.toughmind.util.TtsMode
import kotlin.math.roundToInt

@Composable
fun SettingsScreen(
    onLogout: () -> Unit,
    onOpenAbout: () -> Unit,
    viewModel: ProfileViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val notificationEnabled by viewModel.notificationEnabled.collectAsStateWithLifecycle()
    val soundEnabled by viewModel.soundEnabled.collectAsStateWithLifecycle()
    val themeMode by viewModel.themeMode.collectAsStateWithLifecycle()
    val language by viewModel.language.collectAsStateWithLifecycle()
    val showPartnerOnMap by viewModel.showPartnerOnMap.collectAsStateWithLifecycle()
    val elderMode by viewModel.elderMode.collectAsStateWithLifecycle()
    val ttsPreset by viewModel.ttsPreset.collectAsStateWithLifecycle()
    val ttsMode by viewModel.ttsMode.collectAsStateWithLifecycle()
    val fontScale by viewModel.fontScale.collectAsStateWithLifecycle()
    val shownFontScale = if (elderMode && fontScale <= 1.01f) 1.25f else fontScale
    val speechRate by viewModel.speechRate.collectAsStateWithLifecycle()
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text("外观与语言", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(10.dp))
                Text("主题", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf(
                        "system" to "跟随系统",
                        "light" to "浅色",
                        "dark" to "深色",
                    ).forEach { (value, label) ->
                        FilterChip(
                            selected = themeMode == value,
                            onClick = { viewModel.setThemeMode(value) },
                            label = { Text(label) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                            ),
                        )
                    }
                }
                Spacer(Modifier.height(10.dp))
                Text("语言 / Language", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(
                        selected = language == "zh",
                        onClick = { viewModel.setLanguage("zh") },
                        label = { Text("中文") },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                            selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                        ),
                    )
                    FilterChip(
                        selected = language == "en",
                        onClick = { viewModel.setLanguage("en") },
                        label = { Text("English") },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                            selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                        ),
                    )
                }
                HorizontalDivider(Modifier.padding(vertical = 10.dp))
                SettingToggleRow(
                    title = "关怀模式",
                    checked = elderMode,
                    onCheckedChange = { enabled ->
                        viewModel.setFontScale(if (enabled) 1.25f else 1f)
                    },
                )
                Text(
                    "开启后字号放大到 1.25 倍；下方也可以单独微调字体和朗读速度。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    "字体大小 ${(shownFontScale * 100).roundToInt()}%",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Slider(
                    value = shownFontScale,
                    onValueChange = { viewModel.setFontScale(it) },
                    valueRange = 1f..1.5f,
                    steps = 4,
                )
                Text(
                    "朗读速度 ${"%.1f".format(speechRate)}x",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Slider(
                    value = speechRate,
                    onValueChange = { viewModel.setSpeechRate(it) },
                    valueRange = 0.7f..1.3f,
                    steps = 5,
                )
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text("朗读音色", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text("朗读模式", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    listOf(TtsMode.CLOUD, TtsMode.OFFLINE).forEach { mode ->
                        FilterChip(
                            selected = ttsMode == mode.key,
                            onClick = { viewModel.setTtsMode(mode.key) },
                            label = { Text(mode.labelZh) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                            ),
                        )
                    }
                }
                Text(
                    if (ttsMode == TtsMode.CLOUD.key) {
                        "云端优先使用系统网络音色；没有网络音色时自动回退离线音色。"
                    } else {
                        "离线优先使用已下载的音色；方言音色需要先在系统中安装。"
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Spacer(Modifier.height(8.dp))
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        listOf(
                            com.shineleong.toughmind.util.TtsPreset.AUTO,
                            com.shineleong.toughmind.util.TtsPreset.MANDARIN,
                        ).forEach { preset ->
                            FilterChip(
                                selected = ttsPreset == preset.key,
                                onClick = { viewModel.setTtsPreset(preset.key) },
                                label = { Text(preset.labelZh) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                    selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                                ),
                            )
                        }
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        listOf(
                            com.shineleong.toughmind.util.TtsPreset.CANTONESE,
                            com.shineleong.toughmind.util.TtsPreset.ENGLISH,
                        ).forEach { preset ->
                            FilterChip(
                                selected = ttsPreset == preset.key,
                                onClick = { viewModel.setTtsPreset(preset.key) },
                                label = { Text(preset.labelZh) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                    selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer,
                                ),
                            )
                        }
                    }
                }
                Text(
                    "方言音色取决于系统 TTS 是否安装；没有对应音色时会提示。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                TextButton(onClick = {
                    val install = Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA)
                    runCatching { context.startActivity(install) }.onFailure {
                        runCatching {
                            context.startActivity(Intent(TextToSpeech.Engine.ACTION_CHECK_TTS_DATA))
                        }
                    }
                }) {
                    Text("下载离线音色")
                }
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text("消息通知设置", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                SettingToggleRow(
                    title = "关心提醒推送",
                    checked = notificationEnabled,
                    onCheckedChange = viewModel::setNotificationEnabled,
                )
                HorizontalDivider(Modifier.padding(vertical = 8.dp))
                SettingToggleRow(
                    title = "提醒提示音",
                    checked = soundEnabled,
                    onCheckedChange = viewModel::setSoundEnabled,
                )
            }
        }

        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(onClick = onOpenAbout),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("关于APP", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                    Icon(
                        Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                }
                HorizontalDivider(Modifier.padding(vertical = 10.dp))
                SettingToggleRow(
                    title = "在地图上显示关心的人",
                    checked = showPartnerOnMap,
                    onCheckedChange = viewModel::setShowPartnerOnMap,
                )
            }
        }

        TechButton(
            text = "退出登录",
            onClick = { viewModel.logout(onLogout) },
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun SettingToggleRow(
    title: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(title, style = MaterialTheme.typography.bodyLarge)
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}
````

<a id="s05-5"></a>

## 步骤 05.5 · 关心建议与浪漫清单

建议卡片与 100 条浪漫清单的抽取、完成进度。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/advice/AdviceScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/advice/AdviceViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/romance/RomanceScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/romance/RomanceViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/advice/AdviceScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.advice

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.GoldDot
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.formatDateTime
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun AdviceScreen(
    viewModel: AdviceViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val advices by viewModel.advices.collectAsStateWithLifecycle()

    Column(Modifier.fillMaxSize()) {
        if (advices.isEmpty()) {
            Text(
                text = "暂无关心建议，等待云端生成",
                color = TextSecondary,
                modifier = Modifier.padding(16.dp),
            )
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(advices, key = { it.id }) { advice ->
                    AdviceItem(advice)
                }
            }
        }
    }
}

@Composable
private fun AdviceItem(advice: AdviceEntity) {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                GoldDot(size = 8)
                Spacer(Modifier.width(6.dp))
                Text(
                    text = "智能建议",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.secondary,
                )
            }
            Text(
                text = advice.content,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Text(
                text = formatDateTime(advice.timestamp),
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/advice/AdviceViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.advice

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.repository.AdviceRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.stateIn

@OptIn(ExperimentalCoroutinesApi::class)
class AdviceViewModel(
    adviceRepository: AdviceRepository,
    preferences: Preferences,
) : ViewModel() {

    val advices: StateFlow<List<AdviceEntity>> = preferences.currentDeviceId
        .flatMapLatest { id ->
            if (id.isBlank()) flowOf(emptyList())
            else adviceRepository.observeAdvice(id)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/romance/RomanceScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.romance

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.RomanceCategory
import com.shineleong.toughmind.data.model.RomanceIdea
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary

/**
 * 「一起做的一万件浪漫小事」：
 * 100 件具体灵感 + 分类 + 随机抽取 + 完成进度，完成的条目保存在本地。
 */
@Composable
fun RomanceScreen(
    viewModel: RomanceViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val doneIds by viewModel.doneIds.collectAsStateWithLifecycle()
    val category = viewModel.category
    val ideas = viewModel.visibleIdeas

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            RomanceHeaderCard(
                doneCount = doneIds.size,
                onDraw = viewModel::draw,
            )
        }
        item {
            CategoryRow(
                selected = category,
                onSelect = viewModel::selectCategory,
            )
        }
        items(ideas, key = { it.id }) { idea ->
            RomanceItem(
                idea = idea,
                done = idea.id in doneIds,
                onToggle = { viewModel.toggleDone(idea.id) },
            )
        }
        item { Spacer(Modifier.height(8.dp)) }
    }

    viewModel.picked?.let { picked ->
        RandomPickDialog(
            idea = picked,
            onConfirm = viewModel::markPickedDone,
            onShuffle = viewModel::draw,
            onDismiss = viewModel::dismissPick,
        )
    }
}

@Composable
private fun RomanceHeaderCard(
    doneCount: Int,
    onDraw: () -> Unit,
) {
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.Favorite,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(22.dp),
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = tr("一起做的一万件浪漫小事", "10,000 little romantic things"),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    modifier = Modifier.weight(1f),
                )
            }
            Text(
                text = tr(
                    "先从这一百件开始。完成的每一件，都会累计进你们的一万件。",
                    "Start with these one hundred. Every finished one counts toward your 10,000.",
                ),
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            Row(verticalAlignment = Alignment.Bottom) {
                Text(
                    text = "$doneCount",
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                )
                Text(
                    text = " / ${RomanceCatalog.TOTAL_GOAL}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                    modifier = Modifier.padding(bottom = 6.dp),
                )
            }
            ProgressBar(
                fraction = doneCount.toFloat() / RomanceCatalog.TOTAL_GOAL,
            )
            TextButton(onClick = onDraw, modifier = Modifier.align(Alignment.End)) {
                Icon(
                    Icons.Filled.AutoAwesome,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(tr("随机抽一件", "Draw one"))
            }
        }
    }
}

@Composable
private fun ProgressBar(fraction: Float) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(8.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(fraction.coerceIn(0f, 1f))
                .clip(RoundedCornerShape(4.dp))
                .background(
                    Brush.horizontalGradient(
                        listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.secondary)
                    )
                ),
        )
    }
}

@Composable
private fun CategoryRow(
    selected: RomanceCategory?,
    onSelect: (RomanceCategory?) -> Unit,
) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        item {
            FilterChip(
                selected = selected == null,
                onClick = { onSelect(null) },
                label = { Text(tr("全部", "All")) },
            )
        }
        items(RomanceCategory.entries) { category ->
            FilterChip(
                selected = selected == category,
                onClick = { onSelect(category) },
                label = { Text("${category.emoji} ${category.label}") },
            )
        }
    }
}

@Composable
private fun RomanceItem(
    idea: RomanceIdea,
    done: Boolean,
    onToggle: () -> Unit,
) {
    TechCard(
        modifier = Modifier.fillMaxWidth(),
        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onToggle),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "%04d".format(idea.id),
                style = MaterialTheme.typography.labelMedium,
                color = if (done) TextSecondary else MaterialTheme.colorScheme.primary,
                modifier = Modifier.width(44.dp),
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = idea.title,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (done) TextSecondary else TextPrimary,
                    textDecoration = if (done) TextDecoration.LineThrough else TextDecoration.None,
                )
                Text(
                    text = "${idea.category.emoji} ${idea.category.label}",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                )
            }
            Icon(
                imageVector = if (done) Icons.Filled.CheckCircle else Icons.Filled.RadioButtonUnchecked,
                contentDescription = if (done) tr("已完成", "Done") else tr("未完成", "Not done"),
                tint = if (done) MaterialTheme.colorScheme.tertiary else TextSecondary,
                modifier = Modifier.size(22.dp),
            )
        }
    }
}

@Composable
private fun RandomPickDialog(
    idea: RomanceIdea,
    onConfirm: () -> Unit,
    onShuffle: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                Icons.Filled.AutoAwesome,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
            )
        },
        title = { Text(tr("今天做这一件", "Do this one today")) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = "%04d · ${idea.category.emoji} ${idea.category.label}".format(idea.id),
                    style = MaterialTheme.typography.labelMedium,
                    color = TextSecondary,
                )
                Text(
                    text = idea.title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextPrimary,
                )
            }
        },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(tr("就做这件", "Do it"))
            }
        },
        dismissButton = {
            Row {
                TextButton(onClick = onShuffle) {
                    Text(tr("再抽一次", "Again"))
                }
                TextButton(onClick = onDismiss) {
                    Text(tr("关闭", "Close"))
                }
            }
        },
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/romance/RomanceViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.romance

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.RomanceCatalog
import com.shineleong.toughmind.data.model.RomanceCategory
import com.shineleong.toughmind.data.model.RomanceIdea
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/** 一起做的一万件浪漫小事：分类浏览、抽一件、完成状态本地保存。 */
class RomanceViewModel(
    private val preferences: Preferences,
) : ViewModel() {

    val doneIds: StateFlow<Set<Int>> = preferences.romanceDoneIds
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptySet())

    var category by mutableStateOf<RomanceCategory?>(null)
        private set

    /** 盲盒抽到的这一件；为空表示弹窗关闭。 */
    var picked by mutableStateOf<RomanceIdea?>(null)
        private set

    val visibleIdeas: List<RomanceIdea>
        get() = RomanceCatalog.byCategory(category)

    fun selectCategory(value: RomanceCategory?) {
        category = value
    }

    fun toggleDone(id: Int) {
        viewModelScope.launch { preferences.toggleRomanceDone(id) }
    }

    /** 从还没做的清单里抽一件；如果都做完了，就回看全部。 */
    fun draw() {
        val finished = doneIds.value
        val pending = RomanceCatalog.ideas.filterNot { it.id in finished }
        val pool = pending.ifEmpty { RomanceCatalog.ideas }
        picked = pool.random()
    }

    fun dismissPick() {
        picked = null
    }

    fun markPickedDone() {
        picked?.let { toggleDone(it.id) }
        picked = null
    }
}
````

---

返回索引：[README.md](README.md)
