# I2C 通信学习笔记（含 EEPROM 应用）
## 一、I2C 核心定义与核心特性
### 1. 基本定义
I2C（Inter-Integrated Circuit，集成电路间总线）是一种**双线同步串行通信协议**，由 SDA（Serial Data，串行数据线）和 SCL（Serial Clock，串行时钟线）两根信号线组成，支持多主设备和多从设备通信，广泛应用于嵌入式系统中芯片间的数据传输（如 EEPROM、传感器、LCD 模块等外设与 MCU 的通信）。

### 2. 核心特性
| 特性                | 说明                                                                 |
|---------------------|----------------------------------------------------------------------|
| 双线通信             | 仅需 SDA（数据线）和 SCL（时钟线），布线简洁，节省 GPIO 资源。         |
| 多主多从架构         | 总线可挂载多个主设备和从设备，通过从设备地址区分不同设备，无需片选线。 |
| 同步通信             | 由主设备产生时钟信号（SCL）同步数据传输，传输速率稳定，可靠性高。     |
| 总线仲裁机制         | 多个主设备同时发起通信时，通过总线仲裁避免冲突，保障通信有序进行。     |
| 双向传输             | SDA 线既可发送数据也可接收数据，支持主设备与从设备间的双向数据交互。 |

### 3. 典型应用场景
- 存储扩展：与 EEPROM（电可擦可编程只读存储器）通信，实现数据掉电保存（文档核心应用场景）。
- 传感器数据采集：连接温湿度传感器、光照传感器等，传输采集到的数字信号。
- 外设控制：控制 LCD 显示模块、音频芯片、电源管理芯片等外设的工作状态。

## 二、I2C 硬件设计要点（结合 EEPROM 应用）
### 1. 核心硬件组成（文档明确提及）
| 硬件单元       | 功能说明                                                                 |
|----------------|--------------------------------------------------------------------------|
| Vcc            | 电源引脚，为 I2C 外设（如 EEPROM）提供工作电压（需匹配外设额定电压）。     |
| GND            | 地引脚，保障电源回路和信号参考地，需与 MCU 共地，减少干扰。               |
| SDA（SDA0）    | 串行数据线，用于主从设备间的数据传输，文档中标识为“IKSDA0”，需配置为开漏输出模式。 |
| SCL            | 串行时钟线，由主设备产生时钟信号，同步数据传输（文档未明确标识，为 I2C 标准引脚）。 |
| SA0/SA1        | 从设备地址选择引脚（文档中提及“SAOTO”，推测为 SA0 引脚），通过拉高/拉低配置 EEPROM 的从地址，实现多 EEPROM 挂载。 |
| 上拉电阻       | SDA 和 SCL 线需外接 4.7KΩ~10KΩ 上拉电阻至 Vcc，确保总线空闲时为高电平，避免信号漂浮（I2C 协议强制要求）。 |

### 2. 硬件连接规范
- 总线拓扑：所有设备的 SDA 引脚连接到同一根 SDA 线，所有设备的 SCL 引脚连接到同一根 SCL 线，形成总线结构。
- 电源与地线：Vcc 需稳定供电，可添加 0.1μF 旁路电容滤除电源噪声；GND 需单点接地，避免地环路干扰。
- 地址配置：通过 SA0/SA1 引脚的电平组合（高/低）配置 EEPROM 从地址，确保总线上每个从设备地址唯一（如 SA0=0 时地址为 0xA0，SA0=1 时地址为 0xA2）。
- 引脚复用：若 MCU 的 SDA/SCL 引脚为复用功能，需在硬件设计时确认引脚功能，避免与其他外设冲突。

### 3. 抗干扰设计
- 上拉电阻选型：根据总线长度和传输速率选择合适的上拉电阻，短线传输（<1m）优先选用 4.7KΩ，长线传输可选用 10KΩ。
- 总线保护：可在 SDA/SCL 线串联 TVS 管或限流电阻，防止静电或过流损坏设备。
- 布线要求：SDA 和 SCL 线需平行布线，长度尽量短，远离电源线和高速数字信号线，减少电磁干扰。

