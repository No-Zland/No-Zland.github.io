# 09 · 客户端测试与工程脚本

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

单元测试覆盖几何计算、天气映射、关心提示解析、小智本地大脑与宠物习性；辅助脚本负责资源生成与本文档生成。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 单元测试与仪器测试](#s09-1) | JVM 单测直接 `./gradlew :app:testDebugUnitTest` 运行；仪器测试需要真机或模拟器。 | 8 |
| [2. 工程脚本](#s09-2) | `generate_assets.py` 生成图标与默认头像；`gen_devdoc.py` 生成本套开发文档并校验覆盖率。 | 2 |

本篇共 **2 个步骤 / 10 个文件**，按表格顺序写入即可还原对应代码。

<a id="s09-1"></a>

## 步骤 09.1 · 单元测试与仪器测试

JVM 单测直接 `./gradlew :app:testDebugUnitTest` 运行；仪器测试需要真机或模拟器。

本步骤涉及的文件：

- `app/src/test/java/com/shineleong/toughmind/data/model/CareTipLibraryTest.kt`
- `app/src/test/java/com/shineleong/toughmind/data/model/OwlHabitsTest.kt`
- `app/src/test/java/com/shineleong/toughmind/data/remote/CareTipParserTest.kt`
- `app/src/test/java/com/shineleong/toughmind/data/remote/WeatherMappingTest.kt`
- `app/src/test/java/com/shineleong/toughmind/data/remote/XiaozhiLocalBrainTest.kt`
- `app/src/test/java/com/shineleong/toughmind/ExampleUnitTest.kt`
- `app/src/test/java/com/shineleong/toughmind/util/GeoMathTest.kt`
- `app/src/androidTest/java/com/shineleong/toughmind/ExampleInstrumentedTest.kt`

### `app/src/test/java/com/shineleong/toughmind/data/model/CareTipLibraryTest.kt`

````kotlin
package com.shineleong.toughmind.data.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate

class CareTipLibraryTest {

    @Test
    fun `couple mode returns four distinct angles`() {
        val tips = CareTipLibrary.suggestions(
            scene = "TA 当前状态：学习中；关系模式：情侣；",
            coupleMode = true,
            seed = 1_000L,
        )

        assertEquals(4, tips.size)
        assertEquals(AdviceKind.LOVE, tips.last().kind)
        assertEquals(4, tips.map { it.content }.toSet().size)
    }

    @Test
    fun `family mode never returns love line`() {
        val tips = CareTipLibrary.suggestions(
            scene = "TA 当前状态：驾驶中；关系模式：家人；",
            coupleMode = false,
            seed = 2_000L,
        )

        assertEquals(3, tips.size)
        assertFalse(tips.any { it.kind == AdviceKind.LOVE })
    }

    @Test
    fun `different seeds rotate wording`() {
        val first = CareTipLibrary.suggestions("TA 当前状态：学习中；", true, seed = 0L)
        val second = CareTipLibrary.suggestions("TA 当前状态：学习中；", true, seed = 1_000L)

        assertTrue(first.map { it.content } != second.map { it.content })
    }

    @Test
    fun `urgent context skips sweet talk even in couple mode`() {
        val tips = CareTipLibrary.suggestions(
            scene = "医学异常；关系模式：情侣；",
            coupleMode = true,
            seed = 3L,
        )

        assertEquals(3, tips.size)
        assertFalse(tips.any { it.kind == AdviceKind.LOVE })
    }

    @Test
    fun `duplicate angles from model are replaced by missing ones`() {
        val remote = listOf(
            CareTip(AdviceKind.ACTION, "给 TA 打个电话。"),
            CareTip(AdviceKind.ACTION, "再给 TA 发条消息。"),
            CareTip(AdviceKind.WORDS, "说一句我在。"),
            CareTip(AdviceKind.SURPRISE, "点一份热饮。"),
        )

        val completed = CareTipLibrary.complete(
            tips = remote,
            scene = "关系模式：情侣；TA 当前状态：学习中；",
            coupleMode = true,
            seed = 5L,
        )

        assertEquals(4, completed.size)
        assertTrue(completed.any { it.kind == AdviceKind.LOVE })
        assertEquals(4, completed.map { it.kind }.toSet().size)
    }
}

class RomanceCatalogTest {

    @Test
    fun `catalog has one hundred unique ideas`() {
        assertEquals(100, RomanceCatalog.ideas.size)
        assertEquals(100, RomanceCatalog.ideas.map { it.id }.toSet().size)
        assertTrue(RomanceCatalog.ideas.all { it.title.isNotBlank() })
    }

    @Test
    fun `every category has ideas and filtering works`() {
        RomanceCategory.entries.forEach { category ->
            assertTrue(RomanceCatalog.byCategory(category).isNotEmpty())
        }
        assertEquals(RomanceCatalog.ideas.size, RomanceCatalog.byCategory(null).size)
    }

    @Test
    fun `daily love line is stable and belongs to catalog`() {
        val date = LocalDate.of(2026, 10, 19)
        val line = RomanceCatalog.dailyLoveLine(date)

        assertEquals(line, RomanceCatalog.dailyLoveLine(date))
        assertTrue(RomanceCatalog.loveLines.contains(line))
        assertTrue(RomanceCatalog.anotherLoveLine(line) in RomanceCatalog.loveLines)
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/data/model/OwlHabitsTest.kt`

````kotlin
package com.shineleong.toughmind.data.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDateTime
import java.time.ZoneId

class OwlHabitsTest {

    private val zone: ZoneId = ZoneId.of("Asia/Shanghai")

    private fun at(
        day: Int = 19,
        hour: Int,
        minute: Int = 0,
    ): Long = LocalDateTime.of(2026, 10, day, hour, minute)
        .atZone(zone)
        .toInstant()
        .toEpochMilli()

    @Test
    fun `pet names are trimmed, collapsed and capped`() {
        assertEquals("小 灰", OwlHabits.normalizeName("  小   灰  "))
        assertEquals("", OwlHabits.normalizeName("   "))
        assertEquals(
            OwlHabits.MAX_NAME_LENGTH,
            OwlHabits.normalizeName("很".repeat(30)).length,
        )
    }

    @Test
    fun `species defaults to brown and parses snowy`() {
        assertEquals(OwlSpecies.BROWN, OwlSpecies.fromStorage(null))
        assertEquals(OwlSpecies.BROWN, OwlSpecies.fromStorage("cat"))
        assertEquals(OwlSpecies.SNOWY, OwlSpecies.fromStorage("snowy"))
        assertEquals(OwlSpecies.SNOWY, OwlSpecies.fromStorage("SNOWY"))
    }

    @Test
    fun `new pet species parse from storage and are not owls`() {
        assertEquals(OwlSpecies.INK_CAT, OwlSpecies.fromStorage("ink_cat"))
        assertEquals(OwlSpecies.RURAL_DOG, OwlSpecies.fromStorage("rural_dog"))
        assertEquals(OwlSpecies.HAMSTER, OwlSpecies.fromStorage("hamster"))
        assertTrue(OwlSpecies.HAMSTER.label.isNotBlank())
        assertFalse(OwlSpecies.INK_CAT.isOwl)
        assertFalse(OwlSpecies.RURAL_DOG.isOwl)
        assertTrue(OwlSpecies.BROWN.isOwl)
    }

    @Test
    fun `feed adds satiety and starts digestion`() {
        val now = at(hour = 20)
        val result = OwlHabits.feed(PetState(updatedAt = now), "我", now, zone)

        assertTrue(result.accepted)
        assertEquals(PetResultCode.FED, result.code)
        assertEquals(84, result.state.satiety)
        assertEquals(1, result.state.feedCountToday)
        assertEquals(now, result.state.lastFedAt)
        assertEquals("我", result.state.lastFedBy)
        assertEquals(OwlHabits.FEED_COOLDOWN_MS, OwlHabits.feedCooldownRemaining(result.state, now))
    }

    @Test
    fun `cannot feed again while digesting`() {
        val now = at(hour = 20)
        val fed = OwlHabits.feed(PetState(updatedAt = now), "我", now, zone)
        val again = OwlHabits.feed(fed.state, "我", now + 30_000L, zone)

        assertFalse(again.accepted)
        assertEquals(PetResultCode.REFUSED_COOLDOWN, again.code)
        assertEquals(90, again.secondsRemaining)
        assertTrue(again.state.satiety <= fed.state.satiety)
    }

    @Test
    fun `feeding a full owl is refused instead of overfeeding`() {
        val now = at(hour = 20)
        val full = PetState(satiety = 95, updatedAt = now)
        val result = OwlHabits.feed(full, "我", now, zone)

        assertFalse(result.accepted)
        assertEquals(PetResultCode.REFUSED_FULL, result.code)
        assertEquals(95, result.state.satiety)
    }

    @Test
    fun `a very full meal marks the owl as overfed`() {
        val now = at(hour = 20)
        val almostFull = PetState(satiety = 90, mood = 70, updatedAt = now)
        val result = OwlHabits.feed(almostFull, "我", now, zone)

        assertTrue(result.accepted)
        assertEquals(PetResultCode.FED_OVER, result.code)
        assertTrue(result.state.overfed)
        assertEquals(100, result.state.satiety)
        assertTrue(result.state.mood < almostFull.mood)
    }

    @Test
    fun `daily meal limit is enforced`() {
        val now = at(hour = 20)
        val state = PetState(
            satiety = 40,
            feedCountToday = OwlHabits.DAILY_FEED_LIMIT,
            feedDay = "2026-10-19",
            updatedAt = now,
        )
        val result = OwlHabits.feed(state, "我", now, zone)

        assertFalse(result.accepted)
        assertEquals(PetResultCode.REFUSED_DAILY_LIMIT, result.code)
    }

    @Test
    fun `sleeping owl refuses food but can be woken by a pet`() {
        val now = at(hour = 3)
        val sleeping = PetState(energy = 8, asleep = true, updatedAt = now)

        val feed = OwlHabits.feed(sleeping, "我", now, zone)
        assertFalse(feed.accepted)
        assertEquals(PetResultCode.REFUSED_SLEEPING, feed.code)

        val pet = OwlHabits.pet(sleeping, now, zone)
        assertTrue(pet.accepted)
        assertEquals(PetResultCode.WOKEN, pet.code)
        assertFalse(pet.state.asleep)
        assertTrue(pet.state.energy >= 30)
    }

    @Test
    fun `petting builds bond but repeated pokes annoy`() {
        val now = at(hour = 20)
        val first = OwlHabits.pet(PetState(updatedAt = now, mood = 50), now, zone)
        assertEquals(PetResultCode.PETTED, first.code)
        assertTrue(first.state.bond > 10)
        assertTrue(first.state.mood > 50)

        val spam = OwlHabits.pet(first.state, now + 800L, zone)
        assertFalse(spam.accepted)
        assertEquals(PetResultCode.PET_ANNOYED, spam.code)
        assertTrue(spam.state.mood < first.state.mood)
    }

    @Test
    fun `low energy makes the owl fall asleep over time`() {
        val start = at(hour = 10)
        val state = PetState(energy = 20, satiety = 80, updatedAt = start)
        val later = OwlHabits.advance(state, start + 3 * 3_600_000L, zone)

        assertTrue(later.asleep)
        assertTrue(later.energy <= OwlHabits.SLEEP_ENERGY)
        assertTrue(later.satiety < state.satiety)
    }

    @Test
    fun `daily meal counter resets on a new day`() {
        val start = at(day = 18, hour = 22)
        val state = PetState(
            feedCountToday = 6,
            feedDay = "2026-10-18",
            updatedAt = start,
        )
        val nextDay = OwlHabits.advance(state, at(day = 19, hour = 9), zone)

        assertEquals(0, nextDay.feedCountToday)
        assertEquals("2026-10-19", nextDay.feedDay)
    }

    @Test
    fun `owl rhythm follows real local time`() {
        assertEquals(OwlRhythm.DUSK, OwlHabits.rhythmAt(at(hour = 7), zone))
        assertEquals(OwlRhythm.DAY_REST, OwlHabits.rhythmAt(at(hour = 12), zone))
        assertEquals(OwlRhythm.DUSK, OwlHabits.rhythmAt(at(hour = 19), zone))
        assertEquals(OwlRhythm.NIGHT, OwlHabits.rhythmAt(at(hour = 23), zone))
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/data/remote/CareTipParserTest.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.data.model.AdviceKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CareTipParserTest {

    @Test
    fun `parses json array from model`() {
        val raw = """
            [
              {"kind":"action","text":"给 TA 点一杯热饮，备注忙完再喝。"},
              {"kind":"words","content":"发一句“忙完告诉我”，不催 TA。"},
              {"kind":"love","text":"你先去忙，我把想你排进今天的日程。"}
            ]
        """.trimIndent()

        val tips = CareTipParser.parse(raw)

        assertEquals(3, tips.size)
        assertEquals(AdviceKind.ACTION, tips[0].kind)
        assertEquals(AdviceKind.WORDS, tips[1].kind)
        assertEquals(AdviceKind.LOVE, tips[2].kind)
        assertTrue(tips[1].content.contains("忙完告诉我"))
    }

    @Test
    fun `parses numbered chinese labels`() {
        val raw = """
            1. [马上做] 给 TA 发一个十分钟的休息计时。
            2. 【说句话】先问 TA 想被安慰还是想听建议。
            3. [小惊喜] 点一份 TA 爱吃的小食送到楼下。
            4. [情话] 累了就往我这边靠一会儿。
        """.trimIndent()

        val tips = CareTipParser.parse(raw)

        assertEquals(4, tips.size)
        assertEquals(AdviceKind.ACTION, tips[0].kind)
        assertEquals(AdviceKind.WORDS, tips[1].kind)
        assertEquals(AdviceKind.SURPRISE, tips[2].kind)
        assertEquals(AdviceKind.LOVE, tips[3].kind)
        assertEquals("点一份 TA 爱吃的小食送到楼下。", tips[2].content)
    }

    @Test
    fun `strips markdown fences and bullets`() {
        val raw = """
            ```json
            - {"kind":"action","text":"先打电话确认 TA 是否安全。"}
            ```
        """.trimIndent()

        // 单条 JSON 对象不是数组，走行解析；至少不应把代码围栏当成建议。
        val tips = CareTipParser.parse(raw)
        assertTrue(tips.isEmpty() || tips.none { it.content.contains("```") })
    }

    @Test
    fun `completes partial answer to four angles in couple mode`() {
        val completed = CareTipParser.parseAndComplete(
            raw = "1. [马上做] 给 TA 发一个十分钟的休息计时。",
            scene = "TA 当前状态：学习中；关系模式：情侣；",
            coupleMode = true,
        )

        assertEquals(4, completed.size)
        assertTrue(completed.any { it.kind == AdviceKind.LOVE })
        assertTrue(completed.any { it.kind == AdviceKind.WORDS })
        assertTrue(completed.any { it.kind == AdviceKind.SURPRISE })
    }

    @Test
    fun `family mode completes to three angles without love`() {
        val completed = CareTipParser.parseAndComplete(
            raw = "",
            scene = "TA 当前状态：驾驶中；关系模式：家人；",
            coupleMode = false,
        )

        assertEquals(3, completed.size)
        assertTrue(completed.none { it.kind == AdviceKind.LOVE })
        assertTrue(completed.map { it.content }.toSet().size == 3)
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/data/remote/WeatherMappingTest.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import org.junit.Assert.assertEquals
import org.junit.Test

class WeatherMappingTest {

    @Test
    fun clearAndCloudyCodesHaveChineseLabels() {
        assertEquals("晴", weatherDescription(0, isDay = true).first)
        assertEquals("晴夜", weatherDescription(0, isDay = false).first)
        assertEquals("多云", weatherDescription(2, isDay = true).first)
        assertEquals("阴", weatherDescription(3, isDay = true).first)
    }

    @Test
    fun rainAndStormCodesMapToWeatherEmoji() {
        assertEquals("小雨", weatherDescription(61, isDay = true).first)
        assertEquals("雷阵雨", weatherDescription(95, isDay = true).first)
        assertEquals("⛈️", weatherDescription(95, isDay = true).second)
        assertEquals("未知", weatherDescription(999, isDay = true).first)
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/data/remote/XiaozhiLocalBrainTest.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.data.model.XiaozhiContext
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class XiaozhiLocalBrainTest {

    private val context = XiaozhiContext(
        userName = "念",
        partnerName = "安",
        partnerStatus = "驾驶中",
        partnerNote = "在回公司路上",
        partnerOnline = true,
        partnerHasLocation = true,
        partnerDistanceMeters = 3_200.0,
        partnerDirection = "东北",
        weatherLabel = "多云",
        weatherTemperature = 23.5,
        weatherEmoji = "⛅",
        hour = 15,
        minute = 20,
        dateText = "10月23日 周四",
    )

    @Test
    fun greetingMentionsXiaozhi() {
        val reply = XiaozhiLocalBrain.reply("你好", context, seed = 1)
        assertTrue(reply, reply.contains("小智"))
        assertTrue(reply, reply.contains("念"))
    }

    @Test
    fun tiredReplySuggestsRest() {
        val reply = XiaozhiLocalBrain.reply("我有点累", context, seed = 7)
        assertTrue(reply, reply.contains("休息") || reply.contains("歇"))
    }

    @Test
    fun weatherReplyUsesTemperatureAndLabel() {
        val reply = XiaozhiLocalBrain.reply("今天天气怎么样", context, seed = 3)
        assertTrue(reply, reply.contains("23.5"))
        assertTrue(reply, reply.contains("多云"))
    }

    @Test
    fun weatherReplyDoesNotInventDataWhenMissing() {
        val reply = XiaozhiLocalBrain.reply(
            "今天多少度",
            context.copy(weatherTemperature = null, weatherLabel = ""),
            seed = 4,
        )
        assertTrue(reply, reply.contains("还没拿到"))
        assertFalse(reply, reply.contains("23.5"))
    }

    @Test
    fun partnerQuestionUsesDistanceAndStatus() {
        val reply = XiaozhiLocalBrain.reply("TA 现在在哪？", context, seed = 5)
        assertTrue(reply, reply.contains("安"))
        assertTrue(reply, reply.contains("3.2 公里"))
        assertTrue(reply, reply.contains("东北"))
        assertTrue(reply, reply.contains("驾驶中"))
    }

    @Test
    fun partnerQuestionWithoutLocationIsHonest() {
        val reply = XiaozhiLocalBrain.reply(
            "TA 到哪了",
            context.copy(partnerHasLocation = false, partnerDistanceMeters = null),
            seed = 6,
        )
        assertTrue(reply, reply.contains("还没看到"))
    }

    @Test
    fun timeReplyContainsClock() {
        val reply = XiaozhiLocalBrain.reply("现在几点了", context.copy(hour = 21, minute = 7), seed = 8)
        assertTrue(reply, reply.contains("21:07"))
        assertTrue(reply, reply.contains("晚上"))
    }

    @Test
    fun capabilityMentionsAppEntries() {
        val reply = XiaozhiLocalBrain.reply("你能做什么", context, seed = 9)
        assertTrue(reply, reply.contains("行程") && reply.contains("地图"))
    }

    @Test
    fun unknownInputStillGetsAReply() {
        val reply = XiaozhiLocalBrain.reply("量子纠缠和我的周一有什么关系", context, seed = 10)
        assertTrue(reply.isNotBlank())
        assertTrue(reply.length <= 200)
    }

    @Test
    fun emptyInputGetsGentlePrompt() {
        val reply = XiaozhiLocalBrain.reply("   ", context, seed = 11)
        assertTrue(reply.isNotBlank())
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/ExampleUnitTest.kt`

````kotlin
package com.shineleong.toughmind

import org.junit.Test

import org.junit.Assert.*

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }
}
````

### `app/src/test/java/com/shineleong/toughmind/util/GeoMathTest.kt`

````kotlin
package com.shineleong.toughmind.util

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class GeoMathTest {

    @Test
    fun distanceBetweenTwoKnownPointsIsReasonable() {
        // 杭州西湖附近两点，直线距离约 1.4km
        val distance = GeoMath.distanceMeters(30.2741, 120.1551, 30.2860, 120.1640)
        assertTrue("distance=$distance", distance in 1_200.0..1_800.0)
    }

    @Test
    fun samePointHasZeroDistance() {
        assertEquals(0.0, GeoMath.distanceMeters(30.0, 120.0, 30.0, 120.0), 0.0001)
    }

    @Test
    fun directionLabelsCoverEightDirections() {
        assertEquals("北", GeoMath.directionLabel(0.0))
        assertEquals("东北", GeoMath.directionLabel(45.0))
        assertEquals("东", GeoMath.directionLabel(90.0))
        assertEquals("东南", GeoMath.directionLabel(135.0))
        assertEquals("南", GeoMath.directionLabel(180.0))
        assertEquals("西南", GeoMath.directionLabel(225.0))
        assertEquals("西", GeoMath.directionLabel(270.0))
        assertEquals("西北", GeoMath.directionLabel(315.0))
    }

    @Test
    fun relationDirectionPointsFromMeToPartner() {
        // 我在原点，TA 在东侧 → 方位应接近 90 度
        val relation = GeoMath.relation(30.0, 120.0, 30.0, 120.1)
        assertEquals(90.0, relation.bearingDegrees.toDouble(), 1.0)
        assertEquals("东", relation.directionLabel)
    }

    @Test
    fun normalizeHeadingWrapsAndTreatsUnknownAsZero() {
        assertEquals(10f, GeoMath.normalizeHeading(370f), 0.001f)
        assertEquals(180f, GeoMath.normalizeHeading(180f), 0.001f)
        assertEquals(0f, GeoMath.normalizeHeading(0f), 0.001f)
        assertEquals(0f, GeoMath.normalizeHeading(-1f), 0.001f)
        assertEquals(0f, GeoMath.normalizeHeading(Float.NaN), 0.001f)
        // 360° 与 0° 同为北方，不能画成“北北西”
        assertEquals(0f, GeoMath.normalizeHeading(359.8f), 0.001f)
    }

    @Test
    fun smoothHeadingCrossesNorthWithoutLongWayAround() {
        // 359° → 1° 只应前进 2°，而不是倒转 358°
        val smoothed = GeoMath.smoothHeading(359f, 1f, alpha = 0.5f)
        assertTrue("smoothed=$smoothed", smoothed <= 1f || smoothed >= 359f)
        assertEquals(0f, smoothed, 1f)

        // 90° → 180°，半程应接近 135°
        assertEquals(135f, GeoMath.smoothHeading(90f, 180f, alpha = 0.5f), 0.5f)
    }

    @Test
    fun smoothHeadingKeepsLastKnownWhenDirectionMissing() {
        assertEquals(120f, GeoMath.smoothHeading(120f, 0f), 0.001f)
        assertEquals(90f, GeoMath.smoothHeading(0f, 90f), 0.001f)
    }

    @Test
    fun compassNormalizationKeepsNorthValid() {
        assertEquals(0f, GeoMath.normalizeCompass(0f), 0.001f)
        assertEquals(350f, GeoMath.normalizeCompass(-10f), 0.001f)
        assertEquals(10f, GeoMath.normalizeCompass(370f), 0.001f)
        assertEquals(359.9f, GeoMath.normalizeCompass(359.9f), 0.05f)
    }

    @Test
    fun nullableHeadingSmoothingHandlesMissingAndNorth() {
        assertNull(GeoMath.smoothHeadingOrNull(null, null))
        assertEquals(30f, GeoMath.smoothHeadingOrNull(null, 30f)!!, 0.001f)
        assertEquals(120f, GeoMath.smoothHeadingOrNull(120f, null)!!, 0.001f)

        // 359° → 1° 走 2°，不会绕 358° 回到北
        val crossed = GeoMath.smoothHeadingOrNull(359f, 1f, alpha = 0.5f)!!
        assertTrue("crossed=$crossed", crossed <= 1f || crossed >= 359f)
    }
}
````

### `app/src/androidTest/java/com/shineleong/toughmind/ExampleInstrumentedTest.kt`

````kotlin
package com.shineleong.toughmind

import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.ext.junit.runners.AndroidJUnit4

import org.junit.Test
import org.junit.runner.RunWith

import org.junit.Assert.*

/**
 * Instrumented test, which will execute on an Android device.
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
@RunWith(AndroidJUnit4::class)
class ExampleInstrumentedTest {
    @Test
    fun useAppContext() {
        // Context of the app under test.
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("com.shineleong.toughmind", appContext.packageName)
    }
}
````

<a id="s09-2"></a>

## 步骤 09.2 · 工程脚本

`generate_assets.py` 生成图标与默认头像；`gen_devdoc.py` 生成本套开发文档并校验覆盖率。

本步骤涉及的文件：

- `tools/gen_devdoc.py`
- `tools/generate_assets.py`

### `tools/gen_devdoc.py`

> 本套开发文档的生成器：逐文件写入代码并校验清单覆盖率。

````python
#!/usr/bin/env python3
"""按模块生成《念安 TOUCHMIND 开发文档》，把仓库源码逐文件写入 Markdown。

用法（在仓库根目录执行）::

    python tools/gen_devdoc.py            # 重新生成 docs/devdoc/*.md
    python tools/gen_devdoc.py --check    # 只校验：清单是否覆盖仓库全部源码

设计目标：
1. 文档中的代码块直接来自源文件，不做任何改写，因此"文档即代码"；
2. 每个代码块上方用仓库相对路径标记文件，照抄即可复现；
3. --check 用 include/exclude 规则计算仓库源码全集，与清单里实际引用的文件比对，
   多写、漏写、重复引用都会报错，保证"所有代码"都在文档里。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "tools" / "devdoc_manifest.json"

LANG_BY_SUFFIX = {
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".java": "java",
    ".py": "python",
    ".xml": "xml",
    ".sh": "bash",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".properties": "properties",
    ".keep": "text",
    ".md": "markdown",
}
LANG_BY_NAME = {
    "Dockerfile": "dockerfile",
    "gradlew": "bash",
    "gradlew.bat": "bat",
}


def posix(path: Path) -> str:
    return path.as_posix()


def glob_to_regex(pattern: str) -> re.Pattern:
    """把 gitignore 风格的 glob 转成正则；支持 ** 跨目录、* 单层、? 单字符。"""
    out: List[str] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            if pattern.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
                continue
            if pattern.startswith("**", i):
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
            i += 1
        elif ch == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(ch))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(rel: str, patterns: Iterable[re.Pattern]) -> bool:
    return any(p.match(rel) for p in patterns)


def discover_sources(manifest: dict) -> List[str]:
    """按 include / exclude 规则扫描仓库，返回应从属于文档的源码相对路径。"""
    include = [glob_to_regex(p) for p in manifest["include"]]
    exclude = [glob_to_regex(p) for p in manifest["exclude"]]
    skip_dirs = {".git", ".gradle", ".idea", ".kotlin", "build", ".venv", "__pycache__",
                 "node_modules", ".local", "docs", ".vscode"}

    found: List[str] = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            abs_path = Path(root) / name
            rel = posix(abs_path.relative_to(REPO_ROOT))
            if matches_any(rel, include) and not matches_any(rel, exclude):
                found.append(rel)
    return sorted(found)


def expand_dirs(dirs: Iterable[str], exclude: List[re.Pattern]) -> List[str]:
    """把 section 里的目录展开成该目录下的全部源码文件（递归、按路径排序）。"""
    out: List[str] = []
    for directory in dirs:
        base = REPO_ROOT / directory
        if not base.is_dir():
            raise SystemExit(f"清单中的目录不存在：{directory}")
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel = posix(path.relative_to(REPO_ROOT))
            if matches_any(rel, exclude):
                continue
            out.append(rel)
    return out


def section_files(section: dict, manifest: dict) -> List[str]:
    exclude = [glob_to_regex(p) for p in manifest["exclude"]]
    files = [rel.replace("\\", "/") for rel in section.get("files", [])]
    files.extend(expand_dirs(section.get("dirs", []), exclude))
    return files


def read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "\r\n" in text:
        text = text.replace("\r\n", "\n")
    return text


def language_for(rel: str) -> str:
    name = Path(rel).name
    if name in LANG_BY_NAME:
        return LANG_BY_NAME[name]
    return LANG_BY_SUFFIX.get(Path(rel).suffix.lower(), "text")


def clamp_intro(text: str) -> str:
    return text.strip("\n")


def render_module(module: dict, manifest: dict, module_count: int) -> str:
    module_id = module["id"]
    lines: List[str] = []
    add = lines.append

    add(f"# {module_id} · {module['title']}")
    add("")
    add("> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  ")
    add("> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。")
    add("")
    if module.get("intro"):
        add(clamp_intro(module["intro"]))
        add("")

    sections = module["sections"]
    section_lists = [section_files(s, manifest) for s in sections]
    total_files = sum(len(files) for files in section_lists)

    add("## 本篇复现顺序")
    add("")
    add("| 步骤 | 内容 | 文件数 |")
    add("|---|---|---|")
    for idx, section in enumerate(sections, start=1):
        anchor = f"s{module_id}-{idx}".replace(".", "-")
        add(f"| [{idx}. {section['title']}](#{anchor}) | {section.get('intro', '').strip().splitlines()[0] if section.get('intro') else ''} | {len(section_lists[idx - 1])} |")
    add("")
    add(f"本篇共 **{len(sections)} 个步骤 / {total_files} 个文件**，按表格顺序写入即可还原对应代码。")
    add("")

    for idx, section in enumerate(sections, start=1):
        anchor = f"s{module_id}-{idx}".replace(".", "-")
        add(f'<a id="{anchor}"></a>')
        add("")
        add(f"## 步骤 {module_id}.{idx} · {section['title']}")
        add("")
        if section.get("intro"):
            add(clamp_intro(section["intro"]))
            add("")
        if section_lists[idx - 1]:
            add("本步骤涉及的文件：")
            add("")
            for rel in section_lists[idx - 1]:
                add(f"- `{rel}`")
            add("")
        for rel in section_lists[idx - 1]:
            note = manifest.get("notes", {}).get(rel)
            add(f"### `{rel}`")
            add("")
            if note:
                add(f"> {note}")
                add("")
            lang = language_for(rel)
            body = read_text(REPO_ROOT / rel)
            if body and not body.endswith("\n"):
                body += "\n"
            fence = "````"
            add(f"{fence}{lang}")
            add(body.rstrip("\n"))
            add(fence)
            add("")

    add("---")
    add("")
    add("返回索引：[README.md](README.md)")
    add("")
    return "\n".join(lines)


def render_index(manifest: dict, stats: List[Tuple[dict, int, int]]) -> str:
    lines: List[str] = []
    add = lines.append
    add(f"# {manifest['title']}")
    add("")
    add(clamp_intro(manifest.get("intro", "")))
    add("")
    add("## 文档构成")
    add("")
    add("| 篇 | 主题 | 文件数 | 代码行数 |")
    add("|---|---|---|---|")
    total_files = 0
    total_lines = 0
    for module, file_count, line_count in stats:
        total_files += file_count
        total_lines += line_count
        add(f"| [{module['id']}]({module['slug']}.md) | {module['title']} | {file_count} | {line_count} |")
    add(f"| 合计 | — | **{total_files}** | **{total_lines}** |")
    add("")
    add("## 复现总览")
    add("")
    add(clamp_intro(manifest.get("reproduce", "")))
    add("")
    add("## 阅读与维护约定")
    add("")
    add(clamp_intro(manifest.get("conventions", "")))
    add("")
    add("## 校验")
    add("")
    add("```bash")
    add("python tools/gen_devdoc.py --check   # 校验清单是否覆盖仓库全部源码")
    add("python tools/gen_devdoc.py           # 重新生成全部篇目")
    add("```")
    add("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只校验覆盖率，不写文件")
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))

    used: Dict[str, Tuple[str, str]] = {}
    problems: List[str] = []
    for module in manifest["modules"]:
        for section in module["sections"]:
            for rel in section_files(section, manifest):
                rel_norm = rel.replace("\\", "/")
                if rel_norm in used:
                    problems.append(f"重复引用：{rel_norm}（已出现在 {used[rel_norm][0]} / {used[rel_norm][1]}）")
                used[rel_norm] = (module["id"], section["title"])

    expected = set(discover_sources(manifest))
    used_set = set(used)
    missing = sorted(expected - used_set)
    orphan = sorted(used_set - expected)

    for rel in missing:
        problems.append(f"清单漏写源码：{rel}")
    for rel in orphan:
        problems.append(f"文件不存在或不在 include 范围：{rel}")

    if problems:
        print("文档校验失败：", file=sys.stderr)
        for item in problems:
            print("  - " + item, file=sys.stderr)
        return 1

    out_dir = REPO_ROOT / manifest["outDir"]
    stats: List[Tuple[dict, int, int]] = []
    for module in manifest["modules"]:
        files = [rel for section in module["sections"] for rel in section_files(section, manifest)]
        line_count = sum(len(read_text(REPO_ROOT / rel).splitlines()) for rel in files)
        stats.append((module, len(files), line_count))

    if args.check:
        total_files = sum(s[1] for s in stats)
        total_lines = sum(s[2] for s in stats)
        print(f"文档校验通过：{len(manifest['modules'])} 篇 / {total_files} 个文件 / {total_lines} 行，"
              f"与仓库源码一一对应。")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for module in manifest["modules"]:
        target = out_dir / f"{module['slug']}.md"
        target.write_text(render_module(module, manifest, len(manifest["modules"])),
                          encoding="utf-8", newline="\n")
        print(f"写入 {posix(target.relative_to(REPO_ROOT))}")
    (out_dir / "README.md").write_text(render_index(manifest, stats), encoding="utf-8", newline="\n")
    total_files = sum(s[1] for s in stats)
    total_lines = sum(s[2] for s in stats)
    print(f"写入 {posix((out_dir / 'README.md').relative_to(REPO_ROOT))}")
    print(f"完成：{len(manifest['modules'])} 篇 / {total_files} 个文件 / {total_lines} 行。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

### `tools/generate_assets.py`

````python
"""Generate the TOUCHMIND / 念安 logo and default avatar assets."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app" / "src" / "main" / "res"

NAVY = (10, 27, 51, 255)
PURPLE = (108, 77, 246, 255)
CYAN = (8, 145, 178, 255)
GREEN = (22, 163, 106, 255)
WHITE = (255, 255, 255, 255)


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, fill):
    r = size * 0.29
    draw.ellipse((cx - size * 0.47, cy - size * 0.2, cx - size * 0.47 + 2 * r, cy - size * 0.2 + 2 * r), fill=fill)
    draw.ellipse((cx + size * 0.47 - 2 * r, cy - size * 0.2, cx + size * 0.47, cy - size * 0.2 + 2 * r), fill=fill)
    draw.polygon(
        [
            (cx - size * 0.5, cy + size * 0.02),
            (cx + size * 0.5, cy + size * 0.02),
            (cx, cy + size * 0.62),
        ],
        fill=fill,
    )


def draw_mark(size: int, background: bool) -> Image.Image:
    scale = 4
    canvas = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    s = size * scale

    if background:
        rounded_rect(draw, (0, 0, s, s), int(s * 0.23), NAVY)
        # subtle top glow
        glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((-s * 0.2, -s * 0.55, s * 1.2, s * 0.6), fill=(108, 77, 246, 55))
        canvas.alpha_composite(glow)

    # Two interlocking care rings
    ring_w = max(2, int(s * 0.055))
    r = s * 0.205
    left = (s * 0.395, s * 0.49)
    right = (s * 0.605, s * 0.49)
    draw.ellipse(
        (left[0] - r, left[1] - r, left[0] + r, left[1] + r),
        outline=PURPLE, width=ring_w,
    )
    draw.ellipse(
        (right[0] - r, right[1] - r, right[0] + r, right[1] + r),
        outline=CYAN, width=ring_w,
    )
    # Small green connector / heart at the bottom of the rings
    draw_heart(draw, s * 0.5, s * 0.70, s * 0.20, GREEN)
    # Soft white center highlights
    dot = s * 0.022
    draw.ellipse((left[0] - dot, left[1] - dot, left[0] + dot, left[1] + dot), fill=WHITE)
    draw.ellipse((right[0] - dot, right[1] - dot, right[0] + dot, right[1] + dot), fill=WHITE)

    return canvas.resize((size, size), Image.LANCZOS)


def draw_default_avatar(size: int = 256) -> Image.Image:
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # diagonal gradient circle
    grad = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(s):
        t = y / max(1, s - 1)
        r = int(PURPLE[0] * (1 - t) + CYAN[0] * t)
        g = int(PURPLE[1] * (1 - t) + CYAN[1] * t)
        b = int(PURPLE[2] * (1 - t) + CYAN[2] * t)
        gd.line([(0, y), (s, y)], fill=(r, g, b, 255))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
    img.paste(grad, (0, 0), mask)

    # face
    eye = s * 0.032
    for cx in (s * 0.38, s * 0.62):
        draw.ellipse((cx - eye, s * 0.43 - eye, cx + eye, s * 0.43 + eye), fill=WHITE)
    draw.arc((s * 0.33, s * 0.44, s * 0.67, s * 0.68), start=20, end=160, fill=WHITE, width=max(2, int(s * 0.028)))

    # thin white ring
    draw.ellipse((s * 0.02, s * 0.02, s * 0.98, s * 0.98), outline=(255, 255, 255, 210), width=max(2, int(s * 0.018)))
    return img.resize((size, size), Image.LANCZOS)


def main():
    # Launcher foregrounds
    for density, size in {
        "mdpi": 108,
        "hdpi": 162,
        "xhdpi": 216,
        "xxhdpi": 324,
        "xxxhdpi": 432,
    }.items():
        target = RES / f"drawable-{density}" / "ic_launcher_foreground.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        draw_mark(size, background=False).save(target)

    # Preview / store icon
    draw_mark(512, background=True).save(ROOT / "icon.png")
    nodpi = RES / "drawable-nodpi"
    nodpi.mkdir(parents=True, exist_ok=True)
    draw_mark(512, background=True).save(nodpi / "app_logo.png")

    # Default avatar
    draw_default_avatar(256).save(nodpi / "default_avatar.png")
    print("assets generated")


if __name__ == "__main__":
    main()
````

---

返回索引：[README.md](README.md)
