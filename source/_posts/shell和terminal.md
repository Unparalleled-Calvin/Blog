---
title: shell和terminal
tags: [Shell]
categories: [技术视野]
date: 2023-02-09 09:21:28
---

#### Terminal和TTY

- 古早年代通过电传打印机(**t**ele**ty**pewriter)让用户与计算机交互，打字机上输入的文本可以直接发送到计算机，计算机的输出也通过打字机打印出来。

  <img src="shell和terminal/image-20230209093403164.png" alt="image-20230209093403164" style="zoom:50%;" />

  > UART：Universal Asynchronous Reciver/Transmitter，通用异步收发传输器
  >
  > line dicipine：行规范

- 终端设备(例如VT100)出现并逐渐取代了电传打印机

  > 使用阴极射线管进行显示，供应商采用ascii字符集这一相同标准，同时显示器单行最大80字符的设定也能在现代编程规范中觅得踪影(Google C++ style, PEP8)

- PC时代，显示器和键盘取代了传统终端。考虑到兼容性，在内核中模拟了一个终端(terminal emulator)与tty驱动交互

  <img src="shell和terminal/image-20230209093744371.png" alt="image-20230209093744371" style="zoom: 50%;" />

#### Shell

shell是**操作系统和用户进行交互**的**程序**，运行在terminal之中，常见实现有`sh`，`bash`，`csh`，`cmd`，`pwoershell`，`explore`(windows资源管理器)，`Ubuntu GNOME Terminal`……

#### Console

Console是早期计算机为了调控设备而设立的一些开关等

由内核直接提供的终端页面叫虚拟控制台(Virtual Console)，而上述拥有图形化界面的是终端窗口(伪终端)

#### PTY

运行在用户态的终端是PTY伪终端(**p**seudo t**ty**)，更安全和灵活

> 因此当桌面崩掉无法响应的时候，你仍然能通过内核里的TTY来做要做的事

以GNOME terminal为例，流程为

1. 建立GNOME terminal终端
2. 打开`/dev/ptmx`字符文件，获得文件描述符PTY master，在`/dev/pts/`创建PTY slave设备
3. terminal拥有了上述的设备文件，fork出一个bash
4. terminal监听键盘事件，然后将其发送到PTY master，后者将经由line discipline处理的输入回传给terminal以供显示
5. 当按下回车后tty driver将缓冲的数据复制到pts中，此时bash读取并fork运行相关的命令
6. 由于fork出的命令拥有与bash相同的资源，因此可以操作pts进而回显到terminal上
7. 当按下ctrl C以后，line discipline产生一个SIGINT信号发给pts，进而交给bash来kill子进程

<img src="shell和terminal/image-20230209102402053.png" alt="image-20230209102402053" style="zoom: 50%;" />

#### SSH

SSH的全称是Secure Shell Protocol，目标机器在22端口监听到连接请求做完验证工作后会申请创建一个tty，建立连接后的结构如图

<img src="shell和terminal/image-20230209103551239.png" alt="image-20230209103551239" style="zoom:50%;" />

用户端部分禁用了line discipline，因此相关命令经过回车后才不会被执行。但服务端部分的line discipline没有被禁用，因此能够在服务端执行并正常回显

> 所以才会出现ssh连接远程服务器的时候，终端中输入字符一卡一卡的，因为每一个字符的回显都要经过网络的一次来回传输