## 三、I2C 通信协议核心流程
### 1. 总线状态定义（协议基础）
| 状态           | 定义与实现方式                                                         |
|----------------|------------------------------------------------------------------------|
| 空闲状态       | SDA 和 SCL 均为高电平，总线无数据传输。                                 |
| 起始条件（S）  | 主设备在 SCL 为高电平时，将 SDA 从高电平拉低至低电平，标志通信开始。   |
| 停止条件（P）  | 主设备在 SCL 为高电平时，将 SDA 从低电平拉高至高电平，标志通信结束。   |
| 数据位传输     | SCL 为高电平时，SDA 线电平保持稳定（高电平为 1，低电平为 0），主从设备采样数据；SCL 为低电平时，SDA 线可切换电平准备下一位数据。 |
| 应答位（ACK）  | 每传输 8 位数据后，接收设备需在第 9 个时钟周期将 SDA 拉低，表示数据接收成功（应答）；若 SDA 保持高电平，则为非应答（NACK），主设备可终止传输。 |

### 2. 核心通信流程（以 EEPROM 读写为例）
#### （1）EEPROM 写操作流程
1. 主设备发送**起始条件（S）**，启动 I2C 总线通信。
2. 主设备发送**EEPROM 写地址**（7 位从地址 + 1 位写控制位 0，如 SA0=0 时地址为 0xA0）。
3. 主设备释放 SDA，等待 EEPROM 发送**应答位（ACK）**，确认 EEPROM 已接收地址。
4. 主设备发送**数据存储地址**（EEPROM 内部存储单元的地址，如 0x00 表示第一个存储单元），等待 EEPROM 应答。
5. 主设备发送**待写入数据**（8 位数据），等待 EEPROM 应答（可连续发送多个数据，EEPROM 自动递增存储地址）。
6. 主设备发送**停止条件（P）**，结束写操作，EEPROM 内部执行数据写入（需一定时间，期间总线需保持空闲）。

#### （2）EEPROM 读操作流程
1. 主设备发送**起始条件（S）**。
2. 主设备发送**EEPROM 写地址**（7 位从地址 + 写控制位 0），等待 EEPROM 应答。
3. 主设备发送**数据存储地址**（需读取的 EEPROM 内部地址），等待 EEPROM 应答。
4. 主设备发送**重复起始条件（Sr）**（不发送停止条件，重新启动总线）。
5. 主设备发送**EEPROM 读地址**（7 位从地址 + 读控制位 1，如 0xA1），等待 EEPROM 应答。
6. EEPROM 发送**存储数据**（8 位），主设备接收后发送**非应答位（NACK）**（表示无需继续读取）。
7. 主设备发送**停止条件（P）**，结束读操作，完成数据读取。

### 3. 传输速率等级
- 标准模式（Standard-mode）：100Kbps，适用于大多数低速外设（如 EEPROM）。
- 快速模式（Fast-mode）：400Kbps，适用于高速数据传输场景。
- 高速模式（High-speed mode）：3.4Mbps，适用于对传输速率要求较高的外设。
（文档未明确指定速率，默认推荐使用标准模式 100Kbps 保证兼容性）

## 四、I2C 软件设计流程（基于 MCU 编程）
### 1. 核心初始化步骤
#### （1）使能 I2C 时钟与 GPIO 时钟
- 功能：为 I2C 外设和 SDA/SCL 对应的 GPIO 引脚提供时钟支持（以 STM32 为例）。
- 代码示例：
```c
// 使能 I2C1 时钟和 GPIOB 时钟（假设 SDA=PB7，SCL=PB6）
RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);
RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
```

#### （2）配置 GPIO 引脚为 I2C 复用模式
- 功能：将 SDA 和 SCL 引脚配置为开漏输出的复用功能，满足 I2C 总线要求。
- 代码示例：
```c
GPIO_InitTypeDef GPIO_InitStruct;
// 配置 PB6（SCL）和 PB7（SDA）为复用开漏输出
GPIO_InitStruct.GPIO_Pin = GPIO_Pin_6 | GPIO_Pin_7;
GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_OD; // 复用开漏输出
GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
GPIO_Init(GPIOB, &GPIO_InitStruct);
```

#### （3）初始化 I2C 参数
- 功能：配置 I2C 通信速率、地址模式、应答使能等核心参数。
- 代码示例：
```c
I2C_InitTypeDef I2C_InitStruct;
// 配置 I2C 时钟频率（100Kbps，假设 APB1 时钟为 36MHz）
I2C_InitStruct.I2C_ClockSpeed = 100000;
// 地址模式：7 位地址（I2C 标准模式）
I2C_InitStruct.I2C_Ack = I2C_Ack_Enable; // 使能应答
I2C_InitStruct.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;
I2C_InitStruct.I2C_DutyCycle = I2C_DutyCycle_2; // 占空比 1:2
I2C_InitStruct.I2C_Mode = I2C_Mode_I2C; // I2C 模式
I2C_InitStruct.I2C_OwnAddress1 = 0x00; // 主设备自身地址（无需时设为 0）
I2C_Init(I2C1, &I2C_InitStruct);
```

