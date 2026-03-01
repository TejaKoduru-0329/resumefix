
// document.addEventListener("DOMContentLoaded", () => {

//   // DOM ELEMENTS

//   const form = document.querySelector("form");
//   const fileInput = document.getElementById("resumeInput");
//   const jdTextarea = document.querySelector(".jd-box textarea");

//   const uploadIconWrap = document.getElementById("uploadIconWrap");
//   const uploadStatus = document.getElementById("uploadStatus");
//   const uploadSub = document.getElementById("uploadSub");

//   const fileRow = document.getElementById("fileRow");
//   const fileName = document.getElementById("fileName");
//   const errorText = document.getElementById("fileError");

//   const loading = document.getElementById("loading");
//   const resultsSection = document.getElementById("resultsSection");

//   const beforePreview = document.getElementById("beforePreview");
//   const afterPreview = document.getElementById("afterPreview");

//   const formError = document.getElementById("formError");
//   const formErrorText = document.getElementById("formErrorText");

//   const allowedTypes = [
//     "application/pdf",
//     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
//   ];

//   // HELPER FUNCTIONS

//   function showError(msg) {
//     formErrorText.innerText = msg;
//     formError.style.display = "flex";
//   }

//   function hideError() {
//     formError.style.display = "none";
//   }

//   // FILE UPLOAD HANDLER

//   fileInput.addEventListener("change", function () {
//     const file = this.files[0];
//     if (!file) return;

//     if (!allowedTypes.includes(file.type)) {
//       errorText.style.display = "block";
//       this.value = "";
//       return;
//     }

//     errorText.style.display = "none";
//     hideError();

//     // Upload animation
//     uploadIconWrap.innerHTML = `<div class="spinner-border text-primary"></div>`;
//     uploadStatus.innerText = "Uploading…";
//     uploadSub.innerText = "";
//     fileRow.style.display = "none";

//     setTimeout(() => {
//       uploadIconWrap.innerHTML =
//         `<i class="fa-solid fa-cloud-arrow-up upload-icon"></i>`;
//       uploadStatus.innerText = "Resume Uploaded";
//       uploadSub.innerText = "";
//       fileName.innerText = file.name;
//       fileRow.style.display = "flex";
//     }, 800);
//   });

//   // REMOVE FILE HANDLER

//   window.removeFile = function () {
//     fileInput.value = "";

//     uploadIconWrap.innerHTML =
//       `<i class="fa-solid fa-cloud-arrow-up upload-icon"></i>`;
//     uploadStatus.innerText = "Upload Resume";
//     uploadSub.innerText = "PDF or DOCX";

//     fileRow.style.display = "none";
//     errorText.style.display = "none";
//     hideError();
//   };

//   // FORM SUBMISSION HANDLER

//   form.addEventListener("submit", async function (e) {
//     e.preventDefault();

//     hideError();

//     if (!fileInput.files.length || !jdTextarea.value.trim()) {
//       showError("Please provide both a resume and a job description");
//       return;
//     }

//     loading.style.display = "block";
//     resultsSection.style.display = "none";

//     const formData = new FormData(form);

//     try {
//       const response = await fetch("/api/fix-resume/", {
//         method: "POST",
//         body: formData,
//         headers: {
//           "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
//         }
//       });

//       const data = await response.json();

//       loading.style.display = "none";

//       if (!data.success) {
//         showError(data.error || "AI failed. Please try again.");
//         return;
//       }

//       //  SET PREVIEW CONTENT
//       beforePreview.innerText = data.before_text;
      
//       afterPreview.innerHTML = renderAIContent(data.optimized_content);

//       //  SHOW PREVIEW
//       resultsSection.style.display = "block";

//       //  DOWNLOAD BUTTON
//       const downloadBtn = document.getElementById("downloadBtn");
//       if (downloadBtn && downloadBtn.dataset.analysisId) {
//           downloadBtn.addEventListener("click", function () {
//               const id = this.dataset.analysisId;
//               window.open(`/download/${id}/`, "_blank");
//           });
//       }

    
//       // if (downloadBtn && downloadBtn.dataset.analysisId) {
//       //     downloadBtn.style.display = "inline-block";

//       //     downloadBtn.addEventListener("click", function () {
//       //         const analysisId = this.dataset.analysisId;
//       //         window.open(`/download/${analysisId}/`, "_blank");
//       //     });
//       // }

//       // Scroll to preview
//       resultsSection.scrollIntoView({ behavior: "smooth" });

//     } catch (err) {
//       loading.style.display = "none";
//       showError("Server error. Please try again later.");
//       console.error(err);
//     }
//   });

//   jdTextarea.addEventListener("input", hideError);

//   // AI CONTENT RENDERER
//   function renderAIContent(text) {
//     const lines = text.split("\n");
//     let html = "";

//     let currentSection = "";
//     let bulletBuffer = [];
//     let i = 0;

