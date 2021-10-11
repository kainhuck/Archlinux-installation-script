#!/usr/bin/python

import os
import sys

# 这是archlinux安装后的脚本

def just_run(prompt: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\033[34m正在{prompt}...\033[0m")
            func(*args, **kwargs)
            print("\033[32mOK\033[0m")

        return wrapper

    return decorator


def run_cmd(cmd: str):
    code = os.system(cmd)
    if code != 0:
        sys.exit(code)

# 1. 必要软件安装
class BaseConfig:
    @just_run("配置archlinuxcn源")
    def set_archlinuxcn(self):
        run_cmd('sudo echo -e "\\n[archlinuxcn]\\nServer = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/\$arch" >> /etc/pacman.conf')
        run_cmd("sudo pacman -Syu archlinuxcn-keyring")
    
    @just_run("设置AUR")
    def set_aur(self):
        run_cmd("sudo pacman -S yay")
        run_cmd('yay --aururl "https://aur.tuna.tsinghua.edu.cn" --save')

    @just_run("设置ohmyzsh")
    def set_oh_my_zsh(self):
        run_cmd('sh -c "$(wget https://gitee.com/shenghaiyang/ohmyzsh/raw/master/tools/install.sh -O -)"')
        run_cmd('git clone git://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/plugins/zsh-autosuggestions')
        run_cmd('git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/plugins/zsh-syntax-highlighting')
        run_cmd("sed -in-place -e 's/plugins=(git)/plugins=(docker git sudo zsh-syntax-highlighting zsh-autosuggestions)/g' ~/.zshrc")
        run_cmd("source ~/.zshrc")
    
    @just_run("安装输入法")
    def set_fcitx(self):
        run_cmd("sudo pacman -S fcitx-im fcitx-table-other kcm-fcitx fcitx-skin-material") # kcm 针对kde桌面
        run_cmd("touch ~/.xprofile")
        run_cmd("echo -e 'export XIM=fcitx\\nexport XIM_PROGRAM=fcitx\\nexport GTK_IM_MODULE=fcitx\\nexport QT_IM_MODULE=fcitx\\nexport XMODIFIERS\"@im=fcitx\"' >> ~/.xprofile")
        run_cmd("source ~/.xprofile")
# 2. 各类开发环境
##  golang
##  docker

# 3. 其他软件
##  virtualbox

# 4. 美化
##  grub主题
##  图标主题
##  全局主题
##  kde插件

def main():
    base = BaseConfig()
    base.set_archlinuxcn()
    base.set_aur()
    base.set_oh_my_zsh()
    base.set_fcitx()

if __name__ == "__main__":
    main()