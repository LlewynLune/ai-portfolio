# GitHub 建号、建仓与上传指南

当前仓库已经是本地 Git 仓库，但没有远程地址。账号注册、邮箱验证、密码和二次验证需要你本人完成；以下步骤不要求泄露密码给我。

## 第一步：注册 GitHub 账号

1. 打开 https://github.com/signup。
2. 按页面提示填写邮箱、密码和用户名。
3. 完成人机验证和邮箱验证。
4. 登录后先开启二次验证：Settings → Password and authentication → Two-factor authentication。
5. 不要把公司内部项目、文档、截图或数据上传到公开仓库。

用户名建议：稳定、简短、可长期使用；避免临时绰号、岗位级别或带敏感含义的名称。确定用户名后，再替换仓库中的占位符。

## 第二步：创建远程仓库

1. 登录 GitHub 后点击右上角 + → New repository。
2. Repository name 建议先使用 ai-portfolio。
3. 可见性先选择 Private，等内容核验后再改为 Public。
4. 不要勾选 Add a README、.gitignore 或 license；本地已有 README 和 .gitignore，许可证尚未选定。
5. 创建后复制 GitHub 页面给出的远程地址，格式通常类似：
   - HTTPS：https://github.com/你的用户名/ai-portfolio.git
   - SSH：git@github.com:你的用户名/ai-portfolio.git

## 第三步：连接本地仓库

在本仓库根目录执行，把占位符替换为你的真实用户名和远程地址：

```bash
git remote add origin https://github.com/你的用户名/ai-portfolio.git
git branch -M main
git status
```

检查 remote 只用于确认地址，不包含密码：

```bash
git remote -v
```

## 第四步：检查后再提交

```bash
python3 scripts/check_portfolio.py
python3 -m unittest discover -s tests
```

确认没有内部链接、凭证、日志、截图或未授权数据后，先从 GitHub Settings → Emails 获取本人账户的 noreply 提交邮箱。不要默认沿用公司邮箱，也不要把密码当作 HTTPS Git 密码。

```bash
git config --local user.name "你的公开名字"
git config --local user.email "从 GitHub 账户复制的 noreply 邮箱"
```

这些配置只影响本仓库，不更改全局。ZIP 解压不包含 .git，需要先运行 git init -b main，再设置 remote；原始本地项目目录已初始化，不重复初始化。

首次提交：

```bash
git add .
git commit -m "Initialize AI portfolio"
git push -u origin main
```

## 第五步：配置 GitHub Pages（可选）

1. 先完成一个真实项目和公开发布检查。
2. GitHub 仓库页面进入 Settings → Pages。
3. Source 选择 Deploy from a branch。
4. Branch 选择 main、目录选择 /root。
5. 保存后等待 GitHub 生成访问地址。Pages 展示 index.html 与离线实验结果，不运行 Python API；动态重新实验须在本机启动实验台。

GitHub Pages 不是建仓后自动开启；公开后任何人都可能访问，因此不要把未完成内容当成内部草稿。

## 账号同名 Profile README（可选）

另建一个与 GitHub 用户名完全同名的仓库，在其中放 README.md。可先复制 profile/README-template.md 的结构，等你有真实项目后再启用。

## 公开前最低门槛

- 至少一个真实项目，而不是只有模板。
- 每个指标有来源、样本、环境和时间。
- 每个仓库链接可打开，README 能指导运行。
- 所有第三方材料有许可或出处。
- 没有内部链接、凭证、日志、客户信息、内部代码或未公开模型细节。
- 你本人能解释每个文件、指标和失败样本。
