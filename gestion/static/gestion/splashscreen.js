// Splash Screen Logic
(function() {
    const splash = document.getElementById('splash-screen');
    if (!splash) return;
    const curtainLeft = splash.querySelector('.curtain-left');
    const curtainRight = splash.querySelector('.curtain-right');
    const logo = splash.querySelector('.promesa-logo');
    const dots = splash.querySelectorAll('.dot');
    const particles = splash.querySelectorAll('.particle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    function getTheme() {
        const theme = localStorage.getItem('theme');
        if (theme === 'dark' || theme === 'light') return theme;
        return prefersDark ? 'dark' : 'light';
    }
    function setThemeClass() {
        const theme = getTheme();
        splash.classList.remove('splash-light', 'splash-dark');
        splash.classList.add(theme === 'dark' ? 'splash-dark' : 'splash-light');
        [curtainLeft, curtainRight].forEach(curtain => {
            curtain.classList.remove('curtain-light', 'curtain-dark');
            curtain.classList.add(theme === 'dark' ? 'curtain-dark' : 'curtain-light');
        });
    }
    setThemeClass();
    window.addEventListener('storage', setThemeClass);
    // Bloquear scroll
    document.body.classList.add('splash-active');
    // Animación de entrada
    logo.style.transform = 'scale(0.3) rotate(-15deg)';
    logo.style.opacity = '0';
    setTimeout(() => {
        logo.style.transition = 'all 0.8s cubic-bezier(0.77,0,0.18,1)';
        logo.style.transform = 'scale(1) rotate(0deg)';
        logo.style.opacity = '1';
    }, 200);
    // Animación cortinas
    setTimeout(() => {
        curtainLeft.style.transform = 'translateX(-100%)';
        curtainRight.style.transform = 'translateX(100%)';
    }, 900);
    // Animación partículas (rebote sutil)
    particles.forEach((p, i) => {
        p.animate([
            { transform: 'scale(1) translateY(0)' },
            { transform: 'scale(1.2) translateY(-10px)' },
            { transform: 'scale(1) translateY(0)' }
        ], {
            duration: 1800 + i*120,
            iterations: Infinity,
            direction: 'alternate',
            easing: 'ease-in-out',
            delay: i*200
        });
    });
    // Fade out y quitar splash
    setTimeout(() => {
        splash.classList.add('fade-out');
        document.body.classList.remove('splash-active');
        setTimeout(() => {
            splash.classList.add('splash-hidden');
        }, 600);
    }, 2200);
})(); 