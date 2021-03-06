import ctypes
import os
import platform

import CraftOS.OsUtilsBase
from CraftDebug import craftDebug


class FileAttributes():
    # https://msdn.microsoft.com/en-us/library/windows/desktop/gg258117(v=vs.85).aspx
    FILE_ATTRIBUTE_READONLY = 0x1
    FILE_ATTRIBUTE_REPARSE_POINT = 0x400


class OsUtils(CraftOS.OsUtilsBase.OsUtilsBase):
    @staticmethod
    def rm(path, force=False):
        craftDebug.log.debug("deleting file %s" % path)
        if force:
            OsUtils.removeReadOnlyAttribute(path)
        return ctypes.windll.kernel32.DeleteFileW(path) != 0

    @staticmethod
    def rmDir(path, force=False):
        craftDebug.log.debug("deleting directory %s" % path)
        if force:
            OsUtils.removeReadOnlyAttribute(path)
        return ctypes.windll.kernel32.RemoveDirectoryW(path) != 0

    @staticmethod
    def isLink(path):
        return os.path.islink(path) \
               | OsUtils.getFileAttributes(path) & FileAttributes.FILE_ATTRIBUTE_REPARSE_POINT  # Detect a Junction

    @staticmethod
    def getFileAttributes(path):
        return ctypes.windll.kernel32.GetFileAttributesW(path)

    @staticmethod
    def removeReadOnlyAttribute(path):
        attributes = OsUtils.getFileAttributes(path)
        return ctypes.windll.kernel32.SetFileAttributesW(path,
                                                         attributes & ~ FileAttributes.FILE_ATTRIBUTE_READONLY) != 0

    @staticmethod
    def setConsoleTitle(title):
        return ctypes.windll.kernel32.SetConsoleTitleW(title) != 0

    @staticmethod
    def supportsSymlinks():
        _, ver, _, _ = platform.win32_ver()
        ver = ver.split(".")
        if len(ver) < 3:
            return False
        # Since Windows 10 14972 admin rights are no longer required to create symlinks
        # https://blogs.windows.com/buildingapps/2016/12/02/symlinks-windows-10/
        return ver[0] == "10" and int(ver[2]) >= 14972
