import { fetchAndRenderMolecule } from "./RenderMolecule.js";


document.getElementById('submitBtn').addEventListener('click', async () => 
{
  const cancerType = document.getElementById('cancerType').value;
  const fileInput = document.getElementById('geneticFile');
  const resultDiv = document.getElementById('results');

  if (!fileInput.files[0]) 
  {
    resultDiv.innerHTML = '<p style="color:red;">Please upload a genetic data file.</p>';
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try 
  {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (response.ok && data.predicted_ic50_effect_size !== undefined) 
    {
      const drugList = Array.isArray(data.matched_drug_names) 
      ? data.matched_drug_names.join(', ') 
      : data.matched_drug_names;

      resultDiv.innerHTML = `
        <h3>Predicted IC50 Effect Size for ${cancerType.charAt(0).toUpperCase() + cancerType.slice(1)} Cancer</h3>
        <p><strong>${data.predicted_ic50_effect_size.toFixed(4)}</strong></p>
        <p><strong>Matched Drugs:</strong> ${drugList}</p>
      `;

      if (Array.isArray(data.matched_drug_names) && data.matched_drug_names.length > 0) 
      {
        fetchAndRenderMolecule(data.matched_drug_names[0]);
      }

    } 
    else 
    {
      resultDiv.innerHTML = `<p style="color:red;">❌ ${data.error || 'Prediction failed.'}</p>`;
    }

  } 
  catch (err) 
  {
    resultDiv.innerHTML = `<p style="color:red;">❌ Failed to connect to prediction service.</p>`;
    console.error(err);
  }
});
