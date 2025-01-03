let usersPage = 0;
let postsPage = 0;
let loadingUsers = false;
let loadingPosts = false;
const itemsPerPage = 10;
const searchTerm = window.searchData.term;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        
        button.classList.add('active');
        document.getElementById(button.dataset.tab).classList.add('active');

        // Load content if not already loaded
        if (button.dataset.tab === 'users' && usersPage === 0) {
            loadUsers();
        } else if (button.dataset.tab === 'posts' && postsPage === 0) {
            loadPosts();
        } else if (button.dataset.tab === 'communities') {
            showUnderConstructionMessage();
        }
    });
});

async function loadUsers() {
    if (loadingUsers) return;
    loadingUsers = true;

    const spinner = document.getElementById('users-loading');
    spinner.classList.remove('d-none');

    try {
        const response = await fetch(`../BackEnd/search_users.php?search=${searchTerm}&page=${usersPage}`);
        const result = await response.json();

        if (!result.data || result.data.length === 0) {
            if (usersPage === 0) {
                document.getElementById('users-container').innerHTML = '<div class="alert alert-info">No users found</div>';
            }
            return;
        }

        const container = document.getElementById('users-container');
        result.data.forEach(user => {
            container.insertAdjacentHTML('beforeend', createUserHTML(user));
        });

        usersPage++;
    } catch (error) {
        console.error('Error loading users:', error);
    } finally {
        loadingUsers = false;
        spinner.classList.add('d-none');
    }
}

async function loadPosts() {
    if (loadingPosts) return;
    loadingPosts = true;

    const spinner = document.getElementById('posts-loading');
    spinner.classList.remove('d-none');

    try {
        const response = await fetch(`../BackEnd/search_posts.php?search=${searchTerm}&page=${postsPage}`);
        const result = await response.json();

        if (!result.data || result.data.length === 0) {
            if (postsPage === 0) {
                document.getElementById('posts-container').innerHTML = '<div class="alert alert-info">No posts found</div>';
            }
            return;
        }

        const container = document.getElementById('posts-container');
        result.data.forEach(post => {
            container.insertAdjacentHTML('beforeend', createPostHTML(post));
        });

        postsPage++;
    } catch (error) {
        console.error('Error loading posts:', error);
    } finally {
        loadingPosts = false;
        spinner.classList.add('d-none');
    }
}

function createUserHTML(user) {
    return `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">
                    <a href="public_profile.php?UID=${escapeHtml(user.username)}">
                        ${escapeHtml(user.firstname)} ${escapeHtml(user.lastname)}
                    </a>
                </h5>
                <p class="card-text">
                    <small class="text-muted">@${escapeHtml(user.username)}</small>
                </p>
            </div>
        </div>
    `;
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
                <h6 class="card-subtitle mb-2 text-muted">
                    By <a href="public_profile.php?UID=${escapeHtml(post.username)}">
                        ${escapeHtml(post.username)}
                    </a>
                </h6>
                <p class="card-text">${escapeHtml(post.content.substring(0, 200))}...</p>
                <p class="text-muted">${new Date(post.created_at).toLocaleString()}</p>
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

/* Under Construction Message*/
function showUnderConstructionMessage() {
    const container = document.getElementById('communities-container');
    container.innerHTML = '<div class="alert alert-warning text-center">🚧 We are sorry! This Feature is under construction, be patient 🚧</div>';
}

// Initial load for active tab
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});

// Infinite scroll
window.addEventListener('scroll', () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
        const activeTab = document.querySelector('.tab.active').id;
        if (activeTab === 'users') {
            loadUsers();
        } else {
            loadPosts();
        }
    }
});
