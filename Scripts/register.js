
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