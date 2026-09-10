# 高二17班教学助手

面向课堂教学的 Windows 桌面小工具集。简约白底界面、自研圆角标题栏，关闭后驻留系统托盘，倒计时可作为**霓虹挂件嵌入桌面壁纸层**，讲课时被其他窗口自动压在最底层，不影响上课。

## 功能

- **读书分贝测量仪**：麦克风实时估算分贝，含进度条、峰值、平均、音量区间提示，可校准偏移。
- **特定时刻倒计时**：多个倒计时卡片；事件名自定义；「精确到天 / 精确到秒」切换；到点显示「已到」；本地保存。
- **桌面嵌入挂件**：
  - 逐张「贴到桌面」或「一键全部贴到桌面」；
  - 无底透明、字号可调，默认**动态霓虹**发光字，也可自定义固定颜色；
  - 默认吸附桌面右上角，可拖动并记住位置；
  - 通过 Windows 壁纸层（Progman/WorkerW）真正与壁纸融为一体，打开 WPS 等软件时始终在最底层、不抢焦点；
  - 右键挂件可切换精度、颜色、收回。
- **托盘驻留**：点 ✕ 隐藏到右下角托盘，挂件继续运行；双击托盘图标回到主界面。
- **开机自启**：设置内一键开关，开机自动恢复挂件。

## 技术栈

Python 3.12 · PySide6（Qt）· sounddevice（麦克风）· PyInstaller（打包）· Inno Setup（安装包）

## 本地开发运行

```bash
pip install -r requirements.txt
python main.py
```

## 目录结构

```
main.py                     入口（托盘、单实例、自启参数）
app/
  core/                     存储、倒计时算法、音频采集、自启、壁纸层嵌入
  widgets/                  桌面霓虹挂件与管理器、开关控件
  ui/                       圆角标题栏、主窗口、全局样式
  pages/                    分贝仪 / 倒计时 / 设置 三个页面
assets/app.ico              校徽圆形图标
build/installer.iss         Inno Setup 安装包脚本
.github/workflows/          Windows 自动打包并发布 Release
```

## 自动打包

推送 `v*` 标签即由 GitHub Actions 在 Windows 上构建：
PyInstaller 生成程序 → Inno Setup 生成 `高二17班教学助手_Setup_vX.exe` → 发布到 Releases，
同时上传绿色便携版 zip。也可在 Actions 页面手动 `Run workflow` 生成测试产物。
