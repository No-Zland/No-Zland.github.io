# 06 · 设备、宠物与智能体

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

设备作为一级入口管理多台关心设备；宠物小窝提供养成与场景互动；智能体以宠物外壳接入服务端 Ollama 本地模型，并带本地规则回退。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 设备管理](#s06-1) | 设备码绑定、设为当前、解绑与在线状态。 | 2 |
| [2. 宠物小窝](#s06-2) | 小屋/院子场景绘制、喂食、软垫、门与作息。 | 4 |
| [3. 智能体](#s06-3) | 对话界面、头像、语音播报与本地大脑。 | 4 |

本篇共 **3 个步骤 / 10 个文件**，按表格顺序写入即可还原对应代码。

<a id="s06-1"></a>

## 步骤 06.1 · 设备管理

设备码绑定、设为当前、解绑与在线状态。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/device/DeviceScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/device/DeviceViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/device/DeviceScreen.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.device

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.DeviceInfo
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.security.DeviceCodeCodec
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.formatDateTime
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.TextSecondary

@Composable
fun DeviceScreen(
    viewModel: DeviceViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
    ) {
        DeviceSection(viewModel = viewModel)
    }
}

/** 亲友与设备页内嵌的设备区块；不再单独占一个抽屉入口。 */
@Composable
fun DeviceSection(
    modifier: Modifier = Modifier,
    viewModel: DeviceViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val devices by viewModel.devices.collectAsStateWithLifecycle()
    val currentDeviceId by viewModel.currentDeviceId.collectAsStateWithLifecycle()
    val groupDevices by viewModel.groupDevices.collectAsStateWithLifecycle()
    val clipboard = LocalClipboardManager.current

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        TechCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("绑定设备", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "输入设备标签/屏幕上显示的一串设备码；设备码已加密并带校验位，不包含项目名或开发板型号。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                OutlinedTextField(
                    value = viewModel.inputDeviceCode,
                    onValueChange = viewModel::onInputDeviceCodeChange,
                    label = { Text("设备码") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedTextField(
                    value = viewModel.inputDeviceName,
                    onValueChange = viewModel::onInputDeviceNameChange,
                    label = { Text("设备名称（可选，如：TA 的车载设备）") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                viewModel.error?.let {
                    Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodyMedium)
                }
                viewModel.message?.let {
                    Text(it, color = LevelNormal, style = MaterialTheme.typography.bodyMedium)
                }
                TechButton(onClick = viewModel::bind, text = "绑定", modifier = Modifier.fillMaxWidth())
                TextButton(onClick = viewModel::createLocalDevice) {
                    Text("没有设备？生成一个本地演示设备")
                }
            }
        }

        if (devices.isEmpty()) {
            Text(
                text = "暂无绑定设备。输入设备码后，设备会出现在这里并同步到当前关心组。",
                color = TextSecondary,
            )
        } else {
            devices.forEach { device ->
                DeviceCard(
                    device = device,
                    isCurrent = device.deviceId == currentDeviceId,
                    onSelect = { viewModel.select(device.deviceId) },
                    onUnbind = { viewModel.unbind(device.deviceId) },
                    onCopyCode = { code -> clipboard.setText(AnnotatedString(code)) },
                )
            }
        }

        // 云端关心组里的 ESP32 设备：从「亲友」页移到这里统一管理。
        if (groupDevices.isNotEmpty()) {
            TechCard(modifier = Modifier.fillMaxWidth()) {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "关心组设备",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = "已加入当前云端关心组的 ESP32 设备，它们的在线状态、位置与驾驶信息会同步到关心页。",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    groupDevices.forEach { device ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Column(Modifier.weight(1f)) {
                                Text(
                                    text = device.name,
                                    style = MaterialTheme.typography.bodyMedium,
                                    fontWeight = FontWeight.SemiBold,
                                )
                                Text(
                                    text = "· ${device.relation}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = TextSecondary,
                                )
                            }
                            val (color, label) = if (device.online) {
                                LevelNormal to "在线"
                            } else {
                                Color(0xFF6B7A90) to "离线"
                            }
                            Text(text = label, color = color, fontWeight = FontWeight.Medium)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DeviceCard(
    device: DeviceInfo,
    isCurrent: Boolean,
    onSelect: () -> Unit,
    onUnbind: () -> Unit,
    onCopyCode: (String) -> Unit,
) {
    val deviceCode = remember(device.deviceId) { DeviceCodeCodec.generate(device.deviceId) }
    TechCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = device.deviceName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
                val (color, label) = if (device.isOnline) {
                    LevelNormal to "在线"
                } else {
                    Color(0xFF6B7A90) to "离线"
                }
                Text(text = label, color = color, fontWeight = FontWeight.Medium)
            }
            Text(
                text = "设备 ID：${device.deviceId}",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            Text(
                text = "设备码：$deviceCode",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(onClick = { onCopyCode(deviceCode) }) { Text("复制设备码") }
                TextButton(onClick = onUnbind) { Text("解绑", color = MaterialTheme.colorScheme.error) }
            }
            Text(
                text = "最后上报：${formatDateTime(device.lastOnlineTime)}",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (isCurrent) {
                    Text(
                        text = "当前设备",
                        color = MaterialTheme.colorScheme.secondary,
                        style = MaterialTheme.typography.labelLarge,
                        modifier = Modifier.align(Alignment.CenterVertically),
                    )
                } else {
                    OutlinedButton(
                        onClick = onSelect,
                        modifier = Modifier.height(AppDimens.ButtonHeight),
                        shape = AppDimens.ButtonShape,
                    ) { Text("设为当前") }
                }
                Spacer(Modifier.weight(1f))
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/device/DeviceViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.device

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.model.DeviceInfo
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.model.RemoteDevice
import com.shineleong.toughmind.data.security.DeviceCodeCodec
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.DeviceRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class DeviceViewModel(
    private val deviceRepository: DeviceRepository,
    private val careSyncRepository: CareSyncRepository,
) : ViewModel() {

    val devices: StateFlow<List<DeviceInfo>> =
        deviceRepository.devices.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val currentDeviceId: StateFlow<String> =
        deviceRepository.currentDeviceId.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "")

    /** 云端关心组里的 ESP32 成员；用来区分「已绑定」和「已进组」。 */
    val groupDevices: StateFlow<List<RemoteDevice>> = careSyncRepository.devices

    val groupActive: StateFlow<Boolean> = careSyncRepository.groupActive

    val inviteCode: StateFlow<String> = careSyncRepository.group
        .map { it?.group?.inviteCode.orEmpty() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "")

    var inputDeviceCode by mutableStateOf("")
    var inputDeviceName by mutableStateOf("")
    var error by mutableStateOf<String?>(null)
        private set
    var message by mutableStateOf<String?>(null)
        private set
    var syncingDeviceId by mutableStateOf<String?>(null)
        private set

    fun onInputDeviceCodeChange(value: String) {
        inputDeviceCode = value
    }

    fun onInputDeviceNameChange(value: String) {
        inputDeviceName = value
    }

    fun bind() {
        if (inputDeviceCode.isBlank()) {
            error = "请输入设备码"
            return
        }
        val deviceId = DeviceCodeCodec.decode(inputDeviceCode)
        if (deviceId == null) {
            error = "设备码无效，请检查是否完整复制"
            return
        }
        error = null
        message = null
        val code = inputDeviceCode.trim()
        val deviceName = inputDeviceName.trim()
        viewModelScope.launch {
            deviceRepository.bindDevice(
                deviceId = deviceId,
                deviceName = deviceName,
                deviceType = DeviceType.ESP32,
            )
            if (careSyncRepository.groupActive.value) {
                careSyncRepository.bindDeviceByCode(code, deviceName)
                    .onSuccess { message = "${deviceName.ifBlank { deviceId }} 已绑定并加入当前关心组" }
                    .onFailure { message = "设备已保存，但加入关心组失败：${it.message ?: "请稍后重试"}" }
            } else {
                message = "设备已保存；创建/加入关心组后可在设备页重新绑定入组。"
            }
            inputDeviceCode = ""
            inputDeviceName = ""
        }
    }

    /** 演示/调试用：生成一台本地设备，并显示它的设备码。 */
    fun createLocalDevice() {
        val deviceId = "D-" + java.util.UUID.randomUUID().toString()
            .replace("-", "").take(10).uppercase()
        viewModelScope.launch {
            deviceRepository.bindDevice(deviceId, "新设备", DeviceType.ESP32)
            message = "已生成设备，设备码：${DeviceCodeCodec.generate(deviceId)}"
        }
    }

    fun unbind(deviceId: String) {
        viewModelScope.launch { deviceRepository.unbind(deviceId) }
    }

    fun select(deviceId: String) {
        viewModelScope.launch { deviceRepository.setCurrentDevice(deviceId) }
    }

    /** 用当前关心组的邀请码把 ESP32 加入云端关心组。 */
    fun joinCloudGroup(device: DeviceInfo) {
        if (syncingDeviceId != null) return
        syncingDeviceId = device.deviceId
        error = null
        message = null
        viewModelScope.launch {
            careSyncRepository.joinDevice(device.deviceId, device.deviceName)
                .onSuccess { message = "${device.deviceName} 已加入云端关心组" }
                .onFailure { error = it.message ?: "加入关心组失败，请检查登录与网络" }
            syncingDeviceId = null
        }
    }

    /** 从云端关心组移除设备，本地绑定保留。 */
    fun leaveCloudGroup(device: DeviceInfo) {
        if (syncingDeviceId != null) return
        syncingDeviceId = device.deviceId
        error = null
        message = null
        viewModelScope.launch {
            careSyncRepository.removeDevice(device.deviceId)
                .onSuccess { message = "${device.deviceName} 已移出云端关心组" }
                .onFailure { error = it.message ?: "移出关心组失败，请稍后再试" }
            syncingDeviceId = null
        }
    }

    fun clearFeedback() {
        error = null
        message = null
    }
}
````

<a id="s06-2"></a>

## 步骤 06.2 · 宠物小窝

小屋/院子场景绘制、喂食、软垫、门与作息。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetNookScene.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetSheets.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetSpeech.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetNookScene.kt`

> 小屋/院子场景绘制：天空、草地、栅栏、食盆、门窗等。

````kotlin
package com.shineleong.toughmind.ui.screen.pet

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

// ═══════════════════════════════════════════════════════════════
// 场景绘制：一整张连续背景，而不是几块拼起来的色块
// ═══════════════════════════════════════════════════════════════

private data class YardPalette(
    val skyTop: Color,
    val skyMid: Color,
    val skyBottom: Color,
    val sun: Color,
    val glow: Color,
    val farHill: Color,
    val nearHill: Color,
    val grassTop: Color,
    val grassBottom: Color,
    val cloud: Color,
    val fence: Color,
    val fenceDark: Color,
    val treeDeep: Color,
    val treeMid: Color,
    val treeLight: Color,
    val trunk: Color,
    val night: Boolean,
    val starAlpha: Float,
)

private fun yardPalette(phase: PetDayPhase): YardPalette = when (phase) {
    PetDayPhase.DAWN -> YardPalette(
        skyTop = Color(0xFF5A6FB4),
        skyMid = Color(0xFFE49FA8),
        skyBottom = Color(0xFFFFDFB4),
        sun = Color(0xFFFFE3B0),
        glow = Color(0xFFFFB37A),
        farHill = Color(0xFF8C819C),
        nearHill = Color(0xFF6F806F),
        grassTop = Color(0xFFA3C57C),
        grassBottom = Color(0xFF729F65),
        cloud = Color(0xFFFFE8D8),
        fence = Color(0xFFBE8F69),
        fenceDark = Color(0xFF966A49),
        treeDeep = Color(0xFF356448),
        treeMid = Color(0xFF4E7F54),
        treeLight = Color(0xFF7AA868),
        trunk = Color(0xFF7A5638),
        night = false,
        starAlpha = 0.30f,
    )
    PetDayPhase.DAY -> YardPalette(
        skyTop = Color(0xFF63B8EA),
        skyMid = Color(0xFFA8DAF5),
        skyBottom = Color(0xFFEAF6F0),
        sun = Color(0xFFFFE9A9),
        glow = Color(0xFFFFD27A),
        farHill = Color(0xFF8DBA8F),
        nearHill = Color(0xFF6FA06C),
        grassTop = Color(0xFFA6D178),
        grassBottom = Color(0xFF6BA657),
        cloud = Color(0xFFFFFFFF),
        fence = Color(0xFFC79A6A),
        fenceDark = Color(0xFFA57A50),
        treeDeep = Color(0xFF3D7A46),
        treeMid = Color(0xFF579B52),
        treeLight = Color(0xFF7DBE63),
        trunk = Color(0xFF8A6240),
        night = false,
        starAlpha = 0f,
    )
    PetDayPhase.DUSK -> YardPalette(
        skyTop = Color(0xFF3B3A6B),
        skyMid = Color(0xFF9C5C78),
        skyBottom = Color(0xFFF09A6C),
        sun = Color(0xFFFFD08A),
        glow = Color(0xFFFF9B5E),
        farHill = Color(0xFF5D4C6C),
        nearHill = Color(0xFF4A5A58),
        grassTop = Color(0xFF7C9E68),
        grassBottom = Color(0xFF4E7555),
        cloud = Color(0xFFE8B8A8),
        fence = Color(0xFF9C7254),
        fenceDark = Color(0xFF7A553E),
        treeDeep = Color(0xFF2E4C3C),
        treeMid = Color(0xFF436547),
        treeLight = Color(0xFF648458),
        trunk = Color(0xFF674A32),
        night = true,
        starAlpha = 0.45f,
    )
    PetDayPhase.NIGHT -> YardPalette(
        skyTop = Color(0xFF0B1730),
        skyMid = Color(0xFF172B4D),
        skyBottom = Color(0xFF2E4A67),
        sun = Color(0xFFF4E7C3),
        glow = Color(0xFF9FC2FF),
        farHill = Color(0xFF1C3550),
        nearHill = Color(0xFF24425A),
        grassTop = Color(0xFF3F6A5A),
        grassBottom = Color(0xFF234238),
        cloud = Color(0xFF7287AA),
        fence = Color(0xFF7C6350),
        fenceDark = Color(0xFF5C493A),
        treeDeep = Color(0xFF1E4038),
        treeMid = Color(0xFF2B5547),
        treeLight = Color(0xFF3C6B57),
        trunk = Color(0xFF5A4334),
        night = true,
        starAlpha = 1f,
    )
}

internal fun DrawScope.drawHabitat(
    scene: PetScene,
    phase: PetDayPhase,
    drift: Float,
    twinkle: Float,
    firefly: Float,
) {
    when (scene) {
        PetScene.YARD -> drawYard(phase, drift, twinkle, firefly)
        PetScene.HOUSE -> drawHouse(phase, twinkle)
    }
}

private fun DrawScope.drawYard(
    phase: PetDayPhase,
    drift: Float,
    twinkle: Float,
    firefly: Float,
) {
    val w = size.width
    val h = size.height
    val p = yardPalette(phase)

    drawRect(
        brush = Brush.verticalGradient(
            colors = listOf(p.skyTop, p.skyMid, p.skyBottom),
            startY = 0f,
            endY = h * 0.70f,
        ),
    )
    if (p.starAlpha > 0f) drawStars(w, h, twinkle, p)
    drawCelestialBody(w, h, phase, p)
    if (!p.night) drawClouds(w, h, drift, p)
    drawHills(w, h, p)
    drawLawn(w, h, p)
    drawFence(w, h, p)
    drawTree(w, h, p)
    drawCottage(w, h, phase, p, drift)
    drawBush(w * 0.30f, h * 0.715f, w * 0.075f, p)
    drawFlowers(w, h, p)
    drawGrassTufts(w, h, p)
    drawBowl(w * 0.18f, h * 0.82f, w * 0.12f, phase)
    drawWaterBowl(w * 0.86f, h * 0.895f, w * 0.075f)
    if (p.night) drawFireflies(w, h, firefly)
    drawVignette(w, h, p.night)
}

private fun DrawScope.drawStars(w: Float, h: Float, twinkle: Float, p: YardPalette) {
    val stars = listOf(
        0.10f to 0.08f, 0.22f to 0.16f, 0.34f to 0.09f, 0.46f to 0.19f,
        0.58f to 0.07f, 0.64f to 0.22f, 0.73f to 0.10f, 0.88f to 0.20f,
        0.16f to 0.27f, 0.40f to 0.30f, 0.91f to 0.33f, 0.52f to 0.34f,
    )
    stars.forEachIndexed { index, (sx, sy) ->
        val pulse = (sin(twinkle * (PI * 2).toFloat() + index * 1.3f).toFloat() + 1f) / 2f
        drawCircle(
            color = Color(0xFFFFF3C9).copy(alpha = (0.18f + pulse * 0.55f) * p.starAlpha),
            radius = if (index % 3 == 0) w * 0.0035f else w * 0.0024f,
            center = Offset(w * sx, h * sy),
        )
    }
}

private fun DrawScope.drawCelestialBody(
    w: Float,
    h: Float,
    phase: PetDayPhase,
    p: YardPalette,
) {
    val night = phase == PetDayPhase.NIGHT
    val center = when (phase) {
        PetDayPhase.DAY -> Offset(w * 0.80f, h * 0.15f)
        PetDayPhase.DAWN -> Offset(w * 0.84f, h * 0.30f)
        PetDayPhase.DUSK -> Offset(w * 0.82f, h * 0.36f)
        PetDayPhase.NIGHT -> Offset(w * 0.80f, h * 0.14f)
    }
    val radius = if (night) w * 0.055f else w * 0.065f

    if (night) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(p.glow.copy(alpha = 0.28f), Color.Transparent),
                center = center,
                radius = radius * 3.8f,
            ),
            radius = radius * 3.8f,
            center = center,
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0xFFFFF8DC), Color(0xFFE8D6A4)),
                center = center,
                radius = radius,
            ),
            radius = radius,
            center = center,
        )
        drawCircle(
            color = Color(0x1F3B2E14),
            radius = radius * 0.18f,
            center = center + Offset(-radius * 0.30f, -radius * 0.24f),
        )
        drawCircle(
            color = Color(0x183B2E14),
            radius = radius * 0.11f,
            center = center + Offset(radius * 0.30f, radius * 0.12f),
        )
    } else {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(p.glow.copy(alpha = 0.55f), Color.Transparent),
                center = center,
                radius = radius * 4.2f,
            ),
            radius = radius * 4.2f,
            center = center,
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0xFFFFF6D5), p.sun),
                center = center,
                radius = radius,
            ),
            radius = radius,
            center = center,
        )
    }
}

private fun DrawScope.drawClouds(w: Float, h: Float, drift: Float, p: YardPalette) {
    val shift = drift * w * 0.16f
    drawCloud(
        x = w * 0.08f + shift,
        y = h * 0.20f,
        cloudW = w * 0.30f,
        cloudH = h * 0.040f,
        color = p.cloud.copy(alpha = if (p.night) 0.16f else 0.58f),
    )
    drawCloud(
        x = w * 0.48f + shift * 0.55f,
        y = h * 0.10f,
        cloudW = w * 0.24f,
        cloudH = h * 0.033f,
        color = p.cloud.copy(alpha = if (p.night) 0.12f else 0.44f),
    )
    drawCloud(
        x = w * 0.70f - shift * 0.35f,
        y = h * 0.28f,
        cloudW = w * 0.21f,
        cloudH = h * 0.027f,
        color = p.cloud.copy(alpha = if (p.night) 0.09f else 0.34f),
    )
}

private fun DrawScope.drawCloud(
    x: Float,
    y: Float,
    cloudW: Float,
    cloudH: Float,
    color: Color,
) {
    drawOval(color, Offset(x, y), Size(cloudW, cloudH))
    drawCircle(color, cloudH * 1.75f, Offset(x + cloudW * 0.28f, y + cloudH * 0.32f))
    drawCircle(color, cloudH * 1.35f, Offset(x + cloudW * 0.53f, y + cloudH * 0.10f))
    drawCircle(color, cloudH * 1.05f, Offset(x + cloudW * 0.76f, y + cloudH * 0.45f))
}

private fun DrawScope.drawHills(w: Float, h: Float, p: YardPalette) {
    val far = Path().apply {
        moveTo(0f, h * 0.52f)
        cubicTo(w * 0.18f, h * 0.44f, w * 0.34f, h * 0.55f, w * 0.53f, h * 0.49f)
        cubicTo(w * 0.71f, h * 0.43f, w * 0.85f, h * 0.53f, w, h * 0.47f)
        lineTo(w, h)
        lineTo(0f, h)
        close()
    }
    drawPath(far, p.farHill.copy(alpha = 0.92f))

    val near = Path().apply {
        moveTo(0f, h * 0.585f)
        cubicTo(w * 0.20f, h * 0.535f, w * 0.40f, h * 0.610f, w * 0.61f, h * 0.570f)
        cubicTo(w * 0.78f, h * 0.540f, w * 0.90f, h * 0.600f, w, h * 0.560f)
        lineTo(w, h)
        lineTo(0f, h)
        close()
    }
    drawPath(near, p.nearHill.copy(alpha = 0.96f))
}

private fun DrawScope.drawLawn(w: Float, h: Float, p: YardPalette) {
    val top = h * 0.605f
    val lawn = Path().apply {
        moveTo(0f, top + h * 0.015f)
        cubicTo(w * 0.20f, top - h * 0.026f, w * 0.42f, top + h * 0.022f, w * 0.62f, top - h * 0.008f)
        cubicTo(w * 0.78f, top - h * 0.028f, w * 0.90f, top + h * 0.014f, w, top - h * 0.004f)
        lineTo(w, h)
        lineTo(0f, h)
        close()
    }
    drawPath(
        path = lawn,
        brush = Brush.verticalGradient(
            colors = listOf(p.grassTop, p.grassBottom),
            startY = top - h * 0.04f,
            endY = h,
        ),
    )
    drawPath(
        path = Path().apply {
            moveTo(0f, top + h * 0.015f)
            cubicTo(w * 0.20f, top - h * 0.026f, w * 0.42f, top + h * 0.022f, w * 0.62f, top - h * 0.008f)
            cubicTo(w * 0.78f, top - h * 0.028f, w * 0.90f, top + h * 0.014f, w, top - h * 0.004f)
        },
        color = Color.White.copy(alpha = 0.13f),
        style = Stroke(width = h * 0.005f, cap = StrokeCap.Round),
    )
    // 远处的草色层次，让草地不是一块纯色。
    drawPath(
        path = Path().apply {
            moveTo(0f, top + h * 0.115f)
            cubicTo(w * 0.24f, top + h * 0.090f, w * 0.50f, top + h * 0.125f, w * 0.74f, top + h * 0.100f)
            cubicTo(w * 0.87f, top + h * 0.088f, w * 0.95f, top + h * 0.106f, w, top + h * 0.098f)
        },
        color = Color.White.copy(alpha = 0.045f),
        style = Stroke(width = h * 0.030f, cap = StrokeCap.Round),
    )
}

private fun DrawScope.drawFence(w: Float, h: Float, p: YardPalette) {
    val top = h * 0.555f
    val bottom = h * 0.665f
    val railHeight = h * 0.010f
    drawRoundRect(
        color = p.fence.copy(alpha = 0.85f),
        topLeft = Offset(0f, top + h * 0.030f),
        size = Size(w, railHeight),
        cornerRadius = CornerRadius(railHeight / 2f, railHeight / 2f),
    )
    drawRoundRect(
        color = p.fence.copy(alpha = 0.68f),
        topLeft = Offset(0f, top + h * 0.060f),
        size = Size(w, railHeight * 0.78f),
        cornerRadius = CornerRadius(railHeight / 2f, railHeight / 2f),
    )
    for (index in 0..10) {
        val x = w * (0.015f + index * 0.10f)
        val postTop = top + sin(index * 1.1f).toFloat() * h * 0.004f
        drawRoundRect(
            color = p.fenceDark,
            topLeft = Offset(x, postTop),
            size = Size(w * 0.018f, bottom - postTop),
            cornerRadius = CornerRadius(w * 0.005f, w * 0.005f),
        )
        drawRoundRect(
            color = p.fence,
            topLeft = Offset(x + w * 0.004f, postTop),
            size = Size(w * 0.011f, bottom - postTop),
            cornerRadius = CornerRadius(w * 0.004f, w * 0.004f),
        )
    }
}

private fun DrawScope.drawTree(w: Float, h: Float, p: YardPalette) {
    val cx = w * 0.13f
    val groundY = h * 0.77f
    val treeH = h * 0.36f

    drawOval(
        color = Color(0x22000000),
        topLeft = Offset(cx - w * 0.13f, groundY - h * 0.012f),
        size = Size(w * 0.26f, h * 0.036f),
    )
    val trunk = Path().apply {
        moveTo(cx - w * 0.022f, groundY)
        cubicTo(cx - w * 0.018f, groundY - treeH * 0.22f, cx - w * 0.012f, groundY - treeH * 0.36f, cx - w * 0.010f, groundY - treeH * 0.48f)
        lineTo(cx + w * 0.012f, groundY - treeH * 0.48f)
        cubicTo(cx + w * 0.016f, groundY - treeH * 0.32f, cx + w * 0.020f, groundY - treeH * 0.18f, cx + w * 0.026f, groundY)
        close()
    }
    drawPath(trunk, p.trunk)
    drawPath(
        path = Path().apply {
            moveTo(cx - w * 0.010f, groundY - treeH * 0.30f)
            lineTo(cx - w * 0.052f, groundY - treeH * 0.45f)
        },
        color = p.trunk,
        style = Stroke(width = w * 0.010f, cap = StrokeCap.Round),
    )
    drawPath(
        path = Path().apply {
            moveTo(cx + w * 0.010f, groundY - treeH * 0.33f)
            lineTo(cx + w * 0.050f, groundY - treeH * 0.47f)
        },
        color = p.trunk,
        style = Stroke(width = w * 0.009f, cap = StrokeCap.Round),
    )

    val canopyY = groundY - treeH * 0.72f
    drawCircle(p.treeDeep, w * 0.115f, Offset(cx + w * 0.005f, canopyY + h * 0.010f))
    drawCircle(p.treeMid, w * 0.096f, Offset(cx - w * 0.056f, canopyY - h * 0.008f))
    drawCircle(p.treeMid, w * 0.090f, Offset(cx + w * 0.080f, canopyY - h * 0.010f))
    drawCircle(p.treeLight, w * 0.075f, Offset(cx - w * 0.012f, canopyY - h * 0.038f))
    drawCircle(p.treeLight.copy(alpha = 0.82f), w * 0.050f, Offset(cx + w * 0.046f, canopyY - h * 0.050f))
    listOf(
        Offset(cx - w * 0.080f, canopyY - h * 0.020f),
        Offset(cx + w * 0.010f, canopyY - h * 0.055f),
        Offset(cx + w * 0.095f, canopyY + h * 0.010f),
        Offset(cx - w * 0.030f, canopyY + h * 0.035f),
    ).forEachIndexed { index, point ->
        drawCircle(
            color = p.treeLight.copy(alpha = 0.32f + (index % 2) * 0.12f),
            radius = w * 0.012f,
            center = point,
        )
    }
}

private fun DrawScope.drawCottage(
    w: Float,
    h: Float,
    phase: PetDayPhase,
    p: YardPalette,
    drift: Float,
) {
    val baseY = h * 0.665f
    val wallW = w * 0.30f
    val wallH = h * 0.19f
    val left = w * 0.80f
    val right = left + wallW
    val roofPeak = baseY - wallH - h * 0.10f

    drawOval(
        color = Color(0x22000000),
        topLeft = Offset(left - w * 0.03f, baseY - h * 0.012f),
        size = Size(wallW + w * 0.06f, h * 0.035f),
    )
    drawRoundRect(
        color = if (p.night) Color(0xFFD9C4A8) else Color(0xFFF6E7CE),
        topLeft = Offset(left, baseY - wallH),
        size = Size(wallW, wallH),
        cornerRadius = CornerRadius(w * 0.012f, w * 0.012f),
    )
    drawPath(
        path = Path().apply {
            moveTo(left - w * 0.035f, baseY - wallH + h * 0.010f)
            lineTo(left + wallW * 0.5f, roofPeak)
            lineTo(right + w * 0.035f, baseY - wallH + h * 0.010f)
            close()
        },
        color = if (p.night) Color(0xFF4D3B52) else Color(0xFF9A5F4A),
    )
    drawLine(
        color = (if (p.night) Color(0xFF6E5870) else Color(0xFFB87A60)).copy(alpha = 0.8f),
        start = Offset(left - w * 0.030f, baseY - wallH + h * 0.012f),
        end = Offset(left + wallW * 0.5f, roofPeak + h * 0.010f),
        strokeWidth = w * 0.006f,
        cap = StrokeCap.Round,
    )

    val doorW = wallW * 0.25f
    val doorH = h * 0.105f
    drawRoundRect(
        color = if (p.night) Color(0xFF6B4A33) else Color(0xFFB07A4E),
        topLeft = Offset(left + wallW * 0.56f, baseY - doorH),
        size = Size(doorW, doorH),
        cornerRadius = CornerRadius(w * 0.012f, w * 0.012f),
    )
    drawCircle(
        color = Color(0xFFE8C27A),
        radius = w * 0.007f,
        center = Offset(left + wallW * 0.56f + doorW * 0.78f, baseY - doorH * 0.48f),
    )

    val windowLeft = left + wallW * 0.14f
    val windowTop = baseY - h * 0.145f
    val windowW = wallW * 0.28f
    val windowH = h * 0.085f
    if (phase == PetDayPhase.NIGHT || phase == PetDayPhase.DUSK) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0x66FFD98A), Color.Transparent),
                center = Offset(windowLeft + windowW * 0.5f, windowTop + windowH * 0.5f),
                radius = w * 0.12f,
            ),
            radius = w * 0.12f,
            center = Offset(windowLeft + windowW * 0.5f, windowTop + windowH * 0.5f),
        )
    }
    drawRoundRect(
        color = if (p.night) Color(0xFFFFD98A) else Color(0xFFBEE6F5),
        topLeft = Offset(windowLeft, windowTop),
        size = Size(windowW, windowH),
        cornerRadius = CornerRadius(w * 0.008f, w * 0.008f),
    )
    drawRoundRect(
        color = if (p.night) Color(0xFF8A6547) else Color(0xFF8A5D3B),
        topLeft = Offset(windowLeft, windowTop),
        size = Size(windowW, windowH),
        cornerRadius = CornerRadius(w * 0.008f, w * 0.008f),
        style = Stroke(width = w * 0.007f),
    )
    drawLine(
        color = if (p.night) Color(0xFF8A6547) else Color(0xFF8A5D3B),
        start = Offset(windowLeft + windowW * 0.5f, windowTop),
        end = Offset(windowLeft + windowW * 0.5f, windowTop + windowH),
        strokeWidth = w * 0.006f,
    )
    drawLine(
        color = if (p.night) Color(0xFF8A6547) else Color(0xFF8A5D3B),
        start = Offset(windowLeft, windowTop + windowH * 0.5f),
        end = Offset(windowLeft + windowW, windowTop + windowH * 0.5f),
        strokeWidth = w * 0.006f,
    )

    val chimneyW = w * 0.034f
    val chimneyH = h * 0.075f
    drawRoundRect(
        color = if (p.night) Color(0xFF5A4656) else Color(0xFFA96850),
        topLeft = Offset(right - w * 0.070f, roofPeak + h * 0.020f),
        size = Size(chimneyW, chimneyH),
        cornerRadius = CornerRadius(w * 0.006f, w * 0.006f),
    )
    repeat(3) { index ->
        val t = (drift + index * 0.30f) % 1f
        drawCircle(
            color = Color.White.copy(alpha = (1f - t) * 0.16f),
            radius = w * (0.010f + t * 0.010f),
            center = Offset(
                right - w * 0.053f + t * w * 0.020f,
                roofPeak + h * 0.010f - t * h * 0.070f,
            ),
        )
    }
}

private fun DrawScope.drawBush(cx: Float, cy: Float, radius: Float, p: YardPalette) {
    drawOval(
        color = Color(0x22000000),
        topLeft = Offset(cx - radius * 1.4f, cy + radius * 0.72f),
        size = Size(radius * 2.8f, radius * 0.45f),
    )
    drawCircle(p.treeDeep, radius, Offset(cx, cy))
    drawCircle(p.treeMid, radius * 0.82f, Offset(cx - radius * 0.62f, cy + radius * 0.14f))
    drawCircle(p.treeMid, radius * 0.74f, Offset(cx + radius * 0.58f, cy + radius * 0.18f))
    drawCircle(p.treeLight.copy(alpha = 0.82f), radius * 0.52f, Offset(cx + radius * 0.18f, cy - radius * 0.36f))
}

private fun DrawScope.drawFlowers(w: Float, h: Float, p: YardPalette) {
    data class Flower(val x: Float, val y: Float, val color: Color)

    val flowers = listOf(
        Flower(w * 0.285f, h * 0.790f, Color(0xFFFFD166)),
        Flower(w * 0.365f, h * 0.845f, Color(0xFFFF9FB0)),
        Flower(w * 0.590f, h * 0.800f, Color(0xFFF7F4E8)),
        Flower(w * 0.760f, h * 0.835f, Color(0xFFFFC7D8)),
        Flower(w * 0.900f, h * 0.790f, Color(0xFFFFD166)),
    )
    flowers.forEach { flower ->
        drawLine(
            color = p.treeDeep.copy(alpha = 0.48f),
            start = Offset(flower.x, flower.y),
            end = Offset(flower.x, flower.y + h * 0.025f),
            strokeWidth = w * 0.004f,
            cap = StrokeCap.Round,
        )
        repeat(5) { index ->
            val angle = index * (PI * 2 / 5)
            drawCircle(
                color = flower.color.copy(alpha = 0.92f),
                radius = w * 0.0075f,
                center = Offset(
                    flower.x + cos(angle).toFloat() * w * 0.008f,
                    flower.y + sin(angle).toFloat() * w * 0.008f,
                ),
            )
        }
        drawCircle(Color(0xFFFFF3C4), w * 0.004f, Offset(flower.x, flower.y))
    }
}

private fun DrawScope.drawGrassTufts(w: Float, h: Float, p: YardPalette) {
    val tufts = listOf(
        0.045f to 0.705f, 0.23f to 0.760f, 0.34f to 0.900f, 0.48f to 0.740f,
        0.55f to 0.940f, 0.64f to 0.775f, 0.80f to 0.900f, 0.94f to 0.740f,
    )
    tufts.forEach { (x, y) ->
        val base = Offset(w * x, h * y)
        val color = p.treeDeep.copy(alpha = 0.36f)
        drawLine(color, base, base + Offset(-w * 0.012f, -h * 0.018f), w * 0.004f, cap = StrokeCap.Round)
        drawLine(color, base, base + Offset(w * 0.006f, -h * 0.022f), w * 0.004f, cap = StrokeCap.Round)
        drawLine(color, base, base + Offset(w * 0.015f, -h * 0.012f), w * 0.004f, cap = StrokeCap.Round)
    }
}

/** 宠物脚边的前景草，压住抠图边缘，让它真正站在草地里。 */
internal fun DrawScope.drawForegroundTufts(color: Color) {
    val w = size.width
    val h = size.height
    val tufts = listOf(
        0.28f to 0.965f, 0.36f to 0.985f, 0.43f to 0.970f,
        0.56f to 0.980f, 0.64f to 0.962f, 0.72f to 0.980f,
    )
    tufts.forEachIndexed { index, (x, y) ->
        val base = Offset(w * x, h * y)
        val alpha = 0.72f - (index % 2) * 0.12f
        drawLine(
            color = color.copy(alpha = alpha),
            start = base,
            end = base + Offset(-w * 0.012f, -h * 0.045f),
            strokeWidth = w * 0.006f,
            cap = StrokeCap.Round,
        )
        drawLine(
            color = color.copy(alpha = alpha * 0.85f),
            start = base,
            end = base + Offset(w * 0.005f, -h * 0.055f),
            strokeWidth = w * 0.005f,
            cap = StrokeCap.Round,
        )
        drawLine(
            color = color.copy(alpha = alpha * 0.70f),
            start = base,
            end = base + Offset(w * 0.016f, -h * 0.036f),
            strokeWidth = w * 0.004f,
            cap = StrokeCap.Round,
        )
    }
}

private fun DrawScope.drawBowl(
    cx: Float,
    cy: Float,
    diameter: Float,
    phase: PetDayPhase,
) {
    val bowlH = diameter * 0.42f
    drawOval(
        color = Color(0x22000000),
        topLeft = Offset(cx - diameter * 0.5f, cy + bowlH * 0.26f),
        size = Size(diameter, bowlH * 0.34f),
    )
    drawOval(
        color = if (phase == PetDayPhase.NIGHT) Color(0xFF5A4638) else Color(0xFF8A5A3B),
        topLeft = Offset(cx - diameter * 0.5f, cy),
        size = Size(diameter, bowlH),
    )
    drawOval(
        color = Color(0xFF6B4630),
        topLeft = Offset(cx - diameter * 0.42f, cy + bowlH * 0.12f),
        size = Size(diameter * 0.84f, bowlH * 0.55f),
    )
    drawOval(
        color = Color(0xFFE8B45A),
        topLeft = Offset(cx - diameter * 0.36f, cy + bowlH * 0.15f),
        size = Size(diameter * 0.72f, bowlH * 0.40f),
    )
    repeat(5) { index ->
        drawCircle(
            color = Color(0xFFC98A3A),
            radius = diameter * 0.032f,
            center = Offset(cx - diameter * 0.22f + index * diameter * 0.11f, cy + bowlH * 0.30f),
        )
    }
    drawArc(
        color = Color.White.copy(alpha = 0.18f),
        startAngle = 200f,
        sweepAngle = 80f,
        useCenter = false,
        topLeft = Offset(cx - diameter * 0.42f, cy + bowlH * 0.10f),
        size = Size(diameter * 0.84f, bowlH * 0.58f),
        style = Stroke(width = diameter * 0.012f, cap = StrokeCap.Round),
    )
}

private fun DrawScope.drawWaterBowl(
    cx: Float,
    cy: Float,
    diameter: Float,
) {
    val bowlH = diameter * 0.36f
    drawOval(
        color = Color(0x22000000),
        topLeft = Offset(cx - diameter * 0.5f, cy + bowlH * 0.22f),
        size = Size(diameter, bowlH * 0.32f),
    )
    drawOval(
        color = Color(0xFF7FA9C9),
        topLeft = Offset(cx - diameter * 0.5f, cy),
        size = Size(diameter, bowlH),
    )
    drawOval(
        color = Color(0xFF9FD3EA),
        topLeft = Offset(cx - diameter * 0.40f, cy + bowlH * 0.13f),
        size = Size(diameter * 0.80f, bowlH * 0.52f),
    )
    drawArc(
        color = Color.White.copy(alpha = 0.55f),
        startAngle = 205f,
        sweepAngle = 70f,
        useCenter = false,
        topLeft = Offset(cx - diameter * 0.30f, cy + bowlH * 0.20f),
        size = Size(diameter * 0.60f, bowlH * 0.34f),
        style = Stroke(width = diameter * 0.018f, cap = StrokeCap.Round),
    )
}

private fun DrawScope.drawFireflies(w: Float, h: Float, t: Float) {
    repeat(9) { index ->
        val x = w * (0.08f + index * 0.10f) + sin(t * (PI * 2).toFloat() + index * 1.7f) * w * 0.018f
        val y = h * (0.64f + (index % 4) * 0.06f) + cos(t * (PI * 2).toFloat() + index * 1.1f) * h * 0.014f
        val pulse = (sin(t * (PI * 4).toFloat() + index).toFloat() + 1f) / 2f
        drawCircle(
            color = Color(0x33FFE08A),
            radius = w * 0.014f,
            center = Offset(x, y),
        )
        drawCircle(
            color = Color(0xFFFFE7A0).copy(alpha = 0.32f + pulse * 0.55f),
            radius = w * 0.0045f,
            center = Offset(x, y),
        )
    }
}

private fun DrawScope.drawVignette(w: Float, h: Float, night: Boolean) {
    drawRect(
        brush = Brush.radialGradient(
            colors = listOf(Color.Transparent, Color.Black.copy(alpha = if (night) 0.22f else 0.10f)),
            center = Offset(w * 0.5f, h * 0.52f),
            radius = w * 0.92f,
        ),
    )
    if (night) {
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.16f)),
                startY = h * 0.86f,
                endY = h,
            ),
        )
    }
}

// 

// ---- 以下为从构建缓存恢复的尾部：drawHouse 与状态/文案辅助函数 ----

private fun DrawScope.drawHouse(phase: PetDayPhase, twinkle: Float) {
    val w = size.width
    val h = size.height
    val sky = yardPalette(phase)

    drawRect(
        brush = Brush.verticalGradient(
            colors = listOf(Color(0xFFF9F0E2), Color(0xFFECD8BC)),
            startY = 0f,
            endY = h * 0.66f,
        ),
    )
    // 墙面柔和的光斑
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color(0xFFFFF8E9).copy(alpha = 0.75f), Color.Transparent),
            center = Offset(w * 0.42f, h * 0.30f),
            radius = w * 0.46f,
        ),
        radius = w * 0.46f,
        center = Offset(w * 0.42f, h * 0.30f),
    )

    drawHouseWindow(w, h, phase, twinkle, sky)

    // 相框
    drawRoundRect(
        color = Color(0xFF9A6B46),
        topLeft = Offset(w * 0.47f, h * 0.455f),
        size = Size(w * 0.14f, h * 0.088f),
        cornerRadius = CornerRadius(w * 0.010f, w * 0.010f),
    )
    drawRect(
        color = Color(0xFFD7C2A0),
        topLeft = Offset(w * 0.485f, h * 0.470f),
        size = Size(w * 0.110f, h * 0.058f),
    )
    drawCircle(Color(0xFFE8A0A0), w * 0.012f, Offset(w * 0.520f, h * 0.492f))
    drawLine(Color(0xFF7FA86A), Offset(w * 0.545f, h * 0.520f), Offset(w * 0.560f, h * 0.485f), w * 0.006f)

    val floorTop = h * 0.66f
    drawRect(
        brush = Brush.verticalGradient(
            colors = listOf(Color(0xFFD2A574), Color(0xFFAE7D50)),
            startY = floorTop,
            endY = h,
        ),
        topLeft = Offset(0f, floorTop),
        size = Size(w, h - floorTop),
    )
    drawRect(
        color = Color(0xFFEAD9BF),
        topLeft = Offset(0f, floorTop - h * 0.014f),
        size = Size(w, h * 0.020f),
    )
    for (index in 1..4) {
        val y = floorTop + h * 0.070f * index
        drawLine(
            color = Color(0x227A4F2E),
            start = Offset(0f, y),
            end = Offset(w, y + h * 0.012f),
            strokeWidth = w * 0.003f,
        )
    }

    drawRoundRect(
        color = Color(0xFFB45F55),
        topLeft = Offset(w * 0.16f, h * 0.735f),
        size = Size(w * 0.66f, h * 0.190f),
        cornerRadius = CornerRadius(w * 0.34f, h * 0.095f),
    )
    drawRoundRect(
        color = Color(0xFFD98676),
        topLeft = Offset(w * 0.205f, h * 0.755f),
        size = Size(w * 0.57f, h * 0.150f),
        cornerRadius = CornerRadius(w * 0.30f, h * 0.075f),
    )
    drawOval(
        color = Color.White.copy(alpha = 0.10f),
        topLeft = Offset(w * 0.28f, h * 0.785f),
        size = Size(w * 0.44f, h * 0.080f),
    )

    // 右侧的门
    val doorLeft = w * 0.79f
    val doorTop = h * 0.405f
    val doorW = w * 0.15f
    val doorH = h * 0.255f
    drawRoundRect(
        color = Color(0xFF9E6B43),
        topLeft = Offset(doorLeft, doorTop),
        size = Size(doorW, doorH),
        cornerRadius = CornerRadius(w * 0.020f, w * 0.020f),
    )
    drawRoundRect(
        color = Color(0xFFB88353),
        topLeft = Offset(doorLeft + w * 0.012f, doorTop + h * 0.016f),
        size = Size(doorW - w * 0.024f, doorH - h * 0.032f),
        cornerRadius = CornerRadius(w * 0.014f, w * 0.014f),
    )
    drawRoundRect(
        color = Color(0xFF8D5E3C),
        topLeft = Offset(doorLeft + w * 0.020f, doorTop + h * 0.032f),
        size = Size(doorW - w * 0.040f, h * 0.075f),
        cornerRadius = CornerRadius(w * 0.010f, w * 0.010f),
    )
    drawCircle(
        color = Color(0xFFE8C27A),
        radius = w * 0.008f,
        center = Offset(doorLeft + doorW * 0.80f, doorTop + doorH * 0.54f),
    )

    // 沙发软垫
    drawRoundRect(
        color = Color(0xFFC7796B),
        topLeft = Offset(w * 0.73f, h * 0.625f),
        size = Size(w * 0.24f, h * 0.100f),
        cornerRadius = CornerRadius(w * 0.032f, w * 0.032f),
    )
    drawRoundRect(
        color = Color(0xFFE5A08E),
        topLeft = Offset(w * 0.745f, h * 0.645f),
        size = Size(w * 0.21f, h * 0.070f),
        cornerRadius = CornerRadius(w * 0.028f, w * 0.028f),
    )

    // 吊灯
    val lampX = w * 0.66f
    drawLine(
        color = Color(0xFF7B5A3A),
        start = Offset(lampX, 0f),
        end = Offset(lampX, h * 0.105f),
        strokeWidth = w * 0.004f,
    )
    drawPath(
        path = Path().apply {
            moveTo(lampX - w * 0.050f, h * 0.145f)
            lineTo(lampX + w * 0.050f, h * 0.145f)
            lineTo(lampX + w * 0.030f, h * 0.105f)
            lineTo(lampX - w * 0.030f, h * 0.105f)
            close()
        },
        color = Color(0xFFE8B45A),
    )
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color(0xFFFFD98A).copy(alpha = 0.32f), Color.Transparent),
            center = Offset(lampX, h * 0.165f),
            radius = w * 0.15f,
        ),
        radius = w * 0.15f,
        center = Offset(lampX, h * 0.165f),
    )
    drawCircle(Color(0xFFFFE9B0), w * 0.015f, Offset(lampX, h * 0.150f))

    // 角落的绿植
    drawRoundRect(
        color = Color(0xFFC47B52),
        topLeft = Offset(w * 0.045f, h * 0.585f),
        size = Size(w * 0.085f, h * 0.085f),
        cornerRadius = CornerRadius(w * 0.012f, w * 0.012f),
    )
    drawLine(
        color = Color(0xFF4C7A50),
        start = Offset(w * 0.088f, h * 0.590f),
        end = Offset(w * 0.088f, h * 0.500f),
        strokeWidth = w * 0.006f,
    )
    drawOval(Color(0xFF5D9160), Offset(w * 0.050f, h * 0.505f), Size(w * 0.075f, h * 0.045f))
    drawOval(Color(0xFF75A86A), Offset(w * 0.092f, h * 0.515f), Size(w * 0.070f, h * 0.040f))

    drawBowl(w * 0.20f, h * 0.855f, w * 0.11f, phase)
    drawWaterBowl(w * 0.80f, h * 0.900f, w * 0.08f)

    drawRect(
        brush = Brush.radialGradient(
            colors = listOf(Color.Transparent, Color(0x222A1608)),
            center = Offset(w * 0.5f, h * 0.52f),
            radius = w * 0.92f,
        ),
    )
}

private fun DrawScope.drawHouseWindow(
    w: Float,
    h: Float,
    phase: PetDayPhase,
    twinkle: Float,
    sky: YardPalette,
) {
    val left = w * 0.105f
    val top = h * 0.120f
    val windowW = w * 0.30f
    val windowH = h * 0.250f

    clipRect(left, top, left + windowW, top + windowH) {
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(sky.skyTop, sky.skyMid, sky.skyBottom),
                startY = top,
                endY = top + windowH,
            ),
            topLeft = Offset(left, top),
            size = Size(windowW, windowH),
        )
        if (sky.starAlpha > 0f) {
            repeat(7) { index ->
                val px = left + windowW * (0.12f + index * 0.115f)
                val py = top + windowH * (0.16f + (index % 3) * 0.18f)
                val pulse = (sin(twinkle * (PI * 2).toFloat() + index).toFloat() + 1f) / 2f
                drawCircle(
                    color = Color(0xFFFFF3C9).copy(alpha = (0.25f + pulse * 0.55f) * sky.starAlpha),
                    radius = w * 0.003f,
                    center = Offset(px, py),
                )
            }
        }
        val bodyX = left + windowW * 0.72f
        val bodyY = top + windowH * 0.28f
        val bodyR = windowW * 0.115f
        if (phase == PetDayPhase.NIGHT) {
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(Color(0xFFFFF8DC), Color(0xFFE8D6A4)),
                    center = Offset(bodyX, bodyY),
                    radius = bodyR,
                ),
                radius = bodyR,
                center = Offset(bodyX, bodyY),
            )
        } else {
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(Color(0xFFFFF6D5), sky.sun),
                    center = Offset(bodyX, bodyY),
                    radius = bodyR,
                ),
                radius = bodyR,
                center = Offset(bodyX, bodyY),
            )
        }
        drawPath(
            path = Path().apply {
                moveTo(left, top + windowH * 0.76f)
                cubicTo(
                    left + windowW * 0.28f, top + windowH * 0.62f,
                    left + windowW * 0.55f, top + windowH * 0.78f,
                    left + windowW, top + windowH * 0.65f,
                )
                lineTo(left + windowW, top + windowH)
                lineTo(left, top + windowH)
                close()
            },
            color = sky.farHill.copy(alpha = 0.78f),
        )
    }

    if (phase == PetDayPhase.NIGHT || phase == PetDayPhase.DUSK) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0x44FFD98A), Color.Transparent),
                center = Offset(left + windowW * 0.5f, top + windowH * 0.5f),
                radius = w * 0.17f,
            ),
            radius = w * 0.17f,
            center = Offset(left + windowW * 0.5f, top + windowH * 0.5f),
        )
    }

    drawRoundRect(
        color = Color(0xFF8A5D3B),
        topLeft = Offset(left, top),
        size = Size(windowW, windowH),
        cornerRadius = CornerRadius(w * 0.010f, w * 0.010f),
        style = Stroke(width = w * 0.010f),
    )
    drawLine(
        color = Color(0xFF8A5D3B),
        start = Offset(left + windowW * 0.5f, top),
        end = Offset(left + windowW * 0.5f, top + windowH),
        strokeWidth = w * 0.008f,
    )
    drawLine(
        color = Color(0xFF8A5D3B),
        start = Offset(left, top + windowH * 0.5f),
        end = Offset(left + windowW, top + windowH * 0.5f),
        strokeWidth = w * 0.008f,
    )
    drawRoundRect(
        color = Color(0xFFB0805A),
        topLeft = Offset(left - w * 0.014f, top + windowH - h * 0.006f),
        size = Size(windowW + w * 0.028f, h * 0.020f),
        cornerRadius = CornerRadius(w * 0.008f, w * 0.008f),
    )
    // 窗帘
    drawPath(
        path = Path().apply {
            moveTo(left - w * 0.020f, top - h * 0.025f)
            lineTo(left + w * 0.065f, top - h * 0.025f)
            cubicTo(left + w * 0.045f, top + h * 0.090f, left + w * 0.055f, top + h * 0.180f, left + w * 0.030f, top + h * 0.260f)
            lineTo(left - w * 0.020f, top + h * 0.260f)
            close()
        },
        color = Color(0xFFE7C4B8).copy(alpha = 0.82f),
    )
    drawPath(
        path = Path().apply {
            moveTo(left + windowW + w * 0.020f, top - h * 0.025f)
            lineTo(left + windowW - w * 0.065f, top - h * 0.025f)
            cubicTo(left + windowW - w * 0.045f, top + h * 0.090f, left + windowW - w * 0.055f, top + h * 0.180f, left + windowW - w * 0.030f, top + h * 0.260f)
            lineTo(left + windowW + w * 0.020f, top + h * 0.260f)
            close()
        },
        color = Color(0xFFE7C4B8).copy(alpha = 0.82f),
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetScreen.kt`

> 宠物小窝入口、领养流程与场景装配。

````kotlin
package com.shineleong.toughmind.ui.screen.pet

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

internal enum class PetScene {
    HOUSE,
    YARD,
}

/**
 * 宠物小窝：一整块连续的场景 + 压住场景边缘的信息卡。
 *
 * 场景本身负责天空、草地、小屋、院子和宠物，信息卡只作为场景的下半部分，
 * 不再用一块白底把页面切成互不相干的两截；宠物的透明背景也由 [PetLive2D] 保证。
 */
@Composable
fun PetScreen(
    viewModel: CareViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val pet by viewModel.pet.collectAsStateWithLifecycle()
    val petLoaded by viewModel.petLoaded.collectAsStateWithLifecycle()

    if (!petLoaded) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(tr("正在打开宠物小窝…", "Opening the pet nook…"), color = TextSecondary)
        }
        return
    }

    if (!pet.adopted) {
        PetAdoption(
            busy = viewModel.petBusy,
            onAdoptRandom = { viewModel.adoptRandom("") },
            onAdoptSnowy = { viewModel.adoptOwl(OwlSpecies.SNOWY, "雪团") },
        )
        return
    }

    var scene by rememberSaveable(pet.name) {
        mutableStateOf(if (pet.asleep) PetScene.HOUSE else PetScene.YARD)
    }
    var localNote by remember { mutableStateOf("") }
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }

    LaunchedEffect(Unit) {
        while (true) {
            now = System.currentTimeMillis()
            delay(1_000L)
        }
    }
    LaunchedEffect(pet.asleep) {
        if (pet.asleep) scene = PetScene.HOUSE
    }
    LaunchedEffect(localNote) {
        if (localNote.isNotBlank()) {
            delay(5_000L)
            localNote = ""
        }
    }

    val cooldownSeconds = ((OwlHabits.feedCooldownRemaining(pet, now) + 999L) / 1_000L).toInt()
    val feedLabel = when {
        viewModel.petBusy -> tr("稍等…", "One sec…")
        pet.asleep -> tr("先叫醒它", "Wake first")
        pet.isFull -> tr("它吃饱了", "Too full")
        pet.feedCountToday >= OwlHabits.DAILY_FEED_LIMIT -> tr("今日吃饱", "Done today")
        cooldownSeconds > 0 -> tr("消化 ${formatCooldown(cooldownSeconds)}", "Digest ${formatCooldown(cooldownSeconds)}")
        else -> tr("加粮", "Feed")
    }

    val sleepingNote = tr(
        "它睡着了，先摸摸把它叫醒吧。",
        "It's asleep. A gentle pet will wake it.",
    )
    val fullNote = tr(
        "它已经吃饱了，晚一点再喂也不迟。",
        "It's already full. Try again a little later.",
    )
    val dailyNote = tr(
        "今天的 ${OwlHabits.DAILY_FEED_LIMIT} 顿已经吃完了，明天再来。",
        "All ${OwlHabits.DAILY_FEED_LIMIT} meals are done for today. Come back tomorrow.",
    )
    val cooldownNote = tr(
        "还在消化，再等 ${formatCooldown(cooldownSeconds)} 吧。",
        "Still digesting. Wait ${formatCooldown(cooldownSeconds)}.",
    )
    val toHouseNote = tr("它跟着你回到小窝，把爪子收进了软垫。", "It follows you inside and curls up on the cushion.")
    val toYardNote = tr("它推开门，先去院子里转一圈。", "It pushes the door open and wanders into the yard.")
    val autoFeederNote = tr(
        "自动喂食机、饮水机会作为订阅服务开放，可远程补粮、换水。",
        "Auto feeders and water dispensers are coming as a subscription: refill food and water remotely.",
    )

    PetHome(
        pet = pet,
        scene = scene,
        phase = PetDayPhase.at(now),
        busy = viewModel.petBusy,
        message = viewModel.petMessage,
        messageSeconds = viewModel.petMessageSeconds,
        reaction = viewModel.petReaction,
        reactionToken = viewModel.petReactionToken,
        feedLabel = feedLabel,
        localNote = localNote,
        onFeed = {
            when {
                viewModel.petBusy -> Unit
                pet.asleep -> localNote = sleepingNote
                pet.isFull -> localNote = fullNote
                pet.feedCountToday >= OwlHabits.DAILY_FEED_LIMIT -> localNote = dailyNote
                cooldownSeconds > 0 -> localNote = cooldownNote
                else -> {
                    localNote = ""
                    viewModel.feedPet("self")
                }
            }
        },
        onPet = {
            if (!viewModel.petBusy) {
                localNote = ""
                viewModel.petOwl()
            }
        },
        onSwitchScene = { target ->
            if (target != scene) {
                if (target == PetScene.YARD && pet.asleep) {
                    localNote = sleepingNote
                } else {
                    scene = target
                    localNote = if (target == PetScene.HOUSE) toHouseNote else toYardNote
                }
            }
        },
        onOpenAutoFeeder = { localNote = autoFeederNote },
    )
}

@Composable
private fun PetAdoption(
    busy: Boolean,
    onAdoptRandom: () -> Unit,
    onAdoptSnowy: () -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(
                        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.65f),
                        MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f),
                        MaterialTheme.colorScheme.surface,
                    ),
                ),
            )
            .padding(24.dp),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Surface(
                shape = CircleShape,
                color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                shadowElevation = 14.dp,
                modifier = Modifier.size(104.dp),
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("🐾", fontSize = 46.sp)
                }
            }
            Spacer(Modifier.height(6.dp))
            Text(
                text = tr("领养一只小室友", "Adopt a little roommate"),
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
                textAlign = TextAlign.Center,
            )
            Text(
                text = tr(
                    "它会按自己的作息，在小窝和院子之间活动。",
                    "It keeps its own rhythm, moving between the nook and the yard.",
                ),
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Center,
            )
            Text(
                text = "🦉  🐈‍⬛  🐕  🐹",
                fontSize = 22.sp,
                modifier = Modifier.padding(vertical = 4.dp),
            )
            TechButton(
                text = tr("随机领养一只", "Adopt a random companion"),
                onClick = onAdoptRandom,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedButton(
                onClick = onAdoptSnowy,
                enabled = !busy,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(AppDimens.ButtonHeight),
                shape = AppDimens.ButtonShape,
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
            ) {
                Text(tr("先领养雪鸮「雪团」", "Adopt the snowy owl \"Snowball\""))
            }
        }
    }
}

