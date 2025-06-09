import "../DashboardComponents/NewsCarousel.js"; 
import "../DashboardComponents/CancerDrugRecommender.js"; 


class OncoSageDashboard extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Add CSS if not already present
    if (!document.querySelector('link[href="styles/variables.css"]')) {
      const variablesLink = document.createElement("link");
      variablesLink.rel = "stylesheet";
      variablesLink.href = "styles/variables.css";
      document.head.appendChild(variablesLink);
    }

    if (!document.querySelector('link[href="styles/OncoSageDashboard.css"]')) {
      const styleLink = document.createElement("link");
      styleLink.rel = "stylesheet";
      styleLink.href = "styles/OncoSageDashboard.css";
      document.head.appendChild(styleLink);
    }

    // Container setup
    const wrapper = document.createElement("div");
    wrapper.className = "dashboard-wrapper";

    // HTML for dashboard and tool screen
    wrapper.innerHTML = `
      <section id="main-dashboard" class="fade-in">
        <header class="dashboard-header">
          <h1>&#x1F9EC OncoSage</h1>
        </header>

        <!-- News Carousel Component -->
        <news-carousel></news-carousel>

        <section class="dashboard-grid" id="dashboard-grid"></section>
      </section>

      <section id="tool-screen" class="hidden">
        <button id="back-button">Back to Dashboard</button>
        <div id="tool-container"></div>
      </section>
    `;

    const grid = wrapper.querySelector("#dashboard-grid");
    const toolScreen = wrapper.querySelector("#tool-screen");
    const toolContainer = wrapper.querySelector("#tool-container");
    const dashboardSection = wrapper.querySelector("#main-dashboard");
    const backButton = wrapper.querySelector("#back-button");

    // Enhanced tool definitions with better styling
    const tools = [
      {
        label: "Cancer Drug Predictor",
        description: "AI-powered drug recommendation system",
        componentTag: "cancer-drug-recommender",
        modulePath: "../DashboardComponents/CancerDrugRecommender.js",
        icon: "🧬"
      },
      {
        label: "3D Drug Visualizer",
        description: "Interactive molecular structure viewer",
        componentTag: "three-d-viewer",
        modulePath: "./ThreeDViewer.js",
        icon: "🔬"
      },
      {
        label: "Clinical Trial Finder",
        description: "Find relevant clinical trials",
        componentTag: "trial-finder",
        modulePath: "./TrialFinder.js",
        icon: "🏥"
      }
    ];

    // Create enhanced cards
    tools.forEach((tool, index) => {
      const card = document.createElement("div");
      card.className = "dashboard-card";
      
      // Add animation delay for staggered effect
      card.style.animationDelay = `${index * 0.1}s`;
      
      card.innerHTML = `
        <div class="card-overlay">
          <div class="card-icon" style="font-size: 3rem; margin-bottom: 1rem;">${tool.icon}</div>
          <div class="card-label">${tool.label}</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem; opacity: 0.8;">
            ${tool.description}
          </div>
        </div>
      `;

      // Enhanced click handler with loading state
      card.addEventListener("click", async () => {
        // Add loading state
        toolContainer.innerHTML = '<div class="loading">Loading tool...</div>';
        
        // Hide dashboard and show tool screen
        dashboardSection.classList.add("hidden");
        toolScreen.classList.remove("hidden");
        toolScreen.classList.add("fade-in");

        try {
          // Dynamic import with error handling
          await import(tool.modulePath);
          toolContainer.innerHTML = ""; // Clear loading state
          const el = document.createElement(tool.componentTag);
          el.classList.add("fade-in");
          toolContainer.appendChild(el);
        } catch (error) {
          console.error(`Failed to load ${tool.label}:`, error);
          toolContainer.innerHTML = `
            <div class="error-state">
              <h3>Failed to load ${tool.label}</h3>
              <p>Please try again or contact support if the problem persists.</p>
              <button onclick="this.parentElement.parentElement.querySelector('#back-button').click()"></button>
            </div>
          `;
        }
      });

      // Add keyboard navigation
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', `Open ${tool.label} - ${tool.description}`);
      
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.click();
        }
      });

      grid.appendChild(card);
      
      // Add slide-in animation
      setTimeout(() => {
        card.classList.add("slide-in");
      }, index * 100);
    });

    // Enhanced back button functionality
    backButton.addEventListener("click", () => {
      toolScreen.classList.add("hidden");
      toolScreen.classList.remove("fade-in");
      dashboardSection.classList.remove("hidden");
      dashboardSection.classList.add("fade-in");
      
      // Clean up tool container
      setTimeout(() => {
        toolContainer.innerHTML = "";
      }, 300);
    });

    // Add keyboard shortcut for back button (Escape key)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !toolScreen.classList.contains('hidden')) {
        backButton.click();
      }
    });

    this.appendChild(wrapper);
  }

  // Method to add new tools dynamically
  addTool(toolConfig) {
    const grid = this.querySelector("#dashboard-grid");
    const card = document.createElement("div");
    card.className = "dashboard-card fade-in";
    
    card.innerHTML = `
      <div class="card-overlay">
        <div class="card-icon" style="font-size: 3rem; margin-bottom: 1rem;">${toolConfig.icon || '🔧'}</div>
        <div class="card-label">${toolConfig.label}</div>
        <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem; opacity: 0.8;">
          ${toolConfig.description || 'Custom tool'}
        </div>
      </div>
    `;
    
    grid.appendChild(card);
  }

  // Method to remove tools
  removeTool(toolLabel) {
    const cards = this.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
      const label = card.querySelector('.card-label');
      if (label && label.textContent === toolLabel) {
        card.remove();
      }
    });
  }
}

customElements.define("oncosage-dashboard", OncoSageDashboard);
export default OncoSageDashboard;
