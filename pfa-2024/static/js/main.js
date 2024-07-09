
  const form = document.querySelector('form');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    if (emailInput.value.trim() === '' || passwordInput.value.trim() === '') {
      alert('Please fill in both email and password fields');
      return;
    }

    // If both fields are filled, submit the form
    form.submit();
  });