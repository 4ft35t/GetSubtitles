# coding: utf-8

from collections import OrderedDict as order_dict
from contextlib import closing
import json

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from getsub.constants import SUB_FORMATS
from getsub.downloader.downloader import Downloader


""" assrt.net 字幕下载器
"""


class AssrtDownloader(Downloader):

    name = "Assrt"
    choice_prefix = "[ASSRT]"
    site_url = "http://assrt.net"
    search_url = "http://assrt.net/sub/?searchword={}&no_redir=1"
    session = requests.session()
    session.headers = Downloader.header

    def get_subtitles(self, video, sub_num=5):

        print("Searching ASSRT...", end="\r")

        keywords = self.get_keywords(video)

        sub_dict = order_dict()
        while True:
            # 当前关键字查询
            keyword = " ".join(keywords)
            print(keyword)
            r = self.session.get(
                self.search_url.format(keyword),
                timeout=10,
            )
            bs_obj = BeautifulSoup(r.text, "html.parser")
            subs = bs_obj.find_all('div', {'class': 'subitem'})[1:]
            for sub in subs:
                language = sub.find('div', {'id': 'sublist_div'})
                if not language:
                    continue
                for i in language.find_all('span'):
                    text = i.text
                    if '格式' in text:
                        language = text
                    elif '语言' in text:
                        language = language + text
                        break
                sub = sub.find("a", {"class": "introtitle"})
                if not sub:
                    continue
                sub_name = self.choice_prefix + sub.attrs['title']

                if video.info["type"] == "movie" and "美剧" in sub_name:
                    continue

                sub_url = urljoin(self.site_url, sub.attrs['href'])
                type_score = 0
                type_score += ("英" in language) * 1
                type_score += ("繁" in language) * 2
                type_score += ("简" in language) * 4
                type_score += ("双语" in language) * 8
                sub_dict[f'{sub_name}{language}'] = {
                    "lan": type_score,
                    "link": sub_url,
                    "session": None,
                }
                if len(sub_dict) >= sub_num:
                    del keywords[:]  # 字幕条数达到上限，清空keywords
                    break

            if len(keywords) > 1:  # 字幕数未满，更换关键词继续查询
                keywords.pop(-1)
                continue

            break

        # 第一个候选字幕没有双语
        if len(sub_dict.items()) > 0 and list(sub_dict.items())[0][1]["lan"] < 8:
            sub_dict = order_dict(
                sorted(sub_dict.items(),
                       key=lambda e: e[1]["lan"], reverse=True)
            )
        return sub_dict

    def download_file(self, file_name, sub_url, session=None):
        r = self.session.get(sub_url)
        bs_obj = BeautifulSoup(r.text, "html.parser")

        download_link = bs_obj.find('div', {'class': 'download'})
        download_link = download_link.find('a').attrs['href']

        download_link = urljoin(self.site_url, download_link)

        try:
            with closing(self.session.get(download_link, stream=True)) as response:
                chunk_size = 1024  # 单次请求最大值
                # 内容体总大小
                content_size = int(response.headers.get(
                    "content-length", 1024 * 4))
                sub_data_bytes = b""
                for data in response.iter_content(chunk_size=chunk_size):
                    sub_data_bytes += data
        except requests.Timeout:
            return None, None

        datatypes = ['.rar', '.zip', '.7z', '.ass', '.srt']
        for datatype in datatypes:
            if datatype in download_link:
                print(download_link, datatype, len(sub_data_bytes))
                break
        else:
            datatype = "Unknown"

        return datatype, sub_data_bytes, ""
