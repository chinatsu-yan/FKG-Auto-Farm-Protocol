import customtkinter as ctk
import threading
import sys
import ctypes
from src.core.window import WindowManager
from src.logic.fkg_bot import FKGBot

# ==========================================
# 修复 Windows 多屏 DPI 缩放问题
# ==========================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except Exception:
    pass

# 设置 GUI 主题
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FKGAutoFarmApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Flower Knight Girl - Auto Farm Protocol")
        self.geometry("550x650")
        self.grid_columnconfigure(0, weight=1)

        self.bot_instance = None
        self.bot_thread = None

        self._build_ui()
        
        # 将标准输出重定向到 GUI 的日志框中
        sys.stdout = TextRedirector(self.log_textbox)

    def _build_ui(self):
        # 标题
        ctk.CTkLabel(self, text="🌸 FKG 全自动周回终端 v1.0", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- 窗口绑定 ---
        frame_win = ctk.CTkFrame(self)
        frame_win.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame_win, text="🖥️ 目标浏览器/客户端窗口:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        self.window_combo = ctk.CTkComboBox(frame_win, width=350, values=["点击刷新获取..."])
        self.window_combo.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        ctk.CTkButton(frame_win, text="刷新", width=80, command=self.refresh_windows).grid(row=1, column=1, padx=10, pady=(0, 15))

        # --- 任务配置 ---
        frame_cfg = ctk.CTkFrame(self)
        frame_cfg.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame_cfg, text="🧪 允许消耗 [50%体力恢复蜜] 的最大数量:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        self.potion_entry = ctk.CTkEntry(frame_cfg, width=150)
        self.potion_entry.insert(0, "10") # 默认 10 瓶
        self.potion_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # --- 控制按钮 ---
        self.btn_start = ctk.CTkButton(self, text="▶️ 启动后台挂机", height=45, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#E01B5D", hover_color="#B01548", command=self.toggle_bot)
        self.btn_start.grid(row=3, column=0, padx=20, pady=15, sticky="ew")

        # --- 实时日志控制台 ---
        self.log_textbox = ctk.CTkTextbox(self, height=200, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        self.refresh_windows()

    def refresh_windows(self):
        titles = WindowManager.get_all_windows()
        if titles:
            self.window_combo.configure(values=titles)
            # 尝试默认选中包含特定字眼的窗口
            for t in titles:
                if "Chrome" in t or "Edge" in t or "DMM" in t:
                    self.window_combo.set(t)
                    break
            else:
                self.window_combo.set(titles[0])

    def toggle_bot(self):
        if self.bot_instance and self.bot_instance.is_running:
            # 停止脚本
            self.bot_instance.is_running = False
            self.btn_start.configure(text="▶️ 启动后台挂机", fg_color="#E01B5D", hover_color="#B01548")
            print("\n🛑 已发送停止指令，脚本将在当前循环结束后停机。")
        else:
            # 启动脚本
            target_win = self.window_combo.get()
            try:
                max_pots = int(self.potion_entry.get())
            except ValueError:
                print("❌ 请输入正确的药水数量 (整数)！")
                return

            self.bot_instance = FKGBot(target_title=target_win, max_potions=max_pots)
            
            # 使用独立线程运行，防止 GUI 卡死
            self.bot_thread = threading.Thread(target=self.bot_instance.start_auto_farm, daemon=True)
            self.bot_thread.start()

            self.btn_start.configure(text="⏹️ 停止挂机", fg_color="#2E2E2E", hover_color="#1A1A1A")


# 工具类：将 print 的输出拦截并显示到 GUI 的文本框中
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_data):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_data)
        self.widget.see("end") # 自动滚动到底部
        self.widget.configure(state="disabled")

    def flush(self):
        pass

if __name__ == "__main__":
    app = FKGAutoFarmApp()
    app.mainloop()