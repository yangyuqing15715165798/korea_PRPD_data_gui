# Git操作问题及解决方案

## 问题一：本地更改与远程更新冲突

### 问题描述
当本地文件有未提交的更改，同时远程仓库也有更新时，执行`git pull`会导致冲突。

```bash
$ git pull origin main
error: Your local changes to the following files would be overwritten by merge:
        README.md
Please commit your changes or stash them before you merge.
Aborting
```

### 解决方案

有三种常用解决方法：

#### 方法一：提交本地更改后再拉取（推荐）

1. 添加更改到暂存区
   ```bash
   git add README.md
   ```

2. 提交更改
   ```bash
   git commit -m "更新README文档，添加应用程序截图"
   ```

3. 拉取远程更改
   ```bash
   git pull origin main
   ```

4. 如有冲突，解决冲突后再次提交

5. 推送到远程仓库
   ```bash
   git push origin main
   ```

#### 方法二：暂存本地更改

1. 暂存当前更改
   ```bash
   git stash
   ```

2. 拉取远程更改
   ```bash
   git pull origin main
   ```

3. 恢复暂存的更改
   ```bash
   git stash pop
   ```

4. 如有冲突，解决冲突后提交
   ```bash
   git add .
   git commit -m "解决冲突并合并更改"
   git push origin main
   ```

#### 方法三：放弃本地更改（谨慎使用）

1. 放弃本地更改
   ```bash
   git restore README.md
   ```
   或
   ```bash
   git checkout -- README.md
   ```

2. 拉取远程更改
   ```bash
   git pull origin main
   ```

## 问题二：网络连接问题

### 问题描述
执行Git远程操作时出现网络连接错误：

```bash
fatal: unable to access 'https://github.com/username/repo.git/': Failed to connect to github.com port 443 after 21172 ms: Couldn't connect to server
```

### 解决方案

1. **检查网络连接**
   - 确保网络连接稳定
   - 尝试访问GitHub网站验证连接

2. **配置代理**（如果使用代理）
   ```bash
   git config --global http.proxy http://proxyserver:port
   ```

3. **更改连接协议**
   - 从HTTPS切换到SSH（如果已配置SSH密钥）
   ```bash
   git remote set-url origin git@github.com:username/repo.git
   ```

4. **增加超时时间**
   ```bash
   git config --global http.lowSpeedLimit 1000
   git config --global http.lowSpeedTime 300
   ```

5. **稍后重试**
   - 有时是GitHub服务器暂时性问题，等待一段时间后再尝试

## 常用Git命令参考

- 查看状态：`git status`
- 添加文件：`git add <文件名>` 或 `git add .`（添加所有）
- 提交更改：`git commit -m "提交信息"`
- 拉取更新：`git pull origin <分支名>`
- 推送更改：`git push origin <分支名>`
- 查看分支：`git branch`
- 切换分支：`git checkout <分支名>` 或 `git switch <分支名>`
- 创建分支：`git branch <新分支名>`
- 创建并切换分支：`git checkout -b <新分支名>`
- 合并分支：`git merge <分支名>`
- 查看日志：`git log`
- 查看简洁日志：`git log --oneline` 