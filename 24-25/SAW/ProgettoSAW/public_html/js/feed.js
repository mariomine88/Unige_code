let page = 0;
let loading = false;
const postsPerPage = 10;

async function loadPosts() {
    if (loading) return;
    loading = true;

    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('d-none');

    try {
        const response = await fetch(`../BackEnd/get_posts.php?page=${page}&limit=${postsPerPage}`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Server error');
        }

        if (!result.data || !Array.isArray(result.data)) {
            console.error('Invalid data format received:', result);
            return;
        }

        if (result.data.length === 0) {
            spinner.remove();
            return;
        }

        const container = document.getElementById('posts-container');
        result.data.forEach(post => {
            const postElement = createPostElement(post);
            container.appendChild(postElement);
        });

        page++;
    } catch (error) {
        console.error('Error loading posts:', error);
        const container = document.getElementById('posts-container');
        container.innerHTML += `
            <div class="alert alert-danger">
                Failed to load posts. Please try refreshing the page.
            </div>`;
    } finally {
        loading = false;
        spinner.classList.add('d-none');
    }
}

function createPostElement(post) {
    const div = document.createElement('div');
    div.className = 'card mb-4';
    div.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">
                <a href="post.php?id=${post.id}" class="text-decoration-none text-dark">
                    ${escapeHtml(post.title)}
                </a>
            </h5>
            <h6 class="card-subtitle mb-2 text-muted">
                By <a href="public_profile.php?UID=${escapeHtml(post.username)}" class="text-muted">
                    ${escapeHtml(post.username)}
                </a>
            </h6>
            <p class="card-text">${escapeHtml(post.content.substring(0, 200))}...</p>
            <p class="text-muted">${new Date(post.created_at).toLocaleDateString()}</p>
            
            <div class="comments-section mt-3">
                ${post.comments.map(comment => `
                    <div class="comment border-bottom py-2">
                        <div class="d-flex justify-content-between">
                            <strong class="text-primary">${escapeHtml(comment.username)}</strong>
                            <small class="text-muted">
                                ${new Date(comment.created_at).toLocaleDateString()}
                            </small>
                        </div>
                        <p class="mb-1">${escapeHtml(comment.content)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    return div;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Infinite scroll handler
window.addEventListener('scroll', () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
        loadPosts();
    }
});

// Initial load
document.addEventListener('DOMContentLoaded', loadPosts);
