from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Shopkeeper(Base):
    __tablename__ = 'shopkeepers'

    id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    location = Column(String, nullable=False)
    shop_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    searches = relationship('SearchLog', back_populates='shopkeeper')


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    tags = Column(String, nullable=False)
    seasonal = Column(String, default='all')


class SearchLog(Base):
    __tablename__ = 'search_logs'

    id = Column(Integer, primary_key=True, index=True)
    shopkeeper_id = Column(Integer, ForeignKey('shopkeepers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    customer_segment = Column(String, default='regular')
    preference_tags = Column(String, default='')
    budget = Column(Float, default=0)
    is_raining = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    shopkeeper = relationship('Shopkeeper', back_populates='searches')
    product = relationship('Product')
