document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.querySelector(".chat-form");
  const queryInput = document.querySelector("#query");

  document.querySelectorAll(".quick-mood-btn").forEach((button) => {
    button.addEventListener("click", () => {
      if (!chatForm || !queryInput) return;

      queryInput.value = button.dataset.query || button.textContent.trim();
      chatForm.requestSubmit();
    });
  });
});
