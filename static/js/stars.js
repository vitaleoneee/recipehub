document.addEventListener('DOMContentLoaded', () => {
    const ratingBox = document.querySelector('.star-rating');
    if (!ratingBox) return;

    const stars = ratingBox.querySelectorAll('i');
    const recipeSlug = ratingBox.dataset.slug;
    let selectedRating = 0;
    let isSubmitting = false;

    stars.forEach((star, index) => {
        const ratingValue = index + 1;

        star.addEventListener('mouseenter', () => {
            highlightStars(ratingValue);
        });

        star.addEventListener('mouseleave', () => {
            highlightStars(selectedRating);
        });

        star.addEventListener('click', () => {
            if (isSubmitting) return;
            isSubmitting = true;

            selectedRating = ratingValue;
            highlightStars(selectedRating);

            postData('/reviews/send-review/', {
                rating: selectedRating, slug: recipeSlug
            })
                .then(response => {
                    showReviewMessage('Thanks for your feedback!', response.average_rating);
                })
                .catch(error => {
                    showReviewMessage('An error occurred, please try again.');
                })
                .finally(() => {
                    isSubmitting = false;
                });
        });
    });

    function highlightStars(rating) {
        stars.forEach((star, idx) => {
            star.classList.toggle('fa-solid', idx < rating);
            star.classList.toggle('fa-regular', idx >= rating);
        });
    }
});

function postData(url, data) {
    return fetch(url, {
        method: "POST", headers: {
            "Content-Type": "application/json", "X-CSRFToken": Cookies.get("csrftoken")
        }, body: JSON.stringify(data)
    }).then(response => {
        if (!response.ok) {
            throw new Error(`Request Error: ${response.status}`);
        }
        return response.json();
    });
}

function showReviewMessage(text, avg = null) {
    const container = document.getElementById('rate_div');

    const oldRating = document.getElementById('rating-info');
    if (oldRating) oldRating.remove();

    const oldMessage = document.getElementById('review-message');
    if (oldMessage) oldMessage.remove();

    const ratingDiv = document.createElement('div');
    ratingDiv.id = 'rating-info';
    ratingDiv.classList.add('mt-2', 'd-flex', 'align-items-center', 'gap-2');

    if (avg == null) {
        const noRating = document.createElement('span');
        noRating.classList.add('text-muted', 'fst-italic');
        noRating.textContent = 'No ratings yet – be the first!';
        ratingDiv.appendChild(noRating);
    } else {
        const starIcon = document.createElement('i');
        starIcon.classList.add('fa-solid', 'fa-star', 'text-warning');

        const ratingText = document.createElement('span');
        ratingText.classList.add('fw-semibold');
        ratingText.textContent = `Average rating: ${avg}/5`;

        ratingDiv.appendChild(starIcon);
        ratingDiv.appendChild(ratingText);
    }

    const messageDiv = document.createElement('div');
    messageDiv.id = 'review-message';
    messageDiv.classList.add('mt-2', 'text-success');
    messageDiv.textContent = text;

    container.appendChild(ratingDiv);
    container.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

