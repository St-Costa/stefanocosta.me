document.addEventListener("DOMContentLoaded", function () {
  const slideshows = document.querySelectorAll(".slideshow-container");

  slideshows.forEach((container) => {
    let slideIndex = 0;

    const slides = container.querySelectorAll(".mySlides");
    const dots = container.querySelectorAll(".dot");
    const caption = container.querySelector(".caption");
    const prev = container.querySelector(".prev");
    const next = container.querySelector(".next");

    function showSlide(n) {
      slideIndex = (n + slides.length) % slides.length;

      slides.forEach((slide, i) => {
        slide.style.display = i === slideIndex ? "block" : "none";
      });

      dots.forEach((dot, i) => {
        dot.className = dot.className.replace(" active", "");
        if (i === slideIndex) dot.className += " active";
      });

      const img = slides[slideIndex].querySelector("img");
      caption.textContent = img ? img.alt : "";
    }

    // Click events
    prev.addEventListener("click", () => showSlide(slideIndex - 1));
    next.addEventListener("click", () => showSlide(slideIndex + 1));

    // Keyboard events: Space activates the focused arrow; arrow keys navigate globally within container
    function handleKeydown(e) {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        if (document.activeElement === prev) showSlide(slideIndex - 1);
        if (document.activeElement === next) showSlide(slideIndex + 1);
      }
    }
    prev.addEventListener("keydown", handleKeydown);
    next.addEventListener("keydown", handleKeydown);

    // Inizializza slideshow
    showSlide(0);
  });
});
