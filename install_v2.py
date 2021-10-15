#!/usr/bin/python

# =============================================
# The install script for Archlinux installation
# =============================================

import os
import sys

support_shells = ("bash", "zsh", "fish")
support_desktops = ("gnome", "plasma")
support_language = ("en", "zh")

base_packages = "base base-devel linux linux-firmware vim openssh zsh fish git wget curl grub dhcpcd net-tools"


def print_red(a, end="\n"):
    print(f"\033[31m{a}\033[0m", end=end)


def print_green(a, end="\n"):
    print(f"\033[32m{a}\033[0m", end=end)


def print_yellow(a, end="\n"):
    print(f"\033[33m{a}\033[0m", end=end)


def print_blue(a, end="\n"):
    print(f"\033[34m{a}\033[0m", end=end)


def print_purple(a, end="\n"):
    print(f"\033[35m{a}\033[0m", end=end)


def print_cyan(a, end="\n"):
    print(f"\033[36m{a}\033[0m", end=end)


def just_run(prompt: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print_blue(f"Now in {prompt}...")
            func(*args, **kwargs)
            print_yellow(f"{prompt} successfully finished")
        return wrapper
    return decorator


# Config:
#   The configuration for installation, include hostname, disk partition ...
class Config:
    def __init__(self):
        # boot_way: UEFI or BIOS
        self.boot_way = None
        # cpu_vendor: intel, amd
        self.cpu_vendor = None
        # disk_mount
        # [
        #   {
        #     "disk": "/dev/sda",
        #     "mount_point": "/"
        #   },
        #   {
        #     "disk": "/dev/sdb",
        #     "mount_point": "/home"
        #   },
        # ]
        self.disk_mount = []
        # desktop: None, Gnome, Plasma
        self.desktop = None
        # root_passwd: passwd for root user
        self.root_passwd = None
        # common_users:
        #  [
        #    {
        #      "username": "kainhuck",
        #      "password": "123456",
        #      "shell": "base"
        #    }
        #  ]
        self.common_users = []
        # language: en, zh
        self.language = None
        # swap_size: size of swap
        self.swap_size = None
        # hostname
        self.hostname = None

        self._set_boot_way()
        self._set_cpu_vendor()

    def _set_boot_way(self):
        pass

    def _set_cpu_vendor(self):
        pass

    @just_run("set_disk_mount")
    def set_disk_mount(self):
        pass

    @just_run("set_desktop")
    def set_desktop(self):
        print_purple("Choose a desktop for your Archlinux")
        print_green("0. no desktop")
        for i in range(len(support_desktops)):
            print_green(f"{i+1}. {support_desktops[i]}")
        choose = int(input(">>> "))
        if choose < 0 or choose > len(support_desktops):
            print_red("Invalid input please choose again")
            choose = int(input(">>> "))

        if choose == 0:
            self.desktop = None
        else:
            self.desktop = support_desktops[choose-1]

    @just_run("set_root_password")
    def set_root_password(self):
        print_purple("Please set root password")
        passwd = input(">>> ")
        if len(passwd) == 0:
            print_red("Password is empty, please input again")
            passwd = input(">>> ")
        self.root_passwd = passwd

    @just_run("set_common_users")
    def set_common_users(self):
        if self.desktop is None:
            print_purple("Do you need a common user? [Y/n]")
            ys = input(">>> ").lower()
            if ys == "n":
                return

        i = 1
        username_list = []
        while True:
            print_purple(f"Please input the {i} user's name")
            username = input(">>> ")
            while username == "root" or username in username_list:
                if username == "root":
                    print_red("Username can't be `root`, please input again")
                else:
                    print_red(f"Username `{username}` was used, please input again")
                username = input(">>> ")
            print_purple(f"Please input the {i} user's password")
            password = input(">>> ")
            while len(password) == 0:
                print_red("Password is empty, please input again")
                password = input(">>> ")
            print_purple(f"Please input the {i} user's shell [bash/zsh/fish]")
            shell = input(">>> ")
            while len(shell) == 0 or shell not in support_shells:
                if len(shell) == 0:
                    print_red("Shell is empty, please input again")
                else:
                    print_red(f"Shell `{shell}` is not supported, please input again")
                shell = input(">>> ")

            self.common_users.append({
                "username": username,
                "password": password,
                "shell": shell
            })
            print_purple("Add another user? [Y/n]")
            ys = input(">>> ").lower()
            if ys == "n":
                return
            i += 1

    @just_run("set_language")
    def set_language(self):
        print_purple("Please set language (en/zh)")
        language = input(">>> ").lower()
        if len(language) == 0 or language not in support_language:
            if len(language) == 0:
                print_red("Language is empty, please input again")
            else:
                print_red(f"Language `{language}` is not supported, please input again")
            language = input(">>> ")
        self.language = language

    @just_run("set_swap_size")
    def set_swap_size(self):
        print_purple("Please set swap size (G)")
        swap = int(input(">>> "))
        if swap <= 0:
            print_red("swap must >= 1, please input again")
            swap = int(input(">>> "))
        self.swap_size = swap

    @just_run("set_hostname")
    def set_hostname(self):
        print_purple("Please set hostname")
        hostname = input(">>> ")
        if len(hostname) == 0:
            print_red("Hostname is empty, please input again")
            hostname = input(">>> ")
        self.hostname = hostname

    def print_info(self):
        print_blue("===========================")
        for m in self.disk_mount:
            print_blue("= ", end="")
            print_green("disk mount: ", end="")
            print_cyan(f"{m.disk} => {m.mount_point}")
        print_blue("= ", end="")
        print_green("desktop: ", end="")
        print_cyan(f"{self.desktop}")
        print_blue("= ", end="")
        print_green("root passwd: ", end="")
        print_cyan(f"{self.root_passwd}")
        for u in self.common_users:
            print_blue("= ", end="")
            print_green("common user: ", end="")
            print_cyan(f"{u['username']} | {u['password']} | {u['shell']}")
        print_blue("= ", end="")
        print_green("language: ", end="")
        print_cyan(f"{self.language}")
        print_blue("= ", end="")
        print_green("swap size: ", end="")
        print_cyan(f"{self.swap_size}G")
        print_blue("= ", end="")
        print_green("hostname: ", end="")
        print_cyan(f"{self.hostname}")
        print_blue("===========================")


def run_cmd(cmd: str):
    print_cyan("[RUN] ", end="")
    print_yellow(cmd)
    code = os.system(cmd)
    if code != 0:
        print_red("exit")
        sys.exit(code)


def main():
    cfg = Config()
    cfg.set_disk_mount()
    cfg.set_desktop()
    cfg.set_root_password()
    cfg.set_common_users()
    cfg.set_language()
    cfg.set_swap_size()
    cfg.set_hostname()
    print_purple("All config is finish, please check the info below")
    cfg.print_info()
    print_yellow("Install process will clear all data in disk, are you sure going on? [N/y]")
    ys = input(">>> ").lower()
    if ys != "y":
        print_yellow("Quit")
        return

    # packages
    global base_packages
    if cfg.boot_way == "UEFI":
        base_packages += " efibootmgr"

    if cfg.desktop == "gnome":
        base_packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei gdm gnome gnome-extra"
    elif cfg.desktop == "plasma":
        base_packages += " networkmanager xorg alsa-utils pulseaudio pulseaudio-alsa xf86-input-synaptics ttf-dejavu wqy-microhei plasma kde-applications libdbusmenu-glib appmenu-gtk-module packagekit-qt5"


if __name__ == '__main__':
    main()