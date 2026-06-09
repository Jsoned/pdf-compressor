import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading

class PDFCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF压缩工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', font=('微软雅黑', 10))
        self.style.configure('TLabel', font=('微软雅黑', 10))
        
        # 主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="PDF压缩工具", font=('微软雅黑', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件选择
        ttk.Label(main_frame, text="选择PDF文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=40)
        input_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览...", command=self.select_input).grid(row=1, column=2, pady=5)
        
        # 输出文件选择
        ttk.Label(main_frame, text="保存位置:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=40)
        output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览...", command=self.select_output).grid(row=2, column=2, pady=5)
        
        # 压缩质量选择
        ttk.Label(main_frame, text="压缩质量:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quality = tk.StringVar(value="medium")
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(quality_frame, text="低(文件最小)", variable=self.quality, value="low").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(quality_frame, text="中(推荐)", variable=self.quality, value="medium").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(quality_frame, text="高(质量好)", variable=self.quality, value="high").pack(side=tk.LEFT, padx=5)
        
        # 目标大小
        ttk.Label(main_frame, text="目标大小(MB):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.target_size = tk.StringVar(value="1.5")
        ttk.Entry(main_frame, textvariable=self.target_size, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 压缩按钮
        self.compress_btn = ttk.Button(main_frame, text="开始压缩", command=self.start_compress, width=20)
        self.compress_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="gray")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # 结果显示
        self.result_text = tk.Text(main_frame, height=6, width=60, state='disabled', bg='#f0f0f0')
        self.result_text.grid(row=8, column=0, columnspan=3, pady=10)
        
        # 查找Ghostscript路径
        self.gs_path = self.find_ghostscript()
        if not self.gs_path:
            self.show_result("警告: 未找到Ghostscript，请确保已安装\n")
    
    def find_ghostscript(self):
        """查找Ghostscript可执行文件"""
        possible_paths = [
            r"C:\Users\jyx\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\vm\tools\app\ghostscript\gswin64c.exe",
            r"C:\Program Files\gs\gs10.07.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.02.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.01.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.00.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs9.56.1\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs9.55.0\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs9.56.1\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\gs9.55.0\bin\gswin32c.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 尝试从PATH中查找
        try:
            result = subprocess.run(['where', 'gswin64c'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def select_input(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            # 自动设置输出路径
            if not self.output_path.get():
                dir_name = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                self.output_path.set(os.path.join(dir_name, f"{base_name}_压缩版.pdf"))
    
    def select_output(self):
        """选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存压缩后的PDF",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def get_quality_settings(self):
        """根据选择获取压缩参数"""
        quality = self.quality.get()
        if quality == "low":
            return {
                'PDFSETTINGS': '/screen',
                'ColorImageResolution': '50',
                'GrayImageResolution': '50',
                'MonoImageResolution': '50'
            }
        elif quality == "medium":
            return {
                'PDFSETTINGS': '/screen',
                'ColorImageResolution': '60',
                'GrayImageResolution': '60',
                'MonoImageResolution': '60'
            }
        else:  # high
            return {
                'PDFSETTINGS': '/ebook',
                'ColorImageResolution': '100',
                'GrayImageResolution': '100',
                'MonoImageResolution': '100'
            }
    
    def start_compress(self):
        """开始压缩"""
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("错误", "请选择有效的PDF文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件位置")
            return
        
        if not self.gs_path:
            messagebox.showerror("错误", "未找到Ghostscript，请安装后重试")
            return
        
        # 禁用按钮
        self.compress_btn.config(state='disabled')
        self.progress['value'] = 0
        self.status_label.config(text="正在压缩...", foreground="blue")
        
        # 在后台线程中执行压缩
        thread = threading.Thread(target=self.compress_pdf, args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def compress_pdf(self, input_file, output_file):
        """执行PDF压缩"""
        try:
            settings = self.get_quality_settings()
            
            cmd = [
                self.gs_path,
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={settings["PDFSETTINGS"]}',
                f'-dColorImageResolution={settings["ColorImageResolution"]}',
                f'-dGrayImageResolution={settings["GrayImageResolution"]}',
                f'-dMonoImageResolution={settings["MonoImageResolution"]}',
                '-dDownsampleColorImages=true',
                '-dDownsampleGrayImages=true',
                '-dDownsampleMonoImages=true',
                '-dColorImageDownsampleThreshold=1.0',
                '-dGrayImageDownsampleThreshold=1.0',
                '-dMonoImageDownsampleThreshold=1.0',
                '-dCompressFonts=true',
                '-dSubsetFonts=true',
                '-dEmbedAllFonts=false',
                '-dOptimize=true',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                f'-sOutputFile={output_file}',
                input_file
            ]
            
            # 更新进度
            self.root.after(0, lambda: self.progress.config(value=30))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            self.root.after(0, lambda: self.progress.config(value=80))
            
            if os.path.exists(output_file):
                original_size = os.path.getsize(input_file) / (1024 * 1024)
                final_size = os.path.getsize(output_file) / (1024 * 1024)
                ratio = (1 - final_size / original_size) * 100 if original_size > 0 else 0
                
                result_msg = f"压缩成功!\n"
                result_msg += f"原文件: {original_size:.2f} MB\n"
                result_msg += f"压缩后: {final_size:.2f} MB\n"
                result_msg += f"压缩率: {ratio:.1f}%\n"
                result_msg += f"保存位置: {output_file}"
                
                self.root.after(0, lambda: self.show_result(result_msg))
                self.root.after(0, lambda: self.status_label.config(text="压缩完成", foreground="green"))
                self.root.after(0, lambda: self.progress.config(value=100))
            else:
                error_msg = f"压缩失败\n错误: {result.stderr[:200] if result.stderr else '未知错误'}"
                self.root.after(0, lambda: self.show_result(error_msg))
                self.root.after(0, lambda: self.status_label.config(text="压缩失败", foreground="red"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_result(f"压缩出错: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="错误", foreground="red"))
        finally:
            self.root.after(0, lambda: self.compress_btn.config(state='normal'))
    
    def show_result(self, message):
        """显示结果"""
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', message)
        self.result_text.config(state='disabled')

def main():
    root = tk.Tk()
    app = PDFCompressor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
