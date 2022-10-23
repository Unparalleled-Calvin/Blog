---
title: cpp_easygraph文档
date: 2022-10-23 14:22:33
tags: [Pybind11]
categories: [技术视野]
---

### 简介

cpp_easygraph主要由C++编写，利用[pybind11](https://github.com/pybind/pybind11)框架实现用C++代码到python的桥接。在cpp_easygraph提供的类和方法中，暴露出的接口与python库源码的接口相同(即函数名、参数、效果等)。EasyGraph通过引入cpp_easygraph中的类和方法，将C++实现的内容嵌入到原先的代码中，从而实现类和高性能计算方法的扩展。

### 为何使用Pybind11？

对于一个由C/C++编写的python库来说，开发阶段的测试和最终代码的发布都需要开发者能够快捷且正确地编译代码生成目标文件。Pybind11是一个纯头文件的项目，一方面，它基于原生Python/C API，兼容所有原生函数接口，另一方面，它仅仅保留了部分重要的函数和类，非常轻量，仅需在代码中包含头文件而不需要链接额外的静态库。因此，在不同的操作系统上，可以直接使用`python setup.py build_ext`进行编译和构建，这也极大地方便了开发运维一体化。

### 如何使用Pybind11

#### 开发环境配置

前文所述，pybind11是一个纯头文件的项目，我们可以通过`pip install pybind11`直接进行安装。进入`python根目录/Lib/site-packages/pybind11/include/pybind11`中可以看到其提供的所有头文件。

使用IDE(例如VS等)进行开发时，对于头文件目录相关的配置，可以将`python根目录/Lib/site-packages/pybind11/include`目录以及`Python.h`所在的`python根目录/include`目录加入配置项。对于库目录相关配置，只需将`python3x.lib`所在的`python根目录/libs`目录加入配置项即可。

以Visual Studio 2022举例，目录项配置如下

<img src="http://tva1.sinaimg.cn/large/006g42Mjly1h7eaizu1dqj31n10so1iu.jpg" alt="image.png"  />

另外将输出类型改为dll，文件后缀改为pyd即可生成对应库文件。

#### 代码编写

假设要用C++实现如下python代码

```python
#文件名：foo.py，即我们要写一个名为foo的库
class Guest:
    def __init__(self, name):
        self.name = name

class Vip(Guest):
    def __init__(self, name, no):
        super().__init__(self, name)
        self.no = no
        
class Greeter:
    def __init__(self, name, **attr):
        self.name = name
        self.cnt = 0
        self.attr = attr
    def greet(self, guest, count = False):
        print("Hello " + guest.name + "!")
        if count:
	        self.cnt += 1

def get_localtime():
    import time
    localtime = time.asctime(time.localtime(time.time()))
    return localtime
```

首先我们先来看`Guest`和`Vip`。我们可以定义好前两个类的继承关系和构造函数。

```c++
struct Guest {
    Guest(const std::string& name) :name(name) {}
    std::string name;
};

struct Vip: public Guest {
    Vip(const std::string& name, int no) :Guest(name) {
        this->no = no;
    }
    int no;
};
```

然后我们声明一个模块`foo`，并将这两个类注册进来。

```C++
PYBIND11_MODULE(foo, m) { // 宏PYBIND11_MODULE的第一个参数是导出后在python中的包名，第二个参数是下文module实例的符号
    py::class_<Guest>(m, "Guest") // class_模板中填写要导出的C++类，参数第二个是导出后在python中的类名
        .def(py::init<const std::string&>()); // init模板中填写构造函数的类型表
    py::class_<Vip, Guest>(m, "Vip") // class_模板中第二个参数开始填写要继承的C++类
        .def(py::init<const std::string&, int>());
}
```

接下来我们来实现Greeter。Greeter的构造函数比较复杂，是可变参数，需要固定的格式(args, kwargs)。这里将其写在类的外面。类的方法可以写在类的里面，但需要加上`static`声明，不需要`self`参数，否则需要写在类外面，并且第一个参数为对象自身。

我们希望把Greeter的`cnt`属性也给暴露出来，因此需要写一个get方法，这个方法写在类里面就好。


```C++
struct Greeter {
    std::string name;
    int cnt;
    py::dict attr;
    
    py::object get_cnt() {
        return py::cast(this->cnt); // py::cast可以将参数转为py::object类型(如果能转换的话)
    }
};

py::object Greeter__init__(py::args args, py::kwargs kwargs) {
    py::object self = args[0]; // self一般是第0个positional parameter
    self.attr("__init__")(); // .attr方法类似于python中取attribute，返回一个可能是属性也可能是方法的对象，这里用"()"执行__init__方法进行默认构造的初始化
    Greeter& g = self.cast<Greeter&>(); // cast方法可以将python类型转为C++类型(如果能转换的话)
    std::string name = args[1].cast<std::string>(); // 这里假定name是positional传参的，不在attr中，实际情况可能并非如此
    py::dict attr = kwargs;
    g.name = name;
    g.cnt = 0;
    g.attr = attr;
    return py::none();
}

py::object Greeter_greet(py::object self, py::object guest, py::object count) {
    Greeter& g = self.cast<Greeter&>();
    Guest& gu = guest.cast<Guest&>();
    py::print(py::str("Hello ") + py::str(gu.name) + py::str("!")); // 这里直接调用了python中print，并使用了py::str重载过的+
    if (count.cast<bool>()) { // 不能用if(py::object)，那样是判断指针是否为空 
        g.cnt += 1;
    }
    return py::none(); // 没有返回值，返回None
}
```

由于可变参数需要运行时动态绑定，因此不能上之前一样用静态的模板编译，因此参考Boost Python的[Raw Constructor](https://wiki.python.org/moin/boost.python/HowTo#A.22Raw.22_constructor)加上个人实验，发现如下形式有效(与Boost Python相反)。

```c++
// 在PYBIND11_MODULE中加上
py::class_<Greeter>(m, "Greeter")
    .def(py::init<>())
    .def("__init__", &Greeter__init__) // 可变参数的函数不需要写py::arg
    .def("greet", &Greeter_greet, py::arg("guest"), py::arg("count") = false) // py::arg中填写导出后在python中的方法名，可以对arg对象直接赋值来规定参数默认值
    .def_property("cnt", &Greeter::get_cnt, nullptr); // 第一个参数为导出后在python中的属性名，二三参数分别为get和set该属性的函数指针
```

最后我们写一下`get_localtime`方法

```c++
py::object get_localtime() { // 不需要self参数
    py::object time = py::module_::import("time"); // 运行时导入time模块
    py::object localtime = time.attr("asctime")(time.attr("localtime")(time.attr("time")()));
    return localtime;
}

// 在PYBIND11_MODULE中加上
m.def("get_localtime", &get_localtime); // 写法与method相同
```

生成foo库并实验一下，发现代码正确无误。

<img src="http://tva1.sinaimg.cn/large/006g42Mjly1h7eejvwnc9j30rb0kwne3.jpg" alt="image.png" style="zoom:50%;" />

上述代码涉及如下Pybind11使用知识点：

- C++变量与py::object对象的转换
- 声明一个module并注册类和方法
  - 类继承
  - 类方法的注册
    - init方法
    - 可变参数(init或普通方法)
    - 默认参数
  - 类属性的注册
    - getter
    - setter
  - 模块方法的注册
- 运行时导入其他python模块
- 正确使用if判断
- none返回值

其余一些tricky的使用大多与python有关，例如`set`等内置类型或方法可以通过`builtins`包拿到，以及可以通过`object.__class__()`新建一个对象等。关于API的使用使用可参考[官方文档](https://pybind11.readthedocs.io/en/stable/#)，[官方仓库讨论](https://github.com/pybind/pybind11/discussions)，[官方仓库issue](https://github.com/pybind/pybind11/issues)，stackoverflow等平台

### cpp_easygraph项目架构

#### 目录架构

目录架构与easygraph基本保持一致。easygraph中有的文件夹和.py文件，cpp_easygraph目录下也有对应文件夹和cpp文件。

cpp_easygraph的`common`文件夹中存放共用的头文件以及一些工具函数，这部分在easygraph中没有对应。

python通过可以嵌套的`__init__.py`来指定import时导入的符号，以及在py文件中使用`__all__`来指定文件暴露出去的符号。cpp_easygraph使用`__init__.h`文件期望达到相同的抽象级别。注意，这里使用头文件仅仅为了达成一层include时的抽象，想要include某个文件夹下所有符号，包含该`__init__.h`即可。举例

```c++
// cpp_easygraph/functions/path/path.h
py::object _dijkstra_multisource(py::object G, py::object sources, py::object weight, py::object target);
// other functions need to be exposed...

// cpp_easygraph/functions/path/__init__.h
#include "path.h"
// other header files need to be included

// cpp_easygraph/function/__init__.h
#include "path/__init__.h"
// other header files need to be included

// cpp_easygraph/cpp_easygraph.cpp
#include "functions/__init__.h"
```

#### 类架构

目前仅仅实现了Graph和DiGraph两个类，DiGraph继承于Graph，二者仅有python绑定的函数不同，成员变量是相同的。

实际函数中，要使用成员变量，直接cast到基类的引用Graph&即可。要使用方法，通过传入的py::object对象使用attr进行对应python方法的执行。

#### 类设计

实现Graph类的思路大体沿用easygraph，node和adj均为与python代码一致的map结构。python中dict的键可以是任意可哈希对象，easygraph也支持任意这样的对象成为node.但是C++中的map暂时无法支持多样的类型，因此维护两个内部映射的`node_to_id`和`id_to_node`，在C++函数计算以及数据结构存储时使用node_t(目前typedef为int，可更换为unsigned等)，在函数解析参数和函数返回时使用进行对象的转换。

```c++
// common.h
typedef int node_t;
typedef float weight_t;

// Graph.h
struct Graph {
    node_dict_factory node;
    adj_dict_factory adj;
    py::dict node_to_id, id_to_node, graph;
    node_t id;
    bool dirty_nodes, dirty_adj;
    py::object nodes_cache, adj_cache;
}
```

Graph需要暴露adj和node属性，每次都查找dict生成显然对速度不利。考虑到用户在进行数据增删和数据使用往往是两个不同的时间段，这里牺牲空间加入两个cache对象，当发生数据结构内容改变时置dirty标志为1，下次调用属性get方法时就会重新生成一次，并抹去dirty，以此减少时间消耗。

node和adj的attr部分默认为std::string到weight_t(目前typedef为float，可更换为double等)的映射。

### 将cpp_easygraph嵌入到easygraph

#### 类的嵌入

尝试导入cpp_easygraph并定义GraphC和DiGraph类。两个类继承于cpp_easygraph中C++编写的类，并定义cflag以便在运行时与python类区分。

```python
# graph.py
try:
    import cpp_easygraph
    class GraphC(cpp_easygraph.Graph):
        cflag = 1 # 
except ImportError:
    class GraphC:
        def __init__(self, **graph_attr):
            print("...")
            raise RuntimeError
```

#### 方法的嵌入

为了优雅地嵌入cpp_easygraph的方法，编写了一个装饰器以用于装饰对应的python函数，使得函数最终能根据传入类的类型调用对应语言编写的方法。

```python
# decorators.py
def hybrid(cpp_method_name): # 函数闭包实现装饰器，参数为cpp_easygraph中导出的方法名
    def _hybrid(py_method):
        def method(*args, **kwargs):
            G = args[0]
            if G.cflag and cpp_method_name is not None: # 判断是否为C++编写的类
                import cpp_easygraph
                try:
                    cpp_method = getattr(cpp_easygraph, cpp_method_name)
                    return cpp_method(*args, **kwargs) # 调用C++编写的方法
                except AttributeError as e:
                    print(f"Warning: {e}. use python method instead.")
            return py_method(*args, **kwargs) # 否则依旧调用python编写的方法
        return method
    return _hybrid
```

使用装饰器举例：

```python
@hybrid("cpp_density") # 如果传入GraphC对象，则调用cpp_easygraph.cpp_density
def density(G):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    if m == 0 or n <= 1:
        return 0
    d = m / (n * (n - 1))
    if not G.is_directed():
        d *= 2
    return d
```

#### 实际调用

装饰器使得函数会自动根据传入的类选择对应代码段执行。

```python
import easygraph as eg
G1 = eg.Graph()
G2 = eg.GraphC()
G1.add_edges([(1,2), (3,4)], [{}, {}])
G2.add_edges([(1,2), (3,4)], [{}, {}])
G3 = G2.py() # G2转为Graph类型
G4 = G.cpp() # G1转为GraphC类型
eg.density(G1) # 调用python代码写的函数
eg.density(G2) # 调用C++代码写的函数
eg.density(G3) # 调用python代码写的函数
eg.density(G4) # 调用C++代码写的函数
```

### 遗留问题

- C++实现的Graph类中，python dict类型的nodes和adj以cache的形式存储，导致其并不能做到所见即所得。例如在python中，要对node属性做修改仅需`G.nodes[...][key]=value`即可，但在C++中，这无法改变以std::unordered_map形式存储的实际数据。另外cache无法做到精确更新，每次都是重新生成一遍dict，效率不高。

  思考过的解决方式有：自定义一个继承于dict的类，用于精细化控制nodes和adj的cache，内部封装所属Graph的指针，但这带来两个问题：

  - 如果这个类由C++来写，此类就没有办法继承python dict，因为类的方法和成员等都是运行时确定的，无法静态编译。参见[#1193](https://github.com/pybind/pybind11/issues/1193)
  - 如果这个类由Python来写，那么Graph下属c该类，该类又需要存储Graph的引用，会造成循环引用，无法判断gc能否正常回收内存。
