let page = 0;
let loading = false;
const postsPerPage = 10;

function loadPosts() {
    if (loading || !window.hasFollows) return;
    loading = true;

    const $spinner = $('#loading-spinner');
    const $container = $('#posts-container');
    
    if ($spinner.length) {
        $spinner.removeClass('d-none');
    }

    $.ajax({
        url: '../BackEnd/get_posts.php',
        method: 'GET',
        data: {
            page: page,
            limit: postsPerPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                if (page === 0) {
                    $container.html('<p class="text-muted">No posts from followed users.</p>');
                }
                $spinner.remove();
                return;
            }

            result.data.forEach(post => {
                $container.append(createPostHTML(post));
            });
            page++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading posts:', error);
            $container.append(`
                <div class="alert alert-danger">
                    Failed to load posts. Please try refreshing the page.
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

function createPostHTML(post) {
    if (!post) return '';
    return `
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">
                    <a href="post.php?id=${escapeHtml(post.id)}" class="text-decoration-none text-dark">
                        ${escapeHtml(post.title)}
                    </a>
                </h5>
                <h6 class="card-subtitle mb-2 text-muted">
                    By <a href="public_profile.php?UID=${escapeHtml(post.username)}">
                        ${escapeHtml(post.username)}
                    </a>
                </h6>
                <p class="card-text">${escapeHtml(post.content ? post.content.substring(0, 200) : '')}...</p>
                <p class="text-muted">${new Date(post.created_at).toLocaleString()}</p>
                ${renderComments(post.comments)}
            </div>
        </div>`;
}

function renderComments(comments) {
    if (!comments || !Array.isArray(comments)) return '';
    
    return `
        <div class="comments-section mt-3">
            ${comments.map(comment => {
                if (!comment) return '';
                return `
                    <div class="comment border-bottom py-2">
                        <div class="d-flex justify-content-between">
                            <strong>
                                <a href="public_profile.php?UID=${escapeHtml(comment.username)}">
                                    ${escapeHtml(comment.username)}
                                </a>
                            </strong>
                            <small class="text-muted">
                                ${new Date(comment.created_at).toLocaleString()}
                            </small>
                        </div>
                        <p class="mb-1">${escapeHtml(comment.content)}</p>
                    </div>
                `;
            }).join('')}
        </div>`;
}

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    // Convert to string in case we get a number or other type
    const str = String(unsafe);
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Event handlers
$(document).ready(function() {
    if (window.hasFollows) {
        loadPosts();
        
        $(window).scroll(function() {
            if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
                loadPosts();
            }
        });
    }
});
