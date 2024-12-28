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

// Load more comments functionality
let page = 1;
let loading = false;

document.getElementById('loadMoreComments').addEventListener('click', async function() {
    if (loading) return;
    loading = true;
    
    const order = commentOrder.value;
    const postId = new URLSearchParams(window.location.search).get('id');
    
    try {
        const response = await fetch(`../BackEnd/get_comments.php?post_id=${postId}&page=${page}&order=${order}`);
        const result = await response.json();
        
        if (!result.data || result.data.length === 0) {
            this.style.display = 'none';
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
});

function createCommentHTML(comment) {
    return `
        <div class="comment card mt-2">
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
            </div>
        </div>
    `;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