#### （4）使能 I2C 外设
- 代码示例：
```c
I2C_Cmd(I2C1, ENABLE); // 使能 I2C1
```

### 2. 核心功能函数实现（EEPROM 读写）
#### （1）I2C 起始条件发送函数
```c
void I2C_Start(I2C_TypeDef* I2Cx) {
    // 等待 I2C 总线空闲
    while (I2C_GetFlagStatus(I2Cx, I2C_FLAG_BUSY));
    // 发送起始条件
    I2C_GenerateSTART(I2Cx, ENABLE);
    // 等待起始条件发送完成
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_MODE_SELECT));
}
```

#### （2）I2C 停止条件发送函数
```c
void I2C_Stop(I2C_TypeDef* I2Cx) {
    // 发送停止条件
    I2C_GenerateSTOP(I2Cx, ENABLE);
    // 等待停止条件发送完成
    while (I2C_GetFlagStatus(I2Cx, I2C_FLAG_STOPF));
}
```

#### （3）EEPROM 写数据函数
```c
// 向 EEPROM 指定地址写入 1 字节数据
// I2Cx：I2C 外设（如 I2C1）
// eepromAddr：EEPROM 从地址（如 0xA0）
// dataAddr：EEPROM 内部数据地址（如 0x00）
// data：待写入数据
void EEPROM_WriteByte(I2C_TypeDef* I2Cx, u8 eepromAddr, u8 dataAddr, u8 data) {
    I2C_Start(I2Cx);
    
    // 发送 EEPROM 写地址
    I2C_SendData(I2Cx, eepromAddr);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_TRANSMITTER_MODE_SELECTED));
    
    // 发送数据存储地址
    I2C_SendData(I2Cx, dataAddr);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_BYTE_TRANSMITTED));
    
    // 发送数据
    I2C_SendData(I2Cx, data);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_BYTE_TRANSMITTED));
    
    I2C_Stop(I2Cx);
    delay_ms(5); // 等待 EEPROM 内部写入完成（根据 EEPROM 手册调整）
}
```

#### （4）EEPROM 读数据函数
```c
// 从 EEPROM 指定地址读取 1 字节数据
u8 EEPROM_ReadByte(I2C_TypeDef* I2Cx, u8 eepromAddr, u8 dataAddr) {
    u8 data = 0;
    
    I2C_Start(I2Cx);
    
    // 发送 EEPROM 写地址（设置读取地址）
    I2C_SendData(I2Cx, eepromAddr);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_TRANSMITTER_MODE_SELECTED));
    
    // 发送数据存储地址
    I2C_SendData(I2Cx, dataAddr);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_BYTE_TRANSMITTED));
    
    // 发送重复起始条件
    I2C_GenerateSTART(I2Cx, ENABLE);
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_MODE_SELECT));
    
    // 发送 EEPROM 读地址
    I2C_SendData(I2Cx, eepromAddr | 0x01); // 读控制位置 1
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_RECEIVER_MODE_SELECTED));
    
    // 禁止应答，准备接收数据
    I2C_AcknowledgeConfig(I2Cx, DISABLE);
    // 发送停止条件（接收最后 1 字节时）
    I2C_GenerateSTOP(I2Cx, ENABLE);
    
    // 接收数据
    while (!I2C_CheckEvent(I2Cx, I2C_EVENT_MASTER_BYTE_RECEIVED));
    data = I2C_ReceiveData(I2Cx);
    
    // 重新使能应答（为下次通信做准备）
    I2C_AcknowledgeConfig(I2Cx, ENABLE);
    
    return data;
}
```

## 五、常见问题与解决方案（结合实操场景）
### 1. 总线无响应，无法与 EEPROM 通信
#### 可能原因
- 上拉电阻未接或阻值错误：SDA/SCL 线无默认高电平，总线无法稳定工作。
- 地址配置错误：SA0/SA1 引脚电平设置与软件中地址不匹配（如硬件 SA0=1，软件地址仍为 0xA0）。
- GPIO 模式配置错误：未将 SDA/SCL 配置为复用开漏输出（如误配置为推挽输出）。
- 电源未供电或供电异常：EEPROM 未上电，无法响应主设备指令。
- 总线短路或虚焊：SDA/SCL 线短路到 GND 或 Vcc，或引脚虚焊导致接触不良。

