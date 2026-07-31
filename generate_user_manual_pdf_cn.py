#!/usr/bin/env python3
"""
Generate a professional, high-fidelity 5-page Chinese PDF User Manual for PLaser.
Configures Matplotlib to use Microsoft YaHei or SimHei for perfect Chinese character rendering.
"""

from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Configure matplotlib for Chinese rendering on Windows
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Setup paths
PLASER_DIR = Path(__file__).resolve().parent
output_pdf_path = PLASER_DIR / "PLaser_User_Manual_CN.pdf"
assets_dir = PLASER_DIR / "docs" / "manual_assets"

# Theme Colors matching the PLaser Dashboard
BG_COLOR = "#0a192f"
PANEL_COLOR = "#172a45"
ACCENT_GREEN = "#64ffda"
ACCENT_RED = "#ff7b72"
TEXT_COLOR = "#ffffff"
MUTED_TEXT = "#8892b0"

def add_header(ax, title):
    ax.text(0.05, 0.95, "PLASER 二极管激光器 EDA 仿真套件", color=ACCENT_GREEN, fontsize=10, fontweight="bold", alpha=0.8)
    ax.text(0.05, 0.91, title, color=TEXT_COLOR, fontsize=15, fontweight="bold")
    ax.plot([0.05, 0.95], [0.89, 0.89], color="#233554", transform=ax.transAxes, linewidth=1.5)

def add_footer(ax, page_num):
    ax.plot([0.05, 0.95], [0.08, 0.08], color="#233554", transform=ax.transAxes, linewidth=1.0)
    ax.text(0.05, 0.05, "© 2026 万振文 (AI + 仿真专家). 保留所有权利。", color=MUTED_TEXT, fontsize=8)
    ax.text(0.90, 0.05, f"第 {page_num} 页", color=MUTED_TEXT, fontsize=9)

def draw_paragraph(ax, text, x, y, max_len=45, line_height=0.021, color="#e6f1ff", fontsize=9.2):
    # Chinese characters take more visual width, so limit characters per line to max_len
    lines = []
    curr_line = ""
    for char in text:
        if len(curr_line) < max_len:
            curr_line += char
        else:
            lines.append(curr_line)
            curr_line = char
    if curr_line:
        lines.append(curr_line)
        
    for line in lines:
        ax.text(x, y, line, color=color, fontsize=fontsize, transform=ax.transAxes, alpha=0.9)
        y -= line_height
    return y

def embed_image(fig, img_path, left, bottom, w, h):
    if img_path.exists():
        img = plt.imread(str(img_path))
        img_ax = fig.add_axes([left, bottom, w, h], facecolor="none")
        img_ax.imshow(img)
        img_ax.axis("off")
    else:
        img_ax = fig.add_axes([left, bottom, w, h], facecolor=PANEL_COLOR)
        img_ax.text(0.5, 0.5, f"未找到资源图片:\n{img_path.name}", color=ACCENT_RED, ha='center', va='center')
        img_ax.axis("off")

