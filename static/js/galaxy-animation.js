/**
 * 3D Galaxy Animation System
 * Creates a cinematic, futuristic galaxy-style background animation
 * with stars, particles, depth layers, and cursor-responsive parallax
 */

class GalaxyAnimation {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    
    this.ctx = this.canvas.getContext('2d');
    // Find container - prefer parent, fallback to body
    this.container = this.canvas.parentElement;
    if (!this.container || this.container === document.body) {
      this.container = document.body;
    }
    
    // Configuration
    this.config = {
      intensity: options.intensity || 'full', // 'full', 'light', 'minimal'
      numStars: options.numStars || 300,
      numParticles: options.numParticles || 50,
      parallaxStrength: options.parallaxStrength || 0.3,
      animationSpeed: options.animationSpeed || 0.5,
      enableParallax: options.enableParallax !== false,
      ...options
    };
    
    // State
    this.stars = [];
    this.particles = [];
    this.mouseX = 0;
    this.mouseY = 0;
    this.targetMouseX = 0;
    this.targetMouseY = 0;
    this.animationId = null;
    this.isAnimating = false;
    this.theme = 'light';
    
    // Performance monitoring
    this.frameCount = 0;
    this.lastFpsCheck = performance.now();
    this.fps = 60;
    
    this.init();
  }
  
  init() {
    // Check for reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      this.config.intensity = 'minimal';
      this.config.animationSpeed = 0.1;
    }
    
    // Detect device performance
    this.detectPerformance();
    
    // Setup canvas
    this.setupCanvas();
    
    // Create stars and particles
    this.createStars();
    this.createParticles();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Get initial theme
    this.updateTheme();
    
    // Start animation
    this.start();
  }
  
  detectPerformance() {
    // Detect low-end devices
    const hardwareConcurrency = navigator.hardwareConcurrency || 4;
    const deviceMemory = navigator.deviceMemory || 4;
    
    if (hardwareConcurrency < 4 || deviceMemory < 4) {
      this.config.numStars = Math.floor(this.config.numStars * 0.6);
      this.config.numParticles = Math.floor(this.config.numParticles * 0.5);
      this.config.intensity = 'light';
    }
    
    // Check for mobile devices
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
      this.config.numStars = Math.floor(this.config.numStars * 0.5);
      this.config.numParticles = Math.floor(this.config.numParticles * 0.3);
      this.config.parallaxStrength = 0.1;
      this.config.intensity = 'light';
    }
  }
  
  setupCanvas() {
    const resizeCanvas = () => {
      const rect = this.container.getBoundingClientRect();
      this.canvas.width = rect.width;
      this.canvas.height = rect.height;
      this.width = this.canvas.width;
      this.height = this.canvas.height;
      this.centerX = this.width / 2;
      this.centerY = this.height / 2;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Set canvas styles
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.pointerEvents = 'none';
    this.canvas.style.zIndex = '0';
  }
  
  createStars() {
    this.stars = [];
    const depthLayers = 6; // More depth layers for better parallax effect
    
    for (let i = 0; i < this.config.numStars; i++) {
      const layer = Math.floor(Math.random() * depthLayers);
      const depth = 50 + layer * 180; // Depth ranges from 50 to 950 for smoother depth
      
      this.stars.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        z: depth,
        baseZ: depth,
        radius: Math.random() * 1.8 + 0.2, // Slightly larger range
        speed: (Math.random() * 0.25 + 0.08) * this.config.animationSpeed, // Slower, more cinematic
        opacity: Math.random() * 0.7 + 0.15,
        twinkle: Math.random() * Math.PI * 2, // For twinkling effect
        twinkleSpeed: Math.random() * 0.015 + 0.008, // Slower twinkle
        color: this.getStarColor(layer),
        trailLength: Math.random() * 3 + 1 // For motion trails
      });
    }
  }
  
  createParticles() {
    this.particles = [];
    
    for (let i = 0; i < this.config.numParticles; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        z: Math.random() * 900 + 150, // Extended depth range
        baseZ: Math.random() * 900 + 150,
        radius: Math.random() * 2.5 + 0.8,
        speed: (Math.random() * 0.35 + 0.15) * this.config.animationSpeed, // Slower motion
        opacity: Math.random() * 0.5 + 0.08,
        color: this.getParticleColor(),
        rotation: Math.random() * Math.PI * 2 // For subtle rotation
      });
    }
  }
  
  getStarColor(layer) {
    // Create subtle color variations based on depth - balanced for both themes
    const colors = [
      { r: 255, g: 255, b: 255 }, // Pure white (foreground stars)
      { r: 200, g: 220, b: 255 }, // Cool blue-white
      { r: 255, g: 245, b: 220 }, // Warm white (softer)
      { r: 230, g: 210, b: 255 }, // Purple-white (softer)
      { r: 255, g: 250, b: 240 }, // Soft warm white
      { r: 220, g: 240, b: 255 }  // Cool cyan-white
    ];
    return colors[layer % colors.length];
  }
  
  getParticleColor() {
    // Subtle colored particles - balanced for both themes
    const colors = [
      { r: 150, g: 180, b: 255, a: 0.25 }, // Soft blue
      { r: 255, g: 210, b: 160, a: 0.2 },  // Soft orange
      { r: 210, g: 160, b: 255, a: 0.18 }, // Soft purple
      { r: 160, g: 255, b: 220, a: 0.15 }, // Soft cyan
      { r: 255, g: 180, b: 200, a: 0.2 }  // Soft pink
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }
  
  setupEventListeners() {
    // Mouse movement for parallax
    if (this.config.enableParallax) {
      document.addEventListener('mousemove', (e) => {
        this.targetMouseX = (e.clientX / this.width - 0.5) * 2;
        this.targetMouseY = (e.clientY / this.height - 0.5) * 2;
      });
      
      document.addEventListener('mouseleave', () => {
        this.targetMouseX = 0;
        this.targetMouseY = 0;
      });
    }
    
    // Theme change detection
    const observer = new MutationObserver(() => {
      this.updateTheme();
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
    
    // Visibility change for performance
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pause();
      } else {
        this.start();
      }
    });
  }
  
  updateTheme() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    this.theme = theme;
  }
  
  getBackgroundColor() {
    if (this.theme === 'dark') {
      return { r: 8, g: 12, b: 20 }; // Deep space blue-black (not pure black)
    } else {
      return { r: 248, g: 250, b: 252 }; // Soft light background (not pure white)
    }
  }
  
  animate() {
    if (!this.isAnimating) return;
    
      // Smooth mouse interpolation - more responsive
    this.mouseX += (this.targetMouseX - this.mouseX) * 0.08;
    this.mouseY += (this.targetMouseY - this.mouseY) * 0.08;
    
    // Clear canvas with subtle background
    const bg = this.getBackgroundColor();
    this.ctx.fillStyle = `rgb(${bg.r}, ${bg.g}, ${bg.b})`;
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    // Update and draw particles (background layer)
    this.updateParticles();
    
    // Update and draw stars
    this.updateStars();
    
    // Performance monitoring
    this.monitorPerformance();
    
    this.animationId = requestAnimationFrame(() => this.animate());
  }
  
  updateStars() {
    const parallaxX = this.mouseX * this.config.parallaxStrength;
    const parallaxY = this.mouseY * this.config.parallaxStrength;
    
    this.stars.forEach(star => {
      // Move star forward
      star.z -= star.speed;
      
      // Reset if behind viewer
      if (star.z <= 0) {
        star.z = star.baseZ + 800;
        star.x = Math.random() * this.width;
        star.y = Math.random() * this.height;
      }
      
      // Calculate perspective projection
      const perspective = 500;
      const scale = perspective / (perspective + star.z);
      
      // Apply parallax based on depth - enhanced for better depth perception
      const parallaxFactor = (star.baseZ / 1000) * 0.6; // Increased parallax effect
      const offsetX = parallaxX * parallaxFactor * (1 + star.baseZ / 2000);
      const offsetY = parallaxY * parallaxFactor * (1 + star.baseZ / 2000);
      
      const x = (star.x - this.centerX + offsetX) * scale + this.centerX;
      const y = (star.y - this.centerY + offsetY) * scale + this.centerY;
      const radius = star.radius * scale;
      
      // Calculate opacity with twinkling - enhanced effect
      star.twinkle += star.twinkleSpeed;
      const twinkle = Math.sin(star.twinkle) * 0.25 + 0.75; // More pronounced twinkle
      let opacity = star.opacity * scale * twinkle;
      
      // Adjust opacity based on theme - balanced for readability
      if (this.theme === 'dark') {
        opacity = Math.min(opacity * 1.3, 0.95); // Brighter in dark mode
      } else {
        opacity = Math.min(opacity * 0.35, 0.3); // Subtle in light mode
      }
      
      // Draw star
      this.ctx.beginPath();
      this.ctx.arc(x, y, radius, 0, Math.PI * 2);
      
      const color = star.color;
      this.ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity})`;
      this.ctx.fill();
      
      // Add glow for larger stars in dark mode - enhanced
      if (this.theme === 'dark' && radius > 0.7) {
        const glowSize = radius * 1.5;
        const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, glowSize);
        gradient.addColorStop(0, `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity})`);
        gradient.addColorStop(0.5, `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity * 0.4})`);
        gradient.addColorStop(1, `rgba(${color.r}, ${color.g}, ${color.b}, 0)`);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        // Reset to original fill style
        this.ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity})`;
      }
    });
  }
  
  updateParticles() {
    const parallaxX = this.mouseX * this.config.parallaxStrength * 0.5;
    const parallaxY = this.mouseY * this.config.parallaxStrength * 0.5;
    
    this.particles.forEach(particle => {
      // Move particle
      particle.z -= particle.speed;
      
      // Reset if behind viewer
      if (particle.z <= 0) {
        particle.z = particle.baseZ + 600;
        particle.x = Math.random() * this.width;
        particle.y = Math.random() * this.height;
      }
      
      // Calculate perspective
      const perspective = 500;
      const scale = perspective / (perspective + particle.z);
      
      // Apply parallax - enhanced for particles
      const parallaxFactor = (particle.baseZ / 1000) * 0.4;
      const offsetX = parallaxX * parallaxFactor * (1 + particle.baseZ / 1500);
      const offsetY = parallaxY * parallaxFactor * (1 + particle.baseZ / 1500);
      
      const x = (particle.x - this.centerX + offsetX) * scale + this.centerX;
      const y = (particle.y - this.centerY + offsetY) * scale + this.centerY;
      const radius = particle.radius * scale;
      
      // Calculate opacity - balanced for both themes
      let opacity = particle.opacity * scale;
      if (this.theme === 'dark') {
        opacity = Math.min(opacity * 1.6, 0.45); // Slightly more visible in dark mode
      } else {
        opacity = Math.min(opacity * 0.25, 0.18); // Subtle in light mode
      }
      
      // Draw particle
      this.ctx.beginPath();
      this.ctx.arc(x, y, radius, 0, Math.PI * 2);
      
      const color = particle.color;
      this.ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity * color.a})`;
      this.ctx.fill();
    });
  }
  
  monitorPerformance() {
    this.frameCount++;
    const now = performance.now();
    
    if (now - this.lastFpsCheck > 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.lastFpsCheck = now;
      
      // Reduce quality if FPS drops
      if (this.fps < 30 && this.config.intensity === 'full') {
        this.config.intensity = 'light';
        this.config.numStars = Math.floor(this.config.numStars * 0.7);
        this.config.numParticles = Math.floor(this.config.numParticles * 0.7);
      }
    }
  }
  
  start() {
    if (this.isAnimating) return;
    this.isAnimating = true;
    this.animate();
  }
  
  pause() {
    this.isAnimating = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }
  
  destroy() {
    this.pause();
    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    }
  }
}

// Initialize galaxy animation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Small delay to ensure DOM is fully ready
  setTimeout(() => {
    // Initialize for landing page - full intensity galaxy
    const landingCanvas = document.getElementById('galaxyAnimation');
    if (landingCanvas) {
      window.galaxyAnimation = new GalaxyAnimation('galaxyAnimation', {
        intensity: 'full',
        numStars: 400, // Increased for richer effect
        numParticles: 70, // More particles for depth
        parallaxStrength: 0.45, // Strong parallax for landing page
        animationSpeed: 0.4 // Slower, more cinematic
      });
    }
    
    // Initialize for login page - lighter, refined version
    const loginCanvas = document.getElementById('starField');
    if (loginCanvas) {
      // Remove old star field if exists
      if (window.starFieldAnimation) {
        window.starFieldAnimation.destroy();
      }
      
      window.loginGalaxyAnimation = new GalaxyAnimation('starField', {
        intensity: 'light',
        numStars: 280, // Lighter than landing but still rich
        numParticles: 45, // Fewer particles for subtlety
        parallaxStrength: 0.3, // Moderate parallax
        animationSpeed: 0.35 // Slightly slower for continuity
      });
    }
  }, 100);
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
  if (window.galaxyAnimation) {
    window.galaxyAnimation.destroy();
  }
  if (window.loginGalaxyAnimation) {
    window.loginGalaxyAnimation.destroy();
  }
});

// Export for manual initialization
window.GalaxyAnimation = GalaxyAnimation;

