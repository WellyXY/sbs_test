"""
數據庫模型定義
定義所有數據表的 SQLAlchemy 模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import uuid


class Task(Base):
    """任務模型"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, comment="任務名稱")
    status = Column(String(50), default="pending", comment="任務狀態: pending, in_progress, completed")
    folder_a_path = Column(String(500), nullable=False, comment="文件夾A路徑")
    folder_b_path = Column(String(500), nullable=False, comment="文件夾B路徑")
    total_pairs = Column(Integer, default=0, comment="總視頻對數")
    completed_pairs = Column(Integer, default=0, comment="已完成評估的對數")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="創建時間")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新時間")

    # 關聯關係
    video_pairs = relationship("VideoPair", back_populates="task", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="task", cascade="all, delete-orphan")


class VideoPair(Base):
    """視頻對模型"""
    __tablename__ = "video_pairs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, comment="所屬任務ID")
    video_a_path = Column(String(500), nullable=False, comment="視頻A文件路徑")
    video_b_path = Column(String(500), nullable=False, comment="視頻B文件路徑")
    video_a_name = Column(String(255), nullable=False, comment="視頻A文件名")
    video_b_name = Column(String(255), nullable=False, comment="視頻B文件名")
    is_evaluated = Column(Boolean, default=False, comment="是否已評估")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="創建時間")

    # 關聯關係
    task = relationship("Task", back_populates="video_pairs")
    evaluations = relationship("Evaluation", back_populates="video_pair", cascade="all, delete-orphan")


class Evaluation(Base):
    """評估結果模型"""
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, comment="所屬任務ID")
    video_pair_id = Column(String, ForeignKey("video_pairs.id"), nullable=False, comment="視頻對ID")
    user_id = Column(String, nullable=True, comment="評估用戶ID")
    choice = Column(String(10), nullable=True, comment="選擇結果: A, B, tie, null")
    score_a = Column(Float, default=0.0, comment="視頻A評分")
    score_b = Column(Float, default=0.0, comment="視頻B評分")
    comments = Column(Text, nullable=True, comment="評語")
    is_blind = Column(Boolean, default=True, comment="是否為盲測")
    randomized_order = Column(Boolean, default=True, comment="是否隨機排序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="評估時間")

    # 關聯關係
    task = relationship("Task", back_populates="evaluations")
    video_pair = relationship("VideoPair", back_populates="evaluations")


class User(Base):
    """用戶模型"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, comment="用戶名稱")
    email = Column(String(255), nullable=True, unique=True, comment="電子郵件")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="創建時間")
    is_active = Column(Boolean, default=True, comment="是否啟用")


class SystemConfig(Base):
    """系統配置模型"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment="配置鍵")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(255), nullable=True, comment="配置描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="創建時間")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新時間") 