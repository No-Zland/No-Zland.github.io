实验六  DOS功能调用

1.实验目的：

（1）掌握DOS功能调用的方法。

（2）综合利用汇编指令编写汇编程序。

2.实验内容：

（1）学习键盘输入的功能调用。

（2）学习显示字符串的功能调用。

3.实验步骤：

（1）编辑、汇编源程序，连接后生成相应的.EXE可执行文件。

（2）运行、调试程序，观察结果。

知识点：常用字符输入/出系统功能调用

（1）输出一个字符：DOS功能调用INT 21H的02号功能调用。

使用格式：

MOV  AH, 02H       ；设置功能调用号 AH<-02H

MOV  DL, ‘*’     ；设置入口参数DL<-待显示的字符的ASCII码

INT   21H          ；DOS功能调用：显示

（2）输入一个字符：DOS功能调用INT 21H的01号功能调用。

使用格式：

MOV   AH, 01H      ； 设置功能调用号 AH<-01H

INT   21H           ；DOS功能调用：显示

出口参数：AL=字符的ASCII码

说明：执行此功能时，等待用户按键，然后读取按键值。

4.实验项目：

（1）结合课本上例4.16，编程实现：从键盘上输入某人的姓名***，当按动任意一键时，屏幕上会显示出：“Welcome ***”。

参考程序如下：

|   |   |
|---|---|
|DSEG    SEGMENT<br><br>        MAXLEN  DB  16<br><br>        ACTLEN  DB  ?<br><br>        NAMES   DB  16  DUP(‘ ’)<br><br>        MESS1   DB  ‘Welcome ’<br><br>        MESS2   DB  16  DUP(‘ ’)<br><br>        CRLF    DB  0DAH,0AH,‘$’<br><br>DSEG    ENDS<br><br>CSEG    SEGMENT<br><br>        PROC  FAR<br><br>        ASSUME CS:CSEG,DS:DESG,ES:DESG<br><br>  PUSH   DS   <br><br>SUB    AX,AX<br><br>PUSH   AX<br><br>MOV    AX,DSEG<br><br>MOV    DS,AX<br><br>MOV    ES,AX<br><br>CLD<br><br>BEGIN:  MOV  CX,16<br><br>MOV  AL,20H|LEA  DI,MESS2<br><br>REP  STOSB<br><br>LEA  DX,MAXLEN<br><br>MOV  AH,0AH    ；输入字符串<br><br>INT  21H<br><br>DISPLAY:<br><br>        MOV  CH,0<br><br>        MOV  CL,ACTLEN<br><br>        LEA  SI,NAMES<br><br>        LEA  DI,MESS2<br><br>        REP  MOVSB<br><br>        MOV  AH,09H  <br><br>        LEA  DX,MESS1<br><br>        INT  21H <br><br>EXIT:   RET<br><br>MAIN    ENDP<br><br>CSEG    ENDS<br><br>        END  MAIN|

说明：在使用功能调用时要注意参数的设置以及其它一些特殊要求。比如INT  21H的0Ah功能是带缓冲区的键盘输入，调用时需要设置一个正确的数据缓冲区，缓冲区的第一个字节是允许键入的最大字符数，第二个字节将由DOS填入实际键入的字符数，从第三个字节才是由键盘输入的字符，而且字符的个数不能超过规定的最大字符数。又比如INT  21H的09h功能是显示字符串，此功能除要求在DS：DX中设置缓冲区首地址外，还要求字符串必须以‘$’结束。

（2）编写一个程序，要求能从键盘接收一个个位数N，然后响铃N次（响铃的ASCII码为07H）。

（1）设有一个数组存放10个学生的成绩，分别为76,69,84,90,73,88,98,63,100,80，试着编写一个程序，统计60-69分，70-79分，80-89分，90-99分及100分的人数，分别存放到S6,S7,S8,S9,S10单元中。

5.实验报告主要内容：

（1）写出项目2、3的源程序清单、程序说明、执行结果。

（2）调试说明。包括上机调试的情况、调试步骤、调试所遇到的问题是如何解决的，并对调试过程中的问题进行分析，对执行结果进行分析。