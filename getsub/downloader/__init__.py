# coding: utf-8


from getsub.downloader.zimuzu import ZimuzuDownloader
from getsub.downloader.zimuku import ZimukuDownloader
from getsub.downloader.assrt import AssrtDownloader


class DownloaderManager:

    downloaders = (AssrtDownloader(), ZimukuDownloader(), ZimuzuDownloader())
    downloader_names = [d.__class__.name for d in downloaders]

    @classmethod
    def get_downloader_by_name(cls, name):
        for downloader in DownloaderManager.downloaders:
            if downloader.__class__.name == name:
                return downloader

    @classmethod
    def get_downloader_by_choice_prefix(cls, choice_prefix):
        for downloader in DownloaderManager.downloaders:
            if downloader.__class__.choice_prefix == choice_prefix:
                return downloader
