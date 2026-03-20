# 编译成Windows运行文件
import os
import subprocess


class WindowsCompiler:
    """
    Windows可执行文件编译器
    使用PyInstaller将Python脚本编译成Windows可执行文件
    """
    def __init__(self):
        # 主脚本在项目根目录
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.main_script = os.path.join(project_root, 'main.py')
        # 输出目录和构建目录改为项目根目录下
        self.output_dir = os.path.join(project_root, 'dist')
        self.build_dir = os.path.join(project_root, 'build')
        
    def compile(self, onefile=True, console=False, icon=None):
        """
        编译Python脚本为Windows可执行文件
        :param onefile: 是否生成单个可执行文件
        :param console: 是否显示控制台窗口
        :param icon: 可执行文件图标路径
        :return: bool 是否编译成功
        """
        try:
            # 检查PyInstaller是否安装
            if not self._check_pyinstaller():
                print("PyInstaller未安装，正在安装...")
                self._install_pyinstaller()
            
            # 准备编译命令
            cmd = ['pyinstaller']
            
            # 添加编译选项
            if onefile:
                cmd.append('--onefile')
            if not console:
                cmd.append('--windowed')
            if icon:
                cmd.append(f'--icon={icon}')
            
            # 添加数据文件
            project_root = os.path.dirname(os.path.dirname(__file__))
            templates_path = os.path.join(project_root, 'templates')
            cmd.append(f'--add-data={templates_path};./templates')
            
            # DrissionPage 不需要额外的驱动文件
            
            # 添加输出目录
            cmd.append(f'--distpath={self.output_dir}')
            cmd.append(f'--workpath={self.build_dir}')
            
            # 添加主脚本
            cmd.append(self.main_script)
            
            print(f"开始编译...")
            print(f"编译命令: {' '.join(cmd)}")
            
            # 执行编译命令
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print(f"编译成功!")
            print(f"输出目录: {self.output_dir}")
            
            # 复制templates目录到输出目录
            try:
                import shutil
                # 使用项目根目录的templates
                project_root = os.path.dirname(os.path.dirname(__file__))
                templates_src = os.path.join(project_root, 'templates')
                templates_dest = os.path.join(self.output_dir, 'templates')
                
                if os.path.exists(templates_src):
                    if os.path.exists(templates_dest):
                        shutil.rmtree(templates_dest)
                    shutil.copytree(templates_src, templates_dest)
                    print(f"已复制templates目录到输出目录: {templates_dest}")
            except Exception as e:
                print(f"复制templates目录失败: {e}")
            
            # 清理临时文件
            self._cleanup()
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"编译失败: {e}")
            print(f"错误输出: {e.stderr}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return False
        except Exception as e:
            print(f"编译过程中发生错误: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return False
    
    def _check_pyinstaller(self):
        """
        检查PyInstaller是否安装
        :return: bool 是否安装
        """
        try:
            import PyInstaller
            return True
        except ImportError:
            return False
    
    def _install_pyinstaller(self):
        """
        安装PyInstaller
        :return: bool 是否安装成功
        """
        try:
            import subprocess
            # 使用pip安装PyInstaller
            result = subprocess.run(['pip', 'install', 'pyinstaller'], 
                                  check=True, capture_output=True, text=True)
            print("PyInstaller安装成功！")
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装PyInstaller失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"安装PyInstaller过程中发生错误: {e}")
            return False
    
    def _cleanup(self):
        """
        清理临时文件
        """
        try:
            # 删除.spec文件
            spec_file = os.path.join(os.path.dirname(__file__), 'main.spec')
            if os.path.exists(spec_file):
                os.remove(spec_file)
                print(f"已删除临时文件: {spec_file}")
            
            # 清理根目录下的tmp临时文件
            project_root = os.path.dirname(os.path.dirname(__file__))
            for filename in os.listdir(project_root):
                if filename.startswith('tmp') and not os.path.isdir(os.path.join(project_root, filename)):
                    try:
                        file_path = os.path.join(project_root, filename)
                        os.remove(file_path)
                        print(f"已删除临时文件: {filename}")
                    except Exception as e:
                        print(f"删除临时文件 {filename} 失败: {e}")
            
            # build目录保留，包含编译过程中的临时文件
        except Exception as e:
            print(f"清理临时文件失败: {e}")

# 测试函数
if __name__ == "__main__":
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='黄金价格监控系统 - Windows编译工具')
    parser.add_argument('-y', '--yes', action='store_true', help='自动确认编译')
    parser.add_argument('--onefile', action='store_true', default=True, help='生成单个可执行文件')
    parser.add_argument('--console', action='store_true', default=True, help='显示控制台窗口')
    args = parser.parse_args()
    
    compiler = WindowsCompiler()
    
    print("黄金价格监控系统 - Windows编译工具")
    print("=" * 50)
    print("这个工具将使用PyInstaller将Python脚本编译成Windows可执行文件")
    print("编译后的文件将保存在dist目录中")
    print("=" * 50)
    
    # 检查是否自动确认编译
    if args.yes:
        choice = 'y'
    else:
        # 询问用户是否要编译
        while True:
            choice = input("是否开始编译？(y/n): ").lower()
            if choice in ['y', 'n']:
                break
            print("请输入有效的选项 (y/n)")
    
    if choice == 'y':
        success = compiler.compile(onefile=args.onefile, console=args.console)
        if success:
            print("\n编译成功！")
            print("您可以在dist目录中找到编译后的可执行文件")
            print("运行该文件即可启动黄金价格监控系统")
            print("\n提示：")
            print("1. 编译后的文件可以直接运行，无需安装Python环境")
            print("2. 运行时会显示控制台窗口，可以实时查看抓取内容")
            print("3. 程序会在当前目录生成gold_price.html文件，可用于Web预览")
            print("4. 程序会在当前目录生成gold_monitor.log文件，记录运行日志")
        else:
            print("\n编译失败，请检查错误信息")
    else:
        print("\n已取消编译")