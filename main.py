#!/usr/bin/python
# This is ArchLinux install script

import os
import re
import sys
import subprocess
import platform
import time

UEFI = True
BIOS = False

NO_DESKTOP = 0
GNOME = 1
PLASMA = 2


def just_run(prompt:str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"正在{prompt}...")
            func(*args, **kwargs)
            print("OK")
        return wrapper
    return decorator


def check_platform():
    return platform.uname()[0] == "Linux" and platform.uname()[1] == "archiso"


def check_boot():
    if os.path.exists("/sys/firmware/efi/efivars"):
        return UEFI
    return BIOS


def check_network():
    code, _ = subprocess.getstatusoutput("ping -c 3 www.baidu.com")
    return code == 0


def run_cmd(*cmd):
    cmd_str = " ".join(cmd)
    code, output = subprocess.getstatusoutput(cmd_str)
    try:
        assert code == 0
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


class Installation:
    def __init__(self, boot, desktop, disk, swap, hostname, username, password, ucode):
        self.name = "base"
        self.boot = boot
        self.desktop = desktop
        self.disk = disk
        self.swap = swap
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ucode = ucode

    @staticmethod
    def run_cmd(cmd:str):
        """
        运行命令 todo
        """
        print(cmd)

    @just_run("更新系统时间")
    def update_datetime(self):
        """
        更新系统时间
        """
        self.run_cmd("timedatectl set-ntp true")

    @just_run("磁盘分区")
    def disk_partition(self):
        """
        磁盘分区: 包含分区，格式化，挂载，三步骤 todo
        """
        part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "",  # 删除现有分区
                              "g",  # 新建gpt分区表
                              "n", "", "", "+512M",  # 新建EFI分区/boot分区
                              "n", "", "", f"+{self.swap}G",  # swap分区
                              "n", "", "", "",  # 根分区
                              "w"  # 写入
                              )
        self.run_cmd(f"{part} {self.disk}")
        if self.boot == UEFI:
            # 格式化
            self.run_cmd(f"mkfs.vfat {self.disk}1")
            self.run_cmd(f"mkswap {self.disk}2")
            self.run_cmd(f"mkfs.ext4 {self.disk}3")
            # 挂载
            self.run_cmd(f"mount {self.disk}3 /mnt")
            self.run_cmd("mkdir -p /mnt/boot/EFI")
            self.run_cmd(f"mount {self.disk}1 /mnt/boot/EFI")
            self.run_cmd(f"swapon {self.disk}2")
        elif self.boot == BIOS:
            # 格式化
            self.run_cmd(f"mkfs.ext2 {self.disk}1")
            self.run_cmd(f"mkswap {self.disk}2")
            self.run_cmd(f"mkfs.ext4 {self.disk}3")
            # 挂载
            self.run_cmd(f"mount {self.disk}3 /mnt")
            self.run_cmd("mkdir -p /mnt/boot")
            self.run_cmd(f"mount {self.disk}1 /mnt/boot")
            self.run_cmd(f"swapon {self.disk}2")

    @just_run("下载基础软件包")
    def download_linux(self):
        """
        下载linux基础软件包
        """
        self.run_cmd(f"pacstrap /mnt base base-devel linux linux-firmware vim openssh {self.ucode}")

    @just_run("生成fstab文件")
    def gen_fstab(self):
        """
        生成fstab文件
        """
        self.run_cmd("genfstab -U /mnt >> /mnt/etc/fstab")

    @just_run("切换根目录")
    def chroot(self):
        """
        切换根目录
        """
        self.run_cmd("arch-chroot /mnt")

    @just_run("设置时区")
    def set_timezone(self):
        """
        设置时区
        """
        self.run_cmd("ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime")
        self.run_cmd("hwclock --systohc")

    @just_run("设置地区")
    def set_locale(self):
        """
        系统语言设置
        """
        self.run_cmd("sed -in-place -e 's/#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/g' /etc/locale.gen")
        self.run_cmd("sed -in-place -e 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g' /etc/locale.gen")
        self.run_cmd("locale-gen")
        self.run_cmd('echo "LANG=en_US.UTF-8" > /etc/locale.conf')

    @just_run("设置host")
    def set_host(self):
        """
        设置系统host
        """
        self.run_cmd(f'echo "{self.hostname}" > /etc/hostname')
        self.run_cmd('''tee /etc/hosts <<-'EOF'
        127.0.0.1	localhost
        ::1		localhost
        EOF''')

    @just_run("设置网络")
    def set_network(self):
        """
        设置系统网络：包括下载，自启动
        """
        self.run_cmd("pacman -S dhcpcd networkmanager")
        self.run_cmd("systemctl enable dhcpcd")
        self.run_cmd("systemctl enable NetworkManager")

    @just_run("设置grub引导")
    def set_grub(self):
        """
        设置grub引导
        """
        if self.boot == UEFI:
            self.run_cmd("pacman -S grub efibootmgr")
            self.run_cmd("grub-install --target=x86_64-efi --efi-directory=/boot/EFI --bootloader-id=GRUB")
            self.run_cmd("grub-mkconfig -o /boot/grub/grub.cfg")
        elif self.boot == BIOS:
            self.run_cmd("pacman -S grub")
            self.run_cmd(f"grub-install {self.disk}")
            self.run_cmd("grub-mkconfig -o /boot/grub/grub.cfg")

    @just_run("设置用户名和密码")
    def set_user(self):
        """
        设置普通用户
        """
        self.run_cmd(f'echo -e "{self.password}\\n{self.password}\\n" | passwd')
        self.run_cmd(f"useradd -m -G wheel -s /bin/bash {self.username}")
        self.run_cmd(f'echo -e "{self.password}\\n{self.password}\\n" | passwd {self.username}')
        self.run_cmd("sed -in-place -e 's/# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/g' /etc/sudoers")

    @just_run("设置桌面环境")
    def set_desktop(self):
        """
        设置桌面环境
        """
        if self.desktop == NO_DESKTOP:
            return
        self.run_cmd("pacman -S xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics")
        self.run_cmd("pacman -S ttf-dejavu wqy-microhei git wget curl")
        if self.desktop == GNOME:
            self.run_cmd("pacman -S gdm gnome gnome-extra")
            self.run_cmd("systemctl enable gdm")
        elif self.desktop == PLASMA:
            self.run_cmd("pacman -S plasma kde-applications")
            self.run_cmd("systemctl enable sddm")

    @just_run("进行收尾工作")
    def finish(self):
        """
        收尾工作
        """
        self.run_cmd("exit")
        self.run_cmd("umount -R /mnt")


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
    boot = check_boot()
    # 选择桌面
    desktop = int(input("脚本支持以下桌面环境:\n0. 无桌面\n1. gnome\n2. plasma\n请选择桌面环境: "))
    while desktop not in (0, 1, 2):
        desktop = int(input("输入有误请重新输入"))
    # 选择磁盘
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

    # 选择swap
    swap_mem = int(input("请输入swap分区的内存大小(单位G): "))
    while swap_mem < 1:
        swap_mem = int(input("输入不合法，请重新输入: "))

    # hostname
    host = input("请输入hostname: ")

    # username & password
    username = input("请输入新用户名: ")
    while username == "root":
        username = input("用户名有误请重新输入: ")
    passwd = input("请为管理员用户设置密码: ")


    # ucode
    ucode = ""
    code = int(input("脚本支持以下cpu:\n0. intel\n1. amd\n2. 其他\n请选择你的cpu类型: "))
    while code not in (0, 1, 2):
        code = int(input("输入有误请重新输入: "))
    if code == 0:
        ucode = "intel-ucode"
    elif code == 1:
        ucode = "amd-ucode"

    installation = Installation(boot, desktop, disks[choose_index], swap_mem, host, username, passwd, ucode)

    # ======================= 下面是正式安装过程 ======================= #
    installation.update_datetime()
    installation.disk_partition()
    installation.download_linux()
    installation.gen_fstab()
    installation.chroot()
    installation.set_timezone()
    installation.set_locale()
    installation.set_host()
    installation.set_network()
    installation.set_grub()
    installation.set_user()
    installation.set_desktop()
    installation.finish()

    print("SUCCESS")


if __name__ == '__main__':
    main()
