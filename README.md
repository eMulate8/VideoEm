# Telegram Video Hosting WebApp  

[![Django](https://img.shields.io/badge/Django-5.1+-green.svg)](https://www.djangoproject.com/)  

A Django web app that hosts videos using **Telegram servers for storage**. Users upload videos via a Telegram bot, edit metadata in the web app, and publish them.  

⚠️ **Note**: Due to Telegram’s limitations:  
- Max video size: **20 MB** (user warning implemented).  
- Video links expire hourly (automatically refreshed using Celery tasks).  
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


### Steps  
1. **Create docker image**:  
   ```bash
   docker image build . -t videoapp
   ``` 

2. **Edit docker-compose.yml**:  
	- Add BOT_TOKEN, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD values

3. **Edit `settings.py`**:  
   - Add SECRET_KEY, BD_NAME, USER_NAME, PWD values
   
4. **Edit `bot_main.py`**
   - Add WEB_APP_URL value
   
5. **Run docker-compose**
	```bash
   docker-compose up
   ``` 


## 🔧 Technical Notes  
- **Telegram Limits**:  
  - Bot cannot access videos >20 MB.  
  - File links expire hourly (`update_temp_links.py` fixes this). 
  - Not showing first frame of video as preview (added thuimbnail)  

---

## 📄 License  
Apache License 2.0

---

### Need Help?  
Open an issue or contact Tg: @emutera.  
