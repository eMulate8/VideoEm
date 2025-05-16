
const videoTable = document.getElementById('videoTable');
const action = 'watch'
const tgWindow = window.Telegram?.WebApp;
const userData = tgWindow.initDataUnsafe?.user;
const telegram_id = userData.id;


if (!videoTable) {
    console.error("Required DOM element 'videoTable' is missing");
}


const get_subscriptions_url = `/api/v1/subscriptions?telegram_id=${telegram_id}`

window.addEventListener('DOMContentLoaded', async () => {

	try {
		const get_subscriptions = await fetch(get_subscriptions_url);

        	if (!get_subscriptions.ok) {
            		throw new Error(`HTTP error! Status: ${get_subscriptions.status}`);
        	}

        	const subscriptions_data = await get_subscriptions.json();

		const to_users = subscriptions_data.subscriptions.map(subscription => subscription.to_user);
		let users = to_users.join(",");

        	if (users !== ""){
            		let next_subs_videos = `/api/v1/video_get?users=${users}`;
		    	next_subs_videos = await loadMoreVideos(next_subs_videos, action);
		    	window.setNextUrl(next_subs_videos);
        	}

	} catch (error) {
        	console.error("Failed to fetch subscriptions or videos:", error);
    	}
});
