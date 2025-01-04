import { escapeHtml } from './utils.js';
import { handleLike } from './likes.js';
import { showAlert } from './utils.js';

let page = 0;  // Changed to start from 0
let loading = false;
const commentsPerPage = 10;

function createCommentHTML(comment) {
    const isLiked = parseInt(comment.is_liked) === 1;  // Fix: properly parse is_liked value
    const commentId = escapeHtml(comment.id);
    return `
        <div class="comment card mt-2" data-comment-id="${commentId}">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <a href="public_profile.php?UID=${escapeHtml(comment.username)}" class="text-primary">
                            ${escapeHtml(comment.firstname + ' ' + comment.lastname)}
                        </a>
                        <small class="text-muted">@${escapeHtml(comment.username)}</small>
                    </div>
                    <small class="text-muted">${new Date(comment.created_at).toLocaleString()}</small>
                </div>
                <p class="mt-2">${escapeHtml(comment.content)}</p>
                <button type="button" 
                        class="btn ${isLiked ? 'btn-primary' : 'btn-outline-primary'} btn-sm comment-like-btn"
                        data-liked="${isLiked}"
                        data-type="comment">
                    <i class="bi bi-hand-thumbs-up"></i>
                    <span class="like-count">${parseInt(comment.like_count) || 0}</span>
                </button>
            </div>
        </div>
    `;
}

async function loadComments(postId, order = 'DESC', reset = false) {
    if (loading) return;
    loading = true;
    
    if (reset) {
        page = 0;  // Reset to 0 instead of 1
        document.getElementById('comments-container').innerHTML = '';
    }
    
    const $spinner = $('#comments-loading-spinner');
    if ($spinner.length) {
        $spinner.removeClass('d-none');
    }

    try {
        const response = await fetch(`../BackEnd/get_comments.php?post_id=${postId}&page=${page}&order=${order}`);
        const result = await response.json();
        
        const commentsContainer = document.getElementById('comments-container');
        
        if (!result.data || result.data.length === 0) {
            if (page === 0) {
                commentsContainer.innerHTML = '<p class="text-muted">No comments yet.</p>';
            }
            if ($spinner.length) {
                $spinner.remove();
            }
            return;
        }

        result.data.forEach(comment => {
            commentsContainer.insertAdjacentHTML('beforeend', createCommentHTML(comment));
        });
        
        page++;
    } catch (error) {
        console.error('Error loading comments:', error);
        const commentsContainer = document.getElementById('comments-container');
        commentsContainer.insertAdjacentHTML('beforeend', `
            <div class="alert alert-danger">
                Failed to load comments. Please try refreshing the page.
            </div>`);
    } finally {
        loading = false;
        if ($spinner.length) {
            $spinner.addClass('d-none');
        }
    }
}

export function initComments(postId) {
    const commentOrder = document.getElementById('commentOrder');
    const commentsContainer = document.getElementById('comments-container');
    
    // Add event delegation for comment likes
    commentsContainer.addEventListener('click', (e) => {
        const likeBtn = e.target.closest('.comment-like-btn');
        if (likeBtn) {
            const commentDiv = likeBtn.closest('.comment');
            if (commentDiv) {
                const commentId = commentDiv.dataset.commentId;
                // Force string to boolean conversion for data-liked attribute
                likeBtn.setAttribute('data-liked', likeBtn.getAttribute('data-liked') === 'true');
                handleLike(commentId, 'comment', likeBtn);
            }
        }
    });

    // Update scroll handling to match feed.js style
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
            loadComments(postId, commentOrder.value);
        }
    });

    // Initial load
    loadComments(postId, commentOrder.value);

    // Handle order changes
    commentOrder.addEventListener('change', () => {
        loadComments(postId, commentOrder.value, true);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('commentForm');
    const commentsContainer = document.getElementById('comments-container');
    const loadingSpinner = document.getElementById('comments-loading-spinner');

    commentForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        formData.append('post_id', postData.postId);

        try {
            const response = await fetch('../BackEnd/add_comment.php', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showAlert('success', 'Comment added successfully!');
                commentForm.reset();
                
                // Reset comments container and page counter
                document.getElementById('comments-container').innerHTML = '';
                page = 0;
                
                // Get current sort order
                const currentOrder = document.getElementById('commentOrder').value;
                
                // Reload comments with current sort order
                await loadComments(postData.postId, currentOrder, true);
            } else {
                showAlert('danger', data.message || 'Error adding comment');
            }
        } catch (error) {
            showAlert('danger', 'An error occurred while adding the comment');
        }
    });

    // ... rest of your existing comments.js code ...
});