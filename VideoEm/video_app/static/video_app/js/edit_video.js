const openDialog = document.getElementById("openDialog");
const cancelButton = document.getElementById("cancel");
const addTagButton = document.getElementById("addTag");
const dialog = document.getElementById("tagAddDialog");
const csrf = document.getElementById("csrf").dataset.csrf;
const addTagUrl = "/api/v1/create_tag";

if (!openDialog || !cancelButton || !addTagButton || !dialog || !csrf) {
    console.error("Required DOM elements are missing");
}

openDialog.addEventListener("click", () => {
    dialog.showModal();
});

cancelButton.addEventListener("click", () => {
    dialog.close();
});

addTagButton.addEventListener("click", async () => {
    try {
		let newTag = document.getElementById("newTag").value;
		newTag = newTag.toLowerCase().replaceAll(/[^a-z]+/g, "");

		if (!newTag) {
			return;
			}
		const response = await fetch(addTagUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrf,
				},
				body: JSON.stringify({
					"tag": newTag
				}),
			});

		if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
		location.reload();
	} catch (error) {
        console.error("Failed to add tag:", error);
    }
});


