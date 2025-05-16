
let isLoading = false;
let throttleTimeout;
const timeout = 400;
let hasMoreVideos = true;
let nextUrl = "";
const durationPreview = 5000;
const thumbnail = '/static/video_app/images/thumbnail.jpg';

window.setNextUrl = function (url) {
    nextUrl = url;
}

/**
 * Creating elements in table cells with the next structure:
 * <div> - videoWrapper
 * <a> - linkToVideo
 * <video></video> - preview
 * <div></div> - title
 * </a>
 * <div> - videoInfo
 * <span></span> - videoViews
 * <span></span> - videoStars
 * <span></span> - videoUsername
 * </div>
 * </div>
 * @param {object} video - object with info about single video, keys = Videos model fields
 * @param {'watch' | 'edit'} action - Flag for forming the link to the video.
 * @returns {HTMLElement} - The created video wrapper element.
 * @throws {Error} - If `video` is not an object or `action` is invalid.
 */
const createVideoElement = (video, action) => {
    if (typeof video !== 'object' || video === null) {
        throw new Error('Invalid video: must be an object');
    }

    const videoWrapper = document.createElement('div');
    videoWrapper.classList.add('video-preview');

    const link_to_video = document.createElement('a');

    if (action == 'watch') {
        link_to_video.href = `/view_video/${video.video_slug}/`;
    }
    else if (action == 'edit') {
        link_to_video.href = `/edit_video/${video.video_id}/`;
    }
    else {
        link_to_video.href = '';
    }

    link_to_video.target = '_self';

    const preview = document.createElement('video');
    preview.src = `/proxy-video/?video_url=${encodeURIComponent(video.temp_link)}`;
    preview.setAttribute('muted', '');
    preview.setAttribute('preload', 'metadata');
    preview.setAttribute('webkit-playsinline', '');
    preview.setAttribute('x-webkit-airplay', 'allow');
    preview.setAttribute('poster', thumbnail);

    link_to_video.appendChild(preview);
    videoWrapper.appendChild(link_to_video);

    const title = document.createElement('div');
    title.classList.add('video-title');
    title.innerText = video.title;
    link_to_video.appendChild(title);

    const videoInfo = document.createElement('div');
    videoInfo.classList.add('video-info');

    const videoViews = document.createElement('span');
    videoViews.classList.add('video-views');
    videoViews.innerText = `${video.view_count} views`;

    const videoStars = document.createElement('span');
    videoStars.classList.add('video-stars');
    videoStars.innerHTML = `${video.stars}
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />
    </svg>`;

    const videoUsername = document.createElement('span');
    videoUsername.classList.add('video-username');
    videoUsername.innerText = `${video.username}`;

    videoInfo.appendChild(videoUsername);

    videoInfo.appendChild(videoViews);
    videoInfo.appendChild(videoStars);

    videoWrapper.appendChild(videoInfo);

    let hasPlayed = false;

    videoWrapper.addEventListener('click', (event) => {

        if (!hasPlayed) {
            event.preventDefault();

            const allVideos = document.querySelectorAll('video');
            allVideos.forEach((vid) => {
                if (vid !== preview) {
                    vid.pause();
                    vid.dataset.isPlaying = 'false';
                }
            });

            preview.play().catch(error => {
                    console.error('Error playing video:', error);
                });

            preview.dataset.isPlaying = 'true';
            hasPlayed = true;

            setTimeout(() => {
                preview.pause();
                preview.dataset.isPlaying = 'false';
            }, 5000);

        } else {
            window.location.href = link_to_video.href;
        }
    });

    return videoWrapper;
};

/**
 * Makes a row in the table with one element and passes data from one video to each element
 * @param {array} videos - array of objects with info about single video
 * @param {str} action - flag for subsequent formation of a link
 * Allowed values:
 *                 - 'watch': The video link leads to the viewing page.
 *                 - 'edit': The video link leads to the editing page.
 * @throws {Error} - If `videos` is not an array or `action` is invalid.
 */
const renderVideos = (videos, action) => {

    if (!videoTable) {
    throw new Error('videoTable not found in the DOM');
    }

    if (!Array.isArray(videos)) {
        throw new Error('Invalid videos: must be an array');
    }

    const fragment = document.createDocumentFragment();

    videos.forEach((video, index) => {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        const videoWrapper = createVideoElement(video, action);

        if (!videoWrapper) {
            console.error('Failed to create video element for video:', video);
            return;
        }

        cell.appendChild(videoWrapper);
        row.appendChild(cell);
        fragment.appendChild(row);
    });

    videoTable.appendChild(fragment);
};

/**
 * Fetches video data from the API and renders it.
 * @param {string} next - URL for the initial request and subsequent paginated requests (CursorPagination).
 * @param {string} action - Flag for forming the link to the video.
 * Allowed values:
 *                 - 'watch': The video link leads to the viewing page.
 *                 - 'edit': The video link leads to the editing page.
 * @returns {string|null} - The `next` URL for pagination, or `null` if no more videos are available.
 * @throws {Error} - If the `next` URL or `action` value is invalid or the API response is malformed.
 */
const loadMoreVideos = async (next, action) => {

    if (!next || !hasMoreVideos) {
        return null;
    };

    try {
        const response = await fetch(next);

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();

        if (data.results.length > 0) {
            renderVideos(data.results, action);
            return data.next
        } else {
            hasMoreVideos = false;
            return null;
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        throw error;
    }
};


/**
 * Convert time from db format to more readable
 * formatDBTime(2000-10-10T10:10:10.958550Z); // Example output: "10 Oct 2000, 10:10"
 * @param {string} dbTime - time from database
 * @returns {string} Formatted date-time string
 */
const formatDBTime = (dbTime) => {

    const date = new Date(dbTime);

    const options = {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };

    return new Intl.DateTimeFormat('en-GB', options).format(date);
}


window.addEventListener('scroll', async () => {
    if (!throttleTimeout) {
        throttleTimeout = setTimeout(async () => {
            throttleTimeout = null;
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight && !isLoading && hasMoreVideos) {
                isLoading = true;
                nextUrl = await loadMoreVideos(nextUrl, action);
                isLoading = false;
            }
        }, timeout);
    }
});
