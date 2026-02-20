import sqlite3
import hashlib
import os
from datetime import datetime

DATABASE_PATH = 'academic_homepage.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 用户表（管理员账户）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 个人信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT,
            bio TEXT,
            avatar_url TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            website TEXT,
            linkedin TEXT,
            github TEXT,
            orcid TEXT,
            research_interests TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 教育背景表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree TEXT NOT NULL,
            institution TEXT NOT NULL,
            field TEXT,
            start_year INTEGER,
            end_year INTEGER,
            description TEXT,
            tags TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 论文表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT NOT NULL,
            journal TEXT,
            year INTEGER,
            volume TEXT,
            pages TEXT,
            doi TEXT,
            url TEXT,
            abstract TEXT,
            keywords TEXT,
            type TEXT DEFAULT 'journal',
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 项目经历表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            detailed_description TEXT,
            role TEXT,
            start_date DATE,
            end_date DATE,
            technologies TEXT,
            url TEXT,
            github_url TEXT,
            status TEXT DEFAULT 'completed',
            tags TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 工作经历表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position TEXT NOT NULL,
            organization TEXT NOT NULL,
            start_date DATE,
            end_date DATE,
            description TEXT,
            location TEXT,
            tags TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 荣誉奖项表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            organization TEXT,
            year INTEGER,
            description TEXT,
            tags TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 友情链接表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            avatar TEXT,
            order_index INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            beian TEXT,
            site_title TEXT DEFAULT '个人学术主页',
            site_description TEXT,
            keywords TEXT,
            analytics_code TEXT,
            show_tags BOOLEAN DEFAULT 1,
            custom_css TEXT,
            footer_text TEXT,
            social_links TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def create_admin_user(username, password, email=None):
    """创建管理员用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f"User '{username}' already exists!")
        conn.close()
        return False
    
    # 创建密码哈希
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, password_hash, email))
        
        conn.commit()
        print(f"Admin user '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def create_default_profile():
    """创建默认个人资料"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查是否已有个人资料
    cursor.execute('SELECT id FROM profile WHERE id = 1')
    if cursor.fetchone():
        conn.close()
        return
    
    cursor.execute('''
        INSERT INTO profile (id, name, title, bio, research_interests, email, website, github)
        VALUES (1, 'Dr. Academic', 'Research Scientist', 
                '欢迎访问我的学术主页！\n\n我是一名专注于**人工智能**和**机器学习**研究的学者。主要研究方向包括深度学习、自然语言处理和计算机视觉。\n\n在这里您可以了解我的学术成果、研究项目和最新动态。如有学术合作或交流需求，欢迎与我联系。',
                '机器学习, 深度学习, 自然语言处理, 计算机视觉',
                'researcher@example.com',
                'https://example.com',
                'https://github.com/researcher')
    ''')
    
    conn.commit()
    conn.close()
    print("Default profile created!")

