import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

def plot_prpd(file_path, save_path=None):
    """
    仅绘制PRPD数据的2D图，纵轴显示为0-100%，横轴显示为0-360°相位。
    
    参数:
    file_path (str): PRPD数据文件的路径。
    save_path (str, optional): 保存图像的路径，如果为None则不保存。
    """
    # 读取数据
    df = pd.read_csv(file_path, header=None)
    # 创建自定义颜色方案
    #               黑     白         黄         红
    colors = ['#000000', '#FFFFFE', '#FFFF13', '#FF0000']
    custom_cmap = LinearSegmentedColormap.from_list('custom', colors)
    
    # 创建只含2D图的figure
    fig, ax = plt.subplots(figsize=(10,6))
    
    # 绘制2D图
    img = ax.imshow(df.values, cmap=custom_cmap, origin='lower', 
                    extent=[0, 360, 0, 100], aspect='auto')
    ax.set_title('2D PRPD Plot')
    ax.set_xlabel('Phase (°)')
    ax.set_ylabel('Voltage (%)')
    
    # 设置刻度
    ax.set_xticks(np.arange(0, 361, 90))  # 每90度一个刻度
    ax.set_yticks(np.arange(0, 101, 25))  # 每25%一个刻度
    
    # 创建colorbar
    fig.colorbar(img, ax=ax)
    
    # 保存图像（如果指定了保存路径）
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图像已保存到: {save_path}")
    
    plt.show()


#显示保存 设置高分辨率300pi
plot_prpd("D:/韩国设备-局放PRPD图收集/尖端放电/corona3_PRPD.csv",'D:/韩国设备-局放PRPD图收集/尖端放电/corona3_3_PRPD.png')