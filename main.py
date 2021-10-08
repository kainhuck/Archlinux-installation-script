#!/user/bin/python
# This is ArchLinux install script

import os
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
    run_cmd("ping", "www.baidu.com")


def run_cmd(*cmd):
    cmd_str = " ".join(cmd)
    print(f"RUN >>> {cmd_str}")
    code, output = subprocess.getstatusoutput(cmd_str)
    try:
        assert code == SUCCESS
        print(f"OUT >>> {output}")
    except AssertionError as e:
        print(f"ERROR >>> {output}")
        sys.exit(code)


def main():
    check_network()

    if not check_platform():
        print("This script only for archlinux installation")
        sys.exit(0)

    # 确定引导方式
    check_boot()

    # 更新系统时间
    run_cmd("timedatectl", "set-ntp", "true")


if __name__ == '__main__':
    main()
