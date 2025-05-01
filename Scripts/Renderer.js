document.getElementById('submitBtn').addEventListener('click', async () => {
    const cancerType = document.getElementById('cancerType').value;
    const fileInput = document.getElementById('geneticFile');
    const resultDiv = document.getElementById('results');
  
    if (!fileInput.files[0]) {
      resultDiv.innerHTML = '<p style="color:red;">Please upload a genetic file.</p>';
      return;
    }
  
    const reader = new FileReader();
    reader.onload = function () {
      const fileData = reader.result;
  
      let recommendations = [];
      switch (cancerType) {
        case 'lung':
          recommendations = [
            { name: 'Afatinib', efficacy: '85%', toxicity: 'Low' },
            { name: 'Osimertinib', efficacy: '90%', toxicity: 'Moderate' }
          ];
          break;
        case 'breast':
          recommendations = [
            { name: 'Tamoxifen', efficacy: '88%', toxicity: 'Low' },
            { name: 'Trastuzumab', efficacy: '83%', toxicity: 'Moderate' }
          ];
          break;
        case 'prostate':
          recommendations = [
            { name: 'Enzalutamide', efficacy: '80%', toxicity: 'Low' },
            { name: 'Abiraterone', efficacy: '85%', toxicity: 'Moderate' }
          ];
          break;
      }
  
      resultDiv.innerHTML = `
        <h3>Recommended Drugs for ${cancerType.charAt(0).toUpperCase() + cancerType.slice(1)} Cancer</h3>
        <ul>
          ${recommendations.map(drug =>
            `<li><strong>${drug.name}</strong> – Efficacy: ${drug.efficacy}, Toxicity: ${drug.toxicity}</li>`
          ).join('')}
        </ul>
      `;
    };
  
    reader.readAsText(fileInput.files[0]);
  });
  