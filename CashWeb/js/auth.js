// auth.js

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginTab = document.querySelector('[data-tab="login"]');
    const registerTab = document.querySelector('[data-tab="register"]');

    if (loginTab && registerTab) {
        loginTab.addEventListener('click', () => {
            document.getElementById('login-tab').classList.remove('hidden');
            document.getElementById('register-tab').classList.add('hidden');
            loginTab.classList.add('active');
            registerTab.classList.remove('active');
        });

        registerTab.addEventListener('click', () => {
            document.getElementById('login-tab').classList.add('hidden');
            document.getElementById('register-tab').classList.remove('hidden');
            registerTab.classList.add('active');
            loginTab.classList.remove('active');
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            alert('Logged in successfully (fake login)');
            window.location.href = 'index.html';
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();
            alert('Account created (fake registration)');
            window.location.href = 'index.html';
        });
    }
});
