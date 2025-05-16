const tgWindow = window.Telegram?.WebApp;
const userData = tgWindow.initDataUnsafe?.user;

const timeLimit = 60000;

const telegram_id = userData.id;


const button_subscribe = document.getElementById('btn_subscribe');
const button_like = document.getElementById('btn_like');
const video_id = document.getElementById('video_id').dataset.video_id;
const csrf = document.getElementById('csrf').dataset.csrf;
const author_id = document.getElementById('author_id').dataset.author_id;
const tg_window = window.Telegram.WebApp;


const url_update_video = `/api/v1/update_video/${video_id}`;
const url_subscription = '/api/v1/subscriptions';

if (!button_subscribe || !button_like || !video_id || !csrf || !author_id) {

    console.error("Required DOM elements are missing");

}

/**
 * Updates a record in the Videos database
 * @param {string} url - API URL
 * @param {string} field - Field in the database to update
 * @param {string} csrf - Django CSRF token
 * @param {number} [telegram_id=null] - Optional: User Telegram ID to add the video to their viewing history
 * @param {string} [video_id=null] - Optional: ID of the video that was viewed
 */
const updateVideo = async (url, field, csrf, telegram_id, video_id = null) => {

    if (!url || !field || !csrf) {
		throw new Error("Missing required parameters: url, field, or csrf");
	}

	const url_add_history = '/api/v1/history_add';

    try {
        const response_get_views = await fetch(url);
        if (!response_get_views.ok) {
            throw new Error(`Failed to fetch view data: ${response_get_views.statusText}`);
        }
        const currentData = await response_get_views.json();
        const updatedValue = currentData[field] + 1;

        const response_update = await fetch(url, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrf,
			},
			body: JSON.stringify({ [field]: updatedValue }),
		});

		if (!response_update.ok) {
			throw new Error(`Failed to update video: ${response_update.statusText}`);
		}

        if (video_id) {
            const response_add_history = await fetch(url_add_history, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrf,
				},
				body: JSON.stringify({
					user: telegram_id,
					video: video_id,
				}),
			});

			if (!response_add_history.ok) {
				throw new Error(`Failed to add viewing history: ${response_add_history.statusText}`);
			}
        }
    } catch (error) {
        console.error('Error occurred:', error);
    }
};

/**
 * Increase views by one
*/
const increaseViews = async () => {
    await updateVideo(url_update_video, 'view_count', csrf, telegram_id, video_id);
};

/**
 * Increase stars by one
*/
const AddStar = async () => {
    await updateVideo(url_update_video, 'stars', csrf);
};

/**
 * Send subscription datas on server
 * @param {string} mtd - HTTP method: 'POST' to add a subscription, 'DELETE' to remove a subscription
 * @throws {Error} - If the request fails or required parameters are missing
 */
const subscription_request = async (mtd) => {

    try {
		if (!mtd || !telegram_id || !author_id || !csrf) {
				throw new Error("Missing required parameters: mtd, telegram_id, author_id, or csrf");
			}

		if (mtd !== "POST" && mtd !== "DELETE") {
				throw new Error("Invalid method: mtd must be 'POST' or 'DELETE'");
			}

		const response = await fetch(url_subscription, {
				method: mtd,
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrf,
				},
				body: JSON.stringify({
					from_user: telegram_id,
					to_user: author_id,
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
	} catch (error) {
        console.error("Failed to process subscription request:", error);
    }
}

button_subscribe.addEventListener('click', async () => {
    try {
		if (button_subscribe.textContent == 'Subscribe') {
			await subscription_request('POST');
			button_subscribe.textContent = 'Unsubscribe';
		} else {
		   await subscription_request('DELETE');
		   button_subscribe.textContent = 'Subscribe';
		}
	} catch (error) {
        console.error("Failed to process subscription request:", error);
    }
});

button_like.addEventListener('click', async () => {

    try {	
		const url_invoice = `/api/v1/invoice_link?user=${telegram_id}&video=${video_id}`;

		const get_invoice_link = await fetch(url_invoice);

		if (!get_invoice_link.ok) {
			throw new Error(`HTTP error! Status: ${get_invoice_link.status}`);
		}

		const invoice_link_data = await get_invoice_link.json();
		const invoice_link = invoice_link_data.invoice_link;

		tg_window.openInvoice(invoice_link);

	} catch (error) {
		console.error("Failed to fetch invoice link:", error);
	}

});


window.addEventListener('DOMContentLoaded', async () => {
    if (author_id == telegram_id) {
        button_subscribe.disabled = true;
    }
    try {
		const get_subscriptions = await fetch(`${url_subscription}?telegram_id=${telegram_id}`);

		if (!get_subscriptions.ok) {
            throw new Error(`HTTP error! Status: ${get_subscriptions.status}`);
        }

		const subscriptions_data = await get_subscriptions.json();
		const to_users = subscriptions_data.subscriptions.map(subscription => subscription.to_user);

		if (to_users.includes(+author_id)) {
			button_subscribe.textContent = 'Unsubscribe';
		}
	} catch (error) {
		console.error("Error fetching subscriptions:", error);
	}

	setTimeout(increaseViews, timeLimit);
});
