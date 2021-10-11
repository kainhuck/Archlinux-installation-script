# Archlinux-installation-script

![GitHub](https://img.shields.io/github/license/kainhuck/Archlinux-installation-script?style=for-the-badge) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/kainhuck/Archlinux-installation-script?style=for-the-badge)

## install.py

archlinux的安装脚本，可选择`Gnome`或者`plasma`桌面（推荐选择 plasma 桌面）
在执行安装任务前需要输入配置，在确认回车前，不会对系统做任何修改

**使用**

安装脚本

```shell
curl -LJO https://github.com/kainhuck/Archlinux-installation-script/releases/download/v1.0/install.py

chmod +x install.py

./install.py
```

安装后的配置脚本(针对kde桌面, 其他桌面按需修改)

```shell
curl -LJO https://github.com/kainhuck/Archlinux-installation-script/releases/download/v2.0/setup.py

chmod +x install.py

./install.py
```