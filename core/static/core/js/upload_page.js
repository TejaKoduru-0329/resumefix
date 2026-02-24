
document.addEventListener("DOMContentLoaded", () => {

  /* ========= ELEMENT REFERENCES ========= */

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

  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  /* ========= HELPERS ========= */

  function showError(msg) {
    formErrorText.innerText = msg;
    formError.style.display = "flex";
  }

  function hideError() {
    formError.style.display = "none";
  }

  /* ========= FILE UPLOAD UI ========= */

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

    // Upload animation
    uploadIconWrap.innerHTML = `<div class="spinner-border text-primary"></div>`;
    uploadStatus.innerText = "Uploading…";
    uploadSub.innerText = "";
    fileRow.style.display = "none";

    setTimeout(() => {
      uploadIconWrap.innerHTML =
        `<i class="fa-solid fa-cloud-arrow-up upload-icon"></i>`;
      uploadStatus.innerText = "Resume Uploaded";
      uploadSub.innerText = "";
      fileName.innerText = file.name;
      fileRow.style.display = "flex";
    }, 800);
  });

  /* ========= REMOVE FILE ========= */

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

  /* ========= FORM SUBMIT (AI CALL) ========= */

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    hideError();

    if (!fileInput.files.length || !jdTextarea.value.trim()) {
      showError("Please provide both a resume and a job description");
      return;
    }

    loading.style.display = "block";
    resultsSection.style.display = "none";

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

      loading.style.display = "none";

      if (!data.success) {
        showError(data.error || "AI failed. Please try again.");
        return;
      }

      // ✅ SET PREVIEW CONTENT
      beforePreview.innerText = data.before_text;
      // afterPreview.innerHTML = data.optimized_content.replace(/\n/g, "<br>");
      afterPreview.innerHTML = renderAIContent(data.optimized_content);

      // ✅ SHOW PREVIEW
      resultsSection.style.display = "block";

      // ✅ DOWNLOAD BUTTON
      const downloadBtn = document.getElementById("downloadBtn");
      if (downloadBtn) {
        downloadBtn.style.display = "inline-block";
        downloadBtn.href = `/download/${data.analysis_id}/`;
      }

      // Scroll to preview
      resultsSection.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
      loading.style.display = "none";
      showError("Server error. Please try again later.");
      console.error(err);
    }
  });

  jdTextarea.addEventListener("input", hideError);


  // function renderAIContent(text) {

  // // Fix heading naming issues
  // text = text
  //   .replace(/\bTECHNICAL SOFT SKILLS\b/g, "TECHNICAL SKILLS")
  //   .replace(/\bSOFT SOFT SKILLS\b/g, "SOFT SKILLS")
  //   .replace(/\bSKILLS\b/g, "SOFT SKILLS");

  // // Bold name (first line)
  // text = text.replace(/^(.+)$/m, "<strong>$1</strong>");

  // return text
  //   // Headings with underline only
  //   .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong><hr class='heading-line'>")

  //   // Bullet points
  //   .replace(/^[-*]\s+(.*)$/gm, "• $1")

  //   // Line breaks
  //   .replace(/\n/g, "<br>");
  // }


  //   function renderAIContent(text) {

  //   // Fix wrong headings
  //   text = text
  //     .replace(/\bTECHNICAL SOFT SKILLS\b/g, "TECHNICAL SKILLS")
  //     .replace(/\bSOFT SOFT SKILLS\b/g, "SOFT SKILLS");
  //   let currentSection = "";
  //   const lines = text.split("\n");
  //   let html = `<div class="resume-preview">`;

  //   lines.forEach((line, index) => {

  //     // Name (first line)
  //     if (index === 0) {
  //       html += `<div class="resume-name">${line}</div>`;
  //       return;
  //     }

  //     // Headings (**HEADING**)
  //     if (/^\*\*(.*?)\*\*$/.test(line)) {
  //       currentSection = line.replace(/\*\*/g, "");
  //       html += `
  //         <div class="resume-heading">${currentSection}</div>
  //         <hr class="heading-line">
  //       `;
  //       return;
  //     }

  //     // Education: college line
  //     if (line.includes("|") && line.match(/\d{4}/)) {
  //       html += `<div class="edu-entry"><div class="edu-college">${line}</div>`;
  //       return;
  //     }

  //     // if (line.includes("|") && line.match(/\d{4}/)) {
  //     //   html += `
  //     //     <div class="edu-entry">
  //     //       <div class="edu-college">
  //     //         ${line.split("|")[0].trim()}
  //     //       </div>
  //     //       <div class="edu-meta">
  //     //         ${line.split("|").slice(1).join("|").trim()}
  //     //       </div>
  //     //     </div>
  //     //   `;
  //     //   return;
  //     // }

  //     // Degree line
  //     if (line.toLowerCase().includes("cgpa") || line.toLowerCase().includes("percentage")) {
  //       html += `<div>${line}</div></div>`;
  //       return;
  //     }

  //     // Technical skills: key:value pairs
  //     if (line.includes(":")) {
  //       html += `<p><strong>${line.split(":")[0]}:</strong> ${line.split(":")[1]}</p>`;
  //       return;
  //     }

  //     // Bullet
  //     // if (line.startsWith("•") || line.startsWith("-")) {
  //     //   html += `<ul><li>${line.replace(/^[-•]\s*/, "")}</li></ul>`;
  //     //   return;
  //     // }

  //     // Project title Bold
  //     if (
  //       currentSection === "PROJECTS" && !line.startsWith("•") && line.trim() !== ""
  //     ) {
  //       html += `<p><strong>${line}</strong></p>`;
  //       return;
  //     }

  //     // Bullets with indent
  //     if (line.startsWith("•")) {
  //       html += `<ul class="resume-bullets"><li>${line.substring(1)}</li></ul>`;
  //       return;
  //     }

  //     // Normal paragraph
  //     if (line.trim()) {
  //       html += `<p>${line}</p>`;
  //     }
  //   });

  //   html += `</div>`;
  //   return html;
  //   }
  // });



  function renderAIContent(text) {
    let currentSection = "";
    const lines = text.split("\n");
    let html = `<div class="resume-preview">`;

    lines.forEach((line, index) => {

      // NAME (only first line bold, big)
      if (index === 0) {
        html += `<div class="resume-name">${line}</div>`;
        return;
      }

      // HEADINGS (**HEADING**)
      if (/^\*\*(.+)\*\*$/.test(line)) {
        currentSection = line.replace(/\*/g, "").trim();
        html += `
          <div class="resume-heading">${currentSection}</div>
          <hr class="heading-line">
        `;
        return;
      }

      // BULLETS (already normalized by Gemini to •)
      if (line.trim().startsWith("•")) {
        html += `
          <ul class="resume-bullets">
            <li>${line.replace(/^•\s*/, "")}</li>
          </ul>
        `;
        return;
      }

      // PROJECT TITLES (first non-bullet line inside PROJECTS)
      if (
        currentSection === "PROJECTS" &&
        line.trim() &&
        !line.startsWith("•")
      ) {
        html += `<p class="project-title">${line}</p>`;
        return;
      }

      // NORMAL TEXT
      if (line.trim()) {
        html += `<p>${line}</p>`;
      }
    });

    html += `</div>`;
    return html;
  }

  
});








