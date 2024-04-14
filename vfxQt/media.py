import os
from typing import Any

from Qt import QtGui, QtSvg

from vfxQt.style import get_frames_per_second


class MediaCache:
    def __init__(self) -> None:
        self._cache = {}
        self._search_dir_paths = []

    def addSearchPath(self, dir_path: str) -> None:
        """Add a search path directory.
        An existing path will be removed and appended
        to the back.
        Args:
            dir_path (str): The directory to add.
        """
        if dir_path not in self._search_dir_paths:
            self._search_dir_paths.append(dir_path)
        else:
            self._search_dir_paths.remove(dir_path)
            self._search_dir_paths.append(dir_path)

    def removeSearchPath(self, dir_path) -> bool:
        """Remove a search path directory.
        Args:
            dir_path (str): The directory to add.
        Returns:
            bool: True if the directory was in the search path else False
        """
        if dir_path in self._search_dir_paths:
            self._search_dir_paths.remove(dir_path)
            return True
        return False

    def supportedResourceExtensions(self) -> list[str]:
        """The list of supported file formats.
        Returns:
            list[str]: The supported extensions.
        """
        return self._supported_resource_ext

    def isResourceSupported(self, resource_name):
        """Check if the resource is supported (purely by extension).
        Args:
            resource_name (str): The resource name.
        Returns:
            bool: The support state.
        """
        resource_file_ext = os.path.splitext(resource_name)[1]
        return resource_file_ext in self._supported_resource_ext

    def getResource(self, resource_name, track=True) -> Any:
        """Get the resource object.
        Args:
            resource_name (str): The resource name.
            track (int): Increment the usage tracker.
        Returns:
            Any: The resource object.
        """
        resource = self._cache.get(resource_name, None)
        if resource:
            if track:
                resource["users"] += 1
            return resource["object"]

        resource_file_ext = os.path.splitext(resource_name)[1]
        if resource_file_ext not in self._supported_resource_ext:
            raise Exception(
                f"Unsupported resource extension {resource_file_ext} | {resource_name}"
            )

        resource_file_path = None
        for search_dir_path in self._search_dir_paths[::-1]:
            search_file_path = os.path.join(search_dir_path, resource_name)
            if os.path.isfile(search_file_path):
                resource_file_path = search_file_path
                break
        if not resource_file_path:
            return None

        self._cache[resource_name] = {
            "object": self.allocateResource(resource_file_path),
            "users": 1,
        }
        return self._cache[resource_name]["object"]

    def allocateResource(self, resource_file_path):
        """Allocate the resource object.
        Args:
            resource_file_path (str): The resource file path.
        Returns:
            Any: The resource object.
        """
        raise NotImplementedError

    def releaseResource(self, resource_name, clear=True):
        """Release the resource object. If no tracked
        users are found, optionally remove the object
        from the cache.
        Args:
            resource_file_path (str): The resource file path.
            clear (bool): If True and no users are found, remove
                          the resource from the cache.
        Returns:
            Any: The resource object.
        """
        resource = self._cache.get(resource_name, None)
        if resource is None:
            raise Exception(f"Resource {resource_name} not found!")
        resource["users"] = max(0, resource["users"] - 1)
        if clear and resource["users"] == 0:
            self._cache.pop(resource_name)

    def clearResources(self, force=False):
        """Clear resources. If force is False, only
        resources who don't have any users are removed.
        Args:
            force (bool): If True remove all resources regardless
                          of the usage state. This can lead
                          to memory leaks.
        Returns:
            Any: The resource object.
        """
        if force:
            self._cache.clear()
            return

        unused_resources = []
        for key, data in self._cache.items():
            if data["users"] <= 0:
                unused_resources.append(key)
        for key in unused_resources:
            self._cache.pop(key)


class ImageCache(MediaCache):
    def __init__(self) -> None:
        super().__init__()
        self._supported_resource_ext = (".svg", ".png", ".jpg", ".jpeg")

    def allocateResource(self, resource_file_path):
        """Allocate the resource object.
        Args:
            resource_file_path (str): The resource file path.
        Returns:
            Any: The resource object.
        """
        resource_file_ext = os.path.splitext(resource_file_path)[1]
        if resource_file_ext == ".svg":
            svg_renderer = QtSvg.QSvgRenderer(resource_file_path)
            if svg_renderer.animated():
                svg_renderer.setFramesPerSecond(get_frames_per_second() * 1000)
            resource_object = svg_renderer
        elif resource_file_ext.endswith((".png", ".jpg", ".jpeg")):
            pixmap = QtGui.QPixmap(resource_file_path)
            resource_object = pixmap
        return resource_object


def getImageCache():
    return getattr(getImageCache, "instance", ImageCache())


class IconCache(MediaCache):
    def __init__(self) -> None:
        super().__init__()


def getIconCache():
    return getattr(getIconCache, "instance", IconCache())
