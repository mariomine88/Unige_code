import { initComments } from './comments.js';
import { handleLike } from './likes.js';

document.addEventListener('DOMContentLoaded', () => {
    if (typeof postData === 'undefined') {
        console.error('postData not defined');
        return;
    }

    // Initialize comments
    initComments(postData.postId);

    // Setup character counter for comment form
    const commentText = document.getElementById('commentText');
    const commentCount = document.getElementById('commentCount');
    if (commentText && commentCount) {
        commentText.addEventListener('input', () => {
            commentCount.textContent = 65535 - commentText.value.length;
        });
    }

    // Setup post like button
    const likeButton = document.getElementById('likeButton');
    if (likeButton) {
        likeButton.addEventListener('click', () => {
            handleLike(postData.postId, 'post', likeButton);
        });
    }

    // Share functionality
    document.getElementById('shareButton').addEventListener('click', async () => {
        const shareUrl = window.location.href;
        const shareTitle = document.querySelector('.card-body h3').textContent;

        try {
            if (navigator.share) {
                await navigator.share({
                    title: shareTitle,
                    url: shareUrl
                });
            } else {
                await navigator.clipboard.writeText(shareUrl);
                // Show temporary success message
                const button = document.getElementById('shareButton');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check"></i> URL Copied!';
                setTimeout(() => {
                    button.innerHTML = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('Error sharing:', err);
        }
    });
});
