import { fetchAndRenderMolecule } from "../scripts/RenderMolecule.js";

class CancerDrugRecommender extends HTMLElement {
  constructor() {
    super();
    this.isLoading = false;
    this.hasResults = false;
    this.currentResults = null;
  }

  connectedCallback() {
    // Load CSS dependencies
    if (!document.querySelector('link[href="styles/variables.css"]')) {
      const variablesLink = document.createElement("link");
      variablesLink.rel = "stylesheet";
      variablesLink.href = "styles/variables.css";
      document.head.appendChild(variablesLink);
    }

    if (!document.querySelector('link[href="styles/CancerDrugRecommender.css"]')) {
      const styleLink = document.createElement("link");
      styleLink.rel = "stylesheet";
      styleLink.href = "styles/CancerDrugRecommender.css";
      document.head.appendChild(styleLink);
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

      <section class="researcher-tools hidden" id="researcher-tools">
        <h2>Research Tools</h2>
        <div class="tool-buttons">
          <button id="downloadReportBtn">
            📊 Download Detailed Report
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

      // Use Electron's fetch wrapper for CORS handling
      let response;
      if (window.electronAPI && window.electronAPI.fetchWithCors) {
        const formData = new FormData();
        formData.append('file', geneticFile);

        response = await window.electronAPI.fetchWithCors('http://localhost:5000/predict', {
          method: 'POST',
          body: formData,
        });
      } else {
        // Fallback for non-Electron environments
        const formData = new FormData();
        formData.append('file', geneticFile);

        response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          body: formData,
        });
      }

      const data = await response.json();

      if (response.ok && data.predicted_ic50_effect_size !== undefined) {
        const recommendations = {
          dosage: data.predicted_ic50_effect_size.toFixed(4),
          primaryDrug: Array.isArray(data.matched_drug_names) && data.matched_drug_names.length > 0
            ? data.matched_drug_names[0]
            : 'N/A',
          combination: data.matched_drug_names || [],
          mechanism: 'Targeted therapy based on genetic profile analysis',
        };

        this.currentResults = {
          cancerType,
          geneticProfile: geneticFile.name,
          recommendations,
          timestamp: new Date().toISOString(),
          analysisData: data
        };

        this.displayResults(recommendations);

        // Show 3D structure for the first matched drug
        if (recommendations.primaryDrug && recommendations.primaryDrug !== 'N/A') {
          fetchAndRenderMolecule(recommendations.primaryDrug);
        }

        this.showResearchTools();
        this.hasResults = true;
      } else {
        this.displayError(data.error || "Prediction failed.");
      }
    } catch (error) {
      this.displayError("Failed to connect to prediction service. Please ensure the backend server is running.");
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

  showResearchTools() {
    this.querySelector("#researcher-tools").classList.remove("hidden");
  }

  displayError(message) {
    const results = this.querySelector("#results");
    results.innerHTML = `
      <div class="error-state">
        <h3>⚠️ Analysis Error</h3>
        <p>${message}</p>
        <div class="error-actions">
          <button class="retry-btn" onclick="location.reload()">
            🔄 Try Again
          </button>
        </div>
      </div>
    `;
  }

  async downloadReport() {
    if (!this.currentResults) {
      if (window.electronAPI) {
        await window.electronAPI.showError('No Data', 'No analysis results available to download.');
      } else {
        alert('No analysis results available to download.');
      }
      return;
    }

    try {
      const reportContent = this.generateReportContent();
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `cancer_drug_analysis_${timestamp}.txt`;

      if (window.electronAPI && window.electronAPI.downloadFile) {
        // Use Electron's native file dialog
        const result = await window.electronAPI.downloadFile({
          defaultPath: filename,
          content: reportContent,
          filters: [
            { name: 'Text Files', extensions: ['txt'] },
            { name: 'JSON Files', extensions: ['json'] },
            { name: 'All Files', extensions: ['*'] }
          ]
        });

        if (result.success) {
          await window.electronAPI.showInfo('Download Complete', 
            `Report saved successfully to: ${result.filePath}`);
        } else if (!result.canceled) {
          throw new Error(result.error || 'Download failed');
        }
      } else {
        // Fallback for non-Electron environments
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Download error:', error);
      if (window.electronAPI) {
        await window.electronAPI.showError('Download Failed', 
          `Failed to download report: ${error.message}`);
      } else {
        alert(`Failed to download report: ${error.message}`);
      }
    }
  }

  generateReportContent() {
    const { cancerType, geneticProfile, recommendations, timestamp, analysisData } = this.currentResults;
    
    return `
CANCER DRUG ANALYSIS REPORT
===========================

Analysis Date: ${new Date(timestamp).toLocaleDateString()}
Cancer Type: ${cancerType}
Genetic Profile File: ${geneticProfile}

DRUG RECOMMENDATIONS
===================

Primary Recommendation: ${recommendations.primaryDrug}
IC50 Effect Size: ${recommendations.dosage}
Mechanism of Action: ${recommendations.mechanism}

Combination Therapy:
${recommendations.combination.map(drug => `  - ${drug}`).join('\n')}

TREATMENT CONSIDERATIONS
=======================

- Monitor for common side effects
- Regular imaging follow-up recommended
- Consider genetic counseling
- Discuss fertility preservation if applicable

IMPORTANT DISCLAIMER
===================

These recommendations are based on current genetic profile analysis and 
should be reviewed by a qualified oncologist. Individual patient factors 
must be considered before making any treatment decisions.

RAW ANALYSIS DATA
================

${JSON.stringify(analysisData, null, 2)}

Generated by Cancer Drug Research Platform
For research purposes only.
    `.trim();
  }
}

// Register the custom element
customElements.define("cancer-drug-recommender", CancerDrugRecommender);

export default CancerDrugRecommender;
