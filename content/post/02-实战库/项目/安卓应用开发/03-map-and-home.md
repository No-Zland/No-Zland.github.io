# 03 · 地图与首页

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

首页是全屏地图：自己与亲友头像标记、状态气泡、距离与天气浮层、地点搜索、路线规划与导航面板。百度地图为主引擎，osmdroid + OpenStreetMap 作为无 Key 回退。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 地图引擎与标记](#s03-1) | `CareMap` 按 `MapConfig.USE_BAIDU` 选择百度或 OSM 实现；`AvatarMarkerFactory` 生成 3×3 栅格状态圈头像。 | 8 |
| [2. 首页与导航面板](#s03-2) | `HomeScreen` 组装地图、顶部浮层、导航浮层、约见搜索、人物详情与心情弹窗；拆分后每个文件只负责一类浮层。 | 7 |

本篇共 **2 个步骤 / 15 个文件**，按表格顺序写入即可还原对应代码。

<a id="s03-1"></a>

## 步骤 03.1 · 地图引擎与标记

`CareMap` 按 `MapConfig.USE_BAIDU` 选择百度或 OSM 实现；`AvatarMarkerFactory` 生成 3×3 栅格状态圈头像。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/map/AvatarMarkerFactory.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/BaiduMapView.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/LocationMap.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/MapConfig.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/MapPerson.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/MapStyle.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/OsmMapView.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/map/PlaceMarkerFactory.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/map/AvatarMarkerFactory.kt`

> 头像标记绘制：3×3 栅格状态圈、主题外框与在线/离线着色。

````kotlin
package com.shineleong.toughmind.ui.map

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RadialGradient
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.Shader
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asAndroidBitmap
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.sin

/**
 * 地图人物 Marker：头像圆环 + 右上角状态点 + 可选的右下角状态徽标 + 头像上方的对话气泡。
 *
 * 人物表示“人在哪、面朝哪”：头像圆心就是真实坐标；有朝向时在头像后方画一束扇形方向光，
 * 并在圆环上画一个箭头。GPS 针形（水滴形）只留给地图上的地点（会合点 / 目的地），
 * 不再用于人物，避免把“人”误读成“地点”。
 */
data class MarkerIcon(
    val bitmap: Bitmap,
    val anchorX: Float = 0.5f,
    val anchorY: Float = 1f,
)

object AvatarMarkerFactory {

    /** 扇形方向光的半角（度）。 */
    private const val HEADING_HALF_ANGLE = 30f

    fun create(
        avatar: ImageBitmap?,
        initials: String,
        ringColor: Int,
        statusColor: Int,
        moodEmoji: String = "🙂",
        badgeText: String? = null,
        heading: Float? = null,
        online: Boolean = false,
        showStatusBadge: Boolean = true,
        bubbleText: String? = null,
        bubbleColor: Int = 0xF2FFFFFF.toInt(),
        bubbleTextColor: Int = 0xFF0A1B33.toInt(),
        sizePx: Int = 192,
    ): MarkerIcon {
        val size = sizePx.coerceAtLeast(72).toFloat()
        val ringRadius = size * 0.415f
        val avatarRadius = size * 0.355f
        val emojiRadius = size * 0.16f
        val headingDegrees = heading
            ?.takeIf { it.isFinite() }
            ?.let { ((it % 360f) + 360f) % 360f }
        val coneRadius = ringRadius * 2.2f

        val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = bubbleTextColor
            textSize = size * 0.17f
            textAlign = Paint.Align.LEFT
        }
        val bubbleLines = bubbleText
            ?.trim()
            ?.takeIf { it.isNotBlank() }
            ?.let { wrapText(it, size * 3.25f, textPaint, maxLines = 2) }
            .orEmpty()
        val lineHeight = textPaint.textSize * 1.3f
        val bubblePaddingX = size * 0.18f
        val bubblePaddingY = size * 0.14f
        val textWidth = bubbleLines.maxOfOrNull { textPaint.measureText(it) } ?: 0f
        val bubbleWidth = if (bubbleLines.isEmpty()) {
            0f
        } else {
            (textWidth + bubblePaddingX * 2).coerceIn(size * 1.45f, size * 3.6f)
        }
        val bubbleHeight = if (bubbleLines.isEmpty()) {
            0f
        } else {
            bubbleLines.size * lineHeight + bubblePaddingY * 2
        }
        val tailHeight = if (bubbleLines.isEmpty()) 0f else size * 0.10f
        val bubbleGap = if (bubbleLines.isEmpty()) 0f else size * 0.07f
        val topExtra = bubbleHeight + tailHeight + bubbleGap

        // 朝向扇形可能伸到画布上方或左右两侧，需要额外留白；气泡仍画在最上方。
        val coneTopNeed = if (headingDegrees != null) {
            (coneRadius + size * 0.04f - size * 0.5f).coerceAtLeast(0f)
        } else {
            0f
        }
        val extraTop = (coneTopNeed - topExtra).coerceAtLeast(0f)
        val contentWidth = if (headingDegrees != null) size * 2.02f else size * 1.32f
        val canvasWidth = max(contentWidth, bubbleWidth).toInt()
        val canvasHeight = (extraTop + topExtra + size * 1.55f).toInt()

        val bitmap = Bitmap.createBitmap(canvasWidth, canvasHeight, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        val avatarCx = canvasWidth / 2f
        val avatarCy = extraTop + topExtra + size / 2f

        if (headingDegrees != null) {
            drawHeadingCone(
                canvas = canvas,
                cx = avatarCx,
                cy = avatarCy,
                coneRadius = coneRadius,
                heading = headingDegrees,
                color = ringColor,
            )
        }

        if (bubbleLines.isNotEmpty()) {
            val bubbleLeft = avatarCx - bubbleWidth / 2f
            val bubbleBottom = bubbleHeight
            val bubbleRect = RectF(bubbleLeft, 0f, bubbleLeft + bubbleWidth, bubbleBottom)
            val bubblePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = bubbleColor }
            canvas.drawRoundRect(bubbleRect, size * 0.12f, size * 0.12f, bubblePaint)
            val tail = Path().apply {
                moveTo(avatarCx - size * 0.08f, bubbleBottom)
                lineTo(avatarCx + size * 0.08f, bubbleBottom)
                lineTo(avatarCx, bubbleBottom + tailHeight)
                close()
            }
            canvas.drawPath(tail, bubblePaint)
            bubbleLines.forEachIndexed { index, line ->
                val baseline = bubblePaddingY - textPaint.fontMetrics.ascent + index * lineHeight
                canvas.drawText(line, bubbleLeft + bubblePaddingX, baseline, textPaint)
            }
        }

        // 投影 + 白色头像底，圆心即真实坐标（不再使用针尖）
        canvas.drawCircle(
            avatarCx,
            avatarCy,
            ringRadius,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = 0x33000000
                setShadowLayer(size * 0.05f, 0f, size * 0.03f, 0x55000000)
            },
        )
        canvas.drawCircle(
            avatarCx,
            avatarCy,
            ringRadius,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = 0xFFFFFFFF.toInt() },
        )

        // 头像裁剪为圆形
        val avatarCircle = Path().apply { addCircle(avatarCx, avatarCy, avatarRadius, Path.Direction.CW) }
        val save = canvas.save()
        canvas.clipPath(avatarCircle)
        val androidAvatar = avatar?.asAndroidBitmap()
        if (androidAvatar != null) {
            val side = androidAvatar.width.coerceAtMost(androidAvatar.height)
            val left = (androidAvatar.width - side) / 2
            val top = (androidAvatar.height - side) / 2
            canvas.drawBitmap(
                androidAvatar,
                Rect(left, top, left + side, top + side),
                RectF(
                    avatarCx - avatarRadius,
                    avatarCy - avatarRadius,
                    avatarCx + avatarRadius,
                    avatarCy + avatarRadius,
                ),
                Paint(Paint.ANTI_ALIAS_FLAG).apply { isFilterBitmap = true },
            )
        } else {
            canvas.drawCircle(
                avatarCx,
                avatarCy,
                avatarRadius,
                Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    shader = LinearGradient(
                        avatarCx - avatarRadius,
                        avatarCy - avatarRadius,
                        avatarCx + avatarRadius,
                        avatarCy + avatarRadius,
                        0xFF7C5CFF.toInt(),
                        0xFF0891B2.toInt(),
                        Shader.TileMode.CLAMP,
                    )
                },
            )
            val labelPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = 0xFFFFFFFF.toInt()
                textSize = avatarRadius * 0.95f
                textAlign = Paint.Align.CENTER
                isFakeBoldText = true
            }
            val label = initials.trim().take(1).ifBlank { "?" }
            val metrics = labelPaint.fontMetrics
            val baseline = avatarCy - (metrics.ascent + metrics.descent) / 2f
            canvas.drawText(label, avatarCx, baseline, labelPaint)
        }
        canvas.restoreToCount(save)

        // 彩色描边
        canvas.drawCircle(
            avatarCx,
            avatarCy,
            ringRadius,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                style = Paint.Style.STROKE
                strokeWidth = max(2f, size * 0.032f)
                color = ringColor
            },
        )
        if (online) {
            canvas.drawCircle(
                avatarCx,
                avatarCy,
                ringRadius + size * 0.022f,
                Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    style = Paint.Style.STROKE
                    strokeWidth = max(2f, size * 0.035f)
                    color = 0xFF16A36A.toInt()
                },
            )
        }

        // 右上角在线状态点
        val dotCx = avatarCx + ringRadius * 0.72f
        val dotCy = avatarCy - ringRadius * 0.72f
        val dotRadius = size * 0.052f
        canvas.drawCircle(
            dotCx,
            dotCy,
            dotRadius + size * 0.015f,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = 0xFFFFFFFF.toInt() },
        )
        canvas.drawCircle(
            dotCx,
            dotCy,
            dotRadius,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = statusColor },
        )

        // 右下角状态徽标：可按场景关闭，只保留干净的头像。
        if (showStatusBadge) {
            val emojiOffset = ringRadius * 0.62f
            val emojiCx = avatarCx + emojiOffset
            val emojiCy = avatarCy + emojiOffset
            canvas.drawCircle(
                emojiCx,
                emojiCy,
                emojiRadius + size * 0.022f,
                Paint(Paint.ANTI_ALIAS_FLAG).apply { color = 0xFFFFFFFF.toInt() },
            )
            val gridPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = if (online) statusColor else 0xFF9AA4B2.toInt()
            }
            val gridHalf = emojiRadius * 0.62f
            val gap = gridHalf * 0.24f
            val cell = (gridHalf * 2f - gap * 4f) / 3f
            for (row in 0..2) {
                for (col in 0..2) {
                    val left = emojiCx - gridHalf + gap + col * (cell + gap)
                    val top = emojiCy - gridHalf + gap + row * (cell + gap)
                    canvas.drawRoundRect(
                        android.graphics.RectF(left, top, left + cell, top + cell),
                        cell * 0.24f,
                        cell * 0.24f,
                        gridPaint,
                    )
                }
            }
        }

        if (headingDegrees != null) {
            drawHeadingArrow(
                canvas = canvas,
                cx = avatarCx,
                cy = avatarCy,
                ringRadius = ringRadius,
                heading = headingDegrees,
                color = ringColor,
                strokeWidth = max(2f, size * 0.024f),
            )
        }

        return MarkerIcon(bitmap = bitmap, anchorX = 0.5f, anchorY = avatarCy / canvasHeight)
    }

    /** 头像后方的扇形方向光：向朝向方向渐隐，像百度地图的蓝色方向扇。 */
    private fun drawHeadingCone(
        canvas: Canvas,
        cx: Float,
        cy: Float,
        coneRadius: Float,
        heading: Float,
        color: Int,
    ) {
        val start = heading - 90f - HEADING_HALF_ANGLE
        val sweep = HEADING_HALF_ANGLE * 2f
        val oval = RectF(cx - coneRadius, cy - coneRadius, cx + coneRadius, cy + coneRadius)
        val path = Path().apply {
            moveTo(cx, cy)
            lineTo(
                cx + coneRadius * cos(Math.toRadians(start.toDouble())).toFloat(),
                cy + coneRadius * sin(Math.toRadians(start.toDouble())).toFloat(),
            )
            arcTo(oval, start, sweep, false)
            close()
        }
        val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            shader = RadialGradient(
                cx,
                cy,
                coneRadius,
                intArrayOf(
                    withAlpha(color, 0x66),
                    withAlpha(color, 0x55),
                    withAlpha(color, 0x00),
                ),
                floatArrayOf(0f, 0.5f, 1f),
                Shader.TileMode.CLAMP,
            )
        }
        canvas.drawPath(path, fill)
    }

    /** 圆环外侧的方向箭头，让朝向在缩小后仍然一眼可读。 */
    private fun drawHeadingArrow(
        canvas: Canvas,
        cx: Float,
        cy: Float,
        ringRadius: Float,
        heading: Float,
        color: Int,
        strokeWidth: Float,
    ) {
        val angle = heading - 90f
        val baseRadius = ringRadius * 1.02f
        val tipRadius = ringRadius * 1.42f
        val half = 13f
        fun point(radius: Float, degrees: Float): Pair<Float, Float> {
            val rad = Math.toRadians(degrees.toDouble())
            return (cx + radius * cos(rad)).toFloat() to (cy + radius * sin(rad)).toFloat()
        }
        val (ax, ay) = point(baseRadius, angle - half)
        val (bx, by) = point(baseRadius, angle + half)
        val (tx, ty) = point(tipRadius, angle)
        val path = Path().apply {
            moveTo(ax, ay)
            lineTo(tx, ty)
            lineTo(bx, by)
            close()
        }
        canvas.drawPath(
            path,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                style = Paint.Style.FILL
                this.color = 0xFFFFFFFF.toInt()
            },
        )
        canvas.drawPath(
            path,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                style = Paint.Style.STROKE
                this.strokeWidth = strokeWidth
                this.color = color
            },
        )
    }

    private fun withAlpha(color: Int, alpha: Int): Int =
        (color and 0x00FFFFFF) or ((alpha and 0xFF) shl 24)

    private fun wrapText(
        text: String,
        maxWidth: Float,
        paint: Paint,
        maxLines: Int,
    ): List<String> {
        if (paint.measureText(text) <= maxWidth) return listOf(text)
        val lines = mutableListOf<String>()
        val current = StringBuilder()
        var truncated = false
        for (char in text) {
            val candidate = current.toString() + char
            if (paint.measureText(candidate) > maxWidth && current.isNotEmpty()) {
                lines.add(current.toString())
                current.clear()
                if (lines.size >= maxLines) {
                    truncated = true
                    break
                }
            }
            current.append(char)
        }
        if (lines.size < maxLines && current.isNotEmpty()) {
            lines.add(current.toString())
        }
        if (truncated && lines.isNotEmpty()) {
            lines[lines.lastIndex] = lines.last().dropLast(1) + "…"
        }
        return lines.ifEmpty { listOf(text.take(1)) }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/BaiduMapView.kt`

> 百度地图实现：头像标记、朝向、缩放、2D/3D 与英文底图切换。

````kotlin
package com.shineleong.toughmind.ui.map

import android.os.Bundle
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.baidu.mapapi.map.BaiduMap
import com.baidu.mapapi.map.BitmapDescriptorFactory
import com.baidu.mapapi.map.MapStatus
import com.baidu.mapapi.map.MapStatusUpdateFactory
import com.baidu.mapapi.map.MapLanguage
import com.baidu.mapapi.map.Marker as BaiduMarker
import com.baidu.mapapi.map.MarkerOptions
import com.baidu.mapapi.map.Overlay
import com.baidu.mapapi.map.Polyline
import com.baidu.mapapi.map.PolylineOptions
import com.baidu.mapapi.map.MapView as BaiduMapView
import com.baidu.mapapi.model.LatLng
import com.baidu.mapapi.model.LatLngBounds
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.util.GeoMath

@Composable
internal fun BaiduCareMap(
    people: List<MapPerson>,
    places: List<MapPlace>,
    trail: List<com.shineleong.toughmind.data.model.SelfLocation>,
    route: List<LatLng>,
    mapStyle: MapStyle,
    modifier: Modifier,
    focusPersonId: String?,
    focusToken: Int,
    onPersonClick: (String) -> Unit,
    onPickMeetup: (Double, Double) -> Unit,
    onSearchPlace: () -> Unit,
    onMapClick: (Double, Double) -> Unit,
    onPoiClick: (Double, Double, String) -> Unit,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val currentOnClick by rememberUpdatedState(onPersonClick)
    val mapView = remember { BaiduMapView(context).apply { showZoomControls(false) } }
    val english = LocalAppLanguage.current == "en"
    LaunchedEffect(english) {
        // 百度英文地图需要在控制台开通「境内英文服务」高级权限；未开通时此调用不生效。
        kotlinx.coroutines.delay(800)
        runCatching {
            mapView.map.setMapLanguage(
                if (english) MapLanguage.ENGLISH else MapLanguage.CHINESE,
                true,
            )
        }
    }
    val markerSizePx = with(LocalDensity.current) { 50.dp.roundToPx() }
    val selfRing = MaterialTheme.colorScheme.primary.toArgb()
    val partnerRing = MaterialTheme.colorScheme.secondary.toArgb()
    val lineColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.62f).toArgb()
    val trailColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.32f).toArgb()
    val routeColor = MaterialTheme.colorScheme.secondary.copy(alpha = 0.92f).toArgb()
    val density = LocalDensity.current
    val fitPadding = remember(density) {
        intArrayOf(
            with(density) { 64.dp.roundToPx() },
            with(density) { 138.dp.roundToPx() },
            with(density) { 64.dp.roundToPx() },
            with(density) { 120.dp.roundToPx() },
        )
    }
    val markers = remember { mutableMapOf<String, BaiduMarker>() }
    val appliedIcons = remember { mutableMapOf<String, String>() }
    val lineHolder = remember { arrayOfNulls<Overlay>(1) }
    val trailHolder = remember { arrayOfNulls<Overlay>(1) }
    val routeHolder = remember { arrayOfNulls<Overlay>(1) }
    var fittedKey by remember { mutableStateOf("") }
    var handledFocusToken by remember { mutableIntStateOf(-1) }
    var zoomBefore3d by remember { androidx.compose.runtime.mutableFloatStateOf(0f) }
    var lastStyle by remember { mutableStateOf(MapStyle.NORMAL) }

    val iconSignature = people.joinToString("|") { it.iconSignature() }
    val bubbleColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.96f).toArgb()
    val bubbleTextColor = MaterialTheme.colorScheme.onSecondaryContainer.toArgb()
    val selfPerson = people.firstOrNull { it.isSelf }
    val icons = remember(people, iconSignature, bubbleColor, bubbleTextColor, selfRing, partnerRing) {
        people.associate { person ->
            val bearing = if (!person.isSelf && selfPerson != null) {
                GeoMath.bearingDegrees(selfPerson.lat, selfPerson.lon, person.lat, person.lon).toFloat()
            } else {
                null
            }
            person.id to AvatarMarkerFactory.create(
                avatar = person.avatar,
                initials = person.initials,
                ringColor = if (person.isSelf) selfRing else partnerRing,
                statusColor = person.statusColor.toArgb(),
                moodEmoji = person.statusEmoji,
                badgeText = null,
                heading = if (person.isSelf) person.heading else person.heading ?: bearing,
                online = person.online,
                showStatusBadge = false,
                bubbleText = person.bubbleText,
                bubbleColor = bubbleColor,
                bubbleTextColor = bubbleTextColor,
                sizePx = markerSizePx,
            )
        }
    }

    // 地点（会合点 / 目的地）用 GPS 针形标记，与人物头像区分开
    val meetupColor = MaterialTheme.colorScheme.tertiary.toArgb()
    val destinationColor = MaterialTheme.colorScheme.primary.toArgb()
    val placeLabelColor = MaterialTheme.colorScheme.onSurface.toArgb()
    val placeLabelBackground = MaterialTheme.colorScheme.surface.copy(alpha = 0.94f).toArgb()
    val placeSignature = places.joinToString("|") {
        "${it.id}:${it.name}:${it.kind}:$meetupColor:$destinationColor:$placeLabelColor:$placeLabelBackground"
    }
    val placeIcons = remember(placeSignature) {
        places.associate { place ->
            place.id to PlaceMarkerFactory.create(
                label = place.name,
                pinColor = if (place.kind == MapPlaceKind.MEETUP) meetupColor else destinationColor,
                labelColor = placeLabelColor,
                labelBackground = placeLabelBackground,
                sizePx = markerSizePx,
            )
        }
    }
    val placeMarkers = remember { mutableMapOf<String, BaiduMarker>() }
    val appliedPlaceIcons = remember { mutableMapOf<String, String>() }

    DisposableEffect(lifecycleOwner, mapView) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> mapView.onResume()
                Lifecycle.Event.ON_PAUSE -> mapView.onPause()
                Lifecycle.Event.ON_DESTROY -> mapView.onDestroy()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        mapView.map.setOnMarkerClickListener { marker ->
            val personId = marker.extraInfo?.getString(EXTRA_PERSON_ID).orEmpty()
            if (personId.isNotBlank()) {
                currentOnClick(personId)
                true
            } else {
                false
            }
        }
        mapView.map.setOnMapClickListener(object : com.baidu.mapapi.map.BaiduMap.OnMapClickListener {
            override fun onMapClick(point: LatLng?) {
                if (point != null) onMapClick(point.latitude, point.longitude)
            }

            override fun onMapPoiClick(poi: com.baidu.mapapi.map.MapPoi?) {
                val position = poi?.position ?: return
                onPoiClick(position.latitude, position.longitude, poi.name.orEmpty())
            }
        })
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            mapView.onDestroy()
        }
    }

    LaunchedEffect(Unit) {
        if (people.isEmpty()) {
            mapView.map.setMapStatus(
                MapStatusUpdateFactory.newLatLngZoom(LatLng(DEFAULT_LAT, DEFAULT_LON), 13f)
            )
        }
    }

    LaunchedEffect(mapStyle, mapView) {
        val map = mapView.map ?: return@LaunchedEffect
        val current = map.mapStatus ?: return@LaunchedEffect
        when (mapStyle) {
            MapStyle.NORMAL -> {
                map.setMapType(BaiduMap.MAP_TYPE_NORMAL)
                map.setBuildingsEnabled(false)
                map.uiSettings.setOverlookingGesturesEnabled(false)
                map.uiSettings.setRotateGesturesEnabled(false)
                map.uiSettings.setCompassEnabled(false)
            }
            MapStyle.THREE_D -> {
                map.setMapType(BaiduMap.MAP_TYPE_NORMAL)
                map.setBuildingsEnabled(true)
                map.uiSettings.setOverlookingGesturesEnabled(true)
                map.uiSettings.setRotateGesturesEnabled(true)
                map.uiSettings.setCompassEnabled(true)
            }
            MapStyle.SATELLITE -> {
                map.setMapType(BaiduMap.MAP_TYPE_SATELLITE)
                map.setBuildingsEnabled(false)
                map.uiSettings.setOverlookingGesturesEnabled(false)
                map.uiSettings.setRotateGesturesEnabled(false)
                map.uiSettings.setCompassEnabled(false)
            }
        }
        val is3d = mapStyle == MapStyle.THREE_D
        if (is3d && lastStyle != MapStyle.THREE_D) {
            zoomBefore3d = current.zoom
        }
        val targetZoom = when {
            is3d -> current.zoom.coerceAtLeast(19f)
            lastStyle == MapStyle.THREE_D && zoomBefore3d > 0f -> zoomBefore3d
            else -> current.zoom
        }
        val status = MapStatus.Builder(current)
            .overlook(if (is3d) -45f else 0f)
            .rotate(if (is3d) current.rotate else 0f)
            .zoom(targetZoom)
            .build()
        map.setMapStatus(MapStatusUpdateFactory.newMapStatus(status))
        lastStyle = mapStyle
    }

    LaunchedEffect(people, icons, trail) {
        val map = mapView.map
        val visibleIds = people.map { it.id }.toSet()
        markers.keys.toList().filter { it !in visibleIds }.forEach { id ->
            markers.remove(id)?.remove()
            appliedIcons.remove(id)
        }

        people.forEach { person ->
            val icon = icons[person.id] ?: return@forEach
            val point = LatLng(person.lat, person.lon)
            val iconKey = person.iconSignature()
            val marker = markers[person.id]
            if (marker == null) {
                markers[person.id] = map.addOverlay(
                    MarkerOptions()
                        .position(point)
                        .icon(BitmapDescriptorFactory.fromBitmap(icon.bitmap))
                        .anchor(icon.anchorX, icon.anchorY)
                        .clickable(true)
                        .extraInfo(Bundle().apply { putString(EXTRA_PERSON_ID, person.id) })
                ) as BaiduMarker
                appliedIcons[person.id] = iconKey
            } else {
                marker.position = point
                if (appliedIcons[person.id] != iconKey) {
                    marker.setIcon(BitmapDescriptorFactory.fromBitmap(icon.bitmap))
                    marker.setAnchor(icon.anchorX, icon.anchorY)
                    appliedIcons[person.id] = iconKey
                }
            }
        }

        val trailPoints = trail.map { LatLng(it.lat, it.lon) }
        if (trailPoints.size >= 2) {
            val trailLine = trailHolder[0]
            if (trailLine == null) {
                trailHolder[0] = map.addOverlay(
                    PolylineOptions()
                        .points(trailPoints)
                        .width(5f)
                        .color(trailColor)
                        .dottedLine(false)
                )
            } else {
                (trailLine as? Polyline)?.points = trailPoints
            }
        } else {
            trailHolder[0]?.let { it.remove(); trailHolder[0] = null }
        }

        val linePoints = people.map { LatLng(it.lat, it.lon) }
        if (linePoints.size >= 2) {
            val line = lineHolder[0]
            if (line == null) {
                lineHolder[0] = map.addOverlay(
                    PolylineOptions()
                        .points(linePoints)
                        .width(7f)
                        .color(lineColor)
                        .dottedLine(true)
                )
            } else {
                (line as? Polyline)?.points = linePoints
            }
        } else {
            lineHolder[0]?.let { it.remove(); lineHolder[0] = null }
        }

        val key = people.joinToString(",") { it.id }
        if (key != fittedKey && focusToken <= 0) {
            val located = people.filter { it.lat != 0.0 || it.lon != 0.0 }
            if (located.size >= 2) {
                val distance = GeoMath.distanceMeters(
                    located[0].lat,
                    located[0].lon,
                    located[1].lat,
                    located[1].lon,
                )
                if (distance < 3_000) {
                    val centerLat = (located[0].lat + located[1].lat) / 2
                    val centerLon = (located[0].lon + located[1].lon) / 2
                    map.setMapStatus(
                        MapStatusUpdateFactory.newLatLngZoom(LatLng(centerLat, centerLon), 15f)
                    )
                } else {
                    val bounds = LatLngBounds.Builder().apply {
                        located.forEach { include(LatLng(it.lat, it.lon)) }
                    }.build()
                    map.setMapStatus(
                        MapStatusUpdateFactory.newLatLngBounds(
                            bounds,
                            fitPadding[0],
                            fitPadding[1],
                            fitPadding[2],
                            fitPadding[3],
                        )
                    )
                }
            } else if (located.size == 1) {
                map.setMapStatus(
                    MapStatusUpdateFactory.newLatLngZoom(
                        LatLng(located[0].lat, located[0].lon),
                        15.5f,
                    )
                )
            }
            fittedKey = key
        }
    }

    LaunchedEffect(places, placeIcons) {
        val map = mapView.map
        val visibleIds = places.map { it.id }.toSet()
        placeMarkers.keys.toList().filter { it !in visibleIds }.forEach { id ->
            placeMarkers.remove(id)?.remove()
            appliedPlaceIcons.remove(id)
        }
        places.forEach { place ->
            val icon = placeIcons[place.id] ?: return@forEach
            val point = LatLng(place.lat, place.lon)
            val iconKey = "${place.name}:${place.kind}"
            val marker = placeMarkers[place.id]
            if (marker == null) {
                placeMarkers[place.id] = map.addOverlay(
                    MarkerOptions()
                        .position(point)
                        .icon(BitmapDescriptorFactory.fromBitmap(icon.bitmap))
                        .anchor(icon.anchorX, icon.anchorY)
                        .clickable(false)
                ) as BaiduMarker
                appliedPlaceIcons[place.id] = iconKey
            } else {
                marker.position = point
                if (appliedPlaceIcons[place.id] != iconKey) {
                    marker.setIcon(BitmapDescriptorFactory.fromBitmap(icon.bitmap))
                    marker.setAnchor(icon.anchorX, icon.anchorY)
                    appliedPlaceIcons[place.id] = iconKey
                }
            }
        }
    }

    LaunchedEffect(focusPersonId, focusToken, people) {
        if (focusToken <= 0 || focusToken == handledFocusToken) return@LaunchedEffect
        val target = people.firstOrNull { it.id == focusPersonId } ?: return@LaunchedEffect
        if (target.lat == 0.0 && target.lon == 0.0) return@LaunchedEffect
        handledFocusToken = focusToken
        mapView.map.setMapStatus(
            MapStatusUpdateFactory.newLatLngZoom(
                LatLng(target.lat, target.lon),
                16f,
            )
        )
    }

    LaunchedEffect(route, routeColor) {
        val map = mapView.map
        if (route.size >= 2) {
            val line = routeHolder[0]
            if (line == null) {
                routeHolder[0] = map.addOverlay(
                    PolylineOptions()
                        .points(route)
                        .width(14f)
                        .color(routeColor)
                        .dottedLine(false)
                )
            } else {
                (line as? Polyline)?.points = route
            }
        } else {
            routeHolder[0]?.let { it.remove(); routeHolder[0] = null }
        }
    }

    CareMapBox(modifier) {
        AndroidView(factory = { mapView }, modifier = Modifier.fillMaxSize())
        MapControls(
            onZoomIn = {
                val status = mapView.map.mapStatus
                mapView.map.setMapStatus(
                    MapStatusUpdateFactory.zoomTo((status.zoom + 1.5f).coerceAtMost(19f))
                )
            },
            onSearchPlace = onSearchPlace,
            onZoomOut = {
                val status = mapView.map.mapStatus
                mapView.map.setMapStatus(
                    MapStatusUpdateFactory.zoomTo((status.zoom - 1.5f).coerceAtLeast(4f))
                )
            },
            onRecenter = {
                val target = people.firstOrNull { it.isSelf } ?: people.firstOrNull()
                if (target != null) {
                    mapView.map.setMapStatus(
                        MapStatusUpdateFactory.newLatLngZoom(
                            LatLng(target.lat, target.lon),
                            16f,
                        )
                    )
                }
            },
            onPickMeetup = {
                val center = mapView.map.mapStatus.target
                onPickMeetup(center.latitude, center.longitude)
            },
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/LocationMap.kt`

> 地图入口：按 `MapConfig.USE_BAIDU` 选择百度 / OSM，并叠加控件与选中回调。

````kotlin
package com.shineleong.toughmind.ui.map

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Flag
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SmallFloatingActionButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.baidu.mapapi.model.LatLng
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LocalCareColors

internal const val EXTRA_PERSON_ID = "map_person_id"
internal const val DEFAULT_LAT = 30.2741
internal const val DEFAULT_LON = 120.1551

/**
 * 全屏"念安"地图：显示我与 TA 的头像标记（带朝向），以及会合点 / 目的地地点针。
 * 头像可点击展开详情；GPS 针形只用于地点。百度地图为主引擎，osmdroid 为免 Key 回退。
 */
@Composable
fun CareMap(
    people: List<MapPerson>,
    modifier: Modifier = Modifier,
    places: List<MapPlace> = emptyList(),
    trail: List<com.shineleong.toughmind.data.model.SelfLocation> = emptyList(),
    route: List<LatLng> = emptyList(),
    mapStyle: MapStyle = MapStyle.NORMAL,
    focusPersonId: String? = null,
    focusToken: Int = 0,
    onPersonClick: (String) -> Unit,
    onPickMeetup: (Double, Double) -> Unit,
    onSearchPlace: () -> Unit,
    onMapClick: (Double, Double) -> Unit,
    onPoiClick: (Double, Double, String) -> Unit,
) {
    if (MapConfig.USE_BAIDU) {
        BaiduCareMap(
            people,
            places,
            trail,
            route,
            mapStyle,
            modifier,
            focusPersonId,
            focusToken,
            onPersonClick,
            onPickMeetup,
            onSearchPlace,
            onMapClick,
            onPoiClick,
        )
    } else {
        OsmCareMap(
            people,
            places,
            trail,
            route,
            mapStyle,
            modifier,
            focusPersonId,
            focusToken,
            onPersonClick,
            onPickMeetup,
            onSearchPlace,
            onMapClick,
            onPoiClick,
        )
    }
}

@Composable
internal fun CareMapBox(modifier: Modifier, content: @Composable () -> Unit) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(0.dp))
            .background(LocalCareColors.current.mapBackground),
    ) {
        content()
    }
}

@Composable
internal fun MapControls(
    onZoomIn: () -> Unit,
    onZoomOut: () -> Unit,
    onRecenter: () -> Unit,
    onPickMeetup: () -> Unit,
    onSearchPlace: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(end = 16.dp, bottom = 96.dp),
        horizontalAlignment = Alignment.End,
        verticalArrangement = Arrangement.Bottom,
    ) {
        SmallFloatingActionButton(
            onClick = onZoomIn,
            containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
            contentColor = MaterialTheme.colorScheme.primary,
        ) {
            Icon(
                Icons.Filled.Add,
                contentDescription = "放大地图",
                modifier = Modifier.size(AppDimens.IconSize),
            )
        }
        Box(Modifier.padding(top = 8.dp)) {
            SmallFloatingActionButton(
                onClick = onZoomOut,
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
                contentColor = MaterialTheme.colorScheme.primary,
            ) {
                Icon(
                Icons.Filled.Remove,
                contentDescription = "缩小地图",
                modifier = Modifier.size(AppDimens.IconSize),
            )
            }
        }
        Box(Modifier.padding(top = 8.dp)) {
            SmallFloatingActionButton(
                onClick = onRecenter,
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
                contentColor = MaterialTheme.colorScheme.primary,
            ) {
                Icon(
                Icons.Filled.MyLocation,
                contentDescription = "回到我的位置",
                modifier = Modifier.size(AppDimens.IconSize),
            )
            }
        }
        Box(Modifier.padding(top = 8.dp)) {
            SmallFloatingActionButton(
                onClick = onSearchPlace,
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
                contentColor = MaterialTheme.colorScheme.primary,
            ) {
                Icon(
                Icons.Filled.Send,
                contentDescription = "搜索地点",
                modifier = Modifier.size(AppDimens.IconSize),
            )
            }
        }
        Box(Modifier.padding(top = 8.dp)) {
            SmallFloatingActionButton(
                onClick = onPickMeetup,
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
                contentColor = MaterialTheme.colorScheme.primary,
            ) {
                Icon(
                Icons.Filled.Flag,
                contentDescription = "设为会合点",
                modifier = Modifier.size(AppDimens.IconSize),
            )
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/MapConfig.kt`

````kotlin
package com.shineleong.toughmind.ui.map

/**
 * 地图引擎切换开关。
 *
 * 已接入百度地图 SDK（AK 配置于 AndroidManifest.xml）。
 *  - USE_BAIDU = true  → 使用百度地图（默认，功能更全，贴合国内场景）
 *  - USE_BAIDU = false → 回退开源 osmdroid + OpenStreetMap（免 Key）
 *
 * 切换仅需修改本开关，业务层调用 LocationMap 无需改动。
 */
object MapConfig {
    const val USE_BAIDU = true
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/MapPerson.kt`

````kotlin
package com.shineleong.toughmind.ui.map

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap

/** 地图上的一位家庭成员（自己或 TA）。 */
data class MapPerson(
    val id: String,
    val name: String,
    val initials: String,
    val avatar: ImageBitmap?,
    val lat: Double,
    val lon: Double,
    val isSelf: Boolean,
    val statusColor: Color,
    val online: Boolean,
    val statusEmoji: String = "❔",
    val moodEmoji: String = "🙂",
    val bubbleText: String? = null,
    val heading: Float? = null,
)
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/MapStyle.kt`

````kotlin
package com.shineleong.toughmind.ui.map

/** 地图底图样式：普通 2D、带俯角的 3D、卫星影像。 */
enum class MapStyle(val label: String) {
    NORMAL("2D"),
    THREE_D("3D"),
    SATELLITE("卫星"),
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/OsmMapView.kt`

> osmdroid 回退实现：无 Key 时仍可显示地图与标记。

````kotlin
package com.shineleong.toughmind.ui.map

import android.graphics.drawable.BitmapDrawable
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.baidu.mapapi.model.LatLng
import com.shineleong.toughmind.util.GeoMath
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView as OsmMapView
import org.osmdroid.views.overlay.Marker as OsmMarker
import org.osmdroid.views.overlay.Polyline as OsmPolyline

@Composable
internal fun OsmCareMap(
    people: List<MapPerson>,
    places: List<MapPlace>,
    trail: List<com.shineleong.toughmind.data.model.SelfLocation>,
    route: List<LatLng>,
    mapStyle: MapStyle,
    modifier: Modifier,
    focusPersonId: String?,
    focusToken: Int,
    onPersonClick: (String) -> Unit,
    onPickMeetup: (Double, Double) -> Unit,
    onSearchPlace: () -> Unit,
    onMapClick: (Double, Double) -> Unit,
    onPoiClick: (Double, Double, String) -> Unit,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val currentOnClick by rememberUpdatedState(onPersonClick)
    val mapView = remember {
        OsmMapView(context).apply {
            setTileSource(TileSourceFactory.MAPNIK)
            setMultiTouchControls(true)
            setBuiltInZoomControls(false)
            controller.setZoom(15.0)
            controller.setCenter(GeoPoint(DEFAULT_LAT, DEFAULT_LON))
        }
    }
    val markerSizePx = with(LocalDensity.current) { 50.dp.roundToPx() }
    val selfRing = MaterialTheme.colorScheme.primary.toArgb()
    val partnerRing = MaterialTheme.colorScheme.secondary.toArgb()
    val lineColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.62f).toArgb()
    val trailColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.32f).toArgb()
    val routeColor = MaterialTheme.colorScheme.secondary.copy(alpha = 0.92f).toArgb()
    val markers = remember { mutableMapOf<String, OsmMarker>() }
    val appliedIcons = remember { mutableMapOf<String, String>() }
    val polyline = remember {
        OsmPolyline(mapView).apply {
            setColor(lineColor)
            setWidth(6f)
        }
    }
    val trailLine = remember {
        OsmPolyline(mapView).apply {
            setColor(trailColor)
            setWidth(4f)
        }
    }
    val routeLine = remember {
        OsmPolyline(mapView).apply {
            setColor(routeColor)
            setWidth(9f)
        }
    }
    var fittedKey by remember { mutableStateOf("") }
    var handledFocusToken by remember { mutableIntStateOf(-1) }

    val iconSignature = people.joinToString("|") { it.iconSignature() }
    val bubbleColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.96f).toArgb()
    val bubbleTextColor = MaterialTheme.colorScheme.onSecondaryContainer.toArgb()
    val selfPerson = people.firstOrNull { it.isSelf }
    val markerIcons = remember(people, iconSignature, bubbleColor, bubbleTextColor, selfRing, partnerRing) {
        people.associate { person ->
            val bearing = if (!person.isSelf && selfPerson != null) {
                GeoMath.bearingDegrees(selfPerson.lat, selfPerson.lon, person.lat, person.lon).toFloat()
            } else {
                null
            }
            person.id to AvatarMarkerFactory.create(
                avatar = person.avatar,
                initials = person.initials,
                ringColor = if (person.isSelf) selfRing else partnerRing,
                statusColor = person.statusColor.toArgb(),
                moodEmoji = person.statusEmoji,
                badgeText = null,
                heading = if (person.isSelf) person.heading else person.heading ?: bearing,
                online = person.online,
                showStatusBadge = false,
                bubbleText = person.bubbleText,
                bubbleColor = bubbleColor,
                bubbleTextColor = bubbleTextColor,
                sizePx = markerSizePx,
            )
        }
    }

    // 地点（会合点 / 目的地）用 GPS 针形标记，与人物头像区分开
    val meetupColor = MaterialTheme.colorScheme.tertiary.toArgb()
    val destinationColor = MaterialTheme.colorScheme.primary.toArgb()
    val placeLabelColor = MaterialTheme.colorScheme.onSurface.toArgb()
    val placeLabelBackground = MaterialTheme.colorScheme.surface.copy(alpha = 0.94f).toArgb()
    val placeSignature = places.joinToString("|") {
        "${it.id}:${it.name}:${it.kind}:$meetupColor:$destinationColor:$placeLabelColor:$placeLabelBackground"
    }
    val placeIcons = remember(placeSignature) {
        places.associate { place ->
            place.id to PlaceMarkerFactory.create(
                label = place.name,
                pinColor = if (place.kind == MapPlaceKind.MEETUP) meetupColor else destinationColor,
                labelColor = placeLabelColor,
                labelBackground = placeLabelBackground,
                sizePx = markerSizePx,
            )
        }
    }
    val placeMarkers = remember { mutableMapOf<String, OsmMarker>() }
    val appliedPlaceIcons = remember { mutableMapOf<String, String>() }

    DisposableEffect(lifecycleOwner, mapView) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> mapView.onResume()
                Lifecycle.Event.ON_PAUSE -> mapView.onPause()
                Lifecycle.Event.ON_DESTROY -> mapView.onDetach()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        mapView.overlays.add(trailLine)
        mapView.overlays.add(polyline)
        mapView.overlays.add(routeLine)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            mapView.onDetach()
        }
    }

    LaunchedEffect(mapStyle, mapView) {
        // osmdroid 没有真正的 3D 建筑，3D 选项在 UI 上会被禁用；这里只切普通/卫星。
        mapView.setTileSource(
            if (mapStyle == MapStyle.SATELLITE) TileSourceFactory.USGS_SAT else TileSourceFactory.MAPNIK
        )
        mapView.invalidate()
    }

    LaunchedEffect(people, markerIcons, trail) {
        val visibleIds = people.map { it.id }.toSet()
        markers.keys.toList().filter { it !in visibleIds }.forEach { id ->
            markers.remove(id)?.let { mapView.overlays.remove(it) }
            appliedIcons.remove(id)
        }
        people.forEach { person ->
            val icon: MarkerIcon = markerIcons[person.id] ?: return@forEach
            val iconKey = person.iconSignature()
            val marker = markers.getOrPut(person.id) {
                OsmMarker(mapView).apply {
                    setAnchor(OsmMarker.ANCHOR_CENTER, OsmMarker.ANCHOR_CENTER)
                    setOnMarkerClickListener { _, _ ->
                        currentOnClick(person.id)
                        true
                    }
                }.also { mapView.overlays.add(it) }
            }
            marker.position = GeoPoint(person.lat, person.lon)
            marker.title = person.name
            if (appliedIcons[person.id] != iconKey) {
                marker.icon = BitmapDrawable(context.resources, icon.bitmap)
                marker.setAnchor(icon.anchorX, icon.anchorY)
                appliedIcons[person.id] = iconKey
            }
        }
        polyline.setPoints(people.map { GeoPoint(it.lat, it.lon) })
        trailLine.setPoints(trail.map { GeoPoint(it.lat, it.lon) })
        mapView.invalidate()

        val key = people.joinToString(",") { it.id }
        if (key != fittedKey && focusToken <= 0) {
            val located = people.filter { it.lat != 0.0 || it.lon != 0.0 }
            if (located.size >= 2) {
                val distance = GeoMath.distanceMeters(
                    located[0].lat,
                    located[0].lon,
                    located[1].lat,
                    located[1].lon,
                )
                if (distance < 3_000) {
                    val centerLat = (located[0].lat + located[1].lat) / 2
                    val centerLon = (located[0].lon + located[1].lon) / 2
                    mapView.controller.setCenter(GeoPoint(centerLat, centerLon))
                    mapView.controller.setZoom(15.0)
                } else {
                    val box = BoundingBox(
                        located.maxOf { it.lat },
                        located.maxOf { it.lon },
                        located.minOf { it.lat },
                        located.minOf { it.lon },
                    )
                    mapView.zoomToBoundingBox(box, false)
                }
            } else if (located.size == 1) {
                mapView.controller.setCenter(GeoPoint(located[0].lat, located[0].lon))
                mapView.controller.setZoom(15.5)
            }
            fittedKey = key
        }
        mapView.invalidate()
    }

    LaunchedEffect(places, placeIcons) {
        val visibleIds = places.map { it.id }.toSet()
        placeMarkers.keys.toList().filter { it !in visibleIds }.forEach { id ->
            placeMarkers.remove(id)?.let { mapView.overlays.remove(it) }
            appliedPlaceIcons.remove(id)
        }
        places.forEach { place ->
            val icon: MarkerIcon = placeIcons[place.id] ?: return@forEach
            val iconKey = "${place.name}:${place.kind}"
            val marker = placeMarkers.getOrPut(place.id) {
                OsmMarker(mapView).apply {
                    setAnchor(OsmMarker.ANCHOR_CENTER, OsmMarker.ANCHOR_BOTTOM)
                    setOnMarkerClickListener { _, _ -> false }
                }.also { mapView.overlays.add(it) }
            }
            marker.position = GeoPoint(place.lat, place.lon)
            marker.title = place.name
            if (appliedPlaceIcons[place.id] != iconKey) {
                marker.icon = BitmapDrawable(context.resources, icon.bitmap)
                marker.setAnchor(icon.anchorX, icon.anchorY)
                appliedPlaceIcons[place.id] = iconKey
            }
        }
        mapView.invalidate()
    }

    LaunchedEffect(focusPersonId, focusToken, people) {
        if (focusToken <= 0 || focusToken == handledFocusToken) return@LaunchedEffect
        val target = people.firstOrNull { it.id == focusPersonId } ?: return@LaunchedEffect
        if (target.lat == 0.0 && target.lon == 0.0) return@LaunchedEffect
        handledFocusToken = focusToken
        mapView.controller.animateTo(
            GeoPoint(target.lat, target.lon),
            16.0,
            350L,
        )
    }

    LaunchedEffect(route, routeColor) {
        routeLine.setPoints(route.map { GeoPoint(it.latitude, it.longitude) })
        mapView.invalidate()
    }

    CareMapBox(modifier) {
        AndroidView(factory = { mapView }, modifier = Modifier.fillMaxSize())
        MapControls(
            onZoomIn = { mapView.controller.setZoom((mapView.zoomLevelDouble + 1.5).coerceAtMost(19.0)) },
            onSearchPlace = onSearchPlace,
            onZoomOut = { mapView.controller.setZoom((mapView.zoomLevelDouble - 1.5).coerceAtLeast(3.0)) },
            onRecenter = {
                val target = people.firstOrNull { it.isSelf } ?: people.firstOrNull()
                if (target != null) {
                    mapView.controller.setCenter(GeoPoint(target.lat, target.lon))
                    mapView.controller.setZoom(16.0)
                }
            },
            onPickMeetup = {
                val center = mapView.mapCenter
                onPickMeetup(center.latitude, center.longitude)
            },
        )
    }
}

/** 人物图标的缓存键：头像、心情、在线状态与朝向（按 4° 分桶）任一变化都重建位图。 */
internal fun MapPerson.iconSignature(): String {
    val headingBucket = heading?.let { (it / 4f).toInt() } ?: -1
    return "$id:$initials:${statusColor.value}:${avatar?.hashCode()}:$statusEmoji:$bubbleText:" +
        "$online:$isSelf:$headingBucket"
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/map/PlaceMarkerFactory.kt`

````kotlin
package com.shineleong.toughmind.ui.map

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import kotlin.math.max

/** 地图地点类型：会合点 / 导航目的地。 */
enum class MapPlaceKind { MEETUP, DESTINATION }

/**
 * 地图上的一个“地点”（不是人）。
 * 会合点、地图选点、搜索结果都走这里，用 GPS 针形标记落在真实坐标上。
 */
data class MapPlace(
    val id: String,
    val lat: Double,
    val lon: Double,
    val name: String = "",
    val kind: MapPlaceKind = MapPlaceKind.DESTINATION,
)

/**
 * 地点 Marker：经典 GPS 水滴针 + 针心白点 + 右侧名称胶囊。
 * 针尖是真实坐标（anchorY = 针尖 / 画布高度），与人物的头像圆心锚点区分开。
 */
object PlaceMarkerFactory {

    fun create(
        label: String,
        pinColor: Int,
        labelColor: Int,
        labelBackground: Int,
        sizePx: Int = 192,
    ): MarkerIcon {
        val size = sizePx.coerceAtLeast(72).toFloat()
        val radius = size * 0.30f
        val headCy = radius + size * 0.10f
        val tipY = headCy + radius * 1.85f
        val pinCx = radius + size * 0.07f

        val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = labelColor
            textSize = size * 0.30f
            textAlign = Paint.Align.LEFT
            isFakeBoldText = true
        }
        val text = ellipsize(label.trim(), size * 3.0f, textPaint)
        val chipPadX = size * 0.20f
        val chipPadY = size * 0.12f
        val textHeight = textPaint.descent() - textPaint.ascent()
        val chipWidth = if (text.isEmpty()) 0f else textPaint.measureText(text) + chipPadX * 2
        val chipHeight = textHeight + chipPadY * 2
        val chipLeft = pinCx + radius + size * 0.10f
        val chipTop = headCy - chipHeight / 2f

        val canvasWidth = (
            if (text.isEmpty()) pinCx + radius + size * 0.10f
            else chipLeft + chipWidth + size * 0.06f
            ).toInt()
        val canvasHeight = (tipY + size * 0.08f).toInt()

        val bitmap = Bitmap.createBitmap(
            max(canvasWidth, 1),
            max(canvasHeight, 1),
            Bitmap.Config.ARGB_8888,
        )
        val canvas = Canvas(bitmap)

        val pin = Path().apply {
            moveTo(pinCx, tipY)
            cubicTo(
                pinCx - radius * 0.55f,
                headCy + radius * 1.05f,
                pinCx - radius,
                headCy + radius * 0.55f,
                pinCx - radius,
                headCy,
            )
            arcTo(
                RectF(pinCx - radius, headCy - radius, pinCx + radius, headCy + radius),
                180f,
                180f,
                false,
            )
            cubicTo(
                pinCx + radius,
                headCy + radius * 0.55f,
                pinCx + radius * 0.55f,
                headCy + radius * 1.05f,
                pinCx,
                tipY,
            )
            close()
        }

        // 投影
        canvas.drawPath(
            pin,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = 0x33000000
                setShadowLayer(size * 0.055f, 0f, size * 0.04f, 0x55000000)
            },
        )
        // 针体
        canvas.drawPath(pin, Paint(Paint.ANTI_ALIAS_FLAG).apply { color = pinColor })
        canvas.drawPath(
            pin,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                style = Paint.Style.STROKE
                strokeWidth = max(2f, size * 0.028f)
                color = 0xFFFFFFFF.toInt()
            },
        )
        // 针心：白底 + 主题色小点
        canvas.drawCircle(
            pinCx,
            headCy,
            radius * 0.36f,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = 0xFFFFFFFF.toInt() },
        )
        canvas.drawCircle(
            pinCx,
            headCy,
            radius * 0.17f,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = pinColor },
        )

        // 名称胶囊
        if (text.isNotEmpty()) {
            val chip = RectF(chipLeft, chipTop, chipLeft + chipWidth, chipTop + chipHeight)
            canvas.drawRoundRect(
                chip,
                chipHeight / 2f,
                chipHeight / 2f,
                Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    color = labelBackground
                    setShadowLayer(size * 0.04f, 0f, size * 0.02f, 0x44000000)
                },
            )
            canvas.drawRoundRect(
                chip,
                chipHeight / 2f,
                chipHeight / 2f,
                Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    style = Paint.Style.STROKE
                    strokeWidth = max(1.5f, size * 0.012f)
                    color = withAlpha(pinColor, 0x55)
                },
            )
            val baseline = chipTop + chipPadY - textPaint.fontMetrics.ascent
            canvas.drawText(text, chipLeft + chipPadX, baseline, textPaint)
        }

        return MarkerIcon(
            bitmap = bitmap,
            anchorX = pinCx / canvasWidth,
            anchorY = tipY / canvasHeight,
        )
    }

    private fun ellipsize(text: String, maxWidth: Float, paint: Paint): String {
        if (text.isEmpty()) return ""
        if (paint.measureText(text) <= maxWidth) return text
        var result = text
        while (result.length > 1 && paint.measureText("$result…") > maxWidth) {
            result = result.dropLast(1)
        }
        return "$result…"
    }

    private fun withAlpha(color: Int, alpha: Int): Int =
        (color and 0x00FFFFFF) or ((alpha and 0xFF) shl 24)
}
````

