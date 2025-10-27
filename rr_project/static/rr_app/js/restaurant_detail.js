// Restaurant Reservation System - Table Selection

document.addEventListener('DOMContentLoaded', function() {
    initializeTableSelection();
    initializeReservationForm();
});

// Table Selection System
function initializeTableSelection() {
    const tables = document.querySelectorAll('.table.available');
    const selectedTableInput = document.getElementById('selected-table');
    const tableStatusElement = document.getElementById('table-status');
    const reserveBtn = document.getElementById('reserve-btn');
    const guestCountSelect = document.querySelector('[name="guest_count"]');
    const tableSelectionInfo = document.getElementById('selected-table-info');
    
    let selectedTable = null;
    
    // Handle table clicks
    tables.forEach(table => {
        table.addEventListener('click', function() {
            const tableNumber = this.dataset.table;
            const tableCapacity = parseInt(this.dataset.capacity);
            const guestCount = parseInt(guestCountSelect?.value || 1);
            
            // Check if table capacity is suitable for guest count
            if (guestCount > tableCapacity) {
                showNotification(`Table ${tableNumber} can only accommodate ${tableCapacity} guests. Please select a larger table.`, 'warning');
                return;
            }
            
            // Remove previous selection
            if (selectedTable) {
                selectedTable.classList.remove('selected');
            }
            
            // Select new table
            selectedTable = this;
            this.classList.add('selected');
            
            // Update form
            if (selectedTableInput) {
                selectedTableInput.value = tableNumber;
            }
            
            // Update status display
            if (tableStatusElement) {
                tableStatusElement.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="color: var(--table-selected);">
                        <path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/>
                    </svg>
                    Table ${tableNumber} selected (${tableCapacity} seats)
                `;
                tableStatusElement.style.color = 'var(--table-selected)';
            }
            
            // Update info message
            if (tableSelectionInfo) {
                tableSelectionInfo.innerHTML = `
                    <p style="color: var(--table-selected); font-weight: 600;">
                        ✓ Table ${tableNumber} selected (Capacity: ${tableCapacity} guests)
                    </p>
                `;
            }
            
            // Enable reservation button
            if (reserveBtn) {
                reserveBtn.disabled = false;
                reserveBtn.style.opacity = '1';
            }
            
            showNotification(`Table ${tableNumber} selected successfully!`, 'success');
        });
        
        // Add hover effects with capacity info
        table.addEventListener('mouseenter', function() {
            const tableNumber = this.dataset.table;
            const tableCapacity = this.dataset.capacity;
            
            if (tableSelectionInfo && !this.classList.contains('reserved')) {
                const originalContent = tableSelectionInfo.innerHTML;
                tableSelectionInfo.innerHTML = `
                    <p style="color: var(--table-hover); font-weight: 600;">
                        Table ${tableNumber} - Capacity: ${tableCapacity} guests (Click to select)
                    </p>
                `;
                
                // Reset on mouse leave
                setTimeout(() => {
                    table.addEventListener('mouseleave', function() {
                        if (!this.classList.contains('selected')) {
                            tableSelectionInfo.innerHTML = originalContent;
                        }
                    }, { once: true });
                }, 100);
            }
        });
    });
    
    // Handle guest count changes
    if (guestCountSelect) {
        guestCountSelect.addEventListener('change', function() {
            const guestCount = parseInt(this.value);
            
            // Check if currently selected table can accommodate new guest count
            if (selectedTable) {
                const tableCapacity = parseInt(selectedTable.dataset.capacity);
                
                if (guestCount > tableCapacity) {
                    // Deselect current table
                    selectedTable.classList.remove('selected');
                    selectedTable = null;
                    
                    if (selectedTableInput) selectedTableInput.value = '';
                    if (tableStatusElement) {
                        tableStatusElement.innerHTML = 'No table selected';
                        tableStatusElement.style.color = 'var(--text-muted)';
                    }
                    
                    if (reserveBtn) {
                        reserveBtn.disabled = true;
                        reserveBtn.style.opacity = '0.6';
                    }
                    
                    showNotification(`Please select a table that can accommodate ${guestCount} guests.`, 'info');
                }
            }
            
            // Highlight suitable tables
            tables.forEach(table => {
                const tableCapacity = parseInt(table.dataset.capacity);
                const tableElement = table;
                
                // Remove any previous highlighting
                tableElement.style.filter = '';
                
                if (guestCount <= tableCapacity) {
                    // Suitable table
                    tableElement.style.filter = 'brightness(1.1)';
                } else {
                    // Table too small
                    tableElement.style.filter = 'brightness(0.7)';
                }
            });
            
            // Reset highlighting after 3 seconds
            setTimeout(() => {
                tables.forEach(table => {
                    if (!table.classList.contains('selected')) {
                        table.style.filter = '';
                    }
                });
            }, 3000);
        });
    }
}

// Reservation Form Handling
function initializeReservationForm() {
    const form = document.getElementById('reservation-form');
    const submitBtn = document.getElementById('reserve-btn');
    
    if (!form || !submitBtn) return;
    
    // Form validation
    const validateForm = () => {
        const selectedTable = document.getElementById('selected-table').value;
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        // Check if table is selected
        if (!selectedTable) {
            showNotification('Please select a table before making a reservation.', 'error');
            return false;
        }
        
        // Check required fields
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = 'var(--error)';
                field.addEventListener('input', function() {
                    this.style.borderColor = '';
                }, { once: true });
            }
        });
        
        if (!isValid) {
            showNotification('Please fill in all required fields.', 'error');
        }
        
        return isValid;
    };
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        // Show loading state
        const originalContent = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="animate-spin">
                <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
            </svg>
            Processing Reservation...
        `;
        
        // Add loading animation
        const style = document.createElement('style');
        style.textContent = `
            .animate-spin {
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        // Simulate processing time
        setTimeout(() => {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
            
            // Show success message
            showNotification('Reservation submitted successfully! Check your email for confirmation.', 'success');
            
            // Here you would normally submit the form data to your backend
            // For now, we'll just log the data
            const formData = new FormData(form);
            console.log('Reservation Data:', Object.fromEntries(formData));
            
            // Remove loading animation
            document.head.removeChild(style);
            
            // Optionally, you could redirect or show a confirmation modal
            // window.location.href = '/reservation-confirmation/';
            
        }, 2000);
    });
}


// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.reservation-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `reservation-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                ${getNotificationIcon(type)}
            </div>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                </svg>
            </button>
        </div>
    `;
    
    // Add styles
    const notificationStyles = `
        .reservation-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 400px;
            z-index: 1000;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            animation: slideIn 0.3s ease;
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: var(--white);
            border-left: 4px solid;
        }
        
        .notification-success .notification-content { border-color: var(--success); }
        .notification-error .notification-content { border-color: var(--error); }
        .notification-warning .notification-content { border-color: var(--warning); }
        .notification-info .notification-content { border-color: var(--info); }
        
        .notification-icon { flex-shrink: 0; }
        .notification-success .notification-icon { color: var(--success); }
        .notification-error .notification-icon { color: var(--error); }
        .notification-warning .notification-icon { color: var(--warning); }
        .notification-info .notification-icon { color: var(--info); }
        
        .notification-message {
            flex: 1;
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .notification-close:hover {
            background: var(--gray-100);
            color: var(--text-primary);
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    
    // Add styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'notification-styles';
        styleElement.textContent = notificationStyles;
        document.head.appendChild(styleElement);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,13H11V7H13M12,17.3A1.3,1.3 0 0,1 10.7,16A1.3,1.3 0 0,1 12,14.7A1.3,1.3 0 0,1 13.3,16A1.3,1.3 0 0,1 12,17.3M15.73,3H8.27L3,8.27V15.73L8.27,21H15.73L21,15.73V8.27L15.73,3Z"/></svg>',
        info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>'
    };
    return icons[type] || icons.info;
}

// Utility function for smooth scrolling (if needed)
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}