import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import time
import os
import random
import re
from urllib.parse import urljoin
import socket
import datetime
import threading
import concurrent.futures

# 全局变量控制任务中断
zhongduan_caozuo = False

# 爬取函数
def paqu_wangzhi(wangzhi, cunfang_mulu, jindu_wenben, zhuangtai_biaoqian):
    if zhongduan_caozuo:
        return  # 如果用户取消任务，则直接退出

    toubu = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'close'
    }
    chongshi_cishu = 3

    for chongshi in range(chongshi_cishu):
        if zhongduan_caozuo:
            return  # 如果用户取消任务，则直接退出

        try:
            socket.setdefaulttimeout(10)
            fanhui = requests.get(wangzhi, headers=toubu, timeout=10)
            fanhui.raise_for_status()

            neirong = BeautifulSoup(fanhui.content, 'html.parser')
            biaoti = neirong.title.string.strip() if neirong.title and neirong.title.string else "无标题"
            biaoti = re.sub(r'[\\/*?:"<>|]', "", biaoti)

            lianjie = []
            for link in neirong.find_all('a'):
                href = link.get('href')
                if href:
                    quanzhong_lianjie = urljoin(wangzhi, href)
                    lianjie.append(quanzhong_lianjie)

            zhengwen = neirong.get_text()

            wenjianming = os.path.join(cunfang_mulu, f"{biaoti}.txt")
            with open(wenjianming, 'w', encoding='utf-8') as wenjian:
                wenjian.write(f"URL: {wangzhi}\n")
                wenjian.write(f"标题: {biaoti}\n")
                wenjian.write(f"内容:\n{zhengwen}\n")
                wenjian.write(f"链接:\n")
                for lianjie_danwei in lianjie:
                    wenjian.write(f"{lianjie_danwei}\n")

            jindu_wenben.insert(tk.END, f"成功爬取：{wangzhi}\n")
            jindu_wenben.yview(tk.END)
            return

        except requests.exceptions.RequestException as cuowu:
            jindu_wenben.insert(tk.END, f"爬取 {wangzhi} 失败 (第 {chongshi+1} 次尝试)：{cuowu}\n")
            jindu_wenben.yview(tk.END)
            time.sleep(random.randint(2, 5))
        except socket.timeout as cuowu:
            jindu_wenben.insert(tk.END, f"爬取 {wangzhi} 超时 (第 {chongshi+1} 次尝试)：{cuowu}\n")
            jindu_wenben.yview(tk.END)
            time.sleep(random.randint(2, 5))
        except Exception as cuowu:
            jindu_wenben.insert(tk.END, f"发生未知错误：{cuowu}\n")
            jindu_wenben.yview(tk.END)
            return

    jindu_wenben.insert(tk.END, f"爬取 {wangzhi} 失败，达到最大重试次数\n")
    jindu_wenben.yview(tk.END)

# 启动爬取的函数，用于后台线程运行
def qidong_paqu(zhuangtai_biaoqian):
    global zhongduan_caozuo
    zhongduan_caozuo = False  # 重置停止标志

    wangzhi_shuru = wangzhi_wenben.get("1.0", tk.END).strip()
    if not wangzhi_shuru:
        messagebox.showwarning("输入为空", "请输入要爬取的网址！")
        return

    wangzhi_liebiao = wangzhi_shuru.splitlines()
    cunfang_mulu = mulu_shuru.get()
    if not os.path.exists(cunfang_mulu):
        os.makedirs(cunfang_mulu)  # 如果目录不存在则创建

    qishi_shijian = time.time()
    zhuangtai_biaoqian.config(text="正在爬取...", fg="orange")  # 更新状态标签

    qidong_anniu.config(state=tk.DISABLED)  # 禁用开始按钮

    # 使用 ThreadPoolExecutor 实现多线程爬取
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as zhixing:
        renwu = [zhixing.submit(paqu_wangzhi, wangzhi.strip(), cunfang_mulu, jindu_wenben, zhuangtai_biaoqian) for wangzhi in wangzhi_liebiao if wangzhi.strip()]
        concurrent.futures.wait(renwu)  # 等待所有爬取任务完成

    jieshu_shijian = time.time()
    if not zhongduan_caozuo:
        jindu_wenben.insert(tk.END, f"爬取完成，耗时：{jieshu_shijian - qishi_shijian:.2f} 秒\n")
        jindu_wenben.yview(tk.END)
        zhuangtai_biaoqian.config(text="爬取完成", fg="green")  # 更新状态标签
    else:
        jindu_wenben.insert(tk.END, "爬取已被用户取消。\n")
        jindu_wenben.yview(tk.END)
        zhuangtai_biaoqian.config(text="爬取已取消", fg="red")

# 启动爬取线程
def qidong_paqu_xiancheng():
    xiancheng = threading.Thread(target=qidong_paqu, args=(zhuangtai_biaoqian,))
    xiancheng.daemon = True
    xiancheng.start()

# 停止爬取
def zhongzhi_paqu():
    global zhongduan_caozuo
    zhongduan_caozuo = True
    zhuangtai_biaoqian.config(text="正在取消爬取...", fg="red")

# 选择保存目录
def xuanze_cunfang_mulu():
    wenjianjia = filedialog.askdirectory()
    if wenjianjia:
        mulu_shuru.delete(0, tk.END)
        mulu_shuru.insert(0, wenjianjia)

# 创建UI界面
zhujiemian = tk.Tk()
zhujiemian.title("网页爬虫")

# 设置窗口大小
zhujiemian.geometry("600x450")

# 输入网址框
tk.Label(zhujiemian, text="请输入要爬取的网址，每行一个：").pack(pady=5)
wangzhi_wenben = tk.Text(zhujiemian, height=6, width=70)
wangzhi_wenben.pack(pady=5)

# 选择保存目录
tk.Label(zhujiemian, text="请选择保存目录：").pack(pady=5)
mulu_shuru = tk.Entry(zhujiemian, width=50)
mulu_shuru.pack(pady=5)
xuanze_anniu = tk.Button(zhujiemian, text="选择目录", command=xuanze_cunfang_mulu)
xuanze_anniu.pack(pady=5)

# 开始爬取和停止按钮
anniu_kuang = tk.Frame(zhujiemian)
anniu_kuang.pack(pady=10)

qidong_anniu = tk.Button(anniu_kuang, text="开始爬取", command=qidong_paqu_xiancheng)
qidong_anniu.grid(row=0, column=0, padx=10)

zhongzhi_anniu = tk.Button(anniu_kuang, text="停止爬取", command=zhongzhi_paqu)
zhongzhi_anniu.grid(row=0, column=1, padx=10)

# 状态标签
zhuangtai_biaoqian = tk.Label(zhujiemian, text="准备爬取", fg="blue")
zhuangtai_biaoqian.pack(pady=5)

# 显示日志进度的Text框
jindu_wenben = tk.Text(zhujiemian, height=10, width=70)
jindu_wenben.pack(pady=5)

# 运行主循环
zhujiemian.mainloop()
