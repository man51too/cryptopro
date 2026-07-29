"""Pydantic schemas for watchlist and alerts."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration."""
    
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    SCORE_INCREASE = "score_increase"
    SCORE_DECREASE = "score_decrease"
    ATH_RECOVERY = "ath_recovery"


class NotificationMethod(str, Enum):
    """Notification method enumeration."""
    
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"


class WatchlistBase(BaseModel):
    """Base watchlist schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class WatchlistCreate(WatchlistBase):
    """Schema for creating a watchlist."""
    
    coin_ids: List[int] = []


class WatchlistUpdate(BaseModel):
    """Schema for updating a watchlist."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class WatchlistInDB(WatchlistBase):
    """Schema for watchlist in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class Watchlist(WatchlistInDB):
    """Public watchlist schema with coins."""
    
    coins: Optional[List[dict]] = None


class WatchlistItem(BaseModel):
    """Schema for watchlist item."""
    
    id: int
    watchlist_id: int
    coin_id: int
    custom_name: Optional[str] = None
    notes: Optional[str] = None
    added_at: datetime


class AlertBase(BaseModel):
    """Base alert schema."""
    
    alert_type: AlertType
    coin_id: int
    threshold_value: float
    notification_methods: List[NotificationMethod] = [NotificationMethod.EMAIL]
    is_active: bool = True


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    
    webhook_url: Optional[str] = None
    message_template: Optional[str] = None


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    
    threshold_value: Optional[float] = None
    is_active: Optional[bool] = None
    notification_methods: Optional[List[NotificationMethod]] = None


class AlertInDB(AlertBase):
    """Schema for alert in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    webhook_url: Optional[str] = None
    message_template: Optional[str] = None
    triggered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Alert(AlertInDB):
    """Public alert schema."""
    
    coin_symbol: Optional[str] = None
    coin_name: Optional[str] = None
    current_value: Optional[float] = None


class AlertTrigger(BaseModel):
    """Schema for alert trigger event."""
    
    alert_id: int
    triggered_value: float
    triggered_at: datetime
    notification_sent: bool
