// Restaurant Detail Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeReservationForm();
    initializeInteractiveButtons();
    initializeSocialActions();
});

// Smooth scroll to reservation section
function scrollToReservation() {
    const reservationSection = document.getElementById('reservation-section');
    if (reservationSection) {
        reservationSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        // Add a subtle highlight effect
        reservationSection.style.boxShadow = '0 0 20px rgba(24, 119, 242, 0.3)';
        setTimeout(() => {
            reservationSection.style.boxShadow = '';
        }, 2000);
    }
}

// Initialize reservation form functionality
function initializeReservationForm() {
    const form = document.getElementById('reservation-form');
    const submitBtn = document.getElementById('reserve-btn');
    
    if (!form || !submitBtn) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Add loading state
        const originalContent = submitBtn.innerHTML;
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="animation: spin 1s linear infinite;">
                <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
            </svg>
            Processing...
        `;
        
        // Simulate form submission (replace with actual submission logic)
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.innerHTML = originalContent;
            
            // Show success message (you can customize this)
            showMessage('Reservation request submitted successfully!', 'success');
        }, 2000);
    });
    
    // Form validation
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}

// Field validation
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    // Remove existing error styling
    field.classList.remove('error');
    
    if (!value && field.hasAttribute('required')) {
        field.classList.add('error');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.classList.add('error');
            return false;
        }
    }
    
    return true;
}

// Clear field error styling
function clearFieldError(e) {
    e.target.classList.remove('error');
}

// Initialize interactive buttons
function initializeInteractiveButtons() {
    // Bookmark button
    const bookmarkBtn = document.querySelector('.bookmark-btn');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            const isBookmarked = this.classList.contains('active');
            
            // Update button appearance
            if (isBookmarked) {
                this.style.background = 'var(--instagram-pink)';
                this.style.color = 'white';
                this.style.borderColor = 'var(--instagram-pink)';
                showMessage('Restaurant bookmarked!', 'success');
            } else {
                this.style.background = '';
                this.style.color = '';
                this.style.borderColor = '';
                showMessage('Bookmark removed', 'info');
            }
        });
    }
    
    // Share button
    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            if (navigator.share) {
                navigator.share({
                    title: document.title,
                    url: window.location.href
                });
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(window.location.href).then(() => {
                    showMessage('Link copied to clipboard!', 'success');
                });
            }
        });
    }
}

// Initialize social-like actions for reviews
function initializeSocialActions() {
    // Like buttons
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('liked');
            const isLiked = this.classList.contains('liked');
            
            if (isLiked) {
                this.style.color = 'var(--instagram-pink)';
                this.innerHTML = this.innerHTML.replace('Like', 'Liked');
            } else {
                this.style.color = '';
                this.innerHTML = this.innerHTML.replace('Liked', 'Like');
            }
        });
    });
    
    // Reply buttons (placeholder functionality)
    const replyButtons = document.querySelectorAll('.reply-btn');
    replyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            showMessage('Reply feature coming soon!', 'info');
        });
    });
}

// Utility function to show messages
function showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `message-toast message-${type}`;
    messageEl.textContent = message;
    
    // Style the message
    Object.assign(messageEl.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 16px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        fontSize: '14px',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px',
        wordWrap: 'break-word'
    });
    
    // Set background color based on type
    const colors = {
        success: '#00c851',
        error: '#ff4444',
        warning: '#ffbb33',
        info: '#1877F2'
    };
    messageEl.style.backgroundColor = colors[type] || colors.info;
    
    // Add to page
    document.body.appendChild(messageEl);
    
    // Animate in
    setTimeout(() => {
        messageEl.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        messageEl.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 300);
    }, 3000);
}

// Bookmark restaurant function (called from template)
function bookmarkRestaurant(restaurantId) {
    const btn = event.target.closest('.bookmark-btn');
    if (btn) {
        btn.click();
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .form-group input.error,
    .form-group select.error,
    .form-group textarea.error {
        border-color: #ff4444;
        box-shadow: 0 0 0 3px rgba(255, 68, 68, 0.1);
    }
    
    .btn.loading {
        opacity: 0.7;
        pointer-events: none;
    }
    
    .action-btn.liked {
        color: var(--instagram-pink) !important;
    }
    
    .bookmark-btn.active {
        background: var(--instagram-pink) !important;
        color: white !important;
        border-color: var(--instagram-pink) !important;
    }
    
    .feed-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feed-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .review-post {
        transition: background-color 0.2s ease, transform 0.2s ease;
    }
    
    .review-post:hover {
        transform: translateX(4px);
    }
`;
document.head.appendChild(style);