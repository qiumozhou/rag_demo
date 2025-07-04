# RAG 智能问答系统

基于检索增强生成(RAG)技术的智能问答系统，结合文档检索和大语言模型，为用户提供准确、相关的知识问答服务。

## ✨ 功能特性

### 🔍 智能检索
- 基于语义相似度的文档检索
- 支持多种文档格式 (PDF、DOCX、TXT、MD)
- 自动文本分块和向量化存储
- 可配置的检索参数和相似度阈值

### 🤖 生成回答
- 结合检索结果与语言模型生成回答
- 置信度评估和响应时间统计
- 引用来源展示和可追溯性
- 支持批量查询处理

### 📚 文档管理
- 拖拽上传文档功能
- 文档预览和内容管理
- 文档统计和类型分析
- 支持文档删除和知识库清空

### ⚙️ 系统配置
- 模型参数调优
- 检索策略配置
- 主题和语言设置
- 系统状态监控

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI** - 高性能Web框架
- **Python** - 主要开发语言
- **LangChain** - LLM应用开发框架
- **ChromaDB** - 向量数据库
- **Sentence Transformers** - 文本嵌入模型
- **PyPDF2/python-docx** - 文档解析

### 前端技术栈
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 前端构建工具
- **Element Plus** - Vue 3组件库
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端安装

1. 安装Python依赖
```bash
pip install -r requirements.txt
```

2. 启动后端服务
```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 前端安装

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

## 📖 使用指南

### 1. 文档上传
- 访问"文档管理"页面
- 点击"上传文档"按钮
- 拖拽或选择文档文件
- 系统将自动处理和向量化文档

### 2. 智能问答
- 进入"智能问答"页面
- 在输入框中输入问题
- 系统将检索相关文档并生成回答
- 查看引用来源和置信度

### 3. 系统配置
- 访问"系统设置"页面
- 调整模型参数和检索配置
- 保存设置以优化系统性能

## 🔧 配置说明

### 模型配置
```python
# 嵌入模型
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

# 语言模型
llm_model_name = "microsoft/DialoGPT-medium"

# 上下文长度
max_context_length = 4000
```

### 检索配置
```python
# 文档分块大小
chunk_size = 1000
chunk_overlap = 200

# 检索参数
top_k = 5
similarity_threshold = 0.7
```

## 📁 项目结构

```
rag-system/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务服务
│   └── main.py             # 应用入口
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json        # 前端依赖
├── data/                   # 数据目录
│   ├── chroma/             # 向量数据库
│   └── uploads/            # 上传文件
└── README.md               # 项目说明
```

## 🛠️ API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/upload` | 上传文档 |
| POST | `/api/v1/query` | 智能问答 |
| GET | `/api/v1/documents` | 获取文档列表 |
| GET | `/api/v1/status` | 系统状态 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |

## 🔄 系统流程

1. **文档处理流程**
   ```
   文档上传 → 文本提取 → 分块处理 → 向量化 → 存储到ChromaDB
   ```

2. **问答流程**
   ```
   用户问题 → 向量检索 → 相关文档 → LLM生成 → 返回答案
   ```

## 🎯 性能优化

### 检索优化
- 调整chunk_size和chunk_overlap参数
- 优化相似度阈值设置
- 启用重排序功能

### 模型优化
- 选择合适的嵌入模型
- 调整温度参数控制随机性
- 配置合理的上下文长度

## 📝 开发说明

### 添加新功能
1. 后端: 在`app/api/endpoints.py`中添加新的API端点
2. 前端: 在`src/views/`中创建新页面组件
3. 状态管理: 在`src/stores/`中添加相应的store

### 自定义模型
1. 在`app/core/config.py`中配置模型路径
2. 更新`app/services/rag_service.py`中的模型加载逻辑

## 🐛 常见问题

### Q: 文档上传失败
A: 检查文件格式和大小是否符合要求，确保后端服务正常运行

### Q: 检索结果不准确
A: 尝试调整相似度阈值，或增加更多相关文档到知识库

### Q: 系统响应慢
A: 检查模型加载状态，考虑使用更轻量的模型或优化硬件配置

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) - 句子嵌入模型
- [Vue.js](https://vuejs.org/) - 前端框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库

## 📞 联系方式

如有问题或建议，请提交Issue或联系开发团队。

---

**RAG智能问答系统** - 让知识检索更智能，让问答更准确！ 