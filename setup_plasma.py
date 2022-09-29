#!/usr/bin/python

import os
import sys
import subprocess


# 这是archlinux安装后的脚本

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


def run_cmd(cmd: str, debug: bool = True, exit_: bool = True, stdout: bool = False) -> str:
    if debug:
        print("{} {}".format(apply_cyan("[RUN]"), apply_yellow(cmd)))

    if stdout:
        code = os.system(cmd)
        output = ""
    else:
        code, output = subprocess.getstatusoutput(cmd)

    try:
        assert code == 0
    except AssertionError:
        if exit_:
            print("{}".format(apply_red(f"RUN ERROR: {cmd}")))
            sys.exit(code)
        else:
            return ""

    return output


def just_run(prompt: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print("{}".format(apply_yellow(f"正在{prompt}...")))
            func(*args, **kwargs)
            print("{}".format(apply_green("OK")))

        return wrapper

    return decorator


# 1. 必要软件安装
class BaseConfig:
    @just_run("配置archlinuxcn源")
    def set_archlinuxcn(self):
        run_cmd("sudo sed -in-place -e 's/#Color/Color/g' /etc/pacman.conf")
        run_cmd("sudo sh -c 'cat >> /etc/pacman.conf <<EOF\n[archlinuxcn]\nServer = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/\$arch\nEOF'")
        run_cmd("sudo pacman -Syu")
        run_cmd("sudo pacman -S --noconfirm archlinuxcn-keyring")

    @just_run("设置AUR")
    def set_aur(self):
        run_cmd("sudo pacman -S yay")
        run_cmd('yay --aururl "https://aur.tuna.tsinghua.edu.cn" --save')

    @just_run("安装输入法")
    def set_fcitx(self):
        run_cmd("sudo pacman -S --noconfirm fcitx fcitx-table-other kcm-fcitx fcitx-skin-material")  # kcm 针对kde桌面
        run_cmd("touch ~/.xprofile")
        run_cmd("echo -e 'export XIM=fcitx\\nexport XIM_PROGRAM=fcitx\\nexport GTK_IM_MODULE=fcitx\\nexport QT_IM_MODULE=fcitx\\nexport XMODIFIERS=\"@im=fcitx\"\\n' >> ~/.xprofile")
        run_cmd("source ~/.xprofile")

    @just_run("安装nerd-font字体")
    def set_font(self):
        run_cmd("sudo pacman -S --noconfirm nerd-fonts-complete")

    @just_run("设置ohmyzsh")
    def set_oh_my_zsh(self):
        run_cmd('sh -c "$(wget https://gitee.com/shenghaiyang/ohmyzsh/raw/master/tools/install.sh -O -)"')
        run_cmd('git clone git://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/plugins/zsh-autosuggestions')
        run_cmd('git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/plugins/zsh-syntax-highlighting')
        run_cmd("sed -in-place -e 's/plugins=(git)/plugins=(docker git sudo zsh-syntax-highlighting zsh-autosuggestions)/g' ~/.zshrc")
        run_cmd("zsh -c 'source ~/.zshrc'")

    @just_run("修改中文目录为英文")
    def set_user_dir(self):
        run_cmd("mv ~/公共 ~/Public")
        run_cmd("sed -in-place -e 's/公共/Public/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/模板 ~/Template")
        run_cmd("sed -in-place -e 's/模板/Template/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/视频 ~/Video")
        run_cmd("sed -in-place -e 's/视频/Video/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/图片 ~/Picture")
        run_cmd("sed -in-place -e 's/图片/Picture/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/文档 ~/Documents")
        run_cmd("sed -in-place -e 's/文档/Documents/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/下载 ~/Download")
        run_cmd("sed -in-place -e 's/下载/Download/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/音乐 ~/Music")
        run_cmd("sed -in-place -e 's/音乐/Music/g' ~/.config/user-dirs.dirs")

        run_cmd("mv ~/桌面 ~/Desktop")
        run_cmd("sed -in-place -e 's/桌面/Desktop/g' ~/.config/user-dirs.dirs")


# 2. 各类开发环境
class Develop:
    @just_run("安装golang")
    def set_golang(self):
        run_cmd('sudo pacman -S --noconfirm go')
        run_cmd('mkdir ~/.go')
        run_cmd('mkdir ~/.go/bin')
        run_cmd('mkdir ~/.go/src')
        run_cmd('mkdir ~/.go/pkg')
        run_cmd('echo -e "export GOROOT=/usr/lib/go\\nexport GOPATH=~/Documents/go\\nexport GOBIN=~/Documents/go/bin\\nexport PATH=$PATH:$GOROOT/bin:$GOBIN\\n" >> ~/.xprofile')
        run_cmd('source ~/.xprofile')
        run_cmd('go env -w GOPROXY=https://goproxy.io,direct')
        run_cmd('sudo pacman -S --noconfirm goland-jre goland')

    @just_run("安装docker")
    def set_docker(self):
        run_cmd('sudo pacman -S --noconfirm docker')
        run_cmd('sudo gpasswd -a ${USER} docker')
        run_cmd("sudo mkdir /etc/docker")
        run_cmd("sudo touch /etc/docker/daemon.json")
        run_cmd('''sudo tee /etc/docker/daemon.json <<-'EOF'\n{\n	"registry-mirrors": ["http://hub-mirror.c.163.com"]\n}\nEOF''')
        run_cmd("sudo systemctl enable docker")


# 3. 常用软件
class Software:
    @just_run("安装virtualbox")
    def set_virtualbox(self):
        run_cmd('sudo pacman -S --noconfirm virtualbox virtualbox-ext-oracle virtualbox-guest-iso net-tools')

    @just_run("安装telegram")
    def set_telegram(self):
        run_cmd('sudo pacman -S --noconfirm telegram-desktop')

    @just_run("安装google-chrome")
    def set_chrome(self):
        run_cmd('yay -S --noconfirm google-chrome')

    @just_run("安装typora")
    def set_typora(self):
        run_cmd("sudo pacman -S --noconfirm typora")

    @just_run("安装vscode")
    def set_vscode(self):
        run_cmd("yay -S --noconfirm visual-studio-code-bin")

    @just_run("安装qq音乐")
    def set_qqmusic(self):
        run_cmd("yay -S --noconfirm qqmusic-bin")


# 4. 美化
class Beauty:
    @just_run("安装papirus图标主题")
    def set_icon_theme(self):
        run_cmd("sudo pacman -S --noconfirm papirus-icon-theme")

    @just_run("安装layan全局主题")
    def set_layan_theme(self):
        run_cmd("yay -S --noconfirm layan-kde-git")

    @just_run("安装tela-2k grub主题")
    def set_grub_theme(self):
        run_cmd("yay -S --noconfirm grub-theme-tela-color-2k-git")


def main():
    base = BaseConfig()
    base.set_archlinuxcn()
    base.set_aur()
    base.set_fcitx()
    base.set_font()
    base.set_user_dir()
    #
    # dev = Develop()
    # dev.set_golang()
    # dev.set_docker()
    #
    # soft = Software()
    # soft.set_chrome()
    # soft.set_typora()
    # # soft.set_virtualbox()
    # soft.set_telegram()
    # soft.set_vscode()
    # soft.set_qqmusic()
    #
    # b = Beauty()
    # b.set_grub_theme()
    # b.set_icon_theme()
    # b.set_layan_theme()

    # 最后再来安装oh-my-zsh
    base.set_oh_my_zsh()


if __name__ == "__main__":
    main()
