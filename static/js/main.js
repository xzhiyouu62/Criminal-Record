// 臺北市自行車竊盜點位查詢系統 - 腳本

document.addEventListener('DOMContentLoaded', function() {
    // 輸入框聚焦效果
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            const menuItem = this.closest('.menu-item');
            if (menuItem) {
                menuItem.style.transform = 'translateY(-4px) scale(1.02)';
                menuItem.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15), 0 8px 16px rgba(79, 70, 229, 0.2)';
            }
        });
        
        input.addEventListener('blur', function() {
            const menuItem = this.closest('.menu-item');
            if (menuItem) {
                menuItem.style.transform = 'translateY(0) scale(1)';
                menuItem.style.boxShadow = '';
            }
        });
    });

    // 表單提交處理
    const forms = document.querySelectorAll('form');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = e.target.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.classList.add('button-loading');
                
                setTimeout(() => {
                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                        loadingOverlay.style.animation = 'fadeIn 0.3s ease-out';
                    }
                }, 100);
            }
        });
    });

    // 按鈕點擊效果
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = '';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // 滾動視差效果
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.floating-circle');
        
        parallaxElements.forEach((element, index) => {
            const speed = 0.1 + (index * 0.05);
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });

    // 頁面載入動畫
    const animatedElements = document.querySelectorAll('.menu-item');
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
});

function validateInput(inputId) {
    const inputElement = document.getElementById(inputId);
    if (!inputElement) return true;
    
    const inputValue = inputElement.value.trim();
    
    if (inputValue === "" || inputValue === null) {
        alert("請填寫必要的輸入欄位");
        inputElement.focus();
        
        inputElement.style.borderColor = '#ef4444';
        inputElement.style.boxShadow = '0 0 0 4px rgba(239, 68, 68, 0.1)';
        
        setTimeout(() => {
            inputElement.style.borderColor = '';
            inputElement.style.boxShadow = '';
        }, 3000);
        
        return false;
    }
    return true;
}
