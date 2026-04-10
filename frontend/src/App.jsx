import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Leaf, LogOut, LayoutDashboard, Languages, CloudRain, Droplets, ThermometerSun, History, PieChart as PieChartIcon, MapPin, CalendarDays, Eye, EyeOff, Sun, Moon } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList } from 'recharts';
import illustration from './assets/illustration.png';
import bg from './assets/bg.png';
import dashboardBg from './assets/dashboard_bg.png';

const API_URL = 'http://localhost:5000/api';

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/refresh')) {
        return Promise.reject(error);
      }
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken });
          localStorage.setItem('token', res.data.token);
          localStorage.setItem('refresh_token', res.data.refresh_token);
          originalRequest.headers.Authorization = `Bearer ${res.data.token}`;
          return axios(originalRequest);
        } catch (err) {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/';
        }
      } else {
          localStorage.removeItem('token');
          window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

const Navbar = ({ onLogout, token, theme, toggleTheme }) => {
  const { t, i18n } = useTranslation();
  
  const toggleLanguage = () => {
    const nextLng = i18n.language === 'en' ? 'hi' : 'en';
    i18n.changeLanguage(nextLng);
  };

  return (
    <nav className="bg-white dark:bg-slate-900 text-nature-800 dark:text-slate-100 p-4 shadow-md flex justify-between items-center z-20 w-full relative drop-shadow-sm transition-colors border-b border-transparent dark:border-slate-800">
      <div className="flex items-center gap-2">
        <Leaf className="text-nature-600 dark:text-nature-400" />
        <span className="text-xl font-bold tracking-wider text-nature-800 dark:text-white">{t('app_title')}</span>
      </div>
      <div className="flex items-center gap-4">
        <button onClick={toggleTheme} className="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        <button onClick={toggleLanguage} className="bg-nature-100 dark:bg-nature-900/50 text-nature-800 dark:text-nature-200 px-3 py-1 rounded flex items-center gap-2 hover:bg-nature-200 dark:hover:bg-nature-800 transition-colors font-semibold">
          <Languages size={18} /> {i18n.language.toUpperCase()}
        </button>
        {token && (
          <>
            <Link to="/predict" className="hover:text-nature-600 dark:hover:text-nature-400 font-semibold">{t('predict')}</Link>
            <Link to="/dashboard" className="hover:text-nature-600 dark:hover:text-nature-400 font-semibold">{t('dashboard')}</Link>
            <button onClick={onLogout} className="flex items-center gap-1 text-slate-600 dark:text-slate-300 hover:text-red-500 font-semibold">
              <LogOut size={18} /> {t('logout')}
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

// --- SIGN UP PAGE ---
const SignUp = ({ setToken }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
        await axios.post(`${API_URL}/auth/register`, { username, email, password });
        const loginRes = await axios.post(`${API_URL}/auth/login`, { username, password });
        localStorage.setItem('token', loginRes.data.token);
        localStorage.setItem('refresh_token', loginRes.data.refresh_token);
        setToken(loginRes.data.token);
        navigate('/predict');
    } catch (err) {
        alert("Registration failed: " + (err.response?.data?.message || err.message));
    }
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center p-4 font-inter relative bg-cover bg-center" style={{ backgroundImage: `url(${bg})` }}>
      <div className="absolute inset-0 bg-black/40"></div>
      
      <div className="relative z-10 w-full max-w-md bg-white/10 backdrop-blur-md p-8 md:p-10 rounded-3xl shadow-2xl border border-white/20 text-white">
        <div className="text-center mb-10">
           <h2 className="text-4xl font-extrabold tracking-wide mb-3 drop-shadow-lg">Join AgriGuard</h2>
           <p className="text-md text-green-100 font-medium tracking-wide drop-shadow-md">Organic Products for a better world</p>
        </div>

        <form onSubmit={handleRegister} className="flex flex-col gap-6">
           <div className="flex flex-col gap-2">
             <label className="text-sm font-semibold tracking-wide text-green-50">Email</label>
             <input 
               type="email" placeholder="Your email address" 
               className="w-full bg-white/10 border border-white/30 p-3.5 rounded-xl text-md text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-green-400 focus:bg-white/20 transition-all shadow-inner"
               value={email} onChange={e => setEmail(e.target.value)} required />
           </div>

           <div className="flex flex-col gap-2">
             <label className="text-sm font-semibold tracking-wide text-green-50">Username</label>
             <input 
               type="text" placeholder="Choose a username" 
               className="w-full bg-white/10 border border-white/30 p-3.5 rounded-xl text-md text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-green-400 focus:bg-white/20 transition-all shadow-inner"
               value={username} onChange={e => setUsername(e.target.value)} required />
           </div>

           <div className="flex flex-col gap-2 relative">
             <label className="text-sm font-semibold tracking-wide text-green-50">Password</label>
             <div className="relative">
               <input 
                 type={showPassword ? "text" : "password"} placeholder="Create a secure password" 
                 className="w-full bg-white/10 border border-white/30 p-3.5 rounded-xl text-md text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-green-400 focus:bg-white/20 transition-all pr-12 shadow-inner"
                 value={password} onChange={e => setPassword(e.target.value)} required />
               <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-[14px] text-white/70 hover:text-white transition-colors">
                 {showPassword ? <EyeOff size={22} /> : <Eye size={22} />}
               </button>
             </div>
           </div>

           <button type="submit" className="mt-6 w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white p-4 rounded-xl font-bold text-lg shadow-[0_0_20px_rgba(34,197,94,0.4)] transition-all transform hover:-translate-y-0.5">
             Sign Up Now
           </button>
           
           <div className="text-center mt-4 text-sm font-medium">
              <span className="text-white/80">Already a member? </span>
              <Link to="/" className="font-bold text-green-300 hover:text-green-200 hover:underline">Log in</Link>
           </div>
        </form>
      </div>
    </div>
  );
};

// --- LOGIN PAGE ---
const Login = ({ setToken }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { username, password });
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      setToken(res.data.token);
      navigate('/predict');
    } catch (err) {
      alert("Login Failed: " + (err.response?.data?.message || 'Error'));
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center bg-[#f2cca0] dark:bg-transparent p-4 font-inter transition-colors">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl flex flex-col md:flex-row max-w-5xl w-full mx-auto overflow-hidden min-h-[600px] transition-colors">
        {/* Left Form Section */}
        <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
          {/* App Stores placeholder */}
          <div className="flex gap-4 mb-10 items-center justify-start opacity-70">
            <div className="font-bold text-sm flex items-center gap-1 dark:text-slate-300"><span className="text-blue-500 text-lg">▶</span> Google Play</div>
            <div className="font-bold text-sm bg-black dark:bg-slate-700 text-white px-2 py-1 rounded-md flex items-center gap-1"> App Store</div>
          </div>

          <div className="mb-8">
            <h3 className="text-slate-600 dark:text-slate-400 text-lg font-medium">Welcome</h3>
            <h2 className="text-4xl font-extrabold text-slate-800 dark:text-white mt-1">Log In</h2>
          </div>

          <form onSubmit={handleLogin} className="flex flex-col gap-5 w-full max-w-sm">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Your Email / Username</label>
              <input 
                type="text" placeholder="Your email or username" 
                className="border border-indigo-200 dark:border-slate-600 p-3 rounded-lg text-md focus:ring-2 focus:ring-[#1a6b32] focus:border-[#1a6b32] focus:outline-none transition-all placeholder:text-blue-200 dark:placeholder:text-slate-500 bg-white dark:bg-slate-700 dark:text-white"
                value={username} onChange={e => setUsername(e.target.value)} required />
            </div>

            <div className="flex flex-col gap-1 relative">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Password</label>
              <div className="relative">
                <input 
                  type={showPassword ? "text" : "password"} placeholder="Your password" 
                  className="w-full border border-slate-300 dark:border-slate-600 p-3 rounded-lg text-md focus:ring-2 focus:ring-[#1a6b32] focus:border-[#1a6b32] focus:outline-none transition-all pr-10 bg-white dark:bg-slate-700 dark:text-white"
                  value={password} onChange={e => setPassword(e.target.value)} required />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-600 dark:text-slate-400 dark:hover:text-slate-200">
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <div className="text-right mt-1">
                <a href="#" className="text-sm text-blue-500 hover:underline">Forgot password ?</a>
              </div>
            </div>

            <button type="submit" className="mt-4 w-full bg-[#1e5828] text-white p-3 rounded-lg font-bold hover:bg-[#1a4a22] shadow-md transition-all">
              Log In
            </button>
            <div className="text-center mt-2">
              <span className="text-sm text-slate-500 dark:text-slate-400">Don't have an account ? </span>
              <Link to="/signup" className="text-sm font-bold text-[#1e5828] dark:text-green-500 hover:underline">Sign up</Link>
            </div>
          </form>
        </div>

        {/* Right Illustration Section */}
        <div className="w-full md:w-1/2 bg-[#176a33] p-8 md:p-12 flex flex-col justify-between items-center text-center relative overflow-hidden hidden md:flex">
          {/* Subtle background shapes */}
          <div className="absolute top-[-50px] right-[-50px] w-64 h-64 bg-[#1e803f] rounded-full opacity-50 blur-2xl"></div>
          <div className="absolute bottom-[-100px] left-[-50px] w-80 h-80 bg-[#125828] rounded-full opacity-50 blur-2xl"></div>
          
          <div className="z-10 w-full flex justify-end">
            <h1 className="text-white text-2xl font-bold tracking-wide">AgriGuard <span className="block text-sm font-normal opacity-80">( Surveyor )</span></h1>
          </div>

          <div className="z-10 my-8 w-full max-w-sm">
            <img src={illustration} alt="Farmers Illustration" className="w-full drop-shadow-xl rounded-xl object-contain" />
          </div>

          <div className="z-10 mt-auto">
            <h2 className="text-3xl font-bold text-white mb-4">Empower Your Farming Journey</h2>
            <p className="text-green-100 text-sm max-w-sm mx-auto leading-relaxed">
              Leverage data-driven insights and AI predictions to maximize your crop yield and make informed agricultural decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const INDIAN_CITIES = [
  "Ahmedabad", "Amritsar", "Agra", "Bangalore", "Bhopal", "Bhubaneswar", "Chandigarh", "Chennai",
  "Coimbatore", "Delhi", "Faridabad", "Ghaziabad", "Guwahati", "Hyderabad", "Indore", "Jaipur",
  "Kanpur", "Kochi", "Kolkata", "Lucknow", "Ludhiana", "Meerut", "Mumbai", "Mysore", "Nagpur",
  "Nashik", "Patna", "Pune", "Rajkot", "Surat", "Thane", "Vadodara", "Varanasi", "Visakhapatnam"
];

// --- PREDICT PAGE ---
const PredictPage = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ N: '', P: '', K: '', ph: '', city: '', date: '', targetCrop: '', rainfall: '' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [cropImpact, setCropImpact] = useState("Normal");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleChange = (e) => setFormData({...formData, [e.target.name]: e.target.value});

  const handleCityChange = (e) => {
    setFormData({...formData, city: e.target.value});
    setShowSuggestions(true);
  };

  const selectCity = (city) => {
    setFormData({...formData, city});
    setShowSuggestions(false);
  };

  const filteredCities = INDIAN_CITIES.filter(c => c.toLowerCase().startsWith(formData.city.toLowerCase()));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setForecast([]);
    try {
      const weatherRes = await axios.get(`${API_URL}/weather`, { params: { city: formData.city }});
      const { temperature, humidity, rainfall } = weatherRes.data;

      const predPayload = {
        N: Number(formData.N), P: Number(formData.P), K: Number(formData.K), ph: Number(formData.ph),
        temperature, humidity, 
        rainfall, 
        date: formData.date, target_crop: formData.targetCrop
      };
      const predRes = await axios.post(`${API_URL}/predict`, predPayload);
      setResult({...predRes.data, cur_weather: weatherRes.data});

      axios.get(`${API_URL}/weather/forecast`, { params: { city: formData.city }})
           .then(res => {
               setForecast(res.data.forecast);
               setCropImpact(res.data.crop_impact || "Normal");
           })
           .catch(err => console.log(err));

    } catch (error) {
      alert("Error: " + (error.response?.data?.message || 'Server connection failed'));
    }
    setLoading(false);
  };

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];

  return (
    <div className="min-h-screen pb-10 font-inter relative bg-cover bg-center bg-fixed" style={{ backgroundImage: `url(${dashboardBg})` }}>
      <div className="absolute inset-0 bg-black/40"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto flex flex-col gap-10 px-4 md:px-8">
        
        {/* Header Section */}
        <div className="text-center mt-6 mb-4 md:mt-8 md:mb-6 animate-fade-in">
           <span className="bg-white/90 text-green-800 font-bold px-5 py-1.5 rounded-full text-xs tracking-widest shadow-lg inline-block mb-4 uppercase backdrop-blur-sm">Welcome to Agriculture</span>
           <h1 className="text-5xl md:text-6xl font-extrabold text-white drop-shadow-xl mb-4">
              Agriculture <span className="text-[#ffeb99]">from a</span><br />Fresh Perspective
           </h1>
           <p className="text-white pt-2 max-w-2xl mx-auto text-lg drop-shadow-lg font-medium">
              Leverage data-driven insights and seasonal conditions to maximize your harvest and make informed, confident farming decisions.
           </p>
        </div>

        <div className={`grid grid-cols-1 gap-8 items-start ${result ? 'lg:grid-cols-2' : 'max-w-2xl mx-auto w-full'}`}>
          
          {/* Form Section */}
          <div className="bg-white/95 dark:bg-slate-800/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/40 dark:border-slate-700 h-fit transition-colors">
          <h2 className="text-3xl font-semibold mb-6 flex items-center gap-2 dark:text-white"><Leaf className="text-nature-600 dark:text-nature-400"/> {t('predict')}</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
            <div className="col-span-full relative">
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">{t('city_label')}</label>
               <input 
                 name="city" required placeholder="e.g. Pune" 
                 value={formData.city} 
                 onChange={handleCityChange} 
                 onFocus={() => setShowSuggestions(true)}
                 onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                 className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 bg-transparent focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none dark:text-white dark:placeholder:text-slate-500 transition-colors"
                 autoComplete="off"
               />
               {showSuggestions && filteredCities.length > 0 && (
                 <ul className="absolute z-50 w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 mt-1 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                   {filteredCities.map((city, idx) => (
                     <li 
                       key={idx} 
                       onMouseDown={(e) => { e.preventDefault(); selectCity(city); }}
                       className="p-3 hover:bg-nature-50 dark:hover:bg-slate-700 cursor-pointer text-slate-700 dark:text-slate-200 font-medium border-b border-slate-100 dark:border-slate-700 last:border-0 transition-colors"
                     >
                       {city}
                     </li>
                   ))}
                 </ul>
               )}
            </div>
            
            <div className="col-span-full">
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">Expected Month/Year of Sowing</label>
               <input name="date" type="month" required value={formData.date} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none text-slate-700 dark:text-white bg-transparent transition-colors color-scheme-dark"/>
            </div>

            <div>
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">{t('n_label')}</label>
               <input name="N" type="number" required placeholder="N ratio" value={formData.N} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none bg-transparent dark:text-white transition-colors"/>
            </div>
            <div>
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">{t('p_label')}</label>
               <input name="P" type="number" required placeholder="P ratio" value={formData.P} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none bg-transparent dark:text-white transition-colors"/>
            </div>
            <div>
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">{t('k_label')}</label>
               <input name="K" type="number" required placeholder="K ratio" value={formData.K} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none bg-transparent dark:text-white transition-colors"/>
            </div>
            <div>
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">{t('ph_label')}</label>
               <input name="ph" type="number" step="0.1" required placeholder="6.5" value={formData.ph} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none bg-transparent dark:text-white transition-colors"/>
            </div>

            <div className="col-span-full">
               <label className="text-sm text-slate-600 dark:text-slate-400 font-medium">Your Target/Desired Crop (Optional comparison)</label>
               <input name="targetCrop" placeholder="e.g. Maize" value={formData.targetCrop} onChange={handleChange} className="w-full text-lg border-b-2 border-slate-300 dark:border-slate-600 p-2 focus:border-nature-500 dark:focus:border-nature-400 focus:outline-none bg-transparent dark:text-white transition-colors"/>
            </div>
            <div className="col-span-full mt-4">
              <button disabled={loading} className="w-full uppercase tracking-wider font-bold bg-nature-600 text-white p-4 rounded-xl shadow-md hover:bg-nature-700 transition-all disabled:opacity-50">
                {loading ? "Analyzing Soil & Weather..." : t('predict_button')}
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className="flex flex-col gap-6 animate-fade-in">
            {/* Top Analysis Card */}
            <div className="bg-white/95 dark:bg-slate-800/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/40 dark:border-slate-700 transition-colors">
              <div className={`p-6 bg-nature-50 dark:bg-slate-700/50 rounded-xl mb-6 flex flex-col md:flex-row items-center gap-6 ${result.wiki_info?.image_url ? 'justify-between' : 'justify-center text-center'} transition-colors`}>
                <div className={result.wiki_info?.image_url ? 'text-left' : 'text-center'}>
                  <h3 className="text-xl text-slate-600 dark:text-slate-300 block">{t('best_crop')}</h3>
                  <h1 className="text-5xl font-extrabold text-nature-700 dark:text-nature-400 tracking-tight mt-2">{result.crop}</h1>
                  <p className="mt-2 text-nature-600 dark:text-nature-300 font-medium bg-nature-100 dark:bg-nature-900/40 inline-block px-3 py-1 rounded-full">{t('confidence')} {result.confidence}%</p>
                  
                  {result.wiki_info && result.wiki_info.extract && (
                    <p className="mt-4 text-slate-600 dark:text-slate-300 text-sm max-w-sm line-clamp-3">{result.wiki_info.extract}</p>
                  )}
                </div>
                
                {result.wiki_info?.image_url && (
                  <div className="flex-shrink-0">
                    <img src={result.wiki_info.image_url} alt={result.crop} className="w-40 h-40 object-cover rounded-full shadow-lg border-4 border-white dark:border-slate-600" />
                  </div>
                )}
              </div>
              
              {result.fallback && (
               <div className="bg-red-50 dark:bg-red-900/30 border-l-4 border-red-500 dark:border-red-400 p-4 mb-4 rounded-lg flex items-start">
                 <p className="text-red-700 dark:text-red-300 font-medium text-sm flex gap-2"><span className="text-red-800 dark:text-red-400 text-lg">⚠️</span> {result.fallback}</p>
               </div>
              )}

              {/* Geo & Season Info + New Advisory */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {result.geo_advice && (
                  <>
                    <div className="bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-600 transition-colors">
                      <div className="flex items-center gap-2 text-slate-800 dark:text-slate-200 font-bold mb-1"><CalendarDays className="text-nature-600 dark:text-nature-400" size={18}/> Best Sowing Time</div>
                      <p className="text-slate-600 dark:text-slate-300 text-sm">{result.geo_advice.season}</p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-600 transition-colors">
                      <div className="flex items-center gap-2 text-slate-800 dark:text-slate-200 font-bold mb-1"><MapPin className="text-blue-500 dark:text-blue-400" size={18}/> Ideal Regions</div>
                      <p className="text-slate-600 dark:text-slate-300 text-sm">{result.geo_advice.regions}</p>
                    </div>
                  </>
                )}
                {result.soil_health && (
                    <div className="bg-emerald-50 dark:bg-emerald-900/30 p-4 rounded-xl shadow-sm border border-emerald-100 dark:border-emerald-800/50 transition-colors">
                      <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold mb-1"><Leaf className="text-emerald-600 dark:text-emerald-400" size={18}/> Soil Health</div>
                      <p className="text-emerald-700 dark:text-emerald-200 text-sm font-medium">{result.soil_health}</p>
                    </div>
                )}
                {result.irrigation && (
                    <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-xl shadow-sm border border-blue-100 dark:border-blue-800/50 transition-colors">
                      <div className="flex items-center gap-2 text-blue-800 dark:text-blue-300 font-bold mb-1"><Droplets className="text-blue-500 dark:text-blue-400" size={18}/> Irrigation Schedule</div>
                      <p className="text-blue-700 dark:text-blue-200 text-sm font-medium">{result.irrigation}</p>
                    </div>
                )}
              </div>

              {/* Fertilizer Guide */}
              <div className="mb-4">
                <h3 className="font-bold text-slate-800 dark:text-slate-200 text-lg mb-2">{t('fertilizer')}</h3>
                <ul className="list-disc pl-5 text-slate-600 dark:text-slate-300 text-md leading-relaxed transition-colors">
                  {result.fertilizer.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            </div>

            {/* Graphical Analytics Card */}
            {result.chart_data && (
              <div className="bg-white/95 dark:bg-slate-800/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/40 dark:border-slate-700 transition-colors">
                 <h3 className="font-bold text-slate-800 dark:text-slate-200 text-lg mb-4">Probability Distribution (Top 5)</h3>
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="h-[200px] w-full">
                     <ResponsiveContainer width="100%" height="100%">
                       <PieChart>
                         <Pie data={result.chart_data} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2} dataKey="value">
                           {result.chart_data.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                         </Pie>
                         <RechartsTooltip />
                       </PieChart>
                     </ResponsiveContainer>
                   </div>
                   <div className="h-[200px] w-full">
                     <ResponsiveContainer width="100%" height="100%">
                       <BarChart data={result.chart_data} layout="vertical" margin={{top: 5, right: 20, left: 20, bottom: 5}}>
                         <XAxis type="number" hide />
                         <YAxis dataKey="name" type="category" width={80} tick={{fontSize: 12, fill: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569'}} />
                         <RechartsTooltip />
                         <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                           {result.chart_data.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                           ))}
                         </Bar>
                       </BarChart>
                     </ResponsiveContainer>
                   </div>
                 </div>
              </div>
            )}
            
            {/* Target Crop Comparison Graph */}
            {result.comparison_data && result.comparison_data.length > 0 && (
              <div className="bg-white/95 dark:bg-slate-800/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/40 dark:border-slate-700 transition-colors">
                 <h3 className="font-bold text-slate-800 dark:text-slate-200 text-lg mb-4">Target vs Recommendation</h3>
                 <div className="h-[250px] w-full">
                   <ResponsiveContainer width="100%" height="100%">
                     <BarChart data={result.comparison_data} margin={{top: 20, right: 30, left: 20, bottom: 5}}>
                       <CartesianGrid strokeDasharray="3 3" />
                       <XAxis dataKey="name" tick={{fontSize: 14, fontWeight: 'bold', fill: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569'}} />
                       <YAxis label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft', fill: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569' }} />
                       <RechartsTooltip formatter={(value, name, props) => [`${value}%`, `Crop: ${props.payload.crop}`]} />
                       <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={60} minPointSize={5}>
                         <LabelList dataKey="value" position="top" formatter={(val) => `${val}%`} style={{fontWeight: 'bold', fill: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569'}} />
                         {result.comparison_data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? '#22c55e' : '#f59e0b'} />
                         ))}
                       </Bar>
                     </BarChart>
                   </ResponsiveContainer>
                 </div>
                 <div className="mt-4 text-center text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-700/50 p-3 rounded-lg border border-slate-200 dark:border-slate-600 transition-colors">
                    The AI suggests <strong className="text-nature-700 dark:text-nature-400">{result.comparison_data[0].crop}</strong> with <strong>{result.comparison_data[0].value}%</strong> confidence, 
                    while your input <strong className="text-amber-600 dark:text-amber-400">{result.comparison_data[1].crop}</strong> has <strong>{result.comparison_data[1].value}%</strong> suitability.
                 </div>
              </div>
            )}

            {/* Weather Forecast */}
            {forecast.length > 0 && (
              <div className="bg-white/95 dark:bg-slate-800/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/40 dark:border-slate-700 transition-colors">
                <h3 className="font-bold text-slate-800 dark:text-slate-200 text-lg mb-3">{t('weather_forecast')}</h3>
                {cropImpact !== "Normal" && (
                   <div className="bg-orange-50 dark:bg-orange-900/30 border-l-4 border-orange-400 dark:border-orange-500 p-3 mb-4 rounded text-sm font-medium text-orange-800 dark:text-orange-300">
                     Forecast Alert: {cropImpact}
                   </div>
                )}
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                  {forecast.slice(0, 5).map((f, i) => (
                    <div key={i} className="min-w-[100px] flex-shrink-0 bg-blue-50 dark:bg-slate-700 p-3 rounded-lg border border-blue-100 dark:border-slate-600 text-center transition-colors">
                      <div className="text-xs text-slate-500 dark:text-slate-400 font-bold mb-1">{f.date.slice(5, 10).replace('-', '/')}</div>
                      <div className="text-lg font-bold text-slate-800 dark:text-white">{Math.round(f.temperature)}°</div>
                      <div className="text-xs text-blue-600 dark:text-blue-400 capitalize mt-1">{f.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

// --- DASHBOARD PAGE ---
const DashboardPage = () => {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState([]);
  const [historyFilter, setHistoryFilter] = useState({ date: '' });

  useEffect(() => {
    fetchDashboardData();
  }, [historyFilter.date]);
  
  const fetchDashboardData = () => {
    let url = `${API_URL}/dashboard/history`;
    if (historyFilter.date) {
        url += `?start_date=${historyFilter.date}-01&end_date=${historyFilter.date}-31`;
    }
    axios.get(url)
      .then(res => setHistory(res.data.history))
      .catch(console.error);

    axios.get(`${API_URL}/dashboard/stats`)
      .then(res => setStats(res.data.crop_stats))
      .catch(console.error);
  }

  const handleExportCsv = async () => {
    try {
        const res = await axios.get(`${API_URL}/dashboard/export`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'predictions_export.csv');
        document.body.appendChild(link);
        link.click();
    } catch (err) {
        alert('Failed to download CSV');
    }
  };

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'];

  return (
    <div className="min-h-screen p-4 md:p-8 bg-slate-50 dark:bg-slate-900 font-inter transition-colors">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-md border-t-4 border-nature-600 transition-colors">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2 dark:text-white"><PieChartIcon className="text-nature-600"/> Predicted Crops Analytics</h2>
            {stats.length > 0 ? (
               <div className="h-[300px] w-full">
                 <ResponsiveContainer width="100%" height="100%">
                   <PieChart>
                     <Pie data={stats} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                       {stats.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                     </Pie>
                     <RechartsTooltip />
                     <Legend verticalAlign="bottom" height={36}/>
                   </PieChart>
                 </ResponsiveContainer>
               </div>
            ) : <p className="text-slate-500 dark:text-slate-400">No predictions yet.</p>}
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-md border-t-4 border-blue-600 flex flex-col max-h-[600px] transition-colors">
            <div className="flex justify-between items-center mb-6">
               <h2 className="text-2xl font-semibold flex items-center gap-2 dark:text-white"><History className="text-blue-600"/> History</h2>
               <div className="flex gap-2">
                 <input type="month" value={historyFilter.date} onChange={e => setHistoryFilter({...historyFilter, date: e.target.value})} className="border dark:border-slate-600 rounded px-2 py-1 text-sm bg-slate-50 dark:bg-slate-700 dark:text-white outline-none" />
                 <button onClick={handleExportCsv} className="bg-slate-800 dark:bg-slate-950 text-white text-sm font-bold px-3 py-1 rounded hover:bg-slate-700 dark:hover:bg-slate-900 transition">Export CSV</button>
               </div>
            </div>
            
            <div className="space-y-4 overflow-y-auto pr-2 flex-grow">
              {history.length > 0 ? history.map((h, i) => (
                <div key={i} className="p-3 border border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/50 rounded-lg flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    {h.result.wiki_info?.image_url ? (
                      <img src={h.result.wiki_info.image_url} alt="crop" className="w-12 h-12 rounded-full object-cover shadow-sm border border-white dark:border-slate-600" />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-nature-200 dark:bg-slate-600 flex items-center justify-center text-nature-600 dark:text-nature-400"><Leaf size={20}/></div>
                    )}
                    <div>
                      <span className="font-bold text-slate-800 dark:text-white text-lg block">{h.result.crop}</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400">{new Date(h.result.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-sm bg-nature-100 dark:bg-nature-900/40 text-nature-700 dark:text-nature-300 font-bold py-1 px-2 rounded-full mb-1">{h.result.confidence}% Confidence</span>
                    <span className="text-[10px] text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-600">Model: {h.result.selected_model || "XGBoost"}</span>
                  </div>
                </div>
              )) : <p className="text-slate-500 dark:text-slate-400">No history available.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- MAIN APP Component ---
export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setToken(null);
  };

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 font-inter transition-colors text-slate-900 dark:text-slate-100">
        <Navbar onLogout={handleLogout} token={token} theme={theme} toggleTheme={toggleTheme} />
        <Routes>
          <Route path="/" element={!token ? <Login setToken={setToken} /> : <PredictPage />} />
          <Route path="/signup" element={!token ? <SignUp setToken={setToken} /> : <PredictPage />} />
          <Route path="/predict" element={token ? <PredictPage /> : <Login setToken={setToken} />} />
          <Route path="/dashboard" element={token ? <DashboardPage /> : <Login setToken={setToken} />} />
        </Routes>
      </div>
    </Router>
  );
}
