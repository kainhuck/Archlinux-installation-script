#!/usr/bin/python

# =============================================
# The install script for Archlinux installation
# =============================================

import os
import sys
import platform
import subprocess

# =================================== global values ====================================

support_shells = ["bash", "zsh", "fish"]
support_desktops = ["no_desktop", "gnome", "plasma"]
support_language = ["en", "zh"]

base_packages = "base base-devel linux linux-firmware vim openssh zsh fish git wget curl grub dhcpcd net-tools"

UEFI = "UEFI"
BIOS = "BIOS"

CPU_AMD = "AuthenticAMD"
CPU_INTEL = "GenuineIntel"


# ======================================================================================


# =================================== color function ===================================

def apply_red(s) -> str:
    return f"\033[31m{s}\033[0m"


def apply_green(s) -> str:
    return f"\033[32m{s}\033[0m"


def apply_yellow(s) -> str:
    return f"\033[33m{s}\033[0m"


def apply_blue(s) -> str:
    return f"\033[34m{s}\033[0m"


def apply_purple(s) -> str:
    return f"\033[35m{s}\033[0m"


def apply_cyan(s) -> str:
    return f"\033[36m{s}\033[0m"


# ======================================================================================


def run_cmd(cmd: str, debug: bool = True, exit_: bool = True) -> str:
    if debug:
        print("{} {}".format(apply_cyan("[RUN]"), apply_yellow(cmd)))

    code, output = subprocess.getstatusoutput(cmd)

    try:
        assert code == 0
    except AssertionError:
        if exit_:
            print("{}".format(apply_red(f"ERROR: {output}")))
            sys.exit(code)
        else:
            return ""

    return output


def run_cmd_chroot(cmd: str, debug: bool = True, exit_: bool = True) -> str:
    run_cmd(f"arch-chroot /mnt {cmd}", debug, exit_)


def disk_partition(*ops):
    cmd_format = 'echo -e "{args}" | fdisk '
    args = []
    for p in ops:
        args.append(f"{p}\\n")
    return cmd_format.format(args="".join(args))


def read_str(prompt: str) -> str:
    s = input(apply_blue(f"{prompt} >>> "))

    while len(s) == 0:
        print("{}".format(apply_red("can't input none")))
        s = input(apply_blue(f"{prompt} >>> "))

    return s


def read_int(prompt: str, pos: bool = False) -> int:
    while True:
        int_str = read_str(prompt)
        try:
            n = int(int_str)
            if pos:
                if n < 0:
                    print("{}".format(apply_red("must be a positive integer")))
                    continue
                else:
                    return n
            else:
                return n
        except:
            print("{}".format(apply_red("please input a integer")))
            continue


def choose_from_list(subject: str, items: list) -> object:
    print("{}{}{}".format(apply_purple("please choose a "), apply_yellow(subject), apply_purple(" from bellow")))
    for i, d in enumerate(items):
        print("{}. {}".format(apply_yellow(i), apply_cyan(d)))
    while True:
        n = read_int("please choose a number", True)
        if n > len(items) - 1:
            print("{}".format(apply_red(f"big then {len(items) - 1}")))
            continue
        else:
            return items[n]


class DiskMount:
    def __init__(self, disk: str, mount_point: str):
        self.disk = disk
        self.mount_point = mount_point


class User:
    def __init__(self, name: str, passwd: str, shell: str = "bash"):
        self.name = name
        self.passwd = passwd
        self.shell = shell


