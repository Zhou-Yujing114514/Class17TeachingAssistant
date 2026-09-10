"""麦克风实时电平采集（sounddevice 延迟导入，无设备时优雅降级）。"""
import math

from PySide6.QtCore import QObject, Signal


class AudioMeter(QObject):
    failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self._rms = 1e-7
        self._stream = None
        self._sd = None

    def start(self) -> bool:
        if self.running:
            return True
        try:
            import sounddevice as sd
        except Exception as e:  # 缺少 PortAudio / 无声音驱动
            self.failed.emit(f"麦克风不可用：{e}")
            return False
        try:
            self._sd = sd

            def callback(indata, frames, time_info, status):  # 音频线程回调
                if indata is not None and len(indata):
                    rms = float(math.sqrt(max(0.0, (indata ** 2).mean())))
                    # 指数平滑，避免数字乱跳
                    self._rms = 0.7 * self._rms + 0.3 * rms

            self._stream = sd.InputStream(channels=1, blocksize=1024,
                                          dtype="float32", callback=callback,
                                          latency="high")
            self._stream.start()
            self.running = True
            return True
        except Exception as e:
            self.running = False
            self.failed.emit(f"无法打开麦克风：{e}\n请检查系统麦克风权限与设备。")
            return False

    def stop(self):
        self.running = False
        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
        except Exception:
            pass
        self._stream = None
        self._rms = 1e-7

    def read_dbfs(self) -> float:
        rms = min(1.0, max(1e-7, self._rms))
        return 20.0 * math.log10(rms)

    def estimated_db(self, offset: float) -> float:
        """dBFS + 校准偏移，映射为日常口径的估算分贝。"""
        db = self.read_dbfs() + offset
        return max(20.0, min(120.0, db))


def band_of(db: float) -> str:
    if db < 45:
        return "很安静"
    if db < 58:
        return "轻声"
    if db < 72:
        return "朗读适宜"
    if db < 85:
        return "偏响"
    return "过响"
