"""
數據庫配置和連接管理
使用 SQLAlchemy 進行 ORM 操作
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 數據庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./side_by_side.db")

# 創建數據庫引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # 設為 True 可以看到 SQL 查詢日誌
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建基礎模型類
Base = declarative_base()

# 元數據
metadata = MetaData()


def get_db():
    """
    獲取數據庫會話
    用於依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化數據庫
    創建所有表
    """
    Base.metadata.create_all(bind=engine)
    print("✅ 數據庫表創建完成")


def reset_db():
    """
    重置數據庫
    刪除所有表並重新創建
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("🔄 數據庫已重置") 