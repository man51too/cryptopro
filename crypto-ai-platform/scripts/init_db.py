#!/usr/bin/env python3
"""
Database initialization script
Creates tables and populates with sample data
"""
import sys
sys.path.insert(0, '/app')

from app.core.database import engine, Base
from app.models import coin, ai_prediction, user, watchlist
from app.services.ai_engine import ai_engine
from sqlalchemy.orm import Session

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def seed_sample_data():
    """Seed database with sample cryptocurrency data"""
    print("\nSeeding sample data...")
    
    from app.models.coin import Coin
    from app.models.ai_prediction import AIPrediction
    
    # Sample coins data (top cryptocurrencies)
    sample_coins = [
        {
            "coin_id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "rank": 1,
            "current_price": 45000.00,
            "ath": 69000.00,
            "ath_distance_percent": -34.78,
            "required_growth_multiplier": 1.53,
            "market_cap": 880000000000,
            "volume_24h": 25000000000,
        },
        {
            "coin_id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "rank": 2,
            "current_price": 2300.00,
            "ath": 4878.00,
            "ath_distance_percent": -52.84,
            "required_growth_multiplier": 2.12,
            "market_cap": 276000000000,
            "volume_24h": 12000000000,
        },
        {
            "coin_id": "solana",
            "symbol": "SOL",
            "name": "Solana",
            "rank": 5,
            "current_price": 100.00,
            "ath": 260.00,
            "ath_distance_percent": -61.54,
            "required_growth_multiplier": 2.60,
            "market_cap": 42000000000,
            "volume_24h": 2500000000,
        },
        {
            "coin_id": "cardano",
            "symbol": "ADA",
            "name": "Cardano",
            "rank": 8,
            "current_price": 0.50,
            "ath": 3.10,
            "ath_distance_percent": -83.87,
            "required_growth_multiplier": 6.20,
            "market_cap": 17500000000,
            "volume_24h": 450000000,
        },
        {
            "coin_id": "polkadot",
            "symbol": "DOT",
            "name": "Polkadot",
            "rank": 12,
            "current_price": 7.50,
            "ath": 55.00,
            "ath_distance_percent": -86.36,
            "required_growth_multiplier": 7.33,
            "market_cap": 9500000000,
            "volume_24h": 280000000,
        },
    ]
    
    db = Session(engine)
    
    try:
        for coin_data in sample_coins:
            # Create or update coin
            coin = db.query(Coin).filter(Coin.coin_id == coin_data["coin_id"]).first()
            
            if not coin:
                coin = Coin(**coin_data)
                db.add(coin)
                db.commit()
                db.refresh(coin)
                
                # Generate AI prediction
                prediction_data = ai_engine.analyze_coin(coin_data)
                
                ai_prediction = AIPrediction(
                    coin_id=coin.coin_id,
                    **prediction_data,
                    analysis_reasons=str(prediction_data["analysis_reasons"]),
                )
                db.add(ai_prediction)
                db.commit()
                
                print(f"  ✓ Added {coin.name} ({coin.symbol}) - AI Score: {prediction_data['ai_recovery_score']}")
        
        print("\n✓ Sample data seeded successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    seed_sample_data()
    print("\n🎉 Database initialization complete!")
