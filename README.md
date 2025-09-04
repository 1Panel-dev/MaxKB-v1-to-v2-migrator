# MaxKB v1到v2迁移工具

## 迁移路线
```sh
____________________________________________________________________________________________________________________
|                   v1                     |      this  migrator     |                      v2                     |
|                                          |                         |                                             |
|                                          |                         |                                             |
|  --------              ---------------   |           --------      |         ---------               ----------  |
|  | v1.* |~~(upgrade)~~>| v1.10.10-lts |~~(export)~~> | data | ~~(import)~~>| v2.1.0 |~~(upgrade)~~>| >v2.1.0 |   |  
|  --------              ---------------   |           --------      |         ---------               ----------  |
|                                          |                         |                                             |
|                                          |                         |                                             |
|                                          |                         |                                             |
--------------------------------------------------------------------------------------------------------------------
```
如上图所示，v1.10.10-lts之前的版本先升级到v1.10.10-lts，然后使用迁移工具迁移到v2.1.0，再升级到更高的版本。  
❗ 重要：此工具不是升级工具，是迁移工具，用以迁移v1的数据到v2 。  
❗ 重要：此工具只支持 v1.10.10-lts 的数据迁移到 v2.1.0 。

## 迁移操作步骤

### Linux/macOS 系统

1. **导出v1数据**
   ```bash
   # 在v1机器上下载v1-to-v2-migrator
   cd v1-to-v2-migrator
   bash export_v1_data.sh <v1_container_name>

   # 执行后v1-to-v2-migrator中会多一个migrate.zip
   # 将v1-to-v2-migrator复制到v2所在的机器上
   ```

2. **数据导入至v2**
   ```bash
   # 在v2机器上，确保v2.1.0版本的容器已经启动, 专业版和企业版需要在启动后手动导入license
   cd v1-to-v2-migrator
   bash import_v2_data.sh <v2_container_name>
   ```

### Windows 系统

Windows 系统提供了批处理文件(.bat)和 PowerShell 脚本(.ps1)两种版本，推荐使用 PowerShell 版本。

1. **导出v1数据**
   ```powershell
   # PowerShell 版本（推荐）
   .\export_v1_data.ps1 -ContainerName <v1_container_name>
   
   # 或者使用批处理版本
   export_v1_data.bat <v1_container_name>
   ```

2. **数据导入至v2**
   ```powershell
   # PowerShell 版本（推荐）
   .\import_v2_data.ps1 -ContainerName <v2_container_name>
   
   # 或者使用批处理版本
   import_v2_data.bat <v2_container_name>
   ```

详细的 Windows 使用说明请参考：[README_Windows.md](README_Windows.md)

## FAQ
- v1.10.10-lts之前的版本可以直接迁移到v2么？  
答：不可以，必须升级到v1.10.10-lts之后再迁移。

- 可以直接迁移到v2.2.0版本么?  
答：不可以，必须先迁移到v2.1.0，再升级到v2.2.0。

- 可以迁移到已有数据的v2.1.0版本么？     
答：不可以，v2.1.0的环境必须是空环境。

- 社区版可以迁移到专业版么？  
答：不可以，v1社区版只能迁移到v2社区版，v1专业版只能迁移到v2专业版，且v1和v2的专业版必须有有效的license许可。


