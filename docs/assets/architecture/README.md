# 架构图源文件

[云帆项目架构](yunfan-ontology-agent-system-evolution.mmd)采用 Mermaid 文本格式，展示事实关联、模式选择、规则检查和业务执行的关系。Read 在返回事实后结束；Draft 生成建议；Write 继续检查并执行动作。

阅读入口：[架构说明](../../architecture.md) · [十站目录](../../book-map.md)。架构说明已内嵌可在 GitHub 显示的 Mermaid 图，学习和运行项目无需安装绘图工具。

需要编辑或导出图片时，可以把 `.mmd` 文件交给支持 Mermaid 的编辑器。若已安装 Mermaid CLI，也可以在仓库根目录运行：

```bash
mmdc -i docs/assets/architecture/yunfan-ontology-agent-system-evolution.mmd \
  -o artifacts/yunfan-architecture.svg -b white
```

导出文件保存在本地 `artifacts/`。修改后同步[架构说明](../../architecture.md)中的 Mermaid 图。来源连接器、身份认证和持久化的实现范围也在该文说明。
