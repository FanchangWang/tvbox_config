# -*- coding: utf-8 -*-
import requests
import re
import json
import traceback
import sys

sys.path.append('../../')
try:
    from base.spider import Spider
except ImportError:
    # 定义一个基础接口类，用于本地测试
    class Spider:
        def init(self, extend=""):
            pass

class Spider(Spider):
    def __init__(self):
        self.siteUrl = "https://www.kuaikaw.cn"
        self.nextData = None  # 缓存NEXT_DATA数据
        self.cateManual = {
            "🦄 甜宠": "462",
            "🦄 古装仙侠": "1102",
            "🦄 现代言情": "1145",
            "🦄 青春": "1170",
            "🦄 豪门恩怨": "585",
            "🦄 逆袭": "417-464",
            "🦄 重生": "439-465",
            "🦄 系统": "1159",
            "🦄 总裁": "1147",
            "🦄 职场商战": "943"
        }
        
    def getName(self):
        # 返回爬虫名称
        return "河马短剧"
    
    def init(self, extend=""):
        return
    
    def fetch(self, url, headers=None):
        """统一的网络请求接口"""
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                "Referer": self.siteUrl,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            }
        
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"请求异常: {url}, 错误: {str(e)}")
            return None
    
    def isVideoFormat(self, url):
        # 检查是否为视频格式
        video_formats = ['.mp4', '.mkv', '.avi', '.wmv', '.m3u8', '.flv', '.rmvb']
        for format in video_formats:
            if format in url.lower():
                return True
        return False
    
    def manualVideoCheck(self):
        # 不需要手动检查
        return False
    
    def homeContent(self, filter):
        """获取首页分类及筛选"""
        result = {}
        # 分类列表，使用已初始化的cateManual
        classes = []
        for k in self.cateManual:
            classes.append({
                'type_name': k,
                'type_id': self.cateManual[k]
            })
        result['class'] = classes
        # 获取首页推荐视频
        try:
            result['list'] = self.homeVideoContent()['list']
        except:
            result['list'] = []
  
        return result
    
    def homeVideoContent(self):
        """获取首页推荐视频内容"""
        videos = []
        try:
            response = self.fetch(self.siteUrl)
            html_content = response.text
            # 提取NEXT_DATA JSON数据
            next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            next_data_match = re.search(next_data_pattern, html_content, re.DOTALL)
            if next_data_match:
                next_data_json = json.loads(next_data_match.group(1))
                page_props = next_data_json.get("props", {}).get("pageProps", {})
                # 获取轮播图数据 - 这些通常是推荐内容
                if "bannerList" in page_props and isinstance(page_props["bannerList"], list):
                    banner_list = page_props["bannerList"]
                    for banner in banner_list:
                        book_id = banner.get("bookId", "")
                        book_name = banner.get("bookName", "")
                        cover_url = banner.get("coverWap", banner.get("wapUrl", ""))
                        # 获取状态和章节数
                        status = banner.get("statusDesc", "")
                        total_chapters = banner.get("totalChapterNum", "")
                        if book_id and book_name:
                            videos.append({
                                "vod_id": f"/drama/{book_id}",
                                "vod_name": book_name,
                                "vod_pic": cover_url,
                                "vod_remarks": f"{status} {total_chapters}集" if total_chapters else status
                            })
                
                # SEO分类下的推荐
                if "seoColumnVos" in page_props and isinstance(page_props["seoColumnVos"], list):
                    for column in page_props["seoColumnVos"]:
                        book_infos = column.get("bookInfos", [])
                        for book in book_infos:
                            book_id = book.get("bookId", "")
                            book_name = book.get("bookName", "")
                            cover_url = book.get("coverWap", "")
                            status = book.get("statusDesc", "")
                            total_chapters = book.get("totalChapterNum", "")
                            
                            if book_id and book_name:
                                videos.append({
                                    "vod_id": f"/drama/{book_id}",
                                    "vod_name": book_name,
                                    "vod_pic": cover_url,
                                    "vod_remarks": f"{status} {total_chapters}集" if total_chapters else status
                                })
                 
            # # 去重
            # seen = set()
            # unique_videos = []
            # for video in videos:
            #     if video["vod_id"] not in seen:
            #         seen.add(video["vod_id"])
            #         unique_videos.append(video)
            # videos = unique_videos
        
        except Exception as e:
            print(f"获取首页推荐内容出错: {e}")
        
        result = {
            "list": videos
        }
        return result
    
    def categoryContent(self, tid, pg, filter, extend):
        """获取分类内容"""
        result = {}
        videos = []
        url = f"{self.siteUrl}/browse/{tid}/{pg}"
        response = self.fetch(url)
        html_content = response.text
        # 提取NEXT_DATA JSON数据
        next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        next_data_match = re.search(next_data_pattern, html_content, re.DOTALL)
        if next_data_match:
            next_data_json = json.loads(next_data_match.group(1))
            page_props = next_data_json.get("props", {}).get("pageProps", {})
            # 获取总页数和当前页
            current_page = page_props.get("page", 1)
            total_pages = page_props.get("pages", 1)
            # 获取书籍列表
            book_list = page_props.get("bookList", [])
            # 转换为通用格式
            for book in book_list:
                book_id = book.get("bookId", "")
                book_name = book.get("bookName", "")
                cover_url = book.get("coverWap", "")
                status_desc = book.get("statusDesc", "")
                total_chapters = book.get("totalChapterNum", "")
                if book_id and book_name:
                    videos.append({
                        "vod_id": f"/drama/{book_id}",
                        "vod_name": book_name,
                        "vod_pic": cover_url,
                        "vod_remarks": f"{status_desc} {total_chapters}集" if total_chapters else status_desc
                    })
            # 构建返回结果
            result = {
                "list": videos,
                "page": int(current_page),
                "pagecount": total_pages,
                "limit": len(videos),
                "total": total_pages * len(videos) if videos else 0
            }
        return result
    
    def switch(self, key, pg):
        # 搜索功能
        search_results = []
        # 获取第一页结果，并检查总页数
        url = f"{self.siteUrl}/search?searchValue={key}&page={pg}"
        response = self.fetch(url)
        html_content = response.text
        # 提取NEXT_DATA JSON数据
        next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        next_data_match = re.search(next_data_pattern, html_content, re.DOTALL)
        if next_data_match:
            next_data_json = json.loads(next_data_match.group(1))
            page_props = next_data_json.get("props", {}).get("pageProps", {})
            # 获取总页数
            total_pages = page_props.get("pages", 1)
            # 处理所有页的数据
            all_book_list = []
            # 添加第一页的书籍列表
            book_list = page_props.get("bookList", [])
            all_book_list.extend(book_list)
            # 如果有多页，获取其他页的数据
            if total_pages > 1 :  # quick模式只获取第一页
                for page in range(2, total_pages + 1):
                    next_page_url = f"{self.siteUrl}/search?searchValue={key}&page={page}"
                    next_page_response = self.fetch(next_page_url)
                    next_page_html = next_page_response.text
                    next_page_match = re.search(next_data_pattern, next_page_html, re.DOTALL)
                    if next_page_match:
                        next_page_json = json.loads(next_page_match.group(1))
                        next_page_props = next_page_json.get("props", {}).get("pageProps", {})
                        next_page_books = next_page_props.get("bookList", [])
                        all_book_list.extend(next_page_books)
            # 转换为统一的搜索结果格式
            for book in all_book_list:
                book_id = book.get("bookId", "")
                book_name = book.get("bookName", "")
                cover_url = book.get("coverWap", "")
                total_chapters = book.get("totalChapterNum", "0")
                status_desc = book.get("statusDesc", "")
                # 构建视频项
                vod = {
                    "vod_id": f"/drama/{book_id}",
                    "vod_name": book_name,
                    "vod_pic": cover_url,
                    "vod_remarks": f"{status_desc} {total_chapters}集"
                }
                search_results.append(vod)
        result = {
            "list": search_results,
            "page": pg
        }
        return result

    def searchContent(self, key, quick, pg=1):
        result = self.switch(key, pg=pg)
        result['page'] = pg
        return result
    
    def searchContentPage(self, key, quick, pg=1):
        return self.searchContent(key, quick, pg)

    def detailContent(self, ids):
        # 获取剧集信息
        vod_id = ids[0]
        episode_id = None
        chapter_id = None
        
        if not vod_id.startswith('/drama/'):
            if vod_id.startswith('/episode/'):
                episode_info = vod_id.replace('/episode/', '').split('/')
                if len(episode_info) >= 2:
                    episode_id = episode_info[0]
                    chapter_id = episode_info[1]
                    vod_id = f'/drama/{episode_id}'
            else:
                vod_id = '/drama/' + vod_id
        
        drama_url = self.siteUrl + vod_id
        print(f"请求URL: {drama_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Referer": self.siteUrl,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        rsp = self.fetch(drama_url, headers=headers)
        if not rsp or rsp.status_code != 200:
            print(f"请求失败，状态码: {getattr(rsp, 'status_code', 'N/A')}")
            return {}
        
        html = rsp.text
        next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        
        if not next_data_match:
            print("未找到NEXT_DATA内容")
            return {}
        
        try:
            next_data = json.loads(next_data_match.group(1))
            page_props = next_data.get("props", {}).get("pageProps", {})
            print(f"找到页面属性，包含 {len(page_props.keys())} 个键")
            
            book_info = page_props.get("bookInfoVo", {})
            chapter_list = page_props.get("chapterList", [])
            
            title = book_info.get("title", "")
            sub_title = f"{book_info.get('totalChapterNum', '')}集"
            
            categories = []
            for category in book_info.get("categoryList", []):
                categories.append(category.get("name", ""))
            
            vod_content = book_info.get("introduction", "")
            
            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": book_info.get("coverWap", ""),
                "type_name": ",".join(categories),
                "vod_year": "",
                "vod_area": book_info.get("countryName", ""),
                "vod_remarks": sub_title,
                "vod_actor": ", ".join([p.get("name", "") for p in book_info.get("performerList", [])]),
                "vod_director": "",
                "vod_content": vod_content
            }
            
            # 处理播放列表
            play_url_list = []
            episodes = []
            
            if chapter_list:
                print(f"找到 {len(chapter_list)} 个章节")
                
                # 先检查是否有可以直接使用的MP4链接作为模板
                mp4_template = None
                first_mp4_chapter_id = None
                
                # 先搜索第一个章节的MP4链接
                # 为提高成功率，尝试直接请求第一个章节的播放页
                if chapter_list and len(chapter_list) > 0:
                    first_chapter = chapter_list[0]
                    first_chapter_id = first_chapter.get("chapterId", "")
                    drama_id_clean = vod_id.replace('/drama/', '')
                    
                    if first_chapter_id and drama_id_clean:
                        first_episode_url = f"{self.siteUrl}/episode/{drama_id_clean}/{first_chapter_id}"
                        print(f"请求第一集播放页: {first_episode_url}")
                        
                        first_rsp = self.fetch(first_episode_url, headers=headers)
                        if first_rsp and first_rsp.status_code == 200:
                            first_html = first_rsp.text
                            # 直接从HTML提取MP4链接
                            mp4_pattern = r'(https?://[^"\']+\.mp4)'
                            mp4_matches = re.findall(mp4_pattern, first_html)
                            if mp4_matches:
                                mp4_template = mp4_matches[0]
                                first_mp4_chapter_id = first_chapter_id
                                print(f"找到MP4链接模板: {mp4_template}")
                                print(f"模板对应的章节ID: {first_mp4_chapter_id}")
                
                # 如果未找到模板，再检查章节对象中是否有MP4链接
                if not mp4_template:
                    for chapter in chapter_list[:5]:  # 只检查前5个章节以提高效率
                        if "chapterVideoVo" in chapter and chapter["chapterVideoVo"]:
                            chapter_video = chapter["chapterVideoVo"]
                            mp4_url = chapter_video.get("mp4", "") or chapter_video.get("mp4720p", "") or chapter_video.get("vodMp4Url", "")
                            if mp4_url and ".mp4" in mp4_url:
                                mp4_template = mp4_url
                                first_mp4_chapter_id = chapter.get("chapterId", "")
                                print(f"从chapterVideoVo找到MP4链接模板: {mp4_template}")
                                print(f"模板对应的章节ID: {first_mp4_chapter_id}")
                                break
                
                # 遍历所有章节处理播放信息
                for chapter in chapter_list:
                    chapter_id = chapter.get("chapterId", "")
                    chapter_name = chapter.get("chapterName", "")
                    
                    # 1. 如果章节自身有MP4链接，直接使用
                    if "chapterVideoVo" in chapter and chapter["chapterVideoVo"]:
                        chapter_video = chapter["chapterVideoVo"]
                        mp4_url = chapter_video.get("mp4", "") or chapter_video.get("mp4720p", "") or chapter_video.get("vodMp4Url", "")
                        if mp4_url and ".mp4" in mp4_url:
                            episodes.append(f"{chapter_name}${mp4_url}")
                            continue
                    
                    # 2. 如果有MP4模板，尝试替换章节ID构建MP4链接
                    if mp4_template and first_mp4_chapter_id and chapter_id:
                        # 替换模板中的章节ID部分
                        if first_mp4_chapter_id in mp4_template:
                            new_mp4_url = mp4_template.replace(first_mp4_chapter_id, chapter_id)
                            episodes.append(f"{chapter_name}${new_mp4_url}")
                            continue
                    
                    # 3. 如果上述方法都不可行，回退到使用chapter_id构建中间URL
                    if chapter_id and chapter_name:
                        url = f"{vod_id}${chapter_id}${chapter_name}"
                        episodes.append(f"{chapter_name}${url}")
            
            if not episodes and vod_id:
                # 尝试构造默认的集数
                total_chapters = int(book_info.get("totalChapterNum", "0"))
                if total_chapters > 0:
                    print(f"尝试构造 {total_chapters} 个默认集数")
                    
                    # 如果知道章节ID的模式，可以构造
                    if chapter_id and episode_id:
                        for i in range(1, total_chapters + 1):
                            chapter_name = f"第{i}集"
                            url = f"{vod_id}${chapter_id}${chapter_name}"
                            episodes.append(f"{chapter_name}${url}")
                    else:
                        # 使用普通的构造方式
                        for i in range(1, total_chapters + 1):
                            chapter_name = f"第{i}集"
                            url = f"{vod_id}${chapter_name}"
                            episodes.append(f"{chapter_name}${url}")
            
            if episodes:
                play_url_list.append("#".join(episodes))
                vod['vod_play_from'] = '珍爱短剧'
                vod['vod_play_url'] = '$$$'.join(play_url_list)
            
            result = {
                'list': [vod]
            }
            return result
        except Exception as e:
            print(f"解析详情页失败: {str(e)}")
            print(traceback.format_exc())
            return {}

    def playerContent(self, flag, id, vipFlags):
        result = {}
        print(f"调用playerContent: flag={flag}, id={id}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Referer": self.siteUrl,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        # 解析id参数
        parts = id.split('$')
        drama_id = None
        chapter_id = None
        
        if len(parts) >= 2:
            drama_id = parts[0]
            chapter_id = parts[1]
            chapter_name = parts[2] if len(parts) > 2 else "第一集"
            print(f"解析参数: drama_id={drama_id}, chapter_id={chapter_id}")
        else:
            # 处理旧数据格式
            print(f"使用原始URL格式: {id}")
            result["parse"] = 0
            result["url"] = id
            result["header"] = json.dumps(headers)
            return result
        
        # 直接检查chapter_id是否包含http（可能已经是视频链接）
        if 'http' in chapter_id and '.mp4' in chapter_id:
            print(f"已经是MP4链接: {chapter_id}")
            result["parse"] = 0
            result["url"] = chapter_id
            result["header"] = json.dumps(headers)
            return result
        
        # 构建episode页面URL
        drama_id_clean = drama_id.replace('/drama/', '')
        episode_url = f"{self.siteUrl}/episode/{drama_id_clean}/{chapter_id}"
        print(f"请求episode页面: {episode_url}")
        
        try:
            rsp = self.fetch(episode_url, headers=headers)
            if not rsp or rsp.status_code != 200:
                print(f"请求失败，状态码: {getattr(rsp, 'status_code', 'N/A')}")
                result["parse"] = 0
                result["url"] = id
                result["header"] = json.dumps(headers)
                return result
            
            html = rsp.text
            print(f"获取页面大小: {len(html)} 字节")
            
            # 尝试从NEXT_DATA提取视频链接
            mp4_url = None
            
            # 方法1: 从NEXT_DATA提取
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            if next_data_match:
                try:
                    print("找到NEXT_DATA")
                    next_data = json.loads(next_data_match.group(1))
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    
                    # 从chapterList中查找当前章节
                    chapter_list = page_props.get("chapterList", [])
                    print(f"找到章节列表，长度: {len(chapter_list)}")
                    
                    for chapter in chapter_list:
                        if chapter.get("chapterId") == chapter_id:
                            print(f"找到匹配的章节: {chapter.get('chapterName')}")
                            chapter_video = chapter.get("chapterVideoVo", {})
                            mp4_url = chapter_video.get("mp4", "") or chapter_video.get("mp4720p", "") or chapter_video.get("vodMp4Url", "")
                            if mp4_url:
                                print(f"从chapterList找到MP4链接: {mp4_url}")
                                break
                    
                    # 如果未找到，尝试从当前章节获取
                    if not mp4_url:
                        current_chapter = page_props.get("chapterInfo", {})
                        if current_chapter:
                            print("找到当前章节信息")
                            chapter_video = current_chapter.get("chapterVideoVo", {})
                            mp4_url = chapter_video.get("mp4", "") or chapter_video.get("mp4720p", "") or chapter_video.get("vodMp4Url", "")
                            if mp4_url:
                                print(f"从chapterInfo找到MP4链接: {mp4_url}")
                except Exception as e:
                    print(f"解析NEXT_DATA失败: {str(e)}")
                    print(traceback.format_exc())
            
            # 方法2: 直接从HTML中提取MP4链接
            if not mp4_url:
                mp4_pattern = r'(https?://[^"\']+\.mp4)'
                mp4_matches = re.findall(mp4_pattern, html)
                if mp4_matches:
                    # 查找含有chapter_id的链接
                    matched_mp4 = False
                    for url in mp4_matches:
                        if chapter_id in url:
                            mp4_url = url
                            matched_mp4 = True
                            print(f"从HTML直接提取章节MP4链接: {mp4_url}")
                            break
                    
                    # 如果没找到包含chapter_id的链接，使用第一个
                    if not matched_mp4 and mp4_matches:
                        mp4_url = mp4_matches[0]
                        print(f"从HTML直接提取MP4链接: {mp4_url}")
            
            if mp4_url and ".mp4" in mp4_url:
                print(f"最终找到的MP4链接: {mp4_url}")
                result["parse"] = 0
                result["url"] = mp4_url
                result["header"] = json.dumps(headers)
                return result
            else:
                print(f"未找到有效的MP4链接，尝试再次解析页面内容")
                # 再尝试一次从HTML中广泛搜索所有可能的MP4链接
                all_mp4_pattern = r'(https?://[^"\']+\.mp4)'
                all_mp4_matches = re.findall(all_mp4_pattern, html)
                if all_mp4_matches:
                    mp4_url = all_mp4_matches[0]
                    print(f"从HTML广泛搜索找到MP4链接: {mp4_url}")
                    result["parse"] = 0
                    result["url"] = mp4_url
                    result["header"] = json.dumps(headers)
                    return result
                
                print(f"未找到视频链接，返回原episode URL: {episode_url}")
                result["parse"] = 0
                result["url"] = episode_url
                result["header"] = json.dumps(headers)
                return result
        except Exception as e:
            print(f"请求或解析失败: {str(e)}")
            print(traceback.format_exc())
            result["parse"] = 0
            result["url"] = id
            result["header"] = json.dumps(headers)
            return result
    
    def localProxy(self, param):
        # 本地代理处理，此处简单返回传入的参数
        return [200, "video/MP2T", {}, param]

    def destroy(self):
        # 资源回收
        pass 