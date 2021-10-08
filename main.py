#!/usr/bin/python
# This is ArchLinux install script

import os
import re
import sys
import subprocess
import platform
import time

SUCCESS = 0
IS_UEFI = True


def check_platform():
    return platform.uname()[0] == "Linux" and platform.uname()[1] == "archiso"


def check_boot():
    global IS_UEFI
    IS_UEFI = os.path.exists("/sys/firmware/efi/efivars")


def check_network():
    code, _ = subprocess.getstatusoutput("ping -c 3 www.baidu.com")
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


def disk_partition(*ops):
    cmd_format = 'echo -e "{args}" | fdisk'
    args = []
    for p in ops:
        args.append(f"{p}\\n")
    return cmd_format.format(args="".join(args))


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
    swap_mem = int(input("请输入swap分区的内存大小(单位G): "))
    while swap_mem < 0:
        swap_mem = int(input("输入不合法，请重新输入: "))

    # todo 现在只支持UEFI引导方式
    part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "", # 删除现有分区
                         "g",   # 新建gpt分区表
                         "n", "", "", "+512M", "t", "1", # 新建EFI分区
                         "n", "", "", f"+{swap_mem}G", "t", "", "19", # swap分区
                         "n", "", "", "", "t", "", "20", # 根分区
                         "w" # 写入
                         )

    run_cmd(part, dev)
    print("OK")

    # 格式化分区
    print("正在格式化分区...")
    run_cmd("mkfs.vfat", dev + "1")
    run_cmd("mkswap", dev + "2")
    run_cmd("mkfs.ext4", dev + "3")
    print("OK")

    # 挂载分区
    print("正在挂载分区...")
    run_cmd("mount", dev+"3", "/mnt")
    run_cmd("mkdir", "-p", "/mnt/boot/EFI")
    run_cmd("mount", dev+"1", "/mnt/boot/EFI")
    run_cmd("swapon", dev+"2")
    print("OK")

    # 安装系统及必要软件
    print("开始安装系统")
    desktop = int(input("脚本支持以下桌面环境:\n0. 无桌面\n1. gnome\n2. plasma\n请选择桌面环境: "))
    while desktop not in (0, 1, 2):
        desktop = int(input("输入有误请重新输入"))

    de = ""
    if desktop == 1:
        de = "gdm gnome gnome-extra alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics"
    elif desktop == 2:
        de = "plasma kde-applications alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics"

    ucode = ""
    code = int(input("脚本支持以下cpu类型:\n0. intel\n1. amd\n2. 其他\n请选择类型: "))
    while code not in (0, 1, 2):
        code = int(input("输入有误请重新输入"))
    if code == 0:
        ucode = "intel-ucode"
    elif code == 1:
        ucode = "amd-ucode"

    print("这一步比较漫长(取决于网络环境)，请耐心等待...")
    run_cmd("pacstrap", "/mnt", "base", "base-devel linux linux-firmware vim openssh dhcpcd networkmanager grub efibootmgr ttf-dejavu wqy-microhei fish xorg git wget curl", de, ucode)
    print("OK")

    # 生成fstab
    print("正在生成fstab...")
    run_cmd("genfstab", "-U", "/mnt", ">>", "/mnt/etc/fstab")
    print("OK")

    # chroot
    print("正在切换根目录...")
    run_cmd("arch-chroot", "/mnt")
    print("OK")

    # 设置时区
    print("正在设置时区...")
    run_cmd("ln", "-sf", "/usr/share/zoneinfo/Asia/Shanghai", "/etc/localtime")
    run_cmd("hwclock", "--systohc")
    print("OK")

    # 本地化
    print("正在设置语言...")
    run_cmd("sed", "-in-place", "-e", "'s/#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/g'", "/etc/locale.gen")
    run_cmd("sed", "-in-place", "-e", "'s/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g'", "/etc/locale.gen")
    run_cmd("locale-gen")
    if desktop == 0:
        run_cmd('echo', '"LANG=en_US.UTF-8"', '>', '/etc/locale.conf')
    else:
        run_cmd('echo', '"LANG=zh_CN.UTF-8"', '>', '/etc/locale.conf')
    print("OK")

    # Host
    print("正在设置host...")
    host = input("请输入hostname: ")
    run_cmd('echo', f'"{host}"', '>', '/etc/hostname')
    run_cmd('''tee /etc/hosts <<-'EOF'
127.0.0.1	localhost
::1		localhost
EOF''')
    print("OK")

    # 设置各种必要服务开机自启
    print("设置必要服务开机自启...")
    run_cmd("systemctl", "enable", "dhcpcd")
    run_cmd("systemctl", "enable", "NetworkManager")
    run_cmd("systemctl", "enable", "sshd")
    if desktop == 1:
        run_cmd("systemctl", "enable", "gdm")
    if desktop == 2:
        run_cmd("systemctl", "enable", "sddm")
    print("OK")

    # 用户和密码
    print("正在设置用户名和密码...")
    username = input("请输入新用户名: ")
    while username == "root":
        username = input("用户名有误请重新输入: ")
    passwd = input("请为管理员用户设置密码: ")
    run_cmd('echo', '-e', f"{passwd}\n{passwd}\n", "|", "passwd")
    run_cmd("useradd", "-m", "-G", "wheel", "-s", "/bin/fish", username)
    run_cmd('echo', '-e', f"{passwd}\n{passwd}\n", "|", "passwd", username)
    run_cmd("sed", "-in-place", "-e", "'s/# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/g'", "/etc/sudoers")
    print("OK")

    # grub
    print("正在配置引导...")
    if IS_UEFI:
        run_cmd("grub-install", "--target=x86_64-efi", "--efi-directory=/boot/EFI", "--bootloader-id=GRUB")
        run_cmd("grub-mkconfig", "-o", "/boot/grub/grub.cfg")
    # todo BIOS
    print("OK")

    # 结束工作
    print("正在进行收尾工作...")
    run_cmd("exit")
    run_cmd("umount", "-R", "/mnt")
    print("系统将在五秒钟后关机，关机后请拔出U盘，手动开机")
    time.sleep(5)
    run_cmd("poweroff")


if __name__ == '__main__':
    main()
