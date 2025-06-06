export async function fetchAndRenderMolecule(drugName) {
  try {
    const sdfRes = await fetch(`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${encodeURIComponent(drugName)}/SDF`, {
      headers: { 'Content-Type': 'chemical/x-mdl-sdfile' }
    });

    if (!sdfRes.ok) throw new Error('Failed to fetch molecule data');

    const sdfText = await sdfRes.text();

    const viewer = $3Dmol.createViewer("viewer", { backgroundColor: "white" });
    viewer.clear();
    viewer.addModel(sdfText, "sdf");
    viewer.setStyle({}, { stick: {} });
    viewer.zoomTo();
    viewer.render();
  } catch (err) {
    console.error("Could not fetch or render molecule:", err);
  }
}
