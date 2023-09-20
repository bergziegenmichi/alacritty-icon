from __future__ import annotations

import os
from pathlib import Path

THEME_CACHE: dict[str, Theme] = []

class Theme:
    path: Path = None
    index_file: Path = None
    parents: list[Theme] = None
    directories: list[ThemeSubdirectory] = None

    @staticmethod
    def get_theme_directory(theme_name: str) -> Path:
        icon_theme_directories = [
            Path.home() / ".local/share/icons",
            Path("/usr/share/icons")
        ]
        for icon_theme_directory in icon_theme_directories:
            theme_directory = icon_theme_directory / theme_name
            if theme_directory.is_dir():
                return theme_directory


    @staticmethod
    def from_theme_name(theme_name: str) -> Theme:
        return Theme.check_cache_before_creation(Theme.get_theme_directory(theme_name))


    @staticmethod
    def check_cache_before_creation(theme_directory: Path) -> Theme:
        if str(theme_directory) in THEME_CACHE.keys():
            return THEME_CACHE[str(theme_directory)]
        else:
            return Theme(theme_directory)


    def __init__(self, theme_directory: Path):
        self.path = theme_directory
        self.index_file = theme_directory / "index.theme"

        with open(self.index_file, "r")  as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line != "[Icon Theme]":
                    break

                split_line = line.split("=")
                if len(split_line) == 2:
                    k: str = split_line[0]
                    v: str = split_line[1]
                    vs: list[str] = v.split(",")
                    if k == "Inherits":
                        self.parents = [Theme.from_theme_name(theme_name) for theme_name in vs]
                    if k == "Directories":
                        self.directories = [ThemeSubdirectory(Path(relpath), self) for relpath in vs]

    def has_parents(self) -> bool:
        return self.parents is not None and len(self.parents)

class ThemeSubdirectory:
    relpath: Path = None
    theme: Theme = None
    type: str = None
    size: int = None
    min_size: int = None
    max_size: int = None
    scale: int = None

    def __init__(self, relpath: Path, theme: Theme):
        self.relpath = relpath
        self.theme = theme

        with open(theme.index_file, "r") as f:
            for line in f:
                line = line.strip()
                if read:
                    if line.startswith("["):
                        break

                    split_line = line.split("=")
                    if len(split_line) == 2:
                        k, v = split_line
                        if k == "Type":
                            self.type = v
                        elif k == "Size":
                            self.size = v
                        elif k == "MinSize":
                            self.min_size = v
                        elif k == "MaxSize":
                            self.max_size = v
                        elif k == "Scale":
                            self.scale = v


                if line == f"[{str(relpath)}]":
                    read = True

    def full_path(self) -> Path:
        return self.theme.path / self.relpath


def find_icon(theme_name: str, icon: str, size: int, scale: str):
    filename = find_icon_helper(icon, size, scale, Theme.check_cache_before_creation(Theme.get_theme_directory(theme_name)))
    if filename is not None:
        return filename

    filename = find_icon_helper(icon, size, scale, Theme.check_cache_before_creation(Theme.get_theme_directory("hicolor")))
    if filename is not None:
        return filename

    return lookup_fallback_icon(icon)


def find_icon_helper(icon: str, size: int, scale: str, theme: Theme):
    filename = lookup_icon(icon, size, scale, theme)
    if filename is not None:
        return filename

    if theme.has_parents():
        for parent in theme.parents:
            filename = find_icon_helper(icon, size, scale, parent)
            if filename is not None:
                return filename

    return None


def lookup_icon(iconname: str, size: int, scale: str, theme: Theme):
    for subdir in theme.directories:
        for extension in ["png", "svg", "xpm"]:
            if directory_matches_size(subdir, size, scale):
                filename = f"{subdir.full_path()}/{iconname}.{extension}"
                if os.path.exists(filename):
                    return filename

    minimal_size = MAXINT
    closest_filename:str = None
    for subdir in theme.directories:
        for extension in ["png", "svg", "xpm"]:
            filename = f"{subdir.full_path()}/{iconname}.{extension}"
            if os.path.exists(filename) and directory_size_distance(subdir, size, scale) < minimal_size:
                closest_filename = filename
                minimal_size = directory_size_distance(subdir, size, scale)

    if closest_filename is not None:
        return closest_filename

    return None


def lookup_fallback_icon(iconname):
    for directory in basename list:
        for extension in ["png", "svg", "xpm"]:
            filename = f"{directory}/{iconname}.{extension}"
            if os.path.exists(filename):
                return filename

    return None


def directory_matches_size(subdir: ThemeSubdirectory, icon_size: int, icon_scale: str):
    if icon_scale != "iconscale":
        return False
    if subdir.type is "Fixed":
        return subdir.size == icon_size
    if subdir.type is "Scalable":
        return subdir.min_size <= icon_size <= subdir.max_size
    if type is "Threshold":
        return subdir.size - subdir.scale <= icon_size <= subdir.size + subdir.scale


def directory_size_distance(subdir, icon_size, icon_scale):
    icon_dimension = icon_size * icon_scale

    if subdir.type == "Fixed":
        return abs(subdir.size * subdir.scale - icon_dimension)

    elif subdir.type == "Scalable":
        if icon_dimension < subdir.min_size * subdir.scale:
            return subdir.min_size * subdir.scale - icon_dimension
        elif icon_dimension > subdir.max_size * subdir.scale:
            return icon_dimension - subdir.max_size * subdir.scale

    elif subdir.type == "Threshold":
        # confusing


    if Type is Scaled
        if icon_size * icon_scale < MinSize * Scale
            return MinSize * Scale - icon_size * icon_scale
        if icon_size * icon_scale > MaxSize * Scale
            return icon_size * icon_scale - MaxSize * Scale
        return 0
    if Type is Threshold
        if icon_size * icon_scale < (Size - Threshold) * Scale
            return MinSize * Scale - icon_size * icon_scale
        if icon_size * icon_size > (Size + Threshold) * Scale
            return icon_size * icon_size - MaxSize * Scale
        return 0