def create_default_data():
    """创建默认示例数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建默认系统设置
    cursor.execute('SELECT id FROM settings WHERE id = 1')
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO settings (id, beian, site_title, site_description)
            VALUES (1, '京ICP备12345678号-1 | 京公网安备11010802012345号', '个人学术主页', '专注于人工智能研究的学术主页')
        ''')
    
    # 创建示例论文
    cursor.execute('SELECT id FROM publications LIMIT 1')
    if not cursor.fetchone():
        papers = [
            ('基于深度学习的自然语言处理技术研究', 'Dr. Academic, 李研究员, 王博士', '计算机学报', 2023, '45', '123-135', '10.1234/example.2023.001', 'https://doi.org/10.1234/example.2023.001', '本文提出了一种基于Transformer架构的新型自然语言处理模型，在多个基准数据集上取得了优异的性能。实验结果表明，该方法在文本分类、情感分析和机器翻译任务上均超越了现有方法。', '深度学习, 自然语言处理, Transformer', 'journal'),
            ('面向智能问答的知识图谱构建方法', 'Dr. Academic, 张教授', 'IEEE Transactions on Knowledge and Data Engineering', 2023, '35', '2456-2468', '10.1109/TKDE.2023.001', 'https://ieeexplore.ieee.org/document/123456', '提出了一种自动化的知识图谱构建方法，能够从非结构化文本中抽取实体和关系，构建高质量的知识图谱用于智能问答系统。', '知识图谱, 信息抽取, 智能问答', 'journal'),
            ('大规模预训练模型的高效微调技术', 'Dr. Academic, 陈副教授, 刘博士', 'Advances in Neural Information Processing Systems (NeurIPS)', 2022, '', '3456-3467', '', 'https://proceedings.neurips.cc/paper/2022/hash/abc123', '针对大规模预训练模型微调过程中的计算效率问题，提出了一种参数高效的微调方法，在保持性能的同时显著降低了计算成本。', '预训练模型, 微调, 参数效率', 'conference')
        ]
        
        for paper in papers:
            cursor.execute('''
                INSERT INTO publications (title, authors, journal, year, volume, pages, doi, url, abstract, keywords, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', paper)
    
    # 创建示例项目
    cursor.execute('SELECT id FROM projects LIMIT 1')
    if not cursor.fetchone():
        projects = [
            ('智能对话系统开发', '基于大语言模型的智能对话系统，具备多轮对话、上下文理解和知识问答能力。', '''# 智能对话系统开发项目

## 项目概述
本项目旨在开发一个基于**大语言模型**的智能对话系统，具备强大的多轮对话、上下文理解和专业知识问答能力。

## 核心技术架构
### RAG架构设计
- **检索增强生成（RAG）**：结合向量数据库实现精准的知识检索
- **多模态融合**：支持文本、图片等多种输入格式
- **实时学习**：系统能够从对话中持续学习和改进

### 技术栈详情
- **后端框架**：FastAPI + uvicorn
- **深度学习**：PyTorch + Transformers
- **向量数据库**：Elasticsearch + FAISS
- **缓存系统**：Redis
- **容器化**：Docker + Kubernetes

## 核心功能
1. **智能问答**：基于海量知识库的专业问答
2. **多轮对话**：保持长期上下文记忆
3. **个性化定制**：根据用户偏好调整回答风格
4. **情感理解**：识别和回应用户情感状态

## 性能指标
- **响应延迟**：< 500ms
- **准确率**：> 95%
- **并发支持**：> 10,000 QPS

## 产业化成果
- 已部署至生产环境服务超过**100万**用户
- 日均对话量超过**500万**次
- 用户满意度达到**4.8/5.0**分''', '项目负责人', '2023-01-01', '2023-12-31', 'Python, PyTorch, Transformers, Elasticsearch, FastAPI', 'https://chat.example.com', 'https://github.com/researcher/chat-system', 'completed', '人工智能,对话系统,大模型'),
            ('学术论文推荐算法', '开发基于深度学习的个性化学术论文推荐系统，通过分析用户的研究兴趣和历史阅读记录推荐论文。', '''# 学术论文推荐算法项目

## 项目背景
随着学术论文数量的爆炸式增长，研究人员面临信息过载的挑战。本项目致力于开发智能的论文推荐系统，帮助研究者高效发现相关的高质量研究。

## 算法创新
### 多维度特征提取
- **文本语义**：基于BERT的论文摘要语义理解
- **引用网络**：利用Graph Neural Networks分析引用关系
- **作者信息**：考虑作者的研究领域和影响力
- **时间因子**：结合论文发表时间的权重衰减

### 混合推荐策略
1. **协同过滤**：基于用户行为相似性
2. **内容推荐**：基于论文内容相似性
3. **知识图谱**：基于学科知识图谱的推荐
4. **热度推荐**：结合当前热点研究方向

## 技术实现
```python
# 核心推荐算法
class PaperRecommender:
    def __init__(self):
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.gnn_model = GraphConvolutionalNetwork()
        
    def recommend(self, user_id, k=10):
        # 多路召回 + 精排
        candidates = self.multi_recall(user_id)
        ranked_papers = self.ranking_model(candidates)
        return ranked_papers[:k]
```

## 数据集与评估
- **数据规模**：1000万+ 学术论文
- **用户数据**：10万+ 研究者行为数据
- **评估指标**：
  - NDCG@10: 0.85
  - 召回率@20: 0.72
  - 点击率: 15.6%

## 产品化成果
- 集成到多个学术平台
- 服务全球超过**50万**研究者
- 月均推荐点击量**200万**次''', '算法工程师', '2022-06-01', '2023-05-31', 'Python, TensorFlow, Neo4j, Scikit-learn, Redis', 'https://paperrec.example.com', 'https://github.com/researcher/paper-rec', 'completed', '推荐系统,深度学习,知识图谱'),
            ('多模态情感识别研究', '结合文本、语音和视觉信息的多模态情感识别技术研究，在多个公开数据集上验证了方法的有效性。', '''# 多模态情感识别研究项目

## 研究目标
开发能够综合分析文本、语音和视觉信息的情感识别模型，实现比单模态方法更准确和鲁棒的情感理解。

## 研究创新点
### 1. 多模态融合机制
- **早期融合**：特征级别的模态融合
- **晚期融合**：决策级别的模态融合  
- **注意力机制**：自适应的模态权重分配

### 2. 跨模态对齐
设计了新的跨模态对齐损失函数：
```
L_align = λ₁ * L_text_audio + λ₂ * L_text_visual + λ₃ * L_audio_visual
```

### 3. 时序建模
- **文本**：基于LSTM的序列建模
- **语音**：考虑语音信号的时序特性
- **视频**：3D CNN捕获时空特征

## 实验设置
### 数据集
- **IEMOCAP**：多模态情感数据库
- **CMU-MOSEI**：大规模情感分析数据集
- **自建数据集**：中文多模态情感数据

### 实验结果
| 数据集 | 文本 | 语音 | 视觉 | 多模态 |
|--------|------|------|------|--------|
| IEMOCAP | 72.1% | 68.5% | 65.2% | **79.3%** |
| CMU-MOSEI | 75.8% | 71.2% | 69.7% | **82.1%** |

## 技术贡献
1. 提出了新的多模态融合网络架构
2. 设计了有效的跨模态注意力机制
3. 在多个基准数据集上达到SOTA性能

## 学术产出
- **顶级会议论文**：ACM MM 2022
- **期刊论文**：IEEE TAFFC (在审)
- **开源代码**：GitHub 500+ stars''', '技术负责人', '2022-01-01', '2022-12-31', 'Python, PyTorch, OpenCV, librosa, CUDA', '', 'https://github.com/researcher/multimodal-emotion', 'completed', '多模态,情感识别,深度学习')
        ]
        
        for project in projects:
            cursor.execute('''
                INSERT INTO projects (title, description, detailed_description, role, start_date, end_date, technologies, url, github_url, status, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', project)
    
    # 创建示例工作经历
    cursor.execute('SELECT id FROM experience LIMIT 1')
    if not cursor.fetchone():
        experiences = [
            ('研究科学家', '某科技公司AI实验室', '2022-07-01', None, '负责自然语言处理和机器学习相关研究项目，指导研究团队开展前沿技术研究，与产品团队合作将研究成果产业化。\n\n**主要成就：**\n- 主导开发了公司核心的对话AI产品\n- 发表高质量学术论文3篇\n- 申请技术专利2项', '北京', '大厂,AI领域,核心团队'),
            ('博士后研究员', '清华大学计算机科学与技术系', '2020-09-01', '2022-06-30', '在导师指导下开展人工智能基础理论研究，专注于深度学习理论和算法优化。参与国家自然科学基金重点项目。', '北京', '985,211,顶尖高校'),
            ('研究助理', 'MIT计算机科学与人工智能实验室', '2019-01-01', '2020-08-31', '协助导师进行机器学习和自然语言处理研究，参与了多个国际合作项目。', '马萨诸塞州，剑桥市', '世界顶级,MIT,CSAIL')
        ]
        
        for exp in experiences:
            cursor.execute('''
                INSERT INTO experience (position, organization, start_date, end_date, description, location, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', exp)
    
    # 创建示例教育背景
    cursor.execute('SELECT id FROM education LIMIT 1')
    if not cursor.fetchone():
        educations = [
            ('博士学位', 'Stanford University', '计算机科学', 2015, 2019, '**博士论文：** "Deep Learning Approaches for Natural Language Understanding"\n\n**导师：** Prof. Christopher Manning\n\n**主要研究：** 深度学习在自然语言理解中的应用', '顶尖名校,世界前5'),
            ('硕士学位', 'Carnegie Mellon University', '机器学习', 2013, 2015, '**硕士论文：** "Efficient Training Methods for Neural Networks"\n\n**GPA：** 3.9/4.0', '计算机名校,CMU'),
            ('学士学位', '清华大学', '计算机科学与技术', 2009, 2013, '**毕业设计：** 基于机器学习的图像识别系统\n\n**荣誉：** 优秀毕业生，学业优秀奖', '985,211,双一流')
        ]
        
        for edu in educations:
            cursor.execute('''
                INSERT INTO education (degree, institution, field, start_year, end_year, description, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', edu)
    
    # 创建示例奖项
    cursor.execute('SELECT id FROM awards LIMIT 1')
    if not cursor.fetchone():
        awards = [
            ('国家自然科学基金优秀青年科学基金', '国家自然科学基金委员会', 2023, '表彰在人工智能基础理论研究方面的突出贡献', '国家级,优青,重大荣誉'),
            ('IEEE计算机学会青年学者奖', 'IEEE Computer Society', 2022, '表彰在机器学习领域的创新研究和学术贡献', '国际奖项,IEEE,青年学者'),
            ('ACM SIGKDD博士论文奖', 'ACM SIGKDD', 2020, '全球数据挖掘领域最佳博士论文', '全球第一,博士论文,顶级会议'),
            ('Stanford大学优秀博士毕业生', 'Stanford University', 2019, '计算机科学系年度优秀博士毕业生', '优秀毕业生,Stanford,年度最佳')
        ]
        
        for award in awards:
            cursor.execute('''
                INSERT INTO awards (title, organization, year, description, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', award)
    
    # 创建示例友情链接
    cursor.execute('SELECT id FROM friends LIMIT 1')
    if not cursor.fetchone():
        friends = [
            ('Google Scholar', 'https://scholar.google.com', 'Google学术搜索引擎', 'https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg'),
            ('arXiv.org', 'https://arxiv.org', '计算机科学论文预印本平台', 'https://arxiv.org/favicon.ico'),
            ('Papers With Code', 'https://paperswithcode.com', '机器学习论文与代码资源', 'https://paperswithcode.com/static/img/favicon.png'),
            ('Semantic Scholar', 'https://www.semanticscholar.org', 'AI驱动的学术搜索引擎', 'https://www.semanticscholar.org/img/semantic_scholar_og.png'),
            ('IEEE Xplore', 'https://ieeexplore.ieee.org', 'IEEE数字图书馆', 'https://ieeexplore.ieee.org/favicon.ico')
        ]
        
        for friend in friends:
            cursor.execute('''
                INSERT INTO friends (name, url, description, avatar)
                VALUES (?, ?, ?, ?)
            ''', friend)
    
    conn.commit()
    conn.close()
    print("Default sample data created!")

if __name__ == '__main__':
    init_database()
    create_default_profile()
    
    # 创建默认管理员账户
    import getpass
    print("Creating admin user...")
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    password = getpass.getpass("Enter admin password: ")
    email = input("Enter admin email (optional): ").strip() or None
    
    create_admin_user(username, password, email) 