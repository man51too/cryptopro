"""
Watchlist model for user-saved coins
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Watchlist(Base):
    """
    User watchlist for tracking favorite coins
    """
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    coin_id = Column(String(100), ForeignKey('coins.coin_id'), nullable=False, index=True)
    
    # Custom Notes
    notes = Column(String(500), nullable=True)
    
    # Alert Settings
    alert_on_price_change = Column(Boolean, default=False)
    alert_on_ai_score_change = Column(Boolean, default=False)
    price_change_threshold = Column(Float, nullable=True)  # Percentage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="watchlist")
    # coin = relationship("Coin", back_populates="watchlists")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'coin_id', name='unique_user_coin_watchlist'),
    )
    
    def __repr__(self):
        return f"<Watchlist User:{self.user_id} Coin:{self.coin_id}>"
