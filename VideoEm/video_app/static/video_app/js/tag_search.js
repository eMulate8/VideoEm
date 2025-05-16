
const csrf = document.getElementById("csrf").dataset.csrf;
const action = 'watch';
const searchButton = document.getElementById("btn_search");
const checkboxField = document.getElementById("tags_set");
const searchContainer = document.getElementById("tag_search");

const getTagUrl = "/api/v1/get_tag"

if (!searchButton || !checkboxField || !searchContainer) {
    console.error("Required DOM elements are missing");
}

window.addEventListener('DOMContentLoaded', async () => {
    try {
		const get_tags = await fetch(getTagUrl);
		if (!get_tags.ok) {
			throw new Error(`HTTP error! Status: ${get_tags.status}`);
		}
		const tags = await get_tags.json();

		tags.forEach((tag) => {
			const div = document.createElement('div');
			div.classList.add('checkbox_container');
			const input = document.createElement('input');
			input.type = "checkbox";
			input.id = `${tag.tag}`;
			input.name = "tag"
			const label = document.createElement('label');
			label.setAttribute('for', `${tag.tag}`);
			label.innerHTML = `  ${tag.tag}`;
			div.appendChild(input);
			div.appendChild(label);
			checkboxField.appendChild(div);
		});
	} catch (error) {
		console.error("Failed to fetch tags:", error);
	}
});

searchButton.addEventListener('click', async () => {
    searchContainer.style.display = 'none';

    const checkedBoxes = document.querySelectorAll('input[name=tag]:checked');
    const checkedTags = Array.from(checkedBoxes).map((item) => item.id);
    const tagsToSend = checkedTags.join(',');

    try {
        let next = `/api/v1/search?tags=${tagsToSend}`;
        next = await loadMoreVideos(next, action);
        window.setNextUrl(next);
    } catch (error) {
        console.error("Failed to load videos:", error);
    }
});