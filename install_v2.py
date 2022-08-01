#!/usr/bin/python

# =============================================
# The install script for Archlinux installation
# =============================================

from doctest import FAIL_FAST
import os
import re
import sys
import platform
import subprocess


# =================================== global values ====================================

support_shells = ("bash", "zsh", "fish")
support_desktops = ("gnome", "plasma")
support_language = ("en", "zh")

base_packages = "base base-devel linux linux-firmware vim openssh zsh fish git wget curl grub dhcpcd net-tools"

UEFI = "UEFI"
BIOS = "BIOS"

CPU_AMD = "AuthenticAMD"
CPU_INTEL = "GenuineIntel"

# ======================================================================================


# =================================== color function ===================================

def apply_red(s:str) -> str:
    return f"\033[31m{s}\033[0m"

def apply_green(s:str) -> str:
    return f"\033[32m{s}\033[0m"


def apply_yellow(s:str) -> str:
    return f"\033[33m{s}\033[0m"


def apply_blue(s:str) -> str:
    return f"\033[34m{s}\033[0m"


def apply_purple(s:str) -> str:
    return f"\033[35m{s}\033[0m"


def apply_cyan(s:str) -> str:
    return f"\033[36m{s}\033[0m"

# ======================================================================================


def run_cmd(cmd: str, debug:bool=True, exit:bool=True) -> str:
    if debug:
        print("%s %s" % apply_cyan("[RUN]"), apply_yellow(cmd))

    code, output = subprocess.getstatusoutput(cmd)

    try:
        assert code == 0
    except AssertionError:
        if exit:
            print("%s" % apply_red(f"ERROR: {output}"))
            sys.exit(code)
        else:
            return ""

    return output


class DiskMount:
    def __init__(self, disk:str, mount_point:str):
        self.disk = disk
        self.mount_point = mount_point

class User:
    def __init__(self, name:str, passwd: str, shell:str="bash"):
        self.name = name
        self.passwd = passwd
        self.shell = shell


class Config:
    def __init__(self):
        self.boot = None
        self.cpu_vendor = None
        self.install_disk = None
        self.disk_mount = []   # DiskMount
        self.desktop = None
        self.root_passwd = None
        self.common_users = [] # User
        self.language = None
        self.swap_size = None
        self.hostname = None

        # self._detect_platform()
        self._detect_boot()
        self._detect_cpu_vendor()
    
    def _detect_platform(self):
        """自动检测平台，是否是archlinux安装环境"""
        if platform.uname().system != "Linux" or platform.uname().node != "archiso":
            print("%s" % apply_red("This script only for archlinux installation"))
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

    def set_disk_mount(self):
        all_disk = run_cmd("fdisk -l | grep 'Disk /dev/' | awk '{print $2}'", False, True).split("\n")
        real_disks = []
        for d in all_disk:
            if d.count("loop") > 0 or d.count("rom") > 0 or d.count("airoot") > 0 or d.count("ram") > 0:
                pass
            else:
                real_disks.append(d[:len(d)-1])
        
        if len(real_disks) == 0:
            print("%s" % apply_red("there no disk in this node!"))
            sys.exit(0)
        elif len(real_disks) == 1:
            self.install_disk = real_disks[0]
        else:
            print("%s" % apply_purple("please choose a disk from bellow"))
            for i, d in enumerate(real_disks):
                print("%s. %s" % (apply_yellow(i), apply_cyan(d)))
            while True:
                n = input(apply_blue("please choose a number >>> "))
                try:
                    n = int(n)
                except:
                    print("%s" % apply_red("invalid input"))
                    continue

                if n > len(real_disks) - 1:
                    print("%s" % apply_red("invalid input"))
                    continue
                else:
                    self.install_disk = real_disks[0]
                    break

def main():
    cfg = Config()
    cfg.set_disk_mount()

    print(cfg.boot)
    print(cfg.cpu_vendor)

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