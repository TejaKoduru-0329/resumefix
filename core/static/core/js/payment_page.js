document.addEventListener("DOMContentLoaded", () => {

    let selectedQty   = 5;
    let selectedPrice = 199;

    window.selectPlan = function (card, qty, price) {
        document.querySelectorAll(".plan-card").forEach((c, i) => {
            c.classList.remove("selected");
            const chk = document.getElementById("chk" + i);
            if (chk) chk.classList.remove("active");
        });
        card.classList.add("selected");
        const idx = [...document.querySelectorAll(".plan-card")].indexOf(card);
        const chk = document.getElementById("chk" + idx);
        if (chk) chk.classList.add("active");
        selectedQty   = qty;
        selectedPrice = price;
        const label = document.getElementById("payBtnLabel");
        if (label) label.textContent = `Pay ₹${price} — Get ${qty} Resume Credit${qty > 1 ? "s" : ""}`;
    };

    window.openModal = function () {
        document.getElementById("modalQty").textContent = selectedQty + " Resume Credit" + (selectedQty > 1 ? "s" : "");
        document.getElementById("modalPrice").textContent  = "₹" + selectedPrice;
        document.getElementById("modalBtnPrice").textContent = "₹" + selectedPrice;
        document.getElementById("successNum").textContent  = selectedQty;
        document.getElementById("modalForm").style.display       = "";
        document.getElementById("modalProcessing").style.display = "none";
        document.getElementById("modalSuccess").style.display    = "none";
        document.getElementById("payModal").classList.add("show");
    };

    window.closeModal = function () {
        document.getElementById("payModal").classList.remove("show");
    };

    window.handleOverlayClick = function (e) {
        if (e.target === document.getElementById("payModal")) closeModal();
    };

    window.pickMethod = function (btn) {
        document.querySelectorAll(".method-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
    };

    window.processPayment = function () {
        document.getElementById("modalForm").style.display       = "none";
        document.getElementById("modalProcessing").style.display = "";

        setTimeout(() => {
            document.getElementById("modalProcessing").style.display = "none";
            document.getElementById("modalSuccess").style.display    = "";
            launchConfetti();

            // Credits backend లో add చేయి
            fetch("/payments/add-credits/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrf()
                },
                body: JSON.stringify({ quantity: selectedQty })
            }).then(res => res.json())
              .then(data => {
                  console.log("Credits added:", data.credits);
              }).catch(err => console.error("Credit error:", err));

        }, 2000);
    };

    window.goToResume = function () {
        closeModal();
        window.location.href = "/upload_page/";
    };

    function launchConfetti() {
        const colors = ["#D000F7", "#24BAE3", "#00b894", "#fdcb6e", "#fd79a8"];
        for (let i = 0; i < 60; i++) {
            setTimeout(() => {
                const el = document.createElement("div");
                el.className = "confetti-piece";
                const size = 6 + Math.random() * 6;
                el.style.cssText = `
                    left: ${Math.random() * 100}vw;
                    top: -12px;
                    width: ${size}px;
                    height: ${size}px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    border-radius: ${Math.random() > 0.5 ? "50%" : "2px"};
                    animation-duration: ${1.4 + Math.random() * 0.8}s;
                `;
                document.body.appendChild(el);
                setTimeout(() => el.remove(), 2800);
            }, i * 30);
        }
    }

});

// CSRF token helper
function getCsrf() {
    let csrf = null;
    document.cookie.split(';').forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            csrf = cookie.substring('csrftoken='.length);
        }
    });
    return csrf;
}