# Initialize PDF compilation
with PdfPages(str(output_pdf_path)) as pdf:
    # ====================================================
    # Page 1: Cover Page
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    # Techy background accent lines
    ax.plot([0, 1], [0.85, 0.85], color=PANEL_COLOR, linewidth=3)
    ax.plot([0, 1], [0.15, 0.15], color=PANEL_COLOR, linewidth=3)
    
    # Title
    ax.text(0.1, 0.68, "PLaser", color=ACCENT_GREEN, fontsize=54, fontweight="bold")
    ax.text(0.1, 0.58, "基于物理信息神经网络的\n激光二极管 EDA 仿真套件", color=TEXT_COLOR, fontsize=24, fontweight="bold", linespacing=1.3)
    ax.text(0.1, 0.50, "光-电-热三维有源区参数优化与纵向性能剖面实时分析平台", color=MUTED_TEXT, fontsize=12, style="italic")
    
    # Highlight box
    ax.text(0.1, 0.38, " 用户手册与技术参考指南 (中文版) ", color=ACCENT_GREEN, fontsize=11, fontweight="bold", bbox=dict(boxstyle="square,pad=0.5", facecolor=PANEL_COLOR, edgecolor=ACCENT_GREEN, linewidth=1))
    
    # Meta Details
    ax.text(0.1, 0.28, "适用群体:", color=MUTED_TEXT, fontsize=9, fontweight="bold")
    ax.text(0.1, 0.25, "激光器腔体设计人员、光电工程师及科研合作人员", color=TEXT_COLOR, fontsize=10.5)
    
    ax.text(0.1, 0.20, "作者与服务范围:", color=MUTED_TEXT, fontsize=9, fontweight="bold")
    ax.text(0.1, 0.17, "万振文 (AI + 仿真专家  |  服务：定制化 PINN 求解器研发)", color=TEXT_COLOR, fontsize=10)
    
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 2: Device Architecture & Mapping (4 Panels)
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "1. 器件架构与求解器映射")
    
    y = 0.84
    # Panel 1
    ax.text(0.05, y, "面板 1: 物理器件装配 (14引脚蝶形封装与激光二极管芯片)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p1_txt = (
        "在光纤通信中，边发射半导体激光器集成于标准的14引脚蝶形封装中。该封装内置激光芯片（见图a）、"
        "热电制冷器（TEC）、温度监测热敏电阻等。芯片本身是生长在磷化铟（InP）衬底上的微米级半导体结构，"
        "通过条形电极注入电流，在多量子阱（MQW）有源区激发增益，限制模式并在解理镜面间形成干涉振荡出射。"
    )
    y = draw_paragraph(ax, p1_txt, 0.05, y)
    
    # Panel 2
    y -= 0.01
    ax.text(0.05, y, "面板 2: 过渡热沉 (热沉装配与热耗散)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p2_txt = (
        "为避免高功率运行下的热衰退，芯片以p面朝下方式贴装在铜或碳化硅过渡热沉上。此视图代表封装的"
        "横截面（x-y平面，从镜面看去）。它展示了热量从MQW区通过p接触层流向过渡热沉的散热路径。"
        "底部设定为恒定环境温度T0，提供散热边界的冷端汇点。"
    )
    y = draw_paragraph(ax, p2_txt, 0.05, y)

    # Panel 3
    y -= 0.01
    ax.text(0.05, y, "面板 3: 2D 横向模型 (2D Elmer FEM 横截面求解器)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p3_txt = (
        "横截面（垂直于传播方向，见图b）决定光限制与限制因子。Elmer FEM在横向上求解耦合泊松方程（静电势）、"
        "漂移扩散方程（载流子）、矢量亥姆霍兹方程（波导模式分布）以及晶格热传导方程。物理坐标网格区间"
        "[-6,6]x[0,4.23]微米被直接映射为视口中的x_app=y_Elmer和y_app=z_Elmer-2微米（平移有源区到零点）。"
    )
    y = draw_paragraph(ax, p3_txt, 0.05, y)

    # Panel 4
    y -= 0.01
    ax.text(0.05, y, "面板 4: 1D 纵向腔 (1D 纵向腔体架构)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p4_txt = (
        "沿传播z轴（平行于传播方向，见图c），前/后向光波包络在镜面反射。在非对称腔面镀膜中（R1~90%, R2~5%），"
        "光功率向前镜呈指数增高。功率激增使前镜附近的载流子由于激射而被剧烈消耗，形成空间烧孔（SHB）"
        "载流子纵向耗尽 dip 结构。模型在此有源区传播线上将其离散为51点计算网格，求解耦合速率方程。"
    )
    y = draw_paragraph(ax, p4_txt, 0.05, y)
    
    # Embed three parallel slicing images
    embed_image(fig, assets_dir / "3d_live_laser_chip.jpg", 0.05, 0.14, 0.28, 0.16)
    embed_image(fig, assets_dir / "3d_transparent_transverse_slice.jpg", 0.36, 0.14, 0.28, 0.16)
    embed_image(fig, assets_dir / "3d_transparent_longitudinal_slice.jpg", 0.67, 0.14, 0.28, 0.16)
    ax.text(0.5, 0.10, "图 1.1: 将三维物理芯片 (a) 切片分解为 2D 横向 (b) 与 1D 纵向 (c) 仿真模型示意图", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 2)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 3: Application View Modes (2 Modes)
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "2. 软件运行模式与可视化仪表盘")
    
    y = 0.84
    # View Mode 1
    ax.text(0.05, y, "运行模式 1: 多物理场综合仪表盘", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    m1_txt = (
        "提供全局耦合的多物理场扫参视图。左侧边栏包括设计滑块（反射率R1/R2、腔长L、冷却温度T0、"
        "注入电流）。右侧主显示面板包括六个同步的性能视口：纵向载流子N(z)分布曲线、纵向光功率P(z)曲线、"
        "2D横向波导模场形状、2D截面温度场图，以及波导横向/纵向中心切面的光强分布图。同时具有指示当前激射"
        "终端工作状态、转换效率WPE、终端电流与激射功率的卡片面板。"
    )
    y = draw_paragraph(ax, m1_txt, 0.05, y)
    
    # View Mode 2
    y -= 0.015
    ax.text(0.05, y, "运行模式 2: 3D 腔内物理场分析仪", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    m2_txt = (
        "专用于详尽检查沿腔体 z 轴的局部横截面状态。左侧边栏切换为腔体 z 截面位置选择滑块，并带有一张"
        "输出该位置局部 N(z) 和 P(z) 状态的简易卡片。右侧面板展示当前 z位置处的 2D 模场与 2D 温度分布"
        "切片，同时在下方横向对比地展示侧面（x-z平面）激射场光强三维空间包络与腔体三维温度扩散地貌。"
    )
    y = draw_paragraph(ax, m2_txt, 0.05, y)
    
    # Embed annotated dashboard screenshot
    embed_image(fig, assets_dir / "dashboard_annotated.png", 0.05, 0.12, 0.90, 0.28)
    ax.text(0.5, 0.11, "图 2.1: 多物理场综合仪表盘窗口（展示六个耦合物理输出视口与性能指标）", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 3)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 4: Installation & Onboarding Guide
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "3. 安装与本地新手上门指南")
    
    y = 0.84
    # 3.1 Environment Setup
    ax.text(0.05, y, "3.1 本地环境搭建与软件启动步骤", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    setup_txt = (
        "推荐在较浅磁盘目录（避免路径超出系统上限）下配置独立 Python 虚拟环境：\n"
        "  git clone https://github.com/ZhenwenWan/PLaser.git\n"
        "  cd PLaser\n"
        "  python -m venv .venv\n"
        "  .\\.venv\\Scripts\\Activate.ps1   # 激活 Windows PowerShell 环境\n"
        "  pip install -r requirements.txt\n\n"
        "使用自带的预训练神经网络权重在本地浏览器中直接拉起前端界面：\n"
        "  python -m streamlit run app.py"
    )
    y = draw_paragraph(ax, setup_txt, 0.05, y, max_len=60)
    
    # 3.2 Optional tasks
    y -= 0.015
    ax.text(0.05, y, "3.2 可选的额外执行任务", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    tasks_txt = (
        "• 重新扫参生成数据集: python generate_dataset.py  [包含1500组算例光电热计算]\n"
        "• 重新训练物理神经网络: python train_pinn.py  [拟合数据与有源区连续方程约束]\n"
        "• 重新渲染扫参演示视频: python generate_animation.py  [使用OpenCV渲染MP4视频]"
    )
    y = draw_paragraph(ax, tasks_txt, 0.05, y, max_len=60)
    
    # 3.3 Troubleshooting Table
    y -= 0.015
    ax.text(0.05, y, "3.3 故障排除与常见问题解决", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    
    table_data = [
        ["故障现象", "可能原因", "解决方案"],
        ["ModuleNotFoundError", "Python虚拟环境未成功激活", "运行激活脚本，重新执行 requirements 依赖安装"],
        ["Streamlit Model Missing", "权重文件 pt 或 npz 丢失", "执行 python train_pinn.py 重新训练并保存 pt 模型"],
        ["WinError 206 路径超限", "Windows 路径字符超出上限", "将 PLaser 整体移至浅盘符，例如 C:\\PLaser 后执行"],
        ["MP4 生成失败", "OpenCV 缺少 OpenH264 库", "检查 pip 安装 opencv-python 或手动配置 H264 编码组件"]
    ]
    
    table_y = y
    for i, row in enumerate(table_data):
        row_color = ACCENT_GREEN if i == 0 else "#ffffff"
        font_wt = "bold" if i == 0 else "normal"
        if i == 0:
            rect = plt.Rectangle((0.05, table_y - 0.005), 0.90, 0.025, facecolor=PANEL_COLOR, transform=ax.transAxes)
            ax.add_patch(rect)
        
        ax.text(0.06, table_y, row[0], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.26, table_y, row[1], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.54, table_y, row[2], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        table_y -= 0.035
        
    add_footer(ax, 4)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 5: Verification & Validation
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "4. 算法性能与精度验证指标")
    
    y = 0.84
    ax.text(0.05, y, "4.1 计算延迟与传统数值求解器耗时对比", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    
    # Speed table
    speed_data = [
        ["求解器模式", "计算耗时 (Latency)", "R² 精度系数", "EDA流程中的角色"],
        ["Elmer 2D FEM", "12 - 25 秒", "1.000 (参考基准)", "求解横向截面波导模式与温度"],
        ["2.5D 纵向射击求解器", "1.2 - 2.8 秒", "1.000 (参考基准)", "用于数据集的批量离线产生"],
        ["PLaser PINN 代理模型", "小于 5 毫秒", "大于 0.997", "提供实时交互式的无缝扫参"]
    ]
    
    table_y = y
    for i, row in enumerate(speed_data):
        row_color = ACCENT_GREEN if i == 0 else "#ffffff"
        font_wt = "bold" if i == 0 else "normal"
        if i == 0:
            rect = plt.Rectangle((0.05, table_y - 0.005), 0.90, 0.025, facecolor=PANEL_COLOR, transform=ax.transAxes)
            ax.add_patch(rect)
        
        ax.text(0.06, table_y, row[0], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.26, table_y, row[1], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.48, table_y, row[2], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.68, table_y, row[3], color=row_color, fontsize=8.5, fontweight=font_wt, transform=ax.transAxes)
        table_y -= 0.03
        
    y = table_y - 0.015
    ax.text(0.05, y, "4.2 独立验证集对齐散点图与 PINN 物理损失收敛曲线", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    val_txt = (
        "算法精度验证散点图展示出极高的线性度。反向传播优化过程强制执行有源区内的载流子速率平衡，"
        "使得数据均方根误差（MSE）和物理连续性损失（Continuity Loss）均成功收敛了 6 个数量级。"
    )
    y = draw_paragraph(ax, val_txt, 0.05, y)
    
    # Embed validation plots
    embed_image(fig, assets_dir / "validation_scatter_power.png", 0.05, 0.12, 0.50, 0.22)
    embed_image(fig, assets_dir / "pinn_training_loss.svg", 0.58, 0.12, 0.37, 0.22)
    
    ax.text(0.30, 0.10, "图 4.1: 预测值 vs. 求解器真实值的散点对齐图", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    ax.text(0.76, 0.10, "图 4.2: 神经网络物理损失收敛过程", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 5)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

print(f"Compilation complete. Chinese PDF User Manual saved to {output_pdf_path}")
