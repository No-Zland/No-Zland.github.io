## 一、USART 核心定义与概念
### 1. 基本定义
USART（Universal Synchronous/Asynchronous Receiver/Transmitter）即通用同步/异步收发器，是一种支持同步和异步通信的串行通信接口，可实现设备间的数据双向传输，广泛应用于嵌入式系统与外设（如电脑、传感器、模块等）的通信场景。

### 2. 通信相关基础概念
| 通信类型 | 定义 |
|----------|------|
| 串行通信 | 数据以 bit 为单位，按顺序逐位传输（文档中提及“0位次传送”，即逐位发送接收） |
| 并行通信 | 多个数据位同时传输，需多根数据线，传输速率快但布线复杂 |
| 异步通信 | 无需时钟信号同步，通过起始位、数据位、校验位、停止位约定帧格式实现同步，灵活性高（USART 核心支持模式） |
| 同步通信 | 需时钟信号（如 SCLK 引脚提供）同步数据传输，传输速率稳定，适用于高速通信 |
| 单工通信 | 仅支持单向数据传输（仅发或仅收） |
| 双工通信 | 支持双向数据传输，USART 可实现“两发两收同时”通信 |

### 3. 与 UART 的区别
- UART（Universal Asynchronous Receiver/Transmitter）：仅支持异步通信，无同步时钟引脚。
- USART：兼容异步通信（等同于 UART 功能）和同步通信，功能更全面，支持时钟信号传输（SCLK 引脚）。

## 二、USART 硬件配置
### 1. 总线归属与引脚定义
USART 接口分属 APB1 和 APB2 总线，不同总线对应的引脚配置不同（核心引脚功能：TX 发送数据、RX 接收数据、SCLK 同步时钟、CTS 清除发送、nRTS 请求发送）：

| 引脚类型       | APB2 总线（USART1） | APB1 总线 | ---    | ---   | ---   |
| ---------- | --------------- | ------- | ------ | ----- | ----- |
|            | USART1          | USART2  | USART3 | UART4 | UART5 |
| TX（发送）     | PA9             | PA2     | PB10   | PC10  | PC12  |
| RX（接收）     | PA10            | PA3     | PB11   | PC11  | PD2   |
| SCLK（同步时钟） | PA8             | PA4     | PB12   | -     | -     |
| CTS（清除发送）  | PA11            | PA0     | PB13   | -     | -     |
| nRTS（请求发送） | PA12            | PA1     | PB14   | -     | -     |

### 2. 地线与信号说明
- PGND（功率地线）：用于负电源回路，保障电源稳定性。
- DGND（数字地）：用于数字信号回路，减少数字信号干扰。
- 外壳线：辅助屏蔽，降低外部电磁干扰。

## 三、USART 软件设计
### 1. 核心配置参数
- 波特率：数据传输速率，文档中提及常用配置（如 9600bps，对应“96-N-8-1”格式中的“96”），需通过初始化函数设置（`u32 bound` 参数）。
- 数据位：默认 8 位（“96-N-8-1”格式中的“8”），可配置 7/8/9 位。
- 校验位：“96-N-8-1”格式中的“N”表示无校验位，支持奇校验（O）、偶校验（E）。
- 停止位：“96-N-8-1”格式中的“1”表示 1 位停止位，可配置 1/1.5/2 位。
- 通信模式：支持“两发两收同时”双向通信，需配置串口中断优先级与数据缓冲区。

### 2. 关键初始化流程
#### （1）定义核心宏与变量
```c
// 定义接收缓冲区长度
#define USART1_REC_LEN  （自定义长度，如 200）
// 接收状态标志位（文档中提及 ODUSART_RX_STA，示例值 0x4000 表示接收完成）
u16 USART1_RX_STA = 0;
// 接收数据缓冲区
u8 USART1_RX_BUF[USART1_REC_LEN];
```

#### （2）初始化函数（`void USART_Init(u32 bound)`）
核心功能：配置时钟、引脚、通信参数、中断等，步骤如下：
1. 使能 USART 时钟与对应 GPIO 时钟（如 APB2 总线 USART1 需使能 APB2 时钟）。
2. 配置 GPIO 引脚模式：TX 引脚为推挽输出，RX 引脚为浮空输入或上拉输入。
3. 配置 USART 通信参数：通过 `USART_InitTypeDef` 结构体设置波特率、数据位、校验位、停止位、硬件流控（CTS/RTS 使能与否）。
4. 使能 USART 外设：`USART_Cmd(USART1, ENABLE);`。
5. 配置接收中断：使能 RXNE（接收数据非空）中断，`USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);`。
6. 配置中断优先级：通过 NVIC 控制器设置 USART 中断优先级分组与优先级值。

#### （3）中断服务函数
核心功能：接收数据并存储到缓冲区，更新接收状态标志位：
```c
void USART1_IRQHandler(void) {
    u8 res;
    // 接收数据非空中断
    if (USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        // 读取接收数据
        res = USART_ReceiveData(USART1);
        // 接收未完成且未溢出
        if ((USART1_RX_STA & 0x8000) == 0 && (USART1_RX_STA < USART1_REC_LEN - 1)) {
            // 存储数据到缓冲区
            USART1_RX_BUF[USART1_RX_STA++] = res;
            // 可添加接收完成判断（如检测到换行符 '\n' 置位 0x8000）
            if (res == '\n') {
                USART1_RX_STA |= 0x8000;
            }
        }
    }
}
```

