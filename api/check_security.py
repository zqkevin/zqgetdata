# -*- coding: utf-8 -*-
"""
安全依赖检查脚本
用于检查项目依赖是否存在已知安全漏洞
"""
import subprocess
import sys


def check_pip_audit():
    """使用 pip-audit 检查安全漏洞"""
    try:
        print("=" * 60)
        print("  开始检查依赖包安全漏洞...")
        print("=" * 60)
        print()
        
        # 尝试运行 pip-audit
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ 未发现已知安全漏洞")
            return True
        else:
            print("\n⚠️  发现安全漏洞，请查看上方详细信息")
            print("\n建议操作：")
            print("1. 查看漏洞详情")
            print("2. 更新受影响的包: pip install <package>=<safe_version>")
            print("3. 更新 requirements.txt")
            return False
            
    except FileNotFoundError:
        print("⚠️  pip-audit 未安装")
        print("\n安装方法：")
        print("  pip install pip-audit")
        print("\n或者使用替代方案：")
        print("  pip install safety")
        print("  safety check -r requirements.txt")
        return False
    except subprocess.TimeoutExpired:
        print("❌ 检查超时，请稍后重试")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def check_outdated_packages():
    """检查过时的包"""
    print("\n" + "=" * 60)
    print("  检查过时的依赖包...")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if "Package" not in result.stdout or result.stdout.strip() == "":
            print("✅ 所有包都是最新版本")
        else:
            print("\n💡 提示：可以使用以下命令更新所有包：")
            print("  pip install --upgrade -r requirements.txt")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")


def main():
    """主函数"""
    print("\n🔒 Soccer Data API - 安全检查工具\n")
    
    # 检查安全漏洞
    audit_result = check_pip_audit()
    
    # 检查过时包
    check_outdated_packages()
    
    print("\n" + "=" * 60)
    if audit_result:
        print("  ✅ 安全检查完成，未发现严重问题")
    else:
        print("  ⚠️  安全检查完成，发现需要处理的问题")
    print("=" * 60)
    print()
    
    return 0 if audit_result else 1


if __name__ == "__main__":
    sys.exit(main())
