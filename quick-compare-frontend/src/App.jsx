import React, { useState } from 'react';
import { Search, TrendingUp, TrendingDown, Activity, ShoppingCart, AlertCircle, Cpu, Zap, Database } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [prediction, setPrediction] = useState({});
  const [loading, setLoading] = useState(false);
  const [activePlatform, setActivePlatform] = useState('Zepto');
  const [error, setError] = useState(null);
  
  // Telemetry Performance State variables
  const [latency, setLatency] = useState(null);
  const [isCached, setIsCached] = useState(false);
  const [searchedTerms, setSearchedTerms] = useState(new Set());

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    setError(null);

    const lowercaseQuery = query.trim().toLowerCase();

    try {
      // 1. Fetch live aggregated search results and extract performance headers
      const searchRes = await fetch(`http://127.0.0.1:8000/api/v1/search?query=${query}`);
      if (!searchRes.ok) throw new Error("Failed to grab live platform data inputs.");
      
      const timingHeader = searchRes.headers.get("X-Process-Time-Ms");
      setLatency(timingHeader || "N/A");

      const searchData = await searchRes.json();
      setSearchResults(searchData);

      // Determine cache status based on search history tracking
      if (searchedTerms.has(lowercaseQuery)) {
        setIsCached(true);
      } else {
        setIsCached(false);
        setSearchedTerms(prev => new Set(prev).add(lowercaseQuery));
      }

      // 2. Fetch market analytics trends
      const analyticsRes = await fetch(`http://127.0.0.1:8000/api/v1/analytics/trends?query=${query}`);
      const analyticsData = await analyticsRes.json();
      setAnalytics(analyticsData);

      // 3. Fetch default ML prediction for the active platform
      fetchPrediction(query, activePlatform);
    } catch (err) {
      console.error("Pipeline connectivity error:", err);
      setError("Security Alert or Connectivity Issue: Verification parameters violated or Uvicorn offline.");
    } finally {
      setLoading(false);
    }
  };

  // Fixed Template Literal String Interpolation with the missing $ sign
  const fetchPrediction = async (itemQuery, platformName) => {
    try {
      const predRes = await fetch(`http://127.0.0.1:8000/api/v1/predict/price?query=${itemQuery}&platform=${platformName}`);
      const predData = await predRes.json();
      setPrediction(predData);
    } catch (error) {
      console.error("Error fetching prediction:", error);
    }
  };

  const changePredictionPlatform = (platformName) => {
    setActivePlatform(platformName);
    if (query) {
      fetchPrediction(query, platformName);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans p-6 transition-colors duration-300 flex flex-col justify-between">
      <div>
        {/* Header Layout */}
        <header className="max-w-6xl mx-auto mb-8 flex items-center justify-between border-b border-purple-100 pb-4">
          <div className="flex items-center space-x-3">
            <ShoppingCart className="h-8 w-8 text-purple-600" />
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Smart Grocery Aggregator
            </h1>
          </div>
          {/* <span className="text-xs bg-purple-50 text-purple-600 font-medium px-3 py-1 rounded-full border border-purple-100 shadow-sm">
            Frontend Engine Live
          </span> */}
        </header>

        {/* Main Framework View */}
        <main className="max-w-6xl mx-auto space-y-8">
          {/* Search Component Panel */}
          <section className="bg-white rounded-xl p-6 border border-purple-100 shadow-md">
            <form onSubmit={handleSearch} className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3.5 h-5 w-5 text-purple-400" />
                <input
                  type="text"
                  placeholder="Query items across platforms (e.g., maggi, milk, bread)..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full bg-slate-50 border border-purple-100 rounded-lg pl-10 pr-4 py-3 text-slate-700 placeholder-slate-400 focus:outline-none focus:border-purple-500 focus:bg-white transition-colors shadow-inner"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-semibold px-6 py-3 rounded-lg transition-colors flex items-center space-x-2 cursor-pointer shadow-sm shadow-purple-200"
              >
                {loading ? 'Analyzing Datasets...' : 'Compare Prices'}
              </button>
            </form>
          </section>

          {/* Error Boundary Notification */}
          {error && (
            <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl flex items-center gap-3 text-rose-700 shadow-sm">
              <AlertCircle className="h-5 w-5 text-rose-500 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {searchResults && analytics && !error && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Live Aggregated Results */}
              <div className="lg:col-span-2 space-y-6">
                <h2 className="text-xl font-bold flex items-center gap-2 text-purple-800">
                  Live Price Comparisons (Sorted Lowest to Highest)
                </h2>
                <div className="space-y-4">
                  {(searchResults?.results || []).map((item, idx) => (
                    <div key={idx} className="bg-white rounded-xl p-5 border border-purple-100 flex justify-between items-center hover:border-purple-300 hover:shadow-lg transition-all shadow-sm">
                      <div>
                        <span className="text-xs font-semibold bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-200 mb-2 inline-block">
                          {item.platform}
                        </span>
                        <h3 className="text-lg font-bold text-slate-800">{item.title}</h3>
                        <p className="text-sm text-slate-500 font-medium">Quantity Parameters: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-black text-purple-700">₹{item.price}</div>
                        <a
                          href={item.product_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-indigo-600 font-semibold hover:text-indigo-800 hover:underline mt-1 inline-block"
                        >
                          View Store Link →
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: Analytics & Data Science Trends */}
              <div className="space-y-6">
                {/* <h2 className="text-xl font-bold flex items-center gap-2 text-indigo-800">
                  Data Science Insights
                </h2> */}

                {/* 30-Day Market Baseline */}
                <div className="bg-white rounded-xl p-5 border border-purple-100 space-y-4 shadow-sm">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">30-Day Market Baseline</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-3 rounded-lg border border-purple-50/50">
                      <p className="text-xs font-medium text-slate-500">Avg Price</p>
                      <p className="text-xl font-black text-slate-800">
                        ₹{analytics?.market_summary?.average_market_price || "0.00"}
                      </p>
                    </div>
                    <div className="bg-purple-50/50 p-3 rounded-lg border border-purple-100">
                      <p className="text-xs font-medium text-purple-700">Historical Lowest</p>
                      <p className="text-xl font-black text-purple-700">
                        ₹{analytics?.market_summary?.lowest_historical_price || "0.00"}
                      </p>
                    </div>
                  </div>
                  
                  {/* Visual Tracker Bar */}
                  <div className="space-y-1 pt-2 border-t border-purple-50">
                    <div className="flex justify-between text-xs font-semibold text-slate-400">
                      <span>Min: ₹{analytics?.market_summary?.lowest_historical_price || "0.00"}</span>
                      <span>Max: ₹{analytics?.market_summary?.highest_historical_price || "0.00"}</span>
                    </div>
                    <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden p-0.5 border border-purple-50">
                      <div className="bg-gradient-to-r from-purple-400 via-indigo-400 to-indigo-600 h-full rounded-full w-full"></div>
                    </div>
                  </div>
                </div>

                {/* Predictive ML Window */}
                <div className="bg-white rounded-xl p-5 border border-purple-100 space-y-4 shadow-sm">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <Activity className="h-4 w-4 text-purple-600" /> ML Forecast (7 Days)
                    </h3>
                    <select
                      value={activePlatform}
                      onChange={(e) => changePredictionPlatform(e.target.value)}
                      className="bg-slate-50 border border-purple-100 text-xs font-semibold text-purple-700 rounded px-2 py-1 focus:outline-none cursor-pointer"
                    >
                      <option value="Zepto">Zepto</option>
                      <option value="Blinkit">Blinkit</option>
                      <option value="Swiggy Instamart">Swiggy Instamart</option>
                    </select>
                  </div>

                  {prediction && prediction.predicted_price !== undefined ? (
                    <div className="bg-slate-50 p-4 rounded-lg border border-purple-50/50 space-y-3">
                      <div className="flex justify-between items-center text-sm">
                        <span className="font-medium text-slate-500">Current Price ({prediction.platform}):</span>
                        <span className="font-bold text-slate-700">₹{prediction.current_market_price}</span>
                      </div>
                      <div className="flex justify-between items-center border-t border-purple-100 pt-2 text-sm">
                        <span className="font-semibold text-purple-700">Predicted Price:</span>
                        <span className="text-xl font-black text-purple-600">₹{prediction.predicted_price}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs font-semibold mt-1 bg-white p-2 rounded border border-purple-100">
                        {prediction.market_trajectory?.includes('UPWARD') ? (
                          <TrendingUp className="h-4 w-4 text-rose-600" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-purple-600" />
                        )}
                        <span className={prediction.market_trajectory?.includes('UPWARD') ? 'text-rose-600' : 'text-purple-600'}>
                          Trajectory: {prediction.market_trajectory}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 italic text-center py-2">
                      Select platform to compute trajectory projection.
                    </div>
                  )}
                </div>

                {/* Platform Volatility Metric Tracker */}
                <div className="bg-white rounded-xl p-5 border border-purple-100 space-y-3 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Platform Volatility Index</h3>
                  <div className="space-y-2">
                    {(analytics?.platform_breakdown || []).map((row, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-slate-50 p-2.5 rounded border border-purple-50/30">
                        <span className="text-sm font-semibold text-slate-700">{row.platform}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono font-bold text-purple-600">σ = {row.volatility_index}</span>
                          <div className="w-16 bg-slate-200 h-1.5 rounded-full overflow-hidden">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full" 
                              style={{ width: `${Math.min(row.volatility_index * 20, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </div>
          )}
        </main>
      </div>

      {/* SYSTEM PERFORMANCE TELEMETRY BOTTOM PANEL */}
      {/* {latency && (
        <footer className="max-w-6xl w-full mx-auto mt-12 bg-white border border-purple-100 rounded-xl p-4 shadow-md flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-slate-600 text-sm font-semibold">
            <Cpu className="h-5 w-5 text-purple-600 animate-pulse" />
            <span>Engine Diagnostic Telemetry:</span>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-xs font-bold bg-slate-50 text-slate-600 px-3 py-1.5 rounded-lg border border-purple-50">
              <Zap className="h-4 w-4 text-amber-500" />
              <span>Backend API Latency: <span className="font-mono text-purple-600">{latency} ms</span></span>
            </div>

            <div className={`flex items-center space-x-2 text-xs font-bold px-3 py-1.5 rounded-lg border ${
              isCached 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-100' 
                : 'bg-indigo-50 text-indigo-700 border-indigo-100'
            }`}>
              <Database className={`h-4 w-4 ${isCached ? 'text-emerald-500' : 'text-indigo-500'}`} />
              <span>Pipeline Ingestion Strategy: <span>{isCached ? "IN-MEMORY CACHE HIT" : "LIVE SHOP SCRAPE"}</span></span>
            </div>
          </div>
        </footer>
      )} */}
    </div>
  );
}

export default App;