@Composable
private fun PetHome(
    pet: PetState,
    scene: PetScene,
    phase: PetDayPhase,
    busy: Boolean,
    message: PetResultCode?,
    messageSeconds: Int,
    reaction: PetReaction,
    reactionToken: Int,
    feedLabel: String,
    localNote: String,
    onFeed: () -> Unit,
    onPet: () -> Unit,
    onSwitchScene: (PetScene) -> Unit,
    onOpenAutoFeeder: () -> Unit,
) {
    var actionSpeech by remember { mutableStateOf("") }
    var seenToken by remember { mutableIntStateOf(reactionToken) }
    val resultLine = message?.let { resultSpeech(it, pet, messageSeconds) }

    LaunchedEffect(reactionToken, message) {
        if (reactionToken == seenToken) return@LaunchedEffect
        seenToken = reactionToken
        val spoken = resultLine.orEmpty()
        actionSpeech = spoken
        if (spoken.isNotBlank()) {
            delay(5_200L)
            if (seenToken == reactionToken) actionSpeech = ""
        }
    }

    val idleLine = idleSpeech(pet, scene)
    val speech = when {
        actionSpeech.isNotBlank() -> actionSpeech
        localNote.isNotBlank() -> localNote
        else -> idleLine
    }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.surface),
    ) {
        val compact = maxHeight < 680.dp
        val heroHeight = if (compact) {
            (maxHeight * 0.52f).coerceIn(280.dp, 340.dp)
        } else {
            (maxHeight * 0.60f).coerceIn(370.dp, 580.dp)
        }
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
        ) {
            PetHero(
                pet = pet,
                scene = scene,
                phase = phase,
                reaction = reaction,
                reactionToken = reactionToken,
                speech = speech,
                compact = compact,
                onPet = onPet,
                onSwitchScene = onSwitchScene,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(heroHeight),
            )
            PetInfoSheet(
                pet = pet,
                scene = scene,
                busy = busy,
                compact = compact,
                speech = speech,
                feedLabel = feedLabel,
                onFeed = onFeed,
                onPet = onPet,
                onOpenAutoFeeder = onOpenAutoFeeder,
                modifier = Modifier
                    .fillMaxWidth()
                    .offset(y = (-26).dp),
            )
        }
    }
}

