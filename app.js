/* CarBrandsAI — app.js */
/* Küresel durum */
const state = {
  file: null,
  img: new Image(),
  imgURL: null,
  result: null,
  demoMode: false, // Gerçek AI aktif!
  apiUrl: 'http://localhost:5000', // Backend URL - Updated
  intensity: 0.8,
  particlesEnabled: true,
  glitchEnabled: true,
  scanlineEnabled: true,
};

/* Yardımcılar */
const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const clamp = (v,min,max)=>Math.max(min,Math.min(max,v));

/* DOM referansları */
const yearEl = $('#year');
const introEl = $('#intro');
const skipIntroBtn = $('#skipIntro');
const openSettingsBtn = $('#openSettings');
const settingsEl = $('#settings');
const closeSettingsBtn = $('#closeSettings');
const intensityRange = $('#intensity');
const toggleParticles = $('#toggleParticles');
const toggleGlitch = $('#toggleGlitch');
const toggleScanline = $('#toggleScanline');

const dropZone = $('#dropZone');
const fileInput = $('#fileInput');
const preview = dropZone.querySelector('.preview');
const previewImg = $('#previewImg');
const overlay = $('#overlay');
const scanline = dropZone.querySelector('.scanline');
const monkey = dropZone.querySelector('.monkey');

const analyzeBtn = $('#analyzeBtn');
const viewBtn = $('#viewBtn');
const saveBtn = $('#saveBtn');
const copyJsonBtn = $('#copyJsonBtn');
const clearBtn = $('#clearBtn');

// Modal elements
const imageModal = $('#imageModal');
const modalClose = $('#modalClose');
const modalImage = $('#modalImage');
const modalOverlay = $('#modalOverlay');
const modalBrandName = $('#modalBrandName');
const modalConfidence = $('#modalConfidence');
const modalLatency = $('#modalLatency');
const zoomIn = $('#zoomIn');
const zoomOut = $('#zoomOut');
const resetZoom = $('#resetZoom');

const results = $('#results');
const brandName = $('#brandName');
const confidenceEl = $('#confidence');
const tagsEl = $('#tags');
const latencyEl = $('#latency');

const demoBtn = $('#demoBtn');

/* Başlangıç */
yearEl.textContent = new Date().getFullYear();

/* Intro */
const hideIntro = () => {
  console.log('🚀 Intro gizleniyor...');
  if (introEl) {
    introEl.style.opacity = '0';
    introEl.style.pointerEvents = 'none';
    setTimeout(() => {
      introEl.style.display = 'none';
    }, 500);
  }
};

// Güvenli event listener
document.addEventListener('DOMContentLoaded', () => {
  if (skipIntroBtn) {
    skipIntroBtn.addEventListener('click', hideIntro);
    console.log('✅ Skip intro button ready');
  }
});

// Auto hide intro
setTimeout(hideIntro, 3000);

/* Ayarlar paneli */
openSettingsBtn.addEventListener('click', ()=> settingsEl.classList.remove('hidden'));
closeSettingsBtn.addEventListener('click', ()=> settingsEl.classList.add('hidden'));
settingsEl.addEventListener('click', (e)=>{ if(e.target === settingsEl) settingsEl.classList.add('hidden') });

intensityRange.addEventListener('input', e=>{
  state.intensity = e.target.value/100;
  setParticleDensity(state.intensity);
});
toggleParticles.addEventListener('change', e=>{
  state.particlesEnabled = e.target.checked; bg.toggleParticles(state.particlesEnabled);
});
toggleGlitch.addEventListener('change', e=>{
  state.glitchEnabled = e.target.checked;
  document.querySelectorAll('.glitch').forEach(el=> el.style.animationPlayState = state.glitchEnabled ? 'running':'paused');
});
toggleScanline.addEventListener('change', e=>{
  state.scanlineEnabled = e.target.checked;
  scanline.classList.toggle('off', !state.scanlineEnabled);
});

/* Dropzone & dosya okuma */
const activatePreview = () => {
  preview.classList.remove('hidden');
  dropZone.classList.add('has-image'); // Büyük önizleme için
  analyzeBtn.disabled = false;
  viewBtn.disabled = true; // Henüz analiz yapılmadı
  saveBtn.disabled = true;
  copyJsonBtn.disabled = true;
  results.classList.add('hidden');
};

