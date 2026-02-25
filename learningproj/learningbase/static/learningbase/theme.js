// static/js/theme.js - минимальный вариант
(function() {
    'use strict';
    
    // Функция изменения иконки
    function updateThemeIcon(theme) {
        const iconMap = {
            'light': '#sun-fill',
            'dark': '#moon-stars-fill',
            'auto': '#circle-half'
        };
        
        const themeIcon = document.querySelector('#themeSwitcher svg use');
        if (themeIcon && iconMap[theme]) {
            themeIcon.setAttribute('href', iconMap[theme]);
        }
    }
    
    // При загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        // Загружаем сохраненную тему
        let theme = localStorage.getItem('theme');
        if (!theme) {
            theme = 'dark';
            localStorage.setItem('theme', theme);
        }
        
        // Устанавливаем тему и иконку
        document.documentElement.setAttribute('data-bs-theme', theme);
        updateThemeIcon(theme);
        
        // Обработчик для кнопок темы
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const theme = this.getAttribute('data-theme');
                
                // Устанавливаем тему
                document.documentElement.setAttribute('data-bs-theme', theme);
                localStorage.setItem('theme', theme);
                
                // Меняем иконку
                updateThemeIcon(theme);
                
                // Закрываем dropdown
                const dropdown = bootstrap.Dropdown.getInstance(
                    document.getElementById('themeSwitcher')
                );
                if (dropdown) dropdown.hide();
            });
        });
    });
})();