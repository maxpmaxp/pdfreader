import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pdfreader import PDFDocument, SimplePDFViewer
from PIL import Image, ImageTk
import os
import re

class PDFParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFreader")
        self.root.geometry("700x500")
        self.root.configure(bg="#e0f7fa")

        # 历史记录文件
        self.history_file = "file_history.txt"
        self.recent_files = self.load_history()

        # 当前页面
        self.current_page_num = 0
        self.total_pages = 0

        # 创建框架用于放置按钮和其他控件
        self.button_frame = tk.Frame(root, bg="#f7f7f7", padx=20, pady=20)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # 创建按钮并美化
        self.open_button = tk.Button(self.button_frame, text="打开 PDF", command=self.open_pdf,
                                     font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.open_button.grid(row=0, column=0, pady=20)

        self.next_button = tk.Button(self.button_frame, text="下一页", command=self.next_page,
                                     font=("Arial", 12), bg="#FF9800", fg="white", padx=10, pady=5, state=tk.DISABLED)
        self.next_button.grid(row=0, column=2, pady=20)

        self.prev_button = tk.Button(self.button_frame, text="上一页", command=self.prev_page,
                                     font=("Arial", 12), bg="#FF9800", fg="white", padx=10, pady=5, state=tk.DISABLED)
        self.prev_button.grid(row=0, column=1, pady=20)

        self.reload_button = tk.Button(self.button_frame, text="重新加载 PDF", command=self.reload_pdf,
                                       font=("Arial", 12), bg="#FF5722", fg="white", padx=10, pady=5, state=tk.DISABLED)
        self.reload_button.grid(row=0, column=3, pady=20)

        self.form_button = tk.Button(self.button_frame, text="解析表单", command=self.parse_forms,
                                     font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5, state=tk.DISABLED)
        self.form_button.grid(row=1, column=0, pady=20)

        self.cmap_button = tk.Button(self.button_frame, text="提取字体 CMap", command=self.extract_cmap,
                                     font=("Arial", 12), bg="#FF5722", fg="white", padx=20, pady=5, state=tk.DISABLED)
        self.cmap_button.grid(row=1, column=1, pady=20)

        # 文件历史
        self.history_button = tk.Button(self.button_frame, text="显示历史文件", command=self.show_history,
                                        font=("Arial", 12), bg="#607D8B", fg="white", padx=10, pady=5)
        self.history_button.grid(row=1, column=2, pady=20)

        # 添加提取图像按钮
        self.extract_image_button = tk.Button(self.button_frame, text="提取图像", command=self.extract_image,
                                              font=("Arial", 12), bg="#8BC34A", fg="white", padx=10, pady=5,
                                              state=tk.DISABLED)
        self.extract_image_button.grid(row=1, column=3, pady=20)

        # 页面指示器显示当前页和总页数
        self.page_indicator = tk.Label(self.button_frame, text="页码：0/0", font=("Arial", 12), bg="#f7f7f7", pady=10)
        self.page_indicator.grid(row=0, column=4, padx=20)

        # 显示文本的标签
        self.image_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 10))
        self.image_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.current_viewer = None
        self.doc = None

    def load_history(self):
        """加载文件历史"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return [line.strip() for line in f.readlines()]
        return []

    def save_history(self, file_path):
        """保存文件路径到历史记录中"""
        if file_path not in self.recent_files:
            self.recent_files.append(file_path)
            with open(self.history_file, "a") as f:
                f.write(file_path + "\n")

    def show_history(self):
        """显示历史文件供用户选择"""
        if self.recent_files:
            # 列出最近的文件
            recent_files_str = "\n".join([f"{i + 1}. {file}" for i, file in enumerate(self.recent_files)])
            choice = simpledialog.askinteger("选择历史文件", f"请选择一个历史文件（输入编号）：\n{recent_files_str}")
            if choice and 1 <= choice <= len(self.recent_files):
                file_path = self.recent_files[choice - 1]
                self.open_pdf(file_path)
            else:
                messagebox.showinfo("历史文件", "无效的选择")
        else:
            messagebox.showinfo("历史文件", "没有历史文件记录")

    def open_pdf(self, file_path=None):
        """打开 PDF 文件"""
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                fd = open(file_path, "rb")
                self.doc = PDFDocument(fd)
                self.current_viewer = SimplePDFViewer(fd)
                self.current_page_num = 0
                self.total_pages = len(list(self.doc.pages()))

                self.save_history(file_path)  # 保存到历史记录

                self.update_page_view()

                # 激活分页和解析按钮
                self.next_button.config(state=tk.NORMAL)
                self.prev_button.config(state=tk.NORMAL)
                self.form_button.config(state=tk.NORMAL)
                self.cmap_button.config(state=tk.NORMAL)
                self.extract_image_button.config(state=tk.NORMAL)  # 激活提取图像按钮
                self.reload_button.config(state=tk.NORMAL)  # 激活重新加载按钮

            except Exception as e:
                messagebox.showerror("错误", f"无法打开 PDF: {str(e)}")
        else:
            messagebox.showwarning("警告", "未选择 PDF 文件")

    def reload_pdf(self):
        """重新加载 PDF 内容"""
        self.update_page_view()

    def next_page(self):
        """显示下一页"""
        try:
            if self.current_page_num < self.total_pages - 1:
                self.current_page_num += 1
                self.current_viewer.render()
                self.update_page_view()
            else:
                messagebox.showinfo("结束", "已经到达最后一页")
        except StopIteration:
            messagebox.showinfo("结束", "已经到达最后一页")

    def prev_page(self):
        """显示上一页"""
        try:
            if self.current_page_num > 0:
                self.current_page_num -= 1
                self.current_viewer.render()
                self.update_page_view()
            else:
                messagebox.showinfo("开始", "已经到达第一页")
        except Exception as e:
            messagebox.showerror("错误", f"无法显示上一页: {str(e)}")

    def update_page_view(self):
        """更新当前页的显示内容和页码"""
        if self.current_viewer:
            try:
                self.current_viewer.render()
            except Exception as e:
                messagebox.showerror("渲染错误", f"无法渲染页面: {str(e)}")
                return

            # 获取 PDF markdown 内容
            markdown = self.current_viewer.canvas.text_content

            # 使用正则表达式提取括号中的文本
            extracted_text = re.findall(r'\((.*?)\) Tj', markdown)

            # 将提取的文本拼接成完整的字符串
            plain_text = "".join(extracted_text)

            if not plain_text:
                plain_text = "该页没有可显示的文本内容。"

            self.image_label.config(image='', text=f"第 {self.current_page_num + 1} 页内容:\n{plain_text}")
            self.page_indicator.config(text=f"页码：{self.current_page_num + 1}/{self.total_pages}")

    def parse_forms(self):
        """解析 Form XObjects 表单"""
        try:
            # 渲染页面以确保获取完整资源
            self.current_viewer.render()

            # 检查页面是否有 forms 对象
            if hasattr(self.current_viewer.canvas, 'forms') and self.current_viewer.canvas.forms:
                form_keys = sorted(list(self.current_viewer.canvas.forms.keys()))

                if form_keys:
                    form_text = ""
                    for key in form_keys:
                        form_canvas = self.current_viewer.canvas.forms[key]
                        # 获取表单中的文本
                        form_content = "".join(form_canvas.strings)
                        form_text += f"{key}: {form_content}\n"

                    if form_text:
                        messagebox.showinfo("表单解析结果", f"表单字段: \n{form_text}")
                    else:
                        messagebox.showinfo("表单解析结果", "未找到任何表单内容")
                else:
                    messagebox.showinfo("表单解析结果", "未找到任何表单字段")
            else:
                messagebox.showinfo("表单解析结果", "该页面没有表单字段")
        except Exception as e:
            messagebox.showerror("错误", f"无法解析表单: {str(e)}")

    def extract_cmap(self):
        """提取字体的 CMap"""
        try:
            page = next(self.doc.pages())
            font_resources = page.Resources.Font

            cmap_data = []
            for font_name, font_obj in font_resources.items():
                font = page.Resources.Font[font_name]
                if hasattr(font, 'ToUnicode') and font.ToUnicode:
                    cmap = font.ToUnicode
                    cmap_data.append(cmap.filtered.decode())

            cmap_text = "\n".join(cmap_data)
            messagebox.showinfo("CMap 数据", cmap_text)

        except Exception as e:
            messagebox.showerror("错误", f"无法提取 CMap 数据: {str(e)}")
    def extract_image(self):
        """提取图像"""
        try:
            page = next(self.doc.pages())
            if hasattr(page, 'Resources') and 'XObject' in page.Resources:
                for img_name, xobj_ref in page.Resources.XObject.items():
                    xobj = page.Resources.XObject[img_name]
                    if xobj.Subtype == "Image":
                        pil_image = xobj.to_Pillow()  # 转换为 Pillow 图像
                        image_save_path = f"{img_name}.png"
                        pil_image.save(image_save_path)

                        # 将图像显示在 Tkinter 界面中
                        tk_image = ImageTk.PhotoImage(pil_image)
                        self.image_label.config(image=tk_image, text="")
                        self.image_label.image = tk_image  # 避免图像被垃圾回收

                        messagebox.showinfo("成功", f"图像已保存为 {image_save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法提取图像: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFParserApp(root)
    root.mainloop()