class Config:
    def __init__(self):
        self.boot = None
        self.cpu_vendor = None
        self.install_disk = None
        self.disk_mount = []  # DiskMount TODO
        self.desktop = None
        self.root_passwd = None
        self.common_users = []  # User
        self.language = None  # TODO
        self.swap_size = None
        self.hostname = None

        self._detect_platform()
        self._detect_boot()
        self._detect_cpu_vendor()

        self.set_install_disk()
        self.set_desktop()
        self.set_root_passwd()
        self.set_common_users()
        self.set_swap_size()
        self.set_hostname()

    @staticmethod
    def _detect_platform():
        """自动检测平台，是否是archlinux安装环境"""
        if platform.uname().system != "Linux" or platform.uname().node != "archiso":
            print("{}".format(apply_red("This script only for archlinux installation")))
            sys.exit(0)

    def _detect_boot(self):
        """自动检测启动类型"""
        if os.path.exists("/sys/firmware/efi/efivars"):
            self.boot = UEFI
        else:
            self.boot = BIOS

    def _detect_cpu_vendor(self):
        """自动检测CPU类型"""
        self.cpu_vendor = run_cmd("lscpu | grep Vendor | awk '{print $3}'", False, False)

    def set_install_disk(self):
        """设置安装磁盘"""
        all_disk = run_cmd("fdisk -l | grep 'Disk /dev/' | awk '{print $2}'", False, True).split("\n")
        real_disks = []
        for d in all_disk:
            if d.count("loop") > 0 or d.count("rom") > 0 or d.count("airoot") > 0 or d.count("ram") > 0:
                pass
            else:
                real_disks.append(d[:len(d) - 1])

        if len(real_disks) == 0:
            print("{}".format(apply_red("there no disk in this node!")))
            sys.exit(0)
        elif len(real_disks) == 1:
            self.install_disk = real_disks[0]
        else:
            self.install_disk = choose_from_list("disk", real_disks)

    def set_desktop(self):
        """设置桌面环境"""
        self.desktop = choose_from_list("desktop", support_desktops)

    def set_root_passwd(self):
        """设置root用户密码"""
        self.root_passwd = read_str("please set root's password")

    def set_common_users(self):
        """设置普通用户"""
        yn = read_str("need common users? [y/n]")
        if yn.lower() != "y":
            return
        while True:
            name = read_str("please input username")
            if name == "root" or name in [item.name for item in self.common_users]:
                print("{}".format(apply_red(f"{name} already taken")))
                continue
            passwd = read_str(f"please input password for {name}")
            shell = choose_from_list(f"shell for {name}", support_shells)
            assert isinstance(shell, str)
            self.common_users.append(User(name, passwd, shell))
            yn = read_str("need another user? [y/n]")
            if yn.lower() != "y":
                return

    def set_swap_size(self):
        """设置 swap 大小"""
        self.swap_size = read_int("please set swap size (G)", True)

    def set_hostname(self):
        """设置hostname"""
        self.hostname = read_str("please set hostname")

    def print_info(self):
        print("{}: {}".format(apply_blue("BOOT"), apply_green(f"{self.boot}")))
        print("{}: {}".format(apply_blue("CPU"), apply_green(f"{self.cpu_vendor}")))
        print("{}: {}".format(apply_blue("INSTALLATION"), apply_green(f"{self.install_disk}")))
        print("{}: {}".format(apply_blue("DESKTOP"), apply_green(f"{self.desktop}")))
        print("{}: {}".format(apply_blue("HOSTNAME"), apply_green(f"{self.hostname}")))
        print("{}: {}".format(apply_blue("SWAP_SIZE"), apply_green(f"{self.swap_size}G")))
        print("{}: {}".format(apply_blue("ROOT_PASSWORD"), apply_green(f"{self.root_passwd}")))

        for i, u in enumerate(self.common_users):
            assert isinstance(u, User)
            print("{}: {}".format(apply_blue(f"USER{i + 1}"), apply_green(f"{u.name}")))
            print("{}: {}".format(apply_blue(f"PASSWORD{i + 1}"), apply_green(f"{u.passwd}")))
            print("{}: {}".format(apply_blue(f"SHELL{i + 1}"), apply_green(f"{u.shell}")))


