// Escape HTML function
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Comment order handling
const commentOrder = document.getElementById('commentOrder');
commentOrder.addEventListener('change', function() {
    const order = this.value;
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('order', order);
    window.location.href = currentUrl.toString();
});

// Set initial order value from URL
const urlParams = new URLSearchParams(window.location.search);
const orderParam = urlParams.get('order');
if (orderParam) {
    commentOrder.value = orderParam;
}

// Replace load more button with infinite scroll
let page = 1;
let loading = false;
let hasMoreComments = true;

// Initial load of comments
async function loadComments() {
    if (loading || !hasMoreComments) return;
    loading = true;
    
    const order = commentOrder.value;
    const postId = new URLSearchParams(window.location.search).get('id');
    
    try {
        const response = await fetch(`../BackEnd/get_comments.php?post_id=${postId}&page=${page}&order=${order}`);
        const result = await response.json();
        
        if (!result.data || result.data.length === 0) {
            hasMoreComments = false;
            return;
        }

        const commentsContainer = document.getElementById('comments-container');
        result.data.forEach(comment => {
            commentsContainer.insertAdjacentHTML('beforeend', createCommentHTML(comment));
        });
        
        page++;
    } catch (error) {
        console.error('Error loading comments:', error);
    } finally {
        loading = false;
    }
}

// Infinite scroll handler
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && hasMoreComments) {
            loadComments();
        }
    });
}, { threshold: 0.5 });

// Create and observe sentinel element
const sentinel = document.createElement('div');
sentinel.id = 'sentinel';
sentinel.style.height = '20px';
document.getElementById('comments-container').after(sentinel);
observer.observe(sentinel);

// Initial load
loadComments();

// Update comments when order changes
commentOrder.addEventListener('change', function() {
    const order = this.value;
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('order', order);
    window.location.href = currentUrl.toString();
});

// Wrap the post like button code in DOMContentLoaded and add null check
document.addEventListener('DOMContentLoaded', function() {
    const postLikeButton = document.querySelector('.post-like-btn');
    if (postLikeButton) {
        postLikeButton.addEventListener('click', function() {
            const postId = new URLSearchParams(window.location.search).get('id');
            const isLiked = this.classList.contains('btn-primary');
            handlePostLike(postId, isLiked, this);
        });
    }
});

async function handlePostLike(postId, isLiked, button) {
    try {
        const response = await fetch('../BackEnd/like_handler.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                targetId: postId,
                action: isLiked ? 'unlike' : 'like',
                type: 'post'
            })
        });

        const result = await response.json();
        
        if (result.success) {
            button.classList.toggle('btn-primary');
            button.classList.toggle('btn-outline-primary');
            button.querySelector('.post-like-count').textContent = result.likeCount;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function createCommentHTML(comment) {
    const isLiked = comment.is_liked === "1";
    const commentId = escapeHtml(comment.id);
    return `
        <div class="comment card mt-2" data-comment-id="${commentId}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong class="text-primary">
                            <a href="public_profile.php?UID=${escapeHtml(comment.username)}">
                                ${escapeHtml(comment.firstname + ' ' + comment.lastname)}
                            </a>
                        </strong>
                        <small class="text-muted ms-2">
                            @${escapeHtml(comment.username)}
                        </small>
                    </div>
                    <small class="text-muted">
                        ${new Date(comment.created_at).toLocaleString()}
                    </small>
                </div>
                <p class="mt-2 mb-1">${escapeHtml(comment.content)}</p>
                <div class="d-flex align-items-center mt-2">
                    <button type="button" 
                            id="likeButton_${commentId}" 
                            class="btn ${isLiked ? 'btn-primary' : 'btn-outline-primary'} btn-sm comment-like-btn"
                            onclick="handleCommentLike('${commentId}', this)">
                        <i class="bi bi-hand-thumbs-up"></i>
                        <span id="likeCount_${commentId}" class="comment-like-count">
                            ${comment.like_count || 0}
                        </span>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Add this new function for handling comment likes
async function handleCommentLike(commentId, button) {
    const isLiked = button.classList.contains('btn-primary');
    
    try {
        const response = await fetch('../BackEnd/like_handler.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                targetId: commentId,
                type: 'comment',
                action: isLiked ? 'unlike' : 'like'
            })
        });

        const data = await response.json();
        
        if (data.success) {
            button.classList.toggle('btn-primary');
            button.classList.toggle('btn-outline-primary');
            
            const likeCount = document.getElementById(`likeCount_${commentId}`);
            if (likeCount) {
                likeCount.textContent = data.likeCount;
            }
        } else {
            console.error('Like operation failed:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Remove or comment out the previous comment-like event listener since we're now using onclick
// ...existing code...
