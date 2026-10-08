## 前言

很多人想用 AI 搞渗透，但卡在第一步——**环境都没搭起来**。Git 不会装、Node 不知道版本、Claude Code 不知道怎么配。这篇从零开始，手把手带你搭好 Claude Code 渗透环境，每步都有截图，照着点就行。最后附上我们定制的 **CLAUDE.md 渗透配置**，下载直接用。

[下载 CLAUDE.md](https://xiaoguo-3ca.pages.dev/img/CLAUDE.md)

## 第一步：安装 Git

先去 Git 官网下载安装包：https://git-scm.com/install/windows

![下载Git](https://xiaoguo-3ca.pages.dev/img/2.png)

下载后双击运行，一路 Next 就行，不用改任何设置。安装过程截图：

![img](https://xiaoguo-3ca.pages.dev/img/3.png)![img](https://xiaoguo-3ca.pages.dev/img/4.png)![img](https://xiaoguo-3ca.pages.dev/img/5.png)![img](https://xiaoguo-3ca.pages.dev/img/6.png)![img](https://xiaoguo-3ca.pages.dev/img/7.png)![img](https://xiaoguo-3ca.pages.dev/img/8.png)![img](https://xiaoguo-3ca.pages.dev/img/9.png)![img](https://xiaoguo-3ca.pages.dev/img/10.png)![img](https://xiaoguo-3ca.pages.dev/img/11.png)![img](https://xiaoguo-3ca.pages.dev/img/12.png)![img](https://xiaoguo-3ca.pages.dev/img/13.png)![img](https://xiaoguo-3ca.pages.dev/img/14.png)![img](https://xiaoguo-3ca.pages.dev/img/15.png)![img](https://xiaoguo-3ca.pages.dev/img/16.png)

## 第二步：安装 Node.js

下载 Node.js：https://nodejs.org/en

![img](https://xiaoguo-3ca.pages.dev/img/17.png)![img](https://xiaoguo-3ca.pages.dev/img/18.png)

![img](https://xiaoguo-3ca.pages.dev/img/17.png)![img](https://xiaoguo-3ca.pages.dev/img/18.png)![img](https://xiaoguo-3ca.pages.dev/img/19.png)![img](https://xiaoguo-3ca.pages.dev/img/20.png)![img](https://xiaoguo-3ca.pages.dev/img/21.png)![img](https://xiaoguo-3ca.pages.dev/img/22.png)![img](https://xiaoguo-3ca.pages.dev/img/23.png)![img](https://xiaoguo-3ca.pages.dev/img/24.png)![img](https://xiaoguo-3ca.pages.dev/img/25.png)

## 第三步：安装 Claude Code

按 Win+R，输入 `cmd` 打开命令行：

![img](https://xiaoguo-3ca.pages.dev/img/26.png)

执行以下命令（点击复制）：

`npm pack @anthropic-ai/claude-code`复制

`npm install -g .anthropic-ai-claude-code-*.tgz`复制

验证：

`claude --version`复制

![img](https://xiaoguo-3ca.pages.dev/img/27.png)![img](https://xiaoguo-3ca.pages.dev/img/28.png)

## 第四步：安装 ClawGod

https://github.com/0Chencc/clawgod

**Windows：**

`irm https://github.com/0Chencc/clawgod/releases/latest/download/install.ps1 | iex`复制

**Mac：**

`curl -fsSL https://github.com/0Chencc/clawgod/releases/latest/download/install.sh | bash`复制

![img](https://xiaoguo-3ca.pages.dev/img/29.png)![img](https://xiaoguo-3ca.pages.dev/img/30.png)![img](https://xiaoguo-3ca.pages.dev/img/31.png)![img](https://xiaoguo-3ca.pages.dev/img/32.png)![img](https://xiaoguo-3ca.pages.dev/img/33.png)![img](https://xiaoguo-3ca.pages.dev/img/34.png)

## 第五步：配置 CLAUDE.md

创建 .claude 目录，把 [CLAUDE.md](https://xiaoguo-3ca.pages.dev/img/CLAUDE.md) 放进去：

![img](https://xiaoguo-3ca.pages.dev/img/35.png)![img](https://xiaoguo-3ca.pages.dev/img/36.png)![img](https://xiaoguo-3ca.pages.dev/img/37.png)![img](https://xiaoguo-3ca.pages.dev/img/38.png)![img](https://xiaoguo-3ca.pages.dev/img/39.png)![img](https://xiaoguo-3ca.pages.dev/img/40.png)![img](https://xiaoguo-3ca.pages.dev/img/41.png)![img](https://xiaoguo-3ca.pages.dev/img/42.png)![img](https://xiaoguo-3ca.pages.dev/img/43.png)![img](https://xiaoguo-3ca.pages.dev/img/44.png)

## 第六步：启动

`claude`复制

```
{apiKey:"你的私钥",aseURL:"https://api.deepseek.com",model:"deepseek-v4-pro",smallModel:"deepseek-v4-flash",	imeoutMs:3000000}
```

**至此环境搭建完毕！**CLAUDE.md 已经内置了渗透测试角色，打开 Claude Code 就能直接开工。