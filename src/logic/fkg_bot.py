import time
from src.core.window import WindowManager
from src.core.vision import VisionManager
from src.core.action import ActionManager

class FKGBot:
    def __init__(self, target_title="Chrome", max_potions=5):
        self.target_title = target_title
        self.max_potions = max_potions
        self.used_potions = 0
        self.is_running = False

    def start_auto_farm(self):
        """
        启动自动周回（嗑药）的主循环
        """
        print(f"\n🚀 [FKG Bot] 启动自动化引擎！目标窗口: {self.target_title}")
        print(f"📊 设定最大消耗恢复蜜: {self.max_potions} 瓶")
        
        # 1. 锁定窗口句柄
        win = WindowManager.get_window(self.target_title)
        if not win:
            print(f"❌ [FKG Bot] 致命错误：找不到名为 '{self.target_title}' 的窗口！")
            return
            
        hwnd = win._hWnd
        self.is_running = True

        # 2. 进入状态机无限循环
        while self.is_running:
            # 每次循环开始，截取一次后台画面
            screen = VisionManager.take_background_screenshot(hwnd)
            
            if screen is None:
                print("⚠️ [FKG Bot] 画面截取失败，可能是窗口尺寸异常，5秒后重试...")
                time.sleep(5)
                continue

            # --- 状态判定与动作执行 ---
            
            # 状态 A: 弹出是否使用体力药界面 (左半屏安全切片机制)
            if VisionManager.find_image_in_frame("assets/battle/prompt_use_item.png", screen, threshold=0.8):
                # 【新增防呆】如果设定的吃药次数是 0，或者之前已经吃够了，在这里安全停止
                if self.used_potions >= self.max_potions:
                    print(f"🛑 [任务完成] 已达到预设次数 ({self.max_potions})，本次体力耗尽不再吃药，脚本安全退出。")
                    self.is_running = False
                    break
                    
                print(f"💊 [状态] 检测到体力耗尽，准备吃药 (当前进度 {self.used_potions}/{self.max_potions} 瓶)...")
                
                h, w = screen.shape[:2]
                left_half_screen = screen[:, :w//2]
                btn_result = VisionManager.find_image_in_frame("assets/battle/btn_use_honey.png", left_half_screen, threshold=0.8)
                
                if btn_result:
                    print("✅ 成功锁定左侧免费恢复蜜，执行点击！")
                    ActionManager.background_click(hwnd, btn_result)
                    time.sleep(2) 
                else:
                    print("⚠️ 未能在左半侧找到可用药水 (可能免费药已耗尽)！脚本停止。")
                    self.is_running = False
                    break
                continue
                
            # 状态 B: 确认消耗药水弹窗 (【修正】移除这里的 break，让流程继续)
            elif self._check_and_click(hwnd, screen, "assets/battle/btn_confirm_yes.png", "assets/battle/btn_confirm_yes.png"):
                self.used_potions += 1
                print(f"✅ [状态] 点击确认消耗药水！(当前进度: {self.used_potions}/{self.max_potions})")
                time.sleep(2) 
                continue
                
            # 状态 C: 吃药成功提示弹窗
            elif self._check_and_click(hwnd, screen, "assets/battle/btn_close_popup.png", "assets/battle/btn_close_popup.png"):
                print("🆗 [状态] 关闭恢复成功提示。")
                time.sleep(1.5)
                continue
                
            # 状态 D: 自动再开按钮 (继续周回)
            elif self._check_and_click(hwnd, screen, "assets/battle/btn_auto_resume.png", "assets/battle/btn_auto_resume.png"):
                print("🔄 [状态] 点击自动再开，游戏已恢复自动周回！")
                
                # 【修复核心】在这里判断是否是最后一次吃药。
                # 只有把游戏重新送入自动战斗后，脚本才允许自己下班。
                if self.used_potions >= self.max_potions:
                    print(f"\n🎉 [任务圆满完成] 最后一瓶药水已生效，游戏继续挂机中！")
                    print(f"🛑 脚本监控职责已完成，后台引擎安全关闭。")
                    print(f"👉 (提示: 您可以随时再次点击界面上的按钮重新启动)")
                    self.is_running = False
                    break
                    
                time.sleep(5) # 继续刷本后，休息长一点时间再截图
                continue
                
            # 状态 E: 正常周回中
            else:
                print("💤 [监控中] 未发现异常或需要干预的弹窗，休眠 8 秒...")
                time.sleep(8) # 战斗中无需频繁截图，降低 CPU 占用

    def _check_and_click(self, hwnd, screen, detect_img_path, click_img_path):
        """
        辅助函数：检测屏幕上是否存在特征图，如果存在则点击目标图
        """
        # 1. 检查特征图是否存在
        detect_result = VisionManager.find_image_in_frame(detect_img_path, screen, threshold=0.8)
        
        if detect_result:
            # 2. 如果检测图和点击图不是同一个，则需要重新寻找点击图的坐标
            if detect_img_path != click_img_path:
                click_result = VisionManager.find_image_in_frame(click_img_path, screen, threshold=0.8)
                if click_result:
                    ActionManager.background_click(hwnd, click_result)
                    return True
            else:
                # 如果检测的就是要点击的按钮，直接点
                ActionManager.background_click(hwnd, detect_result)
                return True
                
        return False