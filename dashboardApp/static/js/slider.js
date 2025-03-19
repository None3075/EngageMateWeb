document.addEventListener('DOMContentLoaded', function() {
  let slider = document.getElementById('id_energia');
  if (!slider) {
    slider = document.querySelector('input[type="range"]');
  }
  
  if (slider) {
    let display = document.getElementById(slider.id + '-val');
    if (!display) {
      const span = document.createElement('span');
      span.id = slider.id + '-val';
      slider.parentNode.insertBefore(span, slider.nextSibling);
      display = span;
    }
    
    const updateSlider = () => {
      let min = slider.min ? slider.min : 0;
      let max = slider.max ? slider.max : 100;
      let value = slider.value;
      let percentage = ((value - min) * 100) / (max - min);

      // if percentage is 0 return red
      if (percentage === 0) {
        percentage = 1;
      }
      
      let hue = (percentage * 120) / 100;
      let color = `hsl(${hue}, 70%, 60%)`;
      
      slider.style.backgroundImage = `linear-gradient(to right, ${color}, ${color})`;
      slider.style.backgroundSize = percentage + '% 100%';
      display.textContent = Math.round(percentage) + '%';
    };
    
    slider.addEventListener('input', updateSlider);
    updateSlider();
  }
});