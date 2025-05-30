$(document).ready(function() {
    $('#followButton').on('click', handleFollowAction);
    loadUserPosts();
    
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
            loadUserPosts();
        }
    });
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
    const $container = $('#posts-container');
    
    if ($spinner.length) {
        $spinner.removeClass('d-none');
    }

    $.ajax({
        url: '../BackEnd/get_posts.php',
        method: 'GET',
        data: {
            user_id: window.userData.userId,
            page: page,
            limit: postsPerPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                if (page === 0) {
                    $container.html('<p class="text-muted">No posts found.</p>');
                }
                $spinner.remove();
                return;
            }

            result.data.forEach(post => {
                $container.append(createPostHTML(post, { 
                    showAuthor: false,
                    showCommunity: true 
                }));
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


