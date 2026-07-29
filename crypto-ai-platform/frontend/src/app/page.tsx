'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface MarketOverview {
  total_coins: number
  coins_with_predictions: number
  average_ai_score: number
  high_score_count: number
  market_sentiment: string
}

interface DashboardCoin {
  coin_id: string
  symbol: string
  name: string
  rank: number
  current_price: number
  ath_distance_percent: number
  ai_score?: number
  recovery_probability?: number
  risk_level?: string
}

export default function Home() {
  const [overview, setOverview] = useState<MarketOverview | null>(null)
  const [topPicks, setTopPicks] = useState<DashboardCoin[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewRes, picksRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/dashboard/overview'),
          fetch('http://localhost:8000/api/v1/dashboard/top-ai-picks?limit=10'),
        ])
        
        if (overviewRes.ok) {
          const overviewData = await overviewRes.json()
          setOverview(overviewData)
        }
        
        if (picksRes.ok) {
          const picksData = await picksRes.json()
          setTopPicks(picksData)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-primary">🚀 Crypto AI Platform</span>
            </div>
            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-sm font-medium hover:text-primary">Dashboard</Link>
              <Link href="/ath-scanner" className="text-sm font-medium hover:text-primary">ATH Scanner</Link>
              <Link href="/ai-predictions" className="text-sm font-medium hover:text-primary">AI Predictions</Link>
              <Link href="/moonshot" className="text-sm font-medium hover:text-primary">Moonshot</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">AI-Powered Crypto ATH Recovery Analysis</h1>
          <p className="text-muted-foreground text-lg">
            Discover cryptocurrencies with the highest potential to return to their All-Time Highs
          </p>
        </div>

        {/* Market Overview Cards */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-card rounded-lg p-6 border animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-muted rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : overview ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Total Coins Analyzed</h3>
              <p className="text-3xl font-bold">{overview.total_coins}</p>
            </div>
            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">AI Predictions</h3>
              <p className="text-3xl font-bold">{overview.coins_with_predictions}</p>
            </div>
            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Average AI Score</h3>
              <p className="text-3xl font-bold">{overview.average_ai_score}/100</p>
            </div>
            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Market Sentiment</h3>
              <p className={`text-3xl font-bold ${
                overview.market_sentiment === 'Bullish' ? 'text-green-500' :
                overview.market_sentiment === 'Bearish' ? 'text-red-500' : ''
              }`}>{overview.market_sentiment}</p>
            </div>
          </div>
        ) : null}

        {/* Top AI Picks Table */}
        <div className="bg-card rounded-lg border mb-8">
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold">Top AI Picks</h2>
            <p className="text-muted-foreground">Cryptocurrencies with highest AI recovery scores</p>
          </div>
          
          {loading ? (
            <div className="p-6">
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-16 bg-muted rounded animate-pulse"></div>
                ))}
              </div>
            </div>
          ) : topPicks.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">#</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Coin</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Price</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">ATH Distance</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">AI Score</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Recovery Prob.</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-muted-foreground uppercase">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {topPicks.map((coin, index) => (
                    <tr key={coin.coin_id} className="border-t hover:bg-muted/50">
                      <td className="px-6 py-4 text-sm font-medium">{index + 1}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="font-medium">{coin.name}</div>
                          <span className="ml-2 text-muted-foreground text-sm">{coin.symbol}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right text-sm">
                        ${coin.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-red-500">
                        {coin.ath_distance_percent.toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          (coin.ai_score || 0) >= 80 ? 'bg-green-100 text-green-800' :
                          (coin.ai_score || 0) >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {(coin.ai_score || 0).toFixed(0)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        {(coin.recovery_probability || 0).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          coin.risk_level === 'Low' ? 'bg-green-100 text-green-800' :
                          coin.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          coin.risk_level === 'High' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {coin.risk_level || 'N/A'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6 text-center text-muted-foreground">
              No data available. Make sure the backend is running.
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/ath-scanner" className="block p-6 bg-card rounded-lg border hover:border-primary transition-colors">
            <h3 className="text-lg font-semibold mb-2">📊 ATH Scanner</h3>
            <p className="text-muted-foreground text-sm">Find coins with the biggest drops from their All-Time Highs</p>
          </Link>
          
          <Link href="/ai-predictions" className="block p-6 bg-card rounded-lg border hover:border-primary transition-colors">
            <h3 className="text-lg font-semibold mb-2">🤖 AI Predictions</h3>
            <p className="text-muted-foreground text-sm">View detailed AI analysis and recovery probability for each coin</p>
          </Link>
          
          <Link href="/moonshot" className="block p-6 bg-card rounded-lg border hover:border-primary transition-colors">
            <h3 className="text-lg font-semibold mb-2">🌙 Moonshot Scanner</h3>
            <p className="text-muted-foreground text-sm">Discover coins most likely to return to ATH soon</p>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-muted-foreground text-sm">
          <p>Crypto AI Platform © 2024 - AI-powered cryptocurrency analysis</p>
          <p className="mt-2">Not financial advice. Always do your own research.</p>
        </div>
      </footer>
    </div>
  )
}
