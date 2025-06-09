class AIAgent extends HTMLElement {
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
        window.location.href = 'http://localhost:8501';
      });
  }
}

customElements.define('ai-agent', AIAgent);
export default AIAgent;
