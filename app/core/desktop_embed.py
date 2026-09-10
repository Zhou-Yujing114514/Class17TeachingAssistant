"""把窗口嵌入 Windows 桌面壁纸层（Progman / WorkerW），实现“和壁纸融为一体”。

原理与 Wallpaper Engine 相同：向 Progman 发送 0x052C 消息生成 WorkerW，
枚举找到壁纸层 WorkerW，再 SetParent 把挂件挂进去。
非 Windows 平台全部为空操作（返回 False，走普通置底兜底）。
"""
import sys

IS_WIN = sys.platform == "win32"

if IS_WIN:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    _SMTO_NORMAL = 0x0000


def _find_workerw():
    """找到位于图标层之下的壁纸 WorkerW 句柄。"""
    workerw = wintypes.HWND(0)

    def _enum(hwnd, _lparam):
        shell = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if shell:
            workerw.value = user32.FindWindowExW(0, hwnd, "WorkerW", None)
        return True

    user32.EnumWindows(WNDENUMPROC(_enum), 0)
    return workerw.value


def embed_into_wallpaper(hwnd: int) -> int:
    """把指定窗口挂到壁纸层。成功返回父窗口(WorkerW)句柄，失败返回 0。"""
    if not IS_WIN or not hwnd:
        return 0
    try:
        progman = user32.FindWindowW("Progman", None)
        result = wintypes.DWORD()
        user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, _SMTO_NORMAL, 1000,
                                   ctypes.byref(result))
        workerw = _find_workerw()
        if not workerw:
            return 0
        user32.SetParent(hwnd, workerw)
        return int(workerw)
    except Exception:
        return 0


def parent_alive(parent_hwnd: int) -> bool:
    if not IS_WIN or not parent_hwnd:
        return False
    try:
        return bool(user32.IsWindow(parent_hwnd))
    except Exception:
        return False


def send_to_bottom(hwnd: int) -> bool:
    """兜底：始终置底且不抢焦点。"""
    if not IS_WIN:
        return False
    try:
        HWND_BOTTOM = 1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        return True
    except Exception:
        return False
