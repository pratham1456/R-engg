function checkMachineStatus() {
  fetch('/check_machine_status')
    .then(response => response.json())
    .then(data => {
      const statusElement = document.getElementById("machine-status");
      if (data.status === "online") {
        statusElement.innerHTML = "Online";
        statusElement.style.color = "#45a049";
      } else {
        statusElement.innerHTML = "Offline";
        statusElement.style.color = "#f44336";
      }
    })
    .catch(error => {
      console.log("Error checking machine status.");
      console.log(error);
    });
}

// Auto-check status when the page loads
window.onload = checkMachineStatus;

// Auto-refresh status every 5 seconds
setInterval(checkMachineStatus, 5000);

document.addEventListener("DOMContentLoaded", () => {
  // Prevent --Select-- option from being selected
  const relaySelect = document.getElementById("relay-type");
  const startButton = document.querySelector(".start-btn");
  const stopButton = document.querySelector(".stop-btn");

  function showAlert(event) {
    if (relaySelect.value === "select") {
      event.preventDefault(); // Prevent button action
      alert("Please select a valid Relay Type before proceeding!");
    } else {
      console.log(event.target.innerText + " button clicked!"); // Debugging log
    }
  }

  // Add event listeners for button clicks
  startButton.addEventListener("click", showAlert);
  stopButton.addEventListener("click", showAlert);


  const bugsBtn = document.getElementById("bugs-btn");
  const bugsContainer = document.getElementById("bugs");
  const searchClose = document.getElementById("search-close");

  if (bugsBtn && bugsContainer) {
    bugsBtn.addEventListener("click", () => {
      bugsContainer.classList.toggle("show-bugs");
    });
  }

  if (searchClose && bugsContainer) {
    searchClose.addEventListener("click", () => {
      bugsContainer.classList.remove("show-bugs");
    });
  }

  function makeDraggable(wrapperSelector, headerSelector) {
    const wrapper = document.querySelector(wrapperSelector);
    const header = wrapper?.querySelector(headerSelector);
    if (!wrapper || !header) return;

    let offsetX = 0,
      offsetY = 0,
      isDragging = false;

    header.addEventListener("mousedown", (e) => {
      isDragging = true;
      offsetX = e.clientX - wrapper.offsetLeft;
      offsetY = e.clientY - wrapper.offsetTop;
      header.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      wrapper.style.left = `${e.clientX - offsetX}px`;
      wrapper.style.top = `${e.clientY - offsetY}px`;
    });

    document.addEventListener("mouseup", () => {
      isDragging = false;
      header.style.cursor = "grab";
    });
  }

  makeDraggable(".st1-wrapper", ".head-st1");
  makeDraggable(".st2-wrapper", ".head-st2");

  function setupToggle(wrapperSelector, openBtnSelector, closeBtnSelector) {
    const wrapper = document.querySelector(wrapperSelector);
    const openBtn = document.querySelector(openBtnSelector);
    const closeBtn = document.querySelector(closeBtnSelector);

    if (openBtn) {
      openBtn.addEventListener("click", () => {
        wrapper?.classList.add("show");
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        wrapper?.classList.remove("show");
      });
    }
  }

  setupToggle(".st1-wrapper", ".st1-open-btn", ".st1-close-btn");
  setupToggle(".st2-wrapper", ".st2-open-btn", ".st2-close-btn");
});

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;

  // Hide all tab content sections
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
    tabcontent[i].classList.remove("active");
  }

  // Remove 'active' class from all tab buttons
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }

  // Show the selected tab content
  document.getElementById(tabName).style.display = "flex";
  document.getElementById(tabName).classList.add("active");

  // Add 'active' class to the clicked button
  evt.currentTarget.classList.add("active");
}

// Automatically activate the first tab on page load
document.addEventListener("DOMContentLoaded", function () {
  document.querySelector(".tablinks").click();
});
