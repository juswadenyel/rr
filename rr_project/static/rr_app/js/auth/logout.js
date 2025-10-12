document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        userProfile: document.getElementById('userProfile'),
        profileDropdown: document.getElementById('profileDropdown'),
        logoutBtn: document.getElementById('logoutBtn'),
        userRoleBadge: document.getElementById('userRoleBadge')
    };

    const setupEventListeners = () => {

        elements.userProfile.addEventListener('click', (e) => {
            e.stopPropagation();
            elements.profileDropdown.classList.toggle('active');
        });

        document.addEventListener('click', (e) => {
            if (!elements.profileDropdown.contains(e.target) && 
                !elements.userProfile.contains(e.target)) {
                elements.profileDropdown.classList.remove('active');
            }
        });

        elements.profileDropdown.addEventListener('click', (e) => e.stopPropagation());

        elements.logoutBtn.addEventListener('click', handleLogout);
    };

    const handleLogout = () => {
        window.MessageBox.showConfirm('Are you sure you want to logout?', () => {
            window.ApiCaller.auth.signOut(() => window.MessageBox.hide());
        });
    };

    setupEventListeners();
});
