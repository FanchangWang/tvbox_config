from datetime import datetime
from datetime import timedelta, timezone
import json
from typing import Any

import requests

# github 代理
GITHUB_PROXY = "https://github.allproxy.dpdns.org"

# 解密接口
DECRYPT_URLS = [
    "http://www.饭太硬.com/jm/jiemi.php?url=",
    "https://ua.fongmi.eu.org/box.php?url=",
    "https://shixiong.alwaysdata.net/mao.php?url="
]

# 需要检查的关键字
CHECK_KEYWORDS = ["spider", "sites"]

# 定义数据源
tvbox_sources = [
    {
        "name": "饭太硬",
        "urls": ["http://www.饭太硬.com/tv"]
    },
    {
        "name": "肥猫",
        "urls": ["http://肥猫.com","http://hello.肥猫.com","https://6296.kstore.vip/fm.gif"]
    },
    {
        "name": "王二小放牛娃",
        "urls": ["http://tvbox.王二小放牛娃.top/"]
    },
    {
        "name": "OK吊炸天",
        "urls": ["http://ok321.top/tv"]
    },
    {
        "name": "南风",
        "urls": ["https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json"]
    },
    {
        "name": "巧技",
        "urls": ["http://cdn.qiaoji8.com/tvbox.json"]
    },
    # {
    #     "name": "俊佬",
    #     "urls": ["http://home.jundie.top:81/top98.json"]
    # },
    {
        "name": "香雅情",
        "urls": ["https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json"]
    },
    {
        "name": "PG本地包",
        "urls": ["https://www.252035.xyz/p/jsm.json","https://cnb.cool/fish2018/pg/-/git/raw/master/jsm.json"]
    },
    {
        "name": "真心本地包",
        "urls": ["https://www.252035.xyz/z/FongMi.json","https://cnb.cool/fish2018/zx/-/git/raw/master/FongMi.json"]
    }
]

my_sources = [
    {
        "name": "神州天上人间",
        "urls": ["https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/fl/2.json"]
    },
    {
        "name": "18live",
        "urls": ["https://raw.githubusercontent.com/xiongjian83/TvBox/main/18/18live.json"]
    },
    {
        "name": "19",
        "urls": ["https://raw.githubusercontent.com/xiongjian83/TvBox/main/18/19.json"]
    }
]

# 处理 GitHub URL，添加代理
def process_github_url(url):
    if "raw.githubusercontent.com" in url:
        return f"{GITHUB_PROXY}/{url}"
    return url

# 检查 URL 是否可用
def check_url_availability(url):
    # 首先尝试直接 GET 请求
    try:
        response = requests.get(url, timeout=10)
        content = response.text
        # 检查是否包含关键字
        if all(keyword in content for keyword in CHECK_KEYWORDS):
            return True
    except Exception as e:
        print(f"❌ 直接请求失败: {url}, 错误: {e}")

    # 如果直接请求失败或不包含关键字，尝试解密列表中的每个 URL
    for decrypt_url in DECRYPT_URLS:
        try:
            full_url = f"{decrypt_url}{url}"
            response = requests.get(full_url, timeout=10)
            content = response.text
            if all(keyword in content for keyword in CHECK_KEYWORDS):
                return True
        except Exception as e:
            print(f"❌ 解密请求失败: {full_url}, 错误: {e}")

    return False

# 生成可用的数据源列表
def generate_available_sources(sources):
    available_sources = []
    for source in sources:
        name = source["name"]
        # 遍历所有 urls，按顺序检查
        for url in source["urls"]:
            # 处理 GitHub URL
            processed_url = process_github_url(url)
            # 检查 URL 可用性
            if check_url_availability(processed_url):
                # 如果可用，添加到可用列表
                available_sources.append({
                    "name": name,
                    "url": processed_url,
                })
                print(f"✅ 可用数据源: {name} - {processed_url}")
                break
            # 如果所有 URL 都检查过且不可用，记录错误
            print(f"❌ 错误数据源: {name}")

    return available_sources

# 生成最终的 JSON 数据结构
def generate_final_json(sources):
    return {
        "urls": sources
    }

# 主函数
def main():
    print("开始生成 tvbox 线路...")
    # 检查可用的 tvbox 数据源
    available_tvbox = generate_available_sources(tvbox_sources)
    available_my = generate_available_sources(my_sources)

    # 读取历史保存的 tvbox_history.json my_history.json
    try:
        with open("tvbox_history.json", "r", encoding="utf-8") as f:
            tvbox_history = json.load(f)
    except FileNotFoundError:
        tvbox_history = []

    try:
        with open("my_history.json", "r", encoding="utf-8") as f:
            my_history = json.load(f)
    except FileNotFoundError:
        my_history = []

    # 判断两个字典列表是否相等（忽略顺序）
    def are_lists_equal(list1, list2):
        if len(list1) != len(list2):
            return False
        # 将每个字典转换为可哈希的元组形式，然后比较集合
        set1 = {tuple(sorted(d.items())) for d in list1}
        set2 = {tuple(sorted(d.items())) for d in list2}
        return set1 == set2

    # 判断 available_tvbox 与 tvbox_history 是否有差异
    tvbox_diff = not are_lists_equal(available_tvbox, tvbox_history)
    # 判断 available_my 与 my_history 是否有差异
    my_diff = not are_lists_equal(available_my, my_history)

    if not tvbox_diff and not my_diff:
        print("✅ 无差异，无需更新！脚本结束！")
        return

    # 如果有差异，更新 tvbox_history.json my_history.json
    if tvbox_diff:
        with open("tvbox_history.json", "w", encoding="utf-8") as f:
            json.dump(available_tvbox, f, ensure_ascii=False, indent=2)
    if my_diff:
        with open("my_history.json", "w", encoding="utf-8") as f:
            json.dump(available_my, f, ensure_ascii=False, indent=2)

    if available_tvbox:
        # 转换为东八区时间
        tz = timezone(timedelta(hours=8))
        available_tvbox[0]["name"] += f" [{datetime.now(tz).strftime('%Y-%m-%d %H:%M')}]"
    # 生成可用的 my 数据源（合并 tvbox 和 my 数据源）
    available_my = available_tvbox + available_my

    # 生成 tvbox.json
    if tvbox_diff:
        print(f"✅ tvbox.json 包含 {len(available_tvbox)} 个可用数据源")
        tvbox_json = generate_final_json(available_tvbox)
        with open("tvbox.json", "w", encoding="utf-8") as f:
            json.dump(tvbox_json, f, ensure_ascii=False, indent=2)


    # 生成 my.json
    if my_diff:
        print(f"✅ my.json 包含 {len(available_my)} 个可用数据源")
        my_json = generate_final_json(available_my)
        with open("my.json", "w", encoding="utf-8") as f:
            json.dump(my_json, f, ensure_ascii=False, indent=2)

    print(f"✅ 生成完成！脚本结束！")

if __name__ == "__main__":
    main()
