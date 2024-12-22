---
title: 中国Rust开发者大会参会记录
tags: [Rust]
categories: [技术视野]
date: 2024-09-07 10:17:11
---

Amazon：Rust and 生成式AI应用

PyO3，Rust/Py binding，还有其他一些开源工具例如diffuser-rs等

AWS为Rust开发者提供SDK服务，同时还有生成式AI产品Amazon Q



非凸科技：首席架构师乔丹，Rust程序的不同链接方式在交易系统中的典型应用

投研团队都写Rust，策略/工程，但是strategy和facade(前端)依然要两个团队分别维护

- 第一种方式：crate-type=lib，用workspace捏在一个大项目里，dependency指定A依赖B
  - 代码有泄露风险
- 第二种方式：crate-type=cdylib，用extern C来指定需要分发出去的代码
  - C风格函数无法接受Rust独有类型，FFI
- 第三种方式：crate-type=**rlib**，保留Rust语言特性，性能无损，无FFI
  - 不再开放代码权限，静态链接
  - 但是**ABI**稳定性在长期开发中可能会成为问题，毕竟Rust的工具链一直在更新——不过可以约定公司使用的版本



字节跳动：吴迪，Rust服务端开发

Rust与降本增效——性能高的同时，Review代码的时候极大地减少心智负担，只需要关心业务逻辑

将GO迁移到Rust后，可用性增加，CPU使用率下降，性能提升约50%

要敢于造轮子，社区很多库有的时候没那么完善

Rust可能未来会作为计算基座



JetBrain：交互式debugRust代码

绝大多数人都哦再用println!或者dbg!调试

交互式debug：breakpoint， stepbystep



Sonala：华语区大使李学斌

Bitcoin: proof of work, Ethereum: smart contract (proof of stack), Solana: proof of history

EVM: 以太坊虚拟机，全局竞价，单线执行

SVM：Solana虚拟机，不同的竞价(NTF, DEX等类型)并行在对应队列中单线执行

Sonala的基础交易费非常低，导致会有为了争先交易而产生的泛洪请求。为了保证网络质量采用quic



Vara Network

采用WASM而不是EVM做智能合约，并行采用Actor消息模型



Async维测&定位的探索和思考

Rust，无栈协程，Future用工作线程的栈，没有独立栈空间

协程状态机与函数体里的await位置有关，从而可以记录从pending转而重新执行函数时从哪里恢复



Rust HashMap 比看起来更复杂

场景：开发时序数据库HoraeDB，为了高效并发做了分段HashMap，Rwlock

- 用Vec Buffer提高局部性，减少tlb/cache miss
  - demo: [Rachelint/sharded-hashmap](https://github.com/Rachelint/sharded-hashmap)
- 实际分配的内存比with_capacity指定的多
  - 先乘 8/7，然后对齐到2^n，这么多个buckets对应的kv空间
  - 同时hashmap对内存的随机访问可能会分散在不同的页上
- capacity需要微调合理，否则会内存爆炸
- 尽量不要放太大的东西



Rust和C++互操作及交叉编译 朱树磊 浙江大华

动机

- 公司legacy code比较多

- 使用大型C/C++库和中间件
- 希望使用C++的特性
- HPC的CUDA等类C++语言Rust也无法直接调用

跨语言互操作工具包括FFI，bindgen，cbindgen，cpp!

cxx：安全的C++和Rust互操作工具



