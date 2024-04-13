class MediaCache:
    def __init__(self) -> None:
        self._search_dir_paths = []

    def addSearchPath(self, dir_path):
        pass

    def removeSearchPath(sef, dir_path):
        pass


class ImageCache(MediaCache):
    def __init__(self) -> None:
        super().__init__()


def getImageCache():
    return getattr(getImageCache, "instance", ImageCache())


class IconCache(MediaCache):
    def __init__(self) -> None:
        super().__init__()


def getIconCache():
    return getattr(getIconCache, "instance", IconCache())