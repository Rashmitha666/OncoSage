class LiteratureInsights extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    this.shadowRoot.innerHTML = `
      <style>
        button {
          padding: 10px 20px;
          font-size: 16px;
          cursor: pointer;
        }
      </style>
      <div>
        <h2>Oncology AI Assistant Dashboard</h2>
        <button id="launchBtn">Launch Dashboard</button>
      </div>
    `;
  }

  connectedCallback() {
    this.shadowRoot.getElementById('launchBtn')
      .addEventListener('click', () => {
        window.location.href = 'http://localhost:8050';
      });
  }
}

customElements.define('literature-insights', LiteratureInsights);
export default LiteratureInsights;
