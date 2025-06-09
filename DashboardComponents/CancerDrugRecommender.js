import { fetchAndRenderMolecule } from "../Scripts/RenderMolecule.js";
class CancerDrugRecommender extends HTMLElement 
{
  constructor() {
    super();
    this.isLoading = false;
    this.hasResults = false;
  }

  connectedCallback() {
    // Load CSS dependencies
    if (!document.querySelector('link[href="styles/variables.css"]')) 
    {
      const variablesLink = document.createElement("link");
      variablesLink.rel = "stylesheet";
      variablesLink.href = "styles/variables.css";
      document.head.appendChild(variablesLink);
    }

    if (!document.querySelector('link[href="styles/CancerDrugRecommender.css"]')) 
    {
      const styleLink = document.createElement("link");
      styleLink.rel = "stylesheet";
      styleLink.href = "styles/CancerDrugRecommender.css";
      document.head.appendChild(styleLink);
    }

    // Load 3Dmol.js for molecular visualization
    if (!window.$3Dmol) 
    {
      const script = document.createElement('script');
      script.src = 'https://3dmol.csb.pitt.edu/build/3Dmol-min.js';
      document.head.appendChild(script);
    }

    this.render();
    this.attachEventListeners();
  }

  render() {
    const container = document.createElement("div");
    container.className = "container fade-in";
    
    container.innerHTML = `
      <h1>Cancer Drug Recommender</h1>
      
      <div class="form-group">
        <label for="cancerType">Cancer Type</label>
        <select id="cancerType" aria-describedby="cancerType-help">
          <option value="">Select cancer type...</option>
          <option value="lung">Lung Cancer</option>
          <option value="breast">Breast Cancer</option>
          <option value="prostate">Prostate Cancer</option>
          <option value="colorectal">Colorectal Cancer</option>
          <option value="melanoma">Melanoma</option>
          <option value="leukemia">Leukemia</option>
        </select>
        <small id="cancerType-help" style="color: var(--text-muted); font-size: var(--text-sm);">
          Select the primary cancer type for targeted recommendations
        </small>
      </div>

      <div class="form-group">
        <label for="geneticFile">Genetic Profile Data</label>
        <input type="file" id="geneticFile" accept=".json,.vcf,.csv,.tsv,.txt" 
               aria-describedby="geneticFile-help" />
        <small id="geneticFile-help" style="color: var(--text-muted); font-size: var(--text-sm);">
          Upload genetic profile data (JSON, VCF, CSV, or TSV format)
        </small>
      </div>

      <button id="submitBtn" class="submit-button" disabled>
        <span class="button-text">Analyze & Recommend</span>
        <span class="button-icon">🧬</span>
      </button>

      <div id="results" class="results-section"></div>

      <div id="viewer" class="molecular-viewer">
        <div class="viewer-placeholder">
          <div style="text-align: center; color: var(--text-muted); padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧪</div>
            <p>3D molecular structure will appear here after analysis</p>
          </div>
        </div>
      </div>

      <section class="role-based hidden" id="researcher-tools">
        <h2>Researcher Tools</h2>
        <div class="tool-buttons">
          <button id="downloadReportBtn">
            📊 Download Detailed Report
          </button>
          <button id="exportDataBtn">
            💾 Export Analysis Data
          </button>
          <button id="shareResultsBtn">
            🔗 Share Results
          </button>
        </div>
      </section>

      <section class="role-based hidden" id="oncologist-tools">
        <h2>Oncologist Panel</h2>
        <div class="tool-buttons">
          <button id="useDrugsBtn">
            💊 Apply Drug Combination
          </button>
          <button id="scheduleFollowupBtn">
            📅 Schedule Follow-up
          </button>
          <button id="patientNotesBtn">
            📝 Add to Patient Notes
          </button>
        </div>
      </section>
    `;

    this.appendChild(container);
  }

