// Configuration
// Configuration - Update this URL to match your backend
const API_BASE_URL = 'http://localhost:8000/api/weather';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const weatherContent = document.getElementById('weatherContent');

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load default weather on page load
    loadWeather();
    
    // Handle search form submission
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            loadWeather(query);
        } else {
            loadWeather();
        }
    });
});

// Fetch weather data from Python backend API
async function loadWeather(query = null, lat = null, lon = null) {
    showLoading();
    hideError();
    
    try {
        let url = `${API_BASE_URL}/summary`;
        const params = new URLSearchParams();
        
        if (query) {
            params.append('q', query);
        } else if (lat && lon) {
            params.append('lat', lat);
            params.append('lon', lon);
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        console.log('Fetching weather from:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch weather data: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Weather data received:', data);
        
        renderWeather(data);
        hideLoading();
        
    } catch (error) {
        console.error('Error loading weather:', error);
        showError(error.message);
        hideLoading();
    }
}

// Render weather data to the page
function renderWeather(data) {
    // Update current weather
    document.getElementById('place').textContent = data.place || 'Unknown';
    document.getElementById('date').textContent = data.date || '--';
    document.getElementById('currentIcon').textContent = data.current?.icon || '☁️';
    document.getElementById('currentTemp').textContent = `${data.current?.temp || '--'}°`;
    document.getElementById('feelsLike').textContent = `${data.current?.feels_like || '--'}°`;
    document.getElementById('humidity').textContent = `${data.current?.humidity || '--'}%`;
    document.getElementById('wind').textContent = data.current?.wind || '--';
    document.getElementById('precip').textContent = data.current?.precip || '--';
    
    // Render daily forecast
    const dailyList = document.getElementById('dailyList');
    dailyList.innerHTML = '';
    
    if (data.daily && Array.isArray(data.daily)) {
        data.daily.forEach(day => {
            const li = document.createElement('li');
            li.className = 'day card';
            li.innerHTML = `
                <p class="day__name">${day.name}</p>
                <span class="day__icon" aria-hidden="true">${day.icon}</span>
                <p class="day__temps"><strong>${day.hi}°</strong><span>${day.lo}°</span></p>
            `;
            dailyList.appendChild(li);
        });
    }
    
    // Render hourly forecast
    const hourlyList = document.getElementById('hourlyList');
    hourlyList.innerHTML = '';
    
    if (data.hourly && Array.isArray(data.hourly)) {
        data.hourly.forEach(hour => {
            const li = document.createElement('li');
            li.className = 'hour';
            li.innerHTML = `
                <span class="hour__time">${hour.time}</span>
                <span class="hour__icon" aria-hidden="true">${hour.icon}</span>
                <span class="hour__temp">${hour.temp}°</span>
            `;
            hourlyList.appendChild(li);
        });
    }
    
    weatherContent.style.display = 'block';
}

// UI Helper Functions
function showLoading() {
    loadingEl.style.display = 'block';
    weatherContent.style.display = 'none';
}

function hideLoading() {
    loadingEl.style.display = 'none';
}

function showError(message) {
    errorEl.querySelector('p').textContent = `Error: ${message}`;
    errorEl.style.display = 'block';
    weatherContent.style.display = 'none';
}

function hideError() {
    errorEl.style.display = 'none';
}