//     function flushBullets() {
//       if (bulletBuffer.length) {
//         html += `<ul class="resume-bullets">`;
//         bulletBuffer.forEach(b => {
//           html += `<li>${b}</li>`;
//         });
//         html += `</ul>`;
//         bulletBuffer = [];
//       }
//     }

//     while (i < lines.length) {
//       const line = lines[i].trim();

//       if (!line) {
//         i++;
//         continue;
//       }

//       /* NAME */
//       if (i === 0) {
//         html += `<div class="resume-name">${line}</div>`;
//         i++;
//         continue;
//       }

//       /* SECTION HEADINGS */
//       if (line.startsWith("**") && line.endsWith("**")) {
//         flushBullets();
//         currentSection = line.replace(/\*/g, "");
//         html += `
//           <div class="resume-heading">${currentSection}</div>
//           <hr class="heading-line">
//         `;
//         i++;
//         continue;
//       }

//       /* EDUCATION — ONLY 2-LINE BLOCK */
//       if (
//         currentSection === "EDUCATION" &&
//         lines[i + 1] &&
//         lines[i + 1].includes("|")
//       ) {
//         const collegeLine = line;
//         const degreeLine = lines[i + 1].trim();

//         html += `
//           <div class="edu-entry">
//             <div class="edu-college">${collegeLine}</div>
//             <div class="edu-meta">${degreeLine}</div>
//           </div>
//         `;
//         i += 2;
//         continue;
//       }

//       /* BULLETS */
//       if (line.startsWith("•")) {
//         bulletBuffer.push(line.slice(1).trim());
//         i++;
//         continue;
//       }

//       /* PROJECT / WORK EXPERIENCE TITLE */
//       if (
//         (currentSection === "PROJECTS" || currentSection === "WORK EXPERIENCE") &&
//         !line.startsWith("•")
//       ) {
//         flushBullets();
//         html += `<div class="project-title">${line}</div>`;
//         i++;
//         continue;
//       }

//       /* TECHNICAL SKILLS – inline bold sub-heading */
//       if (currentSection === "TECHNICAL SKILLS" && line.includes(":")) {
//         const [left, right] = line.split(":", 2);
//         html += `<p class="skill-line"><strong>${left}:</strong> ${right.trim()}</p>`;
//         i++;
//         continue;
//       }

//       /* NORMAL TEXT */
//       flushBullets();
//       html += `<p>${line}</p>`;
//       i++;
//     }

//     flushBullets();
//     return html;
//   }
  
// });



