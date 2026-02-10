document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Função para criar explosão de arco-íris
  function createRainbowBlast(x, y) {
    const rainbowEmojis = ['🌈', '✨', '⭐', '💫', '🦄', '🌟', '💖', '💜', '💙', '💚', '💛'];
    // Ajustar número de blasts baseado no tamanho da tela
    const isMobile = window.innerWidth <= 768;
    const numberOfBlasts = isMobile ? 10 : 15;
    
    for (let i = 0; i < numberOfBlasts; i++) {
      const blast = document.createElement('div');
      blast.className = 'rainbow-blast';
      blast.textContent = rainbowEmojis[Math.floor(Math.random() * rainbowEmojis.length)];
      blast.style.left = x + 'px';
      blast.style.top = y + 'px';
      
      // Adicionar variação na animação
      const angle = (i / numberOfBlasts) * 360;
      const distance = isMobile ? 50 : 100 + Math.random() * 100;
      blast.style.setProperty('--angle', angle + 'deg');
      blast.style.animationDelay = (i * 0.05) + 's';
      
      document.body.appendChild(blast);
      
      // Remover elemento após animação
      setTimeout(() => {
        blast.remove();
      }, 1000);
    }
  }

  // Adicionar evento de clique em todos os botões
  document.addEventListener('click', (event) => {
    if (event.target.tagName === 'BUTTON') {
      createRainbowBlast(event.clientX, event.clientY);
    }
  });

  // Adicionar suporte para touch em dispositivos móveis
  document.addEventListener('touchstart', (event) => {
    if (event.target.tagName === 'BUTTON' && event.touches.length > 0) {
      const touch = event.touches[0];
      createRainbowBlast(touch.clientX, touch.clientY);
    }
  });

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            ${details.participants.length > 0 
              ? `<ul class="participants-list">${details.participants.map(p => `<li><span>${p}</span><span class="delete-icon" data-email="${p}" data-activity="${name}" title="Remove participant">🗑️</span></li>`).join('')}</ul>`
              : '<p class="no-participants">No participants yet</p>'}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh activities list
        await fetchActivities();
        
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle participant deletion
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-icon")) {
      const email = event.target.dataset.email;
      const activity = event.target.dataset.activity;

      if (confirm(`Are you sure you want to remove ${email} from ${activity}?`)) {
        try {
          const response = await fetch(
            `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
            {
              method: "DELETE",
            }
          );

          const result = await response.json();

          if (response.ok) {
            // Refresh activities list
            await fetchActivities();
            
            messageDiv.textContent = result.message;
            messageDiv.className = "success";
            messageDiv.classList.remove("hidden");

            // Hide message after 5 seconds
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);
          } else {
            messageDiv.textContent = result.detail || "Failed to unregister";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
          }
        } catch (error) {
          messageDiv.textContent = "Failed to unregister. Please try again.";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
          console.error("Error unregistering:", error);
        }
      }
    }
  });

  // Initialize app
  fetchActivities();
});
