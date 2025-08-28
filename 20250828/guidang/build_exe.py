# -*- coding: utf-8 -*-
"""
PyInstaller打包配置
将桌面文件归档工具打包为exe可执行文件
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """构建exe文件"""
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 主程序文件
    main_script = current_dir / "main.py"
    
    # 图标文件
    icon_file = current_dir / "app_icon.ico"
    
    # 输出目录
    dist_dir = current_dir / "dist"
    build_dir = current_dir / "build"
    
    # modules目录
    modules_dir = current_dir / "modules"
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包为单个exe文件
        "--windowed",                   # 不显示控制台窗口
        "--name=桌面文件归档工具",        # 可执行文件名称
        f"--icon={icon_file}",          # 图标文件
        f"--add-data={modules_dir}{os.pathsep}modules",   # 包含modules目录
        "--hidden-import=pystray",      # 隐式导入
        "--hidden-import=PIL",          # 隐式导入
        "--hidden-import=schedule",     # 隐式导入
        "--hidden-import=psutil",       # 隐式导入
        "--collect-all=pystray",        # 收集所有pystray相关文件
        "--collect-all=PIL",            # 收集所有PIL相关文件
        "--noconsole",                  # 不显示控制台
        "--clean",                      # 清理临时文件
        str(main_script)
    ]
    
    print("开始打包exe文件...")
    print(f"主程序: {main_script}")
    print(f"图标文件: {icon_file}")
    print(f"输出目录: {dist_dir}")
    print()
    
    try:
        # 检查必要文件是否存在
        if not main_script.exists():
            print(f"错误: 主程序文件不存在: {main_script}")
            return False
            
        if not icon_file.exists():
            print(f"警告: 图标文件不存在: {icon_file}，将使用默认图标")
            # 移除图标参数
            cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        
        # 检查modules目录是否存在
        if not modules_dir.exists():
            print(f"错误: modules目录不存在: {modules_dir}")
            return False
            
        # 执行PyInstaller命令
        print("执行PyInstaller命令:")
        print(" ".join(cmd))
        print()
        
        result = subprocess.run(cmd, cwd=current_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 打包成功！")
            
            # 查找生成的exe文件
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
                print(f"📁 输出文件: {exe_file}")
                print(f"📊 文件大小: {file_size:.1f} MB")
                
                # 创建快捷方式信息
                print("\n📋 使用说明:")
                print(f"1. exe文件位置: {exe_file}")
                print("2. 双击运行即可启动桌面文件归档工具")
                print("3. 首次运行会在桌面创建配置文件")
                print("4. 可以将exe文件复制到任意位置使用")
                
            else:
                print("❌ 未找到生成的exe文件")
                return False
                
        else:
            print("❌ 打包失败！")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ PyInstaller未安装或不在PATH中")
        print("请运行: pip install pyinstaller")
        return False
        
    except Exception as e:
        print(f"❌ 打包过程中发生错误: {str(e)}")
        return False
        
    return True

def clean_build_files():
    """清理构建文件"""
    current_dir = Path(__file__).parent
    
    # 要清理的目录和文件
    clean_targets = [
        current_dir / "build",
        current_dir / "__pycache__",
        current_dir / "modules" / "__pycache__",
    ]
    
    # 要清理的文件模式
    file_patterns = [
        "*.spec",
        "*.pyc",
        "*.pyo"
    ]
    
    print("清理构建文件...")
    
    # 清理目录
    for target in clean_targets:
        if target.exists() and target.is_dir():
            try:
                import shutil
                shutil.rmtree(target)
                print(f"已删除目录: {target}")
            except Exception as e:
                print(f"删除目录失败 {target}: {str(e)}")
    
    # 清理文件
    for pattern in file_patterns:
        for file_path in current_dir.rglob(pattern):
            try:
                file_path.unlink()
                print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件失败 {file_path}: {str(e)}")
    
    print("清理完成")

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    
    # 检查包的映射关系 - 有些包的导入名和安装名不同
    required_packages = [
        ("pyinstaller", "PyInstaller"),
        ("pystray", "pystray"),
        ("Pillow", "PIL"),
        ("schedule", "schedule"),
        ("psutil", "psutil")
    ]
    
    missing_packages = []
    
    for install_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {install_name} ({import_name})")
        except ImportError:
            print(f"❌ {install_name} (未安装)")
            missing_packages.append(install_name)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n所有依赖包已安装")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("桌面文件归档工具 - exe打包工具")
    print("=" * 50)
    print()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    print()
    
    # 询问是否清理旧文件
    try:
        clean = input("是否清理旧的构建文件? (y/N): ").strip().lower()
        if clean in ['y', 'yes']:
            clean_build_files()
            print()
    except KeyboardInterrupt:
        print("\n操作已取消")
        return
    
    # 开始打包
    success = build_exe()
    
    if success:
        print("\n🎉 打包完成！")
        print("\n💡 提示:")
        print("- exe文件可以独立运行，无需Python环境")
        print("- 首次运行可能需要一些时间来初始化")
        print("- 建议在不同的Windows系统上测试兼容性")
    else:
        print("\n💥 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()