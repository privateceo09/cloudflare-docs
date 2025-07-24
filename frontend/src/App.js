import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.defaults.headers.common['Content-Type'] = 'application/json';

const App = () => {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [assets, setAssets] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Auth states
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({ email: '', username: '', password: '' });

  // Investment states
  const [selectedAsset, setSelectedAsset] = useState('');
  const [investmentAmount, setInvestmentAmount] = useState('');
  const [multiplier, setMultiplier] = useState(1);

  // Admin states
  const [adminStats, setAdminStats] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setCurrentView('dashboard');
      fetchInitialData();
    }
  }, []);

  const fetchInitialData = async () => {
    try {
      await Promise.all([
        fetchAssets(),
        fetchPortfolio(),
        fetchLeaderboard()
      ]);
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  };

  const fetchAssets = async () => {
    try {
      const response = await axios.get(`${API}/assets`);
      setAssets(response.data);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
    }
  };

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`${API}/portfolio`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    }
  };

  const fetchAdminStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`);
      setAdminStats(response.data);
    } catch (error) {
      console.error('Failed to fetch admin stats:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/auth/login`, loginData);
      const { token, user: userData } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      setUser(userData);
      setCurrentView('dashboard');
      await fetchInitialData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/auth/register`, registerData);
      const { token, user: userData } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      setUser(userData);
      setCurrentView('dashboard');
      await fetchInitialData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleInvestment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await axios.post(`${API}/invest?asset_symbol=${selectedAsset}&amount=${investmentAmount}&multiplier=${multiplier}`);
      await fetchPortfolio();
      setInvestmentAmount('');
      setSelectedAsset('');
      setMultiplier(1);
      
      // Update user balance
      const updatedUser = { ...user, balance: user.balance - parseFloat(investmentAmount) };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error) {
      setError(error.response?.data?.detail || 'Investment failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setCurrentView('login');
    setAssets([]);
    setPortfolio([]);
    setLeaderboard([]);
  };

  const createAdminUser = async () => {
    try {
      const response = await axios.post(`${API}/admin/create-admin`);
      alert(`Admin created: ${response.data.email} / ${response.data.password}`);
    } catch (error) {
      console.error('Failed to create admin:', error);
    }
  };

  if (currentView === 'login') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-600">
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="relative z-10 flex items-center justify-center min-h-screen px-4">
          <div className="max-w-md w-full">
            <div className="bg-white rounded-xl shadow-2xl p-8">
              <div className="text-center mb-8">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <span className="text-white text-2xl font-bold">X</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-800 mb-2">XSpace Investment</h1>
                <p className="text-gray-600">Trade Crypto & Tesla with Confidence</p>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              <div className="flex mb-6">
                <button
                  onClick={() => setCurrentView('login')}
                  className={`flex-1 px-4 py-2 rounded-l-lg font-medium ${currentView === 'login' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  Login
                </button>
                <button
                  onClick={() => setCurrentView('register')}
                  className={`flex-1 px-4 py-2 rounded-r-lg font-medium ${currentView === 'register' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  Register
                </button>
              </div>

              {currentView === 'login' ? (
                <form onSubmit={handleLogin} className="space-y-4">
                  <input
                    type="email"
                    placeholder="Email"
                    value={loginData.email}
                    onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
                  >
                    {loading ? 'Logging in...' : 'Login'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="space-y-4">
                  <input
                    type="email"
                    placeholder="Email"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Username"
                    value={registerData.username}
                    onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    value={registerData.password}
                    onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </button>
                </form>
              )}

              <div className="mt-6 text-center">
                <button
                  onClick={createAdminUser}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Create Admin User
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold">X</span>
              </div>
              <h1 className="text-xl font-bold text-gray-800">XSpace Investment</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-lg font-medium ${currentView === 'dashboard' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('invest')}
                className={`px-4 py-2 rounded-lg font-medium ${currentView === 'invest' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                Invest
              </button>
              <button
                onClick={() => setCurrentView('leaderboard')}
                className={`px-4 py-2 rounded-lg font-medium ${currentView === 'leaderboard' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                Leaderboard
              </button>
              {user?.is_admin && (
                <button
                  onClick={() => {
                    setCurrentView('admin');
                    fetchAdminStats();
                  }}
                  className={`px-4 py-2 rounded-lg font-medium ${currentView === 'admin' ? 'bg-purple-600 text-white' : 'text-purple-700 hover:bg-purple-100'}`}
                >
                  Admin
                </button>
              )}
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Balance:</span>
                <span className="font-semibold text-green-600">${user?.balance?.toFixed(2)}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {currentView === 'dashboard' && (
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Welcome back, {user?.username}!</h2>
              <p className="text-gray-600">Track your investments and explore new opportunities</p>
            </div>

            {/* Hero Section with Background Image */}
            <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 mb-8 overflow-hidden">
              <div className="absolute inset-0 opacity-20">
                <img 
                  src="https://images.unsplash.com/photo-1655804472974-67e35a039ec6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwxfHxjcnlwdG8lMjB0cmFkaW5nfGVufDB8fHxibHVlfDE3NTMzMjk3NjJ8MA&ixlib=rb-4.1.0&q=85"
                  alt="Crypto Trading"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="relative z-10 text-white">
                <h3 className="text-2xl font-bold mb-4">Your Investment Portfolio</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <h4 className="text-lg font-semibold mb-2">Portfolio Value</h4>
                    <p className="text-3xl font-bold">
                      ${portfolio.reduce((sum, inv) => sum + (inv.quantity * inv.current_price), 0).toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <h4 className="text-lg font-semibold mb-2">Total P&L</h4>
                    <p className={`text-3xl font-bold ${portfolio.reduce((sum, inv) => sum + inv.profit_loss, 0) >= 0 ? 'text-green-200' : 'text-red-200'}`}>
                      ${portfolio.reduce((sum, inv) => sum + inv.profit_loss, 0).toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <h4 className="text-lg font-semibold mb-2">Active Investments</h4>
                    <p className="text-3xl font-bold">{portfolio.length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Portfolio */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Your Investments</h3>
              {portfolio.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Asset</th>
                        <th className="text-left py-3 px-4">Quantity</th>
                        <th className="text-left py-3 px-4">Purchase Price</th>
                        <th className="text-left py-3 px-4">Current Price</th>
                        <th className="text-left py-3 px-4">Multiplier</th>
                        <th className="text-left py-3 px-4">P&L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.map((investment) => (
                        <tr key={investment.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div>
                              <div className="font-semibold">{investment.symbol}</div>
                              <div className="text-sm text-gray-600">{investment.asset_name}</div>
                            </div>
                          </td>
                          <td className="py-3 px-4">{investment.quantity.toFixed(4)}</td>
                          <td className="py-3 px-4">${investment.purchase_price.toFixed(2)}</td>
                          <td className="py-3 px-4">${investment.current_price.toFixed(2)}</td>
                          <td className="py-3 px-4">
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                              {investment.multiplier}x
                            </span>
                          </td>
                          <td className={`py-3 px-4 font-semibold ${investment.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${investment.profit_loss.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">You haven't made any investments yet</p>
                  <button
                    onClick={() => setCurrentView('invest')}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Start Investing
                  </button>
                </div>
              )}
            </div>

            {/* Market Overview */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Market Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {assets.map((asset) => (
                  <div key={asset.symbol} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-lg">{asset.symbol}</h4>
                        <p className="text-sm text-gray-600">{asset.name}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${asset.asset_type === 'crypto' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                        {asset.asset_type}
                      </span>
                    </div>
                    <div className="flex justify-between items-end">
                      <div>
                        <p className="text-2xl font-bold">${asset.current_price.toFixed(2)}</p>
                        <p className={`text-sm ${asset.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {asset.price_change_percentage_24h >= 0 ? '+' : ''}{asset.price_change_percentage_24h.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {currentView === 'invest' && (
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Make an Investment</h2>
              <p className="text-gray-600">Choose your asset and investment amount</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Investment Form</h3>
                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                  </div>
                )}
                <form onSubmit={handleInvestment} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Select Asset</label>
                    <select
                      value={selectedAsset}
                      onChange={(e) => setSelectedAsset(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value="">Choose an asset</option>
                      {assets.map((asset) => (
                        <option key={asset.symbol} value={asset.symbol}>
                          {asset.name} ({asset.symbol}) - ${asset.current_price.toFixed(2)}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Investment Amount ($)</label>
                    <input
                      type="number"
                      min="1"
                      max={user?.balance}
                      step="0.01"
                      value={investmentAmount}
                      onChange={(e) => setInvestmentAmount(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter amount to invest"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Multiplier (Risk Level)</label>
                    <select
                      value={multiplier}
                      onChange={(e) => setMultiplier(parseFloat(e.target.value))}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value={0.5}>0.5x (Low Risk)</option>
                      <option value={1}>1x (Normal)</option>
                      <option value={1.5}>1.5x (Medium Risk)</option>
                      <option value={2}>2x (High Risk)</option>
                      <option value={3}>3x (Very High Risk)</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !selectedAsset || !investmentAmount}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
                  >
                    {loading ? 'Processing Investment...' : 'Invest Now'}
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Available Assets</h3>
                <div className="space-y-4">
                  {assets.map((asset) => (
                    <div key={asset.symbol} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold">{asset.name}</h4>
                          <p className="text-sm text-gray-600">{asset.symbol}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${asset.asset_type === 'crypto' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                          {asset.asset_type}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xl font-bold">${asset.current_price.toFixed(2)}</span>
                        <span className={`text-sm font-medium ${asset.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {asset.price_change_percentage_24h >= 0 ? '+' : ''}{asset.price_change_percentage_24h.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'leaderboard' && (
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Leaderboard</h2>
              <p className="text-gray-600">Top performing traders on the platform</p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Rank</th>
                      <th className="text-left py-3 px-4">Trader</th>
                      <th className="text-left py-3 px-4">Total Invested</th>
                      <th className="text-left py-3 px-4">Total P&L</th>
                      <th className="text-left py-3 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((trader, index) => (
                      <tr key={trader.username} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <span className={`font-bold text-lg ${index < 3 ? 'text-yellow-600' : 'text-gray-600'}`}>
                            #{index + 1}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${trader.is_bot ? 'bg-gray-400' : 'bg-blue-500'} text-white font-semibold`}>
                              {trader.username.charAt(0).toUpperCase()}
                            </div>
                            <span className="font-semibold">{trader.username}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">${trader.total_invested.toFixed(2)}</td>
                        <td className={`py-3 px-4 font-semibold ${trader.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ${trader.total_profit_loss.toFixed(2)}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${trader.is_bot ? 'bg-gray-100 text-gray-800' : 'bg-blue-100 text-blue-800'}`}>
                            {trader.is_bot ? 'Bot' : 'Human'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {currentView === 'admin' && user?.is_admin && (
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Admin Dashboard</h2>
              <p className="text-gray-600">Platform management and statistics</p>
            </div>

            {adminStats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Users</h3>
                  <p className="text-3xl font-bold text-blue-600">{adminStats.total_users}</p>
                </div>
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Bot Users</h3>
                  <p className="text-3xl font-bold text-gray-600">{adminStats.total_bots}</p>
                </div>
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Investments</h3>
                  <p className="text-3xl font-bold text-green-600">{adminStats.total_investments}</p>
                </div>
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Platform Value</h3>
                  <p className="text-3xl font-bold text-purple-600">${adminStats.total_platform_value.toFixed(2)}</p>
                </div>
              </div>
            )}

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Admin Controls</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                  Manage Users
                </button>
                <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
                  Update Asset Prices
                </button>
                <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700">
                  Generate Reports
                </button>
                <button className="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700">
                  Platform Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;