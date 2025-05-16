
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const tgWindow = window.Telegram?.WebApp;
const userData = tgWindow.initDataUnsafe?.user;

if (!tabs.length || !tabContents.length) {
    console.error("Required DOM elements for tabs are missing");
}

let videoTable;
let action;

const telegram_id = userData.id;
const photo_url = userData.photo_url;
const user_name = userData.username;

const url_user_get = `/api/v1/user_get/${telegram_id}`;

let next_my_videos = `/api/v1/video_get?user=${telegram_id}`;
let next_history = `/api/v1/watched_videos?user=${telegram_id}`;

tabs.forEach(tab => {

  tab.addEventListener('click', async () => {

    tabs.forEach(t => t.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));

    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');

    if (tab.dataset.tab === 'tab1') {
      action = 'edit';
      videoTable = document.getElementById('videoTable');
      next_my_videos = await loadMoreVideos(next_my_videos, action);
    }

    if (tab.dataset.tab === 'tab2') {
      action = 'watch';
      videoTable = document.getElementById('history');
      next_history = await loadMoreVideos(next_history, action);
    }

  });

});

window.addEventListener('DOMContentLoaded', async () => {
  const activeTab = document.querySelector('.tab.active');

  try {
    const response = await fetch(url_user_get);
    if (!response.ok) {
    	throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    time_create_format = formatDBTime(data.time_create);

    document.getElementById('tg_picture').src = photo_url;
    document.getElementById('full_name').innerText = data.telegram_fullname;
    document.getElementById('time_create').innerText = `Register date: ${time_create_format}`;
    document.getElementById('stars_count').innerText = `Stars: ${data.stars_count}`;
    document.getElementById('video_count').innerText = `Videos: ${data.video_count}`;
    document.getElementById('username').innerText = `Username: @${user_name}`;
  } catch (error) {
        console.error('Error fetching content:', error);
  }

  if (activeTab && activeTab.dataset.tab === 'tab1') {
    action = 'edit';
    videoTable = document.getElementById('videoTable');
    next_my_videos = await loadMoreVideos(next_my_videos, action);
    window.setNextUrl(next_my_videos);
  }

  if (activeTab && activeTab.dataset.tab === 'tab2') {
    action = 'watch';
    videoTable = document.getElementById('history');
    next_history = await loadMoreVideos(next_history, action);
    window.setNextUrl(next_history);
  }

});