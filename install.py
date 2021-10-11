#!/usr/bin/python
# This is ArchLinux install script

import os
import re
import sys
import subprocess
import platform

UEFI = True
BIOS = False

NO_DESKTOP = 0
GNOME = 1
PLASMA = 2


def just_run(prompt: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\033[34m正在{prompt}...\033[0m")
            func(*args, **kwargs)
            print("\033[32mOK\033[0m")

        return wrapper

    return decorator


@just_run("检查平台")
def check_platform():
    if not platform.uname()[0] == "Linux" and platform.uname()[1] == "archiso":
         print("This script only for archlinux installation")
         sys.exit(0)


def check_boot():
    if os.path.exists("/sys/firmware/efi/efivars"):
        return UEFI
    return BIOS


@just_run("检查网络")
def check_network():
    code, _ = subprocess.getstatusoutput("ping -c 3 www.baidu.com")
    if not code == 0:
        print("Please connect Internet")
        sys.exit(0)


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


def find_disk():
    output = run_cmd("fdisk", "-l")
    disks_ = re.findall("(/dev/.+?: [0-9 .]+? .+?iB)", output)
    disks = []
    for each in disks_:
        if "rom" in each or "loop" in each or "airoot" in each:
            continue
        else:
            disks.append(each)

    if len(disks):
        print("\033[34m发现如下可用磁盘:\033[30m")
        for i in range(len(disks)):
            print(f"\033[35m{i} - {disks[i]}\033[30m")
    else:
        print("未发现可用磁盘，程序退出")
        sys.exit(0)

    choose_index_str = input("\033[34m请从上面选择一个要安装的磁盘(输入序号，默认0): \033[30m")
    choose_index = 0
    if len(choose_index_str) != 0:
        choose_index = int(choose_index_str)
    while choose_index < 0 or choose_index >= len(disks):
        choose_index = int(input("\033[31m输入的序号有误，请重新输入: \033[30m"))

    return disks[choose_index].split(":")[0]


class Installation:
    def __init__(self, boot, desktop, disk, swap, hostname, username, password, ucode):
        self.boot = boot
        self.desktop = desktop
        self.disk = disk
        self.swap = swap
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ucode = ucode

    @staticmethod
    def run_cmd(cmd: str):
        """
        运行命令
        """
        print(f"\033[33mRUN\033[30m >>> \033[36m{cmd}\033[0m")
        code = os.system(cmd)
        if code != 0:
            sys.exit(code)
    
    def run_cmd_chroot(self, cmd: str):
        """
        运行命令 arch-chroot
        """
        self.run_cmd(f"arch-chroot /mnt {cmd}")

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
        if self.boot == UEFI:
            part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "",  # 删除现有分区
                              "g",  # 新建gpt分区表
                              "n", "", "", "+512M",  # 新建EFI分区/boot分区
                              "n", "", "", f"+{self.swap}G",  # swap分区
                              "n", "", "", "",  # 根分区
                              "w"  # 写入
                              )
            run_cmd(part, self.disk)
            # 格式化
            run_cmd(f"mkfs.vfat {self.disk}1")
            run_cmd(f"mkswap {self.disk}2")
            run_cmd(f"mkfs.ext4 {self.disk}3")
            # 挂载
            self.run_cmd(f"mount {self.disk}3 /mnt")
            self.run_cmd("mkdir -p /mnt/boot/EFI")
            self.run_cmd(f"mount {self.disk}1 /mnt/boot/EFI")
            self.run_cmd(f"swapon {self.disk}2")
        elif self.boot == BIOS:
            part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "",  # 删除现有分区
                              "o",  # 新建mbr分区表
                              "n", "", "", "", "+512M", "Y",  # 新建EFI分区/boot分区
                              "n", "", "", "", f"+{self.swap}G", "Y",  # swap分区
                              "n", "", "", "", "", "Y",  # 根分区
                              "w"  # 写入
                              )
            run_cmd(part, self.disk)
            # 格式化
            run_cmd(f"mkfs.ext2 {self.disk}1")
            run_cmd(f"mkswap {self.disk}2")
            run_cmd(f"mkfs.ext4 {self.disk}3")
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
        self.run_cmd(f"pacstrap /mnt base base-devel linux linux-firmware vim openssh zsh git wget curl {self.ucode}")

    @just_run("生成fstab文件")
    def gen_fstab(self):
        """
        生成fstab文件
        """
        self.run_cmd("genfstab -U /mnt >> /mnt/etc/fstab")

    @just_run("设置时区")
    def set_timezone(self):
        """
        设置时区
        """
        self.run_cmd_chroot("ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime")
        self.run_cmd_chroot("hwclock --systohc")

    @just_run("设置地区")
    def set_locale(self):
        """
        系统语言设置
        """
        self.run_cmd_chroot("sed -in-place -e 's/#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/g' /etc/locale.gen")
        self.run_cmd_chroot("sed -in-place -e 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g' /etc/locale.gen")
        self.run_cmd_chroot("locale-gen")
        self.run_cmd_chroot('echo "LANG=en_US.UTF-8" > /etc/locale.conf')

    @just_run("设置host")
    def set_host(self):
        """
        设置系统host
        """
        self.run_cmd_chroot(f'echo "{self.hostname}" > /etc/hostname')
        self.run_cmd_chroot('''tee /etc/hosts <<-'EOF'
127.0.0.1	localhost
::1		localhost
EOF''')

    @just_run("设置网络")
    def set_network(self):
        """
        设置系统网络：包括下载，自启动
        """
        self.run_cmd("pacstrap /mnt dhcpcd networkmanager")
        self.run_cmd_chroot("systemctl enable dhcpcd")
        self.run_cmd_chroot("systemctl enable NetworkManager")

    @just_run("设置grub引导")
    def set_grub(self):
        """
        设置grub引导
        """
        if self.boot == UEFI:
            self.run_cmd("pacstrap /mnt grub efibootmgr")
            self.run_cmd_chroot("grub-install --target=x86_64-efi --efi-directory=/boot/EFI --bootloader-id=GRUB")
            self.run_cmd_chroot("grub-mkconfig -o /boot/grub/grub.cfg")
        elif self.boot == BIOS:
            self.run_cmd("pacstrap /mnt grub")
            self.run_cmd_chroot(f"grub-install {self.disk}")
            self.run_cmd_chroot("grub-mkconfig -o /boot/grub/grub.cfg")

    @just_run("设置用户名和密码")
    def set_user(self):
        """
        设置普通用户
        """
        self.run_cmd_chroot(f"sh -c \"echo 'root:{self.password}' | chpasswd\"")
        self.run_cmd_chroot(f"useradd -m -G wheel -s /bin/zsh {self.username}")
        self.run_cmd_chroot(f"sh -c \"echo '{self.username}:{self.password}' | chpasswd\"")
        self.run_cmd_chroot("sed -in-place -e 's/# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/g' /etc/sudoers")

    @just_run("设置桌面环境")
    def set_desktop(self):
        """
        设置桌面环境
        """
        if self.desktop == NO_DESKTOP:
            return
        self.run_cmd("pacstrap /mnt xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics")
        self.run_cmd("pacstrap /mnt ttf-dejavu wqy-microhei")
        if self.desktop == GNOME:
            self.run_cmd("pacstrap /mnt gdm gnome gnome-extra")
            self.run_cmd_chroot("systemctl enable gdm")
        elif self.desktop == PLASMA:
            self.run_cmd("pacstrap /mnt plasma kde-applications libdbusmenu-glib appmenu-gtk-module packagekit-qt5")
            self.run_cmd_chroot("systemctl enable sddm")

    @just_run("进行收尾工作")
    def finish(self):
        """
        收尾工作
        """
        self.run_cmd("umount -R /mnt")


def main():
    # ======================= 检查安装环境 ======================= #
    # 检查平台
    check_platform()

    # 检查网络
    check_network()

    # 确定引导方式
    boot = check_boot()

    # 选择桌面
    desktop = int(input("\033[32m脚本支持以下桌面环境:\033[30m\n\033[35m0. 无桌面\n1. gnome\n2. plasma\n\033[32m请选择桌面环境: \033[30m"))
    while desktop not in (0, 1, 2):
        desktop = int(input("\033[31m输入有误请重新输入: \033[30m"))

    # 选择磁盘
    disk = find_disk()

    # 选择swap
    swap_mem = int(input("\033[36m请输入swap分区的内存大小(单位G): \033[30m"))
    while swap_mem < 1:
        swap_mem = int(input("\033[31m输入不合法，请重新输入: \033[30m"))

    # hostname
    host = input("\033[33m请输入hostname: \033[30m")

    # username & password
    username = input("\033[33m请输入新用户名: \033[30m")
    while username == "root":
        username = input("\033[31m用户名有误请重新输入: \033[30m")
    passwd = input("\033[33m请为管理员用户设置密码: \033[30m")

    # ucode
    ucode = ""
    code = int(input("\033[32m脚本支持以下cpu:\n\033[35m0. intel\n1. amd\n2. 其他\n\033[32m请选择你的cpu类型: \033[30m"))
    while code not in (0, 1, 2):
        code = int(input("\033[31m输入有误请重新输入: \033[30m"))
    if code == 0:
        ucode = "intel-ucode"
    elif code == 1:
        ucode = "amd-ucode"

    print("\033[33m=============信息确认=============\033[30m")
    print(f"\033[33m= \033[36m引导方式: {('BIOS', 'UEFI')[boot]}\033[30m")
    print(f"\033[33m= \033[36m桌面环境: {('无桌面', 'Gnome', 'Plasma')[desktop]}\033[30m")
    print(f"\033[33m= \033[36m安装磁盘: {disk}\033[30m")
    print(f"\033[33m= \033[36mswap大小: {swap_mem}G\033[30m")
    print(f"\033[33m= \033[36mhostname: {host}\033[30m")
    print(f"\033[33m= \033[36mcpu类型: {('intel', 'amd', 'other')[code]}\033[30m")
    print(f"\033[33m= \033[36m用户名: {username}\033[30m")
    print(f"\033[33m= \033[36m密码(root用户也会设置为该密码): {passwd}\033[30m")
    print("\033[33m===============================\033[30m")
    yn = input("确认信息无误(Y/n): ")
    if yn.lower() == "n":
        print("未开始安装, 安装退出")
        exit(0)

    installation = Installation(boot, desktop, disk, swap_mem, host, username, passwd, ucode)

    # ======================= 下面是正式安装过程 ======================= #
    installation.update_datetime()
    installation.disk_partition()
    installation.download_linux()
    installation.gen_fstab()
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
