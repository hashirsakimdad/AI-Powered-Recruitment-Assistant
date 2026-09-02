/**
 * AI Recruit - Modern ATS Platform JavaScript
 * Handles drag-and-drop uploads, theme switching, and interactions
 */

// ============================================
// Theme Management
// ============================================

(function() {
  'use strict';
  
  // Initialize theme from localStorage or system preference
  const savedTheme = localStorage.getItem('theme') || 'dark';
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme === 'auto' ? (prefersDark ? 'dark' : 'light') : savedTheme;
  
  document.documentElement.setAttribute('data-theme', theme);
  
  // Theme toggle handlers
  document.addEventListener('DOMContentLoaded', function() {
    const themeToggles = document.querySelectorAll('.theme-toggle');
    themeToggles.forEach(toggle => {
      toggle.addEventListener('click', function(e) {
        e.preventDefault();
        const newTheme = this.getAttribute('data-theme');
        setTheme(newTheme);
      });
    });
  });
  
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }
})();

// ============================================
// Drag and Drop Upload
// ============================================

function setupDragAndDrop(uploadAreaId, fileInputId) {
  const uploadArea = document.getElementById(uploadAreaId);
  const fileInput = document.getElementById(fileInputId);
  
  if (!uploadArea || !fileInput) return;
  
  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  // Highlight drop area when item is dragged over it
  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => {
      uploadArea.classList.add('dragover');
    }, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => {
      uploadArea.classList.remove('dragover');
    }, false);
  });
  
  // Handle dropped files
  uploadArea.addEventListener('drop', handleDrop, false);
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      fileInput.files = files;
      handleFileSelect(files[0], uploadAreaId);
    }
  }
  
  // Handle file input change
  fileInput.addEventListener('change', function(e) {
    if (this.files.length > 0) {
      handleFileSelect(this.files[0], uploadAreaId);
    }
  });
  
  function handleFileSelect(file, areaId) {
    const uploadArea = document.getElementById(areaId);
    const uploadContent = uploadArea.querySelector('.upload-content');
    const uploadProgress = uploadArea.querySelector('.upload-progress');
    const statusText = uploadArea.querySelector('.status-text');
    
    // Validate file type
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file only.');
      return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }
    
    // Show file name
    if (uploadContent) {
      uploadContent.innerHTML = `
        <i class="bi bi-file-earmark-pdf display-4 text-primary mb-3"></i>
        <p class="mb-2 fw-semibold">${file.name}</p>
        <p class="text-muted small mb-0">${(file.size / 1024).toFixed(2)} KB</p>
        <button type="button" class="btn btn-sm btn-outline-secondary mt-2" onclick="document.getElementById('${fileInputId}').value = ''; location.reload();">
          Change File
        </button>
      `;
    }
  }
}

// Initialize drag and drop for all upload areas on page load
document.addEventListener('DOMContentLoaded', function() {
  // Find all upload areas and initialize them
  const uploadAreas = document.querySelectorAll('[id^="uploadArea"]');
  uploadAreas.forEach(area => {
    const areaId = area.id;
    const jobId = areaId.replace('uploadArea', '');
    const fileInputId = `fileInput${jobId}`;
    setupDragAndDrop(areaId, fileInputId);
  });
  
  // Setup form submission with progress indicators
  const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
  uploadForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const fileInput = form.querySelector('input[type="file"]');
      if (!fileInput || !fileInput.files.length) {
        e.preventDefault();
        alert('Please select a file to upload.');
        return;
      }
      
      // Show loading state
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Processing...';
      }
      
      // Show progress (simulated)
      const uploadArea = form.querySelector('.upload-area');
      if (uploadArea) {
        const uploadContent = uploadArea.querySelector('.upload-content');
        const uploadProgress = uploadArea.querySelector('.upload-progress');
        
        if (uploadContent && uploadProgress) {
          uploadContent.classList.add('d-none');
          uploadProgress.classList.remove('d-none');
          
          const progressBar = uploadProgress.querySelector('.progress-bar');
          const statusText = uploadProgress.querySelector('.status-text');
          
          // Simulate progress
          let progress = 0;
          const interval = setInterval(() => {
            progress += 10;
            if (progressBar) progressBar.style.width = progress + '%';
            
            if (statusText) {
              if (progress < 30) {
                statusText.textContent = 'Extracting text from PDF...';
              } else if (progress < 60) {
                statusText.textContent = 'Validating resume...';
              } else if (progress < 90) {
                statusText.textContent = 'Analyzing skills and experience...';
              } else {
                statusText.textContent = 'Generating personalized feedback...';
              }
            }
            
            if (progress >= 100) {
              clearInterval(interval);
            }
          }, 200);
        }
      }
    });
  });
});

// ============================================
// Chart Rendering
// ============================================

