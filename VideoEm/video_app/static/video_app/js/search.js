
const searchButton = document.getElementById('btn_search');
const toTagButton = document.getElementById('btn_to_tag_search');
const searchField = document.getElementById('search_field');
const action = 'watch';

if (!searchButton || !toTagButton || !searchField) {
    console.error("Required DOM elements are missing");
}

searchButton.addEventListener('click', async () => {
    try {
        let query = searchField.value.replace(/[^a-zA-Z0-9]/g, "").trim();

        if (query !== "") {
            let next = `/api/v1/search?q=${query}`;
            next = await loadMoreVideos(next, action);
            window.setNextUrl(next);
        }
    } catch (error) {
        console.error("Failed to load videos:", error);
    }
});

toTagButton.addEventListener('click', () => {
    window.location.href = "/tag_search/";
});