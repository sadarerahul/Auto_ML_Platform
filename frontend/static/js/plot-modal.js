document.addEventListener("DOMContentLoaded", () => {
  const modal = new bootstrap.Modal(document.getElementById('plotModal'));
  const modalFrame = document.getElementById('modalPlotFrame');

  document.querySelectorAll("iframe").forEach((frame) => {
    frame.style.cursor = "zoom-in";
    frame.addEventListener("click", () => {
      modalFrame.src = frame.src;
      modal.show();
    });
  });
});
