import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser
import pyperclip

class AzureArchiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("AA 额外指令生成器")
        self.root.geometry("600x470")

        tab_control = ttk.Notebook(root)
        
        self.tab_cmd = ttk.Frame(tab_control)
        tab_control.add(self.tab_cmd, text='Environment额外指令栏 (#)')
        
        self.tab_txt = ttk.Frame(tab_control)
        tab_control.add(self.tab_txt, text='对话框文字 ([])')
        
        tab_control.pack(expand=1, fill="both")

        self.setup_cmd_tab()
        self.setup_txt_tab()

    # ==========================================
    # 标签页 1: Environment额外指令栏生成逻辑
    # ==========================================
    def setup_cmd_tab(self):
        frame = ttk.Frame(self.tab_cmd, padding=10)
        frame.pack(fill="both", expand=True)

        lbl_type = ttk.Label(frame, text="选择指令类型:")
        lbl_type.grid(row=0, column=0, sticky="w", pady=5)
        
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
        self.combo_cmd = ttk.Combobox(frame, textvariable=self.cmd_type, values=cmd_options, state="readonly")
        self.combo_cmd.grid(row=0, column=1, sticky="ew", pady=5)
        self.combo_cmd.bind("<<ComboboxSelected>>", self.update_cmd_inputs)
        self.combo_cmd.current(0)

        self.input_frame = ttk.LabelFrame(frame, text="参数设置", padding=10)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        lbl_out = ttk.Label(frame, text="生成的指令队列 (可手动编辑):")
        lbl_out.grid(row=2, column=0, sticky="w", pady=5)
        
        self.txt_cmd_output = scrolledtext.ScrolledText(frame, height=10)
        self.txt_cmd_output.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="添加指令到队列", command=self.add_command).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="复制全部", command=lambda: self.copy_to_clip(self.txt_cmd_output.get("1.0", tk.END))).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清空队列", command=lambda: self.txt_cmd_output.delete("1.0", tk.END)).pack(side="left", padx=5)

        self.update_cmd_inputs()

    def update_cmd_inputs(self, event=None):
        prev_mode = None
        mode_values = ["instant (立即)", "smooth (平滑)"]
        prev_fx = None
        fx_values = ["AronaTouch (序章的指纹识别)", "shot (被射击)"]
        if event and hasattr(event, 'widget'):
            try:
                evval = event.widget.get()
                if evval in mode_values:
                    prev_mode = evval
                if evval in fx_values:
                    prev_fx = evval
            except Exception:
                prev_mode = None
                prev_fx = None

        for widget in self.input_frame.winfo_children():
            widget.destroy()

        selection = self.cmd_type.get()
        self.inputs = {}

        if "等待" in selection:
            ttk.Label(self.input_frame, text="毫秒数 (ms):").grid(row=0, column=0, sticky="e")
            self.inputs['time'] = ttk.Entry(self.input_frame)
            self.inputs['time'].grid(row=0, column=1, sticky="w")
            self.inputs['time'].insert(0, "1000")
            ttk.Label(self.input_frame, text="例: 1000 = 1秒").grid(row=0, column=2, sticky="w", padx=5)

        elif "背景抖动" in selection:
            ttk.Label(self.input_frame, text="该指令无参数，直接添加即可。").grid(row=0, column=0)
            ttk.Label(self.input_frame, text="建议配合 #wait 使用").grid(row=1, column=0)

        elif "背景变换" in selection: # #zmc
            ttk.Label(self.input_frame, text="显示模式:").grid(row=0, column=0, sticky="e", padx=2)
            self.inputs['mode'] = ttk.Combobox(self.input_frame, values=["instant (立即)", "smooth (平滑)"], state="readonly")
            if prev_mode:
                try:
                    self.inputs['mode'].set(prev_mode)
                except Exception:
                    self.inputs['mode'].current(1)
            else:
                if event is None:
                    self.inputs['mode'].current(1)

            self.inputs['mode'].grid(row=0, column=1, sticky="w", pady=2)
            self.inputs['mode'].bind("<<ComboboxSelected>>", self.update_cmd_inputs)
            
            ttk.Label(self.input_frame, text="中心坐标:").grid(row=1, column=0, sticky="e", padx=2)
            coord_frame = ttk.Frame(self.input_frame)
            coord_frame.grid(row=1, column=1, sticky="w", pady=2)
            ttk.Label(coord_frame, text="X:").pack(side="left")
            self.inputs['x'] = ttk.Entry(coord_frame, width=6)
            self.inputs['x'].insert(0, "0")
            self.inputs['x'].pack(side="left", padx=2)
            ttk.Label(coord_frame, text=" Y:").pack(side="left")
            self.inputs['y'] = ttk.Entry(coord_frame, width=6)
            self.inputs['y'].insert(0, "0")
            self.inputs['y'].pack(side="left", padx=2)
            
            ttk.Label(self.input_frame, text="缩放系数:").grid(row=2, column=0, sticky="e", padx=2)
            scale_frame = ttk.Frame(self.input_frame)
            scale_frame.grid(row=2, column=1, sticky="w", pady=2)
            self.inputs['scale'] = ttk.Entry(scale_frame, width=10)
            self.inputs['scale'].insert(0, "3160")
            self.inputs['scale'].pack(side="left")
            ttk.Label(scale_frame, text=" (实际放大倍数为3160除以该系数)", font=("", 9)).pack(side="left", padx=5)

            if "smooth (平滑)" in self.inputs['mode'].get():
                ttk.Label(self.input_frame, text="持续时间:").grid(row=3, column=0, sticky="e", padx=2)
                duration_frame = ttk.Frame(self.input_frame)
                duration_frame.grid(row=3, column=1, sticky="w", pady=2)
                self.inputs['duration'] = ttk.Entry(duration_frame, width=10)
                self.inputs['duration'].insert(0, "1000")
                self.inputs['duration'].pack(side="left")
                ttk.Label(duration_frame, text=" ms (可选)").pack(side="left")

        elif "屏幕文字" in selection: # #st / #stm
            ttk.Label(self.input_frame, text="对齐方式:").grid(row=0, column=0, sticky="e")
            self.inputs['align'] = ttk.Combobox(self.input_frame, values=["左对齐 (#st)", "居中 (#stm)"], state="readonly")
            self.inputs['align'].current(0)
            self.inputs['align'].grid(row=0, column=1, sticky="w")

            coord_frame = ttk.Frame(self.input_frame)
            coord_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
            ttk.Label(coord_frame, text="坐标 X:").pack(side="left")
            self.inputs['x'] = ttk.Entry(coord_frame, width=8)
            self.inputs['x'].insert(0, "0")
            self.inputs['x'].pack(side="left", padx=2)
            ttk.Label(coord_frame, text=" Y:").pack(side="left")
            self.inputs['y'] = ttk.Entry(coord_frame, width=8)
            self.inputs['y'].insert(0, "0")
            self.inputs['y'].pack(side="left", padx=2)

            ttk.Label(self.input_frame, text="显示模式:").grid(row=2, column=0, sticky="e")
            self.inputs['mode'] = ttk.Combobox(self.input_frame, values=["instant (立即)", "smooth (渐显)", "serial (逐字)"], state="readonly")
            self.inputs['mode'].current(0)
            self.inputs['mode'].grid(row=2, column=1, sticky="w")

            ttk.Label(self.input_frame, text="字体大小:").grid(row=3, column=0, sticky="e")
            self.inputs['size'] = ttk.Entry(self.input_frame)
            self.inputs['size'].insert(0, "50")
            self.inputs['size'].grid(row=3, column=1, sticky="w")
            ttk.Label(self.input_frame, text="(50=原大)").grid(row=3, column=2, sticky="w", padx=5)

        elif "特殊效果" in selection:
            ttk.Label(self.input_frame, text="效果类型:").grid(row=0, column=0, sticky="e")
            self.inputs['fx_type'] = ttk.Combobox(self.input_frame, values=["AronaTouch (序章的指纹识别)", "shot (被射击)"], state="readonly")
            if prev_fx:
                try:
                    self.inputs['fx_type'].set(prev_fx)
                except Exception:
                    self.inputs['fx_type'].current(0)
            else:
                self.inputs['fx_type'].current(0)

            self.inputs['fx_type'].grid(row=0, column=1, sticky="w")
            self.inputs['fx_type'].bind("<<ComboboxSelected>>", self.update_cmd_inputs)

            # 如果选择 shot，则显示固定位置 ID 的复选框 (1-5)，允许多选以一次生成多条指令
            if "shot" in self.inputs['fx_type'].get():
                ttk.Label(self.input_frame, text="选择位置ID (可多选，生成一对一指令):").grid(row=1, column=0, sticky="e", padx=2)
                ids_frame = ttk.Frame(self.input_frame)
                ids_frame.grid(row=1, column=1, sticky="w", pady=2)
                # 使用 intvar 字典保存状态
                self.inputs['shot_ids'] = {}
                for i in range(1, 6):
                    var = tk.IntVar(value=0)
                    self.inputs['shot_ids'][i] = var
                    cb = ttk.Checkbutton(ids_frame, text=str(i), variable=var)
                    cb.pack(side="left", padx=2)
                #ttk.Label(self.input_frame, text="(未选择则生成占位，请手动修改)").grid(row=2, column=0, columnspan=2, sticky="w", padx=2)

        elif "菜单" in selection:
            self.menu_var = tk.StringVar(value="#hidemenu")
            ttk.Label(self.input_frame, text="操作类型:").grid(row=0, column=0, padx=5)
            
            rb1 = ttk.Radiobutton(self.input_frame, text="隐藏菜单 (#hidemenu)", 
                                  variable=self.menu_var, value="#hidemenu")
            rb1.grid(row=0, column=1, sticky="w")
            
            rb2 = ttk.Radiobutton(self.input_frame, text="显示菜单 (#showmenu)", 
                                  variable=self.menu_var, value="#showmenu")
            rb2.grid(row=1, column=1, sticky="w")
            
    def add_command(self):
        selection = self.cmd_type.get()
        result = ""

        try:
            if "等待" in selection:
                ms = self.inputs['time'].get()
                result = f"#wait;{ms}"
            
            elif "背景抖动" in selection:
                result = "#bgshake"
            
            elif "背景变换" in selection:
                # #zmc;模式;X坐标,Y坐标;缩放系数;持续时间
                mode = self.inputs['mode'].get().split(" ")[0]
                x, y = self.inputs['x'].get(), self.inputs['y'].get()
                scale = self.inputs['scale'].get()
                
                if mode == "instant":
                    result = f"#zmc;{mode};{x},{y};{scale};"
                else:
                    # 获取持续时间，如果为空则不带分号结尾或留空
                    dur = self.inputs.get('duration')
                    duration = dur.get() if dur else ""
                    result = f"#zmc;{mode};{x},{y};{scale};{duration};"

            elif "屏幕文字" in selection:
                # #st;[X坐标,Y坐标];模式;字体大小;
                align = self.inputs['align'].get()
                prefix = "#stm" if "居中" in align else "#st"
                x, y = self.inputs['x'].get(), self.inputs['y'].get()
                mode = self.inputs['mode'].get().split(" ")[0]
                size = self.inputs['size'].get()
                
                result = f"{prefix};[{x},{y}];{mode};{size};"

            elif "特殊效果" in selection:
                fx = self.inputs['fx_type'].get()
                if "shot" in fx:
                    # 从复选框获取被选中的 ID，生成对应多行 #N;fx;{shot}; 指令
                    shot_vars = self.inputs.get('shot_ids', {})
                    selected = []
                    for id_num, var in shot_vars.items():
                        try:
                            if var.get():
                                selected.append(str(id_num))
                        except Exception:
                            continue

                    if selected:
                        lines = [f"#{i};fx;{{shot}};" for i in selected]
                        result = "\n".join(lines)
                    else:
                        result = "#N;fx;{shot}; (未选择位置ID，已生成占位，请修改)"
                else:
                    result = "#fx;AronaTouch"

            elif "清除屏幕" in selection:
                result = "#clearST"
            
            elif "菜单" in selection:
                result = self.menu_var.get()

            current_content = self.txt_cmd_output.get("1.0", tk.END).strip()
            if current_content:
                self.txt_cmd_output.insert(tk.END, "\n" + result)
            else:
                self.txt_cmd_output.insert(tk.END, result)
                
        except Exception as e:
            messagebox.showerror("错误", f"生成指令失败: {str(e)}")

    # ==========================================
    # 标签页 2: 文本格式化逻辑
    # ==========================================
    def setup_txt_tab(self):
        frame = ttk.Frame(self.tab_txt, padding=10)
        frame.pack(fill="both", expand=True)

        lbl_edit = ttk.Label(frame, text="编辑对话框文本 (选中文字后点击下方按钮):")
        lbl_edit.pack(anchor="w")
        
        self.txt_dialogue = tk.Text(frame, height=8, undo=True)
        self.txt_dialogue.pack(fill="x", pady=5)
        self.txt_dialogue.insert("1.0", "在这里输入对话文本...")

        tools_frame = ttk.LabelFrame(frame, text="格式化工具", padding=5)
        tools_frame.pack(fill="x", pady=5)

        row1 = ttk.Frame(tools_frame)
        row1.pack(fill="x", pady=2)
        ttk.Button(row1, text="加粗 [b]", width=10, command=lambda: self.apply_tag("b")).pack(side="left", padx=2)
        ttk.Button(row1, text="斜体 [i]", width=10, command=lambda: self.apply_tag("i")).pack(side="left", padx=2)
        ttk.Button(row1, text="下划线 [u]", width=10, command=lambda: self.apply_tag("u")).pack(side="left", padx=2)
        ttk.Button(row1, text="删除线 [s]", width=10, command=lambda: self.apply_tag("s")).pack(side="left", padx=2)
        
        row2 = ttk.Frame(tools_frame)
        row2.pack(fill="x", pady=2)
        ttk.Button(row2, text="上标 [sup]", width=10, command=lambda: self.apply_tag("sup")).pack(side="left", padx=2)
        ttk.Button(row2, text="下标 [sub]", width=10, command=lambda: self.apply_tag("sub")).pack(side="left", padx=2)
        ttk.Button(row2, text="清除格式 [-]", width=10, command=lambda: self.insert_text("[-]")).pack(side="left", padx=2)

        row3 = ttk.Frame(tools_frame)
        row3.pack(fill="x", pady=5)
        
        row2 = ttk.Frame(tools_frame)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="颜色:").pack(side="left")
        self.entry_color = ttk.Entry(row2, width=10)
        self.entry_color.insert(0, "FF0000")
        self.entry_color.pack(side="left", padx=2)
        
        self.btn_palette = tk.Button(row2, text="🎨 选择颜色", bg="#f0f0f0", command=self.pick_color)
        self.btn_palette.pack(side="left", padx=5)
        ttk.Button(row2, text="应用颜色", command=self.apply_color).pack(side="left", padx=5)

        ttk.Label(row3, text="文字大小:").pack(side="left", padx=5)
        self.entry_size = ttk.Entry(row3, width=5)
        self.entry_size.insert(0, "60")
        self.entry_size.pack(side="left", padx=2)
        ttk.Button(row3, text="应用文字大小", command=self.apply_size).pack(side="left", padx=2)

        row4 = ttk.Frame(tools_frame)
        row4.pack(fill="x", pady=5)
        ttk.Label(row4, text="注音(Ruby):").pack(side="left")
        self.entry_ruby = ttk.Entry(row4, width=10)
        self.entry_ruby.pack(side="left", padx=2)
        ttk.Button(row4, text="应用注音", command=self.apply_ruby).pack(side="left", padx=2)
        
        ttk.Label(row4, text="透明度(00-99):").pack(side="left", padx=5)
        self.entry_alpha = ttk.Entry(row4, width=5)
        self.entry_alpha.pack(side="left", padx=2)
        ttk.Button(row4, text="应用透明", command=self.apply_alpha).pack(side="left", padx=2)

        main_btn_frame = ttk.Frame(frame)
        main_btn_frame.pack(pady=10)
        ttk.Button(main_btn_frame, text="复制结果", command=lambda: self.copy_to_clip(self.txt_dialogue.get("1.0", tk.END))).pack(side="left")
        ttk.Button(main_btn_frame, text="重置参数", command=self.reset_txt_params).pack(side="left", padx=5)
        ttk.Button(main_btn_frame, text="清空文本", command=lambda: self.txt_dialogue.delete("1.0", tk.END)).pack(side="left", padx=10)

    def get_selection(self):
        try:
            return self.txt_dialogue.selection_get()
        except:
            return ""

    def replace_selection(self, new_text):
        try:
            sel_first = self.txt_dialogue.index("sel.first")
            sel_last = self.txt_dialogue.index("sel.last")
            # 删除旧文本
            self.txt_dialogue.delete(sel_first, sel_last)
            # 插入新文本
            self.txt_dialogue.insert(sel_first, new_text)
        except tk.TclError:
            # 如果没有选中，直接在光标处插入
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
        if sel:
            new_text = f"[{tag}]{sel}[/{tag}]"
            self.replace_selection(new_text)
        else:
            self.insert_text(f"[{tag}][/{tag}]")

    def apply_color(self):
        color = self.entry_color.get()
        sel = self.get_selection()
        if sel:
            # 颜色指令通常格式为 [RRGGBBAA]文本[-]
            new_text = f"[{color}]{sel}[-]"
            self.replace_selection(new_text)
        else:
            self.insert_text(f"[{color}][-]")

    def apply_size(self):
        size = self.entry_size.get()
        sel = self.get_selection()
        if sel:
            new_text = f"[size={size}]{sel}[/size]"
            self.replace_selection(new_text)
        else:
            self.insert_text(f"[size={size}][/size]")

    def apply_ruby(self):
        ruby_text = self.entry_ruby.get()
        if not ruby_text:
            return
        sel = self.get_selection()
        if sel:
            new_text = f"[ruby={ruby_text}]{sel}[/ruby]"
            self.replace_selection(new_text)
        else:
            self.insert_text(f"[ruby={ruby_text}][/ruby]")
            
    def apply_alpha(self):
        alpha = self.entry_alpha.get()
        if not alpha:
            return
        sel = self.get_selection()
        # 透明度指令是 [00]text
        if sel:
            new_text = f"[{alpha}]{sel}"
            self.replace_selection(new_text)
        else:
            self.insert_text(f"[{alpha}]")

    def copy_to_clip(self, content):
        try:
            pyperclip.copy(content.strip())
            messagebox.showinfo("成功", "已复制到剪贴板")
        except:
            # 如果没有pyperclip，尝试使用tk的方法
            self.root.clipboard_clear()
            self.root.clipboard_append(content.strip())
            messagebox.showinfo("成功", "已复制到剪贴板")

    def reset_txt_params(self):
        # 重置颜色
        self.entry_color.delete(0, tk.END)
        self.entry_color.insert(0, "FF0000")
        self.btn_palette.config(bg="#f0f0f0")
        
        # 重置大小
        self.entry_size.delete(0, tk.END)
        self.entry_size.insert(0, "60")
        
        # 重置注音
        self.entry_ruby.delete(0, tk.END)
        
        # 重置透明度
        self.entry_alpha.delete(0, tk.END)
        
        # 重置文本框内容
        self.txt_dialogue.delete("1.0", tk.END)
        self.txt_dialogue.insert("1.0", "在这里输入对话文本...")

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureArchiveTool(root)
    root.mainloop()