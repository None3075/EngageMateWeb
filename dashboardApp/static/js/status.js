// Track the current status to avoid showing the same notification repeatedly
let currentStatus = null;
let notificationTimer = null;

function checkClassStatus() {
    fetch('/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Only show notification if status has changed
            if (data.status !== currentStatus) {
                currentStatus = data.status;
                showNotification(data.status);
            }
        })
        .catch(error => console.error('Error fetching status:', error));
}

function showNotification(status) {
    // Create notification container if it doesn't exist
    let notification = document.getElementById('status-notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'status-notification';
        notification.style.position = 'fixed';
        notification.style.bottom = '20px'; // Changed from top to bottom
        notification.style.right = '20px';
        notification.style.padding = '15px 20px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        notification.style.zIndex = '1000';
        notification.style.transition = 'opacity 0.3s ease-in-out';
        notification.style.cursor = 'pointer';
        document.body.appendChild(notification);
    }
    
    // Clear previous content and any existing timers
    notification.innerHTML = '';
    if (notificationTimer) {
        clearTimeout(notificationTimer);
        notificationTimer = null;
    }
    
    // Add message based on status
    const message = document.createElement('span');
    message.style.marginRight = '15px';
    
    // Set content and styling based on status
    if (status === 'ongoing') {
        notification.style.backgroundColor = '#4CAF50';
        notification.style.color = 'white';
        message.textContent = 'The class is ongoing';
    } else if (status === 'break') {
        notification.style.backgroundColor = '#FF9800';
        notification.style.color = 'white';
        message.textContent = 'The class is on break';
    } else {
        // Default case for any other status (including 'yes')
        notification.style.backgroundColor = '#2196F3';
        notification.style.color = 'white';
        message.textContent = 'Class is not in session';
    }
    
    // Add message to notification
    notification.appendChild(message);
    
    // Add close button
    const closeBtn = document.createElement('span');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.fontWeight = 'bold';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.marginLeft = '10px';
    closeBtn.onclick = function() {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 300);
    };
    notification.appendChild(closeBtn);
    
    // Show the notification
    notification.style.display = 'block';
    notification.style.opacity = '1';
    
    // Only auto-hide for statuses other than 'ongoing' and 'break'
    if (status !== 'ongoing' && status !== 'break') {
        notificationTimer = setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 300);
        }, 5000);
    }
}

// Check status every 1 seconds
setInterval(checkClassStatus, 1000);