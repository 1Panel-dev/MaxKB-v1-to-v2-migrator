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

1. **查找容器名称**
   ```bash
   docker ps  # 查看运行中的容器
   ```

2. **复制迁移工具到 v1 容器**
   ```bash
   docker cp . <v1_container_name>:/opt/maxkb/v1-to-v2-migrator
   ```

3. **在 v1 容器中导出数据**
   ```bash
   docker exec -w /opt/maxkb/v1-to-v2-migrator <v1_container_name> python migrate.py export
   ```

4. **复制数据到主机**
   ```bash
   docker cp <v1_container_name>:/opt/maxkb/v1-to-v2-migrator/migrate.zip ./migrate.zip
   ```

5. **复制工具和数据到 v2 容器**
   ```bash
   docker cp . <v2_container_name>:/opt/maxkb-app/v1-to-v2-migrator
   docker cp ./migrate.zip <v2_container_name>:/opt/maxkb-app/v1-to-v2-migrator/
   ```

6. **在 v2 容器中导入数据**
   ```bash
   docker exec -w /opt/maxkb/v1-to-v2-migrator <v2_container_name> python migrate.py import
   ```


## FAQ
- v1.10.10-lts之前的版本可以直接迁移到v2么？  
答：不可以，必须升级到v1.10.10-lts之后再迁移。
- 可以直接迁移到v2.2.0版本么?  
答：不可以，必须先迁移到v2.1.0，再升级到v2.2.0。
- 社区版可以迁移到专业版么？  
答：不可以，v1社区版只能迁移到v2社区版，v1专业版只能迁移到v2专业版，且v1和v2的专业版必须有有效的license许可。


***
## 内部讨论
需要特殊处理的地方：  
知识库中的图片url需要替换成v2的api url

待定问题：  
用户自己添加的本地向量模型是否自动迁移，还是需要用户自己手动迁移？  
迁移后知识库是否需要重新向量化？
