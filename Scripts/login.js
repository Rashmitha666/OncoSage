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
      window.location.href = "../Dashboard/drugPrediction.html";
    }, 1000);
  } else {
    loginMsg.style.color = "red";
    loginMsg.textContent = "Invalid email or password.";
  }
});