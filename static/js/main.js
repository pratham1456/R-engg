document.addEventListener("DOMContentLoaded", () => {
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

    let offsetX = 0, offsetY = 0, isDragging = false;

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
