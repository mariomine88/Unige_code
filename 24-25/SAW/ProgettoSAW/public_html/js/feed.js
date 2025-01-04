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
