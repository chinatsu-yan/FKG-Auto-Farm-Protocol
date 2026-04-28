import pygetwindow as gw
import time

class WindowManager:
    """
    窗口管理器：负责获取窗口坐标、锁定目标窗口等底层操作。
    """
    
    @staticmethod
    def get_all_windows():
        """
        获取当前系统中所有带标题的窗口列表
        :return: 窗口标题列表 (List[str])
        """
        # 过滤掉没有标题的隐藏后台窗口
        return [win.title for win in gw.getAllWindows() if win.title]

    @staticmethod
    def get_window(title_keyword):
        """
        根据关键字模糊匹配并获取窗口对象
        :param title_keyword: 窗口标题的关键字（例如 "Chrome" 或 "DMM"）
        :return: 窗口对象，如果没找到则返回 None
        """
        try:
            windows = gw.getWindowsWithTitle(title_keyword)
            if windows:
                return windows[0] # 返回匹配到的第一个窗口
            return None
        except Exception as e:
            print(f"[Window] 获取窗口异常: {e}")
            return None

    @staticmethod
    def get_window_rect(title_keyword):
        """
        获取目标窗口的坐标区域
        :param title_keyword: 窗口标题的关键字
        :return: (left, top, width, height) 或者 None
        """
        win = WindowManager.get_window(title_keyword)
        if win:
            return (win.left, win.top, win.width, win.height)
        return None

    @staticmethod
    def activate_window(title_keyword):
        """
        将目标窗口激活并置于前台
        :param title_keyword: 窗口标题的关键字
        :return: bool (是否成功)
        """
        win = WindowManager.get_window(title_keyword)
        if win:
            try:
                # 如果窗口最小化了，先还原
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.5) # 给系统一点时间完成前台切换动画
                return True
            except Exception as e:
                print(f"[Window] 无法激活窗口 (可能由于权限问题): {e}")
                return False
        return False