const clearAll = () => {
  state.file = null;
  state.result = null;
  if(state.imgURL){ URL.revokeObjectURL(state.imgURL); state.imgURL = null; }
  previewImg.src = '';
  preview.classList.add('hidden');
  dropZone.classList.remove('has-image', 'analyzing'); // Büyük önizlemeyi kaldır
  overlay.getContext('2d').clearRect(0,0,overlay.width, overlay.height);
  analyzeBtn.disabled = true;
  viewBtn.disabled = true;
  saveBtn.disabled = true;
  copyJsonBtn.disabled = true;
  results.classList.add('hidden');
};
clearBtn.addEventListener('click', clearAll);

function handleFiles(files){
  console.log('📁 Files received:', files);
  const f = files && files[0];
  if(!f) {
    console.log('❌ No file selected');
    return;
  }
  
  if(!/^image\//.test(f.type)){
    alert('🖼️ Lütfen bir görsel dosyası seçin (JPG, PNG, WEBP)');
    return;
  }
  
  console.log('✅ Valid image file:', f.name);
  state.file = f;
  
  if(state.imgURL) {
    URL.revokeObjectURL(state.imgURL);
  }
  
  state.imgURL = URL.createObjectURL(f);
  state.img.onload = ()=>{
    console.log('🖼️ Image loaded successfully');
    previewImg.src = state.imgURL;
    fitOverlayCanvas();
    activatePreview();
  };
  state.img.onerror = () => {
    console.error('❌ Image load failed');
    alert('Görsel yüklenemedi!');
  };
  state.img.src = state.imgURL;
}

fileInput.addEventListener('change', e => handleFiles(e.target.files));

// Drag & drop
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag');
  handleFiles(e.dataTransfer.files);
});

// Click to upload
dropZone.addEventListener('click', (e) => {
  // Sadece dropzone'a tıklandığında, preview'daki elemanlara değil
  if (e.target === dropZone || e.target.classList.contains('dz-inner') || e.target.classList.contains('dz-icon') || e.target.classList.contains('dz-text')) {
    fileInput.click();
  }
});

// Canvas fitleme
function fitOverlayCanvas() {
  const rect = previewImg.getBoundingClientRect();
  overlay.width = rect.width;
  overlay.height = rect.height;
  overlay.style.width = rect.width + 'px';
  overlay.style.height = rect.height + 'px';
}

