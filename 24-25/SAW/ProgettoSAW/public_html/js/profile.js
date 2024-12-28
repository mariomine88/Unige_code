let page = 0;
let loading = false;
const postsPerPage = 10;

async function loadUserPosts() {
    if (loading) return;
    loading = true;

    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('d-none');

    try {
        const response = await fetch(`../BackEnd/get_user_posts.php?user_id=${window.userData.userId}&page=${page}&limit=${postsPerPage}`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Server error');
        }

        if (!result.data || result.data.length === 0) {
            if (page === 0) {
                document.getElementById('posts-container').innerHTML = '<p class="text-muted">No posts found.</p>';
            }
            document.getElementById('loadMorePosts').style.display = 'none';
            return;
        }

        const container = document.getElementById('posts-container');
        result.data.forEach(post => {
            container.insertAdjacentHTML('beforeend', createPostHTML(post));
        });

        page++;
    } catch (error) {
        console.error('Error loading posts:', error);
        document.getElementById('posts-container').innerHTML += `
            <div class="alert alert-danger">
                Failed to load posts. Please try refreshing the page.
            </div>`;
    } finally {
        loading = false;
        spinner.classList.add('d-none');
    }
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
                <p class="text-muted">Posted on ${new Date(post.created_at).toLocaleString()}</p>
                
                <div class="comments-section mt-3">
                    ${post.comments.map(comment => `
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
                            <p class="mb-1">${escapeHtml(comment.content)}</p>
                        </div>
                    `).join('')}
                </div>
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

document.getElementById('loadMorePosts').addEventListener('click', loadUserPosts);
document.addEventListener('DOMContentLoaded', loadUserPosts);
