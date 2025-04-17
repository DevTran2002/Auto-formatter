#!/usr/bin/env python
"""
Script để cài đặt thư viện spaCy và mô hình ngôn ngữ cần thiết cho ứng dụng
"""
import subprocess
import sys
import os

def install_packages():
    print("Đang cài đặt thư viện spaCy...")
    
    try:
        # Cài đặt spaCy và các dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "spacy"], check=True)
        print("Đã cài đặt thành công thư viện spaCy")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi cài đặt spaCy: {str(e)}")
        return False

def install_spacy_model():
    print("Đang cài đặt mô hình ngôn ngữ spaCy...")
    
    # Cài đặt mô hình tiếng Anh
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print("Đã cài đặt thành công mô hình en_core_web_sm")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi cài đặt mô hình en_core_web_sm: {str(e)}")
        return False
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        return False

if __name__ == "__main__":
    # Cài đặt các gói và thư viện cần thiết
    all_requirements = False
    try:
        # Kiểm tra xem requirements.txt có tồn tại không
        if os.path.exists('requirements.txt'):
            print("Cài đặt các thư viện từ requirements.txt...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            all_requirements = True
        else:
            all_requirements = install_packages()
    except Exception as e:
        print(f"Lỗi khi cài đặt các gói thư viện: {str(e)}")
        all_requirements = False
    
    # Nếu cài đặt thư viện thành công, tiếp tục cài đặt mô hình
    if all_requirements:
        success = install_spacy_model()
        if success:
            print("Cài đặt hoàn tất. Ứng dụng sẵn sàng sử dụng.")
        else:
            print("Có lỗi trong quá trình cài đặt mô hình. Vui lòng kiểm tra lại.")
            sys.exit(1)
    else:
        print("Không thể tiếp tục cài đặt do lỗi thư viện.")
        sys.exit(1) 