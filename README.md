# Telegram Video Hosting WebApp  

[![Django](https://img.shields.io/badge/Django-5.1+-green.svg)](https://www.djangoproject.com/)  
[![Telegram Bot API]](https://core.telegram.org/bots/api)  

A Django web app that hosts videos using **Telegram servers for storage**. Users upload videos via a Telegram bot, edit metadata in the web app, and publish them.  

⚠️ **Note**: Due to Telegram’s limitations:  
- Max video size: **20 MB** (user warning implemented).  
- Video links expire hourly (automatically refreshed via `update_temp_links.py`).  
- Short videos are converted to GIFs (min **5-second duration** enforced).  

---

## ✨ Features  
- **Video Management**:  
  - Upload via Telegram bot (after user registers in the web app).  
  - Edit titles, descriptions, and tags (title editable **once**).  
- **User System**:  
  - Registration via Telegram WebApp.  
  - Subscriptions, stars (Telegram currency), and view tracking.  
- **Database**: PostgreSQL.  
- **Cache Busting**: Bypasses Telegram’s aggressive WebApp caching.  

### 📌 Tabs  
1. **Home**: All published videos (newest first).  
2. **Subscriptions** (❤️): Videos from subscribed users.  
3. **Search**: By title or tags.  
4. **Account**:  
   - User’s videos (published/unpublished).  
   - Profile data (name, registration date, stars, etc.).  
   - Viewing history.  

### 🎥 Video Interaction  
- **Preview**: Click plays first 5 seconds; click again opens:  
  - *Edit page* (from Account) or *Watch page* (elsewhere).  
- **Watch Page**:  
  - Subscribe to author, give stars, view metadata.  
  - Views increment after **1 minute** of staying on video page.  

---

## 🛠️ Installation  

### Prerequisites  
- Python 3.10+  
- Django 5.1+  
- Django Rest Framework 3.15+
- Requests 2.32+
- Shedule 1.2+
- Psycopg 2.9+

### Steps  
1. **Set up Django project**:  
   ```bash
   django-admin startproject <site_name> <directory_name>  # Project and directory named "VideoEm"
   cd VideoEm
   python manage.py startapp <app_name>       # App named "video_app"
   ```  
You can choose any other <site_name>, <directory_name> and <app_name> 
but keep originally names in mind when copying files.

2. **Copy files** to match this structure:  
   ```plaintext
   VideoEm/                   # Main project directory
   ├── templates/             # Base site templates
   ├── video_app/             # App directory
   │   ├── static/            # Static files (CSS/JS)
   │   └── templates/         # App-specific templates
   ├── VideoEm/               # Project settings (settings.py, etc.)
   ├── bot_main.py            # Telegram bot script
   └── update_temp_links.py   # Hourly video link updater
   ```  

3. **Configure `settings.py`** (local development):  
   ```python
   DEBUG = True
   ALLOWED_HOSTS = ['127.0.0.1']
   INSTALLED_APPS = [ ... ,
                    'rest_framework',
                    ]
   MIDDLEWARE = [ ... ,
                '<app_name>.middleware.RequestLoggingMiddleware',
                ]
   TEMPLATES = [ ... , 
            'context_processors': [ ... ,
                '<app_name>.context_processors.static_version',
            ],
    ]
   ```  

4. **Run migrations**:  
   ```bash
   python manage.py migrate
   python manage.py makemigration
   ```  

5. **Launch scripts**:  
   - Start the bot:  
     ```bash
     python bot_main.py
     ```  
   - Schedule link updates (e.g., via cron):  
     ```bash
     python update_temp_links.py
     ```  

---

## 🔧 Technical Notes  
- **Telegram Limits**:  
  - Bot cannot access videos >20 MB.  
  - File links expire hourly (`update_temp_links.py` fixes this). 
  - Not showing first frame of video as preview (added thuimbnail)  

---

## 📄 License  
MIT.  

---

### Need Help?  
Open an issue or contact Tg: @emutera.  