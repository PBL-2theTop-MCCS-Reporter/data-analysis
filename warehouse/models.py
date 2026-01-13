"""
SQLAlchemy ORM Models for Snowflake Data Warehouse
Defines the metrics, dimensions, and facts tables for live data querying.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Metric(Base):
    """Metrics table: Defines available metrics (sales, engagement, etc.)"""
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, nullable=False, unique=True, index=True)
    metric_name = Column(String(255), nullable=False)
    metric_desc = Column(Text)
    data_type = Column(String(50), nullable=False)  # 'numeric', 'percentage', 'count'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to facts
    facts = relationship("Fact", backref="metric")

    def __repr__(self):
        return f"<Metric(id={self.id}, metric_id={self.metric_id}, name='{self.metric_name}')>"

class Dimension(Base):
    """Dimensions table: Stores dimensional data (sites, commands, etc.)"""
    __tablename__ = 'dimensions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dimension_type = Column(String(100), nullable=False, index=True)  # 'site', 'command', etc.
    dimension_code = Column(String(100), nullable=False, index=True)
    dimension_name = Column(String(255), nullable=False)
    dimension_metadata = Column(Text)  # JSON string for additional attributes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('dimension_type', 'dimension_code', name='unique_dimension'),
        Index('idx_dimension_type_code', 'dimension_type', 'dimension_code'),
    )

    # Relationship to fact-dimensions (through fact_dimensions table)
    fact_dimensions = relationship("FactDimension", backref="dimension")

    def __repr__(self):
        return f"<Dimension(id={self.id}, type='{self.dimension_type}', code='{self.dimension_code}', name='{self.dimension_name}')>"

class Fact(Base):
    """Facts table: Stores actual measurements"""
    __tablename__ = 'facts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey('metrics.metric_id'), nullable=False, index=True)
    period_type = Column(Integer, nullable=False, index=True)  # 1=daily, 2=monthly, 3=quarterly, 4=yearly
    period_start = Column(String(8), nullable=False, index=True)  # YYYYMMDD format
    period_end = Column(String(8), nullable=False, index=True)    # YYYYMMDD format
    period_key = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_fact_lookup', 'metric_id', 'period_type', 'period_start', 'period_end'),
        Index('idx_fact_metric_period', 'metric_id', 'period_type'),
    )

    # Relationships
    fact_dimensions = relationship("FactDimension", backref="fact")

    def __repr__(self):
        return f"<Fact(id={self.id}, metric_id={self.metric_id}, period_type={self.period_type}, value={self.value})>"

class FactDimension(Base):
    """Junction table for many-to-many relationship between facts and dimensions"""
    __tablename__ = 'fact_dimensions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fact_id = Column(Integer, ForeignKey('facts.id'), nullable=False, index=True)
    dimension_id = Column(Integer, ForeignKey('dimensions.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('fact_id', 'dimension_id', name='unique_fact_dimension'),
        Index('idx_fact_dimension_lookup', 'fact_id', 'dimension_id'),
    )

    def __repr__(self):
        return f"<FactDimension(id={self.id}, fact_id={self.fact_id}, dimension_id={self.dimension_id})>"
