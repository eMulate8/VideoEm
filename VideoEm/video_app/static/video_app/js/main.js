
const videoTable = document.getElementById('videoTable');
const action = 'watch';

if (!videoTable) {
    console.error("Required DOM element 'videoTable' is missing");
}

document.addEventListener('DOMContentLoaded', async () => {

	try {

        let next = '/api/v1/video_get';
        next = await loadMoreVideos(next, action);
        window.setNextUrl(next);

    } catch (error) {

        console.error("Failed to load videos:", error);
    }

});
