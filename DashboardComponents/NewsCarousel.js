class NewsCarousel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.currentIndex = 0;
    this.isAutoPlaying = true;
    this.autoPlayTimer = null;
  }

  async connectedCallback() {
    try {
      // Create inline styles for immediate rendering
      const style = document.createElement("style");
      style.textContent = this.getInlineStyles();

      // Enhanced news data with more realistic content
      const newsData = await this.fetchNewsData();
      
      this.render(style, newsData);
      this.setupEventListeners(newsData.length);
      this.startAutoPlay();
      
    } catch (error) {
      console.error('Failed to initialize NewsCarousel:', error);
      this.renderError();
    }
  }

  getInlineStyles() {
    return `
      .container {
        position: relative;
        width: 100%;
        max-width: 1200px;
        margin: 2rem auto;
        background: rgba(15, 23, 42, 0.9);
        border-radius: 1.5rem;
        overflow: hidden;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        min-height: 140px;
      }
      
      .slides {
        display: block;
      }

      
      .slide {
        display: none; /* All hidden by default */
        width: 100%;
        box-sizing: border-box;
        padding: 1.5rem 2rem;
        color: #f8fafc;
        font-size: 1.125rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 1rem;
        min-height: 120px;
      }

      .slide.active {
        display: block;
      }
      
      .news-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        max-width: 900px;
      }
      
      .news-category {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      
      .news-item a {
        color: #f8fafc;
        text-decoration: none;
        font-size: 1.125rem;
        font-weight: 600;
        line-height: 1.4;
        text-align: center;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        display: block;
        width: 100%;
        box-sizing: border-box;
      }
      
      .news-item a:hover {
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
        transform: translateY(-2px);
      }
      
      .news-date {
        font-size: 0.8rem;
        color: #94a3b8;
        font-style: italic;
      }
      
      .arrow {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        color: #f8fafc;
        background: rgba(16, 185, 129, 0.8);
        border: none;
        cursor: pointer;
        z-index: 1000;
        padding: 1rem;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
      }
      
      .arrow:hover {
        background: rgba(5, 150, 105, 1);
        transform: translateY(-50%) scale(1.1);
      }
      
      .arrow.left {
        left: 1.5rem;
      }
      
      .arrow.right {
        right: 1.5rem;
      }
      
      .dots {
        display: flex;
        justify-content: center;
        padding: 1rem 0;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.1);
      }
      
      .dot {
        height: 12px;
        width: 12px;
        background-color: rgba(148, 163, 184, 0.4);
        border-radius: 50%;
        cursor: pointer;
        transition: all 0.3s ease;
      }
      
      .dot.active {
        background-color: #10b981;
        transform: scale(1.3);
      }
      
      .dot:hover {
        background-color: #6ee7b7;
        transform: scale(1.2);
      }
    `;
  }

  async fetchNewsData() {
  const apiKey = "94fd1a42e0134935af8e546f7c896999"; // replace with your actual key
  const apiUrl = `https://newsapi.org/v2/everything?q=cancer%20drug&language=en&pageSize=5&sortBy=publishedAt&apiKey=${apiKey}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) throw new Error("Network response was not ok");
    const data = await response.json();

    return data.articles.map(article => ({
      title: article.title,
      link: article.url,
      category: article.source.name || "News",
      date: article.publishedAt
    }));
  } catch (error) {
    console.error("Error fetching news:", error);
    throw error;
  }
}


  render(style, newsData) {
    const container = document.createElement("div");
    container.className = "container";

    const slidesContainer = document.createElement("div");
    slidesContainer.className = "slides";
    slidesContainer.style.width = `${newsData.length * 100}%`;

    // Create slides with enhanced content
    slidesContainer.innerHTML = newsData.map((news, index) => `
      <div class="slide" data-index="${index}">
        <article class="news-item">
          <div class="news-category">${news.category}</div>
          <a href="${news.link}" target="_blank" rel="noopener noreferrer">
            ${news.title}
          </a>
          <div class="news-date">${this.formatDate(news.date)}</div>
        </article>
      </div>
    `).join("");

    // Create navigation dots
    const dotsContainer = document.createElement("div");
    dotsContainer.className = "dots";
    dotsContainer.innerHTML = newsData.map((_, i) => 
      `<span class="dot ${i === 0 ? 'active' : ''}" data-index="${i}" 
             aria-label="Go to slide ${i + 1}"></span>`
    ).join("");

    // Create navigation arrows
    const leftArrow = document.createElement("button");
    leftArrow.className = "arrow left";
    leftArrow.setAttribute('aria-label', 'Previous news item');
    leftArrow.textContent = "‹";

    const rightArrow = document.createElement("button");
    rightArrow.className = "arrow right";
    rightArrow.setAttribute('aria-label', 'Next news item');
    rightArrow.textContent = "›";

    // Create play/pause button
    const playPauseBtn = document.createElement("button");
    playPauseBtn.className = "play-pause-btn";
    playPauseBtn.setAttribute('aria-label', 'Pause auto-play');
    playPauseBtn.innerHTML = "⏸️";
    playPauseBtn.style.cssText = `
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba(0, 0, 0, 0.5);
      color: white;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      cursor: pointer;
      z-index: 1000;
      transition: all 0.3s ease;
    `;

    // Assemble the carousel
    container.append(leftArrow, slidesContainer, rightArrow, dotsContainer, playPauseBtn);
    
    // Add styles and content to shadow DOM
    this.shadowRoot.append(style, container);
    
    this.slidesElement = slidesContainer;
    this.dotsElement = dotsContainer;
    this.playPauseElement = playPauseBtn;
    this.totalSlides = newsData.length;

    console.log("Total slides:", this.totalSlides);
console.log("Actual .slide elements:", this.slidesElement.children.length);

  }

  renderError() {
    const style = document.createElement("style");
    style.textContent = `
      .error-container {
        padding: 2rem;
        text-align: center;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 1rem;
        color: #ef4444;
        margin: 1rem;
      }
    `;
    
    const errorContainer = document.createElement("div");
    errorContainer.className = "error-container";
    errorContainer.innerHTML = `
      <h3>⚠️ Unable to Load News</h3>
      <p>Please check your connection and try again.</p>
    `;
    
    this.shadowRoot.append(style, errorContainer);
  }

  setupEventListeners(totalSlides) {
    const leftArrow = this.shadowRoot.querySelector('.arrow.left');
    const rightArrow = this.shadowRoot.querySelector('.arrow.right');
    const dots = this.shadowRoot.querySelectorAll('.dot');

    // Arrow navigation
    leftArrow.addEventListener('click', () => {
      this.goToPrevious();
      this.resetAutoPlay();
    });

    rightArrow.addEventListener('click', () => {
      this.goToNext();
      this.resetAutoPlay();
    });

    // Dot navigation
    dots.forEach(dot => {
      dot.addEventListener('click', () => {
        const index = parseInt(dot.dataset.index);
        this.goToSlide(index);
        this.resetAutoPlay();
      });
    });

    // Play/pause button
    this.playPauseElement.addEventListener('click', () => {
      this.toggleAutoPlay();
    });

    // Keyboard navigation
    this.shadowRoot.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowLeft':
          this.goToPrevious();
          this.resetAutoPlay();
          break;
        case 'ArrowRight':
          this.goToNext();
          this.resetAutoPlay();
          break;
        case ' ':
          e.preventDefault();
          this.toggleAutoPlay();
          break;
      }
    });

    // Pause on hover
    const container = this.shadowRoot.querySelector('.container');
    container.addEventListener('mouseenter', () => this.pauseAutoPlay());
    container.addEventListener('mouseleave', () => this.resumeAutoPlay());

    // Touch/swipe support
    this.setupTouchEvents();
  }

  setupTouchEvents() {
    let startX = 0;
    let endX = 0;
    const container = this.shadowRoot.querySelector('.container');

    container.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });

    container.addEventListener('touchmove', (e) => {
      e.preventDefault(); // Prevent scrolling
    });

    container.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      const diffX = startX - endX;
      
      if (Math.abs(diffX) > 50) { // Minimum swipe distance
        if (diffX > 0) {
          this.goToNext();
        } else {
          this.goToPrevious();
        }
        this.resetAutoPlay();
      }
    });
  }

  goToNext() {
    this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
    this.updateCarousel();
  }

  goToPrevious() {
    this.currentIndex = (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
    this.updateCarousel();
  }

  goToSlide(index) {
    this.currentIndex = index;
    this.updateCarousel();
  }

  updateCarousel() {
  const slides = this.slidesElement.children;

  Array.from(slides).forEach((slide, index) => {
    slide.style.display = index === this.currentIndex ? "block" : "none";
  });

  this.shadowRoot.querySelectorAll('.dot').forEach((dot, index) => {
    dot.classList.toggle('active', index === this.currentIndex);
  });
}



  startAutoPlay() {
    if (this.autoPlayTimer) clearInterval(this.autoPlayTimer);
    this.autoPlayTimer = setInterval(() => {
      if (this.isAutoPlaying) {
        this.goToNext();
      }
    }, 10000);
  }

  pauseAutoPlay() {
    this.isAutoPlaying = false;
  }

  resumeAutoPlay() {
    this.isAutoPlaying = true;
  }

  resetAutoPlay() {
    this.startAutoPlay();
    this.isAutoPlaying = true;
    this.updatePlayPauseButton();
  }

  toggleAutoPlay() {
    this.isAutoPlaying = !this.isAutoPlaying;
    this.updatePlayPauseButton();
    
    if (this.isAutoPlaying) {
      this.startAutoPlay();
    }
  }

  updatePlayPauseButton() {
    if (this.playPauseElement) {
      this.playPauseElement.innerHTML = this.isAutoPlaying ? "⏸️" : "▶️";
      this.playPauseElement.setAttribute('aria-label', 
        this.isAutoPlaying ? 'Pause auto-play' : 'Resume auto-play'
      );
    }
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  }

  // Public API methods
  addNewsItem(newsItem) {
    // Method to dynamically add news items
    const slideHtml = `
      <div class="slide" data-index="${this.totalSlides}">
        <article class="news-item">
          <div class="news-category">${newsItem.category}</div>
          <a href="${newsItem.link}" target="_blank" rel="noopener noreferrer">
            ${newsItem.title}
          </a>
          <div class="news-date">${this.formatDate(newsItem.date)}</div>
        </article>
      </div>
    `;
    
    this.slidesElement.insertAdjacentHTML('beforeend', slideHtml);
    
    // Add corresponding dot
    const dotHtml = `<span class="dot" data-index="${this.totalSlides}" 
                           aria-label="Go to slide ${this.totalSlides + 1}"></span>`;
    this.dotsElement.insertAdjacentHTML('beforeend', dotHtml);
    
    this.totalSlides++;
    this.slidesElement.style.width = `${this.totalSlides * 100}%`;
    
    // Update event listeners for new dot
    const newDot = this.shadowRoot.querySelector(`[data-index="${this.totalSlides - 1}"]`);
    newDot.addEventListener('click', () => {
      this.goToSlide(this.totalSlides - 1);
      this.resetAutoPlay();
    });
  }

  disconnectedCallback() {
    // Clean up when component is removed
    if (this.autoPlayTimer) {
      clearInterval(this.autoPlayTimer);
    }
  }
}

// Add enhanced styles for news items
const enhancedStyles = document.createElement('style');
enhancedStyles.textContent = `
  .news-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    padding: 0 2rem;
    box-sizing: border-box;
  }
  
  .news-category {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
  }
  
  .news-item a {
    line-height: 1.4;
    text-align: center;
    word-wrap: break-word;
    max-width: 100%;
  }
  
  .news-date {
    font-size: 0.8rem;
    color: #94a3b8;
    font-style: italic;
    white-space: nowrap;
  }
  
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

// Add styles to document head if not already present
if (!document.querySelector('#news-carousel-enhanced-styles')) {
  enhancedStyles.id = 'news-carousel-enhanced-styles';
  document.head.appendChild(enhancedStyles);
}

customElements.define("news-carousel", NewsCarousel);
export default NewsCarousel;
