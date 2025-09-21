// EduTrack Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile-specific enhancements
    initializeMobileFeatures();
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('[role="alert"]');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 5000);

    // Add loading state to buttons
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                var originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                
                // Re-enable button after 3 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 3000);
            }
        });
    });

    // Add fade-in animation to cards
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(function() {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Real-time form validation
    var inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(input);
        });
    });

    function validateField(field) {
        var isValid = field.checkValidity();
        var feedback = field.parentNode.querySelector('.invalid-feedback');
        
        if (!isValid) {
            field.classList.add('is-invalid');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.appendChild(feedback);
            }
            feedback.textContent = field.validationMessage;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    }

    // Search functionality
    var searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var targetSelector = this.getAttribute('data-search');
            var targets = document.querySelectorAll(targetSelector);
            
            targets.forEach(function(target) {
                var text = target.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    target.style.display = '';
                } else {
                    target.style.display = 'none';
                }
            });
        });
    });

    // Progress bar animation
    var progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        var width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 500);
    });

    // Table row click handlers
    var tableRows = document.querySelectorAll('tbody tr[data-href]');
    tableRows.forEach(function(row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function() {
            window.location.href = this.getAttribute('data-href');
        });
    });

    // Print functionality
    var printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var targetSelector = this.getAttribute('data-print');
            var targetElement = document.querySelector(targetSelector);
            if (targetElement) {
                var printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <html>
                        <head>
                            <title>Print - EduTrack</title>
                            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                        </head>
                        <body>
                            ${targetElement.outerHTML}
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
            }
        });
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    var alertClass = 'alert-' + type;
    var alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            var alert = container.querySelector('.alert');
            if (alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Mobile-specific features
function initializeMobileFeatures() {
    // Detect mobile device
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        // Add mobile class to body
        document.body.classList.add('mobile-device');
        
        // Improve touch interactions
        improveTouchInteractions();
        
        // Optimize mobile navigation
        optimizeMobileNavigation();
        
        // Add mobile-specific event listeners
        addMobileEventListeners();
    }
    
    // Responsive table handling
    handleResponsiveTables();
}

function improveTouchInteractions() {
    // Add touch feedback to buttons
    var buttons = document.querySelectorAll('button, a, .btn');
    buttons.forEach(function(button) {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Improve form interactions
    var inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            // Scroll to input on mobile
            setTimeout(function() {
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    });
}

function optimizeMobileNavigation() {
    var mobileMenu = document.getElementById('mobile-menu');
    var mobileMenuButton = document.querySelector('[onclick="toggleMobileMenu()"]');
    
    if (mobileMenu && mobileMenuButton) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
        
        // Close mobile menu when clicking on a link
        var mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
            });
        });
    }
}

function addMobileEventListeners() {
    // Prevent double-tap zoom
    var lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        var now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            // Recalculate layouts after orientation change
            var tables = document.querySelectorAll('.table-responsive');
            tables.forEach(function(table) {
                table.style.width = '100%';
            });
        }, 100);
    });
}

function handleResponsiveTables() {
    // Check if we need to show mobile cards instead of tables
    function checkTableResponsiveness() {
        var tables = document.querySelectorAll('.desktop-table');
        var mobileCards = document.querySelectorAll('.mobile-table');
        
        tables.forEach(function(table) {
            var tableWidth = table.offsetWidth;
            var containerWidth = table.parentElement.offsetWidth;
            
            if (tableWidth > containerWidth) {
                // Table is overflowing, show mobile cards
                table.style.display = 'none';
                var mobileCard = table.parentElement.querySelector('.mobile-table');
                if (mobileCard) {
                    mobileCard.style.display = 'block';
                }
            } else {
                // Table fits, show table
                table.style.display = 'table';
                var mobileCard = table.parentElement.querySelector('.mobile-table');
                if (mobileCard) {
                    mobileCard.style.display = 'none';
                }
            }
        });
    }
    
    // Check on load and resize
    checkTableResponsiveness();
    window.addEventListener('resize', checkTableResponsiveness);
}
