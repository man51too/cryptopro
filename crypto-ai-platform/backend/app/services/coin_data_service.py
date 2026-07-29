"""
Coin Data Service - Fetch and process cryptocurrency data from external APIs
"""
import httpx
from typing import List, Dict, Optional, Any
from loguru import logger
from datetime import datetime

from app.core.config import settings


class CoinGeckoService:
    """Service for fetching data from CoinGecko API"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.timeout = 30.0
        self.headers = {
            "Accept": "application/json",
        }
        if settings.COINGECKO_API_KEY:
            self.headers["x-cg-pro-api-key"] = settings.COINGECKO_API_KEY
    
    async def get_top_coins(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get top cryptocurrencies by market cap"""
        url = f"{self.BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": min(limit, 250),  # CoinGecko max per page
            "page": 1,
            "sparkline": False,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching top coins from CoinGecko: {e}")
            return []
    
    async def get_coin_data(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed data for a specific coin"""
        url = f"{self.BASE_URL}/coins/{coin_id}"
        params = {
            "localization": False,
            "tickers": True,
            "market_data": True,
            "community_data": True,
            "developer_data": True,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching coin {coin_id} data: {e}")
            return None
    
    async def get_coin_ath(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get ATH data for a coin"""
        url = f"{self.BASE_URL}/coins/{coin_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                market_data = data.get("market_data", {})
                ath_data = market_data.get("ath", {})
                ath_date_data = market_data.get("ath_date", {})
                
                return {
                    "ath_price": ath_data.get("usd"),
                    "ath_date": ath_date_data.get("usd"),
                    "current_price": market_data.get("current_price", {}).get("usd"),
                }
        except Exception as e:
            logger.error(f"Error fetching ATH for {coin_id}: {e}")
            return None
    
    def calculate_ath_distance(self, current_price: float, ath: float) -> Dict[str, float]:
        """Calculate distance from ATH and required growth multiplier"""
        if not ath or ath <= 0:
            return {"distance_percent": 0, "multiplier": 1.0}
        
        distance_percent = ((current_price - ath) / ath) * 100
        multiplier = ath / current_price if current_price > 0 else 1.0
        
        return {
            "distance_percent": round(distance_percent, 2),
            "multiplier": round(multiplier, 2),
        }


class CoinDataService:
    """Main service for managing coin data"""
    
    def __init__(self):
        self.coingecko = CoinGeckoService()
    
    async def fetch_and_process_top_coins(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch top coins and process ATH data"""
        logger.info(f"Fetching top {limit} coins...")
        
        coins = await self.coingecko.get_top_coins(limit)
        processed_coins = []
        
        for coin in coins:
            try:
                ath_data = self.coingecko.calculate_ath_distance(
                    coin.get("current_price", 0),
                    coin.get("ath", 0)
                )
                
                processed_coin = {
                    "coin_id": coin.get("id"),
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "rank": coin.get("market_cap_rank"),
                    "current_price": coin.get("current_price"),
                    "ath": coin.get("ath"),
                    "ath_date": coin.get("ath_date"),
                    "atl": coin.get("atl"),
                    "atl_date": coin.get("atl_date"),
                    "market_cap": coin.get("market_cap"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "volume_24h": coin.get("total_volume"),
                    "circulating_supply": coin.get("circulating_supply"),
                    "total_supply": coin.get("total_supply"),
                    "max_supply": coin.get("max_supply"),
                    "ath_distance_percent": ath_data["distance_percent"],
                    "required_growth_multiplier": ath_data["multiplier"],
                    "image_url": coin.get("image", ""),
                }
                
                processed_coins.append(processed_coin)
                
            except Exception as e:
                logger.error(f"Error processing coin {coin.get('id')}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_coins)} coins")
        return processed_coins
    
    async def update_coin_in_db(self, db, coin_data: Dict[str, Any]):
        """Update or insert coin data in database"""
        from app.models.coin import Coin
        
        coin_id = coin_data.get("coin_id")
        if not coin_id:
            return None
        
        # Check if coin exists
        coin = db.query(Coin).filter(Coin.coin_id == coin_id).first()
        
        if coin:
            # Update existing coin
            for key, value in coin_data.items():
                if hasattr(coin, key) and value is not None:
                    setattr(coin, key, value)
            coin.updated_at = datetime.utcnow()
        else:
            # Create new coin
            coin = Coin(**coin_data)
            db.add(coin)
        
        db.commit()
        db.refresh(coin)
        return coin


# Singleton instance
coin_data_service = CoinDataService()
