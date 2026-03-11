



document.addEventListener("DOMContentLoaded", () => {

  const downloadBtn = document.getElementById("templateDownloadBtn");
  const analysisId = downloadBtn.dataset.analysisId;

  document.querySelectorAll(".use-template-btn").forEach(btn => {
    btn.addEventListener("click", async () => {

      const card = btn.closest(".template-card");
      const template = card.dataset.template;

      await fetch("/select-template/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ template })
      });

      document
        .querySelectorAll(".template-card")
        .forEach(c => c.classList.remove("selected"));

      card.classList.add("selected");

      downloadBtn.style.display = "inline-block";
      downloadBtn.innerText = `⬇ Download (${template}) Resume`;

      downloadBtn.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  downloadBtn.addEventListener("click", () => {
    const card = document.querySelector(".template-card.selected");
    const template = card ? card.dataset.template : "classic";
    window.location.href = `/download-template/${analysisId}/?template=${template}`;
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    for (let cookie of document.cookie.split(";")) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}