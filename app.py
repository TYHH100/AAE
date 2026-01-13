import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser
import pyperclip

class AzureArchiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("AA 额外指令生成器 (Refactored)")
        self.root.geometry("700x550")
        self.root.minsize(600, 500)

        # ==========================
        # 1. 全局样式设置
        # ==========================
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用更现代扁平的主题

        # 定义常用颜色和字体
        self.font_main = ("Microsoft YaHei UI", 10)
        self.font_bold = ("Microsoft YaHei UI", 10, "bold")
        
        # 配置通用样式
        self.style.configure(".", font=self.font_main, background="#F5F5F5")
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("TLabel", background="#F5F5F5", foreground="#333333")
        self.style.configure("TButton", padding=5, font=self.font_main)
        self.style.configure("TLabelframe", background="#F5F5F5")
        self.style.configure("TLabelframe.Label", background="#F5F5F5", font=self.font_bold, foreground="#005A9E")
        self.style.configure("TNotebook", background="#E1E1E1")
        self.style.configure("TNotebook.Tab", padding=[10, 5], font=self.font_main)

        # ==========================
        # 2. 主布局容器
        # ==========================
        # 让主窗口内容可伸缩
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.tab_control = ttk.Notebook(root)
        self.tab_control.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_cmd = ttk.Frame(self.tab_control)
        self.tab_txt = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_cmd, text=' Environment 指令 (#) ')
        self.tab_control.add(self.tab_txt, text=' 对话框文字 ([]) ')

        # 初始化两个标签页
        self.setup_cmd_tab()
        self.setup_txt_tab()

    # =========================================================================
    # 标签页 1: Environment 额外指令生成逻辑 (重构版)
    # =========================================================================
    def setup_cmd_tab(self):
        # 布局配置：分为 上(选择)、中(参数)、下(输出)
        self.tab_cmd.columnconfigure(0, weight=1)
        self.tab_cmd.rowconfigure(1, weight=0) # 参数区自适应
        self.tab_cmd.rowconfigure(2, weight=1) # 输出区占据剩余空间

        # --- 顶部：类型选择 ---
        top_frame = ttk.Frame(self.tab_cmd, padding=10)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="选择指令类型:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.cmd_type = tk.StringVar()
        cmd_options = [
            "等待 (#wait)", 
            "背景抖动 (#bgshake)", 
            "背景变换 (#zmc)", 
            "屏幕文字 (#st/#stm)", 
            "特殊效果 (#fx)",
            "清除屏幕文字 (#clearST)",
            "隐藏/恢复菜单 (#hidemenu/show)"
        ]
        self.combo_cmd = ttk.Combobox(top_frame, textvariable=self.cmd_type, values=cmd_options, state="readonly", font=self.font_main)
        self.combo_cmd.grid(row=0, column=1, sticky="ew")
        self.combo_cmd.bind("<<ComboboxSelected>>", self.update_cmd_inputs)
        self.combo_cmd.current(0)

        # --- 中部：动态参数区 ---
        self.input_frame_container = ttk.LabelFrame(self.tab_cmd, text="参数配置", padding=15)
        self.input_frame_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.input_frame_container.columnconfigure(1, weight=1) # 让第二列输入框拉伸

        # --- 底部：输出与操作 ---
        bottom_frame = ttk.Frame(self.tab_cmd, padding=10)
        bottom_frame.grid(row=2, column=0, sticky="nsew")
        bottom_frame.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)

        lbl_out = ttk.Label(bottom_frame, text="生成的指令队列 (可编辑):")
        lbl_out.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.txt_cmd_output = scrolledtext.ScrolledText(bottom_frame, height=8, font=("Consolas", 10))
        self.txt_cmd_output.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # 按钮区
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.grid(row=2, column=0, sticky="ew")
        
        # 使用 grid 布局按钮，使其整齐
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        # 样式化按钮
        btn_add = ttk.Button(btn_frame, text="⬇ 添加到队列", command=self.add_command)
        btn_add.grid(row=0, column=0, sticky="ew", padx=5)
        
        btn_copy = ttk.Button(btn_frame, text="📋 复制全部", command=lambda: self.copy_to_clip(self.txt_cmd_output.get("1.0", tk.END)))
        btn_copy.grid(row=0, column=1, sticky="ew", padx=5)

        btn_clear = ttk.Button(btn_frame, text="🗑 清空队列", command=lambda: self.txt_cmd_output.delete("1.0", tk.END))
        btn_clear.grid(row=0, column=2, sticky="ew", padx=5)

        # 初始化输入框
        self.update_cmd_inputs()

    def update_cmd_inputs(self, event=None):
        """ 根据选择动态刷新参数区 """
        # 保存之前的状态，防止刷新丢失用户选择
        prev_mode = None
        prev_fx = None
        try:
            # 尝试从当前的 widget 里面找值，如果存在的话
            if hasattr(self, 'inputs'):
                if 'mode' in self.inputs and hasattr(self.inputs['mode'], 'get'):
                     prev_mode = self.inputs['mode'].get()
                if 'fx_type' in self.inputs and hasattr(self.inputs['fx_type'], 'get'):
                     prev_fx = self.inputs['fx_type'].get()
        except:
            pass

        # 清空旧控件
        for widget in self.input_frame_container.winfo_children():
            widget.destroy()

        selection = self.cmd_type.get()
        self.inputs = {}
        
        # 辅助函数：快速创建标签和Grid位置
        def add_row(row_idx, label_text, widget, span=1):
            ttk.Label(self.input_frame_container, text=label_text).grid(row=row_idx, column=0, sticky="e", padx=(0, 10), pady=5)
            widget.grid(row=row_idx, column=1, columnspan=span, sticky="ew", pady=5)
            return row_idx + 1

        row = 0

        if "等待" in selection:
            # 创建一个Frame来容纳输入框和单位标签
            time_frame = ttk.Frame(self.input_frame_container)
            
            # 创建输入框并添加到Frame
            self.inputs['time'] = ttk.Entry(time_frame)
            self.inputs['time'].insert(0, "1000")
            self.inputs['time'].pack(side="left", fill="x", expand=True)
            
            # 添加单位标签
            ttk.Label(time_frame, text="ms (1000 = 1秒)").pack(side="left", padx=5)
            
            # 使用add_row辅助函数将整个Frame添加到容器中
            add_row(0, "时长:", time_frame)
            
        elif "背景抖动" in selection:
            ttk.Label(self.input_frame_container, text="提示:").grid(row=0, column=0, sticky="e", padx=10)
            ttk.Label(self.input_frame_container, text="该指令无参数，配合 #wait 使用效果更佳。", foreground="gray").grid(row=0, column=1, sticky="w")

        elif "背景变换" in selection: # #zmc
            # 模式选择
            self.inputs['mode'] = ttk.Combobox(self.input_frame_container, values=["instant (立即)", "smooth (平滑)"], state="readonly")
            if prev_mode and ("instant" in prev_mode or "smooth" in prev_mode):
                 self.inputs['mode'].set(prev_mode)
            else:
                 self.inputs['mode'].current(1)
            self.inputs['mode'].bind("<<ComboboxSelected>>", self.update_cmd_inputs)
            add_row(0, "显示模式:", self.inputs['mode'])

            # 坐标输入
            coord_frame = ttk.Frame(self.input_frame_container)
            self.inputs['x'] = ttk.Entry(coord_frame, width=8)
            self.inputs['x'].insert(0, "0")
            self.inputs['y'] = ttk.Entry(coord_frame, width=8)
            self.inputs['y'].insert(0, "0")
            
            ttk.Label(coord_frame, text="X:").pack(side="left")
            self.inputs['x'].pack(side="left", padx=2)
            ttk.Label(coord_frame, text="Y:").pack(side="left", padx=(10, 2))
            self.inputs['y'].pack(side="left", padx=2)
            
            add_row(1, "中心坐标:", coord_frame)

            # 缩放系数
            scale_frame = ttk.Frame(self.input_frame_container)
            self.inputs['scale'] = ttk.Entry(scale_frame, width=12)
            self.inputs['scale'].insert(0, "3160")
            self.inputs['scale'].pack(side="left")
            ttk.Label(scale_frame, text="(实际倍数 = 3160 / 系数)", font=("", 8), foreground="gray").pack(side="left", padx=5)
            add_row(2, "缩放系数:", scale_frame)

            # 持续时间 (仅Smooth)
            if "smooth" in self.inputs['mode'].get():
                dur_frame = ttk.Frame(self.input_frame_container)
                self.inputs['duration'] = ttk.Entry(dur_frame, width=12)
                self.inputs['duration'].insert(0, "1000")
                self.inputs['duration'].pack(side="left")
                ttk.Label(dur_frame, text="ms").pack(side="left", padx=5)
                add_row(3, "持续时间:", dur_frame)

        elif "清除屏幕文字" in selection:
            ttk.Label(self.input_frame_container, text="功能:").grid(row=0, column=0, sticky="e", padx=10)
            ttk.Label(self.input_frame_container, text="清除所有屏幕上显示的文字 (ST)", foreground="gray").grid(row=0, column=1, sticky="w")

        elif "屏幕文字" in selection: # #st / #stm
            # 对齐
            self.inputs['align'] = ttk.Combobox(self.input_frame_container, values=["左对齐 (#st)", "居中 (#stm)"], state="readonly")
            self.inputs['align'].current(0)
            add_row(0, "对齐方式:", self.inputs['align'])

            # 坐标
            coord_frame = ttk.Frame(self.input_frame_container)
            self.inputs['x'] = ttk.Entry(coord_frame, width=8)
            self.inputs['x'].insert(0, "0")
            self.inputs['y'] = ttk.Entry(coord_frame, width=8)
            self.inputs['y'].insert(0, "0")
            ttk.Label(coord_frame, text="X:").pack(side="left")
            self.inputs['x'].pack(side="left", padx=2)
            ttk.Label(coord_frame, text="Y:").pack(side="left", padx=(10, 2))
            self.inputs['y'].pack(side="left", padx=2)
            add_row(1, "坐标:", coord_frame)

            # 模式
            self.inputs['mode'] = ttk.Combobox(self.input_frame_container, values=["instant (立即)", "smooth (渐显)", "serial (逐字)"], state="readonly")
            self.inputs['mode'].current(0)
            add_row(2, "显示动画:", self.inputs['mode'])

            # 字体大小
            size_frame = ttk.Frame(self.input_frame_container)
            self.inputs['size'] = ttk.Entry(size_frame, width=10)
            self.inputs['size'].insert(0, "50")
            self.inputs['size'].pack(side="left")
            ttk.Label(size_frame, text="(50 = 标准大小)", foreground="gray").pack(side="left", padx=5)
            add_row(3, "字体大小:", size_frame)

        elif "特殊效果" in selection:
            self.inputs['fx_type'] = ttk.Combobox(self.input_frame_container, values=["AronaTouch (序章指纹)", "shot (被射击)"], state="readonly")
            if prev_fx:
                try: self.inputs['fx_type'].set(prev_fx)
                except: self.inputs['fx_type'].current(0)
            else:
                self.inputs['fx_type'].current(0)
            self.inputs['fx_type'].bind("<<ComboboxSelected>>", self.update_cmd_inputs)
            add_row(0, "效果类型:", self.inputs['fx_type'])

            if "shot" in self.inputs['fx_type'].get():
                ids_frame = ttk.Frame(self.input_frame_container)
                self.inputs['shot_ids'] = {}
                for i in range(1, 6):
                    var = tk.IntVar(value=0)
                    self.inputs['shot_ids'][i] = var
                    cb = ttk.Checkbutton(ids_frame, text=str(i), variable=var)
                    cb.pack(side="left", padx=5)
                add_row(1, "位置 ID:", ids_frame)
                ttk.Label(self.input_frame_container, text="* 可多选，将生成多条指令", font=("", 8), foreground="gray").grid(row=2, column=1, sticky="w")

        elif "菜单" in selection:
            self.menu_var = tk.StringVar(value="#hidemenu")
            radio_frame = ttk.Frame(self.input_frame_container)
            ttk.Radiobutton(radio_frame, text="隐藏菜单 (#hidemenu)", variable=self.menu_var, value="#hidemenu").pack(side="left", padx=10)
            ttk.Radiobutton(radio_frame, text="显示菜单 (#showmenu)", variable=self.menu_var, value="#showmenu").pack(side="left", padx=10)
            add_row(0, "操作:", radio_frame)

    def add_command(self):
        # 逻辑保持不变
        selection = self.cmd_type.get()
        result = ""
        try:
            if "等待" in selection:
                ms = self.inputs['time'].get()
                result = f"#wait;{ms}"
            elif "背景抖动" in selection:
                result = "#bgshake"
            elif "背景变换" in selection:
                mode = self.inputs['mode'].get().split(" ")[0]
                x, y = self.inputs['x'].get(), self.inputs['y'].get()
                scale = self.inputs['scale'].get()
                if mode == "instant":
                    result = f"#zmc;{mode};{x},{y};{scale};"
                else:
                    dur = self.inputs.get('duration')
                    duration = dur.get() if dur else ""
                    result = f"#zmc;{mode};{x},{y};{scale};{duration};"
            elif "清除屏幕文字" in selection:
                result = "#clearST"
            elif "屏幕文字" in selection:
                align = self.inputs['align'].get()
                prefix = "#stm" if "居中" in align else "#st"
                x, y = self.inputs['x'].get(), self.inputs['y'].get()
                mode = self.inputs['mode'].get().split(" ")[0]
                size = self.inputs['size'].get()
                result = f"{prefix};[{x},{y}];{mode};{size};"
            elif "特殊效果" in selection:
                fx = self.inputs['fx_type'].get()
                if "shot" in fx:
                    shot_vars = self.inputs.get('shot_ids', {})
                    selected = []
                    for id_num, var in shot_vars.items():
                        try:
                            if var.get(): selected.append(str(id_num))
                        except: continue
                    if selected:
                        lines = [f"#{i};fx;{{shot}};" for i in selected]
                        result = "\n".join(lines)
                    else:
                        result = "#N;fx;{shot}; (未选择位置ID)"
                else:
                    result = "#fx;AronaTouch"
            elif "菜单" in selection:
                result = self.menu_var.get()

            current_content = self.txt_cmd_output.get("1.0", tk.END).strip()
            if current_content:
                self.txt_cmd_output.insert(tk.END, "\n" + result)
            else:
                self.txt_cmd_output.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("错误", f"生成指令失败: {str(e)}")

    # =========================================================================
    # 标签页 2: 文本格式化逻辑 (重构版)
    # =========================================================================
    def setup_txt_tab(self):
        # 布局：上(编辑框) 下(工具栏)
        self.tab_txt.columnconfigure(0, weight=1)
        self.tab_txt.rowconfigure(0, weight=1) 
        self.tab_txt.rowconfigure(1, weight=0)

        # --- 文本编辑区 ---
        edit_frame = ttk.LabelFrame(self.tab_txt, text="对话编辑器", padding=10)
        edit_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.rowconfigure(0, weight=1)

        self.txt_dialogue = tk.Text(edit_frame, height=5, undo=True, font=("Microsoft YaHei", 12), wrap="word")
        self.txt_dialogue.grid(row=0, column=0, sticky="nsew")
        self.txt_dialogue.insert("1.0", "在这里输入对话文本...")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(edit_frame, command=self.txt_dialogue.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.txt_dialogue['yscrollcommand'] = scrollbar.set

        # --- 工具栏区域 ---
        tools_container = ttk.Frame(self.tab_txt)
        tools_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        tools_container.columnconfigure(0, weight=1)
        tools_container.columnconfigure(1, weight=1)
        tools_container.columnconfigure(2, weight=1)

        # 1. 基础格式
        fmt_frame = ttk.LabelFrame(tools_container, text="基础样式", padding=5)
        fmt_frame.grid(row=0, column=0, sticky="nsew", padx=2)
        
        # 使用 Grid 布局按钮
        btns_fmt = [
            ("加粗 [b]", "b"), ("斜体 [i]", "i"),
            ("下划 [u]", "u"), ("删除 [s]", "s"),
            ("上标 [sup]", "sup"), ("下标 [sub]", "sub")
        ]
        for idx, (txt, tag) in enumerate(btns_fmt):
            r, c = divmod(idx, 2)
            ttk.Button(fmt_frame, text=txt, command=lambda t=tag: self.apply_tag(t)).grid(row=r, column=c, sticky="ew", padx=2, pady=2)
        fmt_frame.columnconfigure(0, weight=1)
        fmt_frame.columnconfigure(1, weight=1)

        # 2. 颜色与大小
        color_frame = ttk.LabelFrame(tools_container, text="颜色与大小", padding=5)
        color_frame.grid(row=0, column=1, sticky="nsew", padx=2)
        color_frame.columnconfigure(1, weight=1)

        # 颜色行
        ttk.Label(color_frame, text="色值:").grid(row=0, column=0)
        self.entry_color = ttk.Entry(color_frame, width=8)
        self.entry_color.insert(0, "FF0000")
        self.entry_color.grid(row=0, column=1, sticky="ew", padx=2)
        
        self.btn_palette = tk.Button(color_frame, text="🎨", bg="#f0f0f0", command=self.pick_color, relief="flat", width=3)
        self.btn_palette.grid(row=0, column=2, padx=2)
        ttk.Button(color_frame, text="应用", width=4, command=self.apply_color).grid(row=0, column=3)

        # 大小行
        ttk.Label(color_frame, text="大小:").grid(row=1, column=0)
        self.entry_size = ttk.Entry(color_frame, width=8)
        self.entry_size.insert(0, "60")
        self.entry_size.grid(row=1, column=1, sticky="ew", padx=2)
        ttk.Button(color_frame, text="应用", width=4, command=self.apply_size).grid(row=1, column=3)
        
        # 透明度行
        ttk.Label(color_frame, text="透明:").grid(row=2, column=0)
        self.entry_alpha = ttk.Entry(color_frame, width=8)
        self.entry_alpha.grid(row=2, column=1, sticky="ew", padx=2)
        ttk.Button(color_frame, text="应用", width=4, command=self.apply_alpha).grid(row=2, column=3)

        # 3. 高级与其他
        adv_frame = ttk.LabelFrame(tools_container, text="高级与其他", padding=5)
        adv_frame.grid(row=0, column=2, sticky="nsew", padx=2)
        adv_frame.columnconfigure(1, weight=1)

        ttk.Label(adv_frame, text="注音:").grid(row=0, column=0)
        self.entry_ruby = ttk.Entry(adv_frame)
        self.entry_ruby.grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(adv_frame, text="应用", width=4, command=self.apply_ruby).grid(row=0, column=2)

        ttk.Separator(adv_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Button(adv_frame, text="清除格式 [-]", command=lambda: self.insert_text("[-]")).grid(row=2, column=0, columnspan=3, sticky="ew", pady=1)

        # --- 底部全局操作 ---
        action_frame = ttk.Frame(self.tab_txt, padding=10)
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)

        ttk.Button(action_frame, text="✨ 复制结果", command=lambda: self.copy_to_clip(self.txt_dialogue.get("1.0", tk.END))).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(action_frame, text="↺ 重置参数", command=self.reset_txt_params).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(action_frame, text="🗑 清空文本", command=lambda: self.txt_dialogue.delete("1.0", tk.END)).grid(row=0, column=2, sticky="ew", padx=5)

    # ==========================
    # 辅助逻辑 (保持原样，适配新UI)
    # ==========================
    def get_selection(self):
        try: return self.txt_dialogue.selection_get()
        except: return ""

    def replace_selection(self, new_text):
        try:
            sel_first = self.txt_dialogue.index("sel.first")
            sel_last = self.txt_dialogue.index("sel.last")
            self.txt_dialogue.delete(sel_first, sel_last)
            self.txt_dialogue.insert(sel_first, new_text)
        except tk.TclError:
            self.txt_dialogue.insert(tk.INSERT, new_text)

    def insert_text(self, text):
        self.txt_dialogue.insert(tk.INSERT, text)

    def pick_color(self):
        color_code = colorchooser.askcolor(title="选择颜色")[1]
        if color_code:
            hex_clean = color_code.replace("#", "").upper()
            self.entry_color.delete(0, tk.END)
            self.entry_color.insert(0, hex_clean)
            self.btn_palette.config(bg=color_code)

    def apply_tag(self, tag):
        sel = self.get_selection()
        if sel: self.replace_selection(f"[{tag}]{sel}[/{tag}]")
        else: self.insert_text(f"[{tag}][/{tag}]")

    def apply_color(self):
        color = self.entry_color.get()
        sel = self.get_selection()
        if sel: self.replace_selection(f"[{color}]{sel}[-]")
        else: self.insert_text(f"[{color}][-]")

    def apply_size(self):
        size = self.entry_size.get()
        sel = self.get_selection()
        if sel: self.replace_selection(f"[size={size}]{sel}[/size]")
        else: self.insert_text(f"[size={size}][/size]")

    def apply_ruby(self):
        ruby_text = self.entry_ruby.get()
        if not ruby_text: return
        sel = self.get_selection()
        if sel: self.replace_selection(f"[ruby={ruby_text}]{sel}[/ruby]")
        else: self.insert_text(f"[ruby={ruby_text}][/ruby]")
            
    def apply_alpha(self):
        alpha = self.entry_alpha.get()
        if not alpha: return
        sel = self.get_selection()
        if sel: self.replace_selection(f"[{alpha}]{sel}")
        else: self.insert_text(f"[{alpha}]")

    def copy_to_clip(self, content):
        try:
            pyperclip.copy(content.strip())
            messagebox.showinfo("成功", "已复制到剪贴板")
        except:
            self.root.clipboard_clear()
            self.root.clipboard_append(content.strip())
            messagebox.showinfo("成功", "已复制到剪贴板 (Fallback)")

    def reset_txt_params(self):
        self.entry_color.delete(0, tk.END); self.entry_color.insert(0, "FF0000")
        self.btn_palette.config(bg="#f0f0f0")
        self.entry_size.delete(0, tk.END); self.entry_size.insert(0, "60")
        self.entry_ruby.delete(0, tk.END)
        self.entry_alpha.delete(0, tk.END)
        self.txt_dialogue.delete("1.0", tk.END)
        self.txt_dialogue.insert("1.0", "在这里输入对话文本...")

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureArchiveTool(root)
    root.mainloop()