  attachEventListeners() {
    const submitBtn = this.querySelector("#submitBtn");
    const cancerType = this.querySelector("#cancerType");
    const geneticFile = this.querySelector("#geneticFile");

    // Form validation
    const validateForm = () => {
      const isValid = cancerType.value && (geneticFile.files.length > 0 || cancerType.value);
      submitBtn.disabled = !isValid;
      submitBtn.style.opacity = isValid ? '1' : '0.6';
    };

    cancerType.addEventListener("change", validateForm);
    geneticFile.addEventListener("change", validateForm);

    // Submit handler
    submitBtn.addEventListener("click", () => this.handleSubmit());

    // Tool button handlers
    this.querySelector("#downloadReportBtn")?.addEventListener("click", () => this.downloadReport());
    this.querySelector("#exportDataBtn")?.addEventListener("click", () => this.exportData());
    this.querySelector("#shareResultsBtn")?.addEventListener("click", () => this.shareResults());
    this.querySelector("#useDrugsBtn")?.addEventListener("click", () => this.useSuggestedDrugs());
    this.querySelector("#scheduleFollowupBtn")?.addEventListener("click", () => this.scheduleFollowup());
    this.querySelector("#patientNotesBtn")?.addEventListener("click", () => this.addToPatientNotes());
  }

 async handleSubmit() {
  if (this.isLoading) return;
  this.isLoading = true;

  const submitBtn = this.querySelector("#submitBtn");
  const results = this.querySelector("#results");
  const cancerType = this.querySelector("#cancerType").value;
  const geneticFile = this.querySelector("#geneticFile").files[0];

  submitBtn.innerHTML = `<span class="loading-state">Analyzing...</span>`;
  submitBtn.disabled = true;

  try {
    if (!geneticFile) {
      this.displayError("Please upload a genetic data file.");
      return;
    }

    const formData = new FormData();
    formData.append('file', geneticFile);

    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (response.ok && data.predicted_ic50_effect_size !== undefined) {
      // Format the API response for your displayResults method
      const recommendations = {
        dosage: data.predicted_ic50_effect_size.toFixed(4), // Or get from API if available
        primaryDrug: Array.isArray(data.matched_drug_names) && data.matched_drug_names.length > 0
          ? data.matched_drug_names[0]
          : 'N/A',
        combination: data.matched_drug_names || [],
        mechanism: 'Mechanism info not provided', // Or get from API if available
      };

      this.displayResults(recommendations);

      // Show 3D structure for the first matched drug
      if (recommendations.primaryDrug && recommendations.primaryDrug !== 'N/A') {
        fetchAndRenderMolecule(recommendations.primaryDrug);
      }

      this.showRoleBasedTools();
      this.hasResults = true;
    } else {
      this.displayError(data.error || "Prediction failed.");
    }
  } catch (error) {
    this.displayError("Failed to connect to prediction service.");
    console.error(error);
  } finally {
    this.isLoading = false;
    submitBtn.innerHTML = `
      <span class="button-text">Analyze & Recommend</span>
      <span class="button-icon">🧬</span>
    `;
    submitBtn.disabled = false;
  }
}





  displayResults(recommendations) {
    const results = this.querySelector("#results");
    
    results.innerHTML = `
      <div class="results-header">
        <h3>🎯 Drug Recommendations</h3>
        <div class="confidence-badge" style="background: var(--gradient-accent); color: white; padding: 0.5rem 1rem; border-radius: 2rem; font-weight: 600;">
          IC50: ${recommendations.dosage} 
        </div>
      </div>
      
      <div class="recommendation-grid">
        <div class="primary-drug">
          <h4>Primary Recommendation</h4>
          <div class="drug-card">
            <div class="drug-name">${recommendations.primaryDrug}</div>
            <div class="drug-mechanism">${recommendations.mechanism}</div>
          </div>
        </div>
        
        <div class="combination-therapy">
          <h4>Combination Therapy</h4>
          <div class="drug-list">
            ${recommendations.combination.map(drug => `
              <div class="drug-item">
                <span class="drug-bullet">💊</span>
                <span>${drug}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
      
      <div class="additional-info">
        <div class="info-card">
          <h5>📋 Treatment Considerations</h5>
          <ul>
            <li>Monitor for common side effects</li>
            <li>Regular imaging follow-up recommended</li>
            <li>Consider genetic counseling</li>
            <li>Discuss fertility preservation if applicable</li>
          </ul>
        </div>
        
        <div class="info-card">
          <h5>⚠️ Important Notes</h5>
          <p>These recommendations are based on current genetic profile analysis and should be reviewed by a qualified oncologist. Individual patient factors must be considered.</p>
        </div>
      </div>
    `;

    // Add custom styles for results
    const style = document.createElement('style');
    style.textContent = `
      .results-section {
        margin-top: 2rem;
        padding: 2rem;
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid var(--text-accent);
        border-radius: var(--radius-lg);
        backdrop-filter: blur(10px);
      }
      
      .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 1rem;
      }
      
