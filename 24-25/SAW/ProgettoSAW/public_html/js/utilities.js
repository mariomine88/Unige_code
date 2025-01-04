const COMMENT_MAX_LENGTH = 200;

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    const str = String(unsafe);
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function createPostHTML(post, options = {}) {
    if (!post) return '';
    
    const showAuthor = options.showAuthor !== false;
    
    return `
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">
                    <a href="post.php?id=${escapeHtml(post.id)}" class="text-decoration-none text-dark">
                        ${escapeHtml(post.title)}
                    </a>
                </h5>
                ${showAuthor ? `
                    <h6 class="card-subtitle mb-2 text-muted">
                        By <a href="public_profile.php?UID=${escapeHtml(post.username)}">
                            ${escapeHtml(post.username)}
                        </a>
                    </h6>
                ` : ''}
                <p class="card-text">${escapeHtml(post.content ? post.content.substring(0, 200) : '')}...</p>
                <div class="d-flex justify-content-between align-items-center">
                    <p class="text-muted mb-0">${new Date(post.created_at).toLocaleString()}</p>
                    <span class="text-muted">
                        <i class="bi bi-hand-thumbs-up"></i> 
                        ${post.like_count || 0} likes
                    </span>
                </div>
                ${post.comments ? renderComments(post.comments) : ''}
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
                        <p class="mb-1">
                            ${comment.content.length > COMMENT_MAX_LENGTH 
                                ? escapeHtml(comment.content.substring(0, COMMENT_MAX_LENGTH)) + '...'
                                : escapeHtml(comment.content)}
                        </p>
                    </div>
                `;
            }).join('')}
        </div>`;
}
