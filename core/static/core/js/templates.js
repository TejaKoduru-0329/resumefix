// document.addEventListener("DOMContentLoaded", function () {
//     const grid = document.getElementById("templateGrid");
//     const downloadBtn = document.getElementById("templateDownloadBtn");
//     const analysisId = downloadBtn.dataset.analysisId;

//     const templates = ["classic", "modern", "compact"];

//     templates.forEach(tpl => {
//         const div = document.createElement("div");
//         div.style.display = "inline-block";
//         div.style.margin = "10px";

//         div.innerHTML = `
//             <iframe src="/resume-preview/?template=${tpl}" width="300" height="400"></iframe>
//             <br>
//             <button onclick="selectTemplate('${tpl}')">Use ${tpl}</button>
//         `;
//         grid.appendChild(div);
//     });

//     window.selectTemplate = function (template) {
//         fetch("/select-template/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCookie("csrftoken")
//             },
//             body: JSON.stringify({ template })
//         }).then(() => {
//             downloadBtn.style.display = "inline-block";
//             downloadBtn.innerText = `⬇ Download (${template}) Resume`;
//         });
//     };

//     downloadBtn.addEventListener("click", function () {
//         window.open(`/download/${analysisId}/`, "_blank");
//     });
// });

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== "") {
//         for (let cookie of document.cookie.split(";")) {
//             cookie = cookie.trim();
//             if (cookie.startsWith(name + "=")) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }


// document.addEventListener("DOMContentLoaded", () => {

//   const downloadBtn = document.getElementById("templateDownloadBtn");
//   const analysisId = downloadBtn.dataset.analysisId;

//   document.querySelectorAll(".use-template-btn").forEach(btn => {
//     btn.addEventListener("click", () => {

//       const card = btn.closest(".template-card");
//       const template = card.dataset.template;

//       fetch("/select-template/", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": getCookie("csrftoken")
//         },
//         body: JSON.stringify({ template })
//       });

//       document
//         .querySelectorAll(".template-card")
//         .forEach(c => c.classList.remove("selected"));

//       card.classList.add("selected");

//       downloadBtn.style.display = "inline-block";
//       downloadBtn.innerText = `⬇ Download (${template}) Resume`;
//     });
//   });

//   downloadBtn.addEventListener("click", () => {
//     window.open(`/download/${analysisId}/`, "_blank");
//   });
// });

// function getCookie(name) {
//   let cookieValue = null;
//   if (document.cookie && document.cookie !== "") {
//     for (let cookie of document.cookie.split(";")) {
//       cookie = cookie.trim();
//       if (cookie.startsWith(name + "=")) {
//         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//         break;
//       }
//     }
//   }
//   return cookieValue;
// }



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
    window.open(`/download/${analysisId}/`, "_blank");
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