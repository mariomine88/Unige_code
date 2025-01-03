document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('likeButton');
    if (!likeButton) return;

    let isLiked = window.postData.isLiked;

    likeButton.addEventListener('click', async function() {
        try {
            const response = await fetch('../BackEnd/like_handler.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    targetId: window.postData.postId,
                    type: 'post',
                    action: isLiked ? 'unlike' : 'like'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                isLiked = !isLiked;
                likeButton.classList.toggle('btn-outline-primary');
                likeButton.classList.toggle('btn-primary');
                
                const likeCount = document.getElementById('likeCount');
                if (likeCount) {
                    likeCount.textContent = data.likeCount;
                }
            } else {
                console.error('Like operation failed:', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
