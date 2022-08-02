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
        self.disk_mount = []    # DiskMount TODO
        self.desktop = None
        self.root_passwd = None
        self.common_users = []  # User
        self.language = None    # TODO
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


# ======================================================================================

def main():
    cfg = Config()

    # cfg.set_desktop()
    # cfg.set_root_password()
    # cfg.set_common_users()
    # cfg.set_language()
    # cfg.set_swap_size()
    # cfg.set_hostname()
    # print_purple("All config is finish, please check the info below")
    # cfg.print_info()
    # print_yellow("Install process will clear all data in disk, are you sure going on? [N/y]")
    # ys = input(">>> ").lower()
    # if ys != "y":
    #     print_yellow("Quit")
    #     return

    # packages
    # global base_packages
    # if cfg.boot == "UEFI":
    #     base_packages += " efibootmgr"

    # if cfg.desktop == "gnome":
    #     base_packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei gdm gnome gnome-extra"
    # elif cfg.desktop == "plasma":
    #     base_packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei plasma kde-applications libdbusmenu-glib appmenu-gtk-module packagekit-qt5"


if __name__ == '__main__':
    main()
