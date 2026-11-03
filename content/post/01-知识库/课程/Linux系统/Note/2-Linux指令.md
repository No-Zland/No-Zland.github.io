# Ubuntu 系统目录结构（查看目录相关指令）

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| ls | 列出指定目录下的文件 / 子目录，默认列出当前目录，常用选项-l（详细信息）、-a（显示隐藏文件） | 1. ls /：查看根目录下所有一级目录（如bin、etc、home等 Ubuntu 核心目录）； 2. ls -la /etc：以详细列表形式显示/etc目录（系统配置目录）下所有文件（含隐藏文件） |

| tree | 以树形结构展示目录层级（需先通过sudo apt install tree安装），直观呈现目录结构 | tree -L 2 /home：展示/home目录下 2 级层级结构，清晰查看用户目录下的子目录分布 |

# 创建 / 删除目录

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| mkdir | 创建新目录，-p选项可递归创建多级目录（父目录不存在时自动创建） | 1. mkdir /data/bigdata：在/data目录下创建bigdata子目录（需/data已存在）； 2. mkdir -p /data/hadoop/logs：递归创建/data/hadoop/logs，若/data、/hadoop不存在则自动创建 |

| rmdir | 删除空目录（仅能删除无内容的目录，若目录有文件需先删文件） | 1. rmdir /data/empty_dir：删除/data下的空目录empty_dir；2. 若目录非空：需先执行rm -rf /data/non_empty_dir（强制删除非空目录，谨慎使用） |

# 查看文件、查看路径

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| ls | 查看指定目录下的文件列表（延伸功能，补充文件查看场景） | ls -lh /data：查看/data目录下文件的大小（人性化显示 GB/MB）、权限等信息 |

| pwd | 显示当前工作目录的绝对路径，确认当前所在位置 | 1. 在/home/hadoop目录下执行pwd，输出/home/hadoop；2. 切换目录后执行pwd，验证是否切换到目标路径（如cd /opt && pwd输出/opt） |

# 创建文件、查看文件内容、清屏

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| touch | 创建空文件，若文件已存在则更新文件的修改时间 | 1. touch /data/test.txt：在/data目录下创建空文件test.txt；2. touch log1.log log2.log：同时创建log1.log和log2.log两个空文件 |

| cat | 查看文件全部内容（适合小文件，如配置文件、日志片段） | 1. cat /data/test.txt：查看test.txt的所有内容；2. cat /etc/hostname：查看 Ubuntu 系统的主机名 |

| more | 分页查看大文件内容（仅向下翻页，按空格键翻页、q退出） | more /var/log/syslog：分页查看系统日志文件syslog，避免内容一次性刷屏 |

| less | 分页查看大文件（支持上下翻页、搜索，功能比more强大） | 1. less /etc/profile：查看环境变量配置文件profile；2. 在less界面输入/JAVA_HOME，搜索文件中包含JAVA_HOME的内容 |

| head | 查看文件前 N 行（默认前 10 行），-n指定行数 | head -n 5 /etc/passwd：查看/etc/passwd（用户信息文件）的前 5 行内容 |

| tail | 查看文件后 N 行（默认后 10 行），-f实时跟踪文件更新（常用于监控日志） | 1. tail -n 3 /data/test.txt：查看test.txt的最后 3 行；2. tail -f /var/log/hadoop/hdfs.log：实时监控 Hadoop HDFS 日志的新增内容 |

| clear | 清空终端屏幕（仅清空当前视图，不删除历史内容，按Ctrl+L可快速触发） | 在终端输入clear，终端屏幕将清空，光标回到顶部 |

# help 命令、man 命令、自动补全 Tab、查看历史 history

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| help | 查看 Shell 内置命令的帮助信息（如cd、pwd等内置命令），外部命令需用--help | 1. help cd：查看cd命令的用法（如切换目录的语法、特殊路径~/..的说明）；2. ls --help：查看外部命令ls的帮助信息（所有选项的详细说明） |

| man | 查看命令 / 配置文件的详细手册（含用法、选项、示例），按q退出 | 1. man ls：查看ls命令的完整手册；2. man passwd：查看/etc/passwd配置文件的手册说明 |

| Tab | 终端自动补全功能（无需输入指令，按Tab键即可补全命令 / 路径） | 1. 输入cd /h后按Tab，自动补全为cd /home（若路径唯一）；2. 输入ta后按Tab，自动补全为tar（若命令唯一） |

| history | 查看终端中执行过的历史命令（默认保存 1000 条），!n可重复执行第 n 条命令 | 1. history：列出所有历史命令（含序号）；2. !5：重复执行历史记录中第 5 条命令 |

# 复制 / 剪切指令、重命名

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| cp | 复制文件 / 目录，-r选项复制目录（递归复制子目录和文件），-p保留文件属性 | 1. cp /data/test.txt /tmp/：将test.txt复制到/tmp目录；2. cp -rp /data/bigdata /opt/：将bigdata目录及属性完整复制到/opt |

| mv | 1. 剪切：将文件 / 目录移动到目标路径；2. 重命名：目标路径与原路径同目录时 | 1. 剪切：mv /tmp/test.txt /data/：将test.txt从/tmp移动到/data；2. 重命名：mv /data/test.txt /data/new_test.txt：将test.txt重命名为new_test.txt |

