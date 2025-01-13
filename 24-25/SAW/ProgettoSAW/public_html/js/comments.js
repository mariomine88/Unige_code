import { escapeHtml } from './utils.js';
import { handleLike } from './likes.js';
import { showAlert } from './utils.js';

let page = 0;  // Changed to start from 0
let loading = false;
const commentsPerPage = 10;

function createCommentHTML(comment) {
    const isLiked = parseInt(comment.is_liked) === 1;  // Fix: properly parse is_liked value
    const commentId = escapeHtml(comment.id);
    const timeAgo = moment(comment.created_at).fromNow(); // Use moment.js to format the time difference
    return `
        <div class="comment card mt-2" data-comment-id="${commentId}">
            <div class="card-body">
                <div>
                    <a href="public_profile.php?UID=${escapeHtml(comment.username)}" class="text-primary">
                        ${escapeHtml(comment.username)}
                    </a>
                    <small class="text-muted"> · ${timeAgo}</small>                
                </div>
                <div class="d-flex justify-content-between align-items-start mt-2" style="gap: 10px;">
                    <div style="min-width: 0; flex: 1;">
                        <p class="mb-2" style="word-wrap: break-word; overflow-wrap: break-word;">${escapeHtml(comment.content)}</p>
                    </div>
                    <div class="flex-shrink-0">
                        <button type="button" 
                                class="btn ${isLiked ? 'btn-primary' : 'btn-outline-primary'} btn-sm comment-like-btn"
                                data-liked="${isLiked}"
                                data-type="comment">
                            <i class="bi bi-hand-thumbs-up"></i>
                            <span class="like-count">${parseInt(comment.like_count) || 0}</span>
                        </button>
                    </div>
                </div>
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

    $.ajax({
        url: '../BackEnd/get_comments.php',
        method: 'GET',
        data: {
            post_id: postId,
            page: page,
            order: order
        },
        success: function(result) {
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
        },
        error: function(xhr, status, error) {
            console.error('Error loading comments:', error);
            const commentsContainer = document.getElementById('comments-container');
            commentsContainer.insertAdjacentHTML('beforeend', `
                <div class="alert alert-danger">
                    Failed to load comments. Please try refreshing the page.
                </div>`);
        },
        complete: function() {
            loading = false;
            if ($spinner.length) {
                $spinner.addClass('d-none');
            }
        }
    });
}

export function initComments(postId) {
    const commentOrder = document.getElementById('commentOrder');
    const commentsContainer = document.getElementById('comments-container');
    
    // Handle like button clicks
    commentsContainer.addEventListener('click', (e) => {
        const likeBtn = e.target.closest('.comment-like-btn');
        if (likeBtn) {
            const commentDiv = likeBtn.closest('.comment');
            if (commentDiv) {
                const commentId = commentDiv.dataset.commentId;

                likeBtn.setAttribute('data-liked', likeBtn.getAttribute('data-liked') === 'true');
                handleLike(commentId, 'comment', likeBtn);
            }
        }
    });

    // Load more comments when scrolling
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

    commentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        formData.append('post_id', postData.postId);

        $.ajax({
            url: '../BackEnd/add_comment.php',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false, 
            success: function(data) {
                if (data.success) {
                    showAlert('success', 'Comment added successfully!');
                    commentForm.reset();
                    
                    // Reset comments container and page counter
                    document.getElementById('comments-container').innerHTML = '';
                    page = 0;
                    
                    // Get current sort order
                    const currentOrder = document.getElementById('commentOrder').value;
                    
                    // Reload comments with current sort order
                    loadComments(postData.postId, currentOrder, true);
                } else {
                    showAlert('danger', data.message || 'Error adding comment');
                }
            },
            error: function(xhr, status, error) {
                showAlert('danger', 'An error occurred while adding the comment');
            }
        });
    });
});