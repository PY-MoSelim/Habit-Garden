/* ============================================================
   PATH: habit-garden/app/static/js/garden.js
   PURPOSE: Garden interactions — watering, delete modal,
            achievement toasts, auto-dismiss flashes
   ============================================================ */

/* ── Auto-dismiss flash messages after 4 seconds ── */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach(flash => {
    setTimeout(() => {
      flash.style.transition = "opacity .4s ease, transform .4s ease";
      flash.style.opacity    = "0";
      flash.style.transform  = "translateX(120%)";
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });
});

/* ── Complete (water) a habit via AJAX ── */
async function completeHabit(habitId, btn) {
  btn.disabled    = true;
  btn.textContent = "💧 Watering…";

  try {
    const response = await fetch(`${COMPLETE_URL}${habitId}/complete`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ note: "" }),
    });

    const data = await response.json();

    if (data.status === "success" || data.status === "already_done") {
      btn.textContent = "✓ Watered";
      btn.className   = "btn btn-watered";
      btn.disabled    = true;

      const card = btn.closest(".plant-card");
      if (card) {
        card.classList.add("done");

        if (!card.querySelector(".done-badge")) {
          const badge = document.createElement("div");
          badge.className   = "done-badge";
          badge.textContent = "✓";
          card.querySelector(".plant-visual").appendChild(badge);
        }

        const streakEl = card.querySelector(".streak-count");
        if (streakEl && data.new_streak !== undefined) {
          streakEl.textContent = `${data.new_streak} day streak`;
        }

        if (data.new_stage !== undefined) {
          const dots = card.querySelectorAll(".stage-dot");
          dots.forEach((dot, i) => dot.classList.toggle("filled", i < data.new_stage));
          card.dataset.stage = data.new_stage;
        }

        const plantEmoji = card.querySelector(".plant-emoji");
        if (plantEmoji) {
          plantEmoji.style.animation = "none";
          plantEmoji.style.transform = "scale(1.4)";
          setTimeout(() => {
            plantEmoji.style.transform = "";
            plantEmoji.style.animation = "";
          }, 300);
        }
      }

      if (data.achievements && data.achievements.length > 0) {
        data.achievements.forEach((ach, i) => {
          setTimeout(() => showAchievementToast(ach.icon, ach.title), i * 600);
        });
      }

      updateDoneTodayStat();
    }

  } catch (err) {
    console.error("Error completing habit:", err);
    btn.disabled    = false;
    btn.textContent = "💧 Water";
  }
}

/* ── Update "Done Today" counter ── */
function updateDoneTodayStat() {
  const wateredButtons = document.querySelectorAll(".btn-watered").length;
  const statValue = document.querySelector(".stat-item:first-child .stat-value");
  if (statValue) {
    statValue.textContent = wateredButtons;
    statValue.style.transform = "scale(1.3)";
    setTimeout(() => { statValue.style.transform = ""; }, 300);
  }
}

/* ── Delete confirmation modal ── */
function confirmDelete(habitId, habitName) {
  const modal = document.getElementById("delete-modal");
  const text  = document.getElementById("delete-modal-text");
  const form  = document.getElementById("delete-form");

  text.textContent = `"${habitName}" will be permanently removed from your garden.`;
  form.action      = `${DELETE_URL}${habitId}/delete`;
  modal.style.display = "flex";
  modal.onclick = (e) => { if (e.target === modal) closeModal(); };
}

function closeModal() {
  const modal = document.getElementById("delete-modal");
  if (modal) modal.style.display = "none";
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

/* ── Achievement toast ── */
function showAchievementToast(icon, title) {
  const container = document.getElementById("achievement-toasts");
  if (!container) return;

  const toast       = document.createElement("div");
  toast.className   = "ach-toast";
  toast.textContent = `${icon} Achievement Unlocked: ${title}!`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity .4s ease, transform .4s ease";
    toast.style.opacity    = "0";
    toast.style.transform  = "translateY(20px)";
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

/* ── Staggered card entrance animation ── */
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".plant-card");
  cards.forEach((card, i) => {
    card.style.opacity   = "0";
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "opacity .4s ease, transform .4s ease";
      card.style.opacity    = "1";
      card.style.transform  = "translateY(0)";
    }, i * 80);
  });
});