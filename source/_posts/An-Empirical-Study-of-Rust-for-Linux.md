---
title: An Empirical Study of Rust-for-Linux
tags: []
categories: [论文阅读]
date: 2024-07-23 08:29:11
---

本文主要对[Rust-For-Linux](https://github.com/Rust-for-Linux)下的代码进行了实证研究，总结了使用Rust开发Linux内核的成果和不足，相关数据集开源在[Richardhongyu/rfl_empirical_tools](https://github.com/Richardhongyu/rfl_empirical_tools).

3个RQ：

- RFL的现状是什么
  - 代码审查流程限制了其进一步的发展(driver、file system)
  - 在内存安全上Rust并不是万能的
- RFL是否名副其实
  - RFL的目标是更安全、 开销更小、更容易开发
  - 实际上由于 unsafe的使用，只能做到more securable；一些情况下性能更低(icache miss)；引入了更多的新人加入内核开发
- 从RFL中能学到什么

#### Preliminary

- FFI：Foreign Function Interface，用一种编程语言写的程序能调用另一种编程语言写的函数。RFL主要是使用Rust提供API给C Linux kernel调用
- [rust-lang/rust-bindgen](https://github.com/rust-lang/rust-bindgen)：自动将C头文件定义中的struct、函数声明转为Rust版本

#### RFL现状

6个insights：

- **drivers, netdev, and file systems** are the long tail of RFL code.
  - 大多数都是内存管理，设备中断请求等
- RFL **infrastructure** has **matured**, with safe abstraction and drivers being the next focus.
  - Kbuild在patch中占的比重降低，而safe abstraction的比重升高
- RFL is bottlenecked by **code review** but not by code development.
  - 原因：缺少高质量reviewer；RFL和Linux社区的合作模式不同(回复时间，审核周期等)；死锁：linux的人不喜欢审核没有实际driver的safe abstraction，而没有safe abstraction，RFL的人无法开发driver
- Kernel’s initiative to control memory in fine granularity **conflicts** Rust **philosophy**, which incurs overhead for RFL.
  - Rust不支持C中的bitfield和union等数据结构，只能用一些低效的实现方式
  - Rust也不支持C中一些变量的attributes关键字
- RFL uses helper types to delegate management of kernel data to Rust while leaving the operation to kernel itself.
  - Type和Deref来规范化类型和指针，从而避免C中void *之类的模糊
  - 使用一些类型来帮助管控内核中一些结构体的行为(退出作用域自动释放内存、自动引用计数等)
- The major difficulty of writing safe drivers in Rust is to reconcile the inflexibility of Rust versus kernel programming conventions, which is often an oversight by RFL and the Linux community from what we observe.
  - Rust中用于device probing的类型可能会很复杂
  - Rust中想要做到变长array比较麻烦，而C只需要一个指针和一个长度就可以了

### RFL是否名副其实

<img src="An-Empirical-Study-of-Rust-for-Linux/table 1.png" alt="image-20240723100429712" style="zoom:50%;" />

- with RFL, Linux becomes more “securable” but still cannot be fully secure.
  - Rust基本的内存安全控制
  - unsafe是无法移除的
  - Bug依旧可能由并发或者上下文语意语义产生
- There is no free lunch for performance –it is the programmer that counts!
  - binary普遍增大
  - 一些情况下会效率更高，另一些情况下则不然
- Rust的引入为内核开发带来了很多便利
  - 代码质量、可读性(doc注释)
  - 新人加入(但暂时还不能承担核心任务)

