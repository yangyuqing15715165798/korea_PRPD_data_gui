import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                             QMessageBox, QGroupBox, QComboBox, QSpinBox,
                             QFormLayout, QTabWidget, QRadioButton, QButtonGroup,
                             QListWidget, QStatusBar, QProgressBar)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D

# 设置默认字体为SimHei（或其他支持中文的字体）
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号"-"显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False

class BatchProcessThread(QThread):
    """用于批处理PRPD文件的线程"""
    progress = Signal(int)
    status = Signal(str)
    finished_one = Signal(str, str)  # 文件路径, 保存路径
    
    def __init__(self, file_list, save_dir, color_scheme, dpi, view_mode):
        super().__init__()
        self.file_list = file_list
        self.save_dir = save_dir
        self.color_scheme = color_scheme
        self.dpi = dpi
        self.view_mode = view_mode
        
    def run(self):
        total = len(self.file_list)
        for i, file_path in enumerate(self.file_list):
            try:
                # 更新进度
                self.progress.emit(int((i / total) * 100))
                self.status.emit(f"处理文件 {i+1}/{total}: {os.path.basename(file_path)}")
                
                # 读取数据
                df = pd.read_csv(file_path, header=None)
                
                # 创建颜色方案
                custom_cmap = LinearSegmentedColormap.from_list('custom', self.color_scheme)
                
                # 创建图像
                fig = Figure(figsize=(10, 6), dpi=100)
                
                if self.view_mode == "2D":
                    ax = fig.add_subplot(111)
                    img = ax.imshow(df.values, cmap=custom_cmap, origin='lower', 
                                extent=[0, 360, 0, 100], aspect='auto')
                    ax.set_title('2D PRPD图')
                    ax.set_xlabel('相位 (°)')
                    ax.set_ylabel('电压 (%)')
                    ax.set_xticks(np.arange(0, 361, 90))
                    ax.set_yticks(np.arange(0, 101, 25))
                    fig.colorbar(img, ax=ax)
                else:
                    ax = fig.add_subplot(111, projection='3d')
                    x = np.arange(0, 360, 360/df.shape[1])
                    y = np.arange(0, 100, 100/df.shape[0])
                    X, Y = np.meshgrid(x, y)
                    Z = df.values
                    surf = ax.plot_surface(X, Y, Z, cmap=custom_cmap, 
                                        linewidth=0, antialiased=False)
                    ax.set_title('3D PRPD图')
                    ax.set_xlabel('相位 (°)')
                    ax.set_ylabel('电压 (%)')
                    ax.set_zlabel('幅值')
                    ax.view_init(elev=30, azim=45)
                    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
                
                fig.tight_layout()
                
                # 创建保存路径
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(self.save_dir, f"{filename}_{self.view_mode}.png")
                
                # 保存图像
                fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close(fig)
                
                # 发送完成信号
                self.finished_one.emit(file_path, save_path)
                
            except Exception as e:
                self.status.emit(f"处理文件失败: {os.path.basename(file_path)} - {str(e)}")
        
        self.progress.emit(100)
        self.status.emit("批处理完成")

class MatplotlibCanvas(FigureCanvas):
    """用于在Qt中嵌入Matplotlib的画布类"""
    def __init__(self, parent=None, width=10, height=6, dpi=100, is_3d=False):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if is_3d:
            self.axes = self.fig.add_subplot(111, projection='3d')
        else:
            self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)

