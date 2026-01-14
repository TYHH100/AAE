import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser
import pyperclip
import configparser
import os
import sys
import webbrowser

class AzureArchiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("AA 额外指令生成器")
        self.root.geometry("700x550")
        self.root.minsize(600, 500)

        # ==========================
        # 1. 全局样式设置
        # ==========================
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 定义常用颜色和字体
        self.font_family = tk.StringVar(value="Microsoft YaHei UI")
        self.font_size = tk.StringVar(value="10")
        self.font_main = (self.font_family.get(), int(self.font_size.get()))
        self.font_bold = (self.font_family.get(), int(self.font_size.get()), "bold")
        
        # 定义颜色变量
        self.bg_color = tk.StringVar(value="#F5F5F5")
        self.fg_color = tk.StringVar(value="#333333")
        self.highlight_color = tk.StringVar(value="#005A9E")
        self.notebook_bg = tk.StringVar(value="#E1E1E1")
        
        # 配置通用样式
        self.style.configure(".", font=self.font_main, background=self.bg_color.get())
        self.style.configure("TFrame", background=self.bg_color.get())
        self.style.configure("TLabel", background=self.bg_color.get(), foreground=self.fg_color.get())
        self.style.configure("TButton", padding=5, font=self.font_main)
        self.style.configure("TLabelframe", background=self.bg_color.get())
        self.style.configure("TLabelframe.Label", background=self.bg_color.get(), font=self.font_bold, foreground=self.highlight_color.get())
        self.style.configure("TNotebook", background=self.notebook_bg.get())
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

        # 初始化时间单位设置
        self.seconds_mode = tk.BooleanVar(value=False)
        
        # 初始化两个标签页
        self.setup_cmd_tab()
        self.setup_txt_tab()
        
        # 添加菜单栏
        self.create_menu_bar()
        
        # 加载配置文件
        self.load_config()

    # =========================================================================
    # 标签页 1: Environment 额外指令生成逻辑
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

        lbl_out = ttk.Label(bottom_frame, text="生成的指令队列:")
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
            
            # 根据秒模式设置初始值和标签
            if self.seconds_mode.get():
                self.inputs['time'].insert(0, "1.0")
                unit_text = "秒"
            else:
                self.inputs['time'].insert(0, "1000")
                unit_text = "ms (1000 = 1秒)"
                
            self.inputs['time'].pack(side="left", fill="x", expand=True)
            
            # 添加单位标签
            ttk.Label(time_frame, text=unit_text).pack(side="left", padx=5)
            
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
                
                # 根据秒模式设置初始值和标签
                if self.seconds_mode.get():
                    self.inputs['duration'].insert(0, "1.0")
                    unit_text = "秒"
                else:
                    self.inputs['duration'].insert(0, "1000")
                    unit_text = "ms"
                    
                self.inputs['duration'].pack(side="left")
                ttk.Label(dur_frame, text=unit_text).pack(side="left", padx=5)
                add_row(3, "持续时间:", dur_frame)

        elif "清除屏幕文字" in selection:
            ttk.Label(self.input_frame_container, text="功能:").grid(row=0, column=0, sticky="e", padx=10)
            ttk.Label(self.input_frame_container, text="清除所有屏幕上显示的文字 (ST/STM)\n因为屏幕文字不会主动清除\n需要搭配这个使用", foreground="gray").grid(row=0, column=1, sticky="w")

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
                # 处理时间转换
                time_value = self.inputs['time'].get()
                # 将秒转换为毫秒
                if self.seconds_mode.get():
                    try:
                        ms = str(int(float(time_value) * 1000))
                    except ValueError:
                        ms = "1000"
                else:
                    ms = time_value
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
                    if dur:
                        duration_value = dur.get()
                        # 将秒转换为毫秒
                        if self.seconds_mode.get():
                            try:
                                duration = str(int(float(duration_value) * 1000))
                            except ValueError:
                                duration = "1000"
                        else:
                            duration = duration_value
                    else:
                        duration = ""
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
    # 标签页 2: 文本格式化逻辑
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

    def create_menu_bar(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 创建"设置"菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        
        # 时间单位设置
        self.seconds_mode = tk.BooleanVar(value=False)
        settings_menu.add_checkbutton(
            label="秒自动转换为毫秒", 
            variable=self.seconds_mode, 
            command=self.update_time_input_fields
        )
        
        # 字体设置
        font_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="字体", menu=font_menu)
        
        # 字体名称子菜单
        family_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="字体名称", menu=family_menu)
        
        # 获取系统可用字体
        from tkinter import font
        font_families = sorted(font.families())
        
        # 添加前20种常用字体作为选项
        for family in font_families[:20]:
            family_menu.add_radiobutton(
                label=family, 
                variable=self.font_family, 
                value=family, 
                command=self.change_font_size
            )
        
        family_menu.add_separator()
        family_menu.add_command(
            label="更多...", 
            command=self.show_font_chooser
        )
        
        # 字体大小子菜单
        size_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="字体大小", menu=size_menu)
        
        for size in ["8", "9", "10", "11", "12", "14", "16"]:
            size_menu.add_radiobutton(
                label=f"{size}pt", 
                variable=self.font_size, 
                value=size, 
                command=self.change_font_size
            )
        
        # 主题设置
        self.theme = tk.StringVar(value="clam")
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="主题", menu=theme_menu)
        
        for theme in ["clam", "alt", "default", "classic"]:
            theme_menu.add_radiobutton(
                label=theme.capitalize(), 
                variable=self.theme, 
                value=theme, 
                command=self.change_theme
            )
        
        # 调色设置
        color_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="调色", menu=color_menu)
        
        # 背景颜色
        color_menu.add_command(
            label="背景颜色", 
            command=lambda: self.choose_color("背景颜色", self.bg_color, self.change_colors)
        )
        
        # 前景颜色
        color_menu.add_command(
            label="前景颜色", 
            command=lambda: self.choose_color("前景颜色", self.fg_color, self.change_colors)
        )
        
        # 高亮颜色
        color_menu.add_command(
            label="高亮颜色", 
            command=lambda: self.choose_color("高亮颜色", self.highlight_color, self.change_colors)
        )
        
        # 笔记本背景颜色
        color_menu.add_command(
            label="标签页背景颜色", 
            command=lambda: self.choose_color("标签页背景颜色", self.notebook_bg, self.change_colors)
        )
        
        # 添加"关于"菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 添加文档链接
        help_menu.add_separator()
        help_menu.add_command(label="跳转至AA官方的额外指令介绍", command=self.open_doc_url)
    
    def show_font_chooser(self):
        # 打开字体选择对话框
        from tkinter import font
        
        # 创建对话框窗口
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("选择字体")
        font_dialog.geometry("400x300")
        font_dialog.resizable(True, True)
        
        # 创建列表框显示所有字体
        font_list = tk.Listbox(font_dialog, font=("Courier New", 10))
        font_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 添加所有可用字体到列表框
        font_families = sorted(font.families())
        for family in font_families:
            font_list.insert("end", family)
            
            # 高亮当前选中的字体
            if family == self.font_family.get():
                font_list.selection_set(font_list.size() - 1)
                font_list.see(font_list.size() - 1)
        
        # 创建确认按钮
        def confirm_choice():
            selection = font_list.curselection()
            if selection:
                font_name = font_list.get(selection[0])
                self.font_family.set(font_name)
                self.change_font_size()
            font_dialog.destroy()
        
        # 创建取消按钮
        def cancel_choice():
            font_dialog.destroy()
        
        # 创建按钮框架
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # 添加按钮
        tk.Button(button_frame, text="确认", command=confirm_choice, width=10).pack(side="right", padx=5)
        tk.Button(button_frame, text="取消", command=cancel_choice, width=10).pack(side="right", padx=5)
    
    def get_config_path(self):
        if hasattr(sys, '_MEIPASS'):
            config_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            config_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(config_dir, "config.ini")
    
    def load_config(self):
        # 加载配置文件
        config_path = self.get_config_path()
        config = configparser.ConfigParser()
        
        if os.path.exists(config_path):
            try:
                config.read(config_path, encoding="utf-8")
                
                # 加载时间单位设置
                if config.has_option("Settings", "seconds_mode"):
                    self.seconds_mode.set(config.getboolean("Settings", "seconds_mode"))
                
                # 加载字体设置
                if config.has_option("Settings", "font_family"):
                    self.font_family.set(config.get("Settings", "font_family"))
                
                if config.has_option("Settings", "font_size"):
                    self.font_size.set(config.get("Settings", "font_size"))
                    self.change_font_size()
                
                # 加载主题设置
                if config.has_option("Settings", "theme"):
                    theme = config.get("Settings", "theme")
                    self.theme.set(theme)
                    self.change_theme()
                
                # 加载颜色设置
                color_changed = False
                
                if config.has_option("Settings", "bg_color"):
                    self.bg_color.set(config.get("Settings", "bg_color"))
                    color_changed = True
                
                if config.has_option("Settings", "fg_color"):
                    self.fg_color.set(config.get("Settings", "fg_color"))
                    color_changed = True
                
                if config.has_option("Settings", "highlight_color"):
                    self.highlight_color.set(config.get("Settings", "highlight_color"))
                    color_changed = True
                
                if config.has_option("Settings", "notebook_bg"):
                    self.notebook_bg.set(config.get("Settings", "notebook_bg"))
                    color_changed = True
                
                # 如果颜色有变化，更新界面
                if color_changed:
                    self.change_colors()
                    
                # 更新时间输入字段，确保与seconds_mode保持一致
                self.update_time_input_fields()
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        # 保存配置文件
        config_path = self.get_config_path()
        config = configparser.ConfigParser()
        
        # 创建设置节
        config["Settings"] = {
            "seconds_mode": str(self.seconds_mode.get()),
            "font_family": self.font_family.get(),
            "font_size": self.font_size.get(),
            "theme": self.theme.get(),
            "bg_color": self.bg_color.get(),
            "fg_color": self.fg_color.get(),
            "highlight_color": self.highlight_color.get(),
            "notebook_bg": self.notebook_bg.get()
        }
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def read_version(self):
        try:
            if hasattr(sys, '_MEIPASS'):
                version_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "version")
                if not os.path.exists(version_path):
                    version_path = os.path.join(sys._MEIPASS, "version")
            else:
                version_path = "version"
            
            with open(version_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"读取版本号失败: {e}")
            return
    
    def show_about(self):
        # 显示关于对话框
        version = self.read_version()
        messagebox.showinfo(
            "关于",
            "AA 额外指令生成器\n\n" +
            "项目仓库: github.com/TYHH100/AAE \n" +
            f"版本: {version}"
        )
    
    def open_doc_url(self):
        url = "https://aadoc.foxxlight.top/basics/%E9%A2%9D%E5%A4%96%E6%8C%87%E4%BB%A4"
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("错误", f"打开文档失败: {str(e)}")
    
    def change_font_size(self):
        # 更改应用程序的字体大小和字体族
        try:
            family = self.font_family.get()
            size = int(self.font_size.get())
            self.font_main = (family, size)
            self.font_bold = (family, size, "bold")
            
            # 重新配置样式
            self.style.configure(".", font=self.font_main)
            self.style.configure("TButton", font=self.font_main)
            self.style.configure("TLabelframe.Label", font=self.font_bold)
            self.style.configure("TNotebook.Tab", font=self.font_main)
            
            # 更新输入框和文本框的字体
            self.txt_cmd_output.config(font=self.font_main)
            self.txt_dialogue.config(font=self.font_main)
            
            # 刷新界面
            self.root.update_idletasks()
        except Exception as e:
            messagebox.showerror("错误", f"更改字体失败: {str(e)}")
        
        # 保存配置
        self.save_config()
    
    def choose_color(self, title, color_var, callback):
        # 打开颜色选择对话框
        try:
            color = colorchooser.askcolor(initialcolor=color_var.get(), title=title)
            if color and color[1]:
                color_var.set(color[1])
                if callback:
                    callback()
        except Exception as e:
            messagebox.showerror("错误", f"选择颜色失败: {str(e)}")
    
    def change_colors(self):
        # 更新应用程序的颜色
        try:
            bg_color = self.bg_color.get()
            fg_color = self.fg_color.get()
            highlight_color = self.highlight_color.get()
            notebook_bg = self.notebook_bg.get()
            
            # 更新样式
            self.style.configure(".", background=bg_color)
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelframe", background=bg_color)
            self.style.configure("TLabelframe.Label", background=bg_color, foreground=highlight_color)
            self.style.configure("TNotebook", background=notebook_bg)
            
            # 更新根窗口背景
            self.root.config(background=bg_color)
            
            # 刷新界面
            self.root.update_idletasks()
        except Exception as e:
            messagebox.showerror("错误", f"更改颜色失败: {str(e)}")
        
        # 保存配置
        self.save_config()
    
    def change_theme(self):
        # 更改应用程序的主题
        try:
            theme = self.theme.get()
            self.style.theme_use(theme)
            # 刷新界面
            self.root.update_idletasks()
        except Exception as e:
            messagebox.showerror("错误", f"更改主题失败: {str(e)}")
        
        # 保存配置
        self.save_config()
    
    def update_time_input_fields(self):
        # 当秒模式切换时，更新时间输入字段
        selection = self.cmd_type.get()
        
        if "等待" in selection:
            self.update_wait_time_field()
        elif "背景变换" in selection and "smooth" in self.inputs.get('mode', {}).get():
            self.update_bg_duration_field()
        
        # 保存配置
        self.save_config()
    
    def update_wait_time_field(self):
        # 更新等待指令的时间输入字段
        if 'time' in self.inputs:
            try:
                current_value = self.inputs['time'].get()
                if self.seconds_mode.get():
                    # 从毫秒转换为秒
                    ms = int(current_value)
                    seconds = ms / 1000.0
                    # 显示一位小数
                    new_value = f"{seconds:.1f}"
                else:
                    # 从秒转换为毫秒
                    seconds = float(current_value)
                    ms = int(seconds * 1000)
                    new_value = str(ms)
                
                # 更新输入框内容
                self.inputs['time'].delete(0, tk.END)
                self.inputs['time'].insert(0, new_value)
                
                # 更新单位标签
                parent = self.inputs['time'].master
                for widget in parent.winfo_children():
                    if isinstance(widget, ttk.Label):
                        widget.config(text="秒" if self.seconds_mode.get() else "ms (1000 = 1秒)")
                        break
            except Exception:
                # 如果转换失败，使用默认值
                default_value = "1.0" if self.seconds_mode.get() else "1000"
                self.inputs['time'].delete(0, tk.END)
                self.inputs['time'].insert(0, default_value)
    
    def update_bg_duration_field(self):
        # 更新背景变换指令的持续时间输入字段
        if 'duration' in self.inputs:
            try:
                current_value = self.inputs['duration'].get()
                if self.seconds_mode.get():
                    # 从毫秒转换为秒
                    ms = int(current_value)
                    seconds = ms / 1000.0
                    # 显示一位小数
                    new_value = f"{seconds:.1f}"
                else:
                    # 从秒转换为毫秒
                    seconds = float(current_value)
                    ms = int(seconds * 1000)
                    new_value = str(ms)
                
                # 更新输入框内容
                self.inputs['duration'].delete(0, tk.END)
                self.inputs['duration'].insert(0, new_value)
                
                # 更新单位标签
                parent = self.inputs['duration'].master
                for widget in parent.winfo_children():
                    if isinstance(widget, ttk.Label):
                        widget.config(text="秒" if self.seconds_mode.get() else "ms")
                        break
            except Exception:
                # 如果转换失败，使用默认值
                default_value = "1.0" if self.seconds_mode.get() else "1000"
                self.inputs['duration'].delete(0, tk.END)
                self.inputs['duration'].insert(0, default_value)

    def reset_txt_params(self):
        self.entry_color.delete(0, tk.END); self.entry_color.insert(0, "FF0000")
        self.btn_palette.config(bg="#f0f0f0")
        self.entry_size.delete(0, tk.END); self.entry_size.insert(0, "60")
        self.entry_ruby.delete(0, tk.END)
        self.entry_alpha.delete(0, tk.END)
        #self.txt_dialogue.delete("1.0", tk.END)
        #self.txt_dialogue.insert("1.0", "在这里输入对话文本...")

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureArchiveTool(root)
    root.mainloop()