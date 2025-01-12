$(document).ready(function() {
    $('#joinButton').on('click', handleMembershipAction);
    loadCommunityPosts();
    
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
            loadCommunityPosts();
        }
    });
});

function handleMembershipAction() {
    const $button = $('#joinButton');
    const action = $button.text().trim() === 'Join Community' ? 'join' : 'leave';
    
    $.ajax({
        url: '../BackEnd/follow_handler.php', 
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            communityId: window.communityData.id,
            action: action
        }),
        success: function(response) {
            if (response.success) {
                if (action === 'join') {
                    $button.text('Leave Community');
                    $button.removeClass('btn-primary').addClass('btn-secondary');
                } else {
                    $button.text('Join Community');
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

function loadCommunityPosts() {
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
            community_id: window.communityData.id,
            page: page,
            limit: postsPerPage
        },
        success: function(result) {
            if (!result.data || result.data.length === 0) {
                if (page === 0) {
                    $container.html('<p class="text-muted">No posts yet!</p>');
                }
                $spinner.remove();
                return;
            }

            result.data.forEach(post => {
                const postHTML = createPostHTML(post, {
                    showAuthor: true,
                    showCommunity: false, 
                });
                $container.append(postHTML);
            });
            page++;
        },
        error: function(xhr, status, error) {
            console.error('Error loading posts:', error);
            $container.append(`
                <div class="alert alert-danger">
                    Failed to load community posts. Please try refreshing the page.
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