class PRPDVisualizer(QMainWindow):
    """PRPD数据可视化工具的主窗口"""
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.canvas = None
        self.current_df = None
        self.view_mode = "2D"  # 默认为2D视图
        self.batch_files = []  # 批处理文件列表
        
        # 预定义颜色方案
        self.color_schemes = {
            "默认方案": ['#000000', '#FFFFFE', '#FFFF13', '#FF0000'],
            "蓝绿红": ['#0000FF', '#00FFFF', '#00FF00', '#FF0000'],
            "黑蓝紫": ['#000000', '#0000FF', '#800080', '#FF00FF'],
            "绿黄红": ['#006400', '#7FFF00', '#FFFF00', '#FF0000']
        }
        
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('PRPD数据可视化工具')
        self.setMinimumSize(1000, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 创建单文件处理选项卡
        self.single_tab = QWidget()
        self.createSingleFileTab()
        
        # 创建批处理选项卡
        self.batch_tab = QWidget()
        self.createBatchTab()
        
        # 添加选项卡
        self.tabs.addTab(self.single_tab, "单文件处理")
        self.tabs.addTab(self.batch_tab, "批量处理")
        
        # 将选项卡添加到主布局
        main_layout.addWidget(self.tabs)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar)
    
    def createSingleFileTab(self):
        """创建单文件处理选项卡"""
        layout = QVBoxLayout(self.single_tab)
        
        # 创建上部控制区域
        top_layout = QHBoxLayout()
        
        # 创建按钮组
        button_group = QGroupBox("文件操作")
        button_layout = QHBoxLayout()
        
        # 创建按钮
        self.open_button = QPushButton("打开PRPD文件")
        self.save_button = QPushButton("保存图像")
        self.save_button.setEnabled(False)  # 初始禁用保存按钮
        
        # 添加按钮到布局
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_group.setLayout(button_layout)
        
        # 创建参数设置组
        param_group = QGroupBox("参数设置")
        param_layout = QFormLayout()
        
        # 创建视图模式选择
        view_mode_layout = QHBoxLayout()
        self.view_mode_group = QButtonGroup(self)
        self.view_2d_radio = QRadioButton("2D视图")
        self.view_3d_radio = QRadioButton("3D视图")
        self.view_2d_radio.setChecked(True)
        self.view_mode_group.addButton(self.view_2d_radio, 1)
        self.view_mode_group.addButton(self.view_3d_radio, 2)
        view_mode_layout.addWidget(self.view_2d_radio)
        view_mode_layout.addWidget(self.view_3d_radio)
        
        # 创建颜色方案选择
        self.color_scheme_combo = QComboBox()
        for scheme in self.color_schemes.keys():
            self.color_scheme_combo.addItem(scheme)
        
        # 创建DPI设置
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(72, 600)
        self.dpi_spinbox.setValue(300)
        self.dpi_spinbox.setSingleStep(50)
        
        # 添加参数控件到布局
        param_layout.addRow("视图模式:", view_mode_layout)
        param_layout.addRow("颜色方案:", self.color_scheme_combo)
        param_layout.addRow("保存DPI:", self.dpi_spinbox)
        
        # 创建应用按钮
        self.apply_button = QPushButton("应用设置")
        self.apply_button.setEnabled(False)
        param_layout.addRow(self.apply_button)
        
        param_group.setLayout(param_layout)
        
        # 添加组到顶部布局
        top_layout.addWidget(button_group)
        top_layout.addWidget(param_group)
        
        # 添加文件信息标签
        self.file_info_label = QLabel("未加载文件")
        
        # 创建图像显示区域
        self.plot_container = QVBoxLayout()
        self.plot_widget = QWidget()
        self.plot_widget.setLayout(self.plot_container)
        
        # 将组件添加到布局
        layout.addLayout(top_layout)
        layout.addWidget(self.file_info_label)
        layout.addWidget(self.plot_widget, 1)  # 1表示拉伸因子
        
        # 连接信号和槽
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_image)
        self.apply_button.clicked.connect(self.apply_settings)
        self.view_mode_group.buttonClicked.connect(self.change_view_mode)
    
    def createBatchTab(self):
        """创建批处理选项卡"""
        layout = QVBoxLayout(self.batch_tab)
        
        # 创建上部控制区域
        top_layout = QHBoxLayout()
        
        # 创建文件列表组
        file_group = QGroupBox("文件列表")
        file_layout = QVBoxLayout()
        
        # 创建文件列表
        self.file_list = QListWidget()
        
        # 创建文件操作按钮
        file_buttons_layout = QHBoxLayout()
        self.add_files_button = QPushButton("添加文件")
        self.clear_files_button = QPushButton("清空列表")
        file_buttons_layout.addWidget(self.add_files_button)
        file_buttons_layout.addWidget(self.clear_files_button)
        
        # 添加到文件列表布局
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(file_buttons_layout)
        file_group.setLayout(file_layout)
        
        # 创建批处理设置组
        batch_settings_group = QGroupBox("批处理设置")
        batch_settings_layout = QFormLayout()
        
        # 创建批处理视图模式选择
        batch_view_mode_layout = QHBoxLayout()
        self.batch_view_mode_group = QButtonGroup(self)
        self.batch_view_2d_radio = QRadioButton("2D视图")
        self.batch_view_3d_radio = QRadioButton("3D视图")
        self.batch_view_2d_radio.setChecked(True)
        self.batch_view_mode_group.addButton(self.batch_view_2d_radio, 1)
        self.batch_view_mode_group.addButton(self.batch_view_3d_radio, 2)
        batch_view_mode_layout.addWidget(self.batch_view_2d_radio)
        batch_view_mode_layout.addWidget(self.batch_view_3d_radio)
        
        # 创建批处理颜色方案选择
        self.batch_color_scheme_combo = QComboBox()
        for scheme in self.color_schemes.keys():
            self.batch_color_scheme_combo.addItem(scheme)
        
        # 创建批处理DPI设置
        self.batch_dpi_spinbox = QSpinBox()
        self.batch_dpi_spinbox.setRange(72, 600)
        self.batch_dpi_spinbox.setValue(300)
        self.batch_dpi_spinbox.setSingleStep(50)
        
        # 创建输出目录选择
        self.output_dir_label = QLabel("未选择输出目录")
        self.select_output_dir_button = QPushButton("选择输出目录")
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.output_dir_label, 1)  # 1表示拉伸因子
        output_dir_layout.addWidget(self.select_output_dir_button)
        
        # 添加批处理设置到布局
        batch_settings_layout.addRow("视图模式:", batch_view_mode_layout)
        batch_settings_layout.addRow("颜色方案:", self.batch_color_scheme_combo)
        batch_settings_layout.addRow("保存DPI:", self.batch_dpi_spinbox)
        batch_settings_layout.addRow("输出目录:", output_dir_layout)
        
        # 创建开始批处理按钮
        self.start_batch_button = QPushButton("开始批处理")
        self.start_batch_button.setEnabled(False)
        batch_settings_layout.addRow(self.start_batch_button)
        
        batch_settings_group.setLayout(batch_settings_layout)
        
        # 添加组到顶部布局
        top_layout.addWidget(file_group)
        top_layout.addWidget(batch_settings_group)
        
        # 创建批处理结果标签
        self.batch_result_label = QLabel("未开始批处理")
        
        # 将组件添加到布局
        layout.addLayout(top_layout)
        layout.addWidget(self.batch_result_label)
        
        # 连接信号和槽
        self.add_files_button.clicked.connect(self.add_batch_files)
        self.clear_files_button.clicked.connect(self.clear_batch_files)
        self.select_output_dir_button.clicked.connect(self.select_output_dir)
        self.start_batch_button.clicked.connect(self.start_batch_process)
    
    def open_file(self):
        """打开PRPD数据文件并显示"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开PRPD数据文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.current_file = file_path
                self.file_info_label.setText(f"当前文件: {os.path.basename(file_path)}")
                
                # 读取数据
                self.current_df = pd.read_csv(file_path, header=None)
                
                # 绘制图像
                self.plot_prpd()
                
                # 启用按钮
                self.save_button.setEnabled(True)
                self.apply_button.setEnabled(True)
                
                # 更新状态栏
                self.statusBar.showMessage(f"已加载文件: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")
                self.statusBar.showMessage("加载文件失败")
    
    def get_current_color_scheme(self):
        """获取当前选择的颜色方案"""
        scheme_name = self.color_scheme_combo.currentText()
        return self.color_schemes[scheme_name]
    
    def change_view_mode(self, button):
        """切换视图模式"""
        if button == self.view_2d_radio:
            self.view_mode = "2D"
        else:
            self.view_mode = "3D"
        
        if self.current_df is not None:
            self.plot_prpd()
    
    def plot_prpd(self):
        """绘制PRPD图"""
        if self.current_df is None:
            return
            
        try:
            # 清除之前的图像
            for i in reversed(range(self.plot_container.count())): 
                widget = self.plot_container.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # 获取当前颜色方案
            colors = self.get_current_color_scheme()
            custom_cmap = LinearSegmentedColormap.from_list('custom', colors)
            
            if self.view_mode == "2D":
                # 创建2D画布
                self.canvas = MatplotlibCanvas(self, width=10, height=6, dpi=100, is_3d=False)
                
                # 绘制2D图
                img = self.canvas.axes.imshow(self.current_df.values, cmap=custom_cmap, origin='lower', 
                            extent=[0, 360, 0, 100], aspect='auto')
                self.canvas.axes.set_title('2D PRPD图')
                self.canvas.axes.set_xlabel('相位 (°)')
                self.canvas.axes.set_ylabel('电压 (%)')
                
                # 设置刻度
                self.canvas.axes.set_xticks(np.arange(0, 361, 90))  # 每90度一个刻度
                self.canvas.axes.set_yticks(np.arange(0, 101, 25))  # 每25%一个刻度
                
                # 创建colorbar
                self.canvas.fig.colorbar(img, ax=self.canvas.axes)
            else:
                # 创建3D画布
                self.canvas = MatplotlibCanvas(self, width=10, height=6, dpi=100, is_3d=True)
                
                # 准备3D数据
                x = np.arange(0, 360, 360/self.current_df.shape[1])
                y = np.arange(0, 100, 100/self.current_df.shape[0])
                X, Y = np.meshgrid(x, y)
                Z = self.current_df.values
                
                # 绘制3D图
                surf = self.canvas.axes.plot_surface(X, Y, Z, cmap=custom_cmap, 
                                                    linewidth=0, antialiased=False)
                self.canvas.axes.set_title('3D PRPD图')
                self.canvas.axes.set_xlabel('相位 (°)')
                self.canvas.axes.set_ylabel('电压 (%)')
                self.canvas.axes.set_zlabel('幅值')
                
                # 设置视角
                self.canvas.axes.view_init(elev=30, azim=45)
                
                # 创建colorbar
                self.canvas.fig.colorbar(surf, ax=self.canvas.axes, shrink=0.5, aspect=5)
            
            # 调整布局
            self.canvas.fig.tight_layout()
            
            # 添加到界面
            self.plot_container.addWidget(self.canvas)
            
            # 更新状态栏
            self.statusBar.showMessage(f"已绘制{self.view_mode}图像")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"绘图错误: {str(e)}")
            import traceback
            traceback.print_exc()
            self.statusBar.showMessage("绘图失败")
    
    def apply_settings(self):
        """应用当前参数设置"""
        if self.current_df is not None:
            self.plot_prpd()
    
    def save_image(self):
        """保存当前显示的图像"""
        if not self.current_file or not self.canvas:
            QMessageBox.warning(self, "警告", "没有可保存的图像")
            return
            
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存图像", "", "PNG图像 (*.png);;JPEG图像 (*.jpg);;所有文件 (*)"
        )
        
        if save_path:
            try:
                # 获取当前DPI设置
                dpi = self.dpi_spinbox.value()
                self.canvas.fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
                QMessageBox.information(self, "成功", f"图像已保存到: {save_path}")
                self.statusBar.showMessage(f"图像已保存到: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图像失败: {str(e)}")
                self.statusBar.showMessage("保存图像失败")
    
    def add_batch_files(self):
        """添加批处理文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择PRPD数据文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if file_paths:
            self.batch_files.extend(file_paths)
            self.update_batch_file_list()
            self.check_batch_ready()
    
    def clear_batch_files(self):
        """清空批处理文件列表"""
        self.batch_files = []
        self.update_batch_file_list()
        self.check_batch_ready()
    
    def update_batch_file_list(self):
        """更新批处理文件列表显示"""
        self.file_list.clear()
        for file_path in self.batch_files:
            self.file_list.addItem(os.path.basename(file_path))
        
        # 更新状态栏
        self.statusBar.showMessage(f"批处理文件列表: {len(self.batch_files)}个文件")
    
    def select_output_dir(self):
        """选择批处理输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", ""
        )
        
        if dir_path:
            self.output_dir_label.setText(dir_path)
            self.check_batch_ready()
    
    def check_batch_ready(self):
        """检查批处理是否准备就绪"""
        is_ready = len(self.batch_files) > 0 and self.output_dir_label.text() != "未选择输出目录"
        self.start_batch_button.setEnabled(is_ready)
    
    def start_batch_process(self):
        """开始批处理"""
        # 获取批处理设置
        view_mode = "2D" if self.batch_view_2d_radio.isChecked() else "3D"
        scheme_name = self.batch_color_scheme_combo.currentText()
        color_scheme = self.color_schemes[scheme_name]
        dpi = self.batch_dpi_spinbox.value()
        output_dir = self.output_dir_label.text()
        
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 创建并启动批处理线程
        self.batch_thread = BatchProcessThread(
            self.batch_files, output_dir, color_scheme, dpi, view_mode
        )
        
        # 连接信号
        self.batch_thread.progress.connect(self.update_batch_progress)
        self.batch_thread.status.connect(self.update_batch_status)
        self.batch_thread.finished_one.connect(self.batch_file_processed)
        self.batch_thread.finished.connect(self.batch_process_finished)
        
        # 禁用开始按钮
        self.start_batch_button.setEnabled(False)
        
        # 启动线程
        self.batch_thread.start()
        
        # 更新状态
        self.batch_result_label.setText("批处理进行中...")
    
    def update_batch_progress(self, value):
        """更新批处理进度"""
        self.progress_bar.setValue(value)
    
    def update_batch_status(self, status):
        """更新批处理状态"""
        self.statusBar.showMessage(status)
        self.batch_result_label.setText(status)
    
    def batch_file_processed(self, file_path, save_path):
        """批处理单个文件完成"""
        # 可以在这里添加更多处理逻辑，如更新UI等
        pass
    
    def batch_process_finished(self):
        """批处理完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 启用开始按钮
        self.start_batch_button.setEnabled(True)
        
        # 更新状态
        self.statusBar.showMessage("批处理完成")
        
        # 显示完成消息
        QMessageBox.information(self, "完成", "批处理已完成")

def main():
    app = QApplication(sys.argv)
    window = PRPDVisualizer()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 