// Gerçek AI analizi
async function runAnalysis() {
  if (!state.file) return;
  
  dropZone.classList.add('analyzing');
  analyzeBtn.disabled = true;
  
  try {
    const start = performance.now();
    
    // FormData ile dosya gönder
    const formData = new FormData();
    formData.append('image', state.file);
    
    console.log('🔄 Sending image to AI backend...');
    
    // API çağrısı
    const response = await fetch(`${state.apiUrl}/api/detect`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    const end = performance.now();
    
    console.log('✅ AI Response:', result);
    
    // Sonucu işle
    if (result.error) {
      throw new Error(result.error);
    }
    
    state.result = {
      brand: result.brand,
      confidence: result.confidence,
      latency: result.latency || `${Math.round(end - start)}ms`,
      box: result.box || { x: 50, y: 50, w: 200, h: 150 },
      model_info: result.model_info
    };
    
    displayResults();
    drawBoundingBox();
    
  } catch (error) {
    console.error('❌ Analysis failed:', error);
    
    // Hata durumunda fallback
    state.result = {
      brand: 'Error',
      confidence: 0.0,
      latency: '0ms',
      box: { x: 0, y: 0, w: 0, h: 0 },
      error: error.message
    };
    
    displayResults();
    
    // Kullanıcıya hata mesajı göster
    alert(`AI Analizi başarısız: ${error.message}\n\nLütfen backend sunucusunun çalıştığından emin olun.`);
  }
  
  dropZone.classList.remove('analyzing');
  analyzeBtn.disabled = false;
  viewBtn.disabled = false; // Analiz tamamlandı, tam ekran görüntüleme aktif
  saveBtn.disabled = false;
  copyJsonBtn.disabled = false;
}

// Demo simülasyonu (fallback)
async function runDemo() {
  if (!state.file) return;
  
  dropZone.classList.add('analyzing');
  analyzeBtn.disabled = true;
  
  // Fake loading simulation
  const brands = ['BMW', 'Mercedes', 'Toyota', 'Audi', 'Tesla', 'Honda', 'Ford'];
  const randomBrand = brands[Math.floor(Math.random() * brands.length)];
  const confidence = 0.85 + Math.random() * 0.12;
  
  const start = performance.now();
  await sleep(800 + Math.random() * 400); // Random delay
  const end = performance.now();
  
  // Show results
  state.result = {
    brand: randomBrand,
    confidence: confidence,
    latency: Math.round(end - start) + 'ms',
    box: { x: 50, y: 50, w: 200, h: 150 }
  };
  
  displayResults();
  drawBoundingBox();
  
  dropZone.classList.remove('analyzing');
  analyzeBtn.disabled = false;
  viewBtn.disabled = false; // Demo da tamamlandı
  saveBtn.disabled = false;
  copyJsonBtn.disabled = false;
}

// Analiz butonu - gerçek AI
analyzeBtn.addEventListener('click', () => {
  console.log('🔬 Analysis started');
  if (state.demoMode) {
    runDemo();
  } else {
    runAnalysis(); // Gerçek AI çağrısı
  }
});

// Demo button
demoBtn.addEventListener('click', async () => {
  // Load a demo image
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 300;
  const ctx = canvas.getContext('2d');
  
  // Draw demo car logo
  ctx.fillStyle = '#1e40af';
  ctx.fillRect(0, 0, 400, 300);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 48px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('BMW', 200, 160);
  
  canvas.toBlob(blob => {
    state.file = new File([blob], 'demo.png', { type: 'image/png' });
    handleFiles([state.file]);
  });
});

// Results display
function displayResults() {
  if (!state.result) return;
  
  brandName.textContent = state.result.brand;
  confidenceEl.textContent = Math.round(state.result.confidence * 100) + '%';
  latencyEl.textContent = state.result.latency;
  
  // Add some demo tags
  tagsEl.innerHTML = `
    <span class="tag">Luxury</span>
    <span class="tag">German</span>
    <span class="tag">Sedan</span>
  `;
  
  results.classList.remove('hidden');
}

// Bounding box çizimi
function drawBoundingBox() {
  if (!state.result || !state.result.box) return;
  
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);
  
  const { x, y, w, h } = state.result.box;
  
  // 🔍 FRONTEND DEBUG
  console.log('🖥️ FRONTEND DEBUG:');
  console.log(`   Backend sent: x=${x}, y=${y}, w=${w}, h=${h}`);
  console.log(`   Image natural: ${state.img.naturalWidth}x${state.img.naturalHeight}`);
  console.log(`   Canvas size: ${overlay.width}x${overlay.height}`);
  console.log(`   Preview img display: ${previewImg.clientWidth}x${previewImg.clientHeight}`);
  
  // Scale to overlay size
  const scaleX = overlay.width / state.img.naturalWidth;
  const scaleY = overlay.height / state.img.naturalHeight;
  
  const scaledX = x * scaleX;
  const scaledY = y * scaleY;
  const scaledW = w * scaleX;
  const scaledH = h * scaleY;
  
  console.log(`   Scale factors: scaleX=${scaleX.toFixed(3)}, scaleY=${scaleY.toFixed(3)}`);
  console.log(`   Final scaled: x=${scaledX.toFixed(1)}, y=${scaledY.toFixed(1)}, w=${scaledW.toFixed(1)}, h=${scaledH.toFixed(1)}`);
  
  // Draw bounding box
  ctx.strokeStyle = '#ff4fd8';
  ctx.lineWidth = 3;
  ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
  
  // Draw label
  ctx.fillStyle = 'rgba(255, 79, 216, 0.8)';
  ctx.fillRect(scaledX, scaledY - 30, scaledW, 30);
  ctx.fillStyle = '#000';
  ctx.font = 'bold 16px Arial';
  ctx.fillText(state.result.brand, scaledX + 10, scaledY - 8);
}