document.addEventListener("DOMContentLoaded", () => {

  /* ==========================
     DOM ELEMENTS
  ========================== */

  const form = document.querySelector("form");
  const fileInput = document.getElementById("resumeInput");
  const jdTextarea = document.querySelector(".jd-box textarea");

  const uploadIconWrap = document.getElementById("uploadIconWrap");
  const uploadStatus = document.getElementById("uploadStatus");
  const uploadSub = document.getElementById("uploadSub");

  const fileRow = document.getElementById("fileRow");
  const fileName = document.getElementById("fileName");
  const errorText = document.getElementById("fileError");

  const loading = document.getElementById("loading");
  const resultsSection = document.getElementById("resultsSection");

  const beforePreview = document.getElementById("beforePreview");
  const afterPreview = document.getElementById("afterPreview");

  const formError = document.getElementById("formError");
  const formErrorText = document.getElementById("formErrorText");

  const downloadBtn = document.getElementById("downloadBtn");

  const aiProgress = document.getElementById("aiProgress");
  const aiStatusText = document.getElementById("aiStatusText");
  const fill = document.getElementById("aiProgressFill");
  document.getElementById("formErrorClose").addEventListener("click", hideError);
  

  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  const MIN_LOADER_TIME = 1500; // Minimum time to show loader (ms)

  /* ==========================
     HELPER FUNCTIONS
  ========================== */

  function showError(msg) {
    formErrorText.innerText = msg;
    formError.style.display = "flex";
  }

  function hideError() {
    formError.style.display = "none";
  }

  /* ==========================
     FILE UPLOAD HANDLER
  ========================== */

  fileInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    if (!allowedTypes.includes(file.type)) {
      errorText.style.display = "block";
      this.value = "";
      return;
    }

    errorText.style.display = "none";
    hideError();

    uploadIconWrap.innerHTML = `<div class="spinner-border text-primary"></div>`;
    uploadStatus.innerText = "Uploading…";
    uploadSub.innerText = "";
    fileRow.style.display = "none";

    setTimeout(() => {
      uploadIconWrap.innerHTML =
        `<i class="fa-solid fa-cloud-arrow-up upload-icon"></i>`;
      uploadStatus.innerText = "Resume Uploaded";
      fileName.innerText = file.name;
      fileRow.style.display = "flex";
    }, 700);
  });

  /* ==========================
     REMOVE FILE
  ========================== */

  window.removeFile = function () {
    fileInput.value = "";
    uploadIconWrap.innerHTML =
      `<i class="fa-solid fa-cloud-arrow-up upload-icon"></i>`;
    uploadStatus.innerText = "Upload Resume";
    uploadSub.innerText = "PDF or DOCX";
    fileRow.style.display = "none";
    errorText.style.display = "none";
    hideError();
  };

  /* ==========================
     FORM SUBMIT
  ========================== */

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    hideError();

    if (!fileInput.files.length || !jdTextarea.value.trim()) {
      showError("Please provide both a resume and a job description");
      return;
    }

    resultsSection.style.display = "none";

    // SHOW PROGRESS BAR
    aiProgress.style.display = "block";

    // Animate bar + update status text in stages
    fill.style.width = "20%";
    aiStatusText.innerText = "Analyzing resume…";

    const loaderStartTime = Date.now();
    const progressTimers = [];

    progressTimers.push(setTimeout(() => {
      fill.style.width = "45%";
      aiStatusText.innerText = "Extracting keywords…";
    }, 1000));

    progressTimers.push(setTimeout(() => {
      fill.style.width = "70%";
      aiStatusText.innerText = "Matching ATS keywords…";
    }, 2000));

    progressTimers.push(setTimeout(() => {
      fill.style.width = "90%";
      aiStatusText.innerText = "Optimizing resume content…";
    }, 3000));

    const formData = new FormData(form);

    try {
      const response = await fetch("/api/fix-resume/", {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
      });

      const data = await response.json();

      const elapsed = Date.now() - loaderStartTime;
      const remaining = MIN_LOADER_TIME - elapsed;

      setTimeout(() => {
        // STOP AI PROGRESS
        aiProgress.style.display = "none";
        progressTimers.forEach(t => clearTimeout(t));

        if (!data.success) {
          showError(data.message || "AI failed. Please try again.");
          return;
        }

        /* ==========================
          SAFE RENDER
        ========================== */

        beforePreview.innerText = data.before_text || "";
        afterPreview.innerHTML = renderAIContent(data.optimized_text || "");

        resultsSection.style.display = "block";

        /* ==========================
          DOWNLOAD BUTTON
        ========================== */

        if (downloadBtn) {
          downloadBtn.dataset.analysisId = data.analysis_id;
          downloadBtn.style.display = "inline-block";

          downloadBtn.onclick = function () {
            window.open(`/download/${data.analysis_id}/`, "_blank");
          };
        }

        resultsSection.scrollIntoView({ behavior: "smooth" });
      }, remaining > 0 ? remaining : 0);
    

    } catch (err) {
      const elapsed = Date.now() - loaderStartTime;
      const remaining = MIN_LOADER_TIME - elapsed;

      setTimeout(() => {
        aiProgress.style.display = "none";
        fill.style.width = "0%";
        progressTimers.forEach(t => clearTimeout(t));
        showError("Server error. Please try again later.");
      }, remaining > 0 ? remaining : 0);
      
      console.error(err);
    }
  });

  jdTextarea.addEventListener("input", hideError);

  /* ==========================
     AI CONTENT RENDERER (SAFE)
  ========================== */

  function renderAIContent(text) {
    if (!text || typeof text !== "string") {
      console.warn("renderAIContent: empty or invalid text");
      return "";
    }

    const lines = text.split("\n");
    let html = "";

    let currentSection = "";
    let bulletBuffer = [];
    let i = 0;

    function flushBullets() {
      if (bulletBuffer.length) {
        html += `<ul class="resume-bullets">`;
        bulletBuffer.forEach(b => {
          html += `<li>${b}</li>`;
        });
        html += `</ul>`;
        bulletBuffer = [];
      }
    }

    while (i < lines.length) {
      const line = lines[i].trim();

      if (!line) {
        i++;
        continue;
      }

      if (i === 0) {
        html += `<div class="resume-name">${line}</div>`;
        i++;
        continue;
      }

      if (line.startsWith("**") && line.endsWith("**")) {
        flushBullets();
        currentSection = line.replace(/\*/g, "");
        html += `
          <div class="resume-heading">${currentSection}</div>
          <hr class="heading-line">
        `;
        i++;
        continue;
      }

      if (currentSection === "EDUCATION" && lines[i + 1]?.includes("|")) {
        html += `
          <div class="edu-entry">
            <div class="edu-college">${line}</div>
            <div class="edu-meta">${lines[i + 1].trim()}</div>
          </div>
        `;
        i += 2;
        continue;
      }

      if (line.startsWith("•")) {
        bulletBuffer.push(line.slice(1).trim());
        i++;
        continue;
      }

      if (
        (currentSection === "PROJECTS" || currentSection === "WORK EXPERIENCE") &&
        !line.startsWith("•")
      ) {
        flushBullets();
        html += `<div class="project-title">${line}</div>`;
        i++;
        continue;
      }

      if (currentSection === "TECHNICAL SKILLS" && line.includes(":")) {
        const [left, right] = line.split(":", 2);
        html += `<p class="skill-line"><strong>${left}:</strong> ${right.trim()}</p>`;
        i++;
        continue;
      }

      flushBullets();
      html += `<p>${line}</p>`;
      i++;
    }

    flushBullets();
    return html;
  }

});




