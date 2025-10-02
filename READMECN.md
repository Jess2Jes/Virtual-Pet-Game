[英文](README.md) | 中文  
# 🐾 虚拟宠物游戏  

一个基于控制台的虚拟宠物游戏，采用面向对象编程 (OOP) 构建。  

## 📖 概述
- 用户系统：支持注册和登录  
- 多种宠物（猫、兔子、恐龙、龙、Pou）  
- 宠物照料：喂食、洗澡、治疗、睡觉、散步、玩耍、对话  
- 商店系统：使用游戏内货币购买物品  
- 成长阶段：幼年 → 少年 → 成年 → 老年  
- 影响生存的属性：快乐、饥饿、理智、健康、肥胖度、能量  

## ✨ 功能
- *用户*：身份验证与货币管理  
- *宠物*：随机初始属性、成长系统、不同阶段的 ASCII 艺术图案  
- *互动*：喂食、洗澡、散步、使用药水等  
- *商店*：食物、香皂、药水及其效果  
- *状态界面*：在命令行界面显示格式化的状态信息  
- *时间*：内置游戏时钟与天数计数  

## 📂 项目结构
- main.py – 程序入口，菜单与会话状态  
- game.py – 游戏循环，宠物互动逻辑  
- pet.py – VirtualPet 类，属性、成长、共享库存  
- animal.py – 各宠物子类（猫、兔、恐龙、龙、Pou），含 ASCII 艺术  
- formatter.py – 文本截断与状态框格式化  
- shop.py – 物品目录与购买逻辑  
- user.py – 用户注册、验证与货币管理  

详细文档请参见 [docs/structureCN.md](docs/structureCN.md)  

## 🎮 运行游戏

1. 安装 *Python 3.x*。  
2. 克隆或 fork 仓库：  
   ```bash
   git clone https://github.com/Jess2Jes/Virtual-Pet-Game.git
   cd Virtual-Pet-Game
3. 运行 python main.py

## 🚀 开发计划

- 保存/加载宠物与用户数据（JSON、pickle 或数据库）  
- 图形界面（Tkinter、PyQT，或基于 Flask/FastAPI 的网页版本）  
- 更多宠物与 ASCII 动画  
- 迷你游戏与事件系统  
- 多人/社交互动功能  
- 单元测试与架构重构（服务/模型分层）  

## 👥 作者与贡献者

- [Jess2Jes](https://github.com/Jess2Jes) — 项目负责人 & 主开发者  
- [Hans](https://github.com/Dendroculus) — 贡献者  
- [StevNard](https://github.com/StevNard) — 贡献者  


apakah bisa dipahami
