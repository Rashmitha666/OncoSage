document.getElementById("loginForm")?.addEventListener("submit", function (e) {
  e.preventDefault();

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();
  const loginMsg = document.getElementById("loginMsg");

  // Hardcoded credentials
  const hardcodedEmail = "admin@example.com";
  const hardcodedPassword = "admin123";

  if (email === hardcodedEmail && password === hardcodedPassword) {
    loginMsg.style.color = "green";
    loginMsg.textContent = "Login successful! Redirecting...";
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 1000);
  } else {
    loginMsg.style.color = "red";
    loginMsg.textContent = "Invalid email or password.";
  }
});


// Register logic
document.getElementById("registerForm")?.addEventListener("submit", function (e) {
  e.preventDefault();
  const name = document.getElementById("registerName").value.trim();
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value.trim();
  const role = document.getElementById("registerRole").value;
  const msg = document.getElementById("registerMsg");

  if (!name || !email || !password || !role) {
    msg.textContent = "All fields are required.";
    msg.style.color = "red";
    return;
  }

  localStorage.setItem(email, JSON.stringify({ name, email, password, role }));
  msg.textContent = "Registration successful. Redirecting to login...";
  msg.style.color = "green";
  setTimeout(() => (window.location.href = "index.html"), 2000);
});

// Dashboard (drug recommendation)
function submitData() {
  const file = document.getElementById("geneticData").files[0];
  const cancerType = document.getElementById("cancerType").value;

  if (!file || !cancerType) {
    alert("Please upload genetic data and select a cancer type.");
    return;
  }

  const mockRecommendations = `
    <ul>
      <li>Drug A (80% effectiveness)</li>
      <li>Drug B (75% effectiveness)</li>
      <li>Drug C (60% effectiveness)</li>
    </ul>
  `;

  document.getElementById("recommendations").innerHTML = mockRecommendations;
  document.getElementById("results").classList.remove("hidden");

  const user = JSON.parse(localStorage.getItem("loggedInUser"));
  if (user) showRoleBasedPanels(user.role);
}

function showRoleBasedPanels(role) {
  if (role === "Researcher") {
    document.getElementById("researcher-tools")?.classList.remove("hidden");
  } else if (role === "Oncologist") {
    document.getElementById("oncologist-tools")?.classList.remove("hidden");
  }
}

function downloadReport() {
  alert("Report downloaded successfully.");
}

function useSuggestedDrugs() {
  alert("Suggested drug combination applied.");
}