function renderBarChart(canvasId, labels, scores) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !labels.length || !scores.length) return;
  
  // Get theme
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94A3B8' : '#64748b';
  const gridColor = isDark ? '#2A2F42' : '#e2e8f0';
  const tooltipBg = isDark ? '#1A1F2E' : '#ffffff';
  const tooltipBorder = isDark ? '#40F2DA' : '#5C58F1';
  
  const canvas = ctx.getContext('2d');
  const gradient = canvas.createLinearGradient(0, 0, 0, canvas.canvas.height || 240);
  gradient.addColorStop(0, '#40F2DA');
  gradient.addColorStop(1, '#5C58F1');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'AI Match Score',
        data: scores,
        backgroundColor: gradient,
        borderRadius: 8,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: tooltipBg,
          titleColor: '#F8FAFC',
          bodyColor: '#94A3B8',
          borderColor: tooltipBorder,
          borderWidth: 1,
          padding: 12,
          callbacks: {
            label: function(context) {
              return 'Match Score: ' + context.parsed.y + '%';
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            color: textColor,
            callback: function(value) {
              return value + '%';
            }
          },
          grid: {
            color: gridColor,
          }
        },
        x: {
          ticks: {
            color: textColor,
            maxRotation: 45,
            minRotation: 45,
          },
          grid: {
            display: false,
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    },
  });
}

// ============================================
// Smooth Scrolling
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href.length > 1) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });
});

// ============================================
// Form Validation Enhancement
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });
});

// ============================================
// Auto-dismiss Alerts
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});

// ============================================
// Tooltip Initialization
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// ============================================
// Loading States
// ============================================

function showLoading(element) {
  if (element) {
    element.disabled = true;
    element.dataset.originalText = element.innerHTML;
    element.innerHTML = '<span class="loading-spinner me-2"></span>Loading...';
  }
}

function hideLoading(element) {
  if (element && element.dataset.originalText) {
    element.disabled = false;
    element.innerHTML = element.dataset.originalText;
    delete element.dataset.originalText;
  }
}

// ============================================
// 3D Card Tilt Effect for Auth Pages
// ============================================

function setup3DCardTilt() {
  const authCard = document.querySelector('.auth-card');
  if (!authCard) return;
  
  // Add 3D class
  authCard.classList.add('auth-card-3d');
  
  let isTiltEnabled = true;
  
  // Check if user prefers reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    isTiltEnabled = false;
  }
  
  if (!isTiltEnabled) return;
  
  authCard.addEventListener('mousemove', function(e) {
    const rect = authCard.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;
    
    authCard.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
  });
  
  authCard.addEventListener('mouseleave', function() {
    authCard.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
  });
  
  authCard.addEventListener('mouseenter', function() {
    authCard.style.transition = 'transform 0.1s ease-out';
  });
}

// Initialize 3D effects on page load
document.addEventListener('DOMContentLoaded', function() {
  setup3DCardTilt();
});

// ============================================
// Enhanced Form Input Animations
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('.auth-form .form-control');
  
  inputs.forEach(input => {
    // Add focus animation
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('input-focused');
      const icon = this.parentElement.querySelector('.input-group-text i');
      if (icon) {
        icon.style.transform = 'scale(1.2)';
        icon.style.color = 'var(--primary-color)';
      }
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('input-focused');
      const icon = this.parentElement.querySelector('.input-group-text i');
      if (icon) {
        icon.style.transform = 'scale(1)';
        icon.style.color = '';
      }
    });
    
    // Add value detection for floating labels effect
    input.addEventListener('input', function() {
      if (this.value) {
        this.classList.add('has-value');
      } else {
        this.classList.remove('has-value');
      }
    });
  });
});

// ============================================
// Animated Star Field Background
// ============================================

function createStarField() {
  return;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  setupRecruiterDecisionControls();
});

// ============================================
// Recruiter Decision Controls
// ============================================
function setupRecruiterDecisionControls() {
  const statusButtons = document.querySelectorAll('.candidate-status-btn');
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfMeta ? csrfMeta.content : '';
  
  statusButtons.forEach(button => {
    button.addEventListener('click', async function() {
      const submissionId = this.getAttribute('data-submission-id');
      const newStatus = this.getAttribute('data-status');
      
      if (!submissionId || !newStatus) return;
      
      // Disable button during request
      this.disabled = true;
      const originalText = this.innerHTML;
      this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Updating...';
      
      try {
        const response = await fetch(`/recruiter/candidate/${submissionId}/status`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          credentials: 'same-origin',
          body: JSON.stringify({ status: newStatus })
        });

        let data;
        try {
          data = await response.json();
        } catch {
          throw new Error('Session/security token expired — please refresh the page');
        }

        if (!response.ok) {
          throw new Error(data.error || 'Failed to update status');
        }

        if (data.success) {
          // Show success message
          const alert = document.createElement('div');
          alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
          alert.style.zIndex = '9999';
          alert.innerHTML = `
            <i class="bi bi-check-circle me-2"></i>Candidate status updated to ${data.status}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          `;
          document.body.appendChild(alert);
          
          // Reload page after 1 second to show updated status
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        } else {
          throw new Error(data.error || 'Failed to update status');
        }
      } catch (error) {
        console.error('Error updating candidate status:', error);
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
          <i class="bi bi-exclamation-triangle me-2"></i>Failed to update status: ${error.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        // Re-enable button
        this.disabled = false;
        this.innerHTML = originalText;
      }
    });
  });
}

// ============================================
// Export Functions for Global Use
// ============================================

window.setupDragAndDrop = setupDragAndDrop;
window.renderBarChart = renderBarChart;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.setup3DCardTilt = setup3DCardTilt;
window.createStarField = createStarField;
