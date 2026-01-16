document.addEventListener('DOMContentLoaded', () => {
    const favoriteButton = document.getElementById('favorite-btn');
    if (!favoriteButton) return;

    const slug = favoriteButton.dataset.slug;
    let isFavorited = favoriteButton.dataset.isFavorited === 'true';

    favoriteButton.addEventListener('click', () => {
        favoriteButton.disabled = true;
        favoriteButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i>Processing...';

        postData('/save-recipe/', {slug: slug})
            .then(response => {
                isFavorited = response.is_favorited;
                updateFavoriteButton(isFavorited);
            })
            .catch(error => {
                console.error('Favorite error:', error);
                showFavoriteError('Something went wrong. Try again later.');
            })
            .finally(() => {
                favoriteButton.disabled = false;
            });
    });
});

function postData(url, data) {
    return fetch(url, {
        method: "POST", headers: {
            "Content-Type": "application/json", "X-CSRFToken": Cookies.get("csrftoken")
        }, body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        });
}

function updateFavoriteButton(isFavorited) {
    const btn = document.getElementById('favorite-btn');
    if (!btn) return;

    if (isFavorited) {
        btn.innerHTML = '<i class="fa-solid fa-heart me-1"></i>In Favorites';
        btn.classList.remove('btn-outline-danger');
        btn.classList.add('btn-danger');
    } else {
        btn.innerHTML = '<i class="fa-regular fa-heart me-1"></i>Add to Favorites';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-outline-danger');
    }
}

function showFavoriteError(text) {
    const container = document.getElementById('favorite-btn').parentElement;

    const oldMessage = container.querySelector('.favorite-error');
    if (oldMessage) oldMessage.remove();

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('favorite-error', 'text-danger', 'mt-2');
    messageDiv.textContent = text;

    container.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}