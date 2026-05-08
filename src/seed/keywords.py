from sqlalchemy.orm import sessionmaker

from models.keyword import Keyword
from seed.engine import engine

Session = sessionmaker(bind=engine)

def create_keywords():
    keywords = [
        # CS - Languages
        "python",
        "c++",
        "swift",
        "java",
        "javascript",
        "rust",
        "go",
        "kotlin",
        "ruby",
        "php",
        # CS - Algorithms
        "sorting-algorithms",
        "search-algorithms",
        "graph-algorithms",
        "dynamic-programming",
        "greedy-algorithms",
        "divide-and-conquer",
        "recursion",
        "complexity-analysis",
        "compression",
        "hashing",
        # CS - AI & Machine Learning
        "machine-learning",
        "deep-learning",
        "neural-networks",
        "supervised-learning",
        "unsupervised-learning",
        "reinforcement-learning",
        "nlp",
        "natural-language-processing",
        "computer-vision",
        "image-recognition",
        "classification",
        "regression",
        "clustering",
        "decision-trees",
        "random-forests",
        "gradient-descent",
        "backpropagation",
        "convolutional-neural-networks",
        "recurrent-neural-networks",
        "transformer-models",
        "large-language-models",
        "generative-ai",
        # CS - Systems & Other
        "distributed-systems",
        "concurrent-programming",
        "parallel-computing",
        "operating-systems",
        "embedded-systems",
        "cryptography",
        "network-security",
        "database-systems",
        "data-structures",
        "software-engineering",
        # Industrial Engineering
        "supply-chain-management",
        "logistics",
        "production-planning",
        "inventory-management",
        "quality-control",
        "lean-manufacturing",
        "six-sigma",
        "process-optimization",
        "scheduling",
        "resource-allocation",
        "simulation",
        "queuing-theory",
        "operations-research",
        "project-management",
        "risk-analysis",
        "decision-making",
        "cost-analysis",
        "capacity-planning",
        "forecasting",
    ]

    with Session() as s:
        for i in range(len(keywords)):
            new_keyword = Keyword(name=keywords[i])

            s.add(new_keyword)

        s.commit()
