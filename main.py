#!/usr/bin/python
# This is ArchLinux install script

import os
import re
import sys
import subprocess
import platform


SUCCESS = 0
IS_UEFI = True


def check_platform():
    return platform.uname()[0] == "Linux" and platform.uname()[1] == "archiso"


def check_boot():
    global IS_UEFI
    IS_UEFI = os.path.exists("/sys/firmware/efi/efivars")


def check_network():
    code, _ = subprocess.getstatusoutput("ping -c 1 www.baidu.com")
    return code == SUCCESS


def run_cmd(*cmd):
    cmd_str = " ".join(cmd)
    code, output = subprocess.getstatusoutput(cmd_str)
    try:
        assert code == SUCCESS
    except AssertionError as e:
        print(f"ERROR {output}")
        sys.exit(code)

    return output


def main():
    # ======================= 检查安装环境 ======================= #
    # 检查平台
    print("正在检查安装平台信息...")
    if not check_platform():
        print("This script only for archlinux installation")
        sys.exit(0)
    print("OK")

    print("正在检查网络连接...")
    # 检查网络
    if not check_network():
        print("Please connect Internet")
        sys.exit(0)
    print("OK")

    # 确定引导方式
    check_boot()

    # ======================= 下面是正式安装过程 ======================= #

    # 更新系统时间
    print("正在更新系统时间...")
    run_cmd("timedatectl", "set-ntp", "true")
    print("OK")

    # 磁盘分区
    output = run_cmd("fdisk", "-l")
    disks_ = re.findall("(/dev/.+?: [0-9 .]+? .+?iB)", output)
    disks = []
    for each in disks_:
        if "rom" in each or "loop" in each or "airoot" in each:
            continue
        else:
            disks.append(each)

    if len(disks):
        print("发现如下可用磁盘:")
        for i in range(len(disks)):
            print(f"{i} - {disks[i]}")
    else:
        print("未发现可用磁盘，程序退出")
        sys.exit(0)

    choose_index = int(input("请从上面选择一个要安装的磁盘(输入序号): "))
    while choose_index < 0 or choose_index >= len(disks):
        choose_index = int(input("输入的序号有误，请重新输入: "))

    disk = disks[choose_index]
    dev = disk.split(":")[0]
    print(f"正在进行磁盘分区{dev}...")

    # 挂载分区

    # 安装系统及必要软件

    # 生成fstab

    # chroot

    # 设置时区

    # 本地化

    # Host

    # 设置各种必要服务开机自启

    # 用户和密码

    # grub

    # 结束工作


if __name__ == '__main__':
    main()
