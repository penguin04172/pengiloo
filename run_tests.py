#!/usr/bin/env python3
"""
快速測試腳本 - Pengiloo pytest 測試套件
"""
import subprocess
import sys

def run_tests(args=''):
    """執行 pytest 測試"""
    cmd = f"uv run pytest {args}"
    print(f"執行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def main():
    print("=" * 70)
    print("Pengiloo 測試套件")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1:
        # 帶參數執行
        args = ' '.join(sys.argv[1:])
        return run_tests(args)
    
    # 顯示選單
    print("選擇測試類型:")
    print("  1. 快速測試 (只執行單元測試，無覆蓋率報告)")
    print("  2. 完整測試 (所有測試 + 覆蓋率報告)")
    print("  3. 單元測試 (只執行 @unit 標記的測試)")
    print("  4. 集成測試 (只執行 @integration 標記的測試)")
    print("  5. 特定模組 (輸入測試文件名)")
    print("  6. 詳細輸出 (verbose 模式)")
    print()
    
    choice = input("請選擇 (1-6，或 q 退出): ").strip()
    
    if choice == 'q':
        return 0
    elif choice == '1':
        return run_tests("tests/ -m unit -q --tb=line --no-cov")
    elif choice == '2':
        return run_tests("tests/ -v --cov=. --cov-report=html --cov-report=term")
    elif choice == '3':
        return run_tests("tests/ -m unit -v")
    elif choice == '4':
        return run_tests("tests/ -m integration -v")
    elif choice == '5':
        module = input("輸入測試文件名 (例如: test_ipc.py): ").strip()
        return run_tests(f"tests/{module} -v")
    elif choice == '6':
        return run_tests("tests/ -vv --tb=short")
    else:
        print("無效選擇")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n測試已取消")
        sys.exit(130)
