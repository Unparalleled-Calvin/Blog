---
title: Hexo GitHub Action CI配置(解决文章修改时间问题)
date: 2022-10-14 13:45:32
tags: [Hexo, Github Action]
categories: [技术视野]
---

因为本人懒得每次push完代码再手敲一次部署命令，所以想利用Github Action来实现每次push后自动部署到网页。中文互联网上搜索到的解决方案较老，花了几天时间踩了很多坑之后我这里也是成功配置完毕，因此在这里写篇博客记录一下。

以下是相关版本号

- hexo：v6.3.0
- next：v7.8.0
- node：v16

### 手动部署

- 安装必要插件

    ```shell
    npm install hexo-deployer-git
    ```
    
- hexo配置文件

    ```yaml
    deploy:
      type: git
      repo: # ssh地址
      branch: # 配置过Github Page的分支，配置过程请自行查阅
    ```

- 命令行部署

    ```shell
    hexo d
    ```

### CI自动部署

- 请参考[利用 Github Actions 自动部署 Hexo 博客](https://sanonz.github.io/2020/deploy-a-hexo-blog-from-github-actions/)进行Github的配置以及workflow yaml文件的初步配置，我使用的Hexo+Next版本无需使用主题仓库，因此对应部分我删除了。

- 在yaml中添加/修改两个step

  - checkout是将文件放入当前工作区，默认情况下对git文件做**浅拷贝**(shadow copy)，这里为了保留git log中的时间信息，采用**深拷贝**(deep copy)

    **目前网上资料很少有这一步，但是这一步很关键**

    ```yaml
    - name: Checkout
      uses: actions/checkout@v2
      with:
        fetch-depth: '0'
    ```

  - 第一条指令是取消git对中文文件的转义，否则linux会将`\xxx`解读为`xxx`找不到对应中文文件

    第二条指令从git log中读取文件修改记录，并将sources中文件的修改时间用`touch -d`进行修复
    
    ```yaml
    - name: Restore file modification time
      run: |
        git config --global core.quotepath false
        git ls-files --directory source | while read path; do touch -d "$(git log -1 --format='@%ct' $path)" "$path"; done
    ```
