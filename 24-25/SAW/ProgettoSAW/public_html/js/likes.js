export async function handleLike(targetId, type, button) {
    try {
        const isLiked = button.classList.contains('btn-primary');
        const response = await fetch('../BackEnd/like_handler.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                targetId,
                type,
                action: isLiked ? 'unlike' : 'like'
            })
        });

        const data = await response.json();
        if (data.success) {
            button.classList.toggle('btn-primary');
            button.classList.toggle('btn-outline-primary');
            const countElement = type === 'post' ? 
                button.querySelector('#likeCount') : 
                button.querySelector('.like-count');
            if (countElement) {
                countElement.textContent = data.likeCount;
            }
        }
    } catch (error) {
        console.error('Like operation failed:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('likeButton');
    if (!likeButton) return;

    likeButton.addEventListener('click', function() {
        handleLike(window.postData.postId, 'post', likeButton);
    });
});