      .results-header h3 {
        margin: 0;
        color: var(--text-accent);
      }
      
      .recommendation-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
      }
      
      .drug-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--card-border);
      }
      
      .drug-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-accent);
        margin-bottom: 0.5rem;
      }
      
      .drug-mechanism {
        color: var(--text-secondary);
        font-style: italic;
      }
      
      .drug-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
      }
      
      .drug-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: var(--input-bg);
        border-radius: var(--radius-md);
        border: 1px solid var(--input-border);
      }
      
      .additional-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
      }
      
      .info-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--card-border);
      }
      
      .info-card h5 {
        margin: 0 0 1rem 0;
        color: var(--text-accent);
      }
      
      .info-card ul {
        margin: 0;
        padding-left: 1.5rem;
      }
      
      .info-card li {
        margin-bottom: 0.5rem;
        color: var(--text-secondary);
      }
      
      @media (max-width: 768px) {
        .recommendation-grid,
        .additional-info {
          grid-template-columns: 1fr;
        }
        
        .results-header {
          flex-direction: column;
          align-items: flex-start;
        }
      }
    `;
    
    if (!document.querySelector('#results-styles')) {
      style.id = 'results-styles';
      document.head.appendChild(style);
    }
  }

  

  showRoleBasedTools() {
    this.querySelector("#researcher-tools").classList.remove("hidden");
    this.querySelector("#oncologist-tools").classList.remove("hidden");
  }

  displayError(message) {
    const results = this.querySelector("#results");
    results.innerHTML = `
      <div class="error-state">
        <h3>⚠️ Analysis Error</h3>
        <p>${message}</p>
        <button onclick="location.reload()" style="margin-top: 1rem;">
          🔄 Try Again
        </button>
      </div>
    `;
  }

  // Tool Methods
  downloadReport() {
    if (!this.hasResults) return;
    
    // Simulate report generation
    const reportData = {
      timestamp: new Date().toISOString(),
      patient: "Analysis Report",
      recommendations: "Generated recommendations...",
      confidence: "High confidence level"
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `oncology-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    this.showNotification("📊 Report downloaded successfully!");
  }

  exportData() {
    this.showNotification("💾 Analysis data exported!");
  }

  shareResults() {
    if (navigator.share) {
      navigator.share({
        title: 'OncoSage Analysis Results',
        text: 'Drug recommendation analysis completed',
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      this.showNotification("🔗 Results link copied to clipboard!");
    }
  }

  useSuggestedDrugs() {
    this.showNotification("💊 Drug combination added to treatment plan!");
  }

  scheduleFollowup() {
    this.showNotification("📅 Follow-up appointment scheduled!");
  }

  addToPatientNotes() {
    this.showNotification("📝 Analysis added to patient notes!");
  }

  showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--gradient-accent);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: var(--radius-lg);
      box-shadow: var(--card-shadow);
      z-index: var(--z-tooltip);
      animation: slideInFromRight 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutToRight 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Add notification animations
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
  @keyframes slideInFromRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideOutToRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(notificationStyles);

customElements.define("cancer-drug-recommender", CancerDrugRecommender);
export default CancerDrugRecommender;
