// Глобальная переменная для отслеживания текущей страницы
let currentPage = 1;
const postsPerPage = 10;

// Function to edit a post
function toggleEditForm(postId) {
    const contentElement = document.getElementById(`post-content-${postId}`);
    const editFormElement = document.getElementById(`edit-form-${postId}`);
    
    if (contentElement.style.display === 'none') {
        contentElement.style.display = 'block';
        editFormElement.style.display = 'none';
    } else {
        contentElement.style.display = 'none';
        editFormElement.style.display = 'block';
    }
}

function editPost(postId, content) {
    fetch(`/post/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Ошибка при редактировании поста');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при редактировании поста');
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
                window.location.reload();
            } else {
                alert('Ошибка при удалении поста');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении поста');
        });
    }
}

function loadMorePosts() {
    currentPage++;
    const skip = (currentPage - 1) * postsPerPage;
    
    fetch(`/load_more?skip=${skip}&limit=${postsPerPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.posts && data.posts.length > 0) {
                const postsContainer = document.querySelector('.posts-container');
                
                data.posts.forEach(post => {
                    const postElement = createPostElement(post);
                    postsContainer.appendChild(postElement);
                });
                
                // Скрыть кнопку "Загрузить еще", если постов больше нет
                if (data.posts.length < postsPerPage) {
                    document.getElementById('load-more-btn').style.display = 'none';
                }
            } else {
                document.getElementById('load-more-btn').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при загрузке постов');
        });
}

function createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'post';
    postDiv.id = `post-${post.id}`;
    
    const createdAt = new Date(post.created_at).toLocaleString();
    
    postDiv.innerHTML = `
        <div class="post-header">
            <div>
                <strong>${post.username || 'Аноним'}</strong>
                <small>${createdAt}</small>
            </div>
            <div class="post-actions">
                <button type="button" class="btn-warning" onclick="toggleEditForm('${post.id}')">Редактировать</button>
                <button type="button" class="btn-danger" onclick="deletePost('${post.id}')">Удалить</button>
            </div>
        </div>
        <div class="post-content" id="post-content-${post.id}">
            ${post.content}
        </div>
        <div class="edit-form" id="edit-form-${post.id}" style="display: none;">
            <textarea id="edit-content-${post.id}">${post.content}</textarea>
            <button type="button" class="btn-primary" onclick="editPost('${post.id}', document.getElementById('edit-content-${post.id}').value)">Сохранить</button>
            <button type="button" class="btn-danger" onclick="toggleEditForm('${post.id}')">Отмена</button>
        </div>
    `;
    
    return postDiv;
} 