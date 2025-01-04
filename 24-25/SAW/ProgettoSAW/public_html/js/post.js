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
});
