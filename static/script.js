function createBubbles() {
    for (let i = 0; i < 15; i++) {
      const bubble = document.createElement('div');
      bubble.classList.add('floating-bubble');
      
      // Random size
      const size = Math.random() * 100 + 50;
      bubble.style.width = `${size}px`;
      bubble.style.height = `${size}px`;
      
      // Random position
      bubble.style.left = `${Math.random() * 100}%`;
      bubble.style.top = `${Math.random() * 100}%`;
      
      // Random animation duration and delay
      const duration = Math.random() * 10 + 10;
      const delay = Math.random() * 5;
      bubble.style.animationDuration = `${duration}s`;
      bubble.style.animationDelay = `${delay}s`;
      
      document.body.appendChild(bubble);
    }
  }

  // Set animation delay for form elements
  function setAnimationDelays() {
    const formSectionTitles = document.querySelectorAll('.form-section-title');
    formSectionTitles.forEach((title, index) => {
      title.style.animationDelay = `${0.2 * (index + 1)}s`;
    });
    
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
      group.style.animationDelay = `${0.2 * (index + 1)}s`;
    });
    
    const sliderContainers = document.querySelectorAll('.slider-container');
    sliderContainers.forEach((slider, index) => {
      slider.style.animationDelay = `${0.5 + 0.1 * index}s`;
    });
    
    const radioGroups = document.querySelectorAll('.radio-group');
    radioGroups.forEach((radio, index) => {
      radio.style.animationDelay = `${0.7 + 0.1 * index}s`;
    });
    
    const checkboxContainers = document.querySelectorAll('.checkbox-container');
    checkboxContainers.forEach((checkbox, index) => {
      checkbox.style.animationDelay = `${0.9 + 0.1 * index}s`;
    });
  }
  
  // Update slider value display
  function updateSliderValue(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(valueId);
    valueDisplay.textContent = slider.value;
    
    slider.oninput = function() {
      valueDisplay.textContent = this.value;
    }
  }

  window.onload = function() {
    createBubbles();
    setAnimationDelays();
    updateSliderValue('age-slider', 'age-value');
    updateSliderValue('period-length-slider', 'period-length-value');
    updateSliderValue('cycle-length-slider', 'cycle-length-value');
  };