<a id="s03-2"></a>

## 步骤 03.2 · 首页与导航面板

`HomeScreen` 组装地图、顶部浮层、导航浮层、约见搜索、人物详情与心情弹窗；拆分后每个文件只负责一类浮层。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeMapOverlays.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeMeetup.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeNavigationSheet.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomePersonSheet.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeScreen.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeViewModel.kt`
- `app/src/main/java/com/shineleong/toughmind/ui/screen/home/RouteGuidance.kt`

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeMapOverlays.kt`

> 地图顶部浮层、导航中浮层、连接徽标、状态胶囊与心情气泡。

````kotlin
package com.shineleong.toughmind.ui.screen.home

import android.Manifest
import android.media.AudioManager
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.width
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Slider
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.component.LocalTtsRate
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.CareStatusBadge
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.NavigationModeDialog
import com.shineleong.toughmind.ui.screen.chat.ChatSheet
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Add
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.WeatherPill
import com.shineleong.toughmind.ui.component.formatDistance
import com.shineleong.toughmind.util.BaiduPlaceSearch
import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRoutePlanner
import com.shineleong.toughmind.util.planBaiduRoute
import com.shineleong.toughmind.util.PlaceSuggestion
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import com.shineleong.toughmind.util.NavigationHelper
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.iconLabel
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.map.CareMap
import com.shineleong.toughmind.ui.map.MapPerson
import com.shineleong.toughmind.ui.map.MapPlace
import com.shineleong.toughmind.ui.map.MapPlaceKind
import com.shineleong.toughmind.ui.map.MapStyle
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.NavyPrimary
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlin.math.roundToInt
import kotlinx.coroutines.delay

