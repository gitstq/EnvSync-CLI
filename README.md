# 🔄 EnvSync-CLI

> **Lightweight Terminal Environment Configuration Sync Manager**
> **轻量级终端环境配置同步管理工具**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()
[![Zero Dependencies](https://img.shields.io/badge/Zero-Dependencies-brightgreen)]()

---

## 🌐 Language / 语言

- [English](#english)
- [简体中文](#简体中文)
- [繁體中文](#繁體中文)

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**EnvSync-CLI** is a lightweight, zero-dependency command-line tool designed to help developers manage and synchronize their environment configuration files across multiple devices. Whether you're switching between your work laptop, home desktop, or a fresh VM, EnvSync ensures your `.bashrc`, `.vimrc`, `.gitconfig`, and other dotfiles are always in sync.

**Key Differentiators:**
- 🚀 **Zero Dependencies** - Pure Python standard library, no pip installs required
- 🔒 **Built-in Encryption** - Protect sensitive configs like SSH keys and API tokens
- 📄 **Template Engine** - Conditional configs based on OS, username, or custom variables
- 💾 **Auto Backup** - Never lose your original configs with automatic backups
- 🎨 **Beautiful TUI** - Colorful terminal output with progress bars and tables

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔄 **Bidirectional Sync** | Sync from system → storage or storage → system |
| 🔒 **Simple Encryption** | XOR-based encryption for sensitive files |
| 📄 **Template Support** | `{{ variable }}` substitution with conditional blocks |
| 💾 **Auto Backup** | Automatic `.backup` files before overwriting |
| 📊 **Diff & Status** | Compare system files with stored versions |
| 🎯 **Exclude Patterns** | Skip logs, caches, and other temporary files |
| 🌈 **Colored Output** | Beautiful terminal UI with emoji indicators |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- Git (for cloning)

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/EnvSync-CLI.git
cd EnvSync-CLI

# Install (optional - can also run directly)
pip install -e .
```

#### Basic Usage

```bash
# Initialize a new project
envsync init my-dotfiles --description "My development environment"

# Add files to sync
envsync add ~/.bashrc
envsync add ~/.vimrc
envsync add ~/.gitconfig
envsync add ~/.ssh/config --encrypt --description "SSH config (encrypted)"

# Sync system files to storage
envsync sync-out

# View sync status
envsync status

# Sync storage back to system (on another machine)
envsync sync-in
```

### 📖 Detailed Usage Guide

#### Adding Files

```bash
# Basic add
envsync add ~/.bashrc

# With encryption
envsync add ~/.ssh/config --encrypt

# With template processing
envsync add ~/.bashrc --template

# With custom description
envsync add ~/.vimrc --description "Vim configuration"
```

#### Template Variables

Create dynamic configs that adapt to different systems:

```bash
# Set variables
envsync set-var editor "vim"
envsync set-var theme "dark"
```

In your config file (e.g., `.bashrc`):
```bash
# {{#if os_name == "Linux" }}
alias ls='ls --color=auto'
# {{/if}}
# {{#if os_name == "Darwin" }}
alias ls='ls -G'
# {{/if}}
export EDITOR={{ editor }}
```

#### Encryption

```bash
# Set password
envsync set-password my_secure_password

# Add encrypted file
envsync add ~/.aws/credentials --encrypt

# Sync (files will be encrypted in storage)
envsync sync-out
```

#### Dry Run

Preview changes without applying them:

```bash
envsync sync-out --dry-run
envsync sync-in --dry-run
```

### 💡 Design Philosophy

**Why EnvSync?**

Existing dotfiles managers like `yadm`, `vcsh`, or `home-manager` are powerful but often overkill for simple use cases. They require learning new concepts, complex setup, or specific ecosystems (like Nix).

EnvSync fills the gap with:
- **Simplicity**: Get started in under 30 seconds
- **Portability**: Single Python file, runs anywhere
- **Safety**: Automatic backups prevent data loss
- **Flexibility**: Templates adapt configs to any environment

### 📦 Deployment

```bash
# Install from source
pip install -e .

# Or run without installing
python3 -m envsync.cli --help
```

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feat/amazing-feature`
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**EnvSync-CLI** 是一款轻量级、零依赖的命令行工具，专为帮助开发者在多台设备之间管理和同步环境配置文件而设计。无论你是在工作笔记本、家用台式机还是全新的虚拟机之间切换，EnvSync 都能确保你的 `.bashrc`、`.vimrc`、`.gitconfig` 等 dotfiles 始终保持同步。

**核心差异化亮点：**
- 🚀 **零依赖** - 纯 Python 标准库实现，无需 pip 安装任何包
- 🔒 **内置加密** - 保护 SSH 密钥、API Token 等敏感配置
- 📄 **模板引擎** - 基于操作系统、用户名或自定义变量的条件配置
- 💾 **自动备份** - 自动创建 `.backup` 文件，永不丢失原始配置
- 🎨 **精美 TUI** - 彩色终端输出，支持进度条和表格

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔄 **双向同步** | 支持系统 → 存储 和 存储 → 系统 双向同步 |
| 🔒 **简单加密** | 基于 XOR 的轻量级文件加密 |
| 📄 **模板支持** | `{{ variable }}` 变量替换，支持条件块 |
| 💾 **自动备份** | 覆盖前自动创建备份文件 |
| 📊 **差异对比** | 对比系统文件与存储版本 |
| 🎯 **排除模式** | 自动跳过日志、缓存等临时文件 |
| 🌈 **彩色输出** | 精美终端 UI，带 Emoji 指示器 |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- Git（用于克隆仓库）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/EnvSync-CLI.git
cd EnvSync-CLI

# 安装（可选 - 也可以直接运行）
pip install -e .
```

#### 基础用法

```bash
# 初始化新项目
envsync init my-dotfiles --description "我的开发环境"

# 添加需要同步的文件
envsync add ~/.bashrc
envsync add ~/.vimrc
envsync add ~/.gitconfig
envsync add ~/.ssh/config --encrypt --description "SSH 配置（加密）"

# 将系统文件同步到存储
envsync sync-out

# 查看同步状态
envsync status

# 在另一台机器上将存储同步回系统
envsync sync-in
```

### 📖 详细使用指南

#### 添加文件

```bash
# 基础添加
envsync add ~/.bashrc

# 加密添加
envsync add ~/.ssh/config --encrypt

# 启用模板处理
envsync add ~/.bashrc --template

# 添加描述
envsync add ~/.vimrc --description "Vim 配置"
```

#### 模板变量

创建能够适应不同系统的动态配置：

```bash
# 设置变量
envsync set-var editor "vim"
envsync set-var theme "dark"
```

在配置文件中（例如 `.bashrc`）：
```bash
# {{#if os_name == "Linux" }}
alias ls='ls --color=auto'
# {{/if}}
# {{#if os_name == "Darwin" }}
alias ls='ls -G'
# {{/if}}
export EDITOR={{ editor }}
```

#### 加密功能

```bash
# 设置密码
envsync set-password my_secure_password

# 添加加密文件
envsync add ~/.aws/credentials --encrypt

# 同步（文件将在存储中加密）
envsync sync-out
```

#### 试运行

预览更改而不实际应用：

```bash
envsync sync-out --dry-run
envsync sync-in --dry-run
```

### 💡 设计思路

**为什么选择 EnvSync？**

现有的 dotfiles 管理工具如 `yadm`、`vcsh` 或 `home-manager` 功能强大，但对于简单用例往往过于复杂。它们需要学习新概念、复杂的设置或特定的生态系统（如 Nix）。

EnvSync 填补了以下空白：
- **简单性**：30 秒内即可上手
- **可移植性**：单文件 Python，随处可运行
- **安全性**：自动备份防止数据丢失
- **灵活性**：模板让配置适应任何环境

### 📦 打包与部署

```bash
# 从源码安装
pip install -e .

# 或不安装直接运行
python3 -m envsync.cli --help
```

### 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m 'feat: 添加 amazing feature'`
4. 推送到分支：`git push origin feat/amazing-feature`
5. 创建 Pull Request

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 項目介紹

**EnvSync-CLI** 是一款輕量級、零依賴的命令列工具，專為幫助開發者在多台裝置之間管理和同步環境設定檔而設計。無論你是在工作筆記型電腦、家用桌上型電腦還是全新的虛擬機之間切換，EnvSync 都能確保你的 `.bashrc`、`.vimrc`、`.gitconfig` 等 dotfiles 始終保持同步。

**核心差異化亮點：**
- 🚀 **零依賴** - 純 Python 標準庫實作，無需 pip 安裝任何套件
- 🔒 **內建加密** - 保護 SSH 金鑰、API Token 等敏感設定
- 📄 **模板引擎** - 基於作業系統、使用者名稱或自訂變數的條件設定
- 💾 **自動備份** - 自動建立 `.backup` 檔案，永不遺失原始設定
- 🎨 **精美 TUI** - 彩色終端輸出，支援進度條和表格

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔄 **雙向同步** | 支援系統 → 儲存 和 儲存 → 系統 雙向同步 |
| 🔒 **簡單加密** | 基於 XOR 的輕量級檔案加密 |
| 📄 **模板支援** | `{{ variable }}` 變數替換，支援條件區塊 |
| 💾 **自動備份** | 覆蓋前自動建立備份檔案 |
| 📊 **差異比對** | 比對系統檔案與儲存版本 |
| 🎯 **排除模式** | 自動跳過日誌、快取等暫存檔案 |
| 🌈 **彩色輸出** | 精美終端 UI，帶 Emoji 指示器 |

### 🚀 快速開始

#### 環境要求
- Python 3.8 或更高版本
- Git（用於複製倉庫）

#### 安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/EnvSync-CLI.git
cd EnvSync-CLI

# 安裝（可選 - 也可以直接執行）
pip install -e .
```

#### 基礎用法

```bash
# 初始化新專案
envsync init my-dotfiles --description "我的開發環境"

# 添加需要同步的檔案
envsync add ~/.bashrc
envsync add ~/.vimrc
envsync add ~/.gitconfig
envsync add ~/.ssh/config --encrypt --description "SSH 設定（加密）"

# 將系統檔案同步到儲存
envsync sync-out

# 查看同步狀態
envsync status

# 在另一台機器上將儲存同步回系統
envsync sync-in
```

### 📖 詳細使用指南

#### 添加檔案

```bash
# 基礎添加
envsync add ~/.bashrc

# 加密添加
envsync add ~/.ssh/config --encrypt

# 啟用模板處理
envsync add ~/.bashrc --template

# 添加描述
envsync add ~/.vimrc --description "Vim 設定"
```

#### 模板變數

建立能夠適應不同系統的動態設定：

```bash
# 設定變數
envsync set-var editor "vim"
envsync set-var theme "dark"
```

在設定檔案中（例如 `.bashrc`）：
```bash
# {{#if os_name == "Linux" }}
alias ls='ls --color=auto'
# {{/if}}
# {{#if os_name == "Darwin" }}
alias ls='ls -G'
# {{/if}}
export EDITOR={{ editor }}
```

#### 加密功能

```bash
# 設定密碼
envsync set-password my_secure_password

# 添加加密檔案
envsync add ~/.aws/credentials --encrypt

# 同步（檔案將在儲存中加密）
envsync sync-out
```

#### 試運行

預覽變更而不實際應用：

```bash
envsync sync-out --dry-run
envsync sync-in --dry-run
```

### 💡 設計理念

**為什麼選擇 EnvSync？**

現有的 dotfiles 管理工具如 `yadm`、`vcsh` 或 `home-manager` 功能強大，但對於簡單用例往往過於複雜。它們需要學習新概念、複雜的設定或特定的生態系統（如 Nix）。

EnvSync 填補了以下空白：
- **簡單性**：30 秒內即可上手
- **可攜性**：單檔案 Python，隨處可執行
- **安全性**：自動備份防止資料遺失
- **靈活性**：模板讓設定適應任何環境

### 📦 打包與部署

```bash
# 從原始碼安裝
pip install -e .

# 或不安裝直接執行
python3 -m envsync.cli --help
```

### 🤝 貢獻指南

1. Fork 本倉庫
2. 建立功能分支：`git checkout -b feat/amazing-feature`
3. 提交變更：`git commit -m 'feat: 新增 amazing feature'`
4. 推送到分支：`git push origin feat/amazing-feature`
5. 建立 Pull Request

### 📄 開源協議

本專案採用 MIT 協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

## 💡 設計思路與迭代規劃

### 技術選型原因
- **Python 標準庫**：確保零依賴，任何有 Python 的環境都能直接執行
- **XOR 加密**：輕量級加密方案，足夠保護基本敏感資訊，無需額外加密庫
- **JSON 配置**：人類可讀、易於版本控制、支援巢狀結構
- **Pathlib**：現代化的路徑處理，跨平台相容性更好

### 後續功能迭代計劃
- [ ] Git 整合：直接將配置同步到 Git 倉庫
- [ ] 雲端儲存：支援 S3、Google Drive 等雲端後端
- [ ] 差異合併：互動式解決檔案衝突
- [ ] 外掛系統：允許使用者擴充套件同步前後的 Hook
- [ ] GUI 介面：基於 TUI 的圖形化操作介面

### 社群貢獻方向
- 翻譯：支援更多語言版本
- 模板：貢獻常用配置模板
- 測試：增加更多邊界案例測試
- 文件：完善使用教學和最佳實踐

---

<p align="center">
  Made with ❤️ by EnvSync Team
</p>
