document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    // Update slider values
    document.getElementById('age-slider').addEventListener('input', function() {
        document.getElementById('age-value').textContent = this.value;
    });
    
    document.getElementById('cycle-length-slider').addEventListener('input', function() {
        document.getElementById('cycle-length-value').textContent = this.value;
    });
    
    document.getElementById('period-length-slider').addEventListener('input', function() {
        document.getElementById('period-length-value').textContent = this.value;
    });
    
    // Form validation
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value) {
                isValid = false;
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Please fill in all required fields');
        }
    });
});