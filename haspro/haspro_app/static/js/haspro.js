function deleteObject(url, confirmMessage) {
    if (confirm(confirmMessage)) {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/';  // Redirect to home or another page
            } else {
                alert('Error deleting the object.');
            }
        });
    }
}