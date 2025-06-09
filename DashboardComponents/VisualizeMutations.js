// GenomicDashboard.js
const template = document.createElement('template');
template.innerHTML = `
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/chart.js/dist/Chart.min.css">
  <style>
    body, :host {
      background: #111;
      color: #eee;
      font-family: sans-serif;
      margin: 0;
    }
    .dashboard-box {
      background: #1c1c1c;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 0 10px rgba(255,255,255,0.05);
    }
    h3 {
      color: #ffcc00;
      margin-bottom: 10px;
    }
    #tissueInfo {
      scrollbar-width: thin;
      scrollbar-color: #888 transparent;
    }
    #tissueInfo::-webkit-scrollbar {
      height: 8px;
    }
    #tissueInfo::-webkit-scrollbar-track {
      background: transparent;
    }
    #tissueInfo::-webkit-scrollbar-thumb {
      background-color: #888;
      border-radius: 4px;
    }
  </style>
  <div class="dashboard-box">
    <h3>Upload CSV File</h3>
    <input type="file" id="csvFile" accept=".csv">
    <div id="sampleDropdown" style="margin-top: 10px;"></div>
  </div>
  <div class="dashboard-box">
    <h3>Patient Summary</h3>
    <div id="summary"></div>
  </div>
  <div class="dashboard-box">
    <h3>IC50 Radar Chart</h3>
    <canvas id="ic50Radar" width="600" height="600"></canvas>
  </div>
  <div class="dashboard-box">
    <h3>Mutation Viewer</h3>
    <div id="mutationViewer" style="width:100%; height:300px;"></div>
  </div>
  <div class="dashboard-box">
    <h3>Tissue Information</h3>
    <div id="tissueInfo" style="display:flex; overflow-x:auto; gap:10px; padding:10px;"></div>
  </div>
  
`;

class GenomicDashboard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    this.parsedData = [];
    this.chart = null;
    
  }

  connectedCallback() {
    this.ensureLibraries().then(() => this.init());
   
  }

  async ensureLibraries() {
    // Load Chart.js, Plotly, PapaParse if not present
    const scripts = [
      { src: 'https://cdn.jsdelivr.net/npm/chart.js', global: 'Chart' },
      { src: 'https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js', global: 'Chart' },
      { src: 'https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js', global: 'Papa' },
      { src: 'https://cdn.plot.ly/plotly-2.30.0.min.js', global: 'Plotly' }
    ];
    for (const { src, global } of scripts) {
      if (!window[global]) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = src;
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }
    }
  }

  init() {
    this.shadowRoot.getElementById("csvFile").addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      window.Papa.parse(file, {
        header: true,
        complete: (results) => {
          this.parsedData = results.data.filter(r => r.feature_name); // filter invalid
          if (this.parsedData.length === 0) return;

          const dropdown = document.createElement("select");
          dropdown.id = "rowSelect";
          this.parsedData.forEach((row, i) => {
            const option = document.createElement("option");
            option.value = i;
            option.text = `Sample ${i + 1} - ${row.tissue_type || "Unknown"}`;
            dropdown.appendChild(option);
          });

          const selectDiv = this.shadowRoot.getElementById("sampleDropdown");
          selectDiv.innerHTML = "<strong>Select Sample:</strong><br>";
          selectDiv.appendChild(dropdown);

          // Initial load
          this.loadDashboard(this.parsedData[0]);

          dropdown.addEventListener("change", (e) => {
            const row = this.parsedData[parseInt(e.target.value)];
            this.loadDashboard(row);
          });
        }
      });
    });
        this.shadowRoot.getElementById('downloadBtn').addEventListener('click', () => this.downloadReport());
    
  }

  loadDashboard(row) {
    // Summary
    this.shadowRoot.getElementById('summary').innerHTML = `
      <strong>Drug Target:</strong> ${row.drug_target}<br>
      <strong>Pathway:</strong> ${row.target_pathway}<br>
      <strong>Feature Name:</strong> ${row.feature_name}<br>
      <strong>Tissue:</strong> ${row.tissue_type}<br>
      <strong>Screening Set:</strong> ${row.screening_set}<br>
    `;

    // Radar Chart
    const radarCanvas = this.shadowRoot.getElementById('ic50Radar');
    const ctx = radarCanvas.getContext('2d');
    ctx.clearRect(0, 0, radarCanvas.width, radarCanvas.height);
    if (this.chart) this.chart.destroy();

    this.chart = new window.Chart(radarCanvas, {
      type: 'radar',
      data: {
        labels: [
          "log_ic50_mean_pos",
          "log_ic50_mean_neg",
          "feature_delta_mean_ic50",
          "feature_pos_ic50_var",
          "feature_neg_ic50_var"
        ],
        datasets: [{
          label: "IC50 Metrics",
          data: [
            parseFloat(row.log_ic50_mean_pos || 0),
            parseFloat(row.log_ic50_mean_neg || 0),
            parseFloat(row.feature_delta_mean_ic50 || 0),
            parseFloat(row.feature_pos_ic50_var || 0),
            parseFloat(row.feature_neg_ic50_var || 0),
          ],
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 2
        }]
      },
      options: {
        responsive: false,
        plugins: {
          zoom: {
            pan: { enabled: true, mode: 'xy' },
            zoom: { wheel: { enabled: true }, mode: 'xy' }
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            angleLines: { color: '#444' },
            grid: { color: '#444' },
            pointLabels: { color: '#fff' }
          }
        }
      }
    });

    // Mutation Viewer
    const gene = row.feature_name?.match(/[A-Z0-9]+/g)?.[0] || "Unknown";
    window.Plotly.newPlot(
      this.shadowRoot.getElementById('mutationViewer'),
      [{
        type: 'scatter',
        mode: 'markers+text',
        x: [1],
        y: [1],
        marker: { size: 20, color: 'orange' },
        text: [gene],
        textposition: 'top center'
      }],
      {
        title: `Mutated Gene: ${gene}`,
        paper_bgcolor: '#1c1c1c',
        plot_bgcolor: '#1c1c1c',
        font: { color: '#fff' },
        xaxis: { visible: false },
        yaxis: { visible: false }
      }
    );

    // Tissue Panel
    const tissueBox = this.shadowRoot.getElementById("tissueInfo");
    const tissueType = (row.tissue_type || "unknown").toUpperCase();
    const images = [
      "i1.png", "i2.png", "i3.png", "i1.png", "i2.png", "i3.png", "i4.jpg"
    ];
    tissueBox.innerHTML = "";
    images.forEach((imgFile) => {
      const img = document.createElement('img');
      img.src = imgFile;
      img.alt = `${tissueType} Tissue Image`;
      img.style = `
        max-height:150px; 
        border: 2px solid #555; 
        border-radius: 10px; 
        cursor: pointer;
        flex-shrink: 0;
      `;
      tissueBox.appendChild(img);
    });
  }

  downloadReport() {
  const reportData = {
    generated_at: new Date().toISOString(),
    content: this.shadowRoot.getElementById('summary').innerText
  };

  // Use Electron bridge instead of anchor download
  if (window.electronAPI?.saveReport) {
    window.electronAPI.saveReport(JSON.stringify(reportData, null, 2));
  } else {
    alert("Electron bridge not available. Running in browser?");
  }
}


    

}

customElements.define('genomic-dashboard', GenomicDashboard);
export default GenomicDashboard;