#### 解决方案
- 检查上拉电阻：确认 SDA 和 SCL 线均外接 4.7KΩ~10KΩ 上拉电阻，且焊接良好。
- 核对地址：测量 SA0/SA1 引脚电平，计算正确的 EEPROM 从地址（7 位地址 + 读写控制位）。
- 修正 GPIO 配置：确保 SDA/SCL 配置为“复用开漏输出”（GPIO_Mode_AF_OD）。
- 检查电源：用万用表测量 EEPROM 的 Vcc 引脚电压，确保符合额定电压（如 3.3V 或 5V）。
- 排查硬件连接：用示波器观察 SDA/SCL 线电平变化，或重新焊接引脚，排除短路、虚焊问题。

### 2. 分盘后 Keil5 工程打不开（间接影响 I2C 开发）
#### 问题原因
分盘导致 I2C 工程依赖的芯片包路径失效或缺失，I2C 初始化函数（如 `I2C_Init`）需芯片包支持。

#### 解决方案（文档验证有效）
- 在线安装芯片包
  1. 打开 Keil5 工程，点击右下角 `Pack Installer`（未响应则点击左上角刷新图标）。
  2. 选择对应芯片型号（如 STM32F103C8、GD32F103C8、MM32F103c8），下载并安装匹配的芯片包。
- 离线安装芯片包
  1. 从开发板供应商获取（如中精灵开发板资料自带芯片包）。
  2. 网络下载（如江大提供的芯片包资源）。
  3. 向他人索要匹配的芯片包，直接导入 Keil5（避免重新解压导致路径错误，文档中提及“重新解压自己的芯片包资料压缩包”为错误方法）。

### 3. 数据读写错误或丢失
#### 可能原因
- 未等待 EEPROM 写入完成：EEPROM 内部写入需要时间（通常几毫秒），主设备未延时直接发起下一次通信，导致数据覆盖或写入失败。
- 总线干扰：电源噪声或外部电磁干扰导致数据传输错误。
- 应答位处理不当：软件未正确等待应答位，或误判应答状态，导致数据传输中断。
- 传输速率过高：超过 EEPROM 支持的最大传输速率（如 EEPROM 仅支持 100Kbps，软件配置为 400Kbps）。

#### 解决方案
- 添加写入延时：在发送停止条件后，添加 5~10ms 延时（根据 EEPROM 数据手册调整），等待内部写入完成。
- 优化抗干扰设计：在 Vcc 引脚添加旁路电容，SDA/SCL 线远离电源线和高速信号线，必要时使用屏蔽线。
- 严格处理应答位：每发送 1 字节数据后，必须等待对应的应答事件（如 `I2C_EVENT_MASTER_BYTE_TRANSMITTED`），避免提前发送下一字节。
- 匹配传输速率：软件配置的 I2C 时钟速率需低于或等于 EEPROM 支持的最大速率，默认推荐 100Kbps。

### 4. 多从设备通信时地址冲突
#### 可能原因
多个 I2C 从设备的地址相同（如两个 EEPROM 的 SA0/SA1 引脚电平完全一致），导致主设备无法区分。

#### 解决方案
- 重新配置从地址：通过调整 SA0/SA1 引脚的电平（拉高或拉低），为每个从设备分配唯一的 7 位地址。
- 使用地址扩展：若从设备支持地址扩展功能，可通过硬件引脚或软件指令配置扩展地址，增加地址数量。

## 六、关键注意事项
1. 应答位必须处理：I2C 协议中，应答位是确认数据传输成功的关键，软件中需严格等待应答事件，避免忽略应答导致通信失败。
2. 总线空闲检查：每次发起通信前，需检查 I2C 总线是否空闲（`I2C_FLAG_BUSY`），避免在总线忙时发送起始条件导致冲突。
3. 地址字节格式：7 位从地址需与 1 位读写控制位（0 为写，1 为读）组合为 8 位字节发送（如 0xA0 为写地址，0xA1 为读地址）。
4. EEPROM 写保护：部分 EEPROM 带有写保护引脚（WP），若需写入数据，需将 WP 引脚拉低；若 WP 拉高，EEPROM 禁止写入。
5. 时钟同步：主设备的 SCL 时钟频率需根据总线电容和传输距离调整，频率过高可能导致信号失真，需通过示波器观察信号波形优化。
6. 软件容错设计：可在软件中添加超时机制（如等待应答时设置最大延时），避免因硬件故障导致程序卡死在等待循环中。