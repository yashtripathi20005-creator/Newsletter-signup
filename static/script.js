document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageDiv = document.getElementById('message');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        const data = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email')
        };
        
        // Basic validation
        if (!data.first_name || !data.last_name || !data.email) {
            showMessage('Please fill in all fields.', 'error');
            return;
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        
        // Disable button and show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Subscribing...';
        
        try {
            // Send request to server
            const response = await fetch('/api/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                showMessage(result.message || 'Successfully subscribed! 🎉', 'success');
                form.reset();
            } else {
                showMessage(result.message || 'Subscription failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Network error. Please check your connection and try again.', 'error');
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Subscribe Now';
        }
    });
    
    /**
     * Display a message to the user
     * @param {string} text - The message text
     * @param {string} type - 'success' or 'error'
     */
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = 'message ' + type;
        messageDiv.style.display = 'block';
        
        // Auto-hide after 6 seconds
        clearTimeout(window.messageTimeout);
        window.messageTimeout = setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 6000);
    }
});

/**
 * Unsubscribe function (can be called from anywhere)
 * @param {string} email - The email to unsubscribe
 */
async function unsubscribeEmail(email) {
    try {
        const response = await fetch('/api/unsubscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            alert(result.message);
            return true;
        } else {
            alert(result.message || 'Unsubscribe failed.');
            return false;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
        return false;
    }
}

// Example: If you want to add unsubscribe link in footer
// document.querySelector('.footer')?.appendChild(
//     Object.assign(document.createElement('button'), {
//         textContent: 'Unsubscribe',
//         className: 'unsubscribe-btn',
//         onclick: () => {
//             const email = prompt('Enter your email to unsubscribe:');
//             if (email) unsubscribeEmail(email);
//         }
//     })
// );
