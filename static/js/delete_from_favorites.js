document.addEventListener('DOMContentLoaded', () => {
    const removeButtons = document.querySelectorAll('.remove-favorite-btn');
    if (!removeButtons.length) return;

    removeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const slug = btn.dataset.slug;
            if (!slug) return;

            btn.disabled = true;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i>Removing...';

            postData('remove-saved-recipe/', {slug})
                .then(data => {
                    if (data.status === 'ok' && data.removed) {
                        const card = btn.closest('.col, .card, .recipe-card, [class*="col-"]');
                        if (card) {
                            card.style.opacity = '0';
                            card.style.transform = 'scale(0.95)';
                            card.style.transition = 'all 0.4s ease';
                            setTimeout(() => card.remove(), 400);
                        }
                    } else {
                        showError(btn, data.message || 'Failed to delete');
                    }
                })
                .catch(() => {
                    showError(btn, 'Error. Try again later');
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.innerHTML = originalHTML;
                });
        });
    });
});


function postData(url, data) {
    return fetch(url, {
        method: 'POST', headers: {
            'Content-Type': 'application/json', 'X-CSRFToken': Cookies.get('csrftoken')
        }, body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        });
}


function showError(button, message) {
    let container = button.closest('.card-body') || button.parentElement;

    container.querySelector('.remove-error')?.remove();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'remove-error text-danger mt-2 small';
    errorDiv.textContent = message;

    container.appendChild(errorDiv);

    setTimeout(() => errorDiv.remove(), 4000);
}