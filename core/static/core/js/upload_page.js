
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

  let isSubmitting = false;

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

    if (isSubmitting) return;

    if (!fileInput.files.length || !jdTextarea.value.trim()) {
      showError("Please provide both a resume and a job description");
      return;
    }

    const fixBtn = form.querySelector("button[type='submit']");
    fixBtn.disabled = true;
    fixBtn.innerText = "Processing...";
    isSubmitting = true

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
          fixBtn.disabled = false;
          fixBtn.innerText = "⚡ Fix My Resume";
          isSubmitting = false;
          return;
        }

        // COMPLETE PROGRESS
        fill.style.width = "100%";
        aiStatusText.innerText = "Resume optimized!";

        /* ==========================
          SAFE RENDER
        ========================== */

        beforePreview.innerText = data.before_text || "";
        afterPreview.innerHTML = renderAIContent(data.optimized_text || "");

        resultsSection.style.display = "block";

        // ATS SCORE
        const atsContainer = document.getElementById("atsScoreSection");
        if (atsContainer && data.ats_score) {
          atsContainer.innerHTML = renderATSScore(data.ats_score);
          atsContainer.style.display = "block";
        }

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

        fixBtn.disabled = false;
        fixBtn.innerText = "⚡ Fix My Resume";
        isSubmitting = false;

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

        fixBtn.diabled = false;
        fixBtn.innerText = "⚡ Fix My Resume";
        isSubmitting = false;
      }, remaining > 0 ? remaining : 0);
      
      console.error(err);
    }
  });

  jdTextarea.addEventListener("input", hideError);

  const coverLetterBtn = document.getElementById("generateCoverLetterBtn");
  const coverLetterSection = document.getElementById("coverLetterSection");
  const coverLetterContent = document.getElementById("coverLetterContent");
  const downloadCoverLetterBtn = document.getElementById("downloadCoverLetterBtn");

  if (coverLetterBtn) {
    coverLetterBtn.addEventListener("click", async () => {
      coverLetterBtn.disabled = true;
      coverLetterBtn.innerText = "Generating...";

      try {
        const response = await fetch("/api/cover-letter/", {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
          }
        });

        const data = await response.json();

        if (!data.success) {
          alert("Failed to generate cover letter");
          return;
        }

        coverLetterContent.innerText = data.cover_letter;
        coverLetterSection.style.display = "block";

        // Store for download
        downloadCoverLetterBtn.onclick = async () => {
          const form = new FormData();
          form.append("cover_letter", data.cover_letter);
          form.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

          const res = await fetch("/download-cover-letter/", {
            method: "POST",
            body: form
          });

          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "cover_letter.pdf";
          a.click();
        };

        coverLetterSection.scrollIntoView({ behavior: "smooth" });

      } catch (err) {
        console.error(err);
        alert("Server error");
      } finally {
        coverLetterBtn.disabled = false;
        coverLetterBtn.innerText = "✉ Generate Cover Letter";
      }
    });
  }
  
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
        // Split name and contact if on same line
        const parts = line.split("|");
        const name = parts[0].trim();
        const contact = parts.slice(1).join("|").trim();

        html += `<div class="resume-name">${name}</div>`;
        if (contact) {
            html += `<div class="resume-contact">${contact}</div>`;
        }
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

  function renderATSScore(ats) {
    const beforeScore = ats.before_score;
    const afterScore = ats.after_score;

    const matchedHTML = ats.matched_keywords.map(k =>
      `<span class="ats-tag ats-matched">${k}</span>`).join("");

    const missingHTML = ats.missing_keywords.map(k =>
      `<span class="ats-tag ats-missing">${k}</span>`).join("");

    const addedHTML = ats.added_keywords.map(k =>
      `<span class="ats-tag ats-added">${k}</span>`).join("");

    return `
      <div class="ats-section">
        <h5 class="ats-title">📊 ATS Score Analysis</h5>

        <div class="ats-scores">
          <div class="ats-score-card">
            <div class="ats-circle" style="--score: ${beforeScore}; --color: #e74c3c;">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e0e0e0" stroke-width="10"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e74c3c" stroke-width="10"
                  stroke-dasharray="${beforeScore * 2.51} 251"
                  stroke-linecap="round"
                  transform="rotate(-90 50 50)"/>
              </svg>
              <span class="ats-circle-text">${beforeScore}%</span>
            </div>
            <p class="ats-label">Before Fix</p>
          </div>

          <div class="ats-arrow">→</div>

          <div class="ats-score-card">
            <div class="ats-circle" style="--score: ${afterScore}; --color: #27ae60;">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e0e0e0" stroke-width="10"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#27ae60" stroke-width="10"
                  stroke-dasharray="${afterScore * 2.51} 251"
                  stroke-linecap="round"
                  transform="rotate(-90 50 50)"/>
              </svg>
              <span class="ats-circle-text">${afterScore}%</span>
            </div>
            <p class="ats-label">After Fix</p>
          </div>
        </div>

        <div class="ats-match-bar-wrap">
          <span class="ats-match-label">Keyword Match</span>
          <div class="ats-match-bar">
            <div class="ats-match-fill" style="width: ${ats.keyword_match_percent}%"></div>
          </div>
          <span class="ats-match-percent">${ats.keyword_match_percent}%</span>
        </div>

        ${matchedHTML ? `<div class="ats-keyword-group"><p class="ats-kw-title">✅ Matched Keywords</p><div class="ats-tags">${matchedHTML}</div></div>` : ""}
        ${addedHTML ? `<div class="ats-keyword-group"><p class="ats-kw-title">🟢 Added by AI</p><div class="ats-tags">${addedHTML}</div></div>` : ""}
        
      </div>
    `;
  }

});




