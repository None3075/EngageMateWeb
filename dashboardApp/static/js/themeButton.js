
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', currentTheme);
    themeIcon.classList.toggle('fa-sun', currentTheme === 'light');
    themeIcon.classList.toggle('fa-moon', currentTheme === 'dark');
    toggleButton.addEventListener('click', function() {
        const newTheme = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-bs-theme', newTheme);
        themeIcon.classList.toggle('fa-sun', newTheme === 'light');
        themeIcon.classList.toggle('fa-moon', newTheme === 'dark');
        localStorage.setItem('theme', newTheme);
    });
});