# Windows 脚本使用说明

本项目现在支持 Windows 系统，提供了PowerShell脚本(.ps1)。

## 脚本文件说明

### PowerShell 脚本 (.ps1)
- `export_v1_data.ps1` - v1数据导出脚本（PowerShell版本）
- `import_v2_data.ps1` - v2数据导入脚本（PowerShell版本）


### 使用 PowerShell 脚本（推荐）

#### 1. 导出 v1 数据
```powershell
.\export_v1_data.ps1 -ContainerName <v1_container_name>
```

示例：
```powershell
.\export_v1_data.ps1 -ContainerName maxkb
```

#### 2. 导入到 v2
```powershell
.\import_v2_data.ps1 -ContainerName <v2_container_name>
```

示例：

如果无法执行 PowerShell 脚本，可能需要修改执行策略：

### 临时修改（推荐）
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### 永久修改（管理员权限）
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

## 功能特性

### PowerShell 版本 (.ps1)
- 更好的错误处理机制
- 彩色输出，更易阅读
- 参数验证
- 更详细的状态信息
- 现代化的脚本结构

## 前置条件

1. 已安装 Docker Desktop for Windows
2. MaxKB v1 和 v2 容器正在运行
3. 对于 PowerShell 脚本，需要 PowerShell 5.0 或更高版本

## 故障排除

### 常见问题

1. **容器未运行**
   ```cmd
   docker ps
   ```
   检查容器状态

2. **权限不足**
   - 确保 Docker Desktop 正在运行
   - 以管理员身份运行终端（如果需要）
   - 使用完整路径运行脚本

4. **文件路径问题**
   - 确保在包含迁移工具的目录中运行脚本
   - 检查 migrate.zip 文件是否存在

### 调试模式

对于 PowerShell 脚本，可以添加调试信息：
```powershell
$VerbosePreference = "Continue"
.\export_v1_data.ps1 -ContainerName maxkb -Verbose
```

## 注意事项

1. 确保在包含迁移工具的目录中运行脚本
2. 导入前确保已成功导出数据（migrate.zip 文件存在）
3. 导入完成后建议重启 v2 容器
4. 备份重要数据，以防迁移过程中出现问题

## 支持的操作系统

- Windows 10
- Windows 11
- Windows Server 2016 及以上版本
