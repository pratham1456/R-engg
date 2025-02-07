document.addEventListener('DOMContentLoaded', () => {
    const bugsBtn = document.getElementById('bugs-btn');
    const bugsContainer = document.getElementById('bugs');
    const searchClose = document.getElementById('search-close');


    if (bugsBtn) {
        bugsBtn.addEventListener('click', () => {
          bugsContainer.classList.add('show-bugs');
        });
      }
    
      if (searchClose) {
        searchClose.addEventListener('click', () => {
          bugsContainer.classList.remove('show-bugs');

        });
      }
});