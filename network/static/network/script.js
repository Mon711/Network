// edit button functionality
document.querySelectorAll(".edit-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
        // Get the post ID from the button ID
        const postId = event.target.id.split("-")[2];

        // Get the post content element
        const postContent = document.getElementById(`post-${postId}`);

        // Save the original content in  attribute "data-original-content"
        const originalContent = postContent.textContent;
        postContent.setAttribute("data-original-content", originalContent)

        // Show the "Cancel" and "Save" button
        // Hide the "Like" and "Edit" button
        toggleButtons(postId, ["like-btn", "edit-btn", "like-count"], ["cancel-btn", "save-btn"]);
        
        // Replace the post content with a textarea containing the original content
        postContent.innerHTML = `<textarea id="edit-textarea-${postId}" class="form-control" style="height: 100px" autofocus>${originalContent}</textarea>`
    });
});

document.querySelectorAll(".cancel-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
        // Get the post ID from the button ID
        const postId = event.target.id.split("-")[2];

        // Get the post content element
        const postContent = document.getElementById(`post-${postId}`);

        // Get the original content
        const originalContent = postContent.dataset.originalContent;

        // Hide the "Cancel" and "Save" button
        // Show the "Like" and "Edit" button
        toggleButtons(postId, ["cancel-btn", "save-btn"], ["like-btn", "edit-btn", "like-count"]);

        // Restore the original postContent
        postContent.textContent = originalContent;
    });
});


document.querySelectorAll(".save-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
        // Get the post id from the button ID
        const postId = event.target.id.split("-")[2];

        // Get the new post content from the textarea
        const newContent = document.getElementById(`edit-textarea-${postId}`).value;

        // Hide the "Cancel" and "Save" button
        // Show the "Like" and "Edit" button
        toggleButtons(postId, ["cancel-btn", "save-btn"], ["like-btn", "edit-btn", "like-count"]);

        // Get the csrf token
        const csrftoken = document.querySelector("meta[name='csrf-token']").getAttribute("content");

        // Send AJAX request to the server
        fetch("/update-post", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                post_id: postId,
                new_content: newContent
            })
        }).then(response => response.json())
          .then(data => {
            // Replace the textarea with the new post content
            document.getElementById(`post-${postId}`).textContent = newContent;
          });
    });
});

// A helper Function to handle hiding and showing of buttons
function toggleButtons(postId, hideButtons, showButtons){
    hideButtons.forEach((buttonId) => {
        document.getElementById(`${buttonId}-${postId}`).classList.add("d-none");
    });

    showButtons.forEach((buttonId) => {
        document.getElementById(`${buttonId}-${postId}`).classList.remove("d-none");
    });
}

// Like button functionality
document.querySelectorAll(".like-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
        // Get the post id from the button id
        const postId = event.target.id.split("-")[2];

        // Get the csrf token
        const csrftoken = document.querySelector("meta[name='csrf-token']").getAttribute("content");

        // Get Like button for changing its style after "Like" or "Unlike"
        const likeBtn = document.getElementById(`like-btn-${postId}`);

        // Send a POST request to the server
        fetch("/like-post", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                "post_id": postId
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Update the like count
            document.getElementById(`like-count-${postId}`).textContent = data.likes_count;

            // Update the "Like"/"Unlike" button style
            likeBtn.classList.add(data.text[0]);
            likeBtn.classList.remove(data.text[1]);
            likeBtn.textContent = data.text[2];
        });
    });
});