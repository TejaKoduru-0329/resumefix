document.addEventListener("DOMContentLoaded", () => {

  /* ========= ELEMENT REFERENCES ========= */

  const form = document.querySelector("form"); // ✅ FORM
  const fileInput = document.getElementById("resumeInput");

  const uploadIconWrap = document.getElementById("uploadIconWrap");
  const uploadStatus = document.getElementById("uploadStatus");
  const uploadSub = document.getElementById("uploadSub");

  const fileRow = document.getElementById("fileRow");
  const fileName = document.getElementById("fileName");
  const errorText = document.getElementById("fileError");

  const loading = document.getElementById("loading");
  const jdTextarea = document.querySelector(".jd-box textarea");

  const formError = document.getElementById("formError");
  const formErrorText = document.getElementById("formErrorText");

  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  /* ========= FORM SUBMIT (VALIDATION + LOADER) ========= */

  form.addEventListener("submit", function (e) {

    // ❌ Resume missing
    if (!fileInput.files.length) {
      e.preventDefault();
      showError("Please upload your resume");
      return;
    }

    // ❌ JD missing
    if (!jdTextarea.value.trim()) {
      e.preventDefault();
      showError("Please paste the job description");
      return;
    }

    // ✅ All good
    hideError();

    // show loader (Django will reload page)
    loading.style.display = "block";
  });

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

    // uploading UI
    uploadIconWrap.innerHTML =
      `<div class="spinner-border text-primary"></div>`;
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

  /* ========= ERROR HELPERS ========= */

  function showError(msg) {
    formErrorText.innerText = msg;
    formError.style.display = "flex";
  }

  function hideError() {
    formError.style.display = "none";
  }

  jdTextarea.addEventListener("input", hideError);

});






