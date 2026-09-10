"""倒计时计算与文案格式化。"""
import math
import datetime as dt


def parse_target(iso_text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso_text)


def remaining(target: dt.datetime):
    """返回 (总剩余秒, 是否已到, 天, 时, 分, 秒)。"""
    total = (target - dt.datetime.now()).total_seconds()
    if total <= 0:
        return 0.0, True, 0, 0, 0, 0
    days = int(total // 86400)
    rem = total - days * 86400
    hours = int(rem // 3600)
    rem -= hours * 3600
    minutes = int(rem // 60)
    seconds = int(rem - minutes * 60)
    return total, False, days, hours, minutes, seconds


def format_countdown(target: dt.datetime, precision: str, name: str = "") -> str:
    """按精度生成展示文案。precision: 'day' 精确到天 / 'second' 精确到秒。"""
    total, arrived, d, h, m, s = remaining(target)
    if arrived:
        return f"{name} 已到" if name else "已到"
    if precision == "day":
        days_left = math.ceil(total / 86400)
        return f"距离{name}还有 {days_left} 天"
    return f"距离{name}还有 {d} 天 {h:02d} 时 {m:02d} 分 {s:02d} 秒"
