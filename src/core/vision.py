import cv2
import numpy as np
import os
import win32gui
import win32ui
from ctypes import windll

class VisionManager:
    """
    视觉管理器：负责真·后台截图与图像识别 (无视窗口遮挡)
    """

    @staticmethod
    def take_background_screenshot(hwnd):
        """
        后台截图核心逻辑：即使窗口被遮挡也能截取（但不能最小化！）
        :param hwnd: 目标窗口的句柄
        :return: numpy.ndarray 格式的图像数据 (BGR)
        """
        try:
            # 获取窗口真实大小
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top

            if width <= 0 or height <= 0:
                print("[Vision] 窗口尺寸异常，可能被最小化了！")
                return None

            # 返回窗口的设备上下文（DC）
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # ==========================================
            # 核心透视魔法：PrintWindow
            # 参数 2 (PW_RENDERFULLCONTENT) 是能在 Win8.1 以上系统
            # 抓取带硬件加速的浏览器(Chrome/Edge)画面的关键！
            # ==========================================
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

            if result != 1:
                print("[Vision] 后台截图失败，窗口可能被挂起或最小化。")
                img = None
            else:
                # 将位图转换为 numpy 数组供 OpenCV 使用
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                # 构造 BGRA 图像
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

            # ==========================================
            # 极其重要的内存清理阶段 (防内存泄漏崩溃)
            # ==========================================
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if img is not None:
                # 去除 Alpha 通道，转换为 OpenCV 标准的 BGR 格式
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return frame
            return None

        except Exception as e:
            print(f"[Vision] 发生致命截屏异常: {e}")
            return None

    @staticmethod
    def find_image_in_frame(template_path, screen_frame, threshold=0.8):
        """
        在给定的截图中寻找目标图片
        """
        if not os.path.exists(template_path):
            print(f"[Vision] 找不到特征图片: {template_path}")
            return None

        template = cv2.imread(template_path)
        h, w = template.shape[:2]

        result = cv2.matchTemplate(screen_frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            return (max_loc[0], max_loc[1], w, h)
        return None