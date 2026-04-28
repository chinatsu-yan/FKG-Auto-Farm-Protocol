import ctypes
import random
import time

# Windows API 常量定义
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MK_LBUTTON = 0x0001

class ActionManager:
    """
    动作管理器：负责后台静默操作，不抢占物理鼠标
    """

    @staticmethod
    def background_click(hwnd, target_rect):
        """
        向指定窗口发送后台点击消息 (静默点击)
        :param hwnd: 目标窗口的句柄 (Handle)
        :param target_rect: (x, y, w, h) 目标图片在窗口内的相对坐标和尺寸
        """
        rel_x, rel_y, target_w, target_h = target_rect

        # 1. 计算出安全的随机落点（依然保留防封号的随机偏移）
        safe_margin_x = target_w * 0.2
        safe_margin_y = target_h * 0.2
        
        click_x = int(rel_x + random.randint(int(safe_margin_x), int(target_w - safe_margin_x)))
        click_y = int(rel_y + random.randint(int(safe_margin_y), int(target_h - safe_margin_y)))

        # 2. 将 X 和 Y 坐标打包成 Windows 消息需要的 lParam 格式
        # C语言宏 MAKELONG 的 Python 实现：(Y << 16) | (X & 0xFFFF)
        lparam = (click_y << 16) | (click_x & 0xFFFF)

        # 3. 发送按下和抬起消息 (PostMessage 是异步的，不会阻塞程序)
        ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
        time.sleep(random.uniform(0.05, 0.15)) # 拟人化停顿
        ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)
        
        print(f"[Action] 🎯 成功发送后台点击信号至相对坐标: ({click_x}, {click_y})")