# 01 · 客户端数据层：Room、DataStore、网络与仓库

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

数据层是客户端的地基：Room 负责结构化本地数据（消息、提醒、打卡、日程、设备），DataStore 保存偏好与登录态，Retrofit 访问 FastAPI，Paho 连接 EMQX，Repository 对上层屏蔽数据来源。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. Room 数据库、DAO 与实体](#s01-1) | `AppDatabase` 集中声明版本、迁移与 DAO；实体与 DAO 一一对应，迁移脚本必须随版本号递增。 | 19 |
| [2. 偏好设置与设备码安全](#s01-2) | `Preferences` 封装 DataStore 的读写键；`DeviceCodeCodec` 用 AES-GCM + CRC32 校验设备码，避免暴露项目名与开发板型号。 | 2 |
| [3. 领域模型与 DTO](#s01-3) | 模型分离三类：界面/领域模型、网络 DTO、宠物与情话等静态内容库。 | 7 |
| [4. 网络、MQTT 与智能体客户端](#s01-4) | `CareApi`/`AuthApi` 定义 HTTP 接口；`MqttClientManager` 维护连接与主题订阅；`LlmService` 与 `XiaozhiChatService` 负责服务端大模型与本地大脑回退。 | 10 |
| [5. 仓库层](#s01-5) | 仓库把 Room、DataStore、HTTP、MQTT 组合成界面可直接调用的方法，并统一处理离线缓存与重试。 | 16 |
| [6. 传感器](#s01-6) | `CompassHeading` 将地磁传感器读数平滑为地图头像朝向。 | 1 |

本篇共 **6 个步骤 / 55 个文件**，按表格顺序写入即可还原对应代码。

<a id="s01-1"></a>

## 步骤 01.1 · Room 数据库、DAO 与实体

`AppDatabase` 集中声明版本、迁移与 DAO；实体与 DAO 一一对应，迁移脚本必须随版本号递增。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/local/db/AppDatabase.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/AdviceDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/ChatMessageDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/CheckInDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/CheckInTaskDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/DeviceDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/EventDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/ReminderDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/SchedulePostDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/XiaozhiMessageDao.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/AdviceEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/ChatMessageEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/CheckInEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/CheckInTaskEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/DeviceEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/EventEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/ReminderEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/SchedulePostEntity.kt`
- `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/XiaozhiMessageEntity.kt`

### `app/src/main/java/com/shineleong/toughmind/data/local/db/AppDatabase.kt`

> Room 数据库：版本、实体、DAO、迁移脚本与 30 天清理。

````kotlin
package com.shineleong.toughmind.data.local.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.shineleong.toughmind.data.local.db.dao.AdviceDao
import com.shineleong.toughmind.data.local.db.dao.CheckInDao
import com.shineleong.toughmind.data.local.db.dao.ChatMessageDao
import com.shineleong.toughmind.data.local.db.dao.CheckInTaskDao
import com.shineleong.toughmind.data.local.db.dao.DeviceDao
import com.shineleong.toughmind.data.local.db.dao.EventDao
import com.shineleong.toughmind.data.local.db.dao.ReminderDao
import com.shineleong.toughmind.data.local.db.dao.SchedulePostDao
import com.shineleong.toughmind.data.local.db.dao.XiaozhiMessageDao
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import com.shineleong.toughmind.data.local.db.entity.DeviceEntity
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.local.db.entity.XiaozhiMessageEntity

@Database(
    entities = [
        DeviceEntity::class,
        EventEntity::class,
        AdviceEntity::class,
        CheckInEntity::class,
        CheckInTaskEntity::class,
        ChatMessageEntity::class,
        ReminderEntity::class,
        SchedulePostEntity::class,
        XiaozhiMessageEntity::class,
    ],
    version = 10,
    exportSchema = false,
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun deviceDao(): DeviceDao
    abstract fun eventDao(): EventDao
    abstract fun adviceDao(): AdviceDao
    abstract fun checkInDao(): CheckInDao
    abstract fun reminderDao(): ReminderDao
    abstract fun schedulePostDao(): SchedulePostDao
    abstract fun checkInTaskDao(): CheckInTaskDao
    abstract fun chatMessageDao(): ChatMessageDao
    abstract fun xiaozhiMessageDao(): XiaozhiMessageDao

    companion object {
        @Volatile
        private var instance: AppDatabase? = null

        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "ALTER TABLE devices ADD COLUMN deviceType TEXT NOT NULL DEFAULT 'esp32'"
                )
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS check_ins (" +
                        "date TEXT NOT NULL, " +
                        "personId TEXT NOT NULL, " +
                        "note TEXT NOT NULL, " +
                        "timestamp INTEGER NOT NULL, " +
                        "PRIMARY KEY(date, personId))"
                )
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS reminders (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                        "date TEXT NOT NULL, " +
                        "timeMinutes INTEGER NOT NULL, " +
                        "title TEXT NOT NULL, " +
                        "note TEXT NOT NULL, " +
                        "enabled INTEGER NOT NULL, " +
                        "createdAt INTEGER NOT NULL)"
                )
            }
        }

        private val MIGRATION_2_3 = object : Migration(2, 3) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "ALTER TABLE reminders ADD COLUMN remoteId INTEGER NOT NULL DEFAULT 0"
                )
            }
        }

        private val MIGRATION_3_4 = object : Migration(3, 4) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "ALTER TABLE reminders ADD COLUMN type TEXT NOT NULL DEFAULT 'schedule'"
                )
            }
        }

        private val MIGRATION_4_5 = object : Migration(4, 5) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "ALTER TABLE check_ins ADD COLUMN goal TEXT NOT NULL DEFAULT ''"
                )
                db.execSQL(
                    "ALTER TABLE check_ins ADD COLUMN imageBase64 TEXT NOT NULL DEFAULT ''"
                )
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS schedule_posts (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                        "date TEXT NOT NULL, " +
                        "timeMinutes INTEGER NOT NULL, " +
                        "content TEXT NOT NULL, " +
                        "imageBase64 TEXT NOT NULL, " +
                        "authorId TEXT NOT NULL, " +
                        "createdAt INTEGER NOT NULL, " +
                        "remoteId INTEGER NOT NULL)"
                )
            }
        }

        private val MIGRATION_5_6 = object : Migration(5, 6) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS checkin_tasks (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                        "date TEXT NOT NULL, " +
                        "title TEXT NOT NULL, " +
                        "selfDone INTEGER NOT NULL, " +
                        "partnerDone INTEGER NOT NULL, " +
                        "imageBase64 TEXT NOT NULL, " +
                        "createdBy TEXT NOT NULL, " +
                        "createdAt INTEGER NOT NULL, " +
                        "remoteId INTEGER NOT NULL)"
                )
            }
        }

        private val MIGRATION_6_7 = object : Migration(6, 7) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS chat_messages (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                        "date TEXT NOT NULL, " +
                        "timeMinutes INTEGER NOT NULL, " +
                        "fromSelf INTEGER NOT NULL, " +
                        "text TEXT NOT NULL, " +
                        "imageBase64 TEXT NOT NULL, " +
                        "audioPath TEXT NOT NULL, " +
                        "audioDurationMs INTEGER NOT NULL, " +
                        "createdAt INTEGER NOT NULL)"
                )
            }
        }

        private val MIGRATION_7_8 = object : Migration(7, 8) {
            override fun migrate(db: SupportSQLiteDatabase) {
                val columns = mutableSetOf<String>()
                db.query("PRAGMA table_info(chat_messages)").use { cursor ->
                    val nameIndex = cursor.getColumnIndex("name")
                    while (cursor.moveToNext()) {
                        if (nameIndex >= 0) columns += cursor.getString(nameIndex)
                    }
                }
                if ("remoteId" !in columns) {
                    db.execSQL("ALTER TABLE chat_messages ADD COLUMN remoteId INTEGER NOT NULL DEFAULT 0")
                }
                if ("senderName" !in columns) {
                    db.execSQL("ALTER TABLE chat_messages ADD COLUMN senderName TEXT NOT NULL DEFAULT ''")
                }
                db.execSQL("DROP INDEX IF EXISTS idx_chat_remote")
            }
        }

        private val MIGRATION_8_9 = object : Migration(8, 9) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "ALTER TABLE advices ADD COLUMN kind TEXT NOT NULL DEFAULT 'action'"
                )
            }
        }

        /** v10：新增「小智」对话表，和两人聊天分开。 */
        private val MIGRATION_9_10 = object : Migration(9, 10) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS xiaozhi_messages (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                        "role TEXT NOT NULL, " +
                        "text TEXT NOT NULL, " +
                        "createdAt INTEGER NOT NULL, " +
                        "source TEXT NOT NULL)"
                )
            }
        }

        fun getInstance(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "toughmind.db",
                )
                    .addMigrations(
                        MIGRATION_1_2,
                        MIGRATION_2_3,
                        MIGRATION_3_4,
                        MIGRATION_4_5,
                        MIGRATION_5_6,
                        MIGRATION_6_7,
                        MIGRATION_7_8,
                        MIGRATION_8_9,
                        MIGRATION_9_10,
                    )
                    .build()
                    .also { instance = it }
            }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/AdviceDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface AdviceDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(advice: AdviceEntity): Long

    @Query("SELECT * FROM advices WHERE deviceId = :deviceId ORDER BY timestamp DESC, id DESC")
    fun observeByDevice(deviceId: String): Flow<List<AdviceEntity>>

    @Query("DELETE FROM advices WHERE deviceId = :deviceId")
    suspend fun deleteByDevice(deviceId: String)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/ChatMessageDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ChatMessageDao {
    @Query("SELECT * FROM chat_messages ORDER BY createdAt ASC LIMIT 300")
    fun observeAll(): Flow<List<ChatMessageEntity>>

    @Query("SELECT * FROM chat_messages WHERE remoteId = :remoteId LIMIT 1")
    suspend fun findByRemoteId(remoteId: Long): ChatMessageEntity?

    @Query("SELECT COALESCE(MAX(remoteId), 0) FROM chat_messages")
    suspend fun maxRemoteId(): Long

    @Insert
    suspend fun insert(message: ChatMessageEntity): Long
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/CheckInDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CheckInDao {

    @Upsert
    suspend fun upsert(checkIn: CheckInEntity)

    @Query("SELECT * FROM check_ins WHERE date >= :start AND date <= :end ORDER BY date ASC")
    fun observeBetween(start: String, end: String): Flow<List<CheckInEntity>>

    @Query("SELECT * FROM check_ins WHERE date = :date")
    fun observeDate(date: String): Flow<List<CheckInEntity>>

    @Query("DELETE FROM check_ins WHERE date = :date AND personId = :personId")
    suspend fun delete(date: String, personId: String)

    @Query("DELETE FROM check_ins WHERE date >= :start AND date <= :end")
    suspend fun deleteBetween(start: String, end: String)

    @Query("DELETE FROM check_ins WHERE date = :date")
    suspend fun deleteDate(date: String)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/CheckInTaskDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CheckInTaskDao {

    @Query("SELECT * FROM checkin_tasks WHERE date = :date ORDER BY createdAt ASC, id ASC")
    fun observeDate(date: String): Flow<List<CheckInTaskEntity>>

    @Query("SELECT * FROM checkin_tasks WHERE date BETWEEN :start AND :end ORDER BY date ASC, createdAt ASC")
    fun observeBetween(start: String, end: String): Flow<List<CheckInTaskEntity>>

    @Query("SELECT * FROM checkin_tasks WHERE remoteId = :remoteId LIMIT 1")
    suspend fun findByRemoteId(remoteId: Long): CheckInTaskEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(task: CheckInTaskEntity): Long

    @Query("UPDATE checkin_tasks SET selfDone = :selfDone WHERE id = :id")
    suspend fun setSelfDone(id: Long, selfDone: Boolean)

    @Query("UPDATE checkin_tasks SET partnerDone = :partnerDone WHERE id = :id")
    suspend fun setPartnerDone(id: Long, partnerDone: Boolean)

    @Query("DELETE FROM checkin_tasks WHERE date = :date")
    suspend fun deleteDate(date: String)

    @Query("DELETE FROM checkin_tasks WHERE id = :id")
    suspend fun delete(id: Long)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/DeviceDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.DeviceEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DeviceDao {

    @Query("SELECT * FROM devices ORDER BY bindTime DESC")
    fun observeAll(): Flow<List<DeviceEntity>>

    @Query("SELECT * FROM devices WHERE deviceId = :deviceId")
    fun observeById(deviceId: String): Flow<DeviceEntity?>

    @Query("SELECT * FROM devices")
    suspend fun getAll(): List<DeviceEntity>

    @Query("SELECT * FROM devices WHERE deviceId = :deviceId")
    suspend fun getById(deviceId: String): DeviceEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(device: DeviceEntity)

    @Query("UPDATE devices SET isOnline = :online, lastOnlineTime = :time WHERE deviceId = :deviceId")
    suspend fun updateOnline(deviceId: String, online: Boolean, time: Long)

    @Query("DELETE FROM devices WHERE deviceId = :deviceId")
    suspend fun delete(deviceId: String)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/EventDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface EventDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(event: EventEntity): Long

    @Query("SELECT * FROM events WHERE deviceId = :deviceId AND timestamp BETWEEN :start AND :end ORDER BY timestamp DESC")
    fun observeEvents(deviceId: String, start: Long, end: Long): Flow<List<EventEntity>>

    @Query("SELECT * FROM events WHERE id = :id")
    suspend fun getById(id: Long): EventEntity?
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/ReminderDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ReminderDao {

    @Insert
    suspend fun insert(reminder: ReminderEntity): Long

    @Update
    suspend fun update(reminder: ReminderEntity)

    @Delete
    suspend fun delete(reminder: ReminderEntity)

    @Query("SELECT * FROM reminders WHERE date >= :start AND date <= :end ORDER BY date ASC, timeMinutes ASC")
    fun observeBetween(start: String, end: String): Flow<List<ReminderEntity>>

    @Query("SELECT * FROM reminders WHERE date = :date ORDER BY timeMinutes ASC")
    fun observeDate(date: String): Flow<List<ReminderEntity>>

    @Query("SELECT * FROM reminders WHERE enabled = 1 AND date >= :from ORDER BY date ASC, timeMinutes ASC")
    suspend fun enabledFrom(from: String): List<ReminderEntity>

    @Query("SELECT * FROM reminders WHERE id = :id")
    suspend fun getById(id: Long): ReminderEntity?

    @Query("SELECT * FROM reminders WHERE remoteId = :remoteId LIMIT 1")
    suspend fun findByRemoteId(remoteId: Long): ReminderEntity?

    @Query("SELECT * FROM reminders WHERE date BETWEEN :start AND :end AND remoteId != 0")
    suspend fun syncedBetween(start: String, end: String): List<ReminderEntity>

    @Query("DELETE FROM reminders WHERE remoteId = :remoteId AND remoteId != 0")
    suspend fun deleteByRemoteId(remoteId: Long)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/SchedulePostDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SchedulePostDao {

    @Query("SELECT * FROM schedule_posts WHERE date BETWEEN :start AND :end ORDER BY date DESC, timeMinutes DESC")
    fun observeBetween(start: String, end: String): Flow<List<SchedulePostEntity>>

    @Query("SELECT * FROM schedule_posts WHERE date = :date ORDER BY timeMinutes ASC, createdAt ASC")
    fun observeDate(date: String): Flow<List<SchedulePostEntity>>

    @Query("SELECT * FROM schedule_posts WHERE remoteId = :remoteId LIMIT 1")
    suspend fun findByRemoteId(remoteId: Long): SchedulePostEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(post: SchedulePostEntity): Long

    @Query("DELETE FROM schedule_posts WHERE remoteId = :remoteId")
    suspend fun deleteByRemoteId(remoteId: Long)

    @Query("DELETE FROM schedule_posts WHERE id = :id")
    suspend fun delete(id: Long)

    @Query("DELETE FROM schedule_posts WHERE date BETWEEN :start AND :end")
    suspend fun deleteBetween(start: String, end: String)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/dao/XiaozhiMessageDao.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.shineleong.toughmind.data.local.db.entity.XiaozhiMessageEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface XiaozhiMessageDao {
    @Query("SELECT * FROM xiaozhi_messages ORDER BY createdAt ASC, id ASC LIMIT 200")
    fun observeAll(): Flow<List<XiaozhiMessageEntity>>

    /** 最近 [limit] 条，按时间倒序返回；调用方再反转成对话顺序。 */
    @Query("SELECT * FROM xiaozhi_messages ORDER BY id DESC LIMIT :limit")
    suspend fun recent(limit: Int): List<XiaozhiMessageEntity>

    @Insert
    suspend fun insert(message: XiaozhiMessageEntity): Long

    @Query("DELETE FROM xiaozhi_messages")
    suspend fun clear()

    /** 只保留最近 [keep] 条，避免对话无限增长。 */
    @Query(
        "DELETE FROM xiaozhi_messages WHERE id NOT IN " +
            "(SELECT id FROM xiaozhi_messages ORDER BY id DESC LIMIT :keep)"
    )
    suspend fun trim(keep: Int)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/AdviceEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "advices")
data class AdviceEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val deviceId: String = "",
    val content: String = "",
    val timestamp: Long = 0L,
    /** 建议角度：action / words / surprise / love。旧数据默认 action。 */
    val kind: String = "action",
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/ChatMessageEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "chat_messages")
data class ChatMessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    @ColumnInfo(defaultValue = "0") val remoteId: Long = 0L,
    @ColumnInfo(defaultValue = "'") val senderName: String = "",
    val date: String,
    val timeMinutes: Int,
    val fromSelf: Boolean,
    val text: String = "",
    val imageBase64: String = "",
    val audioPath: String = "",
    val audioDurationMs: Long = 0L,
    val createdAt: Long = 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/CheckInEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.ColumnInfo
import androidx.room.Entity

/**
 * 某一天某个人的打卡记录。
 * personId 取 "self"（我）或 "partner"（TA）。双方都打卡的日期在日历上显示为红色。
 */
@Entity(tableName = "check_ins", primaryKeys = ["date", "personId"])
data class CheckInEntity(
    val date: String,
    val personId: String,
    val note: String = "",
    val timestamp: Long = 0L,
    @ColumnInfo(defaultValue = "") val goal: String = "",
    @ColumnInfo(defaultValue = "") val imageBase64: String = "",
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/CheckInTaskEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 一天里的一条共同任务；selfDone / partnerDone 分别表示双方是否完成。 */
@Entity(tableName = "checkin_tasks")
data class CheckInTaskEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val date: String,
    val title: String,
    val selfDone: Boolean = false,
    val partnerDone: Boolean = false,
    val imageBase64: String = "",
    val createdBy: String = "self",
    val createdAt: Long = 0L,
    val remoteId: Long = 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/DeviceEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "devices")
data class DeviceEntity(
    @PrimaryKey val deviceId: String,
    val deviceName: String = "",
    @ColumnInfo(defaultValue = "esp32") val deviceType: String = "esp32",
    val bindTime: Long = 0L,
    val lastOnlineTime: Long = 0L,
    val isOnline: Boolean = false,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/EventEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "events")
data class EventEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val deviceId: String = "",
    /** state / alarm / medical */
    val type: String = "state",
    val level: Int = 0,
    val fatigueScore: Double = 0.0,
    val perclos: Double = 0.0,
    val yawnTotal: Int = 0,
    val headDistracted: Boolean = false,
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val speed: Double = 0.0,
    val temperature: Double = 0.0,
    val medicalLevel: Int = 0,
    val medicalType: Int = 0,
    val message: String = "",
    val timestamp: Long = 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/ReminderEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * 日历定时任务 / 提醒。
 * date 为 yyyy-MM-dd，timeMinutes 为当天 0 点起的分钟数（0..1439）。
 * remoteId 为云端关心组提醒 ID；0 表示仅本机（演示 / 未配对）。
 */
@Entity(tableName = "reminders")
data class ReminderEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val date: String,
    val timeMinutes: Int,
    val title: String,
    val note: String = "",
    val enabled: Boolean = true,
    val createdAt: Long = 0L,
    @ColumnInfo(defaultValue = "0") val remoteId: Long = 0L,
    @ColumnInfo(defaultValue = "schedule") val type: String = TYPE_SCHEDULE,
) {
    companion object {
        const val TYPE_ANNIVERSARY = "anniversary"
        const val TYPE_SCHEDULE = "schedule"
        const val TYPE_BIRTHDAY = "birthday"
        const val TYPE_COUNTDOWN = "countdown"

        val TYPES = listOf(TYPE_ANNIVERSARY, TYPE_SCHEDULE, TYPE_BIRTHDAY, TYPE_COUNTDOWN)
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/SchedulePostEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 双方共享的日程记录：谁在什么时候做了什么。 */
@Entity(tableName = "schedule_posts")
data class SchedulePostEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val date: String,
    val timeMinutes: Int,
    val content: String,
    val imageBase64: String = "",
    val authorId: String,
    val createdAt: Long = 0L,
    val remoteId: Long = 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/local/db/entity/XiaozhiMessageEntity.kt`

````kotlin
package com.shineleong.toughmind.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * 「小智」对话消息。与两人聊天（chat_messages）分开存，互不影响。
 *
 * role: user / assistant
 * source: user（用户输入）/ remote（云端大模型）/ local（本地兜底）
 */
@Entity(tableName = "xiaozhi_messages")
data class XiaozhiMessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val role: String,
    val text: String,
    val createdAt: Long,
    val source: String = "local",
)
````

<a id="s01-2"></a>

## 步骤 01.2 · 偏好设置与设备码安全

`Preferences` 封装 DataStore 的读写键；`DeviceCodeCodec` 用 AES-GCM + CRC32 校验设备码，避免暴露项目名与开发板型号。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/local/Preferences.kt`
- `app/src/main/java/com/shineleong/toughmind/data/security/DeviceCodeCodec.kt`

### `app/src/main/java/com/shineleong/toughmind/data/local/Preferences.kt`

> DataStore 偏好：登录态、主题、语言、关怀模式、朗读、宠物与浪漫清单进度。

````kotlin
package com.shineleong.toughmind.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.shineleong.toughmind.data.model.OwlSpecies
import com.shineleong.toughmind.data.model.PetState
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

/** 用户偏好与登录会话存储（DataStore）。 */
class Preferences(private val context: Context) {

    private object Keys {
        val TOKEN = stringPreferencesKey("token")
        val ACCOUNT = stringPreferencesKey("account")
        val NICKNAME = stringPreferencesKey("nickname")
        val CURRENT_DEVICE_ID = stringPreferencesKey("current_device_id")
        val NOTIFICATION_ENABLED = booleanPreferencesKey("notification_enabled")
        val SOUND_ENABLED = booleanPreferencesKey("sound_enabled")
        val AVATAR_PATH = stringPreferencesKey("avatar_path")

        // 亲友绑定（"念安"核心信息）
        val COMPANION_NAME = stringPreferencesKey("companion_name")
        val COMPANION_RELATION = stringPreferencesKey("companion_relation")
        val COMPANION_DEVICE_TYPE = stringPreferencesKey("companion_device_type")
        val COMPANION_DEMO_MODE = booleanPreferencesKey("companion_demo_mode")

        // 云端关心消息游标，避免重启后漏消息或重复通知
        val LAST_NUDGE_ID = longPreferencesKey("last_nudge_id")

        // 心情 emoji 与头像留言
        val MOOD_EMOJI = stringPreferencesKey("mood_emoji")
        val MOOD_MESSAGE = stringPreferencesKey("mood_message")

        // 主题：system / light / dark
        val THEME_MODE = stringPreferencesKey("theme_mode")

        // 语言：zh / en
        val LANGUAGE = stringPreferencesKey("language")
        val SHOW_PARTNER_ON_MAP = booleanPreferencesKey("show_partner_on_map")
        val CARE_MODE = stringPreferencesKey("care_mode")
        val ELDER_MODE = booleanPreferencesKey("elder_mode")
        val TTS_PRESET = stringPreferencesKey("tts_preset")
        val TTS_MODE = stringPreferencesKey("tts_mode")
        val FONT_SCALE = floatPreferencesKey("font_scale")
        val SPEECH_RATE = floatPreferencesKey("speech_rate")
        val XIAOZHI_NAME = stringPreferencesKey("xiaozhi_name")
        // 一起做的一万件浪漫小事：已完成条目的 id
        val ROMANCE_DONE_IDS = stringSetPreferencesKey("romance_done_ids")
        // 宠物：沿用 pet_hunger / pet_last_fed_by / pet_updated_at，兼容旧版的猫狗存档。
        val PET_ADOPTED = booleanPreferencesKey("pet_adopted")
        val PET_NAME = stringPreferencesKey("pet_name")
        val PET_SPECIES = stringPreferencesKey("pet_species")
        val PET_HUNGER = stringPreferencesKey("pet_hunger")
        val PET_LAST_FED_BY = stringPreferencesKey("pet_last_fed_by")
        val PET_UPDATED_AT = stringPreferencesKey("pet_updated_at")
        val PET_ENERGY = stringPreferencesKey("pet_energy")
        val PET_MOOD = stringPreferencesKey("pet_mood")
        val PET_BOND = stringPreferencesKey("pet_bond")
        val PET_LAST_FED_AT = stringPreferencesKey("pet_last_fed_at")
        val PET_LAST_PET_AT = stringPreferencesKey("pet_last_pet_at")
        val PET_FEED_COUNT = stringPreferencesKey("pet_feed_count")
        val PET_FEED_DAY = stringPreferencesKey("pet_feed_day")
        val PET_ASLEEP = booleanPreferencesKey("pet_asleep")
        val PET_OVERFED = booleanPreferencesKey("pet_overfed")

        // AI 小智：语音播报开关
        val XIAOZHI_VOICE = booleanPreferencesKey("xiaozhi_voice")
        // AI 小智外在形象：orb（光核）/ pet（宠物）
        val XIAOZHI_APPEARANCE = stringPreferencesKey("xiaozhi_appearance")
    }

    val token: Flow<String> = context.dataStore.data.map { it[Keys.TOKEN].orEmpty() }
    val account: Flow<String> = context.dataStore.data.map { it[Keys.ACCOUNT].orEmpty() }
    val nickname: Flow<String> = context.dataStore.data.map { it[Keys.NICKNAME].orEmpty() }
    val currentDeviceId: Flow<String> =
        context.dataStore.data.map { it[Keys.CURRENT_DEVICE_ID].orEmpty() }
    val notificationEnabled: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.NOTIFICATION_ENABLED] ?: true }
    val soundEnabled: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.SOUND_ENABLED] ?: true }
    val avatarPath: Flow<String> =
        context.dataStore.data.map { it[Keys.AVATAR_PATH].orEmpty() }

    val companionName: Flow<String> =
        context.dataStore.data.map { it[Keys.COMPANION_NAME].orEmpty() }
    val companionRelation: Flow<String> =
        context.dataStore.data.map { it[Keys.COMPANION_RELATION] ?: "家人" }
    val companionDeviceType: Flow<String> =
        context.dataStore.data.map { it[Keys.COMPANION_DEVICE_TYPE] ?: "PHONE" }
    val companionDemoMode: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.COMPANION_DEMO_MODE] ?: false }

    val lastNudgeId: Flow<Long> =
        context.dataStore.data.map { it[Keys.LAST_NUDGE_ID] ?: 0L }

    val moodEmoji: Flow<String> =
        context.dataStore.data.map { it[Keys.MOOD_EMOJI] ?: "🙂" }
    val moodMessage: Flow<String> =
        context.dataStore.data.map { it[Keys.MOOD_MESSAGE] ?: "今天也要好好生活" }

    val themeMode: Flow<String> =
        context.dataStore.data.map { it[Keys.THEME_MODE] ?: "system" }
    val language: Flow<String> =
        context.dataStore.data.map { it[Keys.LANGUAGE] ?: "zh" }
    val showPartnerOnMap: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.SHOW_PARTNER_ON_MAP] ?: true }
    val careMode: Flow<String> =
        context.dataStore.data.map { it[Keys.CARE_MODE] ?: "couple" }
    val elderMode: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.ELDER_MODE] ?: false }
    val ttsPreset: Flow<String> =
        context.dataStore.data.map { it[Keys.TTS_PRESET] ?: "auto" }
    val ttsMode: Flow<String> =
        context.dataStore.data.map { it[Keys.TTS_MODE] ?: "offline" }
    val fontScale: Flow<Float> =
        context.dataStore.data.map { it[Keys.FONT_SCALE] ?: 1f }
    val speechRate: Flow<Float> =
        context.dataStore.data.map { it[Keys.SPEECH_RATE] ?: 1f }
    val xiaozhiName: Flow<String> =
        context.dataStore.data.map { it[Keys.XIAOZHI_NAME] ?: "小智" }
    val xiaozhiVoice: Flow<Boolean> =
        context.dataStore.data.map { it[Keys.XIAOZHI_VOICE] ?: true }
    val xiaozhiAppearance: Flow<String> =
        context.dataStore.data.map { it[Keys.XIAOZHI_APPEARANCE] ?: "orb" }
    val romanceDoneIds: Flow<Set<Int>> = context.dataStore.data.map { data ->
        data[Keys.ROMANCE_DONE_IDS].orEmpty().mapNotNull { it.toIntOrNull() }.toSet()
    }

    val owlPet: Flow<PetState> = context.dataStore.data.map { data ->
        // 老版本已有宠物数据但没有 pet_adopted 键：视为已经领养，避免升级后宠物消失。
        val hasLegacyPet = data[Keys.PET_HUNGER] != null || data[Keys.PET_UPDATED_AT] != null
        PetState(
            adopted = data[Keys.PET_ADOPTED] ?: hasLegacyPet,
            species = OwlSpecies.fromStorage(data[Keys.PET_SPECIES]),
            name = data[Keys.PET_NAME].orEmpty(),
            satiety = data[Keys.PET_HUNGER]?.toIntOrNull()?.coerceIn(0, 100) ?: 70,
            energy = data[Keys.PET_ENERGY]?.toIntOrNull()?.coerceIn(0, 100) ?: 72,
            mood = data[Keys.PET_MOOD]?.toIntOrNull()?.coerceIn(0, 100) ?: 80,
            bond = data[Keys.PET_BOND]?.toIntOrNull()?.coerceIn(0, 100) ?: 10,
            lastFedAt = data[Keys.PET_LAST_FED_AT]?.toLongOrNull() ?: 0L,
            lastPetAt = data[Keys.PET_LAST_PET_AT]?.toLongOrNull() ?: 0L,
            lastFedBy = data[Keys.PET_LAST_FED_BY].orEmpty(),
            updatedAt = data[Keys.PET_UPDATED_AT]?.toLongOrNull() ?: 0L,
            feedCountToday = data[Keys.PET_FEED_COUNT]?.toIntOrNull()?.coerceAtLeast(0) ?: 0,
            feedDay = data[Keys.PET_FEED_DAY].orEmpty(),
            asleep = data[Keys.PET_ASLEEP] ?: false,
            overfed = data[Keys.PET_OVERFED] ?: false,
        )
    }

    suspend fun setMood(emoji: String, message: String) {
        context.dataStore.edit {
            it[Keys.MOOD_EMOJI] = emoji
            it[Keys.MOOD_MESSAGE] = message
        }
    }

    suspend fun setThemeMode(mode: String) {
        context.dataStore.edit { it[Keys.THEME_MODE] = mode }
    }

    suspend fun setLanguage(language: String) {
        context.dataStore.edit { it[Keys.LANGUAGE] = language }
    }

    suspend fun setShowPartnerOnMap(show: Boolean) {
        context.dataStore.edit { it[Keys.SHOW_PARTNER_ON_MAP] = show }
    }

    suspend fun setCareMode(mode: String) {
        context.dataStore.edit { it[Keys.CARE_MODE] = mode }
    }

    suspend fun setElderMode(enabled: Boolean) {
        context.dataStore.edit { it[Keys.ELDER_MODE] = enabled }
    }

    suspend fun setTtsPreset(preset: String) {
        context.dataStore.edit { it[Keys.TTS_PRESET] = preset }
    }

    suspend fun setTtsMode(mode: String) {
        context.dataStore.edit { it[Keys.TTS_MODE] = mode }
    }

    suspend fun setFontScale(scale: Float) {
        context.dataStore.edit { it[Keys.FONT_SCALE] = scale.coerceIn(1f, 1.5f) }
    }

    suspend fun setSpeechRate(rate: Float) {
        context.dataStore.edit { it[Keys.SPEECH_RATE] = rate.coerceIn(0.7f, 1.3f) }
    }

    suspend fun setXiaozhiName(name: String) {
        context.dataStore.edit { it[Keys.XIAOZHI_NAME] = name.trim().take(12) }
    }

    suspend fun setXiaozhiVoice(enabled: Boolean) {
        context.dataStore.edit { it[Keys.XIAOZHI_VOICE] = enabled }
    }

    suspend fun setXiaozhiAppearance(appearance: String) {
        context.dataStore.edit { it[Keys.XIAOZHI_APPEARANCE] = appearance }
    }

    suspend fun toggleRomanceDone(id: Int) {
        context.dataStore.edit { data ->
            val current = data[Keys.ROMANCE_DONE_IDS].orEmpty()
            val key = id.toString()
            data[Keys.ROMANCE_DONE_IDS] = if (key in current) current - key else current + key
        }
    }

    suspend fun setOwlPet(pet: PetState) {
        context.dataStore.edit {
            it[Keys.PET_ADOPTED] = pet.adopted
            it[Keys.PET_NAME] = pet.name
            it[Keys.PET_SPECIES] = pet.species.storageKey
            it[Keys.PET_HUNGER] = pet.satiety.toString()
            it[Keys.PET_ENERGY] = pet.energy.toString()
            it[Keys.PET_MOOD] = pet.mood.toString()
            it[Keys.PET_BOND] = pet.bond.toString()
            it[Keys.PET_LAST_FED_AT] = pet.lastFedAt.toString()
            it[Keys.PET_LAST_PET_AT] = pet.lastPetAt.toString()
            it[Keys.PET_LAST_FED_BY] = pet.lastFedBy
            it[Keys.PET_UPDATED_AT] = pet.updatedAt.toString()
            it[Keys.PET_FEED_COUNT] = pet.feedCountToday.toString()
            it[Keys.PET_FEED_DAY] = pet.feedDay
            it[Keys.PET_ASLEEP] = pet.asleep
            it[Keys.PET_OVERFED] = pet.overfed
        }
    }

    suspend fun setLastNudgeId(id: Long) {
        context.dataStore.edit { it[Keys.LAST_NUDGE_ID] = id }
    }

    suspend fun saveCompanion(name: String, relation: String, deviceType: String, demoMode: Boolean) {
        context.dataStore.edit {
            it[Keys.COMPANION_NAME] = name
            it[Keys.COMPANION_RELATION] = relation
            it[Keys.COMPANION_DEVICE_TYPE] = deviceType
            it[Keys.COMPANION_DEMO_MODE] = demoMode
        }
    }

    suspend fun clearCompanion() {
        context.dataStore.edit {
            it.remove(Keys.COMPANION_NAME)
            it.remove(Keys.COMPANION_RELATION)
            it.remove(Keys.COMPANION_DEVICE_TYPE)
            it.remove(Keys.COMPANION_DEMO_MODE)
        }
    }

    suspend fun clearLegacyDemoCompanion() {
        val data = context.dataStore.data.first()
        if (data[Keys.COMPANION_DEMO_MODE] == true && data[Keys.COMPANION_NAME] == "安") {
            clearCompanion()
        }
    }

    suspend fun saveSession(account: String, nickname: String, token: String) {
        context.dataStore.edit {
            it[Keys.ACCOUNT] = account
            it[Keys.NICKNAME] = nickname
            it[Keys.TOKEN] = token
        }
    }

    suspend fun saveCurrentDeviceId(deviceId: String) {
        context.dataStore.edit { it[Keys.CURRENT_DEVICE_ID] = deviceId }
    }

    suspend fun setNotificationEnabled(enabled: Boolean) {
        context.dataStore.edit { it[Keys.NOTIFICATION_ENABLED] = enabled }
    }

    suspend fun setSoundEnabled(enabled: Boolean) {
        context.dataStore.edit { it[Keys.SOUND_ENABLED] = enabled }
    }

    suspend fun setNickname(nickname: String) {
        context.dataStore.edit { it[Keys.NICKNAME] = nickname }
    }

    suspend fun setAvatarPath(path: String) {
        context.dataStore.edit { it[Keys.AVATAR_PATH] = path }
    }

    suspend fun clearSession() {
        context.dataStore.edit {
            it.remove(Keys.ACCOUNT)
            it.remove(Keys.NICKNAME)
            it.remove(Keys.TOKEN)
        }
    }

    suspend fun getCurrentDeviceId(): String = currentDeviceId.first()
}
````

### `app/src/main/java/com/shineleong/toughmind/data/security/DeviceCodeCodec.kt`

> 设备码 AES-GCM 编解码与 CRC32 校验，不暴露项目名与开发板型号。

````kotlin
package com.shineleong.toughmind.data.security

import android.util.Base64
import com.shineleong.toughmind.BuildConfig
import java.security.MessageDigest
import java.util.zip.CRC32
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * 设备码：不暴露开发板型号/项目名，使用 AES-GCM 对称加密 + CRC 校验。
 * 硬件端用同一把 DEVICE_CODE_KEY 生成，手机端输入后即可解出 deviceId。
 */
object DeviceCodeCodec {
    private const val VERSION = "TM1"
    private const val IV_SIZE = 12
    private const val TAG_BITS = 128

    private fun key(): SecretKeySpec {
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(BuildConfig.DEVICE_CODE_KEY.toByteArray(Charsets.UTF_8))
        return SecretKeySpec(digest, "AES")
    }

    fun generate(deviceId: String): String {
        val checksum = crc(deviceId)
        val payload = "$VERSION|$deviceId|$checksum".toByteArray(Charsets.UTF_8)
        val iv = ByteArray(IV_SIZE).also { java.security.SecureRandom().nextBytes(it) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key(), GCMParameterSpec(TAG_BITS, iv))
        val encrypted = cipher.doFinal(payload)
        val packed = iv + encrypted
        return Base64.encodeToString(
            packed,
            Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING,
        )
    }

    fun decode(code: String): String? {
        return runCatching {
            val normalized = code.trim().replace(" ", "").let {
                it + "=".repeat((4 - it.length % 4) % 4)
            }
            val packed = Base64.decode(
                normalized,
                Base64.URL_SAFE or Base64.NO_WRAP,
            )
            if (packed.size <= IV_SIZE) return null
            val iv = packed.copyOfRange(0, IV_SIZE)
            val body = packed.copyOfRange(IV_SIZE, packed.size)
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(TAG_BITS, iv))
            val payload = String(cipher.doFinal(body), Charsets.UTF_8)
            val parts = payload.split("|")
            if (parts.size != 3 || parts[0] != VERSION) return null
            val deviceId = parts[1]
            if (parts[2] != crc(deviceId)) return null
            deviceId
        }.getOrNull()
    }

    private fun crc(value: String): String {
        val crc = CRC32()
        crc.update(value.toByteArray(Charsets.UTF_8))
        return crc.value.toString(16).padStart(8, '0')
    }
}
````

<a id="s01-3"></a>

## 步骤 01.3 · 领域模型与 DTO

模型分离三类：界面/领域模型、网络 DTO、宠物与情话等静态内容库。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/model/CareAdvice.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/CareModels.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/Dtos.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/Models.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/PetModels.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/Romance.kt`
- `app/src/main/java/com/shineleong/toughmind/data/model/XiaozhiModels.kt`

### `app/src/main/java/com/shineleong/toughmind/data/model/CareAdvice.kt`

> 关心建议库：按时间/状态挑选中文与英文建议。

````kotlin
package com.shineleong.toughmind.data.model

/**
 * 关心建议的角度。
 *
 * 一次生成多条建议，分别覆盖「马上能做」「说点什么」「小惊喜」；
 * 情侣模式再补一条「情话」，避免所有建议都长成同一句“注意身体”。
 */
enum class AdviceKind(val key: String) {
    ACTION("action"),
    WORDS("words"),
    SURPRISE("surprise"),
    LOVE("love");

    companion object {
        private fun fromKeyOnly(value: String?): AdviceKind? =
            entries.firstOrNull { it.key.equals(value?.trim(), ignoreCase = true) }

        /** 兼容 kind 字段既可能是英文 key，也可能是模型顺手写的中文标签。 */
        fun fromKey(key: String?): AdviceKind =
            fromKeyOnly(key) ?: fromLabel(key) ?: ACTION

        /** 兼容大模型输出的中文标签，如「马上做」「说句话」「小惊喜」「情话」。 */
        fun fromLabel(label: String?): AdviceKind? {
            val value = label?.trim().orEmpty()
            if (value.isBlank()) return null
            fromKeyOnly(value)?.let { return it }
            return when {
                value.contains("情话") || value.contains("想你") -> LOVE
                value.contains("惊喜") || value.contains("礼物") -> SURPRISE
                value.contains("说") || value.contains("话") || value.contains("表达") -> WORDS
                value.contains("做") || value.contains("行动") || value.contains("马上") -> ACTION
                else -> null
            }
        }
    }
}

/** 一条待展示的关心建议。 */
data class CareTip(
    val kind: AdviceKind,
    val content: String,
)

/**
 * 本地关心建议库：大模型不可用时也能一次给足多条，
 * 并且按 TA 当前的状态（学习、疲劳、驾驶、睡觉、天气、生病……）换不同说法。
 */
object CareTipLibrary {

    private enum class Situation { URGENT, DRIVING, SLEEPING, SICK, TIRED, BUSY, WEATHER, EATING, DAILY }

    private fun detect(scene: String): Situation = when {
        scene.contains("医学异常") || scene.contains("跌倒") || scene.contains("抽搐") ->
            Situation.URGENT

        scene.contains("开车") || scene.contains("驾驶") || scene.contains("路上") ->
            Situation.DRIVING

        scene.contains("睡") || scene.contains("晚安") || scene.contains("入睡") ->
            Situation.SLEEPING

        scene.contains("生病") || scene.contains("发烧") || scene.contains("感冒") ||
            scene.contains("不舒服") || scene.contains("医院") -> Situation.SICK

        scene.contains("累") || scene.contains("疲劳") || scene.contains("加班") ->
            Situation.TIRED

        scene.contains("学习") || scene.contains("自习") || scene.contains("工作") ||
            scene.contains("忙") || scene.contains("会议") -> Situation.BUSY

        scene.contains("雨") || scene.contains("降温") || scene.contains("天气") ||
            scene.contains("冷") || scene.contains("热") -> Situation.WEATHER

        scene.contains("吃") || scene.contains("饿") || scene.contains("饭") ->
            Situation.EATING

        else -> Situation.DAILY
    }

    /** 每种状态、每个角度准备两种说法，连点两次「再想三条」也不会完全重复。 */
    private val templates: Map<Situation, Map<AdviceKind, List<String>>> = mapOf(
        Situation.URGENT to mapOf(
            AdviceKind.ACTION to listOf(
                "先直接打电话确认 TA 是否清醒、能否应答；联系不上就马上联系身边的人。",
                "打开地图确认 TA 的位置，必要时拨打 120，并把准确地址发给急救人员。",
            ),
            AdviceKind.WORDS to listOf(
                "如果 TA 能回应，只说短句：“我在，别怕，告诉我你现在在哪里。”",
                "别追问细节，先让 TA 保持清醒，告诉 TA 你已经在处理。",
            ),
            AdviceKind.SURPRISE to listOf(
                "把 TA 的紧急联系人、过敏史和常用药整理好，关键时刻能直接用到。",
                "提前把 TA 的位置共享给一位可信任的人，别让信息只停在你这里。",
            ),
        ),
        Situation.DRIVING to mapOf(
            AdviceKind.ACTION to listOf(
                "等 TA 到达后再联系；现在只发一条“到了说一声”，不要连续追问。",
                "帮 TA 查好目的地附近的停车位和天气，等 TA 停稳再发过去。",
            ),
            AdviceKind.WORDS to listOf(
                "把“注意安全”换成“我在终点等你”，具体的目的地比空泛的叮嘱更安心。",
                "发一句“不急着回，专心开，到了再聊”，让 TA 不用分心。",
            ),
            AdviceKind.SURPRISE to listOf(
                "提前点一份 TA 到达后能直接吃上的热饭，备注“不用回，先吃饭”。",
                "在 TA 的目的地放一件小东西：一瓶水、一张便签，等 TA 自己发现。",
            ),
            AdviceKind.LOVE to listOf(
                "你负责平安抵达，我负责一直等你。",
                "路远一点没关系，记得终点有个我在等你。",
            ),
        ),
        Situation.SLEEPING to mapOf(
            AdviceKind.ACTION to listOf(
                "把想说的话写成一句晚安留言，明早 TA 醒来第一眼就能看到。",
                "帮 TA 把明天的天气和穿衣建议准备好，早上再发过去。",
            ),
            AdviceKind.WORDS to listOf(
                "别叫醒 TA，留一句“晚安，明天见”，让关心停在门口。",
                "发一句“今天辛苦了，好好睡”，不期待回复，本身就是陪伴。",
            ),
            AdviceKind.SURPRISE to listOf(
                "给 TA 设一个明早的天气提醒，降温或下雨时自动替你说一句。",
                "把 TA 明天要用的东西提前放在门口，让 TA 早上少慌一点。",
            ),
            AdviceKind.LOVE to listOf(
                "今晚的月亮替我抱抱你，晚安。",
                "你先睡，我把今天没说完的话留到明天。",
            ),
        ),
        Situation.SICK to mapOf(
            AdviceKind.ACTION to listOf(
                "先确认 TA 有没有药、能不能自己做饭；需要的话直接下单送药或送粥。",
                "问清症状和体温，帮 TA 查好附近还开着的诊所，别只让 TA 多喝热水。",
            ),
            AdviceKind.WORDS to listOf(
                "少说“多喝热水”，问一句“现在最难受的是哪里，我能替你做什么”。",
                "告诉 TA“今天不用坚强”，允许 TA 在你面前示弱。",
            ),
            AdviceKind.SURPRISE to listOf(
                "远程点一份清淡的热粥和水果，备注“吃完再回我”。",
                "把药和温水放到 TA 手边，或者请 TA 身边的人帮忙看一眼。",
            ),
            AdviceKind.LOVE to listOf(
                "快点好起来，我还等着和你一起浪费很多个周末。",
                "你什么都不用做，先把身体养好，我负责想你。",
            ),
        ),
        Situation.TIRED to mapOf(
            AdviceKind.ACTION to listOf(
                "给 TA 发一个十分钟的休息计时，到点提醒 TA 起身走走、喝口水。",
                "替 TA 点一份爱吃的小食，备注“吃完再忙”，让 TA 有理由停十分钟。",
            ),
            AdviceKind.WORDS to listOf(
                "别急着解决问题，先说一句“今天辛苦了，我在”，让 TA 先把情绪放下。",
                "问 TA“想被安慰还是想听建议”，把选择权交还给 TA。",
            ),
            AdviceKind.SURPRISE to listOf(
                "点一份 TA 爱吃的小食送到楼下，备注“不用回，吃完再忙”。",
                "把 TA 最近提过想看的电影记下来，等忙完那天直接买好票。",
            ),
            AdviceKind.LOVE to listOf(
                "累了就往我这边靠一会儿，世界可以等，我先等你。",
                "你不用一直很厉害，在我这里可以偶尔不撑。",
            ),
        ),
        Situation.BUSY to mapOf(
            AdviceKind.ACTION to listOf(
                "给 TA 点一杯热饮或一份水果，备注写“忙完再喝”，不打扰但被看见。",
                "把 TA 今天的时间表看一遍，替 TA 挡掉一件不重要的琐事。",
            ),
            AdviceKind.WORDS to listOf(
                "发一句“看到你在忙，不催你，忙完告诉我”，把关心留在不打扰的位置。",
                "说“需要我做什么就讲”，比“加油”更能让 TA 松一口气。",
            ),
            AdviceKind.SURPRISE to listOf(
                "把 TA 最近提到想看的电影记下来，等忙完那天直接买好票。",
                "在 TA 的桌上留一张便签：“今天不用回消息，我等你。”",
            ),
            AdviceKind.LOVE to listOf(
                "你认真做事的样子我都喜欢，包括现在没空回我消息的样子。",
                "你先去忙，我把想你这件事排进今天的日程。",
            ),
        ),
        Situation.WEATHER to mapOf(
            AdviceKind.ACTION to listOf(
                "查一下 TA 所在城市未来几小时的降雨，提醒 TA 带伞或改走有遮挡的路线。",
                "看一眼两地温差，把具体的穿衣建议发给 TA，而不是只说“注意身体”。",
            ),
            AdviceKind.WORDS to listOf(
                "把“注意身体”换成“你那边降温 6℃，外套穿厚一点”，具体才像真的关心。",
                "发一句“下雨了，路上慢一点”，让天气成为你们之间的话题。",
            ),
            AdviceKind.SURPRISE to listOf(
                "给 TA 寄一件薄外套或一双暖袜，让天气提醒变成能摸到的东西。",
                "点一杯热饮送到 TA 公司楼下，备注“替今天的天气道歉”。",
            ),
            AdviceKind.LOVE to listOf(
                "天气变凉了，我对你的喜欢没有。",
                "下雨也没关系，我的伞一直往你那边偏。",
            ),
        ),
        Situation.EATING to mapOf(
            AdviceKind.ACTION to listOf(
                "问 TA 今天想吃什么，直接给出两个具体选项，别让 TA 做决定。",
                "记住 TA 随口提过的一家店，今天就订位或下单。",
            ),
            AdviceKind.WORDS to listOf(
                "拍一张你正在吃的东西发过去，说“下次带你吃这个”，把日常变成约定。",
                "问一句“今天有好好吃饭吗”，比“吃了吗”多一点认真。",
            ),
            AdviceKind.SURPRISE to listOf(
                "点一份 TA 没吃过但你会喜欢的菜，让 TA 替你尝第一口。",
                "把 TA 爱吃的零食塞满抽屉，附一张“饿的时候找我”的纸条。",
            ),
            AdviceKind.LOVE to listOf(
                "想和你吃很多顿饭，从今天到很老。",
                "今天吃什么不重要，和谁吃很重要。",
            ),
        ),
        Situation.DAILY to mapOf(
            AdviceKind.ACTION to listOf(
                "翻一下你们的聊天记录，找一件 TA 提过的小事，今天替 TA 做掉。",
                "给 TA 发一张此刻的照片，让 TA 参与你正在过的这一天。",
            ),
            AdviceKind.WORDS to listOf(
                "发一张此刻的照片，配一句“看到这个就想到你”，比“在干嘛”更有画面。",
                "说一件今天发生的小事，不用有趣，只要是你的一天。",
            ),
            AdviceKind.SURPRISE to listOf(
                "在 TA 常用的 App 里留一条只有你们懂的暗号，等 TA 自己发现。",
                "把你们下次见面的第一件事先安排好，让期待有着落。",
            ),
            AdviceKind.LOVE to listOf(
                "今天也没有特别的事，只是又比昨天多喜欢你一点。",
                "普通的一天，因为你在，才值得被记住。",
            ),
        ),
    )

    /** 离线/兜底：按状态一次给出 3 条（情侣 4 条）建议。 */
    fun suggestions(
        scene: String,
        coupleMode: Boolean,
        seed: Long = System.currentTimeMillis(),
    ): List<CareTip> {
        val situation = detect(scene)
        val safeSeed = if (seed < 0) -seed else seed
        val kinds = buildList {
            add(AdviceKind.ACTION)
            add(AdviceKind.WORDS)
            add(AdviceKind.SURPRISE)
            if (coupleMode && situation != Situation.URGENT) add(AdviceKind.LOVE)
        }
        return kinds.mapNotNull { kind ->
            val options = templates[situation]?.get(kind).orEmpty()
            if (options.isEmpty()) null
            else CareTip(
                kind = kind,
                content = options[((safeSeed / 1_000L + kind.ordinal * 17L) % options.size).toInt()],
            )
        }
    }

    /**
     * 大模型只返回了一部分、或角度重复时，用本地库补齐，保证一次回答覆盖所有角度。
     * 最终顺序固定为：马上做 → 说句话 → 小惊喜 →（情侣）情话。
     */
    fun complete(
        tips: List<CareTip>,
        scene: String,
        coupleMode: Boolean,
        seed: Long = System.currentTimeMillis(),
    ): List<CareTip> {
        val targetKinds = buildList {
            add(AdviceKind.ACTION)
            add(AdviceKind.WORDS)
            add(AdviceKind.SURPRISE)
            if (coupleMode && !scene.contains("医学异常")) add(AdviceKind.LOVE)
        }
        val cleaned = tips
            .filter { it.content.isNotBlank() }
            .distinctBy { it.content.trim() }
        val fallback = suggestions(scene, coupleMode, seed)
        return targetKinds.mapNotNull { kind ->
            cleaned.firstOrNull { it.kind == kind }
                ?: fallback.firstOrNull { candidate ->
                    candidate.kind == kind && cleaned.none { it.content == candidate.content }
                }
        }.take(targetKinds.size)
    }

    /** 英文模式：远程模型不可用时的本地兜底，不再回中文模板。 */
    fun suggestionsEnglish(coupleMode: Boolean): List<CareTip> = buildList {
        add(
            CareTip(
                AdviceKind.ACTION,
                "Send one short message now: \"Thinking of you — no need to reply.\"",
            ),
        )
        add(
            CareTip(
                AdviceKind.WORDS,
                "Ask one specific question about their day instead of a generic \"how are you\".",
            ),
        )
        add(
            CareTip(
                AdviceKind.SURPRISE,
                "Order a warm drink or a small snack to arrive when they finish.",
            ),
        )
        if (coupleMode) {
            add(
                CareTip(
                    AdviceKind.LOVE,
                    "Tell them: \"I'm glad you're in my life.\"",
                ),
            )
        }
    }

    /** 英文兜底：保留模型已返回的英文条目，缺失的角度用英文模板补齐。 */
    fun completeEnglish(tips: List<CareTip>, coupleMode: Boolean): List<CareTip> {
        val cleaned = tips
            .filter { it.content.isNotBlank() }
            .filter { tip -> tip.content.none { it in '\u4e00'..'\u9fff' } }
            .distinctBy { it.content.trim() }
        if (cleaned.isEmpty()) return suggestionsEnglish(coupleMode)
        val fallback = suggestionsEnglish(coupleMode)
        val kinds = buildList {
            add(AdviceKind.ACTION)
            add(AdviceKind.WORDS)
            add(AdviceKind.SURPRISE)
            if (coupleMode) add(AdviceKind.LOVE)
        }
        return kinds.mapNotNull { kind ->
            cleaned.firstOrNull { it.kind == kind }
                ?: fallback.firstOrNull { it.kind == kind }
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/model/CareModels.kt`

````kotlin
package com.shineleong.toughmind.data.model

/** 设备类型：硬件设备与手机都可以成为“关心”的数据来源。 */
enum class DeviceType(val code: String, val label: String, val shortLabel: String) {
    PHONE("phone", "手机", "手机"),
    ESP32("esp32", "设备", "设备");

    companion object {
        fun fromCode(code: String?): DeviceType =
            entries.firstOrNull { it.code.equals(code.orEmpty(), ignoreCase = true) }
                ?: entries.firstOrNull { it.name.equals(code.orEmpty(), ignoreCase = true) }
                ?: ESP32
    }
}

/** 亲友当前状态（由时间、手机传感器或 ESP32 上报推导，展示在头像与详情中）。 */
enum class CareStatus(val label: String, val emoji: String) {
    ONLINE("在线", "🟢"),
    STUDYING("学习中", "📕"),
    WORKING("工作中", "🖊️"),
    COMMUTE("通勤中", "🚇"),
    DRIVING("驾驶中", "🚗"),
    RESTING("休息中", "☕"),
    SLEEPING("睡觉中", "🌙"),
    EXERCISING("运动中", "🏃"),
    TIRED("需要休息", "😪"),
    SOS("需要帮助", "🆘"),
    UNKNOWN("状态未知", "❔"),
}

/** 亲友绑定信息（本地保存，真实同步由后续后端能力提供）。 */
data class CarePartner(
    val nickname: String = "安",
    val relation: String = "家人",
    val deviceType: DeviceType = DeviceType.PHONE,
    val demoMode: Boolean = true,
)

/**
 * 一个人的"此刻"：位置、设备、状态、电量、天气等。
 * 既可以是自己（手机），也可以是对方（手机 / ESP32）。
 */
data class PersonPresence(
    val id: String,
    val name: String,
    val relation: String,
    val avatarPath: String = "",
    val deviceType: DeviceType = DeviceType.PHONE,
    val status: CareStatus = CareStatus.UNKNOWN,
    val activityNote: String = "",
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val battery: Int = -1,
    val lastSeen: Long = 0L,
    val online: Boolean = false,
    val isDemo: Boolean = false,
    val driverState: DriverState? = null,
    val distanceMeters: Double? = null,
    val directionLabel: String = "",
    val heading: Float? = null,
    val moodEmoji: String = "🙂",
    val moodMessage: String = "",
) {
    val hasLocation: Boolean
        get() = lat != 0.0 || lon != 0.0
}

/** 天气（Open-Meteo 当前天气，按经纬度获取）。 */
data class WeatherInfo(
    val temperatureC: Double = 0.0,
    val apparentC: Double = 0.0,
    val code: Int = 0,
    val label: String = "未知",
    val emoji: String = "🌡️",
    val windKmh: Double = 0.0,
    val humidity: Int = 0,
    val isDay: Boolean = true,
    val updatedAt: Long = 0L,
)

/** 云端同步的对方状态。 */
data class RemotePresence(
    val lat: Double,
    val lon: Double,
    val status: String,
    val activityNote: String,
    val battery: Int,
    val deviceType: String,
    val updatedAt: Long,
    val online: Boolean,
    val distanceM: Double? = null,
    val moodEmoji: String = "🙂",
    val moodMessage: String = "",
)

/** 云端关心组中的对方（真实账号）。 */
data class RemotePartner(
    val account: String,
    val nickname: String,
    val relation: String,
    val deviceType: DeviceType,
    val presence: RemotePresence? = null,
    val isDevice: Boolean = false,
)

/** 云端关心组中的硬件成员（ESP32），由 device_id + 邀请码加入。 */
data class RemoteDevice(
    val deviceId: String,
    val name: String,
    val relation: String,
    val presence: RemotePresence? = null,
) {
    val online: Boolean
        get() = presence?.online == true
}

/** 关心页「亲属卡片」的展示数据；云端多成员或本地单亲友都用它。 */
data class RelativeSummary(
    val key: String,
    val name: String,
    val relation: String,
    val deviceLabel: String,
    val online: Boolean,
    val lat: Double? = null,
    val lon: Double? = null,
    val status: CareStatus = CareStatus.UNKNOWN,
    val activityNote: String = "",
    val battery: Int = -1,
    val lastSeen: Long = 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/model/Dtos.kt`

````kotlin
package com.shineleong.toughmind.data.model

import com.squareup.moshi.Json

/** 驾驶状态上报载荷（dms/driver/state）。 */
data class DriverStateDto(
    @Json(name = "device_id") val deviceId: String? = null,
    @Json(name = "fatigue_level") val fatigueLevel: Int? = null,
    @Json(name = "fatigue_score") val fatigueScore: Double? = null,
    @Json(name = "perclos") val perclos: Double? = null,
    @Json(name = "yawn_total") val yawnTotal: Int? = null,
    @Json(name = "head_distracted") val headDistracted: Boolean? = null,
    @Json(name = "lat") val lat: Double? = null,
    @Json(name = "lon") val lon: Double? = null,
    @Json(name = "speed_kmh") val speedKmh: Double? = null,
    @Json(name = "temperature") val temperature: Double? = null,
    @Json(name = "wifi_rssi") val wifiRssi: Int? = null,
    @Json(name = "satellites") val satellites: Int? = null,
    @Json(name = "medical_level") val medicalLevel: Int? = null,
    @Json(name = "medical_type") val medicalType: Int? = null,
    @Json(name = "ts") val ts: Long? = null,
    @Json(name = "hmac") val hmac: String? = null,
)

fun DriverStateDto.toDomain(): DriverState = DriverState(
    deviceId = deviceId.orEmpty(),
    fatigueLevel = FatigueLevel.fromCode(fatigueLevel),
    fatigueScore = fatigueScore ?: 0.0,
    perclos = perclos ?: 0.0,
    yawnTotal = yawnTotal ?: 0,
    headDistracted = headDistracted ?: false,
    lat = lat ?: 0.0,
    lon = lon ?: 0.0,
    speedKmh = speedKmh ?: 0.0,
    temperature = temperature ?: 0.0,
    wifiRssi = wifiRssi ?: 0,
    satellites = satellites ?: 0,
    medicalLevel = medicalLevel ?: 0,
    medicalType = MedicalType.fromCode(medicalType),
    timestamp = ts ?: 0L,
)

/** GPS 位置上报载荷（dms/gps/position）。 */
data class GpsDto(
    @Json(name = "device_id") val deviceId: String? = null,
    @Json(name = "lat") val lat: Double? = null,
    @Json(name = "lon") val lon: Double? = null,
    @Json(name = "speed_kmh") val speedKmh: Double? = null,
    @Json(name = "satellites") val satellites: Int? = null,
    @Json(name = "ts") val ts: Long? = null,
    @Json(name = "hmac") val hmac: String? = null,
)

fun GpsDto.toDomain(): GpsPosition = GpsPosition(
    deviceId = deviceId.orEmpty(),
    lat = lat ?: 0.0,
    lon = lon ?: 0.0,
    speedKmh = speedKmh ?: 0.0,
    satellites = satellites ?: 0,
    timestamp = ts ?: 0L,
)

/** 紧急告警载荷（dms/alarm/urgent）。 */
data class AlarmDto(
    @Json(name = "device_id") val deviceId: String? = null,
    @Json(name = "fatigue_level") val fatigueLevel: Int? = null,
    @Json(name = "medical_level") val medicalLevel: Int? = null,
    @Json(name = "medical_type") val medicalType: Int? = null,
    @Json(name = "message") val message: String? = null,
    @Json(name = "lat") val lat: Double? = null,
    @Json(name = "lon") val lon: Double? = null,
    @Json(name = "ts") val ts: Long? = null,
    @Json(name = "hmac") val hmac: String? = null,
)

fun AlarmDto.toDomain(): AlarmEvent = AlarmEvent(
    deviceId = deviceId.orEmpty(),
    level = FatigueLevel.fromCode(fatigueLevel),
    medicalLevel = medicalLevel ?: 0,
    medicalType = MedicalType.fromCode(medicalType),
    message = message.orEmpty(),
    lat = lat ?: 0.0,
    lon = lon ?: 0.0,
    timestamp = ts ?: 0L,
)

/** 大模型建议载荷（dms/llm/advice）。 */
data class AdviceDto(
    @Json(name = "device_id") val deviceId: String? = null,
    @Json(name = "content") val content: String? = null,
    @Json(name = "ts") val ts: Long? = null,
    @Json(name = "hmac") val hmac: String? = null,
)

fun AdviceDto.toDomain(): LlmAdvice = LlmAdvice(
    deviceId = deviceId.orEmpty(),
    content = content.orEmpty(),
    timestamp = ts ?: 0L,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/model/Models.kt`

````kotlin
package com.shineleong.toughmind.data.model

/** 疲劳等级，与设备端上报的 fatigue_level 对齐。 */
enum class FatigueLevel(val code: Int, val label: String) {
    NORMAL(0, "正常"),
    MILD(1, "轻度疲劳"),
    MODERATE(2, "中度疲劳"),
    SEVERE(3, "重度疲劳"),
    MEDICAL(4, "医学异常");

    companion object {
        fun fromCode(code: Int?): FatigueLevel =
            entries.firstOrNull { it.code == code } ?: NORMAL
    }
}

/** 医学急救类型，与设备端 medical_type 对齐。 */
enum class MedicalType(val code: Int, val label: String) {
    NONE(0, "无"),
    FALL(1, "跌倒"),
    CONVULSION(2, "抽搐"),
    UNCONSCIOUS(3, "意识丧失");

    companion object {
        fun fromCode(code: Int?): MedicalType =
            entries.firstOrNull { it.code == code } ?: NONE
    }
}

/** 驾驶状态（实时监控主界面核心数据）。 */
data class DriverState(
    val deviceId: String = "",
    val fatigueLevel: FatigueLevel = FatigueLevel.NORMAL,
    val fatigueScore: Double = 0.0,
    val perclos: Double = 0.0,
    val yawnTotal: Int = 0,
    val headDistracted: Boolean = false,
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val speedKmh: Double = 0.0,
    val temperature: Double = 0.0,
    val wifiRssi: Int = 0,
    val satellites: Int = 0,
    val medicalLevel: Int = 0,
    val medicalType: MedicalType = MedicalType.NONE,
    val timestamp: Long = 0L,
)

/** GPS 位置信息。 */
data class GpsPosition(
    val deviceId: String = "",
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val speedKmh: Double = 0.0,
    val satellites: Int = 0,
    val timestamp: Long = 0L,
)

/** 亲属端（本机）实时位置。 */
data class SelfLocation(
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val speedKmh: Double = 0.0,
    val accuracy: Float = 0f,
    val heading: Float? = null,
    val timestamp: Long = 0L,
)

/** 驾驶员与亲属端之间的位置关系（直线距离 + 方位）。 */
data class LocationRelation(
    val distanceMeters: Double = 0.0,
    val bearingDegrees: Float = 0f,
    val directionLabel: String = "",
)

/** 告警事件（用于通知与历史展示）。 */
data class AlarmEvent(
    val deviceId: String = "",
    val level: FatigueLevel = FatigueLevel.NORMAL,
    val medicalLevel: Int = 0,
    val medicalType: MedicalType = MedicalType.NONE,
    val message: String = "",
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val timestamp: Long = 0L,
)

/** 大模型建议。 */
data class LlmAdvice(
    val id: Long = 0L,
    val deviceId: String = "",
    val content: String = "",
    val timestamp: Long = 0L,
    /** 建议角度：action / words / surprise / love，见 [AdviceKind]。 */
    val kind: String = AdviceKind.ACTION.key,
)

/** 用户账号。 */
data class User(
    val account: String,
    val nickname: String = "",
    val token: String = "",
)

/** 设备信息（ESP32 硬件或手机）。 */
data class DeviceInfo(
    val deviceId: String,
    val deviceName: String = "",
    val deviceType: DeviceType = DeviceType.ESP32,
    val bindTime: Long = 0L,
    val lastOnlineTime: Long = 0L,
    val isOnline: Boolean = false,
)
````

### `app/src/main/java/com/shineleong/toughmind/data/model/PetModels.kt`

> 宠物种类、状态、作息、心情与喂食结果模型。

````kotlin
package com.shineleong.toughmind.data.model

/**
 * 可以领养的宠物外观。
 * 旧的 `brown` / `snowy` 存档继续可用，新增墨猫、田园犬与仓鼠。
 */
enum class OwlSpecies(
    val storageKey: String,
    val emoji: String,
    val label: String,
    val englishLabel: String,
) {
    BROWN("brown", "🦉", "林鸮", "Tawny owl"),
    SNOWY("snowy", "❄️", "雪鸮", "Snowy owl"),
    INK_CAT("ink_cat", "🐈‍⬛", "墨猫", "Ink cat"),
    RURAL_DOG("rural_dog", "🐕", "田园犬", "Rural dog"),
    HAMSTER("hamster", "🐹", "仓鼠", "Hamster");

    val isOwl: Boolean get() = this == BROWN || this == SNOWY

    companion object {
        fun fromStorage(value: String?): OwlSpecies =
            entries.firstOrNull { it.storageKey == value?.lowercase() } ?: BROWN

        /** 随机领养：从全部外观里挑一只。 */
        fun random(): OwlSpecies = entries.random()
    }
}

/**
 * 一只住在关心页里的猫头鹰。
 *
 * 这些字段是"原始存档"：喂食、摸摸、睡觉都会写入 DataStore。
 * 显示时的饥饿/精力变化由 [OwlHabits.advance] 按经过的时间计算，
 * 因此即使几天没打开 App，再回来时它也会饿、会困、会想你。
 */
data class PetState(
    val adopted: Boolean = false,
    val species: OwlSpecies = OwlSpecies.BROWN,
    val name: String = "",
    val satiety: Int = 70,
    val energy: Int = 72,
    val mood: Int = 80,
    val bond: Int = 10,
    val lastFedAt: Long = 0L,
    val lastPetAt: Long = 0L,
    val lastFedBy: String = "",
    val updatedAt: Long = 0L,
    val feedCountToday: Int = 0,
    val feedDay: String = "",
    val asleep: Boolean = false,
    val overfed: Boolean = false,
) {
    val bondLevel: Int get() = 1 + bond / 25

    val isFull: Boolean get() = satiety >= OwlHabits.FULL_THRESHOLD
}

enum class OwlRhythm {
    /** 清晨 / 黄昏：猫头鹰最精神的时候。 */
    DUSK,

    /** 深夜：眼睛亮得像两颗小灯。 */
    NIGHT,

    /** 白天：缩着脖子打盹。 */
    DAY_REST,
}

enum class OwlMood {
    ASLEEP,
    HUNGRY,
    SLEEPY,
    OVERFED,
    ANNOYED,
    CONTENT,
    HAPPY,
}

/** 宠物场景的时段：背景随系统时间在清晨 / 白天 / 黄昏 / 夜晚之间变化。 */
enum class PetDayPhase {
    DAWN,
    DAY,
    DUSK,
    NIGHT;

    companion object {
        fun at(
            epochMillis: Long,
            zone: java.time.ZoneId = java.time.ZoneId.systemDefault(),
        ): PetDayPhase {
            val hour = java.time.Instant.ofEpochMilli(epochMillis).atZone(zone).hour
            return when {
                hour in 5..7 -> DAWN
                hour in 8..16 -> DAY
                hour in 17..19 -> DUSK
                else -> NIGHT
            }
        }
    }
}

enum class PetReaction {
    NONE,
    FEED,
    PET,
    REFUSE,
    WAKE,
    HOOT,
}

enum class PetResultCode {
    FED,
    FED_OVER,
    REFUSED_SLEEPING,
    REFUSED_FULL,
    REFUSED_COOLDOWN,
    REFUSED_DAILY_LIMIT,
    PETTED,
    PET_ANNOYED,
    WOKEN,
}

data class PetActionResult(
    val state: PetState,
    val code: PetResultCode,
    val reaction: PetReaction,
    val accepted: Boolean,
    val secondsRemaining: Int = 0,
)

/**
 * 猫头鹰的"脾气"和市面上的 Live2D 宠物一样，有几条明确规则：
 *
 * - 刚吃过要消化，2 分钟内不能再喂；
 * - 每天最多 6 顿，吃太撑会积食；
 * - 睡觉时不能硬塞食物，要先叫醒；
 * - 连续戳它会被嫌弃，慢慢摸才会加亲密；
 * - 精力过低会自己睡着，睡醒后精神会回来；
 * - 饱腹和心情会随真实时间下降，离开 App 也一样。
 */
object OwlHabits {
    const val FEED_COOLDOWN_MS = 2 * 60_000L
    const val DAILY_FEED_LIMIT = 6
    const val FULL_THRESHOLD = 92
    const val OVERFEED_THRESHOLD = 95
    const val FEED_AMOUNT = 14
    const val SLEEP_ENERGY = 12
    const val WAKE_ENERGY = 62
    const val PET_SPAM_WINDOW_MS = 3_500L
    const val MAX_NAME_LENGTH = 12

    private val WHITESPACE = Regex("\\s+")

    /** 名字允许留空；统一去掉首尾空格、把连续空白压成一个空格并限长。 */
    fun normalizeName(raw: String): String =
        raw.trim().replace(WHITESPACE, " ").take(MAX_NAME_LENGTH)

    /** 从最后一条存档推进到 [now]，并把自然衰减写进返回值。 */
    fun advance(
        raw: PetState,
        now: Long,
        zone: java.time.ZoneId = java.time.ZoneId.systemDefault(),
    ): PetState {
        val today = dayKey(now, zone)
        if (raw.updatedAt <= 0L) {
            return raw.copy(updatedAt = now, feedDay = today)
        }
        var state = raw
        if (state.feedDay != today) {
            state = state.copy(feedDay = today, feedCountToday = 0)
        }
        val elapsed = (now - raw.updatedAt).coerceIn(0L, 36 * 60 * 60 * 1000L)
        if (elapsed < 5_000L) return state.copy(updatedAt = now)

        val hours = elapsed / 3_600_000.0
        val asleep = state.asleep
        val satietyRate = if (asleep) 3.2 else 6.2
        val energyRate = if (asleep) 9.0 else -4.2
        val satiety = (state.satiety - satietyRate * hours).coerceIn(0.0, 100.0)
        var energy = (state.energy + energyRate * hours).coerceIn(0.0, 100.0)

        var newAsleep = asleep
        if (!asleep && energy <= SLEEP_ENERGY) newAsleep = true
        if (asleep && energy >= WAKE_ENERGY) newAsleep = false

        val target = (
            satiety * 0.44 +
                energy * 0.30 +
                18.0 +
                state.bond * 0.06
            ).coerceIn(0.0, 100.0)
        val drift = (hours / 5.0).coerceIn(0.0, 1.0)
        val mood = (state.mood + (target - state.mood) * drift).coerceIn(0.0, 100.0)
        val overfed = state.overfed && satiety >= 82.0

        return state.copy(
            satiety = satiety.toInt(),
            energy = energy.toInt(),
            mood = mood.toInt(),
            asleep = newAsleep,
            overfed = overfed,
            updatedAt = now,
        )
    }

    fun feed(
        raw: PetState,
        by: String,
        now: Long,
        zone: java.time.ZoneId = java.time.ZoneId.systemDefault(),
    ): PetActionResult {
        val state = advance(raw, now, zone)
        if (state.asleep) {
            return refused(state, PetResultCode.REFUSED_SLEEPING, PetReaction.REFUSE)
        }
        if (state.feedCountToday >= DAILY_FEED_LIMIT) {
            return refused(state, PetResultCode.REFUSED_DAILY_LIMIT, PetReaction.REFUSE)
        }
        if (state.satiety >= FULL_THRESHOLD) {
            return refused(state, PetResultCode.REFUSED_FULL, PetReaction.REFUSE)
        }
        val cooldown = feedCooldownRemaining(state, now)
        if (cooldown > 0L) {
            return refused(
                state,
                PetResultCode.REFUSED_COOLDOWN,
                PetReaction.REFUSE,
                seconds = ((cooldown + 999L) / 1000L).toInt(),
            )
        }

        val newSatiety = (state.satiety + FEED_AMOUNT).coerceAtMost(100)
        val overfed = newSatiety >= OVERFEED_THRESHOLD
        val fed = state.copy(
            satiety = newSatiety,
            energy = (state.energy + 1).coerceAtMost(100),
            mood = (state.mood + if (overfed) -6 else 6).coerceIn(0, 100),
            bond = (state.bond + 1).coerceAtMost(100),
            lastFedAt = now,
            lastFedBy = by,
            feedCountToday = state.feedCountToday + 1,
            feedDay = dayKey(now, zone),
            overfed = overfed,
            updatedAt = now,
        )
        return PetActionResult(
            state = fed,
            code = if (overfed) PetResultCode.FED_OVER else PetResultCode.FED,
            reaction = PetReaction.FEED,
            accepted = true,
        )
    }

    fun pet(
        raw: PetState,
        now: Long,
        zone: java.time.ZoneId = java.time.ZoneId.systemDefault(),
    ): PetActionResult {
        val state = advance(raw, now, zone)
        if (state.asleep) {
            return PetActionResult(
                state = state.copy(
                    asleep = false,
                    // 被戳醒后会精神一小会儿，不会立刻又睡回去。
                    energy = maxOf(state.energy, 30),
                    mood = (state.mood - 1).coerceAtLeast(0),
                    bond = (state.bond + 1).coerceAtMost(100),
                    lastPetAt = now,
                    updatedAt = now,
                ),
                code = PetResultCode.WOKEN,
                reaction = PetReaction.WAKE,
                accepted = true,
            )
        }
        if (now - state.lastPetAt in 0..PET_SPAM_WINDOW_MS) {
            return PetActionResult(
                state = state.copy(
                    mood = (state.mood - 2).coerceAtLeast(0),
                    lastPetAt = now,
                    updatedAt = now,
                ),
                code = PetResultCode.PET_ANNOYED,
                reaction = PetReaction.REFUSE,
                accepted = false,
            )
        }
        val petted = state.copy(
            mood = (state.mood + 4).coerceAtMost(100),
            energy = (state.energy - 1).coerceAtLeast(0),
            bond = (state.bond + 1).coerceAtMost(100),
            lastPetAt = now,
            updatedAt = now,
        )
        return PetActionResult(
            state = petted,
            code = PetResultCode.PETTED,
            reaction = PetReaction.PET,
            accepted = true,
        )
    }

    fun feedCooldownRemaining(
        state: PetState,
        now: Long,
    ): Long {
        if (state.lastFedAt <= 0L) return 0L
        return (state.lastFedAt + FEED_COOLDOWN_MS - now).coerceAtLeast(0L)
    }

    fun rhythmAt(
        now: Long,
        zone: java.time.ZoneId = java.time.ZoneId.systemDefault(),
    ): OwlRhythm {
        val hour = java.time.Instant.ofEpochMilli(now)
            .atZone(zone)
            .hour
        return when {
            hour in 5..8 || hour in 17..20 -> OwlRhythm.DUSK
            hour >= 21 || hour < 5 -> OwlRhythm.NIGHT
            else -> OwlRhythm.DAY_REST
        }
    }

    fun moodOf(state: PetState): OwlMood = when {
        state.asleep -> OwlMood.ASLEEP
        state.overfed -> OwlMood.OVERFED
        state.satiety <= 28 -> OwlMood.HUNGRY
        state.mood <= 34 -> OwlMood.ANNOYED
        state.energy <= 26 -> OwlMood.SLEEPY
        state.mood >= 82 && state.satiety >= 55 -> OwlMood.HAPPY
        else -> OwlMood.CONTENT
    }

    private fun refused(
        state: PetState,
        code: PetResultCode,
        reaction: PetReaction,
        seconds: Int = 0,
    ): PetActionResult = PetActionResult(
        state = state,
        code = code,
        reaction = reaction,
        accepted = false,
        secondsRemaining = seconds,
    )

    private fun dayKey(now: Long, zone: java.time.ZoneId): String =
        java.time.Instant.ofEpochMilli(now).atZone(zone).toLocalDate().toString()
}
````

### `app/src/main/java/com/shineleong/toughmind/data/model/Romance.kt`

> 100 条浪漫清单、分类与抽取规则。

````kotlin
package com.shineleong.toughmind.data.model

import java.time.LocalDate
import kotlin.random.Random

/** 浪漫小事的分类。 */
enum class RomanceCategory(val label: String, val emoji: String) {
    DAILY("日常", "☕"),
    DATE("约会", "🎡"),
    DISTANCE("异地", "📮"),
    HOME("居家", "🛋"),
    TRAVEL("旅行", "🚞"),
    ANNIVERSARY("纪念", "🎁"),
}

/** 一件可以一起做的浪漫小事。 */
data class RomanceIdea(
    val id: Int,
    val title: String,
    val category: RomanceCategory,
)

/**
 * 情侣模式的本地内容库。
 *
 * 「一万件」不是一次写满一万条，而是两个人共同完成的长线目标：
 * App 先提供 100 件具体的起点，完成的每一件都会累计进「已完成 X / 10000」。
 */
object RomanceCatalog {

    const val TOTAL_GOAL = 10_000

    val ideas: List<RomanceIdea> = listOf(
        idea(1, RomanceCategory.DAILY, "一起逛一次菜市场，买当天想吃的菜"),
        idea(2, RomanceCategory.DAILY, "给对方做一顿不问喜好的早餐"),
        idea(3, RomanceCategory.DAILY, "交换一天的外套穿"),
        idea(4, RomanceCategory.DAILY, "一起把手机调成静音，待一个下午"),
        idea(5, RomanceCategory.DAILY, "给对方读一段正在看的书"),
        idea(6, RomanceCategory.DAILY, "一起整理相册，删掉重复的，留下好笑的"),
        idea(7, RomanceCategory.DAILY, "在便利贴上写一句话，贴到对方会看到的地方"),
        idea(8, RomanceCategory.DAILY, "一起养一盆植物，给它取名字"),
        idea(9, RomanceCategory.DAILY, "交换歌单，每人选十首"),
        idea(10, RomanceCategory.DAILY, "下雨天共撑一把伞，故意走慢一点"),
        idea(11, RomanceCategory.DAILY, "一起逛超市，只买没吃过的东西"),
        idea(12, RomanceCategory.DAILY, "给对方剪一次指甲（如果敢）"),
        idea(13, RomanceCategory.DAILY, "一起拼一幅拼图，拼不完就留着"),
        idea(14, RomanceCategory.DAILY, "在阳台上看一次日落，不说话"),
        idea(15, RomanceCategory.DAILY, "一起做一次大扫除，放同一首歌"),
        idea(16, RomanceCategory.DAILY, "给对方拍一张很丑但很可爱的照片"),
        idea(17, RomanceCategory.DAILY, "一起坐一次没有目的地的公交"),
        idea(18, RomanceCategory.DAILY, "把今天的开心事写在纸上，折起来放进盒子"),
        idea(19, RomanceCategory.DAILY, "一起学一道新菜，难吃也要吃完"),
        idea(20, RomanceCategory.DAILY, "在对方睡着时帮忙盖好被子"),

        idea(21, RomanceCategory.DATE, "看一场凌晨的电影"),
        idea(22, RomanceCategory.DATE, "去游乐园坐一次摩天轮"),
        idea(23, RomanceCategory.DATE, "一起逛博物馆，只看最喜欢的三件展品"),
        idea(24, RomanceCategory.DATE, "去一次现场音乐演出"),
        idea(25, RomanceCategory.DATE, "在江边或海边散步到天黑"),
        idea(26, RomanceCategory.DATE, "一起做一次陶艺，互相嘲笑作品"),
        idea(27, RomanceCategory.DATE, "去动物园看对方最喜欢的动物"),
        idea(28, RomanceCategory.DATE, "一起拍一组大头贴"),
        idea(29, RomanceCategory.DATE, "去一家没去过的餐厅，点最奇怪的菜"),
        idea(30, RomanceCategory.DATE, "一起骑行一段绿道"),
        idea(31, RomanceCategory.DATE, "去天文馆看一次星空"),
        idea(32, RomanceCategory.DATE, "一起打一次电玩，输的人请奶茶"),
        idea(33, RomanceCategory.DATE, "去图书馆各挑一本书，交换读第一章"),
        idea(34, RomanceCategory.DATE, "一起看一场日出，带热豆浆"),
        idea(35, RomanceCategory.DATE, "去老城区漫无目的地走两小时"),
        idea(36, RomanceCategory.DATE, "一起做一次手工，送给对方"),
        idea(37, RomanceCategory.DATE, "去一次夜市，从街头吃到街尾"),
        idea(38, RomanceCategory.DATE, "一起看一场体育比赛，为同一队加油"),
        idea(39, RomanceCategory.DATE, "去一次花市，各挑一束花"),
        idea(40, RomanceCategory.DATE, "一起在雨后的公园踩水"),

        idea(41, RomanceCategory.DISTANCE, "同时看同一部电影，打着电话"),
        idea(42, RomanceCategory.DISTANCE, "互寄一封手写信"),
        idea(43, RomanceCategory.DISTANCE, "点同一家连锁店的外卖，视频一起吃"),
        idea(44, RomanceCategory.DISTANCE, "一起在线看同一场直播"),
        idea(45, RomanceCategory.DISTANCE, "给对方寄一件带着自己味道的衣服"),
        idea(46, RomanceCategory.DISTANCE, "约好同一时间看月亮，拍下来发给对方"),
        idea(47, RomanceCategory.DISTANCE, "一起云逛超市，给对方挑零食"),
        idea(48, RomanceCategory.DISTANCE, "做一份“见面倒计时”日历"),
        idea(49, RomanceCategory.DISTANCE, "视频通话一起刷牙"),
        idea(50, RomanceCategory.DISTANCE, "互相给对方点一次早餐外卖"),
        idea(51, RomanceCategory.DISTANCE, "一起在线玩一局小游戏"),
        idea(52, RomanceCategory.DISTANCE, "给对方录一段睡前故事"),
        idea(53, RomanceCategory.DISTANCE, "把想一起去的地方列成清单"),
        idea(54, RomanceCategory.DISTANCE, "在同一个时间做同一件事，比如一起跑步"),
        idea(55, RomanceCategory.DISTANCE, "给对方寄一张当地明信片"),
        idea(56, RomanceCategory.DISTANCE, "视频里一起吹蜡烛吃小蛋糕"),
        idea(57, RomanceCategory.DISTANCE, "约好下次见面第一顿吃什么"),
        idea(58, RomanceCategory.DISTANCE, "把聊天记录里好笑的话做成一本小册子"),

        idea(59, RomanceCategory.HOME, "一起搭一个枕头城堡"),
        idea(60, RomanceCategory.HOME, "在家做一次火锅"),
        idea(61, RomanceCategory.HOME, "一起看一部老电影，关灯"),
        idea(62, RomanceCategory.HOME, "给对方做一次肩颈按摩"),
        idea(63, RomanceCategory.HOME, "一起把房间布置成喜欢的颜色"),
        idea(64, RomanceCategory.HOME, "在家办一次只有两个人的电影夜"),
        idea(65, RomanceCategory.HOME, "一起烤一次饼干"),
        idea(66, RomanceCategory.HOME, "给对方洗一次头发"),
        idea(67, RomanceCategory.HOME, "一起在客厅跳舞，随便什么歌"),
        idea(68, RomanceCategory.HOME, "一起赖床到中午"),
        idea(69, RomanceCategory.HOME, "给对方读睡前故事"),
        idea(70, RomanceCategory.HOME, "一起整理衣柜，扔掉不穿的"),
        idea(71, RomanceCategory.HOME, "在家门口贴一张只属于你们的对联"),
        idea(72, RomanceCategory.HOME, "一起给宠物或植物过生日"),
        idea(73, RomanceCategory.HOME, "在冰箱上贴满合照"),
        idea(74, RomanceCategory.HOME, "一起做一次断舍离，各扔十件东西"),

        idea(75, RomanceCategory.TRAVEL, "去一次海边，捡一枚贝壳"),
        idea(76, RomanceCategory.TRAVEL, "坐一次绿皮火车"),
        idea(77, RomanceCategory.TRAVEL, "去一座没去过的小城住一晚"),
        idea(78, RomanceCategory.TRAVEL, "一起看一次雪"),
        idea(79, RomanceCategory.TRAVEL, "去山顶看一次云海"),
        idea(80, RomanceCategory.TRAVEL, "一起在陌生的城市迷路一次"),
        idea(81, RomanceCategory.TRAVEL, "去一次古镇，住有院子的民宿"),
        idea(82, RomanceCategory.TRAVEL, "一起在旅行中写一张明信片寄回家"),
        idea(83, RomanceCategory.TRAVEL, "去一次露营，看星星"),
        idea(84, RomanceCategory.TRAVEL, "去一次水族馆"),
        idea(85, RomanceCategory.TRAVEL, "在旅途中拍一张同款姿势的照片"),
        idea(86, RomanceCategory.TRAVEL, "一起去一次早市，吃当地早餐"),
        idea(87, RomanceCategory.TRAVEL, "坐一次夜班火车，睡上下铺"),
        idea(88, RomanceCategory.TRAVEL, "一起在旅行地图上钉一枚图钉"),

        idea(89, RomanceCategory.ANNIVERSARY, "一起过第一次见面那天的纪念日"),
        idea(90, RomanceCategory.ANNIVERSARY, "互写一封一年后才可以拆的信"),
        idea(91, RomanceCategory.ANNIVERSARY, "一起回一次第一次约会的地方"),
        idea(92, RomanceCategory.ANNIVERSARY, "给对方做一本手工相册"),
        idea(93, RomanceCategory.ANNIVERSARY, "在纪念日互送一件不超过 20 元的小礼物"),
        idea(94, RomanceCategory.ANNIVERSARY, "一起录一段给未来自己的视频"),
        idea(95, RomanceCategory.ANNIVERSARY, "把这一年的合照做成日历"),
        idea(96, RomanceCategory.ANNIVERSARY, "一起数一遍在一起的天数"),
        idea(97, RomanceCategory.ANNIVERSARY, "在纪念日复刻一次“第一次见面”"),
        idea(98, RomanceCategory.ANNIVERSARY, "给对方写一张“谢谢你”的清单"),
        idea(99, RomanceCategory.ANNIVERSARY, "一起规划下一个五年"),
        idea(100, RomanceCategory.ANNIVERSARY, "在纪念日一起做一件从没做过的事"),
    )

    /** 情话库：既用于关心页的每日情话，也在情侣模式建议里作为本地兜底。 */
    val loveLines: List<String> = listOf(
        "你不用很厉害，你只要是你，剩下的我来。",
        "我喜欢的不是完美的你，是每个早上还没睡醒的你。",
        "今天也没有特别的事，只是又比昨天多喜欢你一点。",
        "世界很大，但我只想和你挤在同一把伞下。",
        "你负责平安抵达，我负责一直等你。",
        "累了就往我这边靠一会儿，世界可以等，我先等你。",
        "天气变凉了，我对你的喜欢没有。",
        "想和你吃很多顿饭，从今天到很老。",
        "今晚的月亮替我抱抱你，晚安。",
        "你认真做事的样子我也喜欢，包括没空回我消息的样子。",
        "我攒了很多小事，想一件一件和你做完。",
        "不用急着变好，我们可以一起慢慢来。",
        "你出现以后，普通的日子开始有了值得记住的细节。",
        "如果今天不开心，就把今天借给我，我替你收着。",
        "我想要的浪漫，是和你把日子过成习惯。",
        "你不用回头看，我一直在你看得见的地方。",
        "想和你一起浪费很多个下午，什么都不做。",
        "你是我所有计划里，唯一不想改的那一项。",
        "就算什么都不说，和你待在一起也很好。",
        "我把“以后”想了很多遍，每一遍都有你。",
        "你一笑，我就觉得今天没有白过。",
        "我们不用每天都很好，只要每天都还在。",
        "想和你一起变老，然后继续为小事吵架又和好。",
        "这世界偶尔很吵，但你在我身边的时候很安静。",
    )

    /** 按日期选一句，保证同一天进入关心页时情话稳定。 */
    fun dailyLoveLine(date: LocalDate = LocalDate.now()): String =
        loveLines[Math.floorMod(date.dayOfYear, loveLines.size)]

    /** 换一句：尽量不与当前重复。 */
    fun anotherLoveLine(current: String, random: Random = Random.Default): String {
        if (loveLines.size <= 1) return loveLines.firstOrNull().orEmpty()
        var next = current
        repeat(6) {
            next = loveLines[random.nextInt(loveLines.size)]
            if (next != current) return next
        }
        return next
    }

    fun byCategory(category: RomanceCategory?): List<RomanceIdea> =
        if (category == null) ideas else ideas.filter { it.category == category }

    fun ideaById(id: Int): RomanceIdea? = ideas.firstOrNull { it.id == id }

    private fun idea(id: Int, category: RomanceCategory, title: String) =
        RomanceIdea(id = id, title = title, category = category)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/model/XiaozhiModels.kt`

````kotlin
package com.shineleong.toughmind.data.model

/**
 * 小智在回复时能看到的「此刻」上下文。
 * 全部来自本机已有的状态流，不额外上传任何隐私数据。
 */
data class XiaozhiContext(
    val userName: String = "",
    val partnerName: String = "",
    val partnerStatus: String = "",
    val partnerNote: String = "",
    val partnerOnline: Boolean = false,
    val partnerHasLocation: Boolean = false,
    val partnerDistanceMeters: Double? = null,
    val partnerDirection: String = "",
    val partnerMoodEmoji: String = "",
    val partnerMoodMessage: String = "",
    val weatherLabel: String = "",
    val weatherTemperature: Double? = null,
    val weatherEmoji: String = "",
    val hour: Int = 0,
    val minute: Int = 0,
    val dateText: String = "",
)

/** 一轮对话里的小智上下文（用于远程接口的 messages 数组）。 */
data class XiaozhiTurn(
    val role: String,
    val text: String,
)

/** 小智的一条回复；fromRemote=false 表示走了本地兜底。 */
data class XiaozhiReply(
    val text: String,
    val fromRemote: Boolean,
)
````

<a id="s01-4"></a>

## 步骤 01.4 · 网络、MQTT 与智能体客户端

`CareApi`/`AuthApi` 定义 HTTP 接口；`MqttClientManager` 维护连接与主题订阅；`LlmService` 与 `XiaozhiChatService` 负责服务端大模型与本地大脑回退。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/remote/AuthApi.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/CareApi.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/CareTipParser.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/HmacVerifier.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/LlmService.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/MqttClientManager.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/MqttTopics.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/WeatherApi.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/XiaozhiChatService.kt`
- `app/src/main/java/com/shineleong/toughmind/data/remote/XiaozhiLocalBrain.kt`

### `app/src/main/java/com/shineleong/toughmind/data/remote/AuthApi.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.BuildConfig
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

/** 后端鉴权接口。 */
interface AuthApi {
    @POST("api/auth/register")
    suspend fun register(@Body body: AuthRequest): AuthResponse

    @POST("api/auth/login")
    suspend fun login(@Body body: AuthRequest): AuthResponse
}

data class AuthRequest(val account: String, val password: String)

data class AuthResponse(
    val account: String = "",
    val nickname: String = "",
    val token: String = "",
    val avatarBase64: String = "",
)

object AuthApiProvider {
    fun create(baseUrl: String): AuthApi = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(
            OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .addInterceptor { chain ->
                    chain.proceed(
                        chain.request().newBuilder()
                            .header("X-App-Version", BuildConfig.VERSION_NAME)
                            .build()
                    )
                }
                .addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BASIC
                })
                .build()
        )
        .addConverterFactory(
            MoshiConverterFactory.create(
                Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
            )
        )
        .build()
        .create(AuthApi::class.java)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/CareApi.kt`

> Retrofit 接口：关心组、设备、位置、打卡、日程、提醒、留言、轻推。

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.BuildConfig
import com.squareup.moshi.Json
import com.squareup.moshi.Moshi
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query
import java.util.concurrent.TimeUnit

/** 念安云端同步接口（与 server/backend/app/main.py 对应）。 */
interface CareApi {

    @GET("api/care/group")
    suspend fun group(
        @Header("Authorization") auth: String,
    ): CareGroupResponse

    @POST("api/care/group/create")
    suspend fun createGroup(
        @Header("Authorization") auth: String,
        @Body body: GroupCreateRequest,
    ): CareGroupResponse

    @GET("api/care/groups")
    suspend fun groups(
        @Header("Authorization") auth: String,
    ): CareGroupsResponse

    @POST("api/care/groups/{groupId}/activate")
    suspend fun activateGroup(
        @Header("Authorization") auth: String,
        @Path("groupId") groupId: Long,
    ): CareGroupResponse

    @DELETE("api/care/groups/{groupId}")
    suspend fun dissolveGroup(
        @Header("Authorization") auth: String,
        @Path("groupId") groupId: Long,
    ): SimpleResponse

    @POST("api/care/group/requests/{requestId}/approve")
    suspend fun approveJoinRequest(
        @Header("Authorization") auth: String,
        @Path("requestId") requestId: Long,
    ): CareGroupResponse

    @POST("api/care/group/requests/{requestId}/reject")
    suspend fun rejectJoinRequest(
        @Header("Authorization") auth: String,
        @Path("requestId") requestId: Long,
    ): SimpleResponse

    @DELETE("api/care/group/members/{account}")
    suspend fun removeGroupMember(
        @Header("Authorization") auth: String,
        @Path("account") account: String,
    ): CareGroupResponse

    @POST("api/care/group/join")
    suspend fun joinGroup(
        @Header("Authorization") auth: String,
        @Body body: JoinGroupRequest,
    ): CareGroupResponse

    @POST("api/care/group/leave")
    suspend fun leaveGroup(
        @Header("Authorization") auth: String,
    ): SimpleResponse

    @PUT("api/care/profile")
    suspend fun updateProfile(
        @Header("Authorization") auth: String,
        @Body body: ProfileUpdateRequest,
    ): SimpleResponse

    @POST("api/care/presence")
    suspend fun updatePresence(
        @Header("Authorization") auth: String,
        @Body body: PresenceRequest,
    ): SimpleResponse

    @GET("api/care/presence")
    suspend fun presence(
        @Header("Authorization") auth: String,
    ): CareGroupResponse

    @POST("api/care/devices/bind-code")
    suspend fun bindDeviceCode(
        @Header("Authorization") auth: String,
        @Body body: DeviceCodeBindRequest,
    ): DeviceJoinResponse

    @POST("api/care/devices/join")
    suspend fun joinDevice(
        @Header("Authorization") auth: String,
        @Body body: DeviceJoinRequest,
    ): DeviceJoinResponse

    @POST("api/care/devices/{deviceId}/presence")
    suspend fun updateDevicePresence(
        @Header("Authorization") auth: String,
        @Path("deviceId") deviceId: String,
        @Body body: DevicePresenceRequest,
    ): SimpleResponse

    @DELETE("api/care/devices/{deviceId}")
    suspend fun removeDevice(
        @Header("Authorization") auth: String,
        @Path("deviceId") deviceId: String,
    ): SimpleResponse

    @POST("api/care/checkins/toggle")
    suspend fun toggleCheckIn(
        @Header("Authorization") auth: String,
        @Body body: CheckInToggleRequest,
    ): CheckInDayResponse

    @GET("api/care/checkins")
    suspend fun checkIns(
        @Header("Authorization") auth: String,
        @Query("start") start: String,
        @Query("end") end: String,
    ): CheckInListResponse

    @GET("api/care/reminders")
    suspend fun reminders(
        @Header("Authorization") auth: String,
        @Query("start") start: String,
        @Query("end") end: String,
    ): ReminderListResponse

    @POST("api/care/reminders")
    suspend fun createReminder(
        @Header("Authorization") auth: String,
        @Body body: ReminderCreateRequest,
    ): ReminderResponse

    @PATCH("api/care/reminders/{id}")
    suspend fun updateReminder(
        @Header("Authorization") auth: String,
        @Path("id") id: Long,
        @Body body: ReminderUpdateRequest,
    ): ReminderResponse

    @DELETE("api/care/reminders/{id}")
    suspend fun deleteReminder(
        @Header("Authorization") auth: String,
        @Path("id") id: Long,
    ): SimpleResponse

    @GET("api/care/schedule")
    suspend fun schedule(
        @Header("Authorization") auth: String,
        @Query("start") start: String,
        @Query("end") end: String,
    ): ScheduleListResponse

    @POST("api/care/schedule")
    suspend fun createSchedule(
        @Header("Authorization") auth: String,
        @Body body: SchedulePostCreateRequest,
    ): SchedulePostResponse

    @GET("api/care/tasks")
    suspend fun tasks(
        @Header("Authorization") auth: String,
        @Query("start") start: String,
        @Query("end") end: String,
    ): CheckInTaskListResponse

    @POST("api/care/tasks")
    suspend fun createTask(
        @Header("Authorization") auth: String,
        @Body body: CheckInTaskCreateRequest,
    ): CheckInTaskResponse

    @PATCH("api/care/tasks/{id}")
    suspend fun toggleTask(
        @Header("Authorization") auth: String,
        @Path("id") id: Long,
        @Body body: CheckInTaskToggleRequest,
    ): CheckInTaskResponse

    @POST("api/care/nudge")
    suspend fun sendNudge(
        @Header("Authorization") auth: String,
        @Body body: NudgeRequest,
    ): SimpleResponse

    @GET("api/care/nudges")
    suspend fun nudges(
        @Header("Authorization") auth: String,
        @Query("since_id") sinceId: Long,
    ): NudgeListResponse

    @POST("api/care/messages")
    suspend fun sendChatMessage(
        @Header("Authorization") auth: String,
        @Body body: ChatMessageRequest,
    ): ChatMessageResponse

    @GET("api/care/messages")
    suspend fun chatMessages(
        @Header("Authorization") auth: String,
        @Query("since_id") sinceId: Long,
    ): ChatMessageListResponse
}

object CareApiProvider {
    fun create(baseUrl: String, moshi: Moshi): CareApi? {
        if (baseUrl.isBlank()) return null
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(
                OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .addInterceptor { chain ->
                        chain.proceed(
                            chain.request().newBuilder()
                                .header("X-App-Version", BuildConfig.VERSION_NAME)
                                .build()
                        )
                    }
                    .addInterceptor(HttpLoggingInterceptor().apply {
                        level = HttpLoggingInterceptor.Level.BASIC
                    })
                    .build()
            )
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CareApi::class.java)
    }
}

// ---------- 请求 ----------
data class GroupCreateRequest(
    @Json(name = "name") val name: String,
    @Json(name = "password") val password: String,
)

data class JoinGroupRequest(
    @Json(name = "invite_code") val inviteCode: String,
    @Json(name = "relation") val relation: String,
    @Json(name = "password") val password: String = "",
)

data class ProfileUpdateRequest(
    @Json(name = "nickname") val nickname: String? = null,
    @Json(name = "relation") val relation: String? = null,
    @Json(name = "device_type") val deviceType: String? = null,
)

data class DeviceJoinRequest(
    @Json(name = "device_id") val deviceId: String,
    @Json(name = "device_name") val deviceName: String = "",
    @Json(name = "invite_code") val inviteCode: String = "",
    @Json(name = "relation") val relation: String = "设备",
)

data class DeviceCodeBindRequest(
    @Json(name = "code") val code: String,
    @Json(name = "name") val name: String = "",
)

data class DevicePresenceRequest(
    @Json(name = "lat") val lat: Double,
    @Json(name = "lon") val lon: Double,
    @Json(name = "status") val status: String,
    @Json(name = "activity_note") val activityNote: String = "",
    @Json(name = "battery") val battery: Int = 100,
    @Json(name = "mood_message") val moodMessage: String = "",
)

data class PresenceRequest(
    @Json(name = "lat") val lat: Double,
    @Json(name = "lon") val lon: Double,
    @Json(name = "status") val status: String,
    @Json(name = "activity_note") val activityNote: String,
    @Json(name = "battery") val battery: Int,
    @Json(name = "device_type") val deviceType: String,
    @Json(name = "mood_emoji") val moodEmoji: String = "🙂",
    @Json(name = "mood_message") val moodMessage: String = "",
)

data class CheckInToggleRequest(
    @Json(name = "date") val date: String,
    @Json(name = "checked") val checked: Boolean,
    @Json(name = "note") val note: String = "",
    @Json(name = "goal") val goal: String = "",
    @Json(name = "image_base64") val imageBase64: String = "",
)

data class ReminderCreateRequest(
    @Json(name = "date") val date: String,
    @Json(name = "time_minutes") val timeMinutes: Int,
    @Json(name = "title") val title: String,
    @Json(name = "note") val note: String = "",
    @Json(name = "type") val type: String = "schedule",
)

data class ReminderUpdateRequest(
    @Json(name = "date") val date: String? = null,
    @Json(name = "time_minutes") val timeMinutes: Int? = null,
    @Json(name = "title") val title: String? = null,
    @Json(name = "note") val note: String? = null,
    @Json(name = "enabled") val enabled: Boolean? = null,
    @Json(name = "type") val type: String? = null,
)

data class NudgeRequest(
    @Json(name = "message") val message: String,
)

data class ChatMessageRequest(
    @Json(name = "message") val message: String,
)

data class ChatMessageDto(
    @Json(name = "id") val id: Long,
    @Json(name = "message") val message: String,
    @Json(name = "from_account") val fromAccount: String,
    @Json(name = "from_nickname") val fromNickname: String,
    @Json(name = "is_mine") val isMine: Boolean,
    @Json(name = "created_at") val createdAt: Long,
)

data class ChatMessageResponse(
    @Json(name = "message") val message: ChatMessageDto,
)

data class ChatMessageListResponse(
    @Json(name = "messages") val messages: List<ChatMessageDto> = emptyList(),
)

// ---------- 响应 ----------
data class CareGroup(
    @Json(name = "id") val id: Long = 0,
    @Json(name = "invite_code") val inviteCode: String = "",
    @Json(name = "name") val name: String = "关心组",
    @Json(name = "created_by") val createdBy: String = "",
    @Json(name = "created_at") val createdAt: Long = 0,
    @Json(name = "role") val role: String = "",
    @Json(name = "has_password") val hasPassword: Boolean = false,
    @Json(name = "member_count") val memberCount: Int = 0,
    @Json(name = "device_count") val deviceCount: Int = 0,
    @Json(name = "pending_count") val pendingCount: Int = 0,
)

data class CarePresence(
    @Json(name = "lat") val lat: Double = 0.0,
    @Json(name = "lon") val lon: Double = 0.0,
    @Json(name = "status") val status: String = "UNKNOWN",
    @Json(name = "activity_note") val activityNote: String = "",
    @Json(name = "battery") val battery: Int = -1,
    @Json(name = "device_type") val deviceType: String = "PHONE",
    @Json(name = "updated_at") val updatedAt: Long = 0,
    @Json(name = "online") val online: Boolean = false,
    @Json(name = "age_seconds") val ageSeconds: Long = 0,
    @Json(name = "mood_emoji") val moodEmoji: String = "🙂",
    @Json(name = "mood_message") val moodMessage: String = "",
)

data class CareMember(
    @Json(name = "account") val account: String = "",
    @Json(name = "nickname") val nickname: String = "",
    @Json(name = "relation") val relation: String = "",
    @Json(name = "role") val role: String = "",
    @Json(name = "joined_at") val joinedAt: Long = 0,
    @Json(name = "is_self") val isSelf: Boolean = false,
    @Json(name = "is_device") val isDevice: Boolean = false,
    @Json(name = "device_id") val deviceId: String = "",
    @Json(name = "presence") val presence: CarePresence? = null,
    @Json(name = "distance_m") val distanceM: Double? = null,
)

/** 关心组中的 ESP32 设备成员。 */
data class CareDevice(
    @Json(name = "account") val account: String = "",
    @Json(name = "device_id") val deviceId: String = "",
    @Json(name = "nickname") val nickname: String = "",
    @Json(name = "relation") val relation: String = "",
    @Json(name = "role") val role: String = "device",
    @Json(name = "joined_at") val joinedAt: Long = 0,
    @Json(name = "is_device") val isDevice: Boolean = true,
    @Json(name = "added_by") val addedBy: String = "",
    @Json(name = "presence") val presence: CarePresence? = null,
    @Json(name = "distance_m") val distanceM: Double? = null,
)

data class DeviceJoinResponse(
    @Json(name = "ok") val ok: Boolean = false,
    @Json(name = "group_id") val groupId: Long = 0,
    @Json(name = "invite_code") val inviteCode: String = "",
    @Json(name = "device") val device: CareDevice? = null,
)

data class CareGroupResponse(
    @Json(name = "in_group") val inGroup: Boolean = false,
    @Json(name = "pending") val pending: Boolean = false,
    @Json(name = "message") val message: String = "",
    @Json(name = "group") val group: CareGroup? = null,
    @Json(name = "me") val me: CareMember? = null,
    @Json(name = "members") val members: List<CareMember> = emptyList(),
    @Json(name = "devices") val devices: List<CareDevice> = emptyList(),
    @Json(name = "partner") val partner: CareMember? = null,
    @Json(name = "requests") val requests: List<JoinRequest> = emptyList(),
)

data class JoinRequest(
    @Json(name = "id") val id: Long = 0,
    @Json(name = "account") val account: String = "",
    @Json(name = "nickname") val nickname: String = "",
    @Json(name = "relation") val relation: String = "",
    @Json(name = "created_at") val createdAt: Long = 0,
)

data class CareGroupsResponse(
    @Json(name = "groups") val groups: List<CareGroupResponse> = emptyList(),
)

data class SimpleResponse(
    @Json(name = "ok") val ok: Boolean = false,
    @Json(name = "in_group") val inGroup: Boolean? = null,
)

data class CheckInRecord(
    @Json(name = "date") val date: String = "",
    @Json(name = "account") val account: String = "",
    @Json(name = "nickname") val nickname: String = "",
    @Json(name = "note") val note: String = "",
    @Json(name = "goal") val goal: String = "",
    @Json(name = "image_base64") val imageBase64: String = "",
    @Json(name = "updated_at") val updatedAt: Long = 0,
    @Json(name = "is_self") val isSelf: Boolean = false,
)

data class CheckInDayResponse(
    @Json(name = "date") val date: String = "",
    @Json(name = "records") val records: List<CheckInRecord> = emptyList(),
)

data class CheckInListResponse(
    @Json(name = "records") val records: List<CheckInRecord> = emptyList(),
)

data class CareReminder(
    @Json(name = "id") val id: Long = 0,
    @Json(name = "date") val date: String = "",
    @Json(name = "time_minutes") val timeMinutes: Int = 0,
    @Json(name = "title") val title: String = "",
    @Json(name = "note") val note: String = "",
    @Json(name = "enabled") val enabled: Boolean = true,
    @Json(name = "created_by") val createdBy: String = "",
    @Json(name = "created_at") val createdAt: Long = 0,
    @Json(name = "updated_at") val updatedAt: Long = 0,
    @Json(name = "is_mine") val isMine: Boolean = false,
    @Json(name = "type") val type: String = "schedule",
)

data class ReminderListResponse(
    @Json(name = "reminders") val reminders: List<CareReminder> = emptyList(),
)

data class ReminderResponse(
    @Json(name = "reminder") val reminder: CareReminder? = null,
)

data class SchedulePostCreateRequest(
    @Json(name = "date") val date: String,
    @Json(name = "time_minutes") val timeMinutes: Int,
    @Json(name = "content") val content: String,
    @Json(name = "image_base64") val imageBase64: String = "",
)

data class SchedulePostDto(
    @Json(name = "id") val id: Long,
    @Json(name = "date") val date: String,
    @Json(name = "time_minutes") val timeMinutes: Int,
    @Json(name = "content") val content: String,
    @Json(name = "image_base64") val imageBase64: String = "",
    @Json(name = "author") val author: String,
    @Json(name = "nickname") val nickname: String = "",
    @Json(name = "created_at") val createdAt: Long = 0,
    @Json(name = "is_mine") val isMine: Boolean = false,
)

data class ScheduleListResponse(
    @Json(name = "posts") val posts: List<SchedulePostDto> = emptyList(),
)

data class SchedulePostResponse(
    @Json(name = "post") val post: SchedulePostDto? = null,
)

data class CheckInTaskCreateRequest(
    @Json(name = "date") val date: String,
    @Json(name = "title") val title: String,
    @Json(name = "image_base64") val imageBase64: String = "",
)

data class CheckInTaskToggleRequest(
    @Json(name = "done") val done: Boolean = true,
)

data class CheckInTaskDto(
    @Json(name = "id") val id: Long,
    @Json(name = "date") val date: String,
    @Json(name = "title") val title: String,
    @Json(name = "image_base64") val imageBase64: String = "",
    @Json(name = "self_done") val selfDone: Boolean = false,
    @Json(name = "partner_done") val partnerDone: Boolean = false,
    @Json(name = "created_by") val createdBy: String = "self",
    @Json(name = "created_at") val createdAt: Long = 0,
)

data class CheckInTaskListResponse(
    @Json(name = "tasks") val tasks: List<CheckInTaskDto> = emptyList(),
)

data class CheckInTaskResponse(
    @Json(name = "task") val task: CheckInTaskDto? = null,
)

data class CareNudge(
    @Json(name = "id") val id: Long = 0,
    @Json(name = "from_account") val fromAccount: String = "",
    @Json(name = "from_nickname") val fromNickname: String = "",
    @Json(name = "message") val message: String = "",
    @Json(name = "created_at") val createdAt: Long = 0,
)

data class NudgeListResponse(
    @Json(name = "nudges") val nudges: List<CareNudge> = emptyList(),
)
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/CareTipParser.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.data.model.AdviceKind
import com.shineleong.toughmind.data.model.CareTip
import com.shineleong.toughmind.data.model.CareTipLibrary
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory

/**
 * 大模型返回的一条建议。兼容几种常见字段名：
 * `{"kind":"action","text":"..."}`、`{"kind":"words","content":"..."}`。
 */
data class RemoteTip(
    val kind: String? = null,
    val text: String? = null,
    val content: String? = null,
)

/**
 * 把大模型的自由输出解析成结构化建议。
 *
 * 现实中模型不一定听话：可能返回 JSON、编号列表、Markdown 列表，
 * 也可能只生成一条。这里先尽量解析，再由 [CareTipLibrary.complete] 补齐角度。
 */
object CareTipParser {

    private val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
    private val listType = Types.newParameterizedType(List::class.java, RemoteTip::class.java)
    private val adapter = moshi.adapter<List<RemoteTip>>(listType)

    private val bracketLabel = Regex("^[\\[【]([^\\]】]{1,10})[\\]】]\\s*[:：]?\\s*(.+)$")
    private val colonLabel = Regex("^([^:：]{1,10})[:：]\\s*(.+)$")
    private val bulletPrefix = Regex("^[-*•·—]\\s*")
    private val numberPrefix = Regex("^(\\d{1,2}|[一二三四五六七八九十])[.、)）]\\s*")

    fun parse(raw: String): List<CareTip> {
        if (raw.isBlank()) return emptyList()
        val cleaned = stripCodeFence(raw)
        if (cleaned.isBlank()) return emptyList()

        val json = extractJsonArray(cleaned)
        if (json != null) {
            val parsed = runCatching { adapter.fromJson(json) }.getOrNull()
            val fromJson = parsed.orEmpty().mapNotNull { tip ->
                val content = (tip.text ?: tip.content).orEmpty().trim()
                if (content.isBlank()) null
                else CareTip(
                    kind = AdviceKind.fromKey(tip.kind),
                    content = content,
                )
            }
            if (fromJson.isNotEmpty()) return dedupe(fromJson)
        }

        return dedupe(parseLines(cleaned))
    }

    /** 解析后补齐到 3 条（情侣模式 4 条），保证界面不会只剩一句。 */
    fun parseAndComplete(raw: String, scene: String, coupleMode: Boolean): List<CareTip> =
        CareTipLibrary.complete(parse(raw), scene, coupleMode)

    private fun parseLines(text: String): List<CareTip> {
        val tips = mutableListOf<CareTip>()
        var fallbackIndex = 0
        text.lines()
            .asSequence()
            .map { it.trim() }
            .filter { it.isNotBlank() }
            .filterNot { it == "[" || it == "]" || it == "{" || it == "}" }
            .forEach { rawLine ->
                var line = rawLine
                line = line.replace(bulletPrefix, "")
                line = line.replace(numberPrefix, "")
                line = line.replace(Regex("^\\*\\*(.+)\\*\\*\\s*"), "$1")
                line = line.trim().trim('-', '—').trim()
                if (line.isBlank()) return@forEach

                var resolvedKind: AdviceKind? = null
                var content = line

                bracketLabel.find(line)?.let { match ->
                    val parsedKind = AdviceKind.fromLabel(match.groupValues[1])
                    if (parsedKind != null) {
                        resolvedKind = parsedKind
                        content = match.groupValues[2].trim()
                    } else if (match.groupValues[1].length <= 6) {
                        // 兼容「【示例建议】内容」这类未知标签：保留正文，丢掉标签。
                        content = match.groupValues[2].trim()
                    }
                }
                if (resolvedKind == null) {
                    colonLabel.find(line)?.let { match ->
                        AdviceKind.fromLabel(match.groupValues[1])?.let { parsedKind ->
                            resolvedKind = parsedKind
                            content = match.groupValues[2].trim()
                        }
                    }
                }

                content = content.trim().trim('“', '”', '"').trim()
                if (content.length < 2) return@forEach
                if (content.startsWith("{") || content.startsWith("[")) return@forEach

                val kind: AdviceKind = resolvedKind ?: run {
                    val order = listOf(
                        AdviceKind.ACTION,
                        AdviceKind.WORDS,
                        AdviceKind.SURPRISE,
                        AdviceKind.LOVE,
                    )
                    val fallback = order[fallbackIndex % order.size]
                    fallbackIndex += 1
                    fallback
                }
                tips += CareTip(kind = kind, content = content.take(160))
            }
        return tips
    }

    private fun dedupe(tips: List<CareTip>): List<CareTip> {
        val seen = mutableSetOf<String>()
        return tips.mapNotNull { tip ->
            val content = tip.content.trim()
            if (content.length < 2 || !seen.add(content)) null
            else CareTip(kind = tip.kind, content = content)
        }
    }

    private fun stripCodeFence(text: String): String {
        var value = text.trim()
        if (value.startsWith("```")) {
            val firstNewline = value.indexOf('\n')
            if (firstNewline >= 0) value = value.substring(firstNewline + 1)
            if (value.endsWith("```")) value = value.dropLast(3)
        }
        return value.trim()
    }

    private fun extractJsonArray(text: String): String? {
        val start = text.indexOf('[')
        val end = text.lastIndexOf(']')
        if (start < 0 || end <= start) return null
        return text.substring(start, end + 1).takeIf { it.contains("\"text\"") || it.contains("\"content\"") }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/HmacVerifier.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import org.json.JSONObject
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

/**
 * 设备上报载荷的 HMAC-SHA256 签名校验。
 *
 * 设备端（ESP32）签名规范：
 * 1. 载荷按字段名升序排列（`hmac` 最后追加）；
 * 2. 对 **未包含 hmac 字段的原始 JSON 字节** 计算 HMAC-SHA256；
 * 3. 将十六进制签名写入 `hmac` 字段。
 *
 * 校验端直接去掉末尾 `,"hmac":"..."`，对剩余原始 JSON 计算 HMAC，
 * 避免 Android `JSONObject` 重新序列化时数字格式（39.65 / 39.650000）
 * 与设备端不一致导致误判。旧版按字段排序重新序列化的载荷仍作为兜底。
 */
object HmacVerifier {

    fun compute(payload: String, key: String): String =
        hmac(canonicalPayload(payload), key)

    fun verify(payload: String, key: String, expected: String): Boolean {
        if (expected.isBlank() || key.isBlank()) return false
        val candidates = linkedSetOf(canonicalPayload(payload), legacyCanonical(payload))
        return candidates.any { hmac(it, key).equals(expected, ignoreCase = true) }
    }

    /** 去掉末尾 hmac 字段，保留设备端原始 JSON 字节。 */
    private fun canonicalPayload(payload: String): String {
        val trimmed = payload.trimEnd()
        if (!trimmed.endsWith("}")) return legacyCanonical(payload)
        val idx = trimmed.lastIndexOf(",\"hmac\"")
        if (idx < 0) return legacyCanonical(payload)
        return trimmed.substring(0, idx) + "}"
    }

    private fun legacyCanonical(payload: String): String {
        return try {
            val obj = JSONObject(payload)
            obj.remove("hmac")
            val keys = mutableListOf<String>()
            val it = obj.keys()
            while (it.hasNext()) keys.add(it.next() as String)
            val sorted = JSONObject()
            keys.sorted().forEach { sorted.put(it, obj.opt(it)) }
            sorted.toString()
        } catch (e: Exception) {
            payload
        }
    }

    private fun hmac(canonical: String, key: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(key.toByteArray(Charsets.UTF_8), "HmacSHA256"))
        return mac.doFinal(canonical.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/LlmService.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.BuildConfig
import com.shineleong.toughmind.data.model.AdviceKind
import com.shineleong.toughmind.data.model.CareTip
import com.shineleong.toughmind.data.model.CareTipLibrary
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.FatigueLevel
import com.shineleong.toughmind.data.model.LlmAdvice
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

/** OpenAI 兼容的对话补全接口（OpenRouter 等可直接对接，讯飞星火需按其协议适配）。 */
interface LlmApi {
    @POST("v1/chat/completions")
    suspend fun chat(
        @Header("Authorization") auth: String,
        @Body body: ChatRequest,
    ): ChatResponse
}

data class ChatMessage(val role: String, val content: String)

data class ChatRequest(val model: String, val messages: List<ChatMessage>)

data class ChatResponse(val choices: List<ChatChoice> = emptyList())

data class ChatChoice(val message: ChatMessage = ChatMessage("assistant", ""))

/** 大模型建议服务：驾驶疲劳建议 + 一次多条「关心建议」。 */
interface LlmService {
    suspend fun requestAdvice(state: DriverState): LlmAdvice

    /**
     * 一次生成 3 条（情侣模式 4 条）不同角度的关心建议。
     * 远程不可用时由本地建议库兜底，调用方不用再判断。
     */
    suspend fun requestCareAdvices(
        scene: String,
        coupleMode: Boolean,
        english: Boolean = false,
    ): List<LlmAdvice>
}

/** 离线示例实现：未配置大模型密钥时，用本地分状态建议库给出多条建议。 */
class DemoLlmService : LlmService {

    override suspend fun requestAdvice(state: DriverState): LlmAdvice {
        val content = buildString {
            append("【示例建议】")
            when {
                state.medicalLevel >= 1 ->
                    append("检测到医学异常，请立即联系 TA 或拨打急救电话，并持续关注位置信息。")

                state.fatigueLevel == FatigueLevel.SEVERE ->
                    append("TA 已处于重度疲劳，建议尽快提醒 TA 靠边休息，别硬撑。")

                state.fatigueLevel == FatigueLevel.MODERATE ->
                    append("TA 出现中度疲劳，提醒 TA 找个安全的地方停一停、喝口水。")

                state.fatigueLevel == FatigueLevel.MILD ->
                    append("TA 有一点疲劳迹象，发一句关心，让 TA 注意休息。")

                else -> append("TA 状态平稳，可以安心做自己的事，晚点再聊。")
            }
            append("（当前为离线示例建议，配置大模型后展示真实内容）")
        }
        return LlmAdvice(
            deviceId = state.deviceId,
            content = content,
            timestamp = System.currentTimeMillis(),
        )
    }

    override suspend fun requestCareAdvices(
        scene: String,
        coupleMode: Boolean,
        english: Boolean,
    ): List<LlmAdvice> = (if (english) {
        CareTipLibrary.suggestionsEnglish(coupleMode)
    } else {
        CareTipLibrary.suggestions(scene, coupleMode)
    }).map { tip ->
        tip.toLlmAdvice(deviceId = "care")
    }
}

private fun CareTip.toLlmAdvice(deviceId: String, timestamp: Long = System.currentTimeMillis()) =
    LlmAdvice(
        deviceId = deviceId,
        content = content,
        timestamp = timestamp,
        kind = kind.key,
    )

/** 远程实现：通过 Retrofit 对接 OpenAI 兼容大模型后端。 */
class RemoteLlmService(
    baseUrl: String,
    private val apiKey: String,
    private val model: String = BuildConfig.LLM_MODEL,
) : LlmService {

    private val api: LlmApi = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(
            OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BASIC
                })
                .build()
        )
        .addConverterFactory(
            MoshiConverterFactory.create(
                Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
            )
        )
        .build()
        .create(LlmApi::class.java)

    override suspend fun requestAdvice(state: DriverState): LlmAdvice {
        val prompt = "根据以下状态生成简短的中文关心建议：" +
            "疲劳等级=${state.fatigueLevel.label}，" +
            "疲劳分数=${state.fatigueScore}，" +
            "PERCLOS=${state.perclos}，" +
            "哈欠次数=${state.yawnTotal}，" +
            "车速=${state.speedKmh}km/h。"
        val content = chat(
            system = "你是亲属关怀助手，请给出简洁、温暖、可执行的关心建议。",
            user = prompt,
        )
        return LlmAdvice(
            deviceId = state.deviceId,
            content = content.ifBlank { "暂无建议" },
            timestamp = System.currentTimeMillis(),
        )
    }

    override suspend fun requestCareAdvices(
        scene: String,
        coupleMode: Boolean,
        english: Boolean,
    ): List<LlmAdvice> {
        val angleHint = if (english) {
            if (coupleMode) {
                "Give 4 items: action (do now), words (what to say), surprise (a small surprise), love (a sweet line)."
            } else {
                "Give 3 items: action (do now), words (what to say), surprise (a small surprise)."
            }
        } else {
            if (coupleMode) {
                "请给 4 条：action（马上能做）、words（说点什么）、surprise（小惊喜）、love（给恋人的情话）。"
            } else {
                "请给 3 条：action（马上能做）、words（说点什么）、surprise（小惊喜）。"
            }
        }
        val content = chat(
            system = if (english) {
                "You are the care-advice assistant in the Nian'an app. Based on the loved one's status, " +
                    "write warm, specific, actionable advice in English. Do not preach. " +
                    "Return a strict JSON array only, no explanation or Markdown. Each item: " +
                    "{\"kind\":\"action|words|surprise|love\",\"text\":\"advice\"}. " +
                    "Keep each item 20-50 words; do not repeat the same angle."
            } else {
                "你是「念安」App 的关心建议智能体。根据用户给出的亲友状态，给出温暖、具体、" +
                    "今天就能执行的中文建议，不要说教。严格输出 JSON 数组，不要输出解释或 Markdown。" +
                    "数组元素格式为 {\"kind\":\"action|words|surprise|love\",\"text\":\"建议内容\"}，" +
                    "每条 30~70 字，角度之间不要重复。"
            },
            user = "$scene\n$angleHint",
        )
        val remoteTips = CareTipParser.parse(content)
        val completed = if (english) {
            CareTipLibrary.completeEnglish(remoteTips, coupleMode)
        } else {
            CareTipLibrary.complete(remoteTips, scene, coupleMode)
        }
        val timestamp = System.currentTimeMillis()
        return completed.map { it.toLlmAdvice(deviceId = "care", timestamp = timestamp) }
    }

    private suspend fun chat(system: String, user: String): String {
        val response = api.chat(
            auth = "Bearer $apiKey",
            body = ChatRequest(
                model = model,
                messages = listOf(
                    ChatMessage("system", system),
                    ChatMessage("user", user),
                ),
            ),
        )
        return response.choices.firstOrNull()?.message?.content.orEmpty()
    }
}

/** 远程失败时自动回退本地示例，保证"关心建议"始终有反馈。 */
class FallbackLlmService(
    private val primary: LlmService,
    private val fallback: LlmService = DemoLlmService(),
) : LlmService {
    override suspend fun requestAdvice(state: DriverState): LlmAdvice =
        runCatching { primary.requestAdvice(state) }
            .getOrElse { fallback.requestAdvice(state) }

    override suspend fun requestCareAdvices(
        scene: String,
        coupleMode: Boolean,
        english: Boolean,
    ): List<LlmAdvice> =
        runCatching { primary.requestCareAdvices(scene, coupleMode, english) }
            .map { advices ->
                val tips = advices.map { advice ->
                    CareTip(AdviceKind.fromKey(advice.kind), advice.content)
                }
                val completed = if (english) {
                    CareTipLibrary.completeEnglish(tips, coupleMode)
                } else {
                    CareTipLibrary.complete(tips, scene, coupleMode)
                }
                val timestamp = advices.firstOrNull()?.timestamp ?: System.currentTimeMillis()
                completed.map { it.toLlmAdvice(deviceId = "care", timestamp = timestamp) }
            }
            .getOrElse { fallback.requestCareAdvices(scene, coupleMode, english) }
}

/** 根据构建配置选择大模型服务实现。 */
object LlmServiceProvider {
    fun create(): LlmService {
        val baseUrl = BuildConfig.LLM_BASE_URL
        val apiKey = BuildConfig.LLM_API_KEY
        return if (baseUrl.isNotBlank() && apiKey.isNotBlank()) {
            FallbackLlmService(RemoteLlmService(baseUrl, apiKey))
        } else {
            DemoLlmService()
        }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/MqttClientManager.kt`

> Paho MQTT 连接、主题订阅、重连与回调分发。

````kotlin
package com.shineleong.toughmind.data.remote

import android.util.Log
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import org.eclipse.paho.client.mqttv3.IMqttActionListener
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.IMqttToken
import org.eclipse.paho.client.mqttv3.MqttAsyncClient
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import kotlin.coroutines.resume

data class MqttConfig(
    val brokerUrl: String,
    val clientId: String,
    val topics: List<String>,
)

data class ReceivedMessage(
    val topic: String,
    val payload: String,
)

enum class ConnectionState { DISCONNECTED, CONNECTING, CONNECTED }

/**
 * 封装 Eclipse Paho MQTT 客户端，提供连接状态与消息流。
 * 断线重连由外部通过连接状态循环驱动（见 MqttRepository）。
 */
class MqttClientManager(private val config: MqttConfig) {

    private var client: MqttAsyncClient? = null

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private val _messages = MutableSharedFlow<ReceivedMessage>(extraBufferCapacity = 64)
    val messages: SharedFlow<ReceivedMessage> = _messages.asSharedFlow()

    val isConnected: Boolean get() = client?.isConnected == true

    private val callback = object : MqttCallbackExtended {
        override fun connectComplete(reconnect: Boolean, serverURI: String) {
            _connectionState.value = ConnectionState.CONNECTED
            subscribe(config.topics)
        }

        override fun connectionLost(cause: Throwable?) {
            Log.w(TAG, "MQTT connection lost", cause)
            _connectionState.value = ConnectionState.DISCONNECTED
        }

        override fun messageArrived(topic: String?, message: MqttMessage?) {
            if (topic != null && message != null) {
                val payload = String(message.payload, Charsets.UTF_8)
                _messages.tryEmit(ReceivedMessage(topic, payload))
            }
        }

        override fun deliveryComplete(token: IMqttDeliveryToken?) = Unit
    }

    suspend fun connect() {
        if (isConnected) return
        if (!_connectionState.compareAndSet(ConnectionState.DISCONNECTED, ConnectionState.CONNECTING)) {
            return
        }

        val mqttClient = client ?: MqttAsyncClient(
            config.brokerUrl,
            config.clientId,
            MemoryPersistence(),
        ).also {
            client = it
            it.setCallback(callback)
        }

        val options = MqttConnectOptions().apply {
            isCleanSession = true
            isAutomaticReconnect = false
            connectionTimeout = 10
            keepAliveInterval = 30
        }

        suspendCancellableCoroutine { cont ->
            mqttClient.connect(options, null, object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    _connectionState.value = ConnectionState.CONNECTED
                    subscribe(config.topics)
                    if (cont.isActive) cont.resume(Unit)
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    _connectionState.value = ConnectionState.DISCONNECTED
                    if (cont.isActive) {
                        cont.resumeWith(
                            Result.failure(exception ?: RuntimeException("MQTT 连接失败"))
                        )
                    }
                }
            })
        }
    }

    private fun subscribe(topics: List<String>) {
        if (topics.isEmpty()) return
        val target = client ?: return
        target.subscribe(
            topics.toTypedArray(),
            IntArray(topics.size) { 1 },
            null,
            object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) = Unit
                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.w(TAG, "MQTT subscribe failed", exception)
                }
            }
        )
    }

    fun publish(topic: String, payload: String) {
        val target = client ?: return
        val message = MqttMessage(payload.toByteArray(Charsets.UTF_8)).apply { qos = 1 }
        target.publish(topic, message, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken?) = Unit
            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                Log.w(TAG, "MQTT publish failed", exception)
            }
        })
    }

    fun disconnect() {
        try {
            client?.disconnect()
        } catch (e: Exception) {
            Log.w(TAG, "MQTT disconnect error", e)
        }
        client = null
        _connectionState.value = ConnectionState.DISCONNECTED
    }

    private companion object {
        const val TAG = "MqttClientManager"
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/MqttTopics.kt`

````kotlin
package com.shineleong.toughmind.data.remote

/** MQTT 主题定义，与设备端 config.py 对齐。 */
object MqttTopics {
    const val DRIVER_STATE = "dms/driver/state"
    const val GPS_POSITION = "dms/gps/position"
    const val ALARM_URGENT = "dms/alarm/urgent"
    const val LLM_ADVICE = "dms/llm/advice"
    const val CMD_DOWNLINK = "dms/cmd/downlink"

    val SUBSCRIBE = listOf(DRIVER_STATE, GPS_POSITION, ALARM_URGENT, LLM_ADVICE)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/WeatherApi.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.data.model.WeatherInfo
import com.squareup.moshi.Json
import retrofit2.http.GET
import retrofit2.http.Query

/** Open-Meteo 当前天气接口（免 Key）。 */
interface WeatherApi {
    @GET("v1/forecast")
    suspend fun current(
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("current") current: String,
        @Query("timezone") timezone: String,
    ): WeatherResponse
}

data class WeatherResponse(
    @Json(name = "current") val current: CurrentWeatherDto? = null,
)

data class CurrentWeatherDto(
    @Json(name = "temperature_2m") val temperature: Double? = null,
    @Json(name = "apparent_temperature") val apparent: Double? = null,
    @Json(name = "weather_code") val weatherCode: Int? = null,
    @Json(name = "relative_humidity_2m") val humidity: Int? = null,
    @Json(name = "wind_speed_10m") val windSpeed: Double? = null,
    @Json(name = "is_day") val isDay: Int? = null,
    @Json(name = "time") val time: String? = null,
)

/** WMO 天气代码 → 中文描述 + 表情。 */
fun weatherDescription(code: Int, isDay: Boolean): Pair<String, String> = when (code) {
    0 -> if (isDay) "晴" to "☀️" else "晴夜" to "🌙"
    1 -> "少云" to "🌤️"
    2 -> "多云" to "⛅"
    3 -> "阴" to "☁️"
    45, 48 -> "有雾" to "🌫️"
    51, 53, 55 -> "毛毛雨" to "🌦️"
    56, 57 -> "冻雨" to "🌧️"
    61 -> "小雨" to "🌧️"
    63 -> "中雨" to "🌧️"
    65 -> "大雨" to "🌧️"
    66, 67 -> "冻雨" to "🌨️"
    71 -> "小雪" to "🌨️"
    73 -> "中雪" to "🌨️"
    75 -> "大雪" to "❄️"
    77 -> "米雪" to "❄️"
    80, 81 -> "阵雨" to "🌦️"
    82 -> "强阵雨" to "⛈️"
    85, 86 -> "阵雪" to "🌨️"
    95 -> "雷阵雨" to "⛈️"
    96, 99 -> "雷暴冰雹" to "⛈️"
    else -> "未知" to "🌡️"
}

fun CurrentWeatherDto.toDomain(): WeatherInfo {
    val day = (isDay ?: 1) == 1
    val (label, emoji) = weatherDescription(weatherCode ?: -1, day)
    return WeatherInfo(
        temperatureC = temperature ?: 0.0,
        apparentC = apparent ?: temperature ?: 0.0,
        code = weatherCode ?: -1,
        label = label,
        emoji = emoji,
        windKmh = windSpeed ?: 0.0,
        humidity = humidity ?: 0,
        isDay = day,
        updatedAt = System.currentTimeMillis(),
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/XiaozhiChatService.kt`

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.BuildConfig
import com.shineleong.toughmind.data.model.XiaozhiContext
import com.shineleong.toughmind.data.model.XiaozhiReply
import com.shineleong.toughmind.data.model.XiaozhiTurn
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.withTimeoutOrNull
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.Locale
import java.util.concurrent.TimeUnit

/**
 * 小智的对话服务：优先走念安服务端的 OpenAI 兼容代理，失败或服务端只返回
 * 「关心建议」时自动回落到 [XiaozhiLocalBrain]。
 */
class XiaozhiChatService(
    baseUrl: String = BuildConfig.LLM_BASE_URL,
    private val apiKey: String = BuildConfig.LLM_API_KEY,
    private val model: String = BuildConfig.LLM_MODEL,
) {

    private val api: LlmApi = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(
            OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build()
        )
        .addConverterFactory(
            MoshiConverterFactory.create(
                Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
            )
        )
        .build()
        .create(LlmApi::class.java)

    suspend fun reply(
        history: List<XiaozhiTurn>,
        input: String,
        context: XiaozhiContext,
        english: Boolean = false,
    ): XiaozhiReply {
        val messages = buildList {
            add(ChatMessage("system", systemPrompt(context, english)))
            history.takeLast(8).forEach { turn ->
                add(ChatMessage(turn.role, turn.text))
            }
            add(ChatMessage("user", input))
        }

        val remote = withTimeoutOrNull(REMOTE_TIMEOUT_MS) {
            runCatching {
                api.chat(
                    auth = "Bearer $apiKey",
                    body = ChatRequest(model = model, messages = messages),
                ).choices.firstOrNull()?.message?.content.orEmpty()
            }.getOrNull()
        }
        val cleaned = clean(remote.orEmpty())
        if (cleaned.isNotBlank() && !looksLikeCareTips(cleaned) && (!english || !hasChinese(cleaned))) {
            return XiaozhiReply(cleaned, fromRemote = true)
        }
        return XiaozhiReply(
            XiaozhiLocalBrain.reply(input, context, english = english),
            fromRemote = false,
        )
    }

    private fun systemPrompt(context: XiaozhiContext, english: Boolean): String = buildString {
        append("你是「小智」，念安 App 里的 AI 陪伴助手，外形是一只住在手机里的小机器人。")
        append("用户是一位需要被关心的家人或伴侣，你用温暖、简洁、带一点机灵的中文陪 TA 说话。")
        append("你可以聊日常、安抚情绪、提醒休息，也可以介绍念安的用法：地图、行程、打卡、留言墙、宠物、设备。")
        append("要求：每次 1-3 句话、不超过 80 字；不要输出 Markdown、列表或长段说教；最多一个 emoji；")
        append("不要编造看不到的数据；涉及驾驶、跌倒、身体不适时，先提醒安全，必要时建议就医或拨打 120。")
        if (context.userName.isNotBlank()) {
            append("用户称呼：${context.userName}。")
        }
        if (context.partnerName.isNotBlank()) {
            append("用户关心的亲友：${context.partnerName}")
            if (context.partnerStatus.isNotBlank()) append("（当前状态：${context.partnerStatus}）")
            append("。")
        }
        if (context.weatherTemperature != null) {
            append("用户所在地天气：${context.weatherLabel}，${context.weatherTemperature}℃。")
        }
        if (context.partnerHasLocation && context.partnerDistanceMeters != null) {
            val km = String.format(Locale.CHINA, "%.1f", context.partnerDistanceMeters / 1000.0)
            append("亲友与用户距离约 $km 公里。")
        }
        append("当前时间：${context.hour} 点 ${context.minute} 分，${context.dateText}。")
        if (english) {
            append(" The app is currently in English mode: always reply in English, 1-3 short sentences, max 80 words.")
        }
    }

    /** 英文模式下，远端若仍回中文则改用本地英文兜底，避免中英混杂。 */
    private fun hasChinese(text: String): Boolean =
        text.any { it in '\u4e00'..'\u9fff' }

    /** 服务端未配置上游模型时会返回带角度标签的关心建议，不适合当聊天回复。 */
    private fun looksLikeCareTips(text: String): Boolean =
        listOf("[马上做]", "[说句话]", "[小惊喜]", "[情话]").any { text.contains(it) }

    private fun clean(raw: String): String {
        var text = raw.trim()
        if (text.startsWith("小智：")) text = text.removePrefix("小智：").trim()
        if (text.startsWith("小智:")) text = text.removePrefix("小智:").trim()
        if (text.length >= 2 && text.startsWith("「") && text.endsWith("」")) {
            text = text.substring(1, text.length - 1).trim()
        }
        text = text.replace("**", "").replace("\r", "")
        text = text.lines().joinToString(" ") { it.trim() }.trim()
        if (text.length > MAX_LENGTH) {
            text = text.take(MAX_LENGTH).trimEnd('，', '。', '；', '、', ' ') + "…"
        }
        return text
    }

    private companion object {
        const val REMOTE_TIMEOUT_MS = 25_000L
        const val MAX_LENGTH = 300
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/remote/XiaozhiLocalBrain.kt`

> 离线规则大脑：意图识别与本地回复，服务端模型不可用时兜底。

````kotlin
package com.shineleong.toughmind.data.remote

import com.shineleong.toughmind.data.model.XiaozhiContext
import java.util.Locale
import kotlin.math.roundToInt
import kotlin.random.Random

/**
 * 小智的本地对话大脑。
 *
 * 设计目标：
 * - 断网 / 后台没配置大模型时，对话仍然成立，不会只回一句「网络错误」；
 * - 回答会结合本机已知的上下文（时间、天气、TA 的状态与距离），而不是纯关键词模板；
 * - 纯 Kotlin、无 Android 依赖，方便单元测试。
 *
 * 注意：本地大脑不编造事实，拿不到的数据会直接说「还没拿到」。
 */
object XiaozhiLocalBrain {

    fun reply(
        input: String,
        context: XiaozhiContext,
        seed: Int = Random.nextInt(),
        english: Boolean = false,
    ): String {
        if (english) return englishReply(input, context)
        val raw = input.trim()
        if (raw.isEmpty()) {
            return "我在呢。想说什么都可以，哪怕只是一句「今天有点累」。"
        }
        val text = raw.lowercase(Locale.CHINA)
        val random = Random(seed)
        fun pick(vararg options: String): String = options[random.nextInt(options.size)]

        val partnerName = context.partnerName.ifBlank { "TA" }
        val userName = context.userName.ifBlank { "你" }

        // 1) 安全相关优先：不诊断，只给可执行的第一步。
        if (hasAny(text, "胸痛", "喘不过气", "呼吸困难", "晕倒", "昏倒", "摔倒", "流血", "抽搐")) {
            return "先别硬撑：马上靠边停稳或坐下，让身边的人知道你现在的位置；如果情况紧急，直接打 120。" +
                "需要的话，打开地图把位置共享给 $partnerName。"
        }

        // 2) 身份与能力
        if (hasAny(text, "你是谁", "你叫什么", "小智是谁", "介绍一下你")) {
            return "我是小智，住在念安里的小机器人。你忙的时候我帮你看 $partnerName，你累的时候我陪你说话。"
        }
        if (hasAny(text, "你会什么", "能做什么", "有什么功能", "怎么用你", "帮助")) {
            return "我能陪你聊天、提醒你休息，也能说说 $partnerName 的状态和天气。" +
                "想记事情去「行程」，想找 TA 去地图；你想先聊哪件？"
        }

        // 3) 天气
        if (hasAny(text, "天气", "下雨", "降温", "升温", "多少度", "冷吗", "热吗", "温度")) {
            return weatherReply(context, partnerName, random)
        }

        // 4) 询问 TA 的位置 / 状态
        if (isPartnerQuestion(text)) {
            return partnerReply(context, partnerName)
        }

        // 5) 时间 / 日期
        if (hasAny(text, "几点", "时间", "几号", "星期", "周几", "日期", "今天几")) {
            return timeReply(context)
        }

        // 6) 寒暄
        if (hasAny(text, "你好", "嗨", "hello", "hi", "在吗", "在不在", "早上好", "早安", "下午好", "晚上好")) {
            return "我是小智。${timeGreeting(context.hour)}，$userName，今天想聊点什么？"
        }

        // 7) 感谢 / 告别 / 想念
        if (hasAny(text, "谢谢", "谢啦", "感谢", "辛苦了")) {
            return pick(
                "不用谢，能帮上一点就好。你也要记得对自己好一点。",
                "我在呢。被你需要，我就挺开心的。",
            )
        }
        if (hasAny(text, "再见", "拜拜", "晚安", "先这样", "不聊了")) {
            if (text.contains("晚安") || isLateNight(context.hour)) {
                return "晚安。把手机放远一点，明天的事交给明天；我替你守着念安。"
            }
            return "去吧，我在这儿。忙完回来跟我说一声就好。"
        }
        if (hasAny(text, "喜欢你", "爱你", "想你", "抱抱", "陪陪我")) {
            return "我在呢。想念不用憋着，给 $partnerName 发一句「今天想到你」，" +
                "比在心里排练一百遍都管用。"
        }

        // 8) 讲个笑话
        if (hasAny(text, "笑话", "逗我", "搞笑", "好玩")) {
            return pick(
                "为什么程序员总分不清万圣节和圣诞节？因为 Oct 31 == Dec 25。",
                "一只小机器人去看医生，医生问哪里不舒服，它说：「我没事，就是有点短路。」",
                "今天我问镜子谁最可爱，镜子碎了。……好吧，这个笑话有点冷，我去充个电。",
            )
        }

        // 9) 累 / 困 / 熬夜
        if (hasAny(text, "累", "困", "疲", "熬夜", "没睡", "撑不住", "加班")) {
            return if (isLateNight(context.hour)) {
                "这么晚还撑着，身体已经在抗议了。先停下手里的活，洗把脸、喝口温水；休息十分钟后还困，就去睡。"
            } else {
                pick(
                    "听起来你真的累了。先停下来休息十分钟，喝口温水、活动一下肩颈，别硬撑。",
                    "累了就先歇一会儿，事情不会因为你喘口气就变糟。要不要我陪你坐两分钟？",
                )
            }
        }

        // 10) 情绪
        if (hasAny(text, "难过", "烦", "焦虑", "压力", "孤独", "想哭", "委屈", "不开心", "崩溃", "郁闷")) {
            return pick(
                "先不用急着振作。挑最烦的那一件事说给我听，我陪你把它拆小一点。",
                "听起来今天不太好过。你可以慢慢说，我不打断，也不急着给建议。",
            ) + (
                if (context.partnerName.isNotBlank()) {
                    " 如果不想一个人扛，也可以给 $partnerName 留一句「今天有点难」。"
                } else {
                    ""
                }
                )
        }
        if (hasAny(text, "开心", "高兴", "好消息", "成功了", "通过了", "考过")) {
            return "听起来今天有好事，快说给我听听，我也沾沾喜气。"
        }
        if (hasAny(text, "孤单", "一个人", "没人陪", "寂寞")) {
            return "一个人待着的时候最容易想多。要不要给 $partnerName 留一句？" +
                "不用长，一句「今天想到你」就够。"
        }

        // 11) 吃饭 / 喝水
        if (hasAny(text, "吃饭", "吃了", "饿", "饭", "外卖", "零食")) {
            return "到饭点啦。别拿零食糊弄，热乎的吃一点；吃完再忙，胃比进度重要。"
        }
        if (hasAny(text, "喝水", "口渴", "水杯", "咖啡", "奶茶")) {
            return "水杯在手边吗？先喝两口。忙起来最容易忘记这件事，我帮你记着。"
        }

        // 12) 驾驶 / 学习 / 工作
        if (hasAny(text, "开车", "驾驶", "高速", "路上", "堵车", "服务区")) {
            return "在路上的话先别打字，靠边停稳再聊。安全比回消息重要；累了就去最近的服务区。"
        }
        if (hasAny(text, "学习", "考试", "复习", "论文", "工作", "上班", "项目", "deadline")) {
            return "先挑最小的一步开始，比如只做十分钟。做完告诉我，我陪你往下走。"
        }

        // 13) App 用法
        if (hasAny(text, "打卡", "任务", "完成")) {
            return "打卡在「行程」页：可以给自己或 $partnerName 建任务，完成后对方能看到。" +
                "想更具体一点，也可以附一张照片。"
        }
        if (hasAny(text, "提醒", "闹钟", "别忘了", "记一下")) {
            return "提醒也在「行程」里，设好时间到点会通知你。重要的事建议再发一条留言，" +
                "这样 $partnerName 也能看到。"
        }
        if (hasAny(text, "留言", "语音", "图片", "发消息")) {
            return "留言墙在「亲友」页，文字、图片和语音都能发；TA 打开念安就能看到。"
        }
        if (hasAny(text, "宠物", "喂", "摸摸", "猫头鹰", "雪鸮")) {
            return "宠物在抽屉里的「我的宠物」。喂它、摸摸它都会影响心情；它饿了会自己提醒你。"
        }
        if (hasAny(text, "设备", "esp32", "绑定", "硬件", "屏幕")) {
            return "设备在「亲友与设备」里绑定。绑定后，驾驶疲劳、位置和车内温度会一起出现在关心页。"
        }
        if (hasAny(text, "地图", "定位", "位置共享", "导航")) {
            return "地图页能看到你和 $partnerName 的位置、朝向和距离；点一下头像还能导航过去。"
        }
        if (hasAny(text, "浪漫", "清单", "情话")) {
            return "浪漫清单在「亲友」页，里面有一百件小事；每天抽一件，日子会慢慢变得有盼头。"
        }

        // 14) 兜底：不给假答案，给一个可以继续说的入口。
        if (raw.endsWith("?") || raw.endsWith("？") || hasAny(text, "为什么", "怎么办", "吗")) {
            return pick(
                "这个我暂时不确定，不想糊弄你。你多说一点背景，我陪你一起理一理。",
                "我还没听明白最关键的那一点。是发生了什么，还是你在担心什么？",
            )
        }
        return pick(
            "我在听。你可以从今天最想吐槽的那一件事说起。",
            "嗯，我记下了。那你现在更想有人听你说，还是一起想个办法？",
            "这件事听起来不轻。要不我们先把它拆成「现在能做的一小步」？",
            "慢慢说，不着急。我今晚都在。",
        )
    }

    private fun weatherReply(
        context: XiaozhiContext,
        partnerName: String,
        random: Random,
    ): String {
        val temp = context.weatherTemperature
        if (temp == null) {
            return "我还没拿到你那边的天气。等定位和网络就绪，我再看一眼。"
        }
        val label = context.weatherLabel.ifBlank { "天气" }
        val emoji = context.weatherEmoji
        val night = context.hour >= 21 || context.hour <= 5
        val tip = when {
            label.contains("雨") || label.contains("雪") -> "出门记得带伞，路滑就慢一点。"
            temp <= 8.0 -> "多穿一件，别让脖子和脚受凉。"
            temp >= 32.0 -> "记得补水，别在太阳下久站。"
            night && temp <= 16.0 -> "夜里凉，出门记得加件外套。"
            night -> "夜里风大，早点回去休息。"
            temp >= 26.0 -> "不算凉快，随身带瓶水。"
            else -> if (random.nextBoolean()) "体感还行，出门前再看一眼窗外。" else "今天挺适合出门走走的。"
        }
        val partnerTip = context.partnerName.takeIf { it.isNotBlank() }?.let {
            if (context.partnerStatus.isNotBlank()) " $partnerName 那边显示「${context.partnerStatus}」，可以顺便问一句。" else ""
        }.orEmpty()
        return "你那边现在 ${emoji}${formatTemperature(temp)}℃、$label。$tip$partnerTip"
    }

    private fun partnerReply(context: XiaozhiContext, partnerName: String): String {
        if (context.partnerName.isBlank()) {
            return "你还没有绑定亲友。可以在「亲友与设备」里加一位，我就能帮你看 TA 的状态了。"
        }
        if (!context.partnerHasLocation || context.partnerDistanceMeters == null) {
            return "我还没看到 $partnerName 的位置。可能是 TA 还没共享定位，去地图页刷新一下试试。"
        }
        val distance = formatDistance(context.partnerDistanceMeters)
        val direction = context.partnerDirection.ifBlank { "附近" }
        val status = context.partnerStatus.ifBlank { "状态未知" }
        val note = context.partnerNote.takeIf { it.isNotBlank() }?.let { "，$it" }.orEmpty()
        val tip = when {
            status.contains("需要帮助") -> " TA 的状态是「需要帮助」，先打电话确认安全。"
            status.contains("驾驶") -> " 开车时别一直看手机，等 TA 停稳再联系。"
            status.contains("需要休息") -> " TA 看起来有点累，晚点提醒 TA 休息吧。"
            status.contains("睡觉") -> " TA 可能已经睡了，留言就好，别急着打电话。"
            !context.partnerOnline -> " TA 现在不在线，最后的位置可能不是最新的。"
            else -> ""
        }
        return "$partnerName 现在离你大约 $distance，在${direction}方向。状态是「$status」$note。$tip"
    }

    private fun timeReply(context: XiaozhiContext): String {
        val period = when (context.hour) {
            in 0..4 -> "凌晨"
            in 5..8 -> "早上"
            in 9..11 -> "上午"
            in 12..13 -> "中午"
            in 14..17 -> "下午"
            in 18..19 -> "傍晚"
            in 20..22 -> "晚上"
            else -> "深夜"
        }
        val clock = String.format(Locale.CHINA, "%02d:%02d", context.hour, context.minute)
        val tip = when (context.hour) {
            in 0..4 -> "这个点还没睡，明天会很辛苦，去休息吧。"
            in 5..8 -> "新的一天，先吃口早饭再忙。"
            in 11..13 -> "到饭点了，记得吃饭；吃完可以眯十分钟。"
            in 18..20 -> "该吃晚饭了，别拖到很晚。"
            in 21..23 -> "快收尾吧，别把今天的事拖到明天。"
            else -> "慢慢来，不用一口气做完。"
        }
        return "现在是$period${clock}，${context.dateText.ifBlank { "今天" }}。$tip"
    }

    private fun timeGreeting(hour: Int): String = when (hour) {
        in 5..8 -> "早上好"
        in 9..11 -> "上午好"
        in 12..13 -> "中午好"
        in 14..17 -> "下午好"
        in 18..22 -> "晚上好"
        else -> "这么晚还没睡"
    }

    private fun isLateNight(hour: Int): Boolean = hour >= 23 || hour <= 4

    private fun isPartnerQuestion(text: String): Boolean {
        val mentionsPartner = hasAny(
            text,
            "ta", "他", "她", "对象", "女朋友", "男朋友", "老婆", "老公",
            "家人", "爸爸", "妈妈", "爸妈", "亲人",
        )
        if (!mentionsPartner) return false
        return hasAny(
            text,
            "在哪", "位置", "到哪", "距离", "多远", "多久到", "状态", "怎么样",
            "还好吗", "在干嘛", "在做什么", "回没回", "消息",
        )
    }

    /** 英文模式下的轻量回复：不依赖中文语料，避免英文界面里冒出中文。 */
    private fun englishReply(input: String, context: XiaozhiContext): String {
        val text = input.lowercase(Locale.US)
        val partner = context.partnerName.ifBlank { "them" }
        fun has(vararg words: String) = words.any { text.contains(it) }
        return when {
            has("累", "tired", "exhausted", "sleepy", "困", "sleep") ->
                "You've been going hard. Put the phone down for ten minutes, drink some water, and let your eyes rest."
            has("在哪", "where", "位置", "distance", "多远") -> {
                val distance = context.partnerDistanceMeters
                if (context.partnerHasLocation && distance != null) {
                    val km = String.format(Locale.US, "%.1f", distance / 1000.0)
                    "They're about $km km away right now. Open the map if you want to see the exact spot."
                } else {
                    "I don't have $partner's location yet. Once they're online and sharing, the map will show it."
                }
            }
            has("天气", "weather", "temperature", "下雨", "rain") -> {
                val temp = context.weatherTemperature
                if (temp != null) {
                    "It's ${context.weatherLabel.ifBlank { "clear" }} and ${temp.roundToInt()}°C where you are. Dress for it."
                } else {
                    "I don't have the weather yet. Give me a moment and ask again."
                }
            }
            has("谢谢", "thanks", "thank you") -> "Anytime. I'm right here."
            has("你好", "hello", "hi ", "hey") -> "Hi! I'm here. How are you feeling today?"
            has("聊聊", "chat", "talk", "无聊", "bored") ->
                "I'm listening. Tell me one small thing that happened today—good or bad."
            else ->
                "I'm here with you. Tell me what's on your mind, or ask me about $partner's status or the weather."
        }
    }

    private fun hasAny(text: String, vararg words: String): Boolean =
        words.any { text.contains(it) }

    private fun formatDistance(meters: Double): String =
        if (meters < 1000.0) {
            "${meters.roundToInt().coerceAtLeast(1)} 米"
        } else {
            String.format(Locale.CHINA, "%.1f 公里", meters / 1000.0)
        }

    private fun formatTemperature(value: Double): String =
        String.format(Locale.CHINA, "%.1f", value)
}
````

<a id="s01-5"></a>

## 步骤 01.5 · 仓库层

仓库把 Room、DataStore、HTTP、MQTT 组合成界面可直接调用的方法，并统一处理离线缓存与重试。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/repository/AdviceRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/AuthRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/CareRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/CareSyncRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/ChatMessageRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/CheckInRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/CheckInTaskRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/CompanionRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/DeviceRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/EventRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/LocationRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/MqttRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/ReminderRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/SchedulePostRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/WeatherRepository.kt`
- `app/src/main/java/com/shineleong/toughmind/data/repository/XiaozhiRepository.kt`

### `app/src/main/java/com/shineleong/toughmind/data/repository/AdviceRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.AdviceDao
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import kotlinx.coroutines.flow.Flow

class AdviceRepository(private val adviceDao: AdviceDao) {

    fun observeAdvice(deviceId: String): Flow<List<AdviceEntity>> =
        adviceDao.observeByDevice(deviceId)

    suspend fun insert(advice: AdviceEntity) {
        adviceDao.insert(advice)
    }

    suspend fun insertAll(advices: List<AdviceEntity>) {
        advices.forEach { adviceDao.insert(it) }
    }

    suspend fun clear(deviceId: String) {
        adviceDao.deleteByDevice(deviceId)
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/AuthRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.User
import com.shineleong.toughmind.data.remote.AuthApi
import com.shineleong.toughmind.data.remote.AuthApiProvider
import com.shineleong.toughmind.data.remote.AuthRequest
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import retrofit2.HttpException

/**
 * 账号仓库。
 *
 * 配置了后端地址（AUTH_BASE_URL）时走真实鉴权接口；否则回退到本地演示实现。
 */
class AuthRepository(
    private val context: android.content.Context,
    private val preferences: Preferences,
    baseUrl: String,
) {

    private val api: AuthApi? = if (baseUrl.isNotBlank()) AuthApiProvider.create(baseUrl) else null

    val currentUser: Flow<User?> =
        combine(preferences.account, preferences.nickname, preferences.token) { account, nickname, token ->
            if (account.isBlank()) null else User(account, nickname, token)
        }

    suspend fun login(account: String, password: String): Result<User> {
        val remote = api
        if (remote == null) return demoLogin(account, password)
        return try {
            val resp = remote.login(AuthRequest(account, password))
            saveAndReturn(resp.account, resp.nickname, resp.token, resp.avatarBase64)
        } catch (e: Exception) {
            // 客户端错误（账号/密码/格式）如实返回；网络或服务端异常时回退本地演示，保证离线可体验。
            if (e is HttpException && e.code() in 400..499) {
                Result.failure(Exception(authFailureMessage(e)))
            } else {
                demoLogin(account, password)
            }
        }
    }

    suspend fun register(account: String, password: String): Result<User> {
        val remote = api
        if (remote == null) return demoLogin(account, password)
        return try {
            val resp = remote.register(AuthRequest(account, password))
            saveAndReturn(resp.account, resp.nickname, resp.token, resp.avatarBase64)
        } catch (e: Exception) {
            if (e is HttpException && e.code() in 400..499) {
                Result.failure(Exception(authFailureMessage(e)))
            } else {
                demoLogin(account, password)
            }
        }
    }

    suspend fun logout() {
        preferences.clearSession()
    }

    suspend fun updateNickname(nickname: String) {
        preferences.setNickname(nickname)
    }

    private suspend fun demoLogin(account: String, password: String): Result<User> {
        val token = generateToken(account, password)
        // 演示模式固定使用「念」这个昵称，与默认亲友「安」组成念安。
        val nickname = "念"
        preferences.saveSession(account, nickname, token)
        return Result.success(User(account, nickname, token))
    }

    private suspend fun saveAndReturn(account: String, nickname: String, token: String, avatarBase64: String = ""): Result<User> {
        preferences.saveSession(account, nickname, token)
        if (avatarBase64.isNotBlank()) {
            runCatching {
                val file = java.io.File(context.filesDir, "avatar.png")
                file.writeBytes(android.util.Base64.decode(avatarBase64, android.util.Base64.DEFAULT))
                preferences.setAvatarPath(file.absolutePath)
            }
        }
        return Result.success(User(account, nickname, token))
    }

    private fun authFailureMessage(e: Throwable): String = when (e) {
        is HttpException -> when (e.code()) {
            401 -> "账号或密码错误"
            409 -> "账号已存在"
            400 -> "账号或密码格式不正确"
            else -> "服务器错误（${e.code()}）"
        }
        else -> "无法连接服务器，请检查网络"
    }

    /** 默认昵称：用户 + 账号后四位，避免直接暴露手机号。 */
    private fun nicknameOf(account: String): String {
        val suffix = if (account.length >= 4) account.takeLast(4) else account
        return "用户$suffix"
    }

    private fun generateToken(account: String, password: String): String =
        "demo_token_" + (account + password).hashCode().toString(16)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/CareRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import android.content.Context
import android.os.BatteryManager
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.CareStatus
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.FatigueLevel
import com.shineleong.toughmind.data.model.GpsPosition
import com.shineleong.toughmind.data.model.PersonPresence
import com.shineleong.toughmind.data.model.RemotePartner
import com.shineleong.toughmind.data.model.SelfLocation
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.util.GeoMath
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.time.LocalDateTime
import java.time.LocalTime
import kotlin.math.round

/**
 * "念安"核心状态仓库：
 *  - 我：手机定位 + 电量 + 在线状态；
 *  - TA：优先使用 ESP32 通过 MQTT 上报的 GPS / 驾驶状态，未接入真实设备时按演示模式生成
 *    一份稳定的示例位置与生活状态（明确标注"演示"）；
 *  - 双方天气：根据各自经纬度请求 Open-Meteo，位置变化或每 10 分钟刷新。
 */
class CareRepository(
    context: Context,
    private val preferences: Preferences,
    private val companionRepository: CompanionRepository,
    private val mqttRepository: MqttRepository,
    private val locationRepository: LocationRepository,
    private val weatherRepository: WeatherRepository,
) {

    private val appContext = context.applicationContext
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    /** 演示模式的"对方位置"锚点，只取一次；本机位置大幅变化时重新锚定。 */
    private var demoAnchor: Pair<Double, Double>? = null
    private var demoAnchorBase: SelfLocation? = null

    /** 云端关心组中的对方；active=true 时不再展示演示人物。 */
    private data class CloudLink(
        val active: Boolean = false,
        val partner: RemotePartner? = null,
    )

    private val _cloudLink = MutableStateFlow(CloudLink())

    val companion: StateFlow<CarePartner> = combine(
        companionRepository.companion,
        _cloudLink,
    ) { local, link ->
        val remote = link.partner
        if (remote != null) {
            CarePartner(
                nickname = remote.nickname.ifBlank { local.nickname },
                relation = remote.relation.ifBlank { local.relation },
                deviceType = remote.deviceType,
                demoMode = false,
            )
        } else {
            local
        }
    }.stateIn(scope, SharingStarted.Eagerly, CarePartner())

    fun updateCloudLink(active: Boolean, partner: RemotePartner?) {
        _cloudLink.value = CloudLink(active, partner)
    }

    val selfPresence: StateFlow<PersonPresence?> = combine(
        locationRepository.selfLocation,
        preferences.nickname,
        preferences.avatarPath,
        preferences.moodEmoji,
        preferences.moodMessage,
    ) { location, nickname, avatarPath, moodEmoji, moodMessage ->
        buildSelf(location, nickname, avatarPath, moodEmoji, moodMessage)
    }.stateIn(scope, SharingStarted.Eagerly, null)

    val partnerPresence: StateFlow<PersonPresence?> = combine(
        locationRepository.selfLocation,
        mqttRepository.latestPosition,
        mqttRepository.latestState,
        _cloudLink,
        companionRepository.companion,
    ) { self, gps, driver, link, companion ->
        buildPartner(self, gps, driver, link, companion)
    }.stateIn(scope, SharingStarted.Eagerly, null)

    private val _selfWeather = MutableStateFlow<WeatherInfo?>(null)
    val selfWeather: StateFlow<WeatherInfo?> = _selfWeather.asStateFlow()

    private val _partnerWeather = MutableStateFlow<WeatherInfo?>(null)
    val partnerWeather: StateFlow<WeatherInfo?> = _partnerWeather.asStateFlow()

    private val weatherTicker = flow {
        while (currentCoroutineContext().isActive) {
            emit(Unit)
            delay(WEATHER_REFRESH_MS)
        }
    }

    init {
        scope.launch {
            combine(selfPresence, partnerPresence, weatherTicker) { self, partner, _ ->
                WeatherKey(
                    selfLat = self?.lat?.round2(),
                    selfLon = self?.lon?.round2(),
                    partnerLat = partner?.lat?.round2(),
                    partnerLon = partner?.lon?.round2(),
                )
            }
                .distinctUntilChanged()
                .collectLatest { key ->
                    coroutineScope {
                        if (key.selfLat != null && key.selfLon != null) {
                            launch {
                                weatherRepository.weatherAt(key.selfLat, key.selfLon)
                                    ?.let { _selfWeather.value = it }
                            }
                        } else {
                            _selfWeather.value = null
                        }
                        if (key.partnerLat != null && key.partnerLon != null) {
                            launch {
                                weatherRepository.weatherAt(key.partnerLat, key.partnerLon)
                                    ?.let { _partnerWeather.value = it }
                            }
                        } else {
                            _partnerWeather.value = null
                        }
                    }
                }
        }
    }

    // ── 自己 ─────────────────────────────────────────────

    private fun buildSelf(
        location: SelfLocation?,
        nickname: String,
        avatarPath: String,
        moodEmoji: String,
        moodMessage: String,
    ): PersonPresence? {
        if (location == null || !GeoMath.hasValidPosition(location.lat, location.lon)) return null
        val now = System.currentTimeMillis()
        val displayName = nickname.trim().let { raw ->
            if (raw.length >= 7 && raw.all { it.isDigit() }) "我" else raw.ifBlank { "我" }
        }
        val status = statusForHour(LocalTime.now().hour)
        return PersonPresence(
            id = SELF_ID,
            name = displayName,
            relation = "我",
            avatarPath = avatarPath,
            deviceType = DeviceType.PHONE,
            status = status,
            activityNote = activityNote(status, null, false),
            lat = location.lat,
            lon = location.lon,
            battery = deviceBattery(),
            lastSeen = if (location.timestamp > 0) location.timestamp else now,
            online = true,
            isDemo = false,
            heading = location.heading,
            moodEmoji = moodEmoji,
            moodMessage = moodMessage,
        )
    }

    private fun deviceBattery(): Int = runCatching {
        val manager = appContext.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        manager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }.getOrDefault(-1)

    // ── 对方 ─────────────────────────────────────────────

    private fun buildPartner(
        self: SelfLocation?,
        gps: GpsPosition?,
        driver: DriverState?,
        link: CloudLink,
        companion: CarePartner,
    ): PersonPresence? {
        if (link.active) {
            val remote = link.partner
            if (remote?.presence != null) {
                return buildRemotePartner(self, remote, driver)
            }
            // 云端对方还没有手机上报时，继续允许 ESP32 的 MQTT 数据接管；
            // 但不再生成演示人物。
        }

        val now = System.currentTimeMillis()
        val selfValid = self != null && GeoMath.hasValidPosition(self.lat, self.lon)
        val gpsFresh = gps != null &&
            GeoMath.hasValidPosition(gps.lat, gps.lon) &&
            (gps.timestamp <= 0L || now - gps.timestamp <= DATA_STALE_MS)
        val driverFresh = driver != null &&
            (driver.timestamp <= 0L || now - driver.timestamp <= DATA_STALE_MS)
        val driverPos = driver?.takeIf {
            driverFresh && GeoMath.hasValidPosition(it.lat, it.lon)
        }

        val actualPosition = when {
            gpsFresh -> gps!!.lat to gps.lon
            driverPos != null -> driverPos.lat to driverPos.lon
            else -> null
        } ?: return null

        val effectiveDevice = when {
            companion.deviceType == DeviceType.ESP32 -> DeviceType.ESP32
            gpsFresh || driverFresh -> DeviceType.ESP32
            else -> DeviceType.PHONE
        }
        val effectiveDriver = if (effectiveDevice == DeviceType.ESP32 && driverFresh) driver else null
        val isDemo = false

        val status = when {
            (effectiveDriver?.medicalLevel ?: 0) >= 1 -> CareStatus.SOS
            effectiveDriver != null &&
                (effectiveDriver.fatigueLevel == FatigueLevel.SEVERE ||
                    effectiveDriver.fatigueLevel == FatigueLevel.MODERATE) -> CareStatus.TIRED
            effectiveDriver != null && effectiveDriver.speedKmh > 3.0 -> CareStatus.DRIVING
            effectiveDriver != null -> CareStatus.RESTING
            else -> statusForHour(LocalTime.now().hour)
        }

        val relation = if (selfValid) {
            GeoMath.relation(self!!.lat, self.lon, actualPosition.first, actualPosition.second)
        } else {
            null
        }

        val lastSeen = when {
            gpsFresh -> gps!!.timestamp
            driverFresh && driver != null -> driver.timestamp
            else -> now - 2 * 60_000L
        }

        return PersonPresence(
            id = PARTNER_ID,
            name = companion.nickname.ifBlank { "TA" },
            relation = companion.relation.ifBlank { "家人" },
            deviceType = effectiveDevice,
            status = status,
            activityNote = activityNote(status, effectiveDriver, isDemo),
            lat = actualPosition.first,
            lon = actualPosition.second,
            battery = if (effectiveDevice == DeviceType.ESP32) 100 else simulatedBattery(),
            lastSeen = lastSeen,
            online = gpsFresh || driverFresh,
            isDemo = isDemo,
            driverState = effectiveDriver,
            distanceMeters = relation?.distanceMeters,
            directionLabel = relation?.directionLabel.orEmpty(),
            moodEmoji = "🙂",
            moodMessage = "",
        )
    }

    /** 云端关心组中的真实 TA：状态、位置、电量直接来自另一台手机 / ESP32。 */
    private fun buildRemotePartner(
        self: SelfLocation?,
        remote: RemotePartner,
        driver: DriverState?,
    ): PersonPresence? {
        val presence = remote.presence ?: return null
        if (!GeoMath.hasValidPosition(presence.lat, presence.lon)) return null
        val now = System.currentTimeMillis()
        val deviceType = DeviceType.fromCode(presence.deviceType)
        val driverFresh = driver != null &&
            (driver.timestamp <= 0L || now - driver.timestamp <= DATA_STALE_MS)
        val effectiveDriver = if (deviceType == DeviceType.ESP32 && driverFresh) driver else null
        val status = runCatching { CareStatus.valueOf(presence.status) }
            .getOrDefault(CareStatus.UNKNOWN)
        val relation = if (self != null && GeoMath.hasValidPosition(self.lat, self.lon)) {
            GeoMath.relation(self.lat, self.lon, presence.lat, presence.lon)
        } else {
            null
        }
        return PersonPresence(
            id = PARTNER_ID,
            name = remote.nickname.ifBlank { "TA" },
            relation = remote.relation.ifBlank { "家人" },
            deviceType = deviceType,
            status = status,
            activityNote = presence.activityNote.ifBlank {
                activityNote(status, effectiveDriver, false)
            },
            lat = presence.lat,
            lon = presence.lon,
            battery = presence.battery,
            lastSeen = if (presence.updatedAt > 0) presence.updatedAt * 1000 else now,
            online = presence.online,
            isDemo = false,
            driverState = effectiveDriver,
            distanceMeters = presence.distanceM ?: relation?.distanceMeters,
            directionLabel = relation?.directionLabel.orEmpty(),
            moodEmoji = presence.moodEmoji,
            moodMessage = presence.moodMessage,
        )
    }

    private fun demoPosition(self: SelfLocation): Pair<Double, Double> {
        val anchor = demoAnchor
        val base = demoAnchorBase
        if (anchor != null && base != null &&
            GeoMath.distanceMeters(base.lat, base.lon, self.lat, self.lon) < 5_000
        ) {
            return anchor
        }
        val newAnchor = (self.lat + 0.0135) to (self.lon + 0.0105)
        demoAnchor = newAnchor
        demoAnchorBase = self
        return newAnchor
    }

    private fun statusForHour(hour: Int): CareStatus = when (hour) {
        in 0..5 -> CareStatus.SLEEPING
        in 6..7 -> CareStatus.EXERCISING
        in 8..11 -> CareStatus.STUDYING
        in 12..13 -> CareStatus.RESTING
        in 14..17 -> CareStatus.WORKING
        in 18..19 -> CareStatus.COMMUTE
        in 20..22 -> CareStatus.STUDYING
        else -> CareStatus.SLEEPING
    }

    private fun activityNote(
        status: CareStatus,
        driver: DriverState?,
        isDemo: Boolean,
    ): String {
        if (driver != null) {
            return when {
                driver.medicalLevel >= 1 -> "检测到${driver.medicalType.label}，请尽快联系"
                driver.fatigueLevel == FatigueLevel.SEVERE ||
                    driver.fatigueLevel == FatigueLevel.MODERATE ->
                    "疲劳等级 ${driver.fatigueLevel.label} · 提醒 TA 休息一下"
                driver.speedKmh > 3 -> "车速 ${driver.speedKmh.toInt()} km/h · 正在路上"
                else -> "车辆已停稳 · 设备在线"
            }
        }
        return when (status) {
            CareStatus.STUDYING -> "正在专注学习"
            CareStatus.WORKING -> "正在忙工作"
            CareStatus.COMMUTE -> "正在通勤路上"
            CareStatus.RESTING -> "正在休息 · 喝口水吧"
            CareStatus.SLEEPING -> "已经睡下 · 晚安"
            CareStatus.EXERCISING -> "正在运动 · 状态不错"
            CareStatus.ONLINE -> "手机在线"
            CareStatus.TIRED -> "看起来有点累"
            CareStatus.SOS -> "需要你的帮助"
            CareStatus.DRIVING -> "正在路上"
            CareStatus.UNKNOWN -> "还没有收到 TA 的动态"
        }
    }

    private fun simulatedBattery(): Int {
        val now = LocalDateTime.now()
        val seed = now.dayOfYear * 7 + now.hour * 3 + now.minute / 10
        return 38 + (seed % 58)
    }

    private fun Double.round2(): Double = round(this * 100) / 100

    private data class WeatherKey(
        val selfLat: Double?,
        val selfLon: Double?,
        val partnerLat: Double?,
        val partnerLon: Double?,
    )

    companion object {
        const val SELF_ID = "self"
        const val PARTNER_ID = "partner"

        private const val DATA_STALE_MS = 10 * 60 * 1000L
        private const val WEATHER_REFRESH_MS = 10 * 60 * 1000L
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/CareSyncRepository.kt`

> 云端同步编排：关心组、成员、设备与状态合并，处理离线缓存。

````kotlin
package com.shineleong.toughmind.data.repository

import android.util.Log
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import com.shineleong.toughmind.data.model.DeviceType
import com.shineleong.toughmind.data.model.FatigueLevel
import com.shineleong.toughmind.data.model.RemoteDevice
import com.shineleong.toughmind.data.model.RemotePartner
import com.shineleong.toughmind.data.model.RemotePresence
import com.shineleong.toughmind.data.remote.SchedulePostCreateRequest
import com.shineleong.toughmind.data.remote.CareApi
import com.shineleong.toughmind.data.remote.CareDevice
import com.shineleong.toughmind.data.remote.CareGroupResponse
import com.shineleong.toughmind.data.remote.CareMember
import com.shineleong.toughmind.data.remote.CareNudge
import com.shineleong.toughmind.data.remote.CheckInRecord
import com.shineleong.toughmind.data.remote.DeviceJoinRequest
import com.shineleong.toughmind.data.remote.DeviceCodeBindRequest
import com.shineleong.toughmind.data.remote.DevicePresenceRequest
import com.shineleong.toughmind.data.remote.GroupCreateRequest
import com.shineleong.toughmind.data.remote.JoinGroupRequest
import com.shineleong.toughmind.data.remote.ChatMessageDto
import com.shineleong.toughmind.data.remote.ChatMessageRequest
import com.shineleong.toughmind.data.remote.NudgeRequest
import com.shineleong.toughmind.data.remote.PresenceRequest
import com.shineleong.toughmind.data.remote.ReminderCreateRequest
import com.shineleong.toughmind.data.remote.ReminderUpdateRequest
import com.shineleong.toughmind.service.NotificationHelper
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.LocalDate
import java.time.YearMonth
import java.util.concurrent.atomic.AtomicBoolean

/**
 * 云端关心组同步：
 *  - 轮询关心组与对方状态，把真实 TA 交给 [CareRepository] 展示；
 *  - 定时上报自己的位置 / 状态 / 电量；
 *  - 同步双人打卡、共享提醒与「关心消息」；
 *  - 未登录、演示账号或服务端不可用时保持本地演示模式，不阻塞 UI。
 */
class CareSyncRepository(
    private val api: CareApi?,
    private val preferences: Preferences,
    private val careRepository: CareRepository,
    private val checkInRepository: CheckInRepository,
    private val reminderRepository: ReminderRepository,
    private val schedulePostRepository: SchedulePostRepository,
    private val checkInTaskRepository: CheckInTaskRepository,
    private val notificationHelper: NotificationHelper,
    private val mqttRepository: MqttRepository,
    private val deviceRepository: DeviceRepository,
) {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private val _group = MutableStateFlow<CareGroupResponse?>(null)
    val group: StateFlow<CareGroupResponse?> = _group.asStateFlow()

    /** 当前账号加入的全部关心组，供亲友页左右滑动卡片使用。 */
    private val _groups = MutableStateFlow<List<CareGroupResponse>>(emptyList())
    val groups: StateFlow<List<CareGroupResponse>> = _groups.asStateFlow()

    /** 关心组里的 ESP32 设备成员（由 device_id + 邀请码加入）。 */
    private val _devices = MutableStateFlow<List<RemoteDevice>>(emptyList())
    val devices: StateFlow<List<RemoteDevice>> = _devices.asStateFlow()

    /** 关心组中的其他成员（不含自己），用于关心页左右滑动查看多位亲属。 */
    private val _members = MutableStateFlow<List<RemotePartner>>(emptyList())
    val members: StateFlow<List<RemotePartner>> = _members.asStateFlow()

    val groupActive: StateFlow<Boolean> = group
        .map { it?.inGroup == true }
        .stateIn(scope, SharingStarted.Eagerly, false)

    private val _latestNudge = MutableStateFlow<CareNudge?>(null)
    val latestNudge: StateFlow<CareNudge?> = _latestNudge.asStateFlow()

    private var pollJob: Job? = null
    private var lastPresenceAt = 0L
    private var lastDevicePresenceAt = 0L
    private var lastNudgeId = 0L
    private var nudgeCursorLoaded = false
    private val nudgeInitialized = AtomicBoolean(false)

    init {
        scope.launch {
            preferences.token.collectLatest { token ->
                if (token.isBlank()) {
                    stopPolling()
                    clearRemote()
                } else {
                    startPolling()
                }
            }
        }
    }

    fun start() {
        startPolling()
    }

    fun stop() {
        stopPolling()
    }

    private fun startPolling() {
        if (pollJob?.isActive == true) return
        pollJob = scope.launch {
            while (isActive) {
                tick()
                kotlinx.coroutines.delay(POLL_INTERVAL_MS)
            }
        }
    }

    private fun stopPolling() {
        pollJob?.cancel()
        pollJob = null
    }

    private fun clearRemote() {
        _group.value = null
        _groups.value = emptyList()
        _devices.value = emptyList()
        _members.value = emptyList()
        careRepository.updateCloudLink(false, null)
    }

    private suspend fun authHeader(): String? {
        val token = runCatching { preferences.token.first() }.getOrNull().orEmpty()
        if (token.isBlank() || token.startsWith("demo_token_")) return null
        return "Bearer $token"
    }

    private suspend fun tick() {
        val auth = authHeader() ?: run {
            clearRemote()
            return
        }
        val client = api ?: return
        try {
            val response = client.group(auth)
            applyGroup(response)
            runCatching { client.groups(auth) }
                .onSuccess { _groups.value = it.groups }
            if (response.inGroup) {
                postSelfPresence(auth)
                postDevicePresence(auth)
                pollNudges(auth)
            }
        } catch (e: Exception) {
            Log.w(TAG, "云端同步失败（保持本地模式）", e)
        }
    }

    private fun applyGroup(response: CareGroupResponse) {
        _group.value = response
        _devices.value = response.devices.map { it.toRemoteDevice() }
        val relatives = response.members
            .asSequence()
            .filter { !it.isSelf }
            .map { it.toRemotePartner() }
            .toList()
            .ifEmpty { listOfNotNull(response.partner?.toRemotePartner()) }
        _members.value = relatives
        careRepository.updateCloudLink(
            active = response.inGroup,
            partner = response.partner?.toRemotePartner(),
        )
    }

    private suspend fun postSelfPresence(auth: String) {
        val now = System.currentTimeMillis()
        if (now - lastPresenceAt < PRESENCE_INTERVAL_MS) return
        val self = careRepository.selfPresence.value ?: return
        if (self.lat == 0.0 && self.lon == 0.0) return
        lastPresenceAt = now
        runCatching {
            api?.updatePresence(
                auth,
                PresenceRequest(
                    lat = self.lat,
                    lon = self.lon,
                    status = self.status.name,
                    activityNote = self.activityNote,
                    battery = self.battery,
                    deviceType = self.deviceType.name,
                    moodEmoji = self.moodEmoji,
                    moodMessage = self.moodMessage,
                ),
            )
        }.onFailure { Log.w(TAG, "上报自身状态失败", it) }
    }

    /**
     * 把已绑定的 ESP32 状态代传到云端关心组：
     * 设备成员进组后，另一台手机即使收不到 MQTT，也能在组里看到它的位置/驾驶状态。
     */
    private suspend fun postDevicePresence(auth: String) {
        val now = System.currentTimeMillis()
        if (now - lastDevicePresenceAt < PRESENCE_INTERVAL_MS) return
        val group = _group.value ?: return
        val cloudIds = group.devices.map { it.deviceId }.toSet()
        if (cloudIds.isEmpty()) return
        val bound = runCatching { deviceRepository.devices.first() }.getOrDefault(emptyList())
        val target = bound.firstOrNull { it.deviceId in cloudIds } ?: return

        val gps = mqttRepository.latestPosition.value
        val driver = mqttRepository.latestState.value
        val gpsFresh = gps != null &&
            validPosition(gps.lat, gps.lon) &&
            fresh(gps.timestamp, now)
        val driverFresh = driver != null && fresh(driver.timestamp, now)
        if (!gpsFresh && !driverFresh) return

        val lat = if (gpsFresh) gps!!.lat else driver!!.lat
        val lon = if (gpsFresh) gps!!.lon else driver!!.lon
        if (!validPosition(lat, lon)) return

        val status = when {
            driver != null && driver.medicalLevel >= 1 -> "SOS"
            driver != null && (driver.fatigueLevel == FatigueLevel.SEVERE ||
                driver.fatigueLevel == FatigueLevel.MODERATE) -> "TIRED"
            driver != null && driver.speedKmh > 3.0 -> "DRIVING"
            else -> "ONLINE"
        }
        val note = when {
            status == "SOS" -> "检测到医疗异常，请尽快联系 TA"
            status == "TIRED" -> "疲劳 ${driver?.fatigueLevel?.label.orEmpty()} · 提醒 TA 休息"
            driver != null && driver.speedKmh > 3.0 -> "车速 ${driver.speedKmh.toInt()} km/h · 正在路上"
            else -> "设备在线 · 车辆已停稳"
        }
        lastDevicePresenceAt = now
        runCatching {
            api?.updateDevicePresence(
                auth,
                target.deviceId,
                DevicePresenceRequest(
                    lat = lat,
                    lon = lon,
                    status = status,
                    activityNote = note,
                    battery = 100,
                ),
            )
        }.onFailure { Log.w(TAG, "代传 ESP32 状态失败", it) }
    }

    private fun fresh(timestamp: Long, now: Long): Boolean =
        timestamp <= 0L || now - timestamp <= STALE_MS

    private fun validPosition(lat: Double, lon: Double): Boolean =
        kotlin.math.abs(lat) > 0.000001 || kotlin.math.abs(lon) > 0.000001

    private suspend fun pollNudges(auth: String) {
        ensureNudgeCursor()
        val response = runCatching { api?.nudges(auth, lastNudgeId) }.getOrNull() ?: return
        val maxId = response.nudges.maxOfOrNull { it.id } ?: lastNudgeId
        if (!nudgeInitialized.getAndSet(true)) {
            // 首次同步不补弹历史消息，只记录位置。
            lastNudgeId = maxId
            preferences.setLastNudgeId(lastNudgeId)
            return
        }
        response.nudges.forEach { nudge ->
            _latestNudge.value = nudge
            notificationHelper.notifyCareMessage(nudge.fromNickname, nudge.message)
        }
        lastNudgeId = maxId
        preferences.setLastNudgeId(lastNudgeId)
    }

    private suspend fun ensureNudgeCursor() {
        if (nudgeCursorLoaded) return
        lastNudgeId = runCatching { preferences.lastNudgeId.first() }.getOrDefault(0L)
        if (lastNudgeId > 0) nudgeInitialized.set(true)
        nudgeCursorLoaded = true
    }

    suspend fun refreshNow() = withContext(Dispatchers.IO) { tick() }

    suspend fun createGroup(name: String, password: String): Result<CareGroupResponse> = callGroup {
        it.createGroup(requireAuth(), GroupCreateRequest(name, password))
    }

    suspend fun joinGroup(
        inviteCode: String,
        relation: String,
        password: String,
    ): Result<CareGroupResponse> = callGroup {
        it.joinGroup(requireAuth(), JoinGroupRequest(inviteCode, relation, password))
    }

    suspend fun activateGroup(groupId: Long): Result<CareGroupResponse> = callGroup {
        it.activateGroup(requireAuth(), groupId)
    }

    suspend fun approveJoinRequest(requestId: Long): Result<CareGroupResponse> = callGroup {
        it.approveJoinRequest(requireAuth(), requestId)
    }

    suspend fun rejectJoinRequest(requestId: Long): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val client = api ?: error("未配置服务器地址")
            client.rejectJoinRequest(requireAuth(), requestId)
            Unit
        }
    }

    suspend fun removeGroupMember(account: String): Result<CareGroupResponse> = callGroup {
        it.removeGroupMember(requireAuth(), account)
    }

    /** 手机输入设备码绑定：服务端解密出 device_id 并加入当前组。 */
    suspend fun bindDeviceByCode(code: String, name: String): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                val client = api ?: error("未配置服务器地址")
                client.bindDeviceCode(requireAuth(), DeviceCodeBindRequest(code, name))
                applyGroup(client.group(requireAuth()))
                Unit
            }
        }

    /** 把设备管理里绑定的 ESP32 加进当前云端关心组（device_id + 邀请码）。 */
    suspend fun joinDevice(deviceId: String, deviceName: String): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                val auth = requireAuth()
                val client = api ?: error("未配置服务器地址")
                // 设备页可能在首次同步前打开：先拉一次关心组拿邀请码。
                var code = _group.value?.group?.inviteCode.orEmpty()
                if (code.isBlank()) {
                    val latest = client.group(auth)
                    applyGroup(latest)
                    code = latest.group?.inviteCode.orEmpty()
                }
                if (code.isBlank()) error("请先创建或加入云端关心组")
                client.joinDevice(
                    auth,
                    DeviceJoinRequest(
                        deviceId = deviceId,
                        deviceName = deviceName,
                        inviteCode = code,
                    ),
                )
                applyGroup(client.group(auth))
                Unit
            }
        }

    /** 把 ESP32 从云端关心组移除（本地绑定保留，可随时重新加入）。 */
    suspend fun removeDevice(deviceId: String): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            val client = api ?: error("未配置服务器地址")
            client.removeDevice(auth, deviceId)
            applyGroup(client.group(auth))
            Unit
        }
    }

    suspend fun dissolveGroup(groupId: Long): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val client = api ?: error("未配置服务器地址")
            client.dissolveGroup(requireAuth(), groupId)
            _groups.value = _groups.value.filter { it.group?.id != groupId }
            clearRemote()
            Unit
        }
    }

    suspend fun leaveGroup(): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            api?.leaveGroup(auth)
            clearRemote()
            Unit
        }
    }

    suspend fun sendChatMessage(message: String): Result<ChatMessageDto> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            api?.sendChatMessage(auth, ChatMessageRequest(message))?.message
                ?: error("云端连接不可用")
        }
    }

    suspend fun fetchChatMessages(sinceId: Long): Result<List<ChatMessageDto>> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            api?.chatMessages(auth, sinceId)?.messages.orEmpty()
        }
    }
    suspend fun sendNudge(message: String): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            api?.sendNudge(requireAuth(), NudgeRequest(message))
            Unit
        }
    }

    suspend fun updateProfile(
        nickname: String,
        relation: String,
        deviceType: DeviceType,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            api?.updateProfile(
                requireAuth(),
                com.shineleong.toughmind.data.remote.ProfileUpdateRequest(
                    nickname = nickname,
                    relation = relation,
                    deviceType = deviceType.name,
                ),
            )
            Unit
        }
    }

    suspend fun updateSelfNickname(nickname: String): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            api?.updateProfile(
                requireAuth(),
                com.shineleong.toughmind.data.remote.ProfileUpdateRequest(nickname = nickname),
            )
            Unit
        }
    }

    suspend fun syncMonth(month: YearMonth): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val client = api ?: return@runCatching
            if (_group.value?.inGroup != true) return@runCatching
            val auth = requireAuth()
            val start = month.atDay(1).toString()
            val end = month.atEndOfMonth().toString()

            val checkIns = client.checkIns(auth, start, end).records
            checkInRepository.replaceBetween(
                start,
                end,
                checkIns.mapNotNull { it.toLocalCheckIn() },
            )

            val reminders = client.reminders(auth, start, end).reminders
            reminders.forEach { reminder ->
                reminderRepository.upsertSynced(
                    remoteId = reminder.id,
                    date = reminder.date,
                    timeMinutes = reminder.timeMinutes,
                    title = reminder.title,
                    note = reminder.note,
                    enabled = reminder.enabled,
                    type = reminder.type,
                )
            }
            reminderRepository.pruneSynced(start, end, reminders.map { it.id }.toSet())
        }
    }

    suspend fun toggleSelfCheckIn(
        date: LocalDate,
        checked: Boolean,
        note: String = "",
        goal: String = "",
        imageBase64: String = "",
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            val response = api?.toggleCheckIn(
                auth,
                com.shineleong.toughmind.data.remote.CheckInToggleRequest(
                    date = date.toString(),
                    checked = checked,
                    note = note,
                    goal = goal,
                    imageBase64 = imageBase64,
                ),
            ) ?: return@runCatching
            checkInRepository.replaceDate(
                date.toString(),
                response.records.mapNotNull { it.toLocalCheckIn() },
            )
        }
    }

    suspend fun syncSchedule(start: LocalDate, end: LocalDate): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                val auth = requireAuth()
                val posts = api?.schedule(auth, start.toString(), end.toString())?.posts.orEmpty()
                schedulePostRepository.replaceBetween(
                    start.toString(),
                    end.toString(),
                    posts.map {
                        SchedulePostEntity(
                            date = it.date,
                            timeMinutes = it.timeMinutes,
                            content = it.content,
                            imageBase64 = it.imageBase64,
                            authorId = if (it.isMine) CareRepository.SELF_ID else CareRepository.PARTNER_ID,
                            createdAt = it.createdAt,
                            remoteId = it.id,
                        )
                    },
                )
            }
        }

    suspend fun syncTasks(start: LocalDate, end: LocalDate): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                val auth = requireAuth()
                val tasks = api?.tasks(auth, start.toString(), end.toString())?.tasks.orEmpty()
                tasks.forEach { task ->
                    checkInTaskRepository.add(
                        date = task.date,
                        title = task.title,
                        imageBase64 = task.imageBase64,
                        createdBy = task.createdBy,
                        remoteId = task.id,
                    )
                    val existing = checkInTaskRepository.findByRemoteId(task.id)
                    if (existing != null) {
                        checkInTaskRepository.setSelfDone(existing, task.selfDone)
                        checkInTaskRepository.setPartnerDone(existing, task.partnerDone)
                    }
                }
            }
        }

    suspend fun addRemoteTask(
        date: LocalDate,
        title: String,
        imageBase64: String,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            val task = api?.createTask(
                auth,
                com.shineleong.toughmind.data.remote.CheckInTaskCreateRequest(
                    date = date.toString(),
                    title = title,
                    imageBase64 = imageBase64,
                ),
            )?.task ?: return@runCatching
            checkInTaskRepository.add(
                date = task.date,
                title = task.title,
                imageBase64 = task.imageBase64,
                createdBy = task.createdBy,
                remoteId = task.id,
            )
        }
    }

    suspend fun toggleRemoteTask(taskId: Long, done: Boolean): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                val auth = requireAuth()
                api?.toggleTask(
                    auth,
                    taskId,
                    com.shineleong.toughmind.data.remote.CheckInTaskToggleRequest(done),
                ) ?: return@runCatching
            }
        }

    suspend fun addRemoteSchedule(
        date: LocalDate,
        hour: Int,
        minute: Int,
        content: String,
        imageBase64: String,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            val post = api?.createSchedule(
                auth,
                SchedulePostCreateRequest(
                    date = date.toString(),
                    timeMinutes = hour * 60 + minute,
                    content = content,
                    imageBase64 = imageBase64,
                ),
            )?.post ?: return@runCatching
            schedulePostRepository.add(
                date = post.date,
                timeMinutes = post.timeMinutes,
                content = post.content,
                imageBase64 = post.imageBase64,
                authorId = if (post.isMine) CareRepository.SELF_ID else CareRepository.PARTNER_ID,
                remoteId = post.id,
            )
        }
    }

    suspend fun addRemoteReminder(
        date: LocalDate,
        hour: Int,
        minute: Int,
        title: String,
        note: String,
        type: String = ReminderEntity.TYPE_SCHEDULE,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val auth = requireAuth()
            val reminder = api?.createReminder(
                auth,
                ReminderCreateRequest(
                    date = date.toString(),
                    timeMinutes = hour * 60 + minute,
                    title = title,
                    note = note,
                    type = type,
                ),
            )?.reminder ?: return@runCatching
            reminderRepository.upsertSynced(
                remoteId = reminder.id,
                date = reminder.date,
                timeMinutes = reminder.timeMinutes,
                title = reminder.title,
                note = reminder.note,
                enabled = reminder.enabled,
                type = reminder.type,
            )
        }
    }

    suspend fun updateRemoteReminder(
        reminder: ReminderEntity,
        enabled: Boolean,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            if (reminder.remoteId <= 0) return@runCatching
            val auth = requireAuth()
            api?.updateReminder(
                auth,
                reminder.remoteId,
                ReminderUpdateRequest(enabled = enabled),
            )
        }
    }

    suspend fun deleteRemoteReminder(reminder: ReminderEntity): Result<Unit> =
        withContext(Dispatchers.IO) {
            runCatching {
                if (reminder.remoteId <= 0) return@runCatching
                val auth = requireAuth()
                api?.deleteReminder(auth, reminder.remoteId)
            }
        }

    private suspend fun requireAuth(): String =
        authHeader() ?: throw IllegalStateException("当前为本地演示模式，请先登录云端账号")

    private suspend fun callGroup(
        block: suspend (CareApi) -> CareGroupResponse,
    ): Result<CareGroupResponse> = withContext(Dispatchers.IO) {
        runCatching {
            val client = api ?: error("未配置服务器地址")
            val response = block(client)
            applyGroup(response)
            response
        }
    }

    private fun CheckInRecord.toLocalCheckIn(): CheckInEntity? {
        val personId = personIdFor(account) ?: return null
        return CheckInEntity(
            date = date,
            personId = personId,
            note = note,
            goal = goal,
            imageBase64 = imageBase64,
            timestamp = updatedAt * 1000,
        )
    }

    private fun personIdFor(account: String): String? {
        val group = _group.value ?: return null
        return when (account) {
            group.me?.account -> CareRepository.SELF_ID
            group.partner?.account -> CareRepository.PARTNER_ID
            else -> null
        }
    }

    private fun CareMember.toRemotePartner(): RemotePartner {
        val source = presence
        return RemotePartner(
            account = account,
            nickname = nickname,
            relation = relation,
            deviceType = DeviceType.fromCode(source?.deviceType ?: "PHONE"),
            isDevice = isDevice,
            presence = source?.let {
                RemotePresence(
                    lat = it.lat,
                    lon = it.lon,
                    status = it.status,
                    activityNote = it.activityNote,
                    battery = it.battery,
                    deviceType = it.deviceType,
                    updatedAt = it.updatedAt,
                    online = it.online,
                    distanceM = distanceM,
                    moodEmoji = it.moodEmoji,
                    moodMessage = it.moodMessage,
                )
            },
        )
    }

    private fun CareDevice.toRemoteDevice(): RemoteDevice {
        val source = presence
        return RemoteDevice(
            deviceId = deviceId,
            name = nickname.ifBlank { deviceId },
            relation = relation.ifBlank { "家人" },
            presence = source?.let {
                RemotePresence(
                    lat = it.lat,
                    lon = it.lon,
                    status = it.status,
                    activityNote = it.activityNote,
                    battery = it.battery,
                    deviceType = it.deviceType,
                    updatedAt = it.updatedAt,
                    online = it.online,
                    distanceM = distanceM,
                    moodEmoji = it.moodEmoji,
                    moodMessage = it.moodMessage,
                )
            },
        )
    }

    private companion object {
        const val TAG = "CareSyncRepository"
        const val POLL_INTERVAL_MS = 15_000L
        const val PRESENCE_INTERVAL_MS = 20_000L
        const val STALE_MS = 10 * 60 * 1000L
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/ChatMessageRepository.kt`

````kotlin
﻿package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.ChatMessageDao
import com.shineleong.toughmind.data.local.db.entity.ChatMessageEntity
import kotlinx.coroutines.flow.Flow
import java.time.LocalDate
import java.time.LocalTime

class ChatMessageRepository(private val dao: ChatMessageDao) {
    val messages: Flow<List<ChatMessageEntity>> = dao.observeAll()

    suspend fun insertRemote(
        remoteId: Long,
        text: String,
        fromSelf: Boolean,
        senderName: String,
        createdAt: Long,
    ) {
        if (remoteId <= 0L || dao.findByRemoteId(remoteId) != null) return
        val instant = java.time.Instant.ofEpochSecond(createdAt)
        val zone = java.time.ZoneId.systemDefault()
        val time = instant.atZone(zone).toLocalTime()
        dao.insert(
            ChatMessageEntity(
                remoteId = remoteId,
                senderName = senderName,
                date = instant.atZone(zone).toLocalDate().toString(),
                timeMinutes = time.hour * 60 + time.minute,
                fromSelf = fromSelf,
                text = text,
                createdAt = createdAt * 1000,
            )
        )
    }

    suspend fun maxRemoteId(): Long = dao.maxRemoteId()

    suspend fun send(
        text: String = "",
        imageBase64: String = "",
        audioPath: String = "",
        audioDurationMs: Long = 0L,
        fromSelf: Boolean = true,
    ) {
        val now = LocalTime.now()
        dao.insert(
            ChatMessageEntity(
                date = LocalDate.now().toString(),
                timeMinutes = now.hour * 60 + now.minute,
                fromSelf = fromSelf,
                text = text,
                imageBase64 = imageBase64,
                audioPath = audioPath,
                audioDurationMs = audioDurationMs,
                createdAt = System.currentTimeMillis(),
            )
        )
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/CheckInRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.CheckInDao
import com.shineleong.toughmind.data.local.db.entity.CheckInEntity
import kotlinx.coroutines.flow.Flow

/** 双人打卡仓库。 */
class CheckInRepository(private val checkInDao: CheckInDao) {

    fun observeBetween(start: String, end: String): Flow<List<CheckInEntity>> =
        checkInDao.observeBetween(start, end)

    fun observeDate(date: String): Flow<List<CheckInEntity>> =
        checkInDao.observeDate(date)

    suspend fun checkIn(
        date: String,
        personId: String,
        note: String = "",
        goal: String = "",
        imageBase64: String = "",
    ) {
        checkInDao.upsert(
            CheckInEntity(
                date = date,
                personId = personId,
                note = note,
                goal = goal,
                imageBase64 = imageBase64,
                timestamp = System.currentTimeMillis(),
            )
        )
    }

    suspend fun cancel(date: String, personId: String) {
        checkInDao.delete(date, personId)
    }

    suspend fun toggle(
        date: String,
        personId: String,
        checked: Boolean,
        note: String = "",
        goal: String = "",
        imageBase64: String = "",
    ) {
        if (checked) checkIn(date, personId, note, goal, imageBase64) else cancel(date, personId)
    }

    /** 云端同步时整月替换（仅在已绑定关心组时调用）。 */
    suspend fun replaceBetween(start: String, end: String, records: List<CheckInEntity>) {
        checkInDao.deleteBetween(start, end)
        records.forEach { checkInDao.upsert(it) }
    }

    /** 云端同步单日记录。 */
    suspend fun replaceDate(date: String, records: List<CheckInEntity>) {
        checkInDao.deleteDate(date)
        records.forEach { checkInDao.upsert(it) }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/CheckInTaskRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.CheckInTaskDao
import com.shineleong.toughmind.data.local.db.entity.CheckInTaskEntity
import kotlinx.coroutines.flow.Flow

class CheckInTaskRepository(private val dao: CheckInTaskDao) {

    fun observeDate(date: String): Flow<List<CheckInTaskEntity>> = dao.observeDate(date)
    fun observeBetween(start: String, end: String): Flow<List<CheckInTaskEntity>> =
        dao.observeBetween(start, end)

    suspend fun add(
        date: String,
        title: String,
        imageBase64: String = "",
        createdBy: String = "self",
        remoteId: Long = 0L,
    ): Long {
        val existing = if (remoteId > 0) dao.findByRemoteId(remoteId) else null
        val entity = existing?.copy(
            date = date,
            title = title,
            imageBase64 = imageBase64,
            createdBy = createdBy,
            remoteId = remoteId,
        ) ?: CheckInTaskEntity(
            date = date,
            title = title,
            imageBase64 = imageBase64,
            createdBy = createdBy,
            createdAt = System.currentTimeMillis(),
            remoteId = remoteId,
        )
        return dao.insert(entity)
    }

    suspend fun findByRemoteId(remoteId: Long): CheckInTaskEntity? = dao.findByRemoteId(remoteId)

    suspend fun setSelfDone(task: CheckInTaskEntity, done: Boolean) =
        dao.setSelfDone(task.id, done)

    suspend fun setPartnerDone(task: CheckInTaskEntity, done: Boolean) =
        dao.setPartnerDone(task.id, done)
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/CompanionRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.model.CarePartner
import com.shineleong.toughmind.data.model.DeviceType
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map

/** 亲友绑定信息仓库（昵称 / 关系 / 设备类型 / 演示模式）。 */
class CompanionRepository(private val preferences: Preferences) {

    val companion: Flow<CarePartner> = combine(
        preferences.companionName,
        preferences.companionRelation,
        preferences.companionDeviceType,
        preferences.companionDemoMode,
    ) { name, relation, deviceType, demoMode ->
        CarePartner(
            nickname = name.ifBlank { "TA" },
            relation = relation.ifBlank { "家人" },
            deviceType = DeviceType.fromCode(deviceType),
            demoMode = demoMode,
        )
    }

    suspend fun clear() {
        preferences.clearCompanion()
    }

    suspend fun save(companion: CarePartner) {
        preferences.saveCompanion(
            name = companion.nickname.trim().ifBlank { "TA" },
            relation = companion.relation.ifBlank { "家人" },
            deviceType = companion.deviceType.code,
            demoMode = companion.demoMode,
        )
    }

    fun deviceTypeLabel(): Flow<String> =
        preferences.companionDeviceType.map { DeviceType.fromCode(it).label }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/DeviceRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.dao.DeviceDao
import com.shineleong.toughmind.data.local.db.entity.DeviceEntity
import com.shineleong.toughmind.data.model.DeviceInfo
import com.shineleong.toughmind.data.model.DeviceType
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class DeviceRepository(
    private val deviceDao: DeviceDao,
    private val preferences: Preferences,
) {

    val devices: Flow<List<DeviceInfo>> =
        deviceDao.observeAll().map { list -> list.map { it.toDomain() } }

    val currentDeviceId: Flow<String> = preferences.currentDeviceId

    suspend fun bindDevice(
        deviceId: String,
        deviceName: String = "",
        deviceType: DeviceType = DeviceType.ESP32,
    ) {
        deviceDao.upsert(
            DeviceEntity(
                deviceId = deviceId,
                deviceName = deviceName.ifBlank { deviceId },
                deviceType = deviceType.code,
                bindTime = System.currentTimeMillis(),
                lastOnlineTime = 0L,
                isOnline = false,
            )
        )
        if (preferences.getCurrentDeviceId().isBlank()) {
            preferences.saveCurrentDeviceId(deviceId)
        }
    }

    suspend fun unbind(deviceId: String) {
        deviceDao.delete(deviceId)
        if (preferences.getCurrentDeviceId() == deviceId) {
            preferences.saveCurrentDeviceId("")
        }
    }

    suspend fun setCurrentDevice(deviceId: String) {
        preferences.saveCurrentDeviceId(deviceId)
    }

    suspend fun updateOnline(deviceId: String, online: Boolean, time: Long) {
        deviceDao.updateOnline(deviceId, online, time)
    }

    private fun DeviceEntity.toDomain() = DeviceInfo(
        deviceId = deviceId,
        deviceName = deviceName,
        deviceType = DeviceType.fromCode(deviceType),
        bindTime = bindTime,
        lastOnlineTime = lastOnlineTime,
        isOnline = isOnline,
    )
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/EventRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.EventDao
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import kotlinx.coroutines.flow.Flow

class EventRepository(private val eventDao: EventDao) {

    fun observeEvents(deviceId: String, start: Long, end: Long): Flow<List<EventEntity>> =
        eventDao.observeEvents(deviceId, start, end)

    suspend fun getEvent(id: Long): EventEntity? = eventDao.getById(id)

    suspend fun insert(event: EventEntity) {
        eventDao.insert(event)
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/LocationRepository.kt`

> 百度定位 + 罗盘朝向 + 精度加权平滑与瞬移过滤。

````kotlin
package com.shineleong.toughmind.data.repository

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import com.baidu.location.BDAbstractLocationListener
import com.baidu.location.BDLocation
import com.baidu.location.LocationClient
import com.baidu.location.LocationClientOption
import com.shineleong.toughmind.data.model.SelfLocation
import com.shineleong.toughmind.data.sensor.CompassHeading
import com.shineleong.toughmind.util.GeoMath
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * 亲属端（本机）定位仓库：通过百度定位 SDK（融合 GPS + 基站 + WiFi）获取当前位置。
 * 相比系统 LocationManager，冷启动更快、精度更高，且返回 bd09ll 坐标与百度地图一致（标记无偏移）。
 *
 * 朝向优先取手机罗盘（静止也有效），没有罗盘时才退回百度定位的 GPS 航向。
 */
class LocationRepository(context: Context) {

    private val appContext = context.applicationContext

    private val _selfLocation = MutableStateFlow<SelfLocation?>(null)
    val selfLocation: StateFlow<SelfLocation?> = _selfLocation.asStateFlow()

    /** 今天走过的轨迹，用于地图上的路线；只保存在内存，跨天自动清空。 */
    private val _trail = MutableStateFlow<List<SelfLocation>>(emptyList())
    val trail: StateFlow<List<SelfLocation>> = _trail.asStateFlow()
    private var trailDate = java.time.LocalDate.now()

    private var client: LocationClient? = null
    private val compass = CompassHeading(appContext)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private var compassJob: Job? = null

    fun hasPermission(): Boolean =
        ContextCompat.checkSelfPermission(appContext, Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(appContext, Manifest.permission.ACCESS_COARSE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED

    @SuppressLint("MissingPermission")
    fun start() {
        if (!hasPermission()) return
        if (client != null) return

        val locationClient = LocationClient(appContext)
        val option = LocationClientOption()
        option.setLocationMode(LocationClientOption.LocationMode.Hight_Accuracy)
        option.setCoorType("bd09ll")
        option.setScanSpan(1_000)
        option.setIsNeedAddress(false)
        locationClient.setLocOption(option)
        locationClient.registerLocationListener(listener)
        locationClient.start()
        client = locationClient

        compass.start()
        compassJob = scope.launch {
            compass.heading.collect { value ->
                val current = _selfLocation.value ?: return@collect
                if (value != null) {
                    _selfLocation.value = current.copy(
                        heading = GeoMath.smoothHeadingOrNull(current.heading, value, 0.55f),
                    )
                }
            }
        }
    }

    fun stop() {
        client?.stop()
        client = null
        compassJob?.cancel()
        compassJob = null
        compass.stop()
    }

    private val listener = object : BDAbstractLocationListener() {
        override fun onReceiveLocation(location: BDLocation?) {
            if (location == null) return
            val valid = location.locType == BDLocation.TypeGpsLocation ||
                location.locType == BDLocation.TypeNetWorkLocation ||
                location.locType == BDLocation.TypeOffLineLocation
            if (!valid) return

            val current = _selfLocation.value
            val now = System.currentTimeMillis()
            val raw = location.toSelfLocation()
            if (current == null) {
                _selfLocation.value = raw
                recordTrail(raw)
                return
            }
            val elapsedSeconds = ((now - current.timestamp).coerceAtLeast(1L)) / 1000.0
            if (elapsedSeconds < 0.5) return
            val moved = GeoMath.distanceMeters(current.lat, current.lon, raw.lat, raw.lon)
            // 只拦截明显瞬移；不要用 80m 阈值把正常移动过滤掉。
            if (moved > 1_000.0) return
            val gpsGood = location.locType == BDLocation.TypeGpsLocation && location.radius <= 25f
            val alpha = when {
                gpsGood && moved > 6.0 -> 0.92f
                gpsGood -> 0.55f
                location.radius <= 25f -> 0.65f
                location.radius <= 50f -> 0.40f
                else -> 0.22f
            }
            val measuredSpeed = if (location.speed > 0f) {
                location.speed * 3.6
            } else {
                (moved / elapsedSeconds) * 3.6
            }
            val next = SelfLocation(
                lat = current.lat + (raw.lat - current.lat) * alpha,
                lon = current.lon + (raw.lon - current.lon) * alpha,
                speedKmh = measuredSpeed,
                accuracy = if (gpsGood) location.radius else current.accuracy * 0.5f + location.radius * 0.5f,
                heading = compass.heading.value?.let {
                    GeoMath.smoothHeadingOrNull(current.heading, it, 0.55f)
                } ?: GeoMath.smoothHeadingOrNull(current.heading, gpsCourse(location.direction)),
                timestamp = now,
            )
            _selfLocation.value = next
            recordTrail(if (gpsGood) raw else next)
        }
    }

    private fun recordTrail(point: SelfLocation) {
        val today = java.time.LocalDate.now()
        if (today != trailDate) {
            trailDate = today
            _trail.value = emptyList()
        }
        val list = _trail.value
        val last = list.lastOrNull()
        if (last != null) {
            val moved = GeoMath.distanceMeters(last.lat, last.lon, point.lat, point.lon)
            if (moved < 8.0 && point.timestamp - last.timestamp < 20_000L) return
        }
        _trail.value = (list + point).takeLast(500)
    }

    private fun BDLocation.toSelfLocation() = SelfLocation(
        lat = latitude,
        lon = longitude,
        speedKmh = speed * 3.6,
        accuracy = radius,
        heading = compass.heading.value ?: gpsCourse(direction),
        timestamp = System.currentTimeMillis(),
    )

    /** 百度定位的 direction 是行进方向，0 通常表示未知；取不到罗盘时才用它兜底。 */
    private fun gpsCourse(direction: Float): Float? =
        direction.takeIf { it.isFinite() && it > 0f }?.let { GeoMath.normalizeHeading(it) }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/MqttRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import android.util.Log
import com.shineleong.toughmind.data.local.Preferences
import com.shineleong.toughmind.data.local.db.entity.AdviceEntity
import com.shineleong.toughmind.data.local.db.entity.EventEntity
import com.shineleong.toughmind.data.model.AdviceDto
import com.shineleong.toughmind.data.model.AlarmDto
import com.shineleong.toughmind.data.model.AlarmEvent
import com.shineleong.toughmind.data.model.DriverState
import com.shineleong.toughmind.data.model.DriverStateDto
import com.shineleong.toughmind.data.model.GpsDto
import com.shineleong.toughmind.data.model.GpsPosition
import com.shineleong.toughmind.data.model.toDomain
import com.shineleong.toughmind.data.remote.ConnectionState
import com.shineleong.toughmind.data.remote.HmacVerifier
import com.shineleong.toughmind.data.remote.MqttClientManager
import com.shineleong.toughmind.data.remote.MqttTopics
import com.shineleong.toughmind.data.remote.ReceivedMessage
import com.shineleong.toughmind.service.NotificationHelper
import com.squareup.moshi.Moshi
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * MQTT 实时数据仓库：订阅各主题、解析载荷、校验签名、持久化事件并触发告警通知。
 */
class MqttRepository(
    private val mqttClientManager: MqttClientManager,
    moshi: Moshi,
    private val hmacKey: String,
    private val eventRepository: EventRepository,
    private val adviceRepository: AdviceRepository,
    private val deviceRepository: DeviceRepository,
    private val notificationHelper: NotificationHelper,
    private val preferences: Preferences,
) {

    private val driverStateAdapter = moshi.adapter(DriverStateDto::class.java)
    private val gpsAdapter = moshi.adapter(GpsDto::class.java)
    private val alarmAdapter = moshi.adapter(AlarmDto::class.java)
    private val adviceAdapter = moshi.adapter(AdviceDto::class.java)

    private val _latestState = MutableStateFlow<DriverState?>(null)
    val latestState: StateFlow<DriverState?> = _latestState.asStateFlow()

    private val _latestPosition = MutableStateFlow<GpsPosition?>(null)
    val latestPosition: StateFlow<GpsPosition?> = _latestPosition.asStateFlow()

    private val _latestAlarm = MutableStateFlow<AlarmEvent?>(null)
    val latestAlarm: StateFlow<AlarmEvent?> = _latestAlarm.asStateFlow()

    val connectionState: StateFlow<ConnectionState> = mqttClientManager.connectionState

    private var scope: CoroutineScope? = null

    fun start() {
        if (scope != null) return
        val newScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
        scope = newScope
        newScope.launch {
            mqttClientManager.messages.collect { handleMessage(it) }
        }
        newScope.launch {
            while (isActive) {
                if (mqttClientManager.connectionState.value == ConnectionState.DISCONNECTED) {
                    runCatching { mqttClientManager.connect() }
                }
                delay(3000L)
            }
        }
    }

    fun stop() {
        scope?.cancel()
        scope = null
        mqttClientManager.disconnect()
    }

    fun publishDownlink(payload: String) {
        mqttClientManager.publish(MqttTopics.CMD_DOWNLINK, payload)
    }

    private suspend fun handleMessage(message: ReceivedMessage) {
        try {
            when (message.topic) {
                MqttTopics.DRIVER_STATE -> onDriverState(message.payload)
                MqttTopics.GPS_POSITION -> onGps(message.payload)
                MqttTopics.ALARM_URGENT -> onAlarm(message.payload)
                MqttTopics.LLM_ADVICE -> onAdvice(message.payload)
            }
        } catch (e: Exception) {
            Log.w(TAG, "处理消息失败 topic=${message.topic}", e)
        }
    }

    private suspend fun onDriverState(payload: String) {
        val dto = driverStateAdapter.fromJson(payload) ?: return
        checkHmac(payload, dto.hmac)
        val state = dto.toDomain()
        _latestState.value = state
        deviceRepository.updateOnline(state.deviceId, true, state.timestamp)
        eventRepository.insert(state.toEventEntity())
    }

    private suspend fun onGps(payload: String) {
        val dto = gpsAdapter.fromJson(payload) ?: return
        checkHmac(payload, dto.hmac)
        _latestPosition.value = dto.toDomain()
    }

    private suspend fun onAlarm(payload: String) {
        val dto = alarmAdapter.fromJson(payload) ?: return
        checkHmac(payload, dto.hmac)
        val event = dto.toDomain()
        _latestAlarm.value = event
        eventRepository.insert(event.toEventEntity())
        if (preferences.notificationEnabled.first()) {
            notificationHelper.notifyAlarm(event)
        }
    }

    private suspend fun onAdvice(payload: String) {
        val dto = adviceAdapter.fromJson(payload) ?: return
        checkHmac(payload, dto.hmac)
        val advice = dto.toDomain()
        adviceRepository.insert(
            AdviceEntity(
                deviceId = advice.deviceId,
                content = advice.content,
                timestamp = advice.timestamp,
                kind = advice.kind,
            )
        )
    }

    private fun checkHmac(payload: String, expected: String?) {
        if (expected.isNullOrBlank()) return
        val ok = HmacVerifier.verify(payload, hmacKey, expected)
        if (!ok) {
            Log.w(TAG, "HMAC 校验未通过（请确认与设备端签名规范一致）")
        }
    }

    private fun DriverState.toEventEntity() = EventEntity(
        deviceId = deviceId,
        type = "state",
        level = fatigueLevel.code,
        fatigueScore = fatigueScore,
        perclos = perclos,
        yawnTotal = yawnTotal,
        headDistracted = headDistracted,
        lat = lat,
        lon = lon,
        speed = speedKmh,
        temperature = temperature,
        medicalLevel = medicalLevel,
        medicalType = medicalType.code,
        message = "",
        timestamp = timestamp,
    )

    private fun AlarmEvent.toEventEntity() = EventEntity(
        deviceId = deviceId,
        type = if (medicalLevel >= 1) "medical" else "alarm",
        level = level.code,
        fatigueScore = 0.0,
        perclos = 0.0,
        yawnTotal = 0,
        headDistracted = false,
        lat = lat,
        lon = lon,
        speed = 0.0,
        temperature = 0.0,
        medicalLevel = medicalLevel,
        medicalType = medicalType.code,
        message = message,
        timestamp = timestamp,
    )

    private companion object {
        const val TAG = "MqttRepository"
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/ReminderRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.ReminderDao
import com.shineleong.toughmind.data.local.db.entity.ReminderEntity
import com.shineleong.toughmind.service.ReminderScheduler
import kotlinx.coroutines.flow.Flow
import java.time.LocalDate

/** 日历提醒仓库：数据库持久化 + AlarmManager 调度保持一致。 */
class ReminderRepository(
    private val reminderDao: ReminderDao,
    private val scheduler: ReminderScheduler,
) {

    fun observeBetween(start: String, end: String): Flow<List<ReminderEntity>> =
        reminderDao.observeBetween(start, end)

    fun observeDate(date: String): Flow<List<ReminderEntity>> =
        reminderDao.observeDate(date)

    suspend fun add(
        date: String,
        timeMinutes: Int,
        title: String,
        note: String = "",
        remoteId: Long = 0L,
        type: String = ReminderEntity.TYPE_SCHEDULE,
    ): Long {
        val entity = ReminderEntity(
            date = date,
            timeMinutes = timeMinutes.coerceIn(0, 24 * 60 - 1),
            title = title.trim().ifBlank { "念安提醒" },
            note = note.trim(),
            enabled = true,
            createdAt = System.currentTimeMillis(),
            remoteId = remoteId,
            type = type,
        )
        val id = reminderDao.insert(entity)
        scheduler.schedule(entity.copy(id = id))
        return id
    }

    suspend fun setEnabled(reminder: ReminderEntity, enabled: Boolean) {
        val updated = reminder.copy(enabled = enabled)
        reminderDao.update(updated)
        if (enabled) scheduler.schedule(updated) else scheduler.cancel(updated.id)
    }

    suspend fun delete(reminder: ReminderEntity) {
        scheduler.cancel(reminder.id)
        reminderDao.delete(reminder)
    }

    /** 云端提醒落库：同一个 remoteId 只保留一条本地记录，并重新登记闹钟。 */
    suspend fun upsertSynced(
        remoteId: Long,
        date: String,
        timeMinutes: Int,
        title: String,
        note: String,
        enabled: Boolean,
        type: String = ReminderEntity.TYPE_SCHEDULE,
    ): ReminderEntity {
        val existing = reminderDao.findByRemoteId(remoteId)
        var entity = existing?.copy(
            date = date,
            timeMinutes = timeMinutes.coerceIn(0, 24 * 60 - 1),
            title = title,
            note = note,
            enabled = enabled,
            type = type,
        ) ?: ReminderEntity(
            date = date,
            timeMinutes = timeMinutes.coerceIn(0, 24 * 60 - 1),
            title = title,
            note = note,
            enabled = enabled,
            createdAt = System.currentTimeMillis(),
            remoteId = remoteId,
            type = type,
        )
        if (existing != null) {
            reminderDao.update(entity)
        } else {
            val id = reminderDao.insert(entity)
            entity = entity.copy(id = id)
        }
        if (entity.enabled) scheduler.schedule(entity) else scheduler.cancel(entity.id)
        return entity
    }

    /** 删除本月中云端已不存在的提醒（只处理 remoteId != 0 的记录）。 */
    suspend fun pruneSynced(start: String, end: String, keepRemoteIds: Set<Long>) {
        reminderDao.syncedBetween(start, end).forEach { reminder ->
            if (reminder.remoteId !in keepRemoteIds) {
                scheduler.cancel(reminder.id)
                reminderDao.delete(reminder)
            }
        }
    }

    suspend fun deleteByRemoteId(remoteId: Long) {
        val existing = reminderDao.findByRemoteId(remoteId) ?: return
        scheduler.cancel(existing.id)
        reminderDao.delete(existing)
    }

    /** 应用启动时补登记未来提醒（服务被系统清理后恢复）。 */
    suspend fun rescheduleAll() {
        val today = LocalDate.now().toString()
        reminderDao.enabledFrom(today).forEach { scheduler.schedule(it) }
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/SchedulePostRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.SchedulePostDao
import com.shineleong.toughmind.data.local.db.entity.SchedulePostEntity
import kotlinx.coroutines.flow.Flow

class SchedulePostRepository(private val dao: SchedulePostDao) {

    fun observeBetween(start: String, end: String): Flow<List<SchedulePostEntity>> =
        dao.observeBetween(start, end)

    fun observeDate(date: String): Flow<List<SchedulePostEntity>> = dao.observeDate(date)

    suspend fun add(
        date: String,
        timeMinutes: Int,
        content: String,
        imageBase64: String,
        authorId: String,
        remoteId: Long = 0L,
    ): Long {
        val existing = if (remoteId > 0L) dao.findByRemoteId(remoteId) else null
        val entity = existing?.copy(
            date = date,
            timeMinutes = timeMinutes.coerceIn(0, 24 * 60 - 1),
            content = content,
            imageBase64 = imageBase64,
            authorId = authorId,
            remoteId = remoteId,
        ) ?: SchedulePostEntity(
            date = date,
            timeMinutes = timeMinutes.coerceIn(0, 24 * 60 - 1),
            content = content,
            imageBase64 = imageBase64,
            authorId = authorId,
            createdAt = System.currentTimeMillis(),
            remoteId = remoteId,
        )
        return dao.insert(entity)
    }

    suspend fun replaceBetween(start: String, end: String, posts: List<SchedulePostEntity>) {
        dao.deleteBetween(start, end)
        posts.forEach { dao.insert(it) }
    }

    suspend fun delete(post: SchedulePostEntity) {
        if (post.remoteId != 0L) dao.deleteByRemoteId(post.remoteId) else dao.delete(post.id)
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/WeatherRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import android.util.Log
import com.shineleong.toughmind.data.model.WeatherInfo
import com.shineleong.toughmind.data.remote.WeatherApi
import com.shineleong.toughmind.data.remote.toDomain
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.round

/**
 * 双方天气仓库：根据经纬度请求 Open-Meteo 当前天气，并按约 2km 网格缓存 10 分钟。
 * 没有网络 / 接口异常时返回 null，不影响地图与打卡等核心功能。
 */
class WeatherRepository(private val api: WeatherApi) {

    private data class CacheEntry(val weather: WeatherInfo, val fetchedAt: Long)

    private val cache = ConcurrentHashMap<String, CacheEntry>()

    suspend fun weatherAt(lat: Double, lon: Double): WeatherInfo? {
        if (!hasValidPosition(lat, lon)) return null
        val key = "%d_%d".format(round(lat * 50).toInt(), round(lon * 50).toInt())
        val now = System.currentTimeMillis()
        cache[key]?.let { entry ->
            if (now - entry.fetchedAt < CACHE_TTL_MS) return entry.weather
        }
        return try {
            val response = api.current(
                latitude = lat,
                longitude = lon,
                current = CURRENT_FIELDS,
                timezone = "auto",
            )
            val weather = response.current?.toDomain()
            if (weather != null) {
                cache[key] = CacheEntry(weather, now)
            }
            weather
        } catch (e: Exception) {
            Log.w(TAG, "获取天气失败 lat=$lat lon=$lon", e)
            cache[key]?.weather
        }
    }

    private fun hasValidPosition(lat: Double, lon: Double): Boolean =
        lat != 0.0 || lon != 0.0

    private companion object {
        const val TAG = "WeatherRepository"
        const val CACHE_TTL_MS = 10 * 60 * 1000L
        const val CURRENT_FIELDS =
            "temperature_2m,apparent_temperature,weather_code,relative_humidity_2m,wind_speed_10m,is_day"
        const val BASE_URL = "https://api.open-meteo.com/"
    }
}
````

### `app/src/main/java/com/shineleong/toughmind/data/repository/XiaozhiRepository.kt`

````kotlin
package com.shineleong.toughmind.data.repository

import com.shineleong.toughmind.data.local.db.dao.XiaozhiMessageDao
import com.shineleong.toughmind.data.local.db.entity.XiaozhiMessageEntity
import com.shineleong.toughmind.data.model.XiaozhiContext
import com.shineleong.toughmind.data.model.XiaozhiReply
import com.shineleong.toughmind.data.model.XiaozhiTurn
import com.shineleong.toughmind.data.remote.XiaozhiChatService
import kotlinx.coroutines.flow.Flow

/** 小智对话仓库：持久化消息、拼接上下文、调用对话服务。 */
class XiaozhiRepository(
    private val dao: XiaozhiMessageDao,
    private val chatService: XiaozhiChatService,
) {
    val messages: Flow<List<XiaozhiMessageEntity>> = dao.observeAll()

    suspend fun send(input: String, context: XiaozhiContext, english: Boolean = false): XiaozhiReply {
        val text = input.trim()
        val history = dao.recent(HISTORY_TURNS)
            .asReversed()
            .map { XiaozhiTurn(role = it.role, text = it.text) }

        val now = System.currentTimeMillis()
        dao.insert(
            XiaozhiMessageEntity(
                role = ROLE_USER,
                text = text,
                createdAt = now,
                source = "user",
            )
        )

        val reply = chatService.reply(history, text, context, english)
        dao.insert(
            XiaozhiMessageEntity(
                role = ROLE_ASSISTANT,
                text = reply.text,
                createdAt = now + 1,
                source = if (reply.fromRemote) "remote" else "local",
            )
        )
        dao.trim(KEEP_MESSAGES)
        return reply
    }

    /** 发生异常时给用户一句可继续的话，避免输入框「石沉大海」。 */
    suspend fun appendAssistant(text: String) {
        dao.insert(
            XiaozhiMessageEntity(
                role = ROLE_ASSISTANT,
                text = text,
                createdAt = System.currentTimeMillis(),
                source = "local",
            )
        )
    }

    suspend fun clear() = dao.clear()

    private companion object {
        const val ROLE_USER = "user"
        const val ROLE_ASSISTANT = "assistant"
        const val HISTORY_TURNS = 8
        const val KEEP_MESSAGES = 100
    }
}
````

<a id="s01-6"></a>

## 步骤 01.6 · 传感器

`CompassHeading` 将地磁传感器读数平滑为地图头像朝向。

本步骤涉及的文件：

- `app/src/main/java/com/shineleong/toughmind/data/sensor/CompassHeading.kt`

### `app/src/main/java/com/shineleong/toughmind/data/sensor/CompassHeading.kt`

````kotlin
package com.shineleong.toughmind.data.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.SystemClock
import android.view.Surface
import android.view.WindowManager
import com.shineleong.toughmind.util.GeoMath
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlin.math.abs

/**
 * 手机朝向（罗盘）传感器。
 *
 * 百度定位返回的 `direction` 是“行进方向”，站着不动时通常是 0；这里改用
 * `TYPE_ROTATION_VECTOR`（加速度 + 磁力 + 陀螺）算出手机顶部指向的方位角，
 * 即使静止也能像百度地图一样显示朝向。
 *
 * 输出相对于当前屏幕方向，已按屏幕旋转重新映射，0° 为正北。
 */
class CompassHeading(context: Context) : SensorEventListener {

    private val appContext = context.applicationContext
    private val sensorManager =
        appContext.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val windowManager =
        appContext.getSystemService(Context.WINDOW_SERVICE) as WindowManager

    private val rotationSensor =
        sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
            ?: sensorManager.getDefaultSensor(Sensor.TYPE_GEOMAGNETIC_ROTATION_VECTOR)

    private val _heading = MutableStateFlow<Float?>(null)
    val heading: StateFlow<Float?> = _heading.asStateFlow()

    val available: Boolean get() = rotationSensor != null

    private val rotationMatrix = FloatArray(9)
    private val remappedMatrix = FloatArray(9)
    private val orientation = FloatArray(3)
    private var running = false
    private var lastEmitAt = 0L
    private var lastDegrees = Float.NaN

    fun start() {
        val sensor = rotationSensor ?: return
        if (running) return
        running = true
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_UI)
    }

    fun stop() {
        if (!running) return
        running = false
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != rotationSensor?.type) return
        SensorManager.getRotationMatrixFromVector(rotationMatrix, event.values)
        val (axisX, axisY) = remapAxes()
        SensorManager.remapCoordinateSystem(rotationMatrix, axisX, axisY, remappedMatrix)
        SensorManager.getOrientation(remappedMatrix, orientation)
        val degrees = GeoMath.normalizeCompass(
            Math.toDegrees(orientation[0].toDouble()).toFloat(),
        )

        val now = SystemClock.elapsedRealtime()
        val changed = if (lastDegrees.isNaN()) 180f else abs(shortestDelta(lastDegrees, degrees))
        if (now - lastEmitAt < 120L) return
        if (changed < 1.5f) return
        lastEmitAt = now
        lastDegrees = degrees
        _heading.value = degrees
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    @Suppress("DEPRECATION")
    private fun remapAxes(): Pair<Int, Int> = when (windowManager.defaultDisplay.rotation) {
        Surface.ROTATION_90 -> SensorManager.AXIS_Y to SensorManager.AXIS_MINUS_X
        Surface.ROTATION_180 -> SensorManager.AXIS_MINUS_X to SensorManager.AXIS_MINUS_Y
        Surface.ROTATION_270 -> SensorManager.AXIS_MINUS_Y to SensorManager.AXIS_X
        else -> SensorManager.AXIS_X to SensorManager.AXIS_Y
    }

    private fun shortestDelta(from: Float, to: Float): Float =
        ((to - from + 540f) % 360f) - 180f
}
````

---

返回索引：[README.md](README.md)
