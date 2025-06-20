# PRPD数据可视化工具

## 项目简介

PRPD（Phase Resolved Partial Discharge）数据可视化工具是一个基于PySide6和Matplotlib开发的图形界面应用程序，用于可视化和分析局部放电PRPD数据。该工具支持2D和3D视图显示，提供单文件处理和批量处理功能，并允许用户自定义显示参数和保存高质量图像。
![image](https://github.com/user-attachments/assets/a8c9bafd-9e71-4d33-a169-4029ead9ec34)
![image](https://github.com/user-attachments/assets/eb65c70f-4b56-41ec-870f-736632f931a9)
![image](https://github.com/user-attachments/assets/b0632485-1405-4f3d-b0cc-cb43876e7897)
![image](https://github.com/user-attachments/assets/04fcbd31-2e05-440c-b6ee-a7b7b52d3287)
![image](https://github.com/user-attachments/assets/1453768c-9198-4f20-839e-29d00c30f2b7)
![image](https://github.com/user-attachments/assets/5e0511e1-3e5a-4d61-9553-eea3e9184be1)


## 功能特点

### 单文件处理
- 加载并显示单个PRPD数据文件
- 支持2D和3D视图切换
- 提供多种颜色方案选择
- 可调整图像保存的DPI
- 一键保存当前显示的图像

### 批量处理
- 支持多个PRPD文件的批量处理
- 可选择输出目录
- 批处理参数独立设置（视图模式、颜色方案、DPI）
- 多线程处理，避免界面卡顿
- 实时显示处理进度和状态
- 自动生成图片文件名（格式：原始文件名_视图模式.png）

### 用户界面
- 选项卡分离单文件处理和批处理功能
- 状态栏显示操作信息
- 进度条显示批处理进度
- 中文界面，支持中文字符显示
- 直观友好的操作界面

## 安装步骤

### 依赖项
本工具依赖以下Python库：
- Python 3.6+
- PySide6
- Matplotlib
- NumPy
- Pandas

### 安装依赖
```bash
pip install PySide6 matplotlib numpy pandas
```

### 字体配置
为了正确显示中文，程序使用了SimHei字体。如果您的系统中没有此字体，可能需要：
1. 安装相应的中文字体
2. 或修改代码中的字体设置：
```python
plt.rcParams['font.sans-serif'] = ['您系统中支持中文的字体名称']
```

## 使用说明

### 启动程序
```bash
python PRPD_GUI.py
```

### 单文件处理
1. 点击"单文件处理"选项卡
2. 点击"打开PRPD文件"按钮选择CSV格式的PRPD数据文件
3. 选择视图模式（2D或3D）
4. 选择颜色方案
5. 设置保存DPI（默认300）
6. 点击"应用设置"按钮更新显示
7. 点击"保存图像"按钮保存当前图像

### 批量处理
1. 点击"批量处理"选项卡
2. 点击"添加文件"按钮选择多个CSV格式的PRPD数据文件
3. 选择批处理的视图模式、颜色方案和DPI
4. 点击"选择输出目录"按钮设置保存路径
5. 点击"开始批处理"按钮开始处理
6. 等待处理完成，状态栏和进度条会显示处理进度

### 批量处理图片命名规则
批量处理时，保存的图片名称会自动根据原始文件名生成，格式为：
- `原始文件名_视图模式.png`

例如：
- 原始文件：`corona3_PRPD.csv`，2D视图 → 保存为：`corona3_PRPD_2D.png`
- 原始文件：`test_data.csv`，3D视图 → 保存为：`test_data_3D.png`

所有图片将保存在用户选择的输出目录中。

## 数据格式要求

输入的CSV文件应为PRPD数据矩阵，不需要包含表头。数据矩阵的：
- 行表示电压百分比（0-100%）
- 列表示相位角度（0-360°）
- 矩阵值表示放电幅值

## 常见问题

### 中文显示为方块
如果图像中的中文显示为方块，请确保您的系统中安装了SimHei字体或修改代码中的字体设置。

### 3D图像显示不完整
3D图像可能需要更大的显示空间，可以尝试调整窗口大小或保存图像后查看。

### 批处理速度慢
批处理速度取决于文件大小和数量，以及计算机性能。处理大量文件时，请耐心等待。

## 开发信息

- 开发语言：Python
- GUI框架：PySide6
- 绘图库：Matplotlib
- 数据处理：NumPy, Pandas
- 多线程：QThread

## 许可证

本项目采用MIT许可证。详细信息请参见LICENSE文件。 
