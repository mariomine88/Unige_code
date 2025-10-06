let usersPage = 0;
let postsPage = 0;
let loadingUsers = false;
let loadingPosts = false;
const itemsPerPage = 10;
const searchTerm = window.searchData.term;
let noMoreUsers = false;
let noMorePosts = false;
let communitiesPage = 0;
let loadingCommunities = false;
let noMoreCommunities = false;

// Tab switching
$('.tab-button').on('click', function() {
    $('.tab-button').removeClass('active');
    $('.tab').removeClass('active');
    
    $(this).addClass('active');
    $(`#${$(this).data('tab')}`).addClass('active');

    if ($(this).data('tab') === 'users' && usersPage === 0) {
        loadUsers();
    } else if ($(this).data('tab') === 'posts' && postsPage === 0) {
        loadPosts();
    } else if ($(this).data('tab') === 'communities') {
        loadCommunities();
    }
});

function loadUsers() {
    if (loadingUsers || noMoreUsers) return;
    loadingUsers = true;

    const $spinner = $('#users-loading');
    const $container = $('#users-container');
    
    $spinner.removeClass('d-none');

    $.ajax({
        url: '../BackEnd/search_users.php',
        method: 'GET',
        data: {
            search: searchTerm,
            page: usersPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                noMoreUsers = true;
                if (usersPage === 0) {
                    $container.html('<div class="alert alert-info">No users found</div>');
                }
                $spinner.remove(); // Remove spinner completely when no more results
                return;
            }

            result.data.forEach(user => {
                $container.append(createUserHTML(user));
            });
            usersPage++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading users:', error);
            $container.append('<div class="alert alert-danger">Failed to load users. Please try refreshing the page.</div>');
        },
        complete: function() {
            loadingUsers = false;
            if (!noMoreUsers) {
                $spinner.addClass('d-none');
            }
        }
    });
}

function loadPosts() {
    if (loadingPosts || noMorePosts) return;
    loadingPosts = true;

    const $spinner = $('#posts-loading');
    const $container = $('#posts-container');
    
    $spinner.removeClass('d-none');

    $.ajax({
        url: '../BackEnd/search_posts.php',
        method: 'GET',
        data: {
            search: searchTerm,
            page: postsPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                noMorePosts = true;
                if (postsPage === 0) {
                    $container.html('<div class="alert alert-info">No posts found</div>');
                }
                $spinner.remove(); // Remove spinner completely when no more results
                return;
            }

            result.data.forEach(post => {
                $container.append(createPostHTML(post, { 
                    showAuthor: true,
                    showCommunity: true 
                })); 
            });
            postsPage++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading posts:', error);
            $container.append('<div class="alert alert-danger">Failed to load posts. Please try refreshing the page.</div>');
        },
        complete: function() {
            loadingPosts = false;
            if (!noMorePosts) {
                $spinner.addClass('d-none');
            }
        }
    });
}

function loadCommunities() {
    if (loadingCommunities || noMoreCommunities) return;
    loadingCommunities = true;

    const $spinner = $('#communities-loading');
    const $container = $('#communities-container');
    
    $spinner.removeClass('d-none');
    
    $.ajax({
        url: '../BackEnd/search_community.php',
        method: 'GET',
        data: {
            search: searchTerm,
            page: communitiesPage,
            limit: itemsPerPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                noMoreCommunities = true;
                if (communitiesPage === 0) {
                    $container.html('<div class="alert alert-info">No communities found</div>');
                }
                $spinner.remove();
                return;
            }

            result.data.forEach(community => {
                $container.append(`
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="community_profile.php?name=${encodeURIComponent(community.name)}">
                                    ${community.name}
                                </a>
                            </h5>
                            <p class="card-text">${community.description || 'No description available'}</p>
                            <p class="text-muted">${community.member_count} Members</p>
                        </div>
                    </div>
                `);
            });
            communitiesPage++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading communities:', error);
            $container.append('<div class="alert alert-danger">Failed to load communities. Please try refreshing the page.</div>');
        },
        complete: function() {
            loadingCommunities = false;
            if (!noMoreCommunities) {
                $spinner.addClass('d-none');
            }
        }
    });
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

// Initial load for active tab
$(document).ready(function() {
    loadUsers();
    
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
            const activeTab = $('.tab.active').attr('id');
            if (activeTab === 'users' && !noMoreUsers) {
                loadUsers();
            } else if (activeTab === 'posts' && !noMorePosts) {
                loadPosts();
            } else if (activeTab === 'communities' && !noMoreCommunities) {
                loadCommunities();
            }
        }
    });
});
