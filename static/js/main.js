document.addEventListener("DOMContentLoaded", () => {
  const bugsBtn = document.getElementById("bugs-btn");
  const bugsContainer = document.getElementById("bugs");
  const searchClose = document.getElementById("search-close");

  if (bugsBtn) {
    bugsBtn.addEventListener("click", () => {
      if (bugsContainer.classList.contains("show-bugs")) {
        bugsContainer.classList.remove("show-bugs");
      } else {
        bugsContainer.classList.add("show-bugs");
      }
    });
  }

  if (searchClose) {
    searchClose.addEventListener("click", () => {
      bugsContainer.classList.remove("show-bugs");
    });
  }


  const wrapper = document.querySelector(".st1-wrapper"),
    header = wrapper.querySelector(".head"),
    openBtn = document.querySelector(".st1-open-btn"),
    closeBtn = document.querySelector(".st1-close-btn");

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

  openBtn.addEventListener("click", () => {
    wrapper.classList.add("show");
  });

  closeBtn.addEventListener("click", () => {
    wrapper.classList.remove("show");
  });
});


