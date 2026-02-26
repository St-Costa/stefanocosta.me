const $cards = document.querySelectorAll('.card');

$cards.forEach(($card) => {
  let bounds;

  function rotateToMouse(e) {
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    const leftX = mouseX - bounds.x;
    const topY = mouseY - bounds.y;
    const center = {
      x: leftX - bounds.width / 2,
      y: topY - bounds.height / 2
    };
    const distance = Math.sqrt(center.x ** 2 + center.y ** 2);

    $card.style.transform = `
      scale3d(1.07, 1.07, 1.07)
      rotate3d(
        ${center.y / 50},
        ${-center.x / 50},
        0,
        ${Math.log(distance) * 5}deg
      )
    `;

    const $glow = $card.querySelector('.glow');
    if ($glow) {
      $glow.style.backgroundImage = `
        radial-gradient(
          circle at
          ${center.x * 2 + bounds.width / 2}px
          ${center.y * 2 + bounds.height / 2}px,
          #ffffff55,
          #0000000f
        )
      `;
    }
  }

  function resetCard() {
    $card.removeEventListener('mousemove', rotateToMouse);
    $card.style.transform = '';
    const $glow = $card.querySelector('.glow');
    if ($glow) $glow.style.backgroundImage = '';
  }

  // Mouse
  $card.addEventListener('mouseenter', () => {
    bounds = $card.getBoundingClientRect();
    $card.addEventListener('mousemove', rotateToMouse);
  });
  $card.addEventListener('mouseleave', resetCard);

  // Touch
  $card.addEventListener('touchstart', (e) => {
    bounds = $card.getBoundingClientRect();
    const touch = e.touches[0];
    rotateToMouse({ clientX: touch.clientX, clientY: touch.clientY });
  }, { passive: true });

  $card.addEventListener('touchmove', (e) => {
    const touch = e.touches[0];
    rotateToMouse({ clientX: touch.clientX, clientY: touch.clientY });
  }, { passive: true });

  $card.addEventListener('touchend', resetCard);

  // Keyboard (focus/blur)
  $card.setAttribute('tabindex', '0');
  $card.addEventListener('focus', () => {
    $card.style.transform = 'scale3d(1.07, 1.07, 1.07)';
  });
  $card.addEventListener('blur', resetCard);
});
