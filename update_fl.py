import os
import requests
import zipfile
import shutil
import hashlib
import json
from datetime import datetime

# 配置参数
GITEE_URL = "https://gitee.com/yiwu369/6758/raw/master/神州.zip"
GITEE_OWNER = "yiwu369"
GITEE_REPO = "6758"
GITEE_BRANCH = "master"
GITEE_FILE = "神州.zip"
TEMP_DIR = "temp"
FL_DIR = "fl"
SOURCE_DIR = f"{FL_DIR}/source"
DATE_FILE = f"{SOURCE_DIR}/date.txt"
JSON_FILE = f"{FL_DIR}/2.json"
LIVE_FILE =  f"{FL_DIR}/FL.txt"

# 创建temp目录
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FL_DIR, exist_ok=True)
os.makedirs(SOURCE_DIR, exist_ok=True)

# 1. 检查Gitee文件是否有更新
def check_update():
    try:
        # 使用Gitee API获取最新提交信息
        api_url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/commits"
        params = {
            'sha': GITEE_BRANCH,
            'path': GITEE_FILE,
            'page': 1,
            'per_page': 1
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code != 200:
            print("无法访问Gitee API")
            return False, None

        # 解析API返回的JSON数据
        commits = response.json()
        if not commits:
            print("未获取到提交信息")
            return False, None

        commit_date_str = commits[0]['commit']['committer']['date']
        # 转换为datetime对象
        remote_datetime = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
        print(f"远程文件时间: {remote_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查本地date.txt文件
        if os.path.exists(DATE_FILE):
            with open(DATE_FILE, "r") as f:
                local_time_str = f.read().strip()
            local_datetime = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M:%S")
            print(f"本地文件时间: {local_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

            if remote_datetime <= local_datetime:
                print("文件未更新，无需下载")
                return False, None
        return True, remote_datetime
    except (IndexError, KeyError, ValueError) as e:
        print(f"检查更新时发生错误: {e}")
    return False, None

# 2. 下载并解压文件
def download_and_extract():
    try:
        # 下载文件
        zip_url = f"https://gitee.com/{GITEE_OWNER}/{GITEE_REPO}/raw/{GITEE_BRANCH}/{GITEE_FILE}"
        response = requests.get(zip_url)

        zip_path = os.path.join(TEMP_DIR, "神州.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        # 解压文件
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(TEMP_DIR)

        # 删除zip文件
        os.remove(zip_path)
        print("文件下载并解压完成")
        return True
    except Exception as e:
        print(f"下载或解压文件失败: {e}")
        return False

# 3. 检查文件是否存在
def check_files_exist():
    check_path1 = os.path.join(TEMP_DIR, "6758", "天上人间", "2.json")
    check_path2 = os.path.join(TEMP_DIR, "6758", "天上人间", "FL.txt")

    if not os.path.exists(check_path1) or not os.path.exists(check_path2):
        print("解压后的文件不完整")
        return False

    return True

# 计算文件hash值
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# 4. 比较文件并更新
def compare_and_update(remote_datetime):
    # 获取源文件路径
    new_json_path = os.path.join(TEMP_DIR, "6758", "天上人间", "2.json")
    new_fl_path = os.path.join(TEMP_DIR, "6758", "天上人间", "FL.txt")

    # 获取目标文件路径
    old_json_path = os.path.join(SOURCE_DIR, "2.json")
    old_fl_path = os.path.join(SOURCE_DIR, "FL.txt")

    # 检查旧文件是否存在
    old_json_exists = os.path.exists(old_json_path)
    old_fl_exists = os.path.exists(old_fl_path)

    # 如果旧文件不存在，直接更新
    if not old_json_exists or not old_fl_exists:
        shutil.copy2(new_json_path, old_json_path)
        shutil.copy2(new_fl_path, old_fl_path)
        # 更新date.txt
        with open(DATE_FILE, "w") as f:
            f.write(remote_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        return True

    # 比较文件hash
    new_json_hash = get_file_hash(new_json_path)
    old_json_hash = get_file_hash(old_json_path)
    new_fl_hash = get_file_hash(new_fl_path)
    old_fl_hash = get_file_hash(old_fl_path)

    if new_json_hash == old_json_hash and new_fl_hash == old_fl_hash:
        print("文件无变化")
        return False

    # 更新文件
    shutil.copy2(new_json_path, old_json_path)
    shutil.copy2(new_fl_path, old_fl_path)

    # 更新date.txt
    with open(DATE_FILE, "w") as f:
        f.write(remote_datetime.strftime("%Y-%m-%d %H:%M:%S"))

    return True

# 5. 复制文件
def copy_files():
    # 复制FL.txt到live.txt
    shutil.copy2(os.path.join(SOURCE_DIR, "FL.txt"), LIVE_FILE)

# 6. 复制并修改JSON文件
def copy_and_modify_json():
    # 读取源JSON文件
    source_json_path = os.path.join(SOURCE_DIR, "2.json")
    with open(source_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 修改lives[0]的url
    if "lives" in data and len(data["lives"]) > 0:
        data["lives"][0]["url"] = f"https://github.allproxy.dpdns.org/https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/{LIVE_FILE}"

    # 添加lives[1]节点
    new_live = {
        "name": "hsck",
        "type": 0,
        "url": "https://github.allproxy.dpdns.org/https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.m3u",
        "ua": "okhttp/5.0.0-alpha.14",
        "epg": "https://diyp99.112114.xyz/",
        "logo": "https://gd-hbimg.huaban.com/ca8b4e7379e601bca6eb21c33c1994e59e991b481ec6c7-RbvXmL_fw658"
    }

    if "lives" in data:
        # 如果lives数组长度大于1，替换索引1，否则添加
        if len(data["lives"]) > 1:
            data["lives"][1] = new_live
        else:
            data["lives"].append(new_live)
    else:
        data["lives"] = [new_live]

    # 写入修改后的JSON文件
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 主函数
def main():
    print("开始更新 fl 线路...")
    # 1. 检查更新
    update_needed, remote_datetime = check_update()
    if not update_needed:
        return

    # 2. 下载并解压
    download_and_extract()

    # 3. 检查文件是否存在
    if not check_files_exist():
        return

    # 4. 比较并更新文件
    if not compare_and_update(remote_datetime):
        return

    # 5. 复制文件
    copy_files()

    # 6. 复制并修改JSON文件
    copy_and_modify_json()

    print("更新完成")

if __name__ == "__main__":
    main()