@Composable
internal fun MapTopOverlay(
    self: PersonPresence?,
    partner: PersonPresence?,
    connectionState: ConnectionState,
    avatar: ImageBitmap?,
    focusPersonId: String?,
    onOpenDrawer: () -> Unit,
    onSelect: (String) -> Unit,
    mapStyle: MapStyle,
    onMapStyleChange: (MapStyle) -> Unit,
    is3dSupported: Boolean,
) {
    val focusedName = when {
        focusPersonId == null -> null
        focusPersonId == self?.id -> "我"
        focusPersonId == partner?.id -> partner?.name
        else -> null
    }
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(start = 12.dp, end = 12.dp, top = 4.dp, bottom = 6.dp),
    ) {
        var showTargets by remember { mutableStateOf(false) }
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .shadow(6.dp, CircleShape)
                    .background(SurfaceWhite, CircleShape)
                    .clickable(onClick = onOpenDrawer)
                    .padding(2.dp),
                contentAlignment = Alignment.Center,
            ) {
                Avatar(
                    nickname = self?.name,
                    size = 40.dp,
                    imageBitmap = avatar,
                    online = self?.online == true,
                    showStatusBadge = false,
                )
            }
            Spacer(Modifier.weight(1f))
            Column(horizontalAlignment = Alignment.End) {
                MapStyleSwitcher(
                    selected = mapStyle,
                    is3dSupported = is3dSupported,
                    onSelect = onMapStyleChange,
                )
                Spacer(Modifier.height(6.dp))
                Box {
                    Surface(
                        onClick = { showTargets = true },
                        shape = RoundedCornerShape(AppDimens.ButtonCorner),
                        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.95f),
                        shadowElevation = 2.dp,
                        modifier = Modifier.height(AppDimens.ButtonHeight),
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                focusedName ?: partner?.name ?: "对象",
                                style = MaterialTheme.typography.bodySmall,
                                fontWeight = FontWeight.SemiBold,
                            )
                            Icon(
                                Icons.Filled.ArrowDropDown,
                                contentDescription = "切换对象",
                                modifier = Modifier.size(AppDimens.IconSize),
                            )
                        }
                    }
                    DropdownMenu(expanded = showTargets, onDismissRequest = { showTargets = false }) {
                        self?.let { me ->
                            DropdownMenuItem(
                                text = { Text("我") },
                                onClick = {
                                    onSelect(me.id)
                                    showTargets = false
                                },
                            )
                        }
                        partner?.let { other ->
                            DropdownMenuItem(
                                text = { Text(other.name) },
                                onClick = {
                                    onSelect(other.id)
                                    showTargets = false
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MapStyleSwitcher(
    selected: MapStyle,
    is3dSupported: Boolean,
    onSelect: (MapStyle) -> Unit,
) {
    Surface(
        shape = RoundedCornerShape(AppDimens.ButtonCorner),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.95f),
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.16f)),
        modifier = Modifier
            .width(205.dp)
            .height(AppDimens.ButtonHeight),
    ) {
        Row(modifier = Modifier.fillMaxHeight()) {
            MapStyle.entries.forEach { style ->
                val enabled = style != MapStyle.THREE_D || is3dSupported
                val active = selected == style
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .padding(3.dp)
                        .clip(RoundedCornerShape(3.dp))
                        .background(
                            if (active) MaterialTheme.colorScheme.primary.copy(alpha = 0.14f)
                            else Color.Transparent
                        )
                        .clickable(enabled = enabled) { onSelect(style) },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = style.label,
                        style = MaterialTheme.typography.labelMedium,
                        color = when {
                            !enabled -> MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
                            active -> MaterialTheme.colorScheme.primary
                            else -> MaterialTheme.colorScheme.onSurfaceVariant
                        },
                        fontWeight = if (active) FontWeight.SemiBold else FontWeight.Normal,
                        maxLines = 1,
                        softWrap = false,
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun NavigationActiveOverlay(
    target: NavTarget,
    self: PersonPresence?,
    partner: PersonPresence?,
    mode: NavMode,
    route: BaiduRoute?,
    onEnd: () -> Unit,
) {
    val fallbackDistance = if (self != null) {
        GeoMath.distanceMeters(self.lat, self.lon, target.lat, target.lon)
    } else {
        0.0
    }
    val progress = remember(self?.lat, self?.lon, route) {
        route?.progressAt(self?.lat ?: 0.0, self?.lon ?: 0.0)
    }
    val modeLabel = when (mode) {
        NavMode.WALKING -> "步行"
        NavMode.EBIKE -> "骑行"
        NavMode.TRANSIT -> "公交"
        NavMode.DRIVING -> "驾车"
    }
    val distanceToManeuver = progress?.distanceToManeuverMeters ?: fallbackDistance
    val remainingMeters = progress?.remainingMeters ?: fallbackDistance
    val remainingSeconds = progress?.remainingSeconds
        ?: route?.durationSeconds
        ?: ((fallbackDistance / 1000.0) / 30.0 * 3600).toInt().coerceAtLeast(60)
    val speedMetersPerSecond = if ((route?.distanceMeters ?: 0) > 0 && (route?.durationSeconds ?: 0) > 0) {
        route!!.distanceMeters.toDouble() / route!!.durationSeconds
    } else {
        when (mode) {
            NavMode.WALKING -> 1.4
            NavMode.EBIKE -> 4.5
            NavMode.TRANSIT -> 6.5
            NavMode.DRIVING -> 9.0
        }
    }
    val secondsToManeuver = (distanceToManeuver / speedMetersPerSecond)
        .roundToInt()
        .coerceAtLeast(1)
    val nextInstruction = progress?.nextInstruction
    val lastRouteStepIndex = (route?.steps?.lastIndex ?: -1)
    val onLastStep = progress != null && progress.stepIndex >= lastRouteStepIndex
    val instruction = when {
        nextInstruction != null -> nextInstruction
        onLastStep -> "到达目的地"
        else -> progress?.instruction ?: "沿当前道路前往 ${target.name}"
    }
    val upcomingInstruction = route?.steps?.getOrNull((progress?.stepIndex ?: 0) + 2)?.instruction

    val bearing = if (self != null) {
        GeoMath.bearingDegrees(self.lat, self.lon, target.lat, target.lon)
    } else 0.0

    val context = LocalContext.current
    val english = LocalAppLanguage.current == "en"
    val ttsRate = LocalTtsRate.current
    var voiceOn by remember { mutableStateOf(true) }
    var ttsReady by remember { mutableStateOf(false) }
    var tts by remember { mutableStateOf<android.speech.tts.TextToSpeech?>(null) }
    val audioManager = remember(context) {
        context.getSystemService(AudioManager::class.java)
    }
    val maxVolume = remember(audioManager) {
        audioManager?.getStreamMaxVolume(AudioManager.STREAM_MUSIC)?.coerceAtLeast(1) ?: 1
    }
    var volume by remember {
        mutableFloatStateOf(
            ((audioManager?.getStreamVolume(AudioManager.STREAM_MUSIC) ?: 0).toFloat() / maxVolume)
                .coerceIn(0f, 1f)
        )
    }
    var lastVolume by remember { mutableFloatStateOf(volume.coerceAtLeast(0.6f)) }
    fun applyVolume(value: Float) {
        volume = value.coerceIn(0f, 1f)
        audioManager?.setStreamVolume(
            AudioManager.STREAM_MUSIC,
            (volume * maxVolume).roundToInt(),
            0,
        )
        voiceOn = volume > 0f
        if (volume <= 0f) tts?.stop()
    }
    DisposableEffect(context, english) {
        val engine = android.speech.tts.TextToSpeech(context) { status ->
            ttsReady = status == android.speech.tts.TextToSpeech.SUCCESS
        }
        engine.language = if (english) java.util.Locale.ENGLISH else java.util.Locale.CHINA
        engine.setSpeechRate(ttsRate.coerceIn(0.7f, 1.3f))
        engine.setAudioAttributes(
            android.media.AudioAttributes.Builder()
                .setUsage(android.media.AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
                .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                .build()
        )
        tts = engine
        onDispose {
            ttsReady = false
            engine.stop()
            engine.shutdown()
        }
    }
    LaunchedEffect(voiceOn) {
        if (!voiceOn) tts?.stop()
    }
    LaunchedEffect(ttsRate) {
        tts?.setSpeechRate(ttsRate.coerceIn(0.7f, 1.3f))
    }

    val currentProgress by rememberUpdatedState(progress)
    val currentVolume by rememberUpdatedState(volume)
    var announcedKey by remember(route) { mutableStateOf("") }
    var lastStepIndex by remember(route) { mutableStateOf(-1) }

    fun speak(text: String, flush: Boolean = false) {
        if (!voiceOn || !ttsReady || text.isBlank()) return
        val params = android.os.Bundle().apply {
            putFloat(android.speech.tts.TextToSpeech.Engine.KEY_PARAM_VOLUME, currentVolume)
        }
        tts?.speak(
            text,
            if (flush) android.speech.tts.TextToSpeech.QUEUE_FLUSH
            else android.speech.tts.TextToSpeech.QUEUE_ADD,
            params,
            "toughmind-nav",
        )
    }

    // 开始导航时先播报全程，再根据位置逐步播报路口。
    LaunchedEffect(ttsReady, tts, target.lat, target.lon) {
        if (!ttsReady) return@LaunchedEffect
        val total = route?.distanceMeters ?: fallbackDistance.toInt()
        speak(
            if (english) {
                "Starting navigation. ${formatRouteDistance(total.toDouble(), true)} total, " +
                    "about ${formatRouteDuration(remainingSeconds, true)}."
            } else {
                "开始导航，全程 ${formatRouteDistance(total.toDouble())}，" +
                    "预计 ${formatRouteDuration(remainingSeconds)}。"
            },
            flush = true,
        )
    }

    LaunchedEffect(
        progress?.stepIndex,
        progress?.distanceToManeuverMeters?.toInt(),
        voiceOn,
        ttsReady,
    ) {
        val p = currentProgress ?: return@LaunchedEffect
        if (!voiceOn || !ttsReady) return@LaunchedEffect
        if (p.stepIndex != lastStepIndex) {
            if (p.stepIndex > 0) {
                val next = nextInstruction ?: p.instruction
                speak(
                    if (english) "Next, ${localizeInstruction(next, true)}"
                    else "接下来，$next",
                )
            }
            lastStepIndex = p.stepIndex
        }
        val threshold = guidanceThresholds(mode).lastOrNull {
            p.distanceToManeuverMeters <= it
        } ?: 0
        if (threshold > 0) {
            val key = "${p.stepIndex}:$threshold"
            if (key != announcedKey) {
                announcedKey = key
                speak(
                    if (english) {
                        "In $threshold m, about ${formatRouteEta(secondsToManeuver, true)}, " +
                            localizeInstruction(instruction, true)
                    } else {
                        "前方 $threshold 米，约 ${formatRouteEta(secondsToManeuver)}，$instruction"
                    },
                )
            }
        }
        if (p.remainingMeters < 25.0) {
            val key = "arrive"
            if (key != announcedKey) {
                announcedKey = key
                speak(
                    if (english) "You're near ${target.name}. Navigation ended."
                    else "已到达 ${target.name} 附近，导航结束。",
                )
            }
        }
    }
    BackHandler { onEnd() }

    Box(modifier = Modifier.fillMaxSize()) {
        Surface(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .statusBarsPadding()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            shape = RoundedCornerShape(20.dp),
            color = MaterialTheme.colorScheme.primary,
            shadowElevation = 10.dp,
        ) {
            Column(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Icon(
                        Icons.Filled.Navigation,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onPrimary,
                        modifier = Modifier.size(AppDimens.IconSize),
                    )
                    Column(Modifier.weight(1f)) {
                        Text(
                            if (english) {
                                "Navigation · ${navModeLabel(mode, true)} · ${if (voiceOn) "Voice on" else "Muted"}"
                            } else {
                                "导航模式 · $modeLabel · ${if (voiceOn) "语音播报" else "已静音"}"
                            },
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f),
                        )
                        Text(
                            text = if (english) {
                                "In ${formatRouteDistance(distanceToManeuver, true)} · " +
                                    "about ${formatRouteEta(secondsToManeuver, true)}, " +
                                    localizeInstruction(instruction, true)
                            } else {
                                "前方 ${formatRouteDistance(distanceToManeuver)} · 约 ${formatRouteEta(secondsToManeuver)}，$instruction"
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimary,
                            maxLines = 2,
                        )
                        Text(
                            if (english) {
                                "${formatRouteDistance(remainingMeters, true)} left · " +
                                    "about ${formatRouteDuration(remainingSeconds, true)}" +
                                    (upcomingInstruction?.let {
                                        " · Next: ${localizeInstruction(it, true)}"
                                    } ?: "")
                            } else {
                                "剩余 ${formatRouteDistance(remainingMeters)} · 约 ${formatRouteDuration(remainingSeconds)}" +
                                    (upcomingInstruction?.let { " · 下一步：$it" } ?: "")
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.9f),
                            maxLines = 2,
                        )
                    }
                    IconButton(
                        onClick = {
                            if (voiceOn) {
                                lastVolume = volume.coerceAtLeast(0.25f)
                                applyVolume(0f)
                            } else {
                                applyVolume(lastVolume.coerceAtLeast(0.25f))
                            }
                        },
                    ) {
                        Icon(
                            imageVector = if (voiceOn) Icons.Filled.VolumeUp else Icons.Filled.VolumeOff,
                            contentDescription = if (voiceOn) "静音" else "取消静音",
                            tint = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier.size(AppDimens.IconSize),
                        )
                    }
                    IconButton(onClick = onEnd) {
                        Icon(
                            Icons.Filled.Close,
                            contentDescription = "退出导航",
                            tint = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier.size(AppDimens.IconSize),
                        )
                    }
                }
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Slider(
                        value = volume,
                        onValueChange = { applyVolume(it) },
                        modifier = Modifier.weight(1f),
                    )
                    TextButton(onClick = {
                        val p = currentProgress
                        val text = if (p != null) {
                            if (english) {
                                "In ${formatRouteDistance(p.distanceToManeuverMeters, true)}, " +
                                    "about ${formatRouteEta(secondsToManeuver, true)}, " +
                                    localizeInstruction(instruction, true)
                            } else {
                                "前方 ${formatRouteDistance(p.distanceToManeuverMeters)}，约 ${formatRouteEta(secondsToManeuver)}，$instruction"
                            }
                        } else {
                            if (english) {
                                "Heading to ${target.name}, " +
                                    "${formatRouteDistance(fallbackDistance, true)} away."
                            } else {
                                "前往${target.name}，距离${formatRouteDistance(fallbackDistance)}，向${GeoMath.directionLabel(bearing)}"
                            }
                        }
                        speak(text, flush = true)
                    }) {
                        Text("播报", color = MaterialTheme.colorScheme.onPrimary)
                    }
                }
            }
        }

        Surface(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .navigationBarsPadding()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            shape = RoundedCornerShape(22.dp),
            color = MaterialTheme.colorScheme.surface,
            shadowElevation = 12.dp,
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    partnerEtaLine(partner, target, mode),
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Button(
                    onClick = onEnd,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(AppDimens.ButtonHeight),
                    shape = AppDimens.ButtonShape,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                ) {
                    Text("结束导航")
                }
                TextButton(
                    onClick = {
                        // 交给百度地图后必须停掉念安 TTS，避免两个语音引擎抢音频而卡在开头
                        voiceOn = false
                        tts?.stop()
                        if (NavigationHelper.open(context, target.lat, target.lon, target.name, mode)) {
                            onEnd()
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("用百度地图导航（会关闭念安语音）")
                }
            }
        }
    }
}

@Composable
private fun ConnectionBadge(state: ConnectionState) {
    val (color, label) = when (state) {
        ConnectionState.CONNECTED -> LevelNormal to "设备已连接"
        ConnectionState.CONNECTING -> LevelMild to "连接中"
        ConnectionState.DISCONNECTED -> MaterialTheme.colorScheme.onSurfaceVariant to "未连接"
    }
    Surface(
        shape = RoundedCornerShape(50),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
        shadowElevation = 4.dp,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Box(
                Modifier
                    .size(8.dp)
                    .background(color, CircleShape)
            )
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = color,
                fontWeight = FontWeight.Medium,
            )
        }
    }
}

@Composable
internal fun FloatingChatBar(
    partner: PersonPresence?,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    Surface(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(26.dp),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.97f),
        shadowElevation = 10.dp,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Icon(Icons.Filled.Mic, contentDescription = "语音留言", tint = TextSecondary)
            Text(
                text = "说点什么…",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                modifier = Modifier.weight(1f),
                maxLines = 1,
            )
            Icon(Icons.Filled.EmojiEmotions, contentDescription = "表情", tint = TextSecondary)
            Icon(Icons.Filled.Add, contentDescription = "更多", tint = TextSecondary)
        }
    }
}

@Composable
private fun BottomStatusPill(
    partner: PersonPresence,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    var dragAmount by remember { mutableFloatStateOf(0f) }
    Surface(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .pointerInput(Unit) {
                detectVerticalDragGestures(
                    onDragEnd = {
                        if (dragAmount < -24f) onClick()
                        dragAmount = 0f
                    },
                    onVerticalDrag = { change, amount ->
                        change.consume()
                        dragAmount += amount
                    },
                )
            },
        shape = RoundedCornerShape(topStart = 18.dp, topEnd = 18.dp),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
        shadowElevation = 10.dp,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 16.dp, end = 16.dp, top = 10.dp, bottom = 2.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                Modifier
                    .width(36.dp)
                    .height(4.dp)
                    .clip(RoundedCornerShape(50))
                    .background(MaterialTheme.colorScheme.onSurface.copy(alpha = 0.35f)),
            )
        }
    }
}