@Composable
private fun PetHero(
    pet: PetState,
    scene: PetScene,
    phase: PetDayPhase,
    reaction: PetReaction,
    reactionToken: Int,
    speech: String,
    compact: Boolean,
    onPet: () -> Unit,
    onSwitchScene: (PetScene) -> Unit,
    modifier: Modifier = Modifier,
) {
    val ambient = rememberInfiniteTransition(label = "pet-ambient")
    val drift by ambient.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(24_000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "cloud-drift",
    )
    val twinkle by ambient.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(4_000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "twinkle",
    )
    val firefly by ambient.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(7_000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "firefly",
    )

    val darkScene = scene == PetScene.YARD && (phase == PetDayPhase.NIGHT || phase == PetDayPhase.DUSK)
    val glassColor = if (darkScene) Color(0xCC101D36) else Color(0xE8FFFFFF)
    val glassText = if (darkScene) Color(0xFFF3F6FA) else Color(0xFF1B2433)
    val bubbleColor = if (darkScene) Color(0xE61A2742) else Color(0xF5FFFFFF)
    val bubbleText = if (darkScene) Color(0xFFF6F1E7) else Color(0xFF1B2433)
    val bubbleBorder = if (darkScene) Color.White.copy(alpha = 0.18f) else Color.Black.copy(alpha = 0.06f)

    BoxWithConstraints(modifier = modifier) {
        val petHeight = if (compact) {
            (maxHeight * 0.58f).coerceIn(170.dp, 210.dp)
        } else {
            (maxHeight * 0.52f).coerceIn(200.dp, 280.dp)
        }
        val petWidth = minOf(maxWidth - 20.dp, petHeight * 1.16f)
        val petBottom = if (compact) 40.dp else 68.dp
        val petFocus = if (compact) 1.30f else if (pet.species.isOwl) 1.10f else 1.18f
        val bubbleBottom = petBottom + petHeight * 0.78f + 8.dp

        Crossfade(
            targetState = scene,
            animationSpec = tween(520, easing = FastOutSlowInEasing),
            label = "pet-scene",
        ) { currentScene ->
            Canvas(Modifier.fillMaxSize()) {
                drawHabitat(
                    scene = currentScene,
                    phase = phase,
                    drift = drift,
                    twinkle = twinkle,
                    firefly = firefly,
                )
            }
        }

        // 宠物身后的柔光让深色宠物在夜色里也能和背景分开。
        Box(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = petBottom)
                .size(petWidth, petHeight),
        ) {
            val glow = when {
                scene == PetScene.HOUSE -> Color(0xFFFFD79A)
                darkScene -> Color(0xFF9FC2FF)
                else -> Color(0xFFFFF2D2)
            }
            Canvas(Modifier.fillMaxSize()) {
                // 先铺一层柔和的接触阴影，宠物才像站在草地上，而不是贴上去的。
                drawOval(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            Color.Black.copy(alpha = if (darkScene) 0.34f else 0.16f),
                            Color.Transparent,
                        ),
                        center = Offset(size.width * 0.5f, size.height * 0.91f),
                        radius = size.width * 0.46f,
                    ),
                    topLeft = Offset(size.width * 0.10f, size.height * 0.80f),
                    size = Size(size.width * 0.80f, size.height * 0.18f),
                )
                drawOval(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            glow.copy(alpha = if (darkScene) 0.20f else 0.18f),
                            Color.Transparent,
                        ),
                        center = Offset(size.width * 0.5f, size.height * 0.55f),
                        radius = size.width * 0.52f,
                    ),
                    topLeft = Offset(size.width * 0.04f, size.height * 0.10f),
                    size = Size(size.width * 0.92f, size.height * 0.82f),
                )
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(glow.copy(alpha = 0.28f), Color.Transparent),
                        center = Offset(size.width * 0.5f, size.height * 0.70f),
                        radius = size.width * 0.56f,
                    ),
                    radius = size.width * 0.56f,
                    center = Offset(size.width * 0.5f, size.height * 0.70f),
                )
            }
            PetLive2D(
                state = pet,
                reaction = reaction,
                reactionToken = reactionToken,
                phase = phase,
                modifier = Modifier.fillMaxSize(),
                contentDescription = tr(
                    "${pet.species.label}宠物，点一下摸摸它",
                    "${pet.species.englishLabel} pet. Tap to pet it.",
                ),
                onTap = onPet,
                backdrop = false,
                focus = petFocus,
            )
            if (scene == PetScene.YARD) {
                Canvas(Modifier.fillMaxSize()) {
                    drawForegroundTufts(
                        color = if (darkScene) Color(0xFF4E7A5D) else Color(0xFF6FA657),
                    )
                }
            }
        }

        // 小屏没有足够高度时，把这句话收进下方信息卡，避免气泡压住宠物的头。
        if (!compact) {
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(horizontal = 20.dp)
                    .padding(bottom = bubbleBottom)
                    .widthIn(max = 310.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Surface(
                    shape = RoundedCornerShape(18.dp),
                    color = bubbleColor,
                    contentColor = bubbleText,
                    shadowElevation = 8.dp,
                    border = BorderStroke(1.dp, bubbleBorder),
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 9.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(petMoodEmoji(pet), fontSize = 15.sp)
                        Spacer(Modifier.width(7.dp))
                        Text(
                            text = speech,
                            style = MaterialTheme.typography.bodySmall,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
                Canvas(Modifier.width(16.dp).height(7.dp)) {
                    drawPath(
                        path = Path().apply {
                            moveTo(0f, 0f)
                            lineTo(size.width, 0f)
                            lineTo(size.width * 0.5f, size.height)
                            close()
                        },
                        color = bubbleColor,
                    )
                }
            }
        }

        Row(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(start = 14.dp, top = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Surface(
                shape = RoundedCornerShape(50),
                color = glassColor,
                shadowElevation = 6.dp,
                border = BorderStroke(1.dp, Color.White.copy(alpha = if (darkScene) 0.14f else 0.65f)),
            ) {
                Row(
                    modifier = Modifier.padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(2.dp),
                ) {
                    PetScene.entries.forEach { option ->
                        SceneTab(
                            label = if (option == PetScene.HOUSE) {
                                tr("小窝", "Nook")
                            } else {
                                tr("院子", "Yard")
                            },
                            selected = scene == option,
                            textColor = glassText,
                            onClick = { onSwitchScene(option) },
                        )
                    }
                }
            }
        }

        Surface(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(end = 14.dp, top = 14.dp),
            shape = RoundedCornerShape(50),
            color = glassColor,
            border = BorderStroke(1.dp, Color.White.copy(alpha = if (darkScene) 0.14f else 0.65f)),
            shadowElevation = 4.dp,
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 11.dp, vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "${phaseEmoji(phase)} ${phaseLabel(phase)}",
                    style = MaterialTheme.typography.labelMedium,
                    color = glassText,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetSheets.kt`

> 场景切换、宠物信息抽屉、喂食按钮与状态环。

````kotlin
package com.shineleong.toughmind.ui.screen.pet

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

@Composable
internal fun SceneTab(
    label: String,
    selected: Boolean,
    textColor: Color,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(50)
    val accent = LocalCareColors.current.accentGradient
    Box(
        modifier = Modifier
            .clip(shape)
            .then(
                if (selected) {
                    Modifier.background(Brush.linearGradient(accent), shape)
                } else {
                    Modifier
                },
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 15.dp, vertical = 7.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            color = if (selected) Color.White else textColor,
        )
    }
}

@Composable
internal fun PetInfoSheet(
    pet: PetState,
    scene: PetScene,
    busy: Boolean,
    compact: Boolean,
    speech: String,
    feedLabel: String,
    onFeed: () -> Unit,
    onPet: () -> Unit,
    onOpenAutoFeeder: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val shape = RoundedCornerShape(topStart = 30.dp, topEnd = 30.dp)
    val displayName = pet.name.ifBlank { defaultPetName(pet.species) }
    val activity = when {
        pet.asleep -> tr("在窝里打盹", "napping inside")
        scene == PetScene.HOUSE -> tr("在小窝休息", "resting inside")
        else -> tr("在院子活动", "out in the yard")
    }
    val lastFed = if (pet.lastFedBy.isBlank()) {
        tr("还没人喂过", "No meals yet")
    } else {
        val fedBy = when (pet.lastFedBy) {
            "self", "我", "Me" -> tr("我", "Me")
            else -> pet.lastFedBy
        }
        tr("上次：$fedBy", "Last: $fedBy")
    }
    val meals = tr(
        "今日已喂 ${pet.feedCountToday}/${OwlHabits.DAILY_FEED_LIMIT} 顿",
        "Meals today ${pet.feedCountToday}/${OwlHabits.DAILY_FEED_LIMIT}",
    )

    Surface(
        modifier = modifier,
        shape = shape,
        color = MaterialTheme.colorScheme.surface,
        contentColor = TextPrimary,
        shadowElevation = 22.dp,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.38f)),
    ) {
        Column(
            modifier = Modifier.padding(
                horizontal = if (compact) 18.dp else 20.dp,
                vertical = if (compact) 9.dp else 13.dp,
            ),
            verticalArrangement = Arrangement.spacedBy(if (compact) 6.dp else 12.dp),
        ) {
            if (!compact) {
                Box(
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .width(38.dp)
                        .height(4.dp)
                        .clip(RoundedCornerShape(50))
                        .background(MaterialTheme.colorScheme.outline.copy(alpha = 0.55f)),
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    if (!compact) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(CircleShape)
                                    .background(if (pet.asleep) LevelNormal.copy(alpha = 0.55f) else Color(0xFF4ADE80)),
                            )
                            Spacer(Modifier.width(6.dp))
                            Text(
                                text = "LIVE 2D · ${tr(pet.species.label, pet.species.englishLabel)}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                        Spacer(Modifier.height(2.dp))
                    }
                    Text(
                        text = displayName,
                        style = if (compact) {
                            MaterialTheme.typography.titleLarge
                        } else {
                            MaterialTheme.typography.headlineSmall
                        },
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                    Text(
                        text = if (compact) {
                            "${roommateTag(pet.species)} · $activity · $meals"
                        } else {
                            "${roommateTag(pet.species)} · $activity"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
                Surface(
                    shape = RoundedCornerShape(50),
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.10f),
                    contentColor = MaterialTheme.colorScheme.primary,
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            Icons.Filled.Favorite,
                            contentDescription = null,
                            modifier = Modifier.size(14.dp),
                        )
                        Spacer(Modifier.width(4.dp))
                        Text(
                            text = "Lv.${pet.bondLevel}",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }

            if (compact) {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.07f),
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(petMoodEmoji(pet), fontSize = 13.sp)
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = speech,
                            style = MaterialTheme.typography.bodySmall,
                            color = TextPrimary,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                PetStatRing(
                    label = tr("饱腹", "Fullness"),
                    value = pet.satiety,
                    color = Color(0xFFF2B84B),
                    compact = compact,
                    modifier = Modifier.weight(1f),
                )
                PetStatRing(
                    label = tr("精力", "Energy"),
                    value = pet.energy,
                    color = Color(0xFF4FC3D9),
                    compact = compact,
                    modifier = Modifier.weight(1f),
                )
                PetStatRing(
                    label = tr("心情", "Mood"),
                    value = pet.mood,
                    color = Color(0xFFFF7CA8),
                    compact = compact,
                    modifier = Modifier.weight(1f),
                )
            }

            if (!compact) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = meals,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    Spacer(Modifier.weight(1f))
                    Text(
                        text = lastFed,
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary.copy(alpha = 0.85f),
                    )
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                FeedButton(
                    text = feedLabel,
                    enabled = !busy,
                    height = AppDimens.ButtonHeight,
                    onClick = onFeed,
                    modifier = Modifier.weight(1f),
                )
                OutlinedButton(
                    onClick = onPet,
                    enabled = !busy,
                    modifier = Modifier
                        .weight(1f)
                        .height(AppDimens.ButtonHeight),
                    shape = RoundedCornerShape(AppDimens.ButtonCorner),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.34f)),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = MaterialTheme.colorScheme.primary,
                    ),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Icon(
                        imageVector = if (pet.asleep) Icons.Filled.WbSunny else Icons.Filled.PanTool,
                        contentDescription = null,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                    Spacer(Modifier.width(7.dp))
                    Text(
                        text = if (pet.asleep) {
                            tr("叫醒", "Wake")
                        } else {
                            tr("抚摸", "Pet")
                        },
                        fontWeight = FontWeight.SemiBold,
                        maxLines = 1,
                    )
                }
            }

            if (!compact) {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .clickable(onClick = onOpenAutoFeeder),
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.52f),
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            modifier = Modifier
                                .size(34.dp)
                                .clip(CircleShape)
                                .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.10f)),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text("🍽️", fontSize = 16.sp)
                        }
                        Spacer(Modifier.width(10.dp))
                        Column(Modifier.weight(1f)) {
                            Text(
                                text = tr("自动喂食机 / 饮水机", "Auto feeder / water dispenser"),
                                style = MaterialTheme.typography.labelLarge,
                                fontWeight = FontWeight.SemiBold,
                                color = TextPrimary,
                            )
                            Text(
                                text = tr("订阅服务筹备中", "Subscription in preparation"),
                                style = MaterialTheme.typography.labelSmall,
                                color = TextSecondary,
                            )
                        }
                        Text(
                            text = tr("了解", "Learn more"),
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FeedButton(
    text: String,
    enabled: Boolean,
    height: Dp,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val shape = RoundedCornerShape(AppDimens.ButtonCorner)
    val accent = LocalCareColors.current.accentGradient
    Surface(
        onClick = onClick,
        enabled = enabled,
        shape = shape,
        color = Color.Transparent,
        contentColor = Color.White,
        shadowElevation = 7.dp,
        modifier = modifier
            .height(height)
            .alpha(if (enabled) 1f else 0.62f),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Brush.linearGradient(accent), shape)
                .padding(horizontal = AppDimens.ContentPaddingHorizontal),
            contentAlignment = Alignment.Center,
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.Restaurant,
                    contentDescription = null,
                    modifier = Modifier.size(AppDimens.IconSize),
                )
                Spacer(Modifier.width(7.dp))
                Text(
                    text = text,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}

@Composable
private fun PetStatRing(
    label: String,
    value: Int,
    color: Color,
    compact: Boolean,
    modifier: Modifier = Modifier,
) {
    val ringSize = if (compact) 50.dp else 58.dp
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(3.dp),
    ) {
        Box(modifier = Modifier.size(ringSize), contentAlignment = Alignment.Center) {
            Canvas(Modifier.fillMaxSize()) {
                val stroke = (if (compact) 4.5.dp else 5.dp).toPx()
                val inset = stroke / 2f
                val arcSize = Size(size.width - stroke, size.height - stroke)
                drawArc(
                    color = color.copy(alpha = 0.15f),
                    startAngle = -90f,
                    sweepAngle = 360f,
                    useCenter = false,
                    topLeft = Offset(inset, inset),
                    size = arcSize,
                    style = Stroke(width = stroke, cap = StrokeCap.Round),
                )
                drawArc(
                    color = color,
                    startAngle = -90f,
                    sweepAngle = 360f * (value.coerceIn(0, 100) / 100f),
                    useCenter = false,
                    topLeft = Offset(inset, inset),
                    size = arcSize,
                    style = Stroke(width = stroke, cap = StrokeCap.Round),
                )
            }
            Text(
                text = value.toString(),
                style = if (compact) {
                    MaterialTheme.typography.titleSmall
                } else {
                    MaterialTheme.typography.titleMedium
                },
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
        }
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary,
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/pet/PetSpeech.kt`

> 宠物台词、作息阶段文案与冷却格式化。

````kotlin
package com.shineleong.toughmind.ui.screen.pet

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.PanTool
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.OwlHabits
import com.shineleong.toughmind.data.model.OwlMood
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetDayPhase
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetResultCode
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.screen.care.CareViewModel
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

//

@Composable
internal fun idleSpeech(pet: PetState, scene: PetScene): String {
    if (pet.asleep) {
        return tr(
            "蜷在软垫里，呼吸慢慢变匀了。",
            "Curled up on the cushion, breathing slowly.",
        )
    }
    return when {
        pet.satiety <= 28 -> tr(
            "食盆空了一会儿，它时不时抬头看你。",
            "The bowl has been empty for a while; it keeps glancing up at you.",
        )
        pet.energy <= 26 -> tr(
            "它打了个哈欠，眼皮快要撑不住了。",
            "It yawns, eyelids already drooping.",
        )
        pet.overfed -> tr(
            "吃得有点撑，正趴着慢慢消化。",
            "A little too full, lying down to digest.",
        )
        OwlHabits.moodOf(pet) == OwlMood.HAPPY -> tr(
            "心情很好，尾巴尖轻轻晃着。",
            "In a lovely mood, tail tip swaying.",
        )
        scene == PetScene.HOUSE -> tr(
            "在窝里转了一圈，又回到你脚边。",
            "It pads around the nook and comes back to your feet.",
        )
        else -> tr(
            "在院子里追一片落叶，玩得很专注。",
            "Chasing a falling leaf in the yard, utterly focused.",
        )
    }
}

@Composable
internal fun resultSpeech(code: PetResultCode, pet: PetState, seconds: Int): String = when (code) {
    PetResultCode.FED -> tr(
        "好吃！它把粮吃得干干净净。",
        "Delicious! It licks the bowl clean.",
    )
    PetResultCode.FED_OVER -> tr(
        "吃得有点撑，它想慢慢消化一会儿。",
        "A bit too much — it wants to digest slowly.",
    )
    PetResultCode.REFUSED_SLEEPING -> tr(
        "它睡着了，先摸摸把它叫醒吧。",
        "It's asleep. A gentle pet will wake it.",
    )
    PetResultCode.REFUSED_FULL -> tr(
        "已经饱了（${pet.satiety}），晚点再喂也不迟。",
        "Already full (${pet.satiety}). Later is fine.",
    )
    PetResultCode.REFUSED_COOLDOWN -> tr(
        "还在消化，再等 ${formatCooldown(seconds)} 吧。",
        "Still digesting. Wait ${formatCooldown(seconds)}.",
    )
    PetResultCode.REFUSED_DAILY_LIMIT -> tr(
        "今天的 ${OwlHabits.DAILY_FEED_LIMIT} 顿已经吃完了，明天再来。",
        "All ${OwlHabits.DAILY_FEED_LIMIT} meals are done for today. Come back tomorrow.",
    )
    PetResultCode.PETTED -> tr(
        "它眯起眼睛，往你手心里蹭了蹭。",
        "It narrows its eyes and leans into your hand.",
    )
    PetResultCode.PET_ANNOYED -> tr(
        "摸得太急啦，它甩了甩耳朵。",
        "Too quick! It flicks its ears at you.",
    )
    PetResultCode.WOKEN -> tr(
        "它被你叫醒了，伸了个懒腰。",
        "It wakes up and stretches.",
    )
}

@Composable
internal fun phaseLabel(phase: PetDayPhase): String = when (phase) {
    PetDayPhase.DAWN -> tr("清晨", "Dawn")
    PetDayPhase.DAY -> tr("白天", "Day")
    PetDayPhase.DUSK -> tr("黄昏", "Dusk")
    PetDayPhase.NIGHT -> tr("深夜", "Night")
}

internal fun phaseEmoji(phase: PetDayPhase): String = when (phase) {
    PetDayPhase.DAWN -> "🌅"
    PetDayPhase.DAY -> "☀️"
    PetDayPhase.DUSK -> "🌇"
    PetDayPhase.NIGHT -> "🌙"
}

@Composable
fun roommateTag(species: OwlSpecies): String = when (species) {
    OwlSpecies.SNOWY -> tr("极夜小室友", "polar-night roommate")
    OwlSpecies.INK_CAT -> tr("夜巡小室友", "night-patrol roommate")
    OwlSpecies.RURAL_DOG -> tr("看家小室友", "little guardian")
    OwlSpecies.HAMSTER -> tr("囤粮小室友", "tiny hoarder")
    else -> tr("夜班小室友", "night-shift roommate")
}

@Composable
internal fun defaultPetName(species: OwlSpecies): String = when (species) {
    OwlSpecies.SNOWY -> tr("雪团", "Snowball")
    OwlSpecies.INK_CAT -> tr("墨墨", "Inky")
    OwlSpecies.RURAL_DOG -> tr("阿黄", "Rusty")
    OwlSpecies.HAMSTER -> tr("团子", "Mochi")
    else -> tr("鸮鸮", "Hoo")
}

internal fun petMoodEmoji(pet: PetState): String = when (OwlHabits.moodOf(pet)) {
    OwlMood.ASLEEP -> "💤"
    OwlMood.HUNGRY -> "🍽️"
    OwlMood.SLEEPY -> "😪"
    OwlMood.OVERFED -> "🤭"
    OwlMood.ANNOYED -> "😾"
    OwlMood.HAPPY -> "💛"
    OwlMood.CONTENT -> "🙂"
}

internal fun formatCooldown(seconds: Int): String {
    val safe = seconds.coerceAtLeast(0)
    val minutes = safe / 60
    val rest = safe % 60
    return "${minutes.toString().padStart(2, '0')}:${rest.toString().padStart(2, '0')}"
}
````

<a id="s06-3"></a>

## 步骤 06.3 · 智能体

对话界面、头像、语音播报与本地大脑。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiAvatar.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiSpeaker.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiViewModel.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiAvatar.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.xiaozhi

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.sin

/** 小智的四种状态，决定眼睛、嘴、光环和浮点动的节奏。 */
enum class XiaozhiMood {
    IDLE,
    LISTENING,
    THINKING,
    SPEAKING,
}

/**
 * 小智的新形象：一颗会呼吸的“光核”，而不是方头方脑的机器人。
 * 保留眨眼、视线、说话嘴型、倾听波纹和思考光点，整体更轻、更干净。
 */
@Composable
fun XiaozhiAvatar(
    mood: XiaozhiMood,
    mouthOpen: Float,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
) {
    val idle = rememberInfiniteTransition(label = "xiaozhi-idle")
    val bob by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(3_000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "xiaozhi-bob",
    )
    val blink by idle.animateFloat(
        initialValue = 1f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 5_400
                1f at 0
                1f at 4_820
                0.06f at 4_920
                0.06f at 4_980
                1f at 5_060
                1f at 5_400
            },
            repeatMode = RepeatMode.Restart,
        ),
        label = "xiaozhi-blink",
    )
    val pulse by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2_400, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "xiaozhi-pulse",
    )
    val wave by idle.animateFloat(
        initialValue = 0f,
        targetValue = (PI * 2).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(1_100, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "xiaozhi-wave",
    )
    val thinkingPhase by idle.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1_400, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "xiaozhi-thinking",
    )

    val scheme = MaterialTheme.colorScheme
    val glow = when (mood) {
        XiaozhiMood.THINKING -> scheme.tertiary
        XiaozhiMood.LISTENING -> scheme.secondary
        XiaozhiMood.SPEAKING -> scheme.primary
        XiaozhiMood.IDLE -> scheme.primary
    }
    val coreTop = lerp(scheme.primary, Color.White, 0.78f)
    val coreBottom = lerp(scheme.primary, Color.White, 0.26f)
    val faceColor = Color(0xFF101A2C)
    val eyeColor = Color(0xFFC7F6FF)

    Box(modifier = modifier) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .semantics { contentDescription = "小智，点一下和它打招呼" }
                .then(
                    if (onClick != null) {
                        Modifier.pointerInput(Unit) {
                            detectTapGestures(onTap = { onClick() })
                        }
                    } else {
                        Modifier
                    }
                )
        ) {
            if (size.minDimension <= 0f) return@Canvas
            val unit = size.minDimension / 220f
            val centerX = size.width / 2f
            val centerY = size.height / 2f + (bob - 0.5f) * 7f
            val speaking = mood == XiaozhiMood.SPEAKING
            val active = mood != XiaozhiMood.IDLE
            val mouth = mouthOpen.coerceIn(0f, 1f)

            withTransform({
                translate(centerX, centerY)
                scale(unit, unit, Offset.Zero)
            }) {
                // 柔和光晕
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            glow.copy(alpha = if (speaking) 0.34f else 0.22f),
                            glow.copy(alpha = 0.07f),
                            Color.Transparent,
                        ),
                        center = Offset.Zero,
                        radius = 128f,
                    ),
                    radius = 128f,
                    center = Offset.Zero,
                )

                // 地面投影
                drawOval(
                    color = Color.Black.copy(alpha = 0.14f),
                    topLeft = Offset(-48f, 86f),
                    size = Size(96f, 13f),
                )

                // 倾听/说话时的波纹
                if (active) {
                    repeat(2) { ring ->
                        val phase = (pulse + ring * 0.5f) % 1f
                        drawCircle(
                            color = glow.copy(alpha = (1f - phase) * 0.22f),
                            radius = 68f + phase * 34f,
                            style = Stroke(width = 1.4f),
                            center = Offset.Zero,
                        )
                    }
                }

                // 说话/思考时缓慢旋转的光弧
                if (active) {
                    rotate(pulse * 360f) {
                        drawArc(
                            brush = Brush.sweepGradient(
                                colors = listOf(
                                    Color.Transparent,
                                    glow.copy(alpha = 0.62f),
                                    Color.Transparent,
                                ),
                                center = Offset.Zero,
                            ),
                            startAngle = 0f,
                            sweepAngle = 250f,
                            useCenter = false,
                            topLeft = Offset(-82f, -82f),
                            size = Size(164f, 164f),
                            style = Stroke(width = 2f, cap = StrokeCap.Round),
                        )
                    }
                }

                // 光核本体
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(coreTop, coreBottom),
                        center = Offset(-18f, -24f),
                        radius = 90f,
                    ),
                    radius = 68f,
                    center = Offset.Zero,
                )
                drawCircle(
                    color = Color.White.copy(alpha = 0.45f),
                    radius = 68f,
                    style = Stroke(width = 1.6f),
                    center = Offset.Zero,
                )
                // 顶部高光
                drawOval(
                    color = Color.White.copy(alpha = 0.38f),
                    topLeft = Offset(-36f, -55f),
                    size = Size(50f, 17f),
                )

                // 面屏（深色，衬托眼睛）
                drawCircle(
                    color = faceColor.copy(alpha = 0.92f),
                    radius = 36f,
                    center = Offset.Zero,
                )
                drawCircle(
                    color = glow.copy(alpha = 0.28f),
                    radius = 36f,
                    style = Stroke(width = 1.2f),
                    center = Offset.Zero,
                )

                // 眼睛
                val eyeHeight = (15f * blink).coerceAtLeast(0f)
                val lookX = if (mood == XiaozhiMood.THINKING) 2f else 0f
                val lookY = if (mood == XiaozhiMood.THINKING) -2f else 0f
                listOf(-13f, 13f).forEach { x ->
                    if (eyeHeight < 3f) {
                        drawRoundRect(
                            color = eyeColor.copy(alpha = 0.85f),
                            topLeft = Offset(x - 5f, -6f),
                            size = Size(10f, 2.2f),
                            cornerRadius = androidx.compose.ui.geometry.CornerRadius(1.1f),
                        )
                    } else {
                        drawRoundRect(
                            color = eyeColor,
                            topLeft = Offset(x - 5f + lookX, -14f + lookY),
                            size = Size(10f, eyeHeight),
                            cornerRadius = androidx.compose.ui.geometry.CornerRadius(5f),
                        )
                        drawCircle(
                            color = Color.White.copy(alpha = 0.9f),
                            radius = 1.5f,
                            center = Offset(x - 2f + lookX, -10f + lookY),
                        )
                    }
                }
                // 一点点腮红，让表情更亲近
                listOf(-23f, 23f).forEach { x ->
                    drawCircle(
                        color = glow.copy(alpha = 0.22f),
                        radius = 4f,
                        center = Offset(x, 7f),
                    )
                }

                // 嘴
                when (mood) {
                    XiaozhiMood.SPEAKING -> {
                        val mouthWidth = 13f + 9f * mouth
                        val mouthHeight = 2.5f + 9f * mouth
                        drawRoundRect(
                            color = eyeColor,
                            topLeft = Offset(-mouthWidth / 2f, 3f),
                            size = Size(mouthWidth, mouthHeight),
                            cornerRadius = androidx.compose.ui.geometry.CornerRadius(mouthHeight / 2f),
                        )
                    }
                    XiaozhiMood.THINKING -> {
                        drawCircle(
                            color = eyeColor.copy(alpha = 0.9f),
                            radius = 2.6f,
                            center = Offset(0f, 7f),
                        )
                    }
                    else -> {
                        drawArc(
                            color = eyeColor,
                            startAngle = 25f,
                            sweepAngle = 130f,
                            useCenter = false,
                            topLeft = Offset(-9f, 0f),
                            size = Size(18f, 12f),
                            style = Stroke(width = 2.4f, cap = StrokeCap.Round),
                        )
                    }
                }

                // 思考光点
                if (mood == XiaozhiMood.THINKING) {
                    repeat(3) { index ->
                        val phase = (thinkingPhase + index * 0.22f) % 1f
                        val alpha = 0.30f + 0.70f * (1f - abs(phase * 2f - 1f))
                        drawCircle(
                            color = glow.copy(alpha = alpha),
                            radius = 2.6f,
                            center = Offset(
                                44f + index * 9f,
                                -64f - 4f * sin((thinkingPhase + index * 0.2f) * PI.toFloat() * 2f),
                            ),
                        )
                    }
                }

                // 环绕光点
                repeat(4) { index ->
                    val angle = pulse * PI.toFloat() * 2f + index * 1.57f
                    val radius = 82f + 4f * sin(wave + index)
                    drawCircle(
                        color = glow.copy(alpha = 0.24f + 0.25f * abs(sin(angle))),
                        radius = if (index % 2 == 0) 2f else 1.4f,
                        center = Offset(
                            radius * kotlin.math.cos(angle),
                            radius * sin(angle) * 0.84f,
                        ),
                    )
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiScreen.kt`

> 智能体对话界面，与宠物外壳统一。

````kotlin
package com.shineleong.toughmind.ui.screen.xiaozhi

import android.widget.Toast
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.clickable
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DeleteSweep
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material.icons.automirrored.filled.VolumeOff
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.AssistChip
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.component.tr
import com.shineleong.toughmind.ui.component.translateText
import com.shineleong.toughmind.ui.component.LocalTtsPreset
import com.shineleong.toughmind.ui.component.LocalTtsMode
import com.shineleong.toughmind.ui.component.LocalTtsRate
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.local.db.entity.XiaozhiMessageEntity
import com.shineleong.toughmind.data.model.PetReaction
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.PetLive2D
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LocalCareColors
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import kotlin.math.exp
import kotlin.math.sin

private val QUICK_PROMPTS = listOf(
    "我有点累",
    "TA 在哪？",
    "今天天气",
    "陪我聊聊",
)

private val TAP_LINES = listOf(
    "嗯？我在呢。",
    "你叫我啦？",
    "我一直都在，你说。",
    "刚刚在发呆，现在专心听你。",
)

private val TAP_LINES_EN = listOf(
    "Hm? I'm here.",
    "You called?",
    "I'm always here. Tell me.",
    "I was spacing out; now I'm all ears.",
)

/**
 * AI 小智：会说话的小机器人 + 对话。
 *
 * - 表情由 [XiaozhiMood] 驱动：待机 / 倾听 / 思考 / 说话；
 * - 说话时 TTS 的 onRangeStart 会推动嘴型和两侧音律条；
 * - 回复优先走云端大模型，服务端没配模型或断网时使用本地上下文兜底。
 */
@Composable
fun XiaozhiScreen(
    viewModel: XiaozhiViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    val thinking by viewModel.thinking.collectAsStateWithLifecycle()
    val voiceEnabled by viewModel.voiceEnabled.collectAsStateWithLifecycle()
    val partner by viewModel.partner.collectAsStateWithLifecycle()
    val nickname by viewModel.nickname.collectAsStateWithLifecycle()
    val name by viewModel.name.collectAsStateWithLifecycle()
    val pet by viewModel.pet.collectAsStateWithLifecycle()

    val speaker = remember { XiaozhiSpeaker(context) }
    val ready by speaker.ready.collectAsStateWithLifecycle()
    val speaking by speaker.speaking.collectAsStateWithLifecycle()
    val failed by speaker.failed.collectAsStateWithLifecycle()
    val voiceEnabledNow = rememberUpdatedState(voiceEnabled)
    val ttsPreset = LocalTtsPreset.current
    val appLanguage = LocalAppLanguage.current
    val ttsMode = LocalTtsMode.current
    val ttsRate = LocalTtsRate.current

    LaunchedEffect(ttsPreset, appLanguage, ttsMode) {
        speaker.setMode(ttsMode)
        speaker.setLocale(ttsPreset.uiLocale(appLanguage == "en"))
    }
    LaunchedEffect(ttsRate) {
        speaker.setRate(ttsRate)
    }
    val noVoiceMessage = tr(
        "这台设备没有可用的语音引擎，仍可以文字聊天。",
        "No voice engine is available on this device; you can still chat by text.",
    )
    val noVoiceShort = tr("没有可用的语音引擎", "No voice engine available")
    val preparingVoice = tr("语音引擎还在准备，稍等一下", "The voice engine is still preparing, one moment")

    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()
    var input by rememberSaveable { mutableStateOf("") }
    var greeting by remember { mutableStateOf<String?>(null) }
    var showClearDialog by remember { mutableStateOf(false) }
    var showNameDialog by remember { mutableStateOf(false) }
    var draftName by remember { mutableStateOf(name) }
    var mouth by remember { mutableFloatStateOf(0f) }

    DisposableEffect(Unit) {
        onDispose { speaker.release() }
    }

    LaunchedEffect(failed) {
        if (failed) {
            Toast.makeText(
                context,
                noVoiceMessage,
                Toast.LENGTH_SHORT,
            ).show()
        }
    }

    // 新回复到达时，若语音开着就朗读。
    LaunchedEffect(Unit) {
        viewModel.replies.collect { reply ->
            if (voiceEnabledNow.value) speaker.speak(reply.text)
        }
    }

    // 用 TTS 的字级回调驱动口型：每个字给一次脉冲，再自然衰减。
    LaunchedEffect(speaking) {
        if (!speaking) {
            mouth = 0f
            return@LaunchedEffect
        }
        val start = withFrameNanos { it }
        var lastTick = speaker.rangeTick.value
        var lastTickAt = 0f
        while (isActive) {
            withFrameNanos { now ->
                val t = (now - start) / 1_000_000_000f
                val tick = speaker.rangeTick.value
                if (tick != lastTick) {
                    lastTick = tick
                    lastTickAt = t
                }
                val decay = exp(-(t - lastTickAt) * 5.5f)
                val flutter = 0.30f + 0.24f * sin(t * 13.7f) + 0.14f * sin(t * 31f)
                mouth = (flutter + 0.62f * decay).coerceIn(0f, 1f)
            }
        }
    }

    val lastAssistant = messages.lastOrNull { it.role == ROLE_ASSISTANT }
    val newestAssistantId = lastAssistant?.id
    val freshCutoff = System.currentTimeMillis() - 8_000L

    val mood = when {
        thinking -> XiaozhiMood.THINKING
        speaking -> XiaozhiMood.SPEAKING
        input.isNotBlank() -> XiaozhiMood.LISTENING
        else -> XiaozhiMood.IDLE
    }

    LaunchedEffect(messages.size, thinking) {
        val count = messages.size + if (thinking) 1 else 0
        if (count > 0) {
            listState.animateScrollToItem(count - 1)
        }
    }

    fun toggleVoice() {
        if (!ready) {
            Toast.makeText(
                context,
                if (failed) noVoiceShort else preparingVoice,
                Toast.LENGTH_SHORT,
            ).show()
            return
        }
        val next = !voiceEnabled
        viewModel.setVoiceEnabled(next)
        if (!next) {
            speaker.stop()
        } else {
            lastAssistant?.text?.let { speaker.speak(it) }
        }
    }

    fun send(text: String) {
        val trimmed = text.trim()
        if (trimmed.isEmpty() || thinking) return
        speaker.stop()
        viewModel.send(trimmed)
        input = ""
    }

    val care = LocalCareColors.current
    val surface = MaterialTheme.colorScheme.surface
    val statusText = greeting ?: when (mood) {
        XiaozhiMood.THINKING -> "让我想想…"
        XiaozhiMood.SPEAKING -> "正在说话"
        XiaozhiMood.LISTENING -> "我在听"
        XiaozhiMood.IDLE -> partner?.name?.let { "我帮你看着 $it" } ?: "随时都在"
    }
    val statusDetail = when {
        greeting != null -> "点一下小智，它会回你一句"
        thinking -> "正在组织一句不敷衍的话"
        speaking -> "正在朗读回复"
        else -> tr(
            "语音${if (voiceEnabled) "已开" else "已关"} · 对话只保存在本机",
            "Voice ${if (voiceEnabled) "on" else "off"} · chats stay on this device",
        )
    }

    val imeVisible = WindowInsets.ime.getBottom(LocalDensity.current) > 0
    val heroHeight = if (imeVisible) 104.dp else 254.dp

    val onTapAvatar: () -> Unit = {
        val line = if (appLanguage == "en") TAP_LINES_EN.random() else TAP_LINES.random()
        greeting = line
        if (voiceEnabled && ready) speaker.speak(line)
        scope.launch {
            delay(2_600)
            if (greeting == line) greeting = null
        }
    }

    // 键盘弹出后压缩了对话区，把最新消息重新带到可见位置。
    LaunchedEffect(imeVisible) {
        if (imeVisible) {
            delay(300)
            val count = messages.size + if (thinking) 1 else 0
            if (count > 0) listState.animateScrollToItem(count - 1)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding(),
    ) {

        @Composable
        fun AssistantFace(size: Dp) {
            PetLive2D(
                state = pet,
                reaction = PetReaction.NONE,
                reactionToken = 0,
                modifier = Modifier.size(size),
                contentDescription = "$name 的宠物形象",
                onTap = onTapAvatar,
                backdrop = false,
            )
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            AssistantFace(64.dp)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.clickable {
                        draftName = name
                        showNameDialog = true
                    },
                )
                Text(
                    text = statusText,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                )
                Text(
                    text = statusDetail,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                    maxLines = 2,
                )
            }
            IconButton(onClick = ::toggleVoice) {
                Icon(
                    if (voiceEnabled) Icons.AutoMirrored.Filled.VolumeUp else Icons.AutoMirrored.Filled.VolumeOff,
                    contentDescription = if (voiceEnabled) "关闭语音播报" else "开启语音播报",
                    tint = MaterialTheme.colorScheme.primary,
                )
            }
            IconButton(onClick = { showClearDialog = true }) {
                Icon(
                    Icons.Filled.DeleteSweep,
                    contentDescription = "清空对话",
                    tint = TextSecondary,
                )
            }
        }

        Box(Modifier.weight(1f)) {
            if (messages.isEmpty() && !thinking) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    AssistantFace(96.dp)
                    Spacer(Modifier.height(12.dp))
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = "点一下小智，它会回你一句",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
            } else {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    items(messages, key = { it.id }) { message ->
                        val animate = message.role == ROLE_ASSISTANT &&
                            message.id == newestAssistantId &&
                            message.createdAt >= freshCutoff
                        XiaozhiMessageRow(
                            message = message,
                            animate = animate,
                            pet = pet,
                        )
                    }
                    if (thinking) {
                        item { ThinkingBubble() }
                    }
                }
            }
        }

        if (messages.size <= 2) {
            LazyRow(
                modifier = Modifier.fillMaxWidth(),
                contentPadding = PaddingValues(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(QUICK_PROMPTS) { prompt ->
                    AssistChip(
                        onClick = {
                            send(if (appLanguage == "en") translateText(prompt, "en") else prompt)
                        },
                        label = { Text(prompt) },
                    )
                }
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedTextField(
                value = input,
                onValueChange = { input = it.take(200) },
                modifier = Modifier.weight(1f),
                placeholder = { Text("跟${name}说点什么…") },
                shape = RoundedCornerShape(22.dp),
                maxLines = 3,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = MaterialTheme.colorScheme.primary,
                    unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.4f),
                ),
            )
            FilledIconButton(
                onClick = {
                    send(input)
                },
                enabled = input.isNotBlank() && !thinking,
                modifier = Modifier.size(48.dp),
            ) {
                Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "发送")
            }
        }
    }

    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = { Text("清空和${name}的对话？") },
            text = { Text("对话只保存在本机，清空后无法恢复。") },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.clear()
                        showClearDialog = false
                    },
                ) { Text("清空") }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) { Text("取消") }
            },
        )
    }

    if (showNameDialog) {
        AlertDialog(
            onDismissRequest = { showNameDialog = false },
            title = { Text("给智能宠物改名") },
            text = {
                OutlinedTextField(
                    value = draftName,
                    onValueChange = { draftName = it.take(12) },
                    singleLine = true,
                    placeholder = { Text("默认叫小智") },
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.setName(draftName.ifBlank { "小智" })
                    showNameDialog = false
                }) { Text("保存") }
            },
            dismissButton = {
                TextButton(onClick = { showNameDialog = false }) { Text("取消") }
            },
        )
    }
}

@Composable
private fun XiaozhiMessageRow(
    message: XiaozhiMessageEntity,
    animate: Boolean,
    pet: PetState,
) {
    val mine = message.role == ROLE_USER
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (mine) Arrangement.End else Arrangement.Start,
        verticalAlignment = Alignment.Top,
    ) {
        if (!mine) {
            PetLive2D(
                state = pet,
                reaction = PetReaction.NONE,
                reactionToken = 0,
                modifier = Modifier.size(30.dp),
                contentDescription = "智能宠物形象",
                backdrop = false,
            )
            Spacer(Modifier.width(6.dp))
        }
        Surface(
            shape = RoundedCornerShape(
                topStart = if (mine) 18.dp else 6.dp,
                topEnd = if (mine) 6.dp else 18.dp,
                bottomStart = 18.dp,
                bottomEnd = 18.dp,
            ),
            color = if (mine) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.55f)
            },
            modifier = Modifier.weight(1f, fill = false),
        ) {
            Column(Modifier.padding(horizontal = 12.dp, vertical = 8.dp)) {
                if (mine) {
                    Text(
                        text = message.text,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                    )
                } else {
                    TypewriterText(
                        text = message.text,
                        animate = animate,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Text(
                    text = timeLabel(message.createdAt),
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary.copy(alpha = 0.7f),
                    modifier = Modifier.padding(top = 2.dp),
                )
            }
        }
        if (mine) {
            Spacer(Modifier.width(6.dp))
            MiniMeAvatar()
        }
    }
}


@Composable
fun AssistantAvatar() {
    Box(
        modifier = Modifier
            .size(30.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            Icons.Filled.SmartToy,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(AppDimens.IconSize),
        )
    }
}

@Composable
private fun MiniMeAvatar() {
    Box(
        modifier = Modifier
            .size(30.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.secondaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "我",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSecondaryContainer,
        )
    }
}

@Composable
private fun TypewriterText(
    text: String,
    animate: Boolean,
    color: Color,
) {
    var shown by remember(text, animate) {
        mutableIntStateOf(if (animate) 0 else text.length)
    }
    LaunchedEffect(text, animate) {
        if (!animate) {
            shown = text.length
            return@LaunchedEffect
        }
        while (shown < text.length) {
            delay(16)
            shown = (shown + 2).coerceAtMost(text.length)
        }
    }
    Text(
        text = text.take(shown) + if (shown < text.length) "▍" else "",
        style = MaterialTheme.typography.bodyLarge,
        color = color,
    )
}

@Composable
private fun ThinkingBubble() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Start,
        verticalAlignment = Alignment.Bottom,
    ) {
        AssistantAvatar()
        Spacer(Modifier.width(7.dp))
        Surface(
            shape = RoundedCornerShape(topStart = 18.dp, topEnd = 18.dp, bottomStart = 5.dp, bottomEnd = 18.dp),
            color = MaterialTheme.colorScheme.surfaceVariant,
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(5.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                val transition = rememberInfiniteTransition(label = "thinking")
                val phase by transition.animateFloat(
                    initialValue = 0f,
                    targetValue = 1f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(900, easing = LinearEasing),
                        repeatMode = RepeatMode.Restart,
                    ),
                    label = "thinking-phase",
                )
                repeat(3) { index ->
                    val alpha = 0.25f + 0.75f * (1f - kotlin.math.abs(((phase + index * 0.22f) % 1f) * 2f - 1f))
                    Box(
                        modifier = Modifier
                            .size(7.dp)
                            .clip(CircleShape)
                            .background(MaterialTheme.colorScheme.primary.copy(alpha = alpha)),
                    )
                }
                Spacer(Modifier.width(4.dp))
                Text(
                    text = "小智正在想",
                    style = MaterialTheme.typography.labelMedium,
                    color = TextSecondary,
                )
            }
        }
    }
}

private fun timeLabel(createdAt: Long): String {
    val zone = ZoneId.systemDefault()
    val time = Instant.ofEpochMilli(createdAt).atZone(zone)
    val date = time.toLocalDate()
    val today = LocalDate.now(zone)
    val clock = time.format(DateTimeFormatter.ofPattern("HH:mm", Locale.getDefault()))
    return when (date) {
        today -> clock
        today.minusDays(1) -> "昨天 $clock"
        else -> "${date.monthValue}/${date.dayOfMonth} $clock"
    }
}

private const val ROLE_USER = "user"
private const val ROLE_ASSISTANT = "assistant"
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiSpeaker.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.xiaozhi

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import com.shineleong.toughmind.util.TtsMode
import java.util.Locale

/**
 * 小智的语音播报。
 *
 * 状态全部用 StateFlow 暴露，方便 Compose 在任意线程安全地更新口型：
 * - ready：引擎可用且支持中文；
 * - speaking：正在朗读；
 * - rangeTick：每读到一个字/词就 +1，供口型动画做「字同步」脉冲；
 * - failed：设备没有可用中文引擎，UI 给出一次提示。
 */
class XiaozhiSpeaker(context: Context) {

    private var engine: TextToSpeech? = null
    private var released = false
    private var utteranceCounter = 0
    private var pendingText: String? = null
    private var initRetries = 0

    private val _ready = MutableStateFlow(false)
    val ready: StateFlow<Boolean> = _ready.asStateFlow()

    private val _speaking = MutableStateFlow(false)
    val speaking: StateFlow<Boolean> = _speaking.asStateFlow()

    private val _rangeTick = MutableStateFlow(0)
    val rangeTick: StateFlow<Int> = _rangeTick.asStateFlow()

    private val _failed = MutableStateFlow(false)
    val failed: StateFlow<Boolean> = _failed.asStateFlow()

    private var desiredLocale: Locale = Locale.SIMPLIFIED_CHINESE
    private var speechRate = 1.02f
    private var mode = TtsMode.OFFLINE

    init {
        engine = TextToSpeech(context.applicationContext) { status -> handleInit(status) }
    }

    private fun handleInit(status: Int) {
        if (released) return
        val tts = engine
        if (tts == null) {
            // 极少数设备会在构造返回前回调 onInit，稍后重试一次。
            if (initRetries++ < 5) {
                Handler(Looper.getMainLooper()).postDelayed({ handleInit(status) }, 80)
            }
            return
        }
        if (status != TextToSpeech.SUCCESS) {
            _failed.value = true
            return
        }
        if (!applyLocale(tts, desiredLocale)) {
            _failed.value = true
            return
        }
        pendingText?.let { text ->
            pendingText = null
            speak(text)
        }
    }

    /** 英文 / 粤语等音色由页面按设置切换；系统没有该音色时返回 false。 */
    fun setLocale(locale: Locale): Boolean {
        desiredLocale = locale
        val tts = engine ?: return false
        val applied = applyLocale(tts, locale)
        if (applied) {
            pendingText?.let { text ->
                pendingText = null
                speak(text)
            }
        } else {
            _failed.value = true
        }
        return applied
    }

    fun setRate(rate: Float) {
        speechRate = rate.coerceIn(0.7f, 1.3f)
        engine?.setSpeechRate(speechRate)
    }

    fun setMode(mode: TtsMode) {
        this.mode = mode
        val tts = engine ?: return
        applyLocale(tts, desiredLocale)
    }

    private fun applyLocale(tts: TextToSpeech, locale: Locale): Boolean {
        val result = tts.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA ||
            result == TextToSpeech.LANG_NOT_SUPPORTED
        ) {
            _ready.value = false
            return false
        }
        val candidates = tts.voices.orEmpty().filter { voice ->
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
            tts.voice = chosen
        }
        tts.setSpeechRate(speechRate)
        tts.setPitch(1.06f)
        tts.setOnUtteranceProgressListener(listener)
        _failed.value = false
        _ready.value = true
        return true
    }

    private val listener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) {
            _speaking.value = true
        }

        override fun onDone(utteranceId: String?) {
            _speaking.value = false
        }

        @Deprecated("Deprecated in Java")
        override fun onError(utteranceId: String?) {
            _speaking.value = false
        }

        override fun onError(utteranceId: String?, errorCode: Int) {
            _speaking.value = false
        }

        override fun onStop(utteranceId: String?, interrupted: Boolean) {
            _speaking.value = false
        }

        /** API 26+：TTS 每读到一个区间就回调，用来驱动嘴型。 */
        override fun onRangeStart(utteranceId: String?, start: Int, end: Int, frame: Int) {
            _rangeTick.value += 1
        }
    }

    fun speak(text: String) {
        val clean = text.trim()
        if (clean.isEmpty()) return
        if (!_ready.value) {
            if (_failed.value) return
            pendingText = clean
            return
        }
        val tts = engine ?: return
        val id = "xiaozhi-${++utteranceCounter}"
        _speaking.value = true
        val result = tts.speak(clean, TextToSpeech.QUEUE_FLUSH, null, id)
        if (result != TextToSpeech.SUCCESS) {
            _speaking.value = false
        }
    }

    fun stop() {
        pendingText = null
        runCatching { engine?.stop() }
        _speaking.value = false
    }

    fun release() {
        released = true
        pendingText = null
        runCatching { engine?.stop() }
        runCatching { engine?.shutdown() }
        engine = null
        _speaking.value = false
        _ready.value = false
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/xiaozhi/XiaozhiViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.xiaozhi

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.XiaozhiContext
import com.shineleong.toughmind.data.model.XiaozhiReply
import com.shineleong.toughmind.data.model.PetState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.XiaozhiRepository
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.time.LocalDateTime

/**
 * 小智对话页状态：
 * - messages：Room 持久化的消息；
 * - thinking：等待模型回复；
 * - replies：新回复事件，UI 用它触发 TTS 口型；
 * - voiceEnabled：语音播报开关（DataStore 持久化）。
 */
class XiaozhiViewModel(
    private val repository: XiaozhiRepository,
    private val careRepository: CareRepository,
    private val preferences: Preferences,
) : ViewModel() {

    val messages = repository.messages.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        emptyList(),
    )

    val partner = careRepository.partnerPresence.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        null,
    )

    val nickname = preferences.nickname.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        "",
    )

    val voiceEnabled = preferences.xiaozhiVoice.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        true,
    )

    val language = preferences.language.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        "zh",
    )

    val name = preferences.xiaozhiName.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        "小智",
    )

    val pet = preferences.owlPet.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        PetState(),
    )

    fun setName(name: String) {
        viewModelScope.launch { preferences.setXiaozhiName(name) }
    }

    private val _thinking = MutableStateFlow(false)
    val thinking: StateFlow<Boolean> = _thinking.asStateFlow()

    private val _replies = MutableSharedFlow<XiaozhiReply>(extraBufferCapacity = 4)
    val replies = _replies.asSharedFlow()

    fun send(input: String) {
        val text = input.trim()
        if (text.isEmpty() || _thinking.value) return
        if (text.length > MAX_INPUT_LENGTH) return

        viewModelScope.launch {
            _thinking.value = true
            try {
                val startedAt = System.currentTimeMillis()
                val reply = repository.send(text, buildContext(), english = language.value == "en")
                // 本地兜底几乎瞬时返回；留一点「思考」时间，避免气泡一闪而过。
                val remaining = MIN_THINKING_MS - (System.currentTimeMillis() - startedAt)
                if (remaining > 0) delay(remaining)
                _replies.emit(reply)
            } catch (t: Throwable) {
                if (t is kotlinx.coroutines.CancellationException) throw t
                repository.appendAssistant(
                    if (language.value == "en") {
                        "I spaced out and missed that. Could you say it again?"
                    } else {
                        "我这边刚刚走神了，没接上。你再说一遍好吗？"
                    },
                )
            } finally {
                _thinking.value = false
            }
        }
    }

    fun setVoiceEnabled(enabled: Boolean) {
        viewModelScope.launch { preferences.setXiaozhiVoice(enabled) }
    }

    fun clear() {
        viewModelScope.launch { repository.clear() }
    }

    private suspend fun buildContext(): XiaozhiContext {
        val partner = runCatching { careRepository.partnerPresence.first() }.getOrNull()
        val weather = runCatching { careRepository.selfWeather.first() }.getOrNull()
        val companion = runCatching { careRepository.companion.first() }.getOrNull()
        val name = runCatching { preferences.nickname.first() }.getOrNull().orEmpty()
        val now = LocalDateTime.now()
        // 没有云端伙伴时，partnerPresence 可能只是占位名「TA」；优先用本地绑定称呼「安」。
        val partnerName = partner?.name
            ?.takeIf { it.isNotBlank() && it != "TA" && it != "对方" }
            ?: companion?.nickname?.takeIf { it.isNotBlank() }
            ?: ""

        return XiaozhiContext(
            userName = name,
            partnerName = partnerName,
            partnerStatus = partner?.status?.label.orEmpty(),
            partnerNote = partner?.activityNote.orEmpty(),
            partnerOnline = partner?.online == true,
            partnerHasLocation = partner?.hasLocation == true,
            partnerDistanceMeters = partner?.distanceMeters,
            partnerDirection = partner?.directionLabel.orEmpty(),
            partnerMoodEmoji = partner?.moodEmoji.orEmpty(),
            partnerMoodMessage = partner?.moodMessage.orEmpty(),
            weatherLabel = weather?.label.orEmpty(),
            weatherTemperature = weather?.temperatureC,
            weatherEmoji = weather?.emoji.orEmpty(),
            hour = now.hour,
            minute = now.minute,
            dateText = "${now.monthValue}月${now.dayOfMonth}日 ${weekdayName(now)}",
        )
    }

    private fun weekdayName(now: LocalDateTime): String = when (now.dayOfWeek.value) {
        1 -> "周一"
        2 -> "周二"
        3 -> "周三"
        4 -> "周四"
        5 -> "周五"
        6 -> "周六"
        else -> "周日"
    }

    private companion object {
        const val MAX_INPUT_LENGTH = 500
        const val MIN_THINKING_MS = 700L
    }
}
````

---

返回索引：[README.md](02-实战库/项目/安卓应用开发/README.md)
