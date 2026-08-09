<div align="center">

[English](README.md) | [Indonesian](READMEID.md) | 中文

</div>

<div align="center">

# 🐾 虚拟宠物游戏

</div>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.x-blue.svg" />
  <img alt="概念" src="https://img.shields.io/badge/概念-面向对象_%26_继承-blueviolet.svg" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img alt="状态" src="https://img.shields.io/badge/status-已完成-brightgreen.svg" />
</p>

一款基于控制台的虚拟宠物模拟游戏，使用 Python 的面向对象编程（OOP）构建。选择一只宠物，给它起名，并在它成长的不同阶段照顾它。管理状态、与它互动玩耍，让它保持健康与快乐！

---

## 🎮 游戏玩法演示

整个游戏在终端中运行，为宠物的不同生命阶段提供详细的状态框与迷人的 ASCII 艺术。

**创建你自己的独特宠物：**
```text
───────────────────────────────── Create Your Own Pet ─────────────────────────────────────────
Name your pet: Mochi
─────────────────────────────────────────────────────────────────────────────────────────────────
Here's five types of species you can choose:
1. Cat
2. Rabbit
3. Dinosaur
4. Dragon
5. Pou
─────────────────────────────────────────────────────────────────────────────────────────────────
Choose his/her species (input type of species here): cat

─────────────────────────────────────────────────────────────────────────────────────────────────
Mochi, a cat, has born!
─────────────────────────────────────────────────────────────────────────────────────────────────
```

**看着它成长，并欣赏每个生命阶段独特的艺术风格：**
```text
==================================================================================================

/|、      ......
(˚ˎ 。7  . miw! .
 |、˜〵   ......
じしˍ,)ノ
~~~~~~~~~~~~~~~
```

**通过详细的状态面板跟踪它的需求：**

<img src="assets/pet_stats.png" alt="宠物状态面板" />

---

## ✨ 核心功能

- **多样化且不断进化的宠物**：从 5 个物种中选择（**猫、兔子、恐龙、龙、Pou**），并体验它们的成长阶段（**婴儿、青少年、成年、老年**），每个阶段都有独特 ASCII 艺术。
- **深度宠物模拟**：管理状态属性，例如 **饥饿、理智、快乐、健康、肥胖、精力**。忽视需求可能导致宠物进入危险状态。
- **互动式照料系统**：
  - **喂食**、**洗澡**、**玩耍**、**交谈**、**散步**、**睡觉**
- **游戏内经济与商店**：通过与宠物互动赚取游戏货币，用于购买食物、肥皂和特殊药水。
- **用户认证系统**：支持注册、登录与更改密码，并包含基础的验证规则。
- **时间系统**：通过游戏内时间/天数推进，宠物状态会随着时间被动变化，需要持续照顾。

---

## 🛠️ 技术展示

- **面向对象编程（OOP）设计**：围绕核心模块构建（`game`、`pet`、`user`、`shop`）。
- **继承与多态**：不同物种基于基础宠物模型实现，并拥有独特行为与 ASCII 艺术。
- **模块化结构**：功能与工具被拆分到不同文件/目录中，便于维护与扩展。

---

## 🚀 开始使用

### 先决条件
- Python 3.x

### 安装与运行

1. 克隆仓库
```bash
git clone https://github.com/Jess2Jes/Virtual-Pet-Game.git
cd Virtual-Pet-Game
```

2. 运行游戏
```bash
python main.py
```

3. 按照屏幕提示注册用户并开始游戏。

---

## 📂 项目结构

（基于当前仓库结构）

```bash
Virtual-Pet-Game/
├── assets/
│   └── pet_stats.png
├── constants/
│   ├── arts/
│   │   ├── cat.py
│   │   ├── dino.py
│   │   ├── dragon.py
│   │   ├── pou.py
│   │   ├── rabbits.py
│   │   └── animalsArt.py
│   └── configs.py
├── datas/
│   ├── conversations.json
│   ├── jokes.json
│   └── words.txt
├── docs/
├── features/
│   ├── minigame/
│   ├── animal.py
│   ├── game.py
│   ├── memento.py
│   ├── pet.py
│   ├── save_manager.py
│   ├── shop.py
│   └── user.py
├── program_testing/
├── saves/
│   └── player_saves.json
├── utils/
├── main.py
├── README.md
├── READMEID.md
├── READMECN.md
└── LICENSE
```

---

## 🗺️ 发展蓝图

- **持久化**：改进存档系统（或迁移到 SQLite）。
- **GUI 实现**：使用 Tkinter / PyQT 制作图形界面版本。
- **更多内容**：新增更多物种、物品与随机事件。
- **迷你游戏**：扩展迷你游戏与奖励系统。
- **测试**：添加单元测试与 CI，提升稳定性。

---

## 👥 作者与贡献者

<table border="0" cellspacing="10" cellpadding="5">
  <tr>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/Jess2Jes">
        <img src="https://github.com/Jess2Jes.png" width="100" height="100" alt="Jess2Jes" style="border-radius: 50%;"/>
      </a>
      <br/>
      <a href="https://github.com/Jess2Jes">Jessica Gunawan</a>
    </td>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/Yoruxyv">
        <img src="https://github.com/Yoruxyv.png" width="100" height="100" alt="Hans" style="border-radius: 50%;"/>
      </a>
      <br/>
      <a href="https://github.com/Yoruxyv">Hans Valerie</a>
    </td>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/StevNard">
        <img src="https://github.com/StevNard.png" width="100" height="100" alt="StevNard"/>
      </a>
      <br/>
      <a href="https://github.com/StevNard">Steven Lienardi</a>
    </td>
  </tr>
</table>

---

## 📜 许可证

本项目采用 MIT 许可证，详情请查看 [`LICENSE`](LICENSE)。