class Installation:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    @staticmethod
    def update_time():
        """更新系统时间"""
        run_cmd("timedatectl set-ntp true")

    def disk_part(self):
        """磁盘分区"""
        if self.cfg.boot == UEFI:
            part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "",  # 删除现有分区
                                  "g",  # 新建gpt分区表
                                  "n", "", "", "", "+512M",  # 新建EFI分区/boot分区
                                  "n", "", "", "", f"+{self.cfg.swap_size}G",  # swap分区
                                  "n", "", "", "", "",  # 根分区
                                  "w"  # 写入
                                  )
            run_cmd(part+self.cfg.install_disk)
            # 格式化
            run_cmd(f"mkfs.vfat {self.cfg.install_disk}1")
            run_cmd(f"mkswap {self.cfg.install_disk}2")
            run_cmd(f"mkfs.ext4 {self.cfg.install_disk}3")
            # 挂载
            run_cmd(f"mount {self.cfg.install_disk}3 /mnt")
            run_cmd("mkdir -p /mnt/boot/EFI")
            run_cmd(f"mount {self.cfg.install_disk}1 /mnt/boot/EFI")
            run_cmd(f"swapon {self.cfg.install_disk}2")
        elif self.cfg.boot == BIOS:
            part = disk_partition("d", "", "d", "", "d", "", "d", "", "d", "", "d", "", "d", "",  # 删除现有分区
                                  "o",  # 新建mbr分区表
                                  "n", "", "", "", "+512M",  # 新建EFI分区/boot分区
                                  "n", "", "", "", f"+{self.cfg.swap_size}G",  # swap分区
                                  "n", "", "", "", "",  # 根分区
                                  "w"  # 写入
                                  )
            run_cmd(part+self.cfg.install_disk)
            # 格式化
            run_cmd(f"mkfs.ext2 {self.cfg.install_disk}1")
            run_cmd(f"mkswap {self.cfg.install_disk}2")
            run_cmd(f"mkfs.ext4 {self.cfg.install_disk}3")
            # 挂载
            run_cmd(f"mount {self.cfg.install_disk}3 /mnt")
            run_cmd("mkdir -p /mnt/boot")
            run_cmd(f"mount {self.cfg.install_disk}1 /mnt/boot")
            run_cmd(f"swapon {self.cfg.install_disk}2")
        else:
            print("{}".format(apply_red(f"unsupported boot {self.cfg.boot}")))
            sys.exit(0)

    def download_linux(self):
        packages = base_packages
        if self.cfg.cpu_vendor == CPU_AMD:
            packages += " amd-ucode"
        elif self.cfg.cpu_vendor == CPU_INTEL:
            packages += " intel-ucode"

        if self.cfg.boot == UEFI:
            packages += " efibootmgr"

        if self.cfg.desktop == "gnome":
            packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei gdm gnome gnome-extra"
        elif self.cfg.desktop == "plasma":
            packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei plasma kde-applications libdbusmenu-glib appmenu-gtk-module packagekit-qt5"

        run_cmd("pacstrap /mnt " + packages)

    @staticmethod
    def gen_fstab():
        """生成fstab文件"""
        run_cmd("genfstab -U /mnt >> /mnt/etc/fstab")

    @staticmethod
    def set_timezone():
        """设置时区"""
        run_cmd_chroot("ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime")
        run_cmd_chroot("hwclock --systohc")

    @staticmethod
    def set_locale():
        """本地化设置"""
        run_cmd_chroot("sed -in-place -e 's/#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/g' /etc/locale.gen")
        run_cmd_chroot("sed -in-place -e 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g' /etc/locale.gen")
        run_cmd_chroot("locale-gen")
        run_cmd_chroot('echo "LANG=en_US.UTF-8" > /etc/locale.conf')

    def set_hostname(self):
        """设置hostname"""
        run_cmd_chroot(f'echo "{self.cfg.hostname}" > /etc/hostname')
        run_cmd_chroot('''tee /etc/hosts <<-'EOF'\n127.0.0.1	localhost\n::1		localhost\nEOF''')

    def set_network(self):
        """网络设置"""
        run_cmd_chroot("systemctl enable dhcpcd")
        if self.cfg.desktop != "no_desktop":
            run_cmd_chroot("systemctl enable NetworkManager")

    def set_user(self):
        """用户设置"""
        run_cmd_chroot(f"sh -c \"echo 'root:{self.cfg.root_passwd}' | chpasswd\"")

        for u in self.cfg.common_users:
            run_cmd_chroot(f"useradd -m -G wheel -s /bin/{u.shell} {u.name}")
            run_cmd_chroot(f"sh -c \"echo '{u.name}:{u.passwd}' | chpasswd\"")

        run_cmd_chroot("sed -in-place -e 's/# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/g' /etc/sudoers")

    def set_grub(self):
        """引导设置"""
        if self.cfg.boot == UEFI:
            run_cmd_chroot("grub-install --target=x86_64-efi --efi-directory=/boot/EFI --bootloader-id=GRUB")
            run_cmd_chroot("grub-mkconfig -o /boot/grub/grub.cfg")
        elif self.cfg.boot == BIOS:
            run_cmd_chroot(f"grub-install {self.cfg.install_disk}")
            run_cmd_chroot("grub-mkconfig -o /boot/grub/grub.cfg")

    def set_desktop(self):
        """设置桌面环境"""
        if self.cfg.desktop == "no_desktop":
            return

        run_cmd_chroot(f"sh -c \"echo 'LANG=zh_CN.UTF-8' > /etc/locale.conf\"")
        if self.cfg.desktop == "gnome":
            run_cmd_chroot("systemctl enable gdm")
        elif self.cfg.desktop == "plasma":
            run_cmd_chroot("systemctl enable sddm")

    @staticmethod
    def finish():
        """一些收尾工作"""
        run_cmd_chroot("systemctl enable sshd")
        run_cmd("umount -R /mnt")


# ======================================================================================

def main():
    cfg = Config()
    print("{}".format(apply_yellow("========= please check info ========")))
    cfg.print_info()
    print("{}".format(apply_yellow("====================================")))

    yn = read_str("ready to install [y/n]")
    if yn.lower() != "y":
        return

    install = Installation(cfg)

    install.update_time()
    install.disk_part()
    install.download_linux()
    install.gen_fstab()
    install.set_timezone()
    install.set_locale()
    install.set_hostname()
    install.set_network()
    install.set_user()
    install.set_grub()
    install.set_desktop()
    install.finish()

    print("{}".format(apply_green("install successfully please reboot your computer")))


if __name__ == '__main__':
    main()
