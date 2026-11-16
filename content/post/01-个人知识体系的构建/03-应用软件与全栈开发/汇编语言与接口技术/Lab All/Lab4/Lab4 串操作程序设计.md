实验四 串操作程序设计

1.  实验目的：

（1）熟悉串操作指令的功能与应用。

（2）掌握串操作的程序设计方法。

2.  实验内容：

（1）学习串的基本操作：串比较、串检索、字符统计等。

（2）编程实现字符串的操作处理。

3.  实验步骤：

（1）预习相关内容，分析问题，设计结构。

（2）编写ASM源程序并对其进行汇编及连接，产生.EXE文件。

（3）调试运行，改进程序。

4.实验项目：

（1）在数据区BUF1和BUF2地址开始分别有一个字符串，长度均为14个字节。试比较这两个字符串，若相同，则给RES单元置0；若不同，则给RES单元置0FFH，并将失配字节送RES+1开始的两个存储单元中。参考源程序如下：

|   |   |
|---|---|
|.MODEL  SMALL<br><br>.DATA  <br><br>BUF1   DB  ‘I am a student’<br><br>BUF2   DB  ‘I am a student’<br><br>RES    DB   3  DUP(?)<br><br>NUMBER EQU  14<br><br>.STACK<br><br>STA    DB   100 DUP(?)<br><br>.CODE<br><br>START:   MOV  AX,DATA<br><br>         MOV  DS,AX<br><br>         MOV  ES,AX<br><br>         LEA  BX,RES<br><br>         LEA  SI,BUF1<br><br>         LEA  DI,BUF2<br><br>         MOV  CX,NUMBER<br><br>         CLD|REPE  CMPSB <br><br>；重复比较<br><br>         JNZ   UNMANE<br><br>         MOV   [BX],AL<br><br>         MOV    DL,[BX]<br><br>         JMP   OVER<br><br>UNNAME:  MOV   AX,0FFH<br><br>         MOV   [BX],AL<br><br>         INC   BX<br><br>         DEC   DI<br><br>         MOV   [BX],DI<br><br>；送不相同的字节地址<br><br>         MOV   AH,4CH<br><br>         INT   21H<br><br>；返回DOS<br><br>         END   START|

（2）在内存数据区有一个数据块，首地址BUF，字节型。检索其中是否有与内存单元KEYWORD中相同的字符。若有则记录第一个遇到的关键字地址；若无则DI置0。（提示：利用SCAN指令加重复前缀可以简单完成关键字的检索。按该指令的要求先将数据块首地址送DI寄存器，数据块长度送CX寄存器，利用ZF标志判断是否检索到）。

（3）编程实现字符统计：在数据区STRING地址开始存有一字符串，以‘$’作为结尾标志，长度不超过250个。统计该字符串的长度，并存于LENG单元中。

5.实验报告主要内容：

（1）写出项目2、3的源程序清单、程序说明、执行结果。

（2）调试说明。包括上机调试的情况、调试步骤、调试所遇到的问题是如何解决的，并对调试过程中的问题进行分析，对执行结果进行分析。