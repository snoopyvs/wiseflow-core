// gsap-animations.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sidebar State Management (FOUC handled in head script)
    const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    if (isCollapsed) {
        gsap.set('.nav-label, .logo-text', { opacity: 0, display: 'none' });
    }

    // 2. Add gsap-loaded class to body to release the CSS FOUC locks
    document.body.classList.add('gsap-loaded');

    // 3. Page Entrance Animation
    gsap.fromTo('main', 
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out', clearProps: 'all' }
    );

    gsap.fromTo('.nav-link', 
        { opacity: 0, x: -20 },
        { opacity: 1, x: 0, duration: 0.5, stagger: 0.05, ease: 'power3.out', clearProps: 'all' }
    );

    // 4. Sidebar Toggle Logic
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
                    duration: 0.1,
                    onComplete: () => {
                        gsap.set('.nav-label, .logo-text', { display: 'none' });
                    }
                });
                
                // Animate the toggle icon rotation
                gsap.to(toggleBtn.querySelector('.material-symbols-outlined'), {
                    rotation: 180,
                    duration: 0.15
                });

            } else {
                // Expanding
                document.documentElement.classList.remove('sidebar-collapsed');
                localStorage.setItem('sidebar_collapsed', 'false');
                
                // Animate text in
                gsap.set('.nav-label', { display: 'inline-block' });
                gsap.set('.logo-text', { display: 'flex' });
                gsap.to('.nav-label, .logo-text', {
                    opacity: 1,
                    duration: 0.15,
                    delay: 0.05 // Wait for width transition to start
                });

                // Animate the toggle icon rotation
                gsap.to(toggleBtn.querySelector('.material-symbols-outlined'), {
                    rotation: 0,
                    duration: 0.15
                });
            }
            
            // Map Leaflet resize fix if map exists
            if (typeof map !== 'undefined' && map !== null) {
                setTimeout(() => { map.invalidateSize(); }, 160);
            }
        });

        // Set initial rotation of toggle button
        if (isCollapsed) {
            gsap.set(toggleBtn.querySelector('.material-symbols-outlined'), { rotation: 180 });
        }
    }

    // 5. Page Exit Animation (Intercept Links)
    const transitionLinks = document.querySelectorAll('a.nav-link');
    transitionLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Ignore collapse button
            if (link.id === 'sidebar-toggle') return;

            const targetUrl = link.getAttribute('href');
            if (!targetUrl || targetUrl.startsWith('#') || link.getAttribute('target') === '_blank') return;
            
            // Ignore if clicking the active page
            if (window.location.pathname === targetUrl) {
                e.preventDefault();
                return;
            }
            
            e.preventDefault();
            
            gsap.to('main', {
                opacity: 0,
                y: -10,
                duration: 0.15,
                ease: 'power2.in',
                onComplete: () => {
                    window.location.href = targetUrl;
                }
            });
        });
    });
});
