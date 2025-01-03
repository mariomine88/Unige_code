const COMMENT_MAX_LENGTH = 200;

$(document).ready(function() {
    $('#followButton').on('click', handleFollowAction);
    loadUserPosts();
    $('#loadMorePosts').on('click', loadUserPosts);
});

function handleFollowAction() {
    const $button = $('#followButton');
    const action = $button.text().trim() === 'Follow' ? 'follow' : 'unfollow';
    
    $.ajax({
        url: '../BackEnd/follow_handler.php',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            userId: window.userData.userId,
            action: action
        }),
        success: function(response) {
            if (response.success) {
                if (action === 'follow') {
                    $button.text('Unfollow');
                    $button.removeClass('btn-primary').addClass('btn-secondary');
                } else {
                    $button.text('Follow');
                    $button.removeClass('btn-secondary').addClass('btn-primary');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

let page = 0;
let loading = false;
const postsPerPage = 10;

function loadUserPosts() {
    if (loading) return;
    loading = true;

    const $spinner = $('#loading-spinner');
    $spinner.removeClass('d-none');

    $.ajax({
        url: `../BackEnd/get_posts.php`,  // Updated endpoint
        method: 'GET',
        data: {
            user_id: window.userData.userId,
            page: page,
            limit: postsPerPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                if (page === 0) {
                    $('#posts-container').html('<p class="text-muted">No posts found.</p>');
                }
                $('#loadMorePosts').hide();
                return;
            }

            const $container = $('#posts-container');
            result.data.forEach(post => {
                $container.append(createPostHTML(post));
            });

            page++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading posts:', error);
            $('#posts-container').append(`
                <div class="alert alert-danger">
                    Failed to load posts. Please try refreshing the page.
                </div>
            `);
        },
        complete: function() {
            loading = false;
            $spinner.addClass('d-none');
        }
    });
}

function createPostHTML(post) {
    return `
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">
                    <a href="post.php?id=${post.id}" class="text-decoration-none text-dark">
                        ${escapeHtml(post.title)}
                    </a>
                </h5>
                <p class="card-text">${escapeHtml(post.content.substring(0, 200))}...</p>
                <div class="d-flex justify-content-between align-items-center">
                    <p class="text-muted mb-0">Posted on ${new Date(post.created_at).toLocaleString()}</p>
                    <span class="text-muted">
                        <i class="bi bi-hand-thumbs-up"></i> 
                        ${post.like_count || 0} likes
                    </span>
                </div>
                
                <div class="comments-section mt-3">
                    ${post.comments ? post.comments.map(comment => `
                        <div class="comment border-bottom py-2">
                            <div class="d-flex justify-content-between">
                                <strong class="text-primary">
                                    <a href="public_profile.php?UID=${escapeHtml(comment.username)}">
                                        ${escapeHtml(comment.username)}
                                    </a>
                                </strong>
                                <small class="text-muted">
                                    ${new Date(comment.created_at).toLocaleString()}
                                </small>
                            </div>
                            <p class="mb-1">
                                ${comment.content.length > COMMENT_MAX_LENGTH 
                                    ? escapeHtml(comment.content.substring(0, COMMENT_MAX_LENGTH)) + '...'
                                    : escapeHtml(comment.content)}
                            </p>
                        </div>
                    `).join('') : ''}
                </div>
            </div>
        </div>
    `;
}

function escapeHtml(unsafe) {
    return $('<div>').text(unsafe).html();
}