#### （4）发送函数（可选）
实现数据发送功能，支持字节发送或字符串发送：
```c
// 发送单个字节
void USART_SendByte(USART_TypeDef* USARTx, u8 data) {
    // 等待发送数据寄存器为空
    while (USART_GetFlagStatus(USARTx, USART_FLAG_TXE) == RESET);
    // 发送数据
    USART_SendData(USARTx, data);
}

// 发送字符串
void USART_SendString(USART_TypeDef* USARTx, u8* str) {
    while (*str != '\0') {
        USART_SendByte(USARTx, *str++);
        // 等待发送完成
        while (USART_GetFlagStatus(USARTx, USART_FLAG_TC) == RESET);
    }
}
```

### 3. 关键寄存器与指令
- 使能控制：`USART_Cmd(USART1, ENABLE)`（使能 USART1 外设）。
- 标志位判断：`USART_GetFlagStatus(USARTx, USART_FLAG_TC)`（判断发送完成）、`USART_GetFlagStatus(USARTx, USART_FLAG_RXNE)`（判断接收数据非空）。
- 中断使能：`USART_ITConfig(USARTx, USART_IT_RXNE, ENABLE)`（使能接收中断）。

## 四、通信协议与帧格式
### 1. 核心协议：RS232
USART 常用 RS232 协议进行异步通信，帧格式遵循“96-N-8-1”标准（文档重点提及）：
- 96：波特率 9600bps。
- N：无校验位（No Parity）。
- 8：8 位数据位。
- 1：1 位停止位。

### 2. RS232 信号定义
| 信号名称 | 功能描述 |
|----------|----------|
| TXD（Transmit Data） | 发送数据，从 USART 输出到外设 |
| RXD（Received Data） | 接收数据，从外设输入到 USART |
| RTS（Request To Send） | 请求发送，USART 向外设请求发送数据 |
| CTS（Clear To Send） | 清除发送，外设告知 USART 可发送数据 |
| DTR（Data Terminal Ready） | 数据终端就绪，表明 USART 设备就绪 |
| DSR（Data Set Ready） | 数据设备就绪，表明外设就绪 |

### 3. 流控机制（RTS/CTS）
- RTS/CTS 是硬件流控信号，用于避免数据溢出：
  1. 当 USART 接收缓冲区未满时，置位 RTS（请求发送），告知外设可发送数据。
  2. 当 USART 接收缓冲区即将满时，复位 RTS，告知外设暂停发送。
  3. 外设收到 RTS 后，通过 CTS 回应：CTS 置位表示允许 USART 发送，复位表示禁止。

## 五、常见问题与解决方案（结合实操场景）
### 1. 串口打印中文乱码
#### 问题原因
Keil5 工程编码与串口接收端编码不一致，导致中文解析错误。

#### 解决方案（文档中验证有效的方法）
- 方法 1：编码转换
  1. 用记事本打开工程中的核心文件（如 main.c），以 UTF-8 编码复制内容。
  2. 在 Keil5 中打开该文件，将 Encode 格式改为 Chinese GB2318。
- 方法 2：编译器配置
  在 Keil5 的 C/C++ 页面 Misc Control 行添加指令：`-no-multibyte-chars`（注：仅 C++ 环境可能兼容，C 环境需优先使用方法 1）。

### 2. 分盘后 Keil5 工程打不开（间接影响 USART 开发）
#### 问题原因
分盘导致芯片包路径失效或缺失，USART 工程依赖对应芯片的外设驱动支持。

#### 解决方案
- 在线安装芯片包
  1. 打开 Keil5 工程，点击右下角 Pack Installer（未响应则点击左上角刷新图标）。
  2. 选择对应芯片型号（如 STM32F103C8、GD32F103C8、MM32F103c8），下载并安装芯片包。
- 离线安装芯片包
  1. 从开发板供应商获取（如中精灵开发板资料自带）。
  2. 网络下载（如江大提供的芯片包资源）。
  3. 向他人索要匹配的芯片包，直接导入 Keil5 即可（避免重新解压导致路径错误）。

### 3. 通信无响应
#### 可能原因与排查步骤
1. 引脚接线错误：核对 TX/RX 交叉连接（USART_TX 接外设_RX，USART_RX 接外设_TX），检查地线是否连接稳定。
2. 波特率/帧格式不匹配：确保 USART 与外设的波特率、数据位、校验位、停止位完全一致（优先使用 96-N-8-1 格式调试）。
3. 时钟配置错误：确认 USART 所属总线时钟已使能（如 APB2 时钟对应 USART1）。
4. 中断未使能：检查 RXNE 中断是否开启，中断优先级配置是否正确。
5. 硬件故障：排查芯片 USART 外设损坏、引脚虚焊等问题，可更换引脚或芯片验证。

## 六、关键注意事项
1. 引脚复用：USART 引脚可能与其他外设复用（如 GPIO），需在初始化时明确配置为 USART 功能，避免引脚冲突。
2. 抗干扰设计：功率地线（PGND）与数字地线（DGND）分开布线，最终单点接地，减少电源干扰；远距离通信可添加 RS232 电平转换芯片（如 MAX232）。
3. 缓冲区设计：接收缓冲区长度需根据实际通信数据量合理设置，避免数据溢出导致丢包。
4. 校验位使用：在干扰较强的场景（如工业环境），建议启用奇校验或偶校验，提升数据传输可靠性。
5. 同步与异步选择：无需时钟同步时，优先使用异步模式（简化硬件连接）；高速通信或多设备同步场景，使用同步模式（需连接 SCLK 引脚）。