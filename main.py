#!/user/bin/python
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
    print(cmd_str)
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
    if not check_platform():
        print("This script only for archlinux installation")
        sys.exit(0)

    # 检查网络
    if not check_network():
        print("Please connect Internet")
        sys.exit(0)

    # 确定引导方式
    check_boot()

    # ======================= 下面是正式安装过程 ======================= #

    # 更新系统时间
    run_cmd("timedatectl", "set-ntp", "true")

    # 磁盘分区
    output = run_cmd("fdisk", "-l")
    disks_ = re.findall("(/dev/.+?: [0-9 .]+? .+?iB)", output)
    disks = []
    for each in disks_:
        if "rom" in each or "loop" in each or "airoot" in each:
            continue
        else:
            disks.append(each)

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


def test():
    disks_ = re.findall("(/dev/.+?: [0-9 .]+? .+?iB)", """Disk /dev/sda: 20 GiB, 21474836480 bytes, 41943040 sectors
Disk model: VBOX HARDDISK
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop0: 673.11 MiB, 705802240 bytes, 1378520 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes""")
    disks = []
    for each in disks_:
        if "rom" in each or "loop" in each or "airoot" in each:
            continue
        else:
            disks.append(each)
    print(disks)


if __name__ == '__main__':
    # main()
    test()