// Save & Copy functions
saveBtn.addEventListener('click', () => {
  if (!state.result) return;
  
  const canvas = document.createElement('canvas');
  canvas.width = state.img.naturalWidth;
  canvas.height = state.img.naturalHeight;
  const ctx = canvas.getContext('2d');
  
  ctx.drawImage(state.img, 0, 0);
  
  // Draw bounding box on full resolution
  const { x, y, w, h } = state.result.box;
  ctx.strokeStyle = '#ff4fd8';
  ctx.lineWidth = 6;
  ctx.strokeRect(x, y, w, h);
  
  ctx.fillStyle = 'rgba(255, 79, 216, 0.8)';
  ctx.fillRect(x, y - 60, w, 60);
  ctx.fillStyle = '#000';
  ctx.font = 'bold 32px Arial';
  ctx.fillText(state.result.brand, x + 20, y - 16);
  
  // Download
  canvas.toBlob(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.result.brand}_detected.png`;
    a.click();
    URL.revokeObjectURL(url);
  });
});

copyJsonBtn.addEventListener('click', () => {
  if (!state.result) return;
  
  const json = JSON.stringify(state.result, null, 2);
  navigator.clipboard.writeText(json).then(() => {
    copyJsonBtn.textContent = 'Kopyalandı!';
    setTimeout(() => {
      copyJsonBtn.textContent = 'JSON\'u Kopyala';
    }, 2000);
  });
});

// Background canvas setup
const bgCanvas = $('#bg');
const bgCtx = bgCanvas.getContext('2d');
let particles = [];
let animationId;

function resizeCanvas() {
  bgCanvas.width = window.innerWidth;
  bgCanvas.height = window.innerHeight;
}

function createParticles() {
  particles = [];
  const count = Math.floor((bgCanvas.width * bgCanvas.height) / 15000 * state.intensity);
  
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * bgCanvas.width,
      y: Math.random() * bgCanvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.3 + 0.1
    });
  }
}

function animateParticles() {
  if (!state.particlesEnabled) {
    animationId = requestAnimationFrame(animateParticles);
    return;
  }
  
  bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
  
  // Draw grid
  bgCtx.strokeStyle = `rgba(79, 211, 255, ${0.03 * state.intensity})`;
  bgCtx.lineWidth = 1;
  
  const gridSize = 50;
  for (let x = 0; x < bgCanvas.width; x += gridSize) {
    bgCtx.beginPath();
    bgCtx.moveTo(x, 0);
    bgCtx.lineTo(x, bgCanvas.height);
    bgCtx.stroke();
  }
  
  for (let y = 0; y < bgCanvas.height; y += gridSize) {
    bgCtx.beginPath();
    bgCtx.moveTo(0, y);
    bgCtx.lineTo(bgCanvas.width, y);
    bgCtx.stroke();
  }
  
  // Draw particles with connections
  particles.forEach((p, index) => {
    p.x += p.vx;
    p.y += p.vy;
    
    if (p.x < 0 || p.x > bgCanvas.width) p.vx *= -1;
    if (p.y < 0 || p.y > bgCanvas.height) p.vy *= -1;
    
    // Draw particle
    bgCtx.beginPath();
    bgCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    bgCtx.fillStyle = `rgba(79, 211, 255, ${p.opacity * state.intensity})`;
    bgCtx.fill();
    
    // Draw connections to nearby particles
    particles.slice(index + 1).forEach(p2 => {
      const dx = p.x - p2.x;
      const dy = p.y - p2.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 150) {
        bgCtx.beginPath();
        bgCtx.moveTo(p.x, p.y);
        bgCtx.lineTo(p2.x, p2.y);
        const opacity = (1 - distance / 150) * 0.4 * state.intensity;
        bgCtx.strokeStyle = `rgba(79, 211, 255, ${opacity})`;
        bgCtx.lineWidth = 1.5;
        bgCtx.stroke();
      }
    });
  });
  
  animationId = requestAnimationFrame(animateParticles);
}

function setParticleDensity(intensity) {
  state.intensity = intensity;
  createParticles();
}

const bg = {
  toggleParticles: (enabled) => {
    state.particlesEnabled = enabled;
    if (!enabled) {
      bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
    }
  }
};

// Initialize
window.addEventListener('resize', () => {
  resizeCanvas();
  createParticles();
});

resizeCanvas();
createParticles();
animateParticles();

// MEGA Interactive Features
let mouseX = 0, mouseY = 0;
let isMouseMoving = false;

// Mouse tracking for interactive effects (no particles)
document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  isMouseMoving = true;
  
  setTimeout(() => { isMouseMoving = false; }, 100);
});

// Scroll-triggered animations
function setupScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        
        // Add stagger effect for cards
        if (entry.target.classList.contains('card')) {
          const cards = Array.from(document.querySelectorAll('.card'));
          const index = cards.indexOf(entry.target);
          entry.target.style.animationDelay = `${index * 0.1}s`;
        }
      }
    });
  }, observerOptions);
  
  // Add reveal class to elements
  const elementsToReveal = document.querySelectorAll('.card, .stat, .features h2, .faq h2');
  elementsToReveal.forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });
}

// Enhanced button effects with sound (optional)
function addButtonSoundEffects() {
  const buttons = document.querySelectorAll('.btn');
  
  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      // Add subtle vibration effect
      if (navigator.vibrate) {
        navigator.vibrate(10);
      }
      
      // Add scale pulse
      btn.style.transform = 'translateY(-3px) scale(1.02)';
    });
    
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
    
    btn.addEventListener('click', () => {
      // Add click feedback
      btn.style.transform = 'translateY(-1px) scale(0.98)';
      setTimeout(() => {
        btn.style.transform = 'translateY(-3px) scale(1.02)';
      }, 100);
    });
  });
}

// Enhanced dropzone with interactive effects
function enhanceDropzone() {
  let pulseInterval;
  
  dropZone.addEventListener('mouseenter', () => {
    dropZone.style.transform = 'scale(1.01)';
    
    // Start subtle pulse
    clearInterval(pulseInterval);
    pulseInterval = setInterval(() => {
      const currentColor = dropZone.style.borderColor;
      dropZone.style.borderColor = currentColor === 'rgb(255, 79, 216)'
        ? 'rgba(79, 211, 255, 0.35)'
        : 'rgb(255, 79, 216)';
    }, 800);
  });
  
  dropZone.addEventListener('mouseleave', () => {
    dropZone.style.transform = '';
    clearInterval(pulseInterval);
    dropZone.style.borderColor = '';
  });
}

// Initialize comfortable enhancements
function initializeEnhancements() {
  console.log('🌟 Loading user-friendly enhancements...');
  
  setupScrollAnimations();
  addButtonSoundEffects();
  enhanceDropzone();
  
  // Use standard particle animation (not enhanced version)
  // Enhanced version was too intense
  
  console.log('✨ Comfortable enhancements activated:');
  console.log('  📊 Scroll-triggered animations');
  console.log('  🎮 Button effects');
  console.log('  🖼️ Enhanced dropzone');
}

// FAQ functionality
function initFAQ() {
  const faqItems = document.querySelectorAll('.faq-item');
  
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    
    if (question && answer) {
      question.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');
        
        // Close all other FAQ items
        faqItems.forEach(otherItem => {
          otherItem.classList.remove('open');
        });
        
        // Toggle current item
        if (!isOpen) {
          item.classList.add('open');
        }
      });
    }
  });
  
  console.log('✅ FAQ functionality ready');
}

// Navigation scroll functionality
function initSmoothScroll() {
  const navLinks = document.querySelectorAll('nav a[href^="#"]');
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetEl = document.getElementById(targetId);
      
      if (targetEl) {
        targetEl.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  console.log('✅ Smooth scroll ready');
}

// Start enhancements after a short delay
setTimeout(() => {
  initializeEnhancements();
  initFAQ();
  initSmoothScroll();
}, 100);

console.log('🚀 CarBrandsAI initialized with comfortable animations!');
// Modal functionality
let modalZoom = 1;
let modalPanX = 0;
let modalPanY = 0;

function openImageModal() {
  if (!state.result || !state.imgURL) return;
  
  console.log('🔍 Opening current analyzed image with bounding box...');
  
  // Şu anki analiz edilmiş görseli + bounding box'ı birleştir
  const combinedCanvas = document.createElement('canvas');
  const ctx = combinedCanvas.getContext('2d');
  
  // Canvas boyutunu natural image boyutuna göre ayarla (yüksek kalite için)
  combinedCanvas.width = state.img.naturalWidth;
  combinedCanvas.height = state.img.naturalHeight;
  
  // Önce orijinal görseli tam boyutunda çiz
  ctx.drawImage(state.img, 0, 0, state.img.naturalWidth, state.img.naturalHeight);
  
  // Sonra bounding box'ı tam boyutunda çiz (backend'den gelen koordinatlarla)
  if (state.result && state.result.box) {
    const { x, y, w, h } = state.result.box;
    
    // Bounding box çiz
    ctx.strokeStyle = '#ff4fd8';
    ctx.lineWidth = 8; // Büyük görsel için daha kalın çizgi
    ctx.strokeRect(x, y, w, h);
    
    // Label background
    ctx.fillStyle = 'rgba(255, 79, 216, 0.9)';
    const labelHeight = 80;
    ctx.fillRect(x, y - labelHeight, Math.max(w, 300), labelHeight);
    
    // Brand text
    ctx.fillStyle = '#000';
    ctx.font = 'bold 48px Arial';
    ctx.fillText(state.result.brand, x + 20, y - 40);
    
    // Confidence text
    ctx.font = '32px Arial';
    ctx.fillText(`${Math.round(state.result.confidence * 100)}%`, x + 20, y - 10);
  }
  
  // Birleştirilmiş görseli modal'da göster
  modalImage.src = combinedCanvas.toDataURL();
  modalImage.onload = () => {
    modalZoom = 1;
    modalPanX = 0;
    modalPanY = 0;
    
    modalBrandName.textContent = state.result.brand;
    modalConfidence.textContent = Math.round(state.result.confidence * 100) + '%';
    modalLatency.textContent = state.result.latency;
  };
  
  imageModal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeImageModal() {
  console.log('❌ Closing image viewer...');
  imageModal.classList.remove('active');
  document.body.style.overflow = ''; // Restore scroll
}

function setupModalCanvas() {
  // Wait for image to be loaded and displayed
  setTimeout(() => {
    const imageRect = modalImage.getBoundingClientRect();
    
    // Set canvas to exact same size as displayed image
    modalOverlay.width = Math.round(imageRect.width);
    modalOverlay.height = Math.round(imageRect.height);
    
    console.log('🖼️ Modal Canvas SIMPLE v4:', {
      imageNatural: { w: state.img.naturalWidth, h: state.img.naturalHeight },
      imageDisplay: { w: imageRect.width, h: imageRect.height },
      canvasSize: { w: modalOverlay.width, h: modalOverlay.height },
      approach: 'Same as main preview'
    });
    
    // Redraw bounding box after canvas is properly sized
    drawModalBoundingBox();
  }, 100);
}

// BOKTAN MODALBOUNDİNG BOX KALDIRILDİ - YOLO ZATENPEeRFECT!
// drawModalBoundingBox() - ARTIK GEREKSİZ, YOLO VALİDATİON SONUÇLARI PERFECT!

function zoomModal(factor) {
  modalZoom = Math.max(0.5, Math.min(5, modalZoom * factor));
  modalImage.style.transform = `scale(${modalZoom}) translate(${modalPanX}px, ${modalPanY}px)`;
  modalOverlay.style.transform = `scale(${modalZoom}) translate(${modalPanX}px, ${modalPanY}px)`;
}

function resetModalZoom() {
  modalZoom = 1;
  modalPanX = 0;
  modalPanY = 0;
  modalImage.style.transform = '';
  modalOverlay.style.transform = '';
}

// Modal event listeners
viewBtn.addEventListener('click', openImageModal);
modalClose.addEventListener('click', closeImageModal);
zoomIn.addEventListener('click', () => zoomModal(1.2));
zoomOut.addEventListener('click', () => zoomModal(0.8));
resetZoom.addEventListener('click', resetModalZoom);

// Close modal on background click
imageModal.addEventListener('click', (e) => {
  if (e.target === imageModal) closeImageModal();
});

// Close modal with ESC key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && imageModal.classList.contains('active')) {
    closeImageModal();
  }
});

// Click on preview image to open modal
preview.addEventListener('click', (e) => {
  if (state.result && (e.target === previewImg || e.target === overlay)) {
    openImageModal();
  }
});

console.log('🖼️ Image modal functionality ready!');
