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


function toggleAllFaults(source) {
    checkboxes = document.querySelectorAll('#add-faults-section input[type="checkbox"][name="fault"]');
    for(var i=0, n=checkboxes.length;i<n;i++) {
        checkboxes[i].checked = source.checked;
    }
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById(sectionId.replace('-section', '-icon'));
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.textContent = '▼';
    } else {
        section.style.display = 'none';
        icon.textContent = '▶';
    }
}