# 重定向、管道命令

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| 重定向> | 覆盖重定向：将命令输出内容写入文件，若文件已存在则覆盖原有内容 | 1. ls -l /data > /data/file_list.txt：将/data目录的文件列表覆盖写入file_list.txt；2. echo "Hadoop Home: /opt/hadoop" > /etc/profile.d/hadoop.sh：将环境变量配置覆盖写入文件 |

| 重定向>> | 追加重定向：将命令输出内容追加到文件末尾，不覆盖原有内容 | 1. echo "Spark Home: /opt/spark" >> /etc/profile.d/hadoop.sh：在hadoop.sh末尾追加 Spark 环境变量；2. date >> /data/operation.log：将当前时间追加到操作日志文件 |

| 管道 ` | ` | 将前一个命令的输出作为后一个命令的输入，实现多命令联动 |

# 链接快捷方法（软链接、硬链接）

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| ln -s | 创建软链接（符号链接）：类似 Windows 快捷方式，链接文件指向源文件路径，源文件删除则链接失效 | ln -s /opt/hadoop /home/hadoop/hadoop-link：在/home/hadoop下创建软链接hadoop-link，指向/opt/hadoop目录 |

| ln | 创建硬链接：与源文件共享同一 inode（文件索引），源文件删除后硬链接仍可访问文件内容（仅支持文件，不支持目录） | ln /data/test.txt /data/test-hard-link.txt：为test.txt创建硬链接test-hard-link.txt，修改任一文件内容，两者同步更新 |

# 文件搜索

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| find | 按路径、文件名、大小、修改时间等条件搜索文件 / 目录 | 1. find /data -name "*.log"：在/data目录下搜索所有.log后缀的文件；2. find /opt -size +100M：在/opt目录下搜索大小超过 100MB 的文件 |

| grep | 在文件或命令输出中搜索指定字符串（支持正则表达式），-n显示行号，-i忽略大小写 | 1. grep "error" /var/log/hadoop/hdfs.log：在 HDFS 日志中搜索包含 “error” 的内容；2. grep -ni "java_home" /etc/profile：在profile文件中忽略大小写搜索 “java_home”，并显示行号 |

# 压缩文件和解压缩（tar 指令为主）

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| tar -zcvf | 打包并通过 gzip 压缩文件 / 目录，生成.tar.gz格式压缩包（c= 打包，z=gzip 压缩，v= 显示过程，f= 指定压缩包名） | tar -zcvf /data/hadoop.tar.gz /opt/hadoop：将/opt/hadoop目录打包并压缩为hadoop.tar.gz，保存到/data目录 |

| tar -zxvf | 解压.tar.gz格式压缩包（x= 解压，z=gzip 解压，v= 显示过程，f= 指定压缩包名），-C指定解压目标路径 | 1. tar -zxvf /data/hadoop.tar.gz：将hadoop.tar.gz解压到当前目录；2. tar -zxvf /data/hadoop.tar.gz -C /opt/：将压缩包解压到/opt目录 |

| tar -jcvf | 打包并通过 bzip2 压缩（生成.tar.bz2格式，压缩率比 gzip 高） | tar -jcvf /data/spark.tar.bz2 /opt/spark：将/opt/spark打包压缩为.tar.bz2格式 |

| tar -jxvf | 解压.tar.bz2格式压缩包 | tar -jxvf /data/spark.tar.bz2 -C /opt/：将spark.tar.bz2解压到/opt目录 |

# 日历 cal、时间 date

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| cal | 显示日历，默认显示当前月日历，cal [年份]显示全年日历，cal [月份] [年份]显示指定月日历 | 1. cal：显示当前月的日历（含星期）；2. cal 10 2024：显示 2024 年 10 月的日历；3. cal 2024：显示 2024 年全年的日历 |

| date | 显示当前系统时间 / 日期，也可设置系统时间（需root权限） | 1. date：显示当前时间（格式如2024-10-01 14:30:25 CST）；2. date "+%Y-%m-%d %H:%M:%S"：自定义时间格式（年 - 月 - 日 时：分: 秒）；3. sudo date -s "2024-10-01 15:00:00"：以root权限设置系统时间为 2024 年 10 月 1 日 15:00 |

# 进程操作、系统状态查看和操作

| 指令名称 | 功能说明 | 样例 |

|---|---|---|

| ps | 查看系统当前运行的进程，-ef显示所有进程的详细信息（PID、所有者、命令等），-aux显示进程资源占用（CPU、内存） | 1. ps -ef：列出所有进程的完整信息（如UID、PID、PPID、CMD）；2. `ps -aux |

| kill | 终止指定进程，需结合ps获取的进程 ID（PID），-9选项强制终止无响应进程 | 1. kill 12345： 终止 PID 为 12345 的进程（需确认进程可终止）； 2. kill -9 67890： 强制终止 PID 为 67890 的卡死进程 |

| top | 实时监控系统进程的资源占用（CPU 使用率、内存使用率、系统负载），按q退出 | top： 进入实时监控界面，可查看 “% Cpu (s)”（CPU 总占用）、“KiB Mem”（内存使用）、“PID”（进程 ID）等信息 |

| df | 查看系统磁盘分区的空间使用情况，-h选项人性化显示容量单位（GB/MB） | df -h： 输出各分区的 “Filesystem”（分区名）、“Size”（总容量）、“Used”（已用容量）、“Avail”（可用容量） |

| du | 查看文件 / 目录的磁盘占用大小，-sh选项显示目录总大小（不展开子目录） | 1. du -sh /data： 查看/data目录的总占用空间； 2. du -h /home/hadoop： 查看/home/hadoop下各文件 / 子目录的占用空间 |