@Composable
internal fun LocationPermissionHint(
    modifier: Modifier = Modifier,
    permissionGranted: Boolean,
    onRequest: () -> Unit,
) {
    Surface(
        modifier = modifier.padding(24.dp),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
        shadowElevation = 12.dp,
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = if (permissionGranted) "正在获取你的位置" else "需要定位权限",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
            Text(
                text = if (permissionGranted) {
                    "定位还在路上。稍等片刻，或点击下方按钮重新获取。"
                } else {
                    "允许定位后，地图才会显示你和 TA 的位置、距离与天气"
                },
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
            )
            Spacer(Modifier.height(4.dp))
            TechButton(
                text = if (permissionGranted) "重新获取位置" else "开启定位",
                onClick = onRequest,
            )
        }
    }
}

@Composable
internal fun MoodBubble(
    emoji: String,
    message: String,
    isSelf: Boolean,
    onEdit: () -> Unit,
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = emoji.ifBlank { "🙂" },
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.clickable(onClick = onEdit),
            )
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = if (isSelf) "我的状态" else "TA 的状态",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSecondaryContainer,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = message.ifBlank { "还没有状态，点右侧说一句吧" },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.82f),
                )
            }
            if (isSelf) {
                TextButton(onClick = onEdit) { Text("换一个") }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeMeetup.kt`

> 约见地点搜索、双方距离与地点卡片。

````kotlin
package com.shineleong.toughmind.ui.screen.home

import android.Manifest
import android.media.AudioManager
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.width
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Slider
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.component.LocalTtsRate
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.CareStatusBadge
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.NavigationModeDialog
import com.shineleong.toughmind.ui.screen.chat.ChatSheet
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Add
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.WeatherPill
import com.shineleong.toughmind.ui.component.formatDistance
import com.shineleong.toughmind.util.BaiduPlaceSearch
import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRoutePlanner
import com.shineleong.toughmind.util.planBaiduRoute
import com.shineleong.toughmind.util.PlaceSuggestion
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import com.shineleong.toughmind.util.NavigationHelper
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.iconLabel
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.map.CareMap
import com.shineleong.toughmind.ui.map.MapPerson
import com.shineleong.toughmind.ui.map.MapPlace
import com.shineleong.toughmind.ui.map.MapPlaceKind
import com.shineleong.toughmind.ui.map.MapStyle
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.NavyPrimary
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlin.math.roundToInt
import kotlinx.coroutines.delay

@Composable
internal fun MeetupSearchDialog(
    selfLat: Double,
    selfLon: Double,
    onDismiss: () -> Unit,
    onPick: (Double, Double, String) -> Unit,
) {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<PlaceSuggestion>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    var city by remember { mutableStateOf("附近") }
    var showCityDialog by remember { mutableStateOf(false) }
    val search = remember {
        BaiduPlaceSearch(
            onResult = { list ->
                results = list
                error = if (list.isEmpty()) "没有找到相关地点" else null
            },
            onError = { error = it },
        )
    }
    DisposableEffect(Unit) { onDispose { search.destroy() } }
    LaunchedEffect(query, city) {
        kotlinx.coroutines.delay(300)
        if (query.isBlank()) {
            results = emptyList()
            error = null
        } else if (city == "附近" && selfLat != 0.0 && selfLon != 0.0) {
            search.searchNearby(query, selfLat, selfLon)
        } else {
            search.searchCity(query, if (city == "附近") "全国" else city)
        }
    }

    if (showCityDialog) {
        var cityDraft by remember { mutableStateOf(if (city == "附近") "" else city) }
        AlertDialog(
            onDismissRequest = { showCityDialog = false },
            title = { Text("搜索范围") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        "默认优先搜索当前位置附近 10 公里。也可以切换城市或全国。",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                    OutlinedTextField(
                        value = cityDraft,
                        onValueChange = { cityDraft = it },
                        singleLine = true,
                        label = { Text("城市，例如：杭州") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    city = cityDraft.trim().ifBlank { "附近" }
                    showCityDialog = false
                }) { Text("确定") }
            },
            dismissButton = {
                Row {
                    TextButton(onClick = { city = "附近"; showCityDialog = false }) { Text("附近") }
                    TextButton(onClick = { city = "全国"; showCityDialog = false }) { Text("全国") }
                }
            },
        )
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
                        .padding(start = 4.dp, end = 14.dp, top = 6.dp, bottom = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                    Surface(
                        shape = RoundedCornerShape(26.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant,
                        modifier = Modifier
                            .weight(1f)
                            .height(48.dp),
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 14.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                Icons.Filled.Search,
                                contentDescription = null,
                                tint = Color(0xFF3385FF),
                            )
                            BasicTextField(
                                value = query,
                                onValueChange = { query = it },
                                singleLine = true,
                                textStyle = MaterialTheme.typography.bodyLarge.copy(
                                    color = MaterialTheme.colorScheme.onSurface,
                                ),
                                modifier = Modifier
                                    .weight(1f)
                                    .padding(horizontal = 10.dp),
                                decorationBox = { inner ->
                                    if (query.isBlank()) {
                                        Text(
                                            "搜索地点",
                                            style = MaterialTheme.typography.bodyLarge,
                                            color = TextSecondary,
                                        )
                                    }
                                    inner()
                                },
                            )
                            Text(
                                city,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.primary,
                                modifier = Modifier
                                    .clickable { showCityDialog = true }
                                    .padding(start = 6.dp, top = 8.dp, bottom = 8.dp),
                            )
                        }
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState()),
                ) {
                    if (query.isBlank()) {
                        Text(
                            "输入地点名称，结果会像百度地图一样即时出现",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                            modifier = Modifier.padding(20.dp),
                        )
                    }
                    error?.let {
                        Text(
                            it,
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary,
                            modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp),
                        )
                    }
                    results.forEach { item ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onPick(item.lat, item.lon, item.name.ifBlank { query })
                                }
                                .padding(horizontal = 20.dp, vertical = 14.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                Icons.Filled.LocationOn,
                                contentDescription = null,
                                tint = Color(0xFF3385FF),
                            )
                            Spacer(Modifier.width(12.dp))
                            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(item.name, style = MaterialTheme.typography.bodyLarge, color = TextPrimary)
                                if (item.address.isNotBlank()) {
                                    Text(
                                        item.address,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = TextSecondary,
                                    )
                                }
                            }
                        }
                        HorizontalDivider(
                            modifier = Modifier.padding(start = 52.dp),
                            color = MaterialTheme.colorScheme.outline.copy(alpha = 0.25f),
                        )
                    }
                }
            }
        }
    }
}

@Composable
internal fun MeetupCard(
    destination: Pair<Double, Double>,
    name: String?,
    self: PersonPresence?,
    partner: PersonPresence?,
    onSearch: () -> Unit,
    onNavigate: () -> Unit,
    onClear: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val selfDistance = self?.let {
        GeoMath.distanceMeters(it.lat, it.lon, destination.first, destination.second)
    }
    val partnerDistance = partner?.let {
        GeoMath.distanceMeters(it.lat, it.lon, destination.first, destination.second)
    }
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.96f),
        shadowElevation = 8.dp,
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(name ?: "双人会合", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(
                        if (name != null) {
                            "百度地图 · ${"%.5f".format(destination.first)}, ${"%.5f".format(destination.second)}"
                        } else {
                            "地图中心 · ${"%.5f".format(destination.first)}, ${"%.5f".format(destination.second)}"
                        },
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                    )
                }
                IconButton(onClick = onClear) {
                    Icon(Icons.Filled.Close, contentDescription = "关闭会合点")
                }
            }
            MeetupPersonRow(name = "我", distance = selfDistance)
            MeetupPersonRow(name = partner?.name ?: "TA", distance = partnerDistance)
            Text(
                "预计时间按直线距离估算：步行 5km/h，驾车 30km/h。",
                style = MaterialTheme.typography.labelSmall,
                color = TextSecondary,
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End,
            ) {
                TextButton(onClick = onSearch) { Text("搜索地点") }
                TextButton(onClick = onNavigate) { Text("导航到会合点") }
            }
        }
    }
}

@Composable
private fun MeetupPersonRow(name: String, distance: Double?) {
    val walkMinutes = distance?.let { ((it / 1000.0) / 5.0 * 60).toInt().coerceAtLeast(1) }
    val driveMinutes = distance?.let { ((it / 1000.0) / 30.0 * 60).toInt().coerceAtLeast(1) }
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
        Text(
            text = if (distance == null) {
                "位置未知"
            } else {
                "${formatDistance(distance)} · 步行约 ${walkMinutes} 分钟 · 驾车约 ${driveMinutes} 分钟"
            },
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary,
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeNavigationSheet.kt`

> 导航目的地选择、路线摘要、开始导航与 ETA 文案。

````kotlin
package com.shineleong.toughmind.ui.screen.home

import android.Manifest
import android.media.AudioManager
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.width
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Slider
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.component.LocalTtsRate
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.CareStatusBadge
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.NavigationModeDialog
import com.shineleong.toughmind.ui.screen.chat.ChatSheet
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Add
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.WeatherPill
import com.shineleong.toughmind.ui.component.formatDistance
import com.shineleong.toughmind.util.BaiduPlaceSearch
import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRoutePlanner
import com.shineleong.toughmind.util.planBaiduRoute
import com.shineleong.toughmind.util.PlaceSuggestion
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import com.shineleong.toughmind.util.NavigationHelper
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.iconLabel
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.map.CareMap
import com.shineleong.toughmind.ui.map.MapPerson
import com.shineleong.toughmind.ui.map.MapPlace
import com.shineleong.toughmind.ui.map.MapPlaceKind
import com.shineleong.toughmind.ui.map.MapStyle
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.NavyPrimary
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlin.math.roundToInt
import kotlinx.coroutines.delay

internal data class NavTarget(val lat: Double, val lon: Double, val name: String)

internal data class NavigationSession(
    val target: NavTarget,
    val mode: NavMode,
    val route: BaiduRoute,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun NavigationSheet(
    target: NavTarget,
    self: PersonPresence?,
    partner: PersonPresence?,
    onDismiss: () -> Unit,
    onStart: (NavMode, BaiduRoute) -> Unit,
) {
    var mode by remember { mutableStateOf(NavMode.DRIVING) }
    var route by remember { mutableStateOf<BaiduRoute?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var planning by remember { mutableStateOf(false) }
    var retryToken by remember { mutableIntStateOf(0) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)

    LaunchedEffect(mode, target, self, retryToken) {
        route = null
        error = null
        if (self == null) {
            error = "还没有获取到当前位置，暂时无法规划路线"
            planning = false
            return@LaunchedEffect
        }
        planning = true
        // 优先百度；百度路线接口不可用时，用 OSRM 获取沿道路的真实几何与分段动作。
        val planned = runCatching {
            kotlinx.coroutines.withTimeout(3_000L) {
                planBaiduRoute(
                    mode = mode,
                    fromLat = self.lat,
                    fromLon = self.lon,
                    toLat = target.lat,
                    toLon = target.lon,
                )
            }
        }.getOrElse {
            runCatching {
                com.shineleong.toughmind.util.OsrmRouteClient.route(
                    mode = mode,
                    fromLat = self.lat,
                    fromLon = self.lon,
                    toLat = target.lat,
                    toLon = target.lon,
                )
            }.getOrNull()
        }
        if (planned != null && planned.points.size >= 2) {
            route = planned
        } else {
            error = "路线规划失败，请检查网络后重试"
        }
        planning = false
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = MaterialTheme.colorScheme.surface,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(
                        "导航",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(target.name, style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                }
                Icon(
                    Icons.Filled.Navigation,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(AppDimens.IconSize),
                )
            }

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(
                    NavMode.DRIVING to "驾车",
                    NavMode.WALKING to "步行",
                    NavMode.TRANSIT to "公交",
                    NavMode.EBIKE to "骑行",
                ).forEach { (value, label) ->
                    FilterChip(
                        selected = mode == value,
                        onClick = { mode = value },
                        label = { Text(label) },
                    )
                }
            }

            val current = route
            when {
                planning -> Text(
                    "正在沿道路规划路线…",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                error != null -> {
                    Text(
                        error!!,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                    TextButton(
                        onClick = { retryToken += 1 },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("重新规划")
                    }
                }
                current != null -> {
                    Text(
                        "全程 %.1f 公里".format(current.distanceMeters / 1000.0),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        "预计 ${(current.durationSeconds / 60).coerceAtLeast(1)} 分钟 · ${current.steps.size} 段道路",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
            }
            Button(
                onClick = { route?.let { onStart(mode, it) } },
                enabled = route != null && !planning,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(AppDimens.ButtonHeight),
                shape = AppDimens.ButtonShape,
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
            ) {
                Text(if (planning) "正在规划路线…" else "开始导航")
            }
        }
    }
}

internal fun partnerEtaLine(partner: PersonPresence?, target: NavTarget, mode: NavMode): String {
    if (partner == null) return "TA 还未上线，暂时没有对方的导航时间"
    val distance = GeoMath.distanceMeters(partner.lat, partner.lon, target.lat, target.lon)
    val speed = when (mode) {
        NavMode.WALKING -> 5.0
        NavMode.EBIKE -> 18.0
        NavMode.TRANSIT -> 20.0
        NavMode.DRIVING -> 30.0
    }
    val minutes = ((distance / 1000.0) / speed * 60).toInt().coerceAtLeast(1)
    return "TA 预计 $minutes 分钟后到达 · %.1f 公里".format(distance / 1000.0)
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomePersonSheet.kt`

> 人物详情抽屉、心情弹窗与驾驶安全卡。

````kotlin
package com.shineleong.toughmind.ui.screen.home

import android.Manifest
import android.media.AudioManager
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.width
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Slider
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.component.LocalTtsRate
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.CareStatusBadge
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.NavigationModeDialog
import com.shineleong.toughmind.ui.screen.chat.ChatSheet
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Add
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.WeatherPill
import com.shineleong.toughmind.ui.component.formatDistance
import com.shineleong.toughmind.util.BaiduPlaceSearch
import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRoutePlanner
import com.shineleong.toughmind.util.planBaiduRoute
import com.shineleong.toughmind.util.PlaceSuggestion
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import com.shineleong.toughmind.util.NavigationHelper
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.iconLabel
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.map.CareMap
import com.shineleong.toughmind.ui.map.MapPerson
import com.shineleong.toughmind.ui.map.MapPlace
import com.shineleong.toughmind.ui.map.MapPlaceKind
import com.shineleong.toughmind.ui.map.MapStyle
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.NavyPrimary
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlin.math.roundToInt
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PersonDetailSheet(
    person: PersonPresence,
    weather: WeatherInfo?,
    isSelf: Boolean,
    onDismiss: () -> Unit,
    onNudge: () -> Unit,
    onSetMood: (String, String) -> Unit,
    onNavigate: (() -> Unit)? = null,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var showMoodDialog by remember { mutableStateOf(false) }
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
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Avatar(
                    nickname = person.name,
                    size = 62.dp,
                    imageBitmap = null,
                    statusEmoji = person.status.emoji,
                    statusColor = person.status.toColor(),
                    moodEmoji = person.moodEmoji,
                    online = person.online,
                    badgeText = null,
                    onMoodClick = if (isSelf) ({ showMoodDialog = true }) else null,
                )
                Column(Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = person.name,
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary,
                        )
                        Spacer(Modifier.width(8.dp))
                        if (person.isDemo) {
                            Surface(
                                shape = RoundedCornerShape(50),
                                color = Gold.copy(alpha = 0.18f),
                            ) {
                                Text(
                                    text = "演示",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                )
                            }
                        }
                    }
                    Text(
                        text = if (isSelf) "我的手机" else "${person.relation} · ${person.deviceType.label}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary,
                    )
                }
                CareStatusBadge(status = person.status)
            }

            if (person.activityNote.isNotBlank()) {
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = person.status.toColor().copy(alpha = 0.10f),
                ) {
                    Text(
                        text = person.activityNote,
                        style = MaterialTheme.typography.bodyMedium,
                        color = person.status.toColor(),
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 9.dp),
                    )
                }
            }

            MoodBubble(
                emoji = person.moodEmoji,
                message = person.moodMessage,
                isSelf = isSelf,
                onEdit = { showMoodDialog = true },
            )

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(1.dp)
                    .background(MaterialTheme.colorScheme.outline.copy(alpha = 0.45f)),
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                InfoLine(
                    label = "设备",
                    value = person.deviceType.iconLabel(),
                    modifier = Modifier.weight(1f),
                )
                Spacer(Modifier.width(16.dp))
                InfoLine(
                    label = "电量",
                    value = if (person.battery in 0..100) "${person.battery}%" else "未知",
                    modifier = Modifier.weight(1f),
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                InfoLine(
                    label = "最近更新",
                    value = formatRelativeTime(person.lastSeen),
                    modifier = Modifier.weight(1f),
                )
                Spacer(Modifier.width(16.dp))
                InfoLine(
                    label = if (isSelf) "状态" else "相距",
                    value = if (isSelf) {
                        person.status.label
                    } else {
                        formatDistance(person.distanceMeters) +
                            if (person.directionLabel.isNotBlank()) " · ${person.directionLabel}" else ""
                    },
                    modifier = Modifier.weight(1f),
                )
            }

            WeatherInfoCard(
                title = if (isSelf) "我这里的天气" else "${person.name}那里的天气",
                weather = weather,
                modifier = Modifier.fillMaxWidth(),
            )

            person.driverState?.let { driver ->
                DriverSafetyCard(driver = driver)
            }

            Spacer(Modifier.height(2.dp))
            if (isSelf) {
                OutlinedButton(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("知道了")
                }
            } else {
                if (onNavigate != null) {
                    OutlinedButton(
                        onClick = onNavigate,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Icon(
                            Icons.Filled.Navigation,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(Modifier.width(6.dp))
                        Text("导航到 TA")
                    }
                }
                TechButton(
                    text = "轻轻提醒 TA",
                    onClick = onNudge,
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    text = "通过设备下行主题发送一条不带打扰的关心提醒",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }

    if (showMoodDialog) {
        MoodDialog(
            initialEmoji = person.moodEmoji,
            initialMessage = person.moodMessage,
            onDismiss = { showMoodDialog = false },
            onSave = onSetMood,
        )
    }
}

@Composable
private fun MoodDialog(
    initialEmoji: String,
    initialMessage: String,
    onDismiss: () -> Unit,
    onSave: (String, String) -> Unit,
) {
    val emojis = listOf(
        "😊", "😄", "🥰", "😌", "😴", "😪", "🥳", "😕",
        "😢", "😤", "🤒", "🌧️", "🌙", "☀️", "❤️", "🍀", "✨", "🐾",
    )
    var emoji by remember(initialEmoji) { mutableStateOf(initialEmoji.ifBlank { "😊" }) }
    var message by remember(initialMessage) { mutableStateOf(initialMessage) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("设置状态") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = "头像右下角会显示这个 emoji，TA 点开你的头像就能看到留言。",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                )
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    emojis.forEach { item ->
                        Surface(
                            onClick = { emoji = item },
                            shape = RoundedCornerShape(12.dp),
                            color = if (emoji == item) {
                                MaterialTheme.colorScheme.primaryContainer
                            } else {
                                MaterialTheme.colorScheme.surfaceVariant
                            },
                            border = if (emoji == item) {
                                BorderStroke(1.5.dp, MaterialTheme.colorScheme.primary)
                            } else {
                                null
                            },
                        ) {
                            Text(
                                text = item,
                                style = MaterialTheme.typography.headlineSmall,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            )
                        }
                    }
                }
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it },
                    label = { Text("要说点什么") },
                    maxLines = 3,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    onSave(emoji, message.trim())
                    onDismiss()
                },
            ) { Text("保存") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("取消") }
        },
    )
}

@Composable
private fun DriverSafetyCard(driver: DriverState) {
    val color = driver.fatigueLevel.toColor()
    TechCard(
        modifier = Modifier.fillMaxWidth(),
        accent = color.copy(alpha = 0.45f),
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                text = "驾驶安全 · 设备正在关注",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
            Text(
                text = "疲劳等级：${driver.fatigueLevel.label}",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold,
                color = color,
            )
            val metrics = listOf(
                "疲劳分数" to "%.1f".format(driver.fatigueScore),
                "PERCLOS" to "%.2f".format(driver.perclos),
                "哈欠次数" to "${driver.yawnTotal}",
                "分心状态" to if (driver.headDistracted) "分心" else "正常",
                "车内温度" to "${driver.temperature.toInt()} ℃",
                "车速" to "${driver.speedKmh.toInt()} km/h",
            )
            metrics.chunked(2).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    row.forEach { (label, value) ->
                        Column(Modifier.weight(1f)) {
                            Text(label, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            Text(
                                value,
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = NavyPrimary,
                            )
                        }
                    }
                    if (row.size == 1) Spacer(Modifier.weight(1f))
                }
            }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeScreen.kt`

> 首页装配：地图、浮层与状态/回调的唯一持有者。

````kotlin
package com.shineleong.toughmind.ui.screen.home

import android.Manifest
import android.media.AudioManager
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.width
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Slider
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import com.shineleong.toughmind.ui.component.Text
import com.shineleong.toughmind.ui.i18n.LocalAppLanguage
import com.shineleong.toughmind.ui.component.LocalTtsRate
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.ui.AppViewModelProvider
import com.shineleong.toughmind.ui.component.Avatar
import com.shineleong.toughmind.ui.component.CareStatusBadge
import com.shineleong.toughmind.ui.component.InfoLine
import com.shineleong.toughmind.ui.component.NavigationModeDialog
import com.shineleong.toughmind.ui.screen.chat.ChatSheet
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.EmojiEmotions
import androidx.compose.material.icons.filled.Add
import com.shineleong.toughmind.ui.component.TechButton
import com.shineleong.toughmind.ui.component.TechCard
import com.shineleong.toughmind.ui.component.WeatherInfoCard
import com.shineleong.toughmind.ui.component.WeatherPill
import com.shineleong.toughmind.ui.component.formatDistance
import com.shineleong.toughmind.util.BaiduPlaceSearch
import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRoutePlanner
import com.shineleong.toughmind.util.planBaiduRoute
import com.shineleong.toughmind.util.PlaceSuggestion
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import com.shineleong.toughmind.util.NavigationHelper
import com.shineleong.toughmind.ui.component.formatRelativeTime
import com.shineleong.toughmind.ui.component.iconLabel
import com.shineleong.toughmind.ui.component.toColor
import com.shineleong.toughmind.ui.map.CareMap
import com.shineleong.toughmind.ui.map.MapPerson
import com.shineleong.toughmind.ui.map.MapPlace
import com.shineleong.toughmind.ui.map.MapPlaceKind
import com.shineleong.toughmind.ui.map.MapStyle
import com.shineleong.toughmind.ui.theme.Gold
import com.shineleong.toughmind.ui.theme.AppDimens
import com.shineleong.toughmind.ui.theme.LevelMild
import com.shineleong.toughmind.ui.theme.LevelNormal
import com.shineleong.toughmind.ui.theme.NavyPrimary
import com.shineleong.toughmind.ui.theme.SurfaceWhite
import com.shineleong.toughmind.ui.theme.TextPrimary
import com.shineleong.toughmind.ui.theme.TextSecondary
import kotlin.math.roundToInt
import kotlinx.coroutines.delay

/**
 * 地图主页：地图铺满整页，双方头像标记悬浮其上。
 * 点击头像 → 底部抽屉展开该成员的状态、设备、电量、天气、驾驶安全等信息。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onOpenDrawer: () -> Unit,
    focusPersonId: String?,
    onFocusConsumed: () -> Unit,
    onNavigationActiveChange: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier,
    viewModel: HomeViewModel = viewModel(factory = AppViewModelProvider.Factory),
) {
    val self by viewModel.selfPresence.collectAsStateWithLifecycle()
    val partner by viewModel.partnerPresence.collectAsStateWithLifecycle()
    val trail by viewModel.trail.collectAsStateWithLifecycle()
    val meetupPoint by viewModel.meetupPoint.collectAsStateWithLifecycle()
    val showPartnerOnMap by viewModel.showPartnerOnMap.collectAsStateWithLifecycle()
    val meetupName by viewModel.meetupName.collectAsStateWithLifecycle()
    var showMeetupSearch by remember { mutableStateOf(false) }
    var showChat by remember { mutableStateOf(false) }
    var showPlaceSearch by remember { mutableStateOf(false) }
    var routeTarget by remember { mutableStateOf<NavTarget?>(null) }
    var mapStyle by rememberSaveable { mutableStateOf(MapStyle.NORMAL) }
    var navigationSession by remember { mutableStateOf<NavigationSession?>(null) }
    val connectionState by viewModel.connectionState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    var permissionGranted by remember { mutableStateOf(viewModel.hasLocationPermission()) }
    val statusBarHeight = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions(),
    ) { grants ->
        if (grants.values.any { it }) {
            permissionGranted = true
            viewModel.startLocationUpdates()
        }
    }

    LaunchedEffect(Unit) {
        if (viewModel.hasLocationPermission()) {
            permissionGranted = true
            viewModel.startLocationUpdates()
        } else {
            permissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                ),
            )
        }
    }

    // 地图只做“以谁为中心”，不再弹出成员资料卡。
    var cameraFocusId by remember { mutableStateOf<String?>(null) }
    var cameraFocusToken by remember { mutableIntStateOf(0) }
    val focusPerson: (String) -> Unit = { id ->
        cameraFocusId = id
        cameraFocusToken += 1
    }

    LaunchedEffect(focusPersonId) {
        if (!focusPersonId.isNullOrBlank()) {
            cameraFocusId = focusPersonId
            cameraFocusToken += 1
            onFocusConsumed()
        }
    }

    LaunchedEffect(navigationSession) {
        onNavigationActiveChange(navigationSession != null)
    }
    DisposableEffect(Unit) {
        onDispose { onNavigationActiveChange(false) }
    }

    val selfAvatar = remember(self?.avatarPath) {
        val path = self?.avatarPath.orEmpty()
        if (path.isBlank()) null
        else runCatching { BitmapFactory.decodeFile(path)?.asImageBitmap() }.getOrNull()
    }

    val selfBubble = rememberTransientBubble(self?.moodMessage)
    val partnerBubble = rememberTransientBubble(partner?.moodMessage)

    val people = remember(self, partner, selfAvatar, showPartnerOnMap, selfBubble, partnerBubble) {
        buildList {
            self?.let { add(it.toMapPerson(selfAvatar, selfBubble)) }
            if (showPartnerOnMap) partner?.let { add(it.toMapPerson(null, partnerBubble)) }
        }
    }

    // GPS 针形只用于地点：会合点、地图选点与导航目的地
    val places = remember(meetupPoint, meetupName, routeTarget, navigationSession) {
        val meetup = meetupPoint
        fun sameAsMeetup(lat: Double, lon: Double): Boolean =
            meetup != null && GeoMath.distanceMeters(lat, lon, meetup.first, meetup.second) < 8.0
        buildList {
            meetup?.let { point ->
                add(
                    MapPlace(
                        id = "meetup",
                        lat = point.first,
                        lon = point.second,
                        name = meetupName ?: "会合点",
                        kind = MapPlaceKind.MEETUP,
                    ),
                )
            }
            routeTarget?.takeIf { !sameAsMeetup(it.lat, it.lon) }?.let { target ->
                add(
                    MapPlace(
                        id = "route_target",
                        lat = target.lat,
                        lon = target.lon,
                        name = target.name,
                        kind = MapPlaceKind.DESTINATION,
                    ),
                )
            }
            navigationSession?.target?.takeIf { !sameAsMeetup(it.lat, it.lon) }?.let { target ->
                add(
                    MapPlace(
                        id = "navigation_target",
                        lat = target.lat,
                        lon = target.lon,
                        name = target.name,
                        kind = MapPlaceKind.DESTINATION,
                    ),
                )
            }
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        CareMap(
            people = people,
            modifier = Modifier.fillMaxSize(),
            places = places,
            trail = trail,
            route = navigationSession?.route?.points.orEmpty(),
            mapStyle = mapStyle,
            focusPersonId = cameraFocusId,
            focusToken = cameraFocusToken,
            onPersonClick = { id -> focusPerson(id) },
            onPickMeetup = { _, _ -> showMeetupSearch = true },
            onSearchPlace = { showPlaceSearch = true },
            onMapClick = { lat, lon -> routeTarget = NavTarget(lat, lon, "地图选点") },
            onPoiClick = { lat, lon, name ->
                routeTarget = NavTarget(lat, lon, name.ifBlank { "地图地点" })
            },
        )

        Box(
            Modifier
                .fillMaxWidth()
                .height(statusBarHeight)
                .background(SurfaceWhite)
                .align(Alignment.TopCenter),
        )

        MapTopOverlay(
            self = self,
            partner = partner,
            connectionState = connectionState,
            avatar = selfAvatar,
            focusPersonId = cameraFocusId,
            onOpenDrawer = onOpenDrawer,
            onSelect = focusPerson,
            mapStyle = mapStyle,
            onMapStyleChange = { mapStyle = it },
            is3dSupported = com.shineleong.toughmind.ui.map.MapConfig.USE_BAIDU,
        )

        self?.heading?.let { heading ->
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(start = 16.dp, bottom = 92.dp),
                shape = RoundedCornerShape(18.dp),
                color = MaterialTheme.colorScheme.surface.copy(alpha = 0.94f),
                shadowElevation = 3.dp,
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Icon(
                        Icons.Filled.Navigation,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp).rotate(heading),
                        tint = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        "朝向 ${GeoMath.directionLabel(heading.toDouble())}",
                        style = MaterialTheme.typography.labelMedium,
                    )
                }
            }
        }

        if (navigationSession == null) {
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 10.dp),
            ) {
                FloatingChatBar(
                    partner = partner,
                    modifier = Modifier.fillMaxWidth(),
                    onClick = { showChat = true },
                )
            }
        }

        meetupPoint?.let { point ->
            MeetupCard(
                destination = point,
                name = meetupName,
                self = self,
                partner = partner,
                onSearch = { showMeetupSearch = true },
                onNavigate = {
                    routeTarget = NavTarget(point.first, point.second, meetupName ?: "会合点")
                },
                onClear = { viewModel.clearMeetupPoint() },
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(start = 16.dp, end = 16.dp, bottom = 88.dp),
            )
        }

        if (showMeetupSearch) {
            MeetupSearchDialog(
                selfLat = self?.lat ?: 0.0,
                selfLon = self?.lon ?: 0.0,
                onDismiss = { showMeetupSearch = false },
                onPick = { lat, lon, name ->
                    viewModel.setMeetupPoint(lat, lon, name)
                    showMeetupSearch = false
                },
            )
        }

        if (showPlaceSearch) {
            MeetupSearchDialog(
                selfLat = self?.lat ?: 0.0,
                selfLon = self?.lon ?: 0.0,
                onDismiss = { showPlaceSearch = false },
                onPick = { lat, lon, name ->
                    routeTarget = NavTarget(lat, lon, name)
                    showPlaceSearch = false
                },
            )
        }

        routeTarget?.let { target ->
            NavigationSheet(
                target = target,
                self = self,
                partner = partner,
                onDismiss = { routeTarget = null },
                onStart = { mode, route ->
                    navigationSession = NavigationSession(target, mode, route)
                    routeTarget = null
                },
            )
        }

        if (self == null) {
            LocationPermissionHint(
                modifier = Modifier.align(Alignment.Center),
                permissionGranted = permissionGranted,
                onRequest = {
                    if (permissionGranted) {
                        viewModel.startLocationUpdates()
                    } else {
                        permissionLauncher.launch(
                            arrayOf(
                                Manifest.permission.ACCESS_FINE_LOCATION,
                                Manifest.permission.ACCESS_COARSE_LOCATION,
                            ),
                        )
                    }
                },
            )
        }
    }

    navigationSession?.let { session ->
        NavigationActiveOverlay(
            target = session.target,
            self = self,
            partner = partner,
            mode = session.mode,
            route = session.route,
            onEnd = { navigationSession = null },
        )
    }

    if (showChat) {
        ChatSheet(onDismiss = { showChat = false })
    }
}

private fun PersonPresence.toMapPerson(avatar: ImageBitmap?, bubbleText: String?): MapPerson = MapPerson(
    id = id,
    name = name,
    initials = name.trim().take(1).ifBlank { "?" },
    avatar = avatar,
    lat = lat,
    lon = lon,
    isSelf = id == CareRepository.SELF_ID,
    statusColor = status.toColor(),
    online = online,
    statusEmoji = status.emoji,
    moodEmoji = moodEmoji,
    bubbleText = bubbleText,
    heading = heading,
)

/** 地图气泡只短暂出现：留言出现或变化时展示 8 秒，然后自动收起。 */
@Composable
private fun rememberTransientBubble(message: String?): String? {
    val text = message.orEmpty()
    var visible by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(text) {
        if (text.isBlank()) {
            visible = null
            return@LaunchedEffect
        }
        visible = text
        delay(8_000L)
        visible = null
    }
    return visible
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/HomeViewModel.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.DeviceInfo
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.remote.MqttTopics
import com.shineleong.toughmind.data.repository.CareRepository
import com.shineleong.toughmind.data.repository.CareSyncRepository
import com.shineleong.toughmind.data.repository.DeviceRepository
import com.shineleong.toughmind.data.repository.LocationRepository
import com.shineleong.toughmind.data.repository.MqttRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/** 地图主页：双方位置、状态、天气与"提醒 TA"动作。 */
class HomeViewModel(
    private val careRepository: CareRepository,
    private val careSyncRepository: CareSyncRepository,
    private val mqttRepository: MqttRepository,
    deviceRepository: DeviceRepository,
    private val preferences: Preferences,
    private val locationRepository: LocationRepository,
) : ViewModel() {

    val selfPresence: StateFlow<PersonPresence?> = careRepository.selfPresence
    val partnerPresence: StateFlow<PersonPresence?> = careRepository.partnerPresence
    val selfWeather = careRepository.selfWeather
    val partnerWeather = careRepository.partnerWeather
    val showPartnerOnMap: StateFlow<Boolean> = preferences.showPartnerOnMap.stateIn(
        viewModelScope, SharingStarted.WhileSubscribed(5_000), true
    )
    val companion: StateFlow<CarePartner> = careRepository.companion
    val connectionState: StateFlow<ConnectionState> = mqttRepository.connectionState
    val groupActive: StateFlow<Boolean> = careSyncRepository.groupActive
    /** 今天的自定位轨迹，地图上画成一条淡色路线。 */
    val trail = locationRepository.trail

    val currentDevice: StateFlow<DeviceInfo?> = combine(
        deviceRepository.devices,
        preferences.currentDeviceId,
    ) { devices, currentId ->
        devices.firstOrNull { it.deviceId == currentId } ?: devices.firstOrNull()
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    fun hasLocationPermission(): Boolean = locationRepository.hasPermission()

    fun startLocationUpdates() = locationRepository.start()

    fun stopLocationUpdates() = locationRepository.stop()

    /** 通过云端关心组给 TA 发一条关心；ESP32 设备同时走 MQTT 下行主题。 */
    fun sendNudge(targetName: String) {
        val safeName = targetName.replace("\"", "").trim()
        val payload = "{\"type\":\"care_nudge\",\"to\":\"$safeName\",\"ts\":${System.currentTimeMillis()}}"
        mqttRepository.publishDownlink(payload)
        viewModelScope.launch {
            careSyncRepository.sendNudge("在想你，记得照顾好自己。")
        }
    }

    fun setMood(emoji: String, message: String) {
        viewModelScope.launch { preferences.setMood(emoji, message) }
    }

    private val _meetupPoint = MutableStateFlow<Pair<Double, Double>?>(null)
    val meetupPoint: StateFlow<Pair<Double, Double>?> = _meetupPoint
    private val _meetupName = MutableStateFlow<String?>(null)
    val meetupName: StateFlow<String?> = _meetupName

    fun setMeetupPoint(lat: Double, lon: Double, name: String? = null) {
        _meetupPoint.value = lat to lon
        _meetupName.value = name
    }

    fun clearMeetupPoint() {
        _meetupPoint.value = null
        _meetupName.value = null
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/ui/screen/home/RouteGuidance.kt`

````kotlin
package com.shineleong.toughmind.ui.screen.home

import com.shineleong.toughmind.util.BaiduRoute
import com.shineleong.toughmind.util.BaiduRouteStep
import com.shineleong.toughmind.util.GeoMath
import com.shineleong.toughmind.util.NavMode
import kotlin.math.roundToInt

/** 当前应播报的路线进度：在第几步、离下一个转向还有多远、还剩多少路。 */
data class RouteProgress(
    val stepIndex: Int,
    val step: BaiduRouteStep,
    val nextStep: BaiduRouteStep?,
    val distanceToManeuverMeters: Double,
    val remainingMeters: Double,
    val remainingSeconds: Int,
) {
    val instruction: String
        get() = step.instruction.ifBlank { "沿当前道路继续前行" }

    val nextInstruction: String?
        get() = nextStep?.instruction?.takeIf { it.isNotBlank() }
}

/**
 * 用当前位置匹配路线最近点，得到当前步骤和到下一个路口的距离。
 * 不依赖 GPS 朝向，原地也能稳定判断；接近步骤末尾时自动切到下一步。
 */
fun BaiduRoute.progressAt(
    lat: Double,
    lon: Double,
    stepIndexHint: Int = 0,
): RouteProgress? {
    if (steps.isEmpty() || lat == 0.0 && lon == 0.0) return null

    data class Annotated(val stepIndex: Int, val point: com.baidu.mapapi.model.LatLng)

    val annotated = steps.flatMapIndexed { index, step ->
        step.points.map { Annotated(index, it) }
    }
    if (annotated.isEmpty()) return null

    val nearest = annotated.minByOrNull {
        GeoMath.distanceMeters(lat, lon, it.point.latitude, it.point.longitude)
    } ?: return null

    var index = nearest.stepIndex.coerceAtLeast(stepIndexHint.coerceIn(0, steps.lastIndex))
    var step = steps[index]
    var maneuver = step.points.lastOrNull()
    var distanceToManeuver = maneuver?.let {
        GeoMath.distanceMeters(lat, lon, it.latitude, it.longitude)
    } ?: 0.0

    // 已经走过当前步骤的终点时，直接切到下一步，避免一直播报“前方 0 米”。
    if (distanceToManeuver < 18.0 && index < steps.lastIndex) {
        index += 1
        step = steps[index]
        maneuver = step.points.lastOrNull()
        distanceToManeuver = maneuver?.let {
            GeoMath.distanceMeters(lat, lon, it.latitude, it.longitude)
        } ?: 0.0
    }

    val nearestRoutePointIndex = points.indices.minByOrNull { pointIndex ->
        val point = points[pointIndex]
        GeoMath.distanceMeters(lat, lon, point.latitude, point.longitude)
    } ?: 0
    var remaining = 0.0
    for (i in nearestRoutePointIndex until points.lastIndex) {
        val a = points[i]
        val b = points[i + 1]
        remaining += GeoMath.distanceMeters(a.latitude, a.longitude, b.latitude, b.longitude)
    }
    if (maneuver != null && index == steps.lastIndex) {
        remaining = maxOf(remaining, distanceToManeuver)
    }
    val ratio = if (distanceMeters > 0) {
        (remaining / distanceMeters).coerceIn(0.0, 1.0)
    } else {
        1.0
    }
    val seconds = (durationSeconds * ratio).roundToInt().coerceAtLeast(0)

    return RouteProgress(
        stepIndex = index,
        step = step,
        nextStep = steps.getOrNull(index + 1),
        distanceToManeuverMeters = distanceToManeuver.coerceAtLeast(0.0),
        remainingMeters = remaining.coerceAtLeast(0.0),
        remainingSeconds = seconds,
    )
}

fun formatRouteDistance(meters: Double, english: Boolean = false): String =
    if (meters >= 1_000) {
        if (english) "%.1f km".format(meters / 1_000.0) else "%.1f 公里".format(meters / 1_000.0)
    } else {
        val value = meters.roundToInt().coerceAtLeast(0)
        if (english) "$value m" else "$value 米"
    }

fun formatRouteDuration(seconds: Int, english: Boolean = false): String {
    val minutes = (seconds / 60).coerceAtLeast(1)
    return if (minutes >= 60) {
        if (english) "${minutes / 60} h ${minutes % 60} min" else "${minutes / 60} 小时 ${minutes % 60} 分钟"
    } else {
        if (english) "$minutes min" else "$minutes 分钟"
    }
}

/** 到下一个路口 / 转向点的短 ETA。 */
fun formatRouteEta(seconds: Int, english: Boolean = false): String = if (seconds < 60) {
    val value = seconds.coerceAtLeast(5)
    if (english) "$value s" else "$value 秒"
} else {
    val value = (seconds / 60).coerceAtLeast(1)
    if (english) "$value min" else "$value 分钟"
}

fun navModeLabel(mode: NavMode, english: Boolean): String {
    if (!english) return mode.label
    return when (mode) {
        NavMode.DRIVING -> "Driving"
        NavMode.WALKING -> "Walking"
        NavMode.TRANSIT -> "Transit"
        NavMode.EBIKE -> "Cycling"
    }
}

/** 把百度 / OSRM 的中文转向说明转成英文；路名保留原文。 */
fun localizeInstruction(text: String, english: Boolean): String {
    if (!english || text.isBlank()) return text
    var result = text
    if (result == "沿当前道路继续前行") return "Continue on the current road"
    if (result.startsWith("沿当前道路前往 ")) {
        return "Continue on the current road to " + result.removePrefix("沿当前道路前往 ")
    }
    result = result
        .replace("到达目的地", "Arrive at destination")
        .replace("右前方", "bear right")
        .replace("左前方", "bear left")
        .replace("右转", "Turn right")
        .replace("左转", "Turn left")
        .replace("掉头", "Make a U-turn")
        .replace("直行", "Go straight")
        .replace("靠右", "Keep right")
        .replace("靠左", "Keep left")
        .replace("进入", "onto ")
        .replace("沿", "Along ")
        .replace("行驶", "continue")
        .replace("公里", "km")
        .replace("米", "m")
        .replace("，", ", ")
        .replace("。", ". ")
        .replace("；", "; ")
    return result.trim()
}

/** 不同出行方式的播报距离阈值，从远到近。 */
fun guidanceThresholds(mode: NavMode): List<Int> = when (mode) {
    NavMode.DRIVING -> listOf(500, 200, 60)
    NavMode.EBIKE -> listOf(300, 100, 40)
    NavMode.WALKING -> listOf(100, 30)
    NavMode.TRANSIT -> listOf(300, 80)
}
````

---

返回索引：[README.md](02-实战库/项目/安卓应用开发/README.md)
