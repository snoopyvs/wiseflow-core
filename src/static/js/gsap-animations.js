// gsap-animations.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sidebar State Management (FOUC is already handled in head script)
    const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    if (isCollapsed) {
        // Instantly apply state to nav labels and logo text to prevent flicker
        gsap.set('.nav-label, .logo-text', { opacity: 0, display: 'none' });
    }

    // 2. Page Entrance Animation
    // Fade in the main content (which is initially opacity-0 via CSS)
    gsap.to('main', {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: 'power3.out',
        clearProps: 'transform'
    });

    // Animate sidebar links staggering in
    gsap.to('.nav-link', {
        opacity: 1,
        x: 0,
        duration: 0.5,
        stagger: 0.05,
        ease: 'power3.out',
        clearProps: 'transform'
    });

    // 3. Sidebar Toggle Logic
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const willCollapse = !document.documentElement.classList.contains('sidebar-collapsed');
            
            if (willCollapse) {
                // Collapsing
                document.documentElement.classList.add('sidebar-collapsed');
                localStorage.setItem('sidebar_collapsed', 'true');
                
                // Animate text out
                gsap.to('.nav-label, .logo-text', {
                    opacity: 0,
                    duration: 0.2,
                    onComplete: () => {
                        gsap.set('.nav-label, .logo-text', { display: 'none' });
                    }
                });
                
                // Animate the toggle icon rotation
                gsap.to(toggleBtn.querySelector('.material-symbols-outlined'), {
                    rotation: 180,
                    duration: 0.3
                });

            } else {
                // Expanding
                document.documentElement.classList.remove('sidebar-collapsed');
                localStorage.setItem('sidebar_collapsed', 'false');
                
                // Animate text in
                gsap.set('.nav-label, .logo-text', { display: 'inline-block' });
                gsap.to('.nav-label, .logo-text', {
                    opacity: 1,
                    duration: 0.3,
                    delay: 0.1 // Wait for width transition to start
                });

                // Animate the toggle icon rotation
                gsap.to(toggleBtn.querySelector('.material-symbols-outlined'), {
                    rotation: 0,
                    duration: 0.3
                });
            }
            
            // Map Leaflet resize fix if map exists
            if (typeof map !== 'undefined' && map !== null) {
                setTimeout(() => { map.invalidateSize(); }, 350); // wait for css transition
            }
        });

        // Set initial rotation of toggle button
        if (isCollapsed) {
            gsap.set(toggleBtn.querySelector('.material-symbols-outlined'), { rotation: 180 });
        }
    }

    // 4. Hover Animations for Nav Links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        // Only apply hover animation if it's not the active link
        if (!link.classList.contains('bg-surface-container-highest')) {
            link.addEventListener('mouseenter', () => {
                gsap.to(link, { 
                    x: 5, 
                    duration: 0.2, 
                    ease: "power2.out" 
                });
            });
            link.addEventListener('mouseleave', () => {
                gsap.to(link, { 
                    x: 0, 
                    duration: 0.2, 
                    ease: "power2.out" 
                });
            });
        }
    });

    // 5. Page Exit Animation (Intercept Links)
    const transitionLinks = document.querySelectorAll('a.nav-link');
    transitionLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetUrl = link.getAttribute('href');
            // If it's a new tab, internal anchor, or the same page, ignore exit animation
            if (targetUrl.startsWith('#') || link.getAttribute('target') === '_blank') return;
            
            e.preventDefault();
            
            // GSAP exit animation
            gsap.to('main', {
                opacity: 0,
                y: -20,
                duration: 0.3,
                ease: 'power3.in',
                onComplete: () => {
                    window.location.href = targetUrl;
                }
            });
        });
    });
});
