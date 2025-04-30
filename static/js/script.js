const signUpButton=document.getElementById('signUpButton');
const signInButton=document.getElementById('signInButton');
const signInForm=document.getElementById('signIn');
const signUpForm=document.getElementById('signup');

signUpButton.addEventListener('click',function(){
    signInForm.style.display="none";
    signUpForm.style.display="block";
})
signInButton.addEventListener('click', function(){
    signInForm.style.display="block";
    signUpForm.style.display="none";
})
// const signUpButton = document.getElementById('signUpButton');
// const signInButton = document.getElementById('signInButton');
// const signInForm = document.getElementById('signIn');
// const signUpForm = document.getElementById('signup');

// // Toggle between sign-in and sign-up forms
// signUpButton.addEventListener('click', function(){
//     signInForm.style.display = "none";
//     signUpForm.style.display = "block";
// });

// signInButton.addEventListener('click', function(){
//     signInForm.style.display = "block";
//     signUpForm.style.display = "none";
// });

// // Check auth status on page load
// document.addEventListener('DOMContentLoaded', function() {
//     checkAuthStatus();
// });

// // Periodically check auth status (optional)
// setInterval(checkAuthStatus, 30000); // Check every 30 seconds

// function checkAuthStatus() {
//     fetch('/check-auth', {
//         credentials: 'include' // Important for session cookies
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.authenticated) {
//             // If authenticated and on auth page, redirect to feature
//             if (window.location.pathname.endsWith('/auth')) {
//                 window.location.href = '/feature';
//             }
//         } else {
//             // If not authenticated and not on auth page, redirect to auth
//             if (!window.location.pathname.endsWith('/auth')) {
//                 window.location.href = '/auth';
//             }
//         }
//     })
//     .catch(error => {
//         console.error('Error checking auth:', error);
//         // Only redirect to auth if we're not already there
//         if (!window.location.pathname.endsWith('/auth')) {
//             window.location.href = '/auth';
//         }
//     });
// }