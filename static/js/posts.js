// Function to edit a post
function editPost(postId, content) {
    fetch(`/post/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `content=${encodeURIComponent(content)}`
    })
    .then(response => {
        if (response.ok) {
            // Reload the page to show updated content
            window.location.reload();
        } else {
            return response.text().then(text => {
                throw new Error(text);
            });
        }
    })
    .catch(error => {
        alert(`Ошибка при редактировании поста: ${error.message}`);
    });
}

// Function to delete a post
function deletePost(postId) {
    if (confirm('Вы уверены, что хотите удалить этот пост?')) {
        fetch(`/post/${postId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                // Remove the post element from the DOM
                const postElement = document.getElementById(`post-${postId}`);
                if (postElement) {
                    postElement.remove();
                }
            } else {
                return response.text().then(text => {
                    throw new Error(text);
                });
            }
        })
        .catch(error => {
            alert(`Ошибка при удалении поста: ${error.message}`);
        });
    }
} 