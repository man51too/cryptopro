"""
Database Base Module
Provides the base class for all SQLAlchemy models
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models.
    
    All model classes should inherit from this base class.
    It provides common functionality and metadata.
    """
    
    @classmethod
    def get_tablename(cls) -> str:
        """Get the table name for this model"""
        return cls.__tablename__
    
    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
