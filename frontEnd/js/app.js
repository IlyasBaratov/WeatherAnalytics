    const API_BASE_URL = 'https://api.weatherdemo.online/api/weather';
// const API_BASE_URL = 'http://localhost:8000/api/weather';

const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const weatherContent = document.getElementById('weatherContent');
const favoritesList = document.getElementById('favoritesList');
const saveFavoriteBtn = document.getElementById('saveFavoriteBtn');
const themeToggle = document.getElementById('themeToggle');
const daysSelect = document.getElementById('daysSelect');

let currentPlace = null;

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

themeToggle.addEventListener('click', () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadWeather();
  loadFavorites();

  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (query) {
      loadWeather(query);
    } else {
      loadWeather();
    }
  });

  saveFavoriteBtn.addEventListener('click', async () => {
    try {
      const q = (searchInput.value && searchInput.value.trim()) || currentPlace;
      if (!q) return;
      const res = await fetch(`${API_BASE_URL}/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q })
      });
      if (!res.ok) throw new Error('Failed to save favorite');
      await loadFavorites();
    } catch (err) {
      console.error(err);
      showError('Could not save favorite');
    }
  });
});

async function loadWeather(query = null, lat = null, lon = null) {
  showLoading();
  hideError();

  try {
    let url = `${API_BASE_URL}/summary`;
    const params = new URLSearchParams();

    if (daysSelect && daysSelect.value) {
      params.append('days', daysSelect.value);
    }
    if (query) {
      params.append('q', query);
    } else if (lat && lon) {
      params.append('lat', lat);
      params.append('lon', lon);
    }

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch weather data: ${response.statusText}`);
    }

    const data = await response.json();
    renderWeather(data);
    hideLoading();

  } catch (error) {
    console.error('Error loading weather:', error);
    showError(error.message);
    hideLoading();
  }
}

function renderWeather(data) {
  currentPlace = data.place || 'Unknown';
  document.getElementById('place').textContent = currentPlace;
  document.getElementById('date').textContent = data.date || '--';
  document.getElementById('currentIcon').textContent = data.current?.icon || '☁️';
  document.getElementById('currentTemp').textContent = `${data.current?.temp || '--'}°`;
  document.getElementById('feelsLike').textContent = `${data.current?.feels_like || '--'}°`;
  document.getElementById('humidity').textContent = `${data.current?.humidity || '--'}%`;
  document.getElementById('wind').textContent = data.current?.wind || '--';
  document.getElementById('precip').textContent = data.current?.precip || '--';

  const dailyList = document.getElementById('dailyList');
  dailyList.innerHTML = '';

  if (data.daily && Array.isArray(data.daily)) {
    data.daily.forEach(day => {
      const li = document.createElement('li');
      li.className = 'day';
      li.innerHTML = `
        <p class="day__name">${day.name}</p>
        <span class="day__icon" aria-hidden="true">${day.icon}</span>
        <p class="day__temps"><strong>${day.hi}°</strong><span>${day.lo}°</span></p>
      `;
      dailyList.appendChild(li);
    });
  }

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

  // Render YouTube videos
  const videosList = document.getElementById('videosList');
  if (videosList) {
    videosList.innerHTML = '';

    if (data.videos && Array.isArray(data.videos) && data.videos.length > 0) {
      data.videos.forEach(video => {
        const li = document.createElement('li');
        li.className = 'video-card';

        const publishedDate = video.published_at
          ? new Date(video.published_at).toLocaleDateString()
          : 'Unknown date';

        li.innerHTML = `
          ${video.thumbnail_url ? `<img src="${video.thumbnail_url}" alt="${video.title}" class="video-card__thumbnail">` : ''}
          <div class="video-card__content">
            <h4 class="video-card__title">${video.title || 'Untitled Video'}</h4>
            <div class="video-card__meta">
              <span class="video-card__channel">${video.channel_title || 'Unknown Channel'}</span>
              <span class="video-card__date">${publishedDate}</span>
            </div>
            <a href="${video.url}" target="_blank" rel="noopener noreferrer" class="video-card__link">
              ▶ Watch on YouTube
            </a>
          </div>
        `;
        videosList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.className = 'videos__empty';
      li.textContent = 'No local news videos available';
      videosList.appendChild(li);
    }
  }

  weatherContent.style.display = 'block';
}

async function loadFavorites() {
  try {
    const res = await fetch(`${API_BASE_URL}/favorites`);
    if (!res.ok) throw new Error('Failed to load favorites');
    const items = await res.json();
    renderFavorites(items);
  } catch (err) {
    console.error(err);
  }
}

function renderFavorites(items) {
  favoritesList.innerHTML = '';
  if (!items || !items.length) {
    const li = document.createElement('li');
    li.className = 'favorites__empty';
    li.textContent = 'No favorites yet';
    favoritesList.appendChild(li);
    return;
  }
  items.forEach(it => {
    const li = document.createElement('li');
    li.className = 'favorites__item';
    const name = it.place || it.location_id;
    li.innerHTML = `
      <span class="favorites__name">${name}</span>
      <div class="favorites__actions">
        <button class="btn btn--small btn--secondary" data-action="view" data-lat="${it.latitude}" data-lon="${it.longitude}">View</button>
        <button class="btn btn--small btn--danger" data-action="delete" data-id="${it.id}">Delete</button>
      </div>
    `;
    favoritesList.appendChild(li);
  });

  favoritesList.querySelectorAll('button').forEach(btn => {
    const action = btn.getAttribute('data-action');
    if (action === 'view') {
      btn.addEventListener('click', () => {
        const lat = parseFloat(btn.getAttribute('data-lat'));
        const lon = parseFloat(btn.getAttribute('data-lon'));
        loadWeather(null, lat, lon);
      });
    } else if (action === 'delete') {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        await deleteFavorite(id);
        await loadFavorites();
      });
    }
  });
}

async function deleteFavorite(id) {
  try {
    const res = await fetch(`${API_BASE_URL}/favorites/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete favorite');
  } catch (err) {
    console.error(err);
    showError('Could not delete favorite');
  }
}

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