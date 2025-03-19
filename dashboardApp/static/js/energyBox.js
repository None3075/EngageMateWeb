document.addEventListener('DOMContentLoaded', function() {
    const boxes = document.querySelectorAll('.energia-box');
    boxes.forEach(box => {
        const energy = parseFloat(box.dataset.energy);
        const hue = energy * 120 / 100;
        box.style.backgroundColor = `hsl(${hue}, 70%, 70%)`;
        box.style.color = 'black';
        box.style.padding = '5px';
        box.style.borderRadius = '4px';
        box.style.textAlign = 'center';
    });
});