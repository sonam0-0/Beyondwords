
// import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
// import { getAuth, onAuthStateChanged, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { 
    getAuth, 
    onAuthStateChanged, 
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    deleteUser
} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
const firebaseConfig = {
  apiKey: "AIzaSyCqRzCp699fXrKP9Kk6bud_k7hvTYHEGXw",
  authDomain: "login-page-c697a.firebaseapp.com",
  projectId: "login-page-c697a",
  storageBucket: "login-page-c697a.appspot.com",
  messagingSenderId: "539007861058",
  appId: "1:539007861058:web:3dde526996102eb3f948db",
  measurementId: "G-75DDR1YBQH"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Track if login was explicit
let isExplicitLogin = false;

// DOM elements
const signInForm = document.getElementById('signInForm');
const signUpForm = document.getElementById('signUpForm');
const authMessage = document.getElementById('authMessage');
const loadingIndicator = document.getElementById('loading');
const authContainer = document.getElementById('authContainer');

// Show auth form after checking initial state
setTimeout(() => {
  if (loadingIndicator) loadingIndicator.style.display = 'none';
  if (authContainer) authContainer.style.display = 'block';
}, 500);

// Sign-In Functionality
if (signInForm) {
  signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
      showMessage('Please enter both email and password', 'authMessage');
      return;
    }

    try {
      isExplicitLogin = true;
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      
      const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ token })
      });
      
      const data = await response.json();
      if (data.success) {
        window.location.href = '/feature';
      } else {
        showMessage(data.error || 'Login failed', 'authMessage');
        isExplicitLogin = false;
      }
    } catch (error) {
      showMessage(getFirebaseErrorMessage(error), 'authMessage');
      isExplicitLogin = false;
    }
  });
}

if (signUpForm) {
  signUpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('rEmail').value;
    const password = document.getElementById('rPassword').value;
    const firstName = document.getElementById('fName').value;
    const lastName = document.getElementById('lName').value;

    if (!email || !password || !firstName || !lastName) {
      showMessage('All fields are required', 'authMessage');
      return;
    }

    try {
      // First create user in Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      
      // Then register with backend
      const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          token,
          firstName,
          lastName
        })
      });
      
      const data = await response.json();
      if (data.success) {
        isExplicitLogin = true;
        window.location.href = '/feature';
      } else {
        showMessage(data.error || 'Registration failed', 'authMessage');
        // Delete the Firebase user if backend registration failed
        await deleteUser(userCredential.user);
      }
    } catch (error) {
      showMessage(getFirebaseErrorMessage(error), 'authMessage');
    }
  });
}

// Auth state observer
onAuthStateChanged(auth, async (user) => {
  if (user && isExplicitLogin) {
    try {
      const token = await user.getIdToken();
      const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ token })
      });
      
      const data = await response.json();
      if (data.success && window.location.pathname !== '/feature') {
        window.location.href = '/feature';
      }
    } catch (error) {
      console.error('Session verification error:', error);
    }
  }
});

// Helper functions
function showMessage(message, elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
      element.style.display = 'none';
    }, 5000);
  }
}

function getFirebaseErrorMessage(error) {
  switch(error.code) {
    case 'auth/invalid-email': return 'Invalid email address';
    case 'auth/email-already-in-use': return 'Email already in use';
    case 'auth/user-disabled': return 'Account disabled';
    case 'auth/user-not-found': return 'Account not found';
    case 'auth/wrong-password': return 'Incorrect password';
    case 'auth/weak-password': return 'Password should be at least 6 characters';
    case 'auth/too-many-requests': return 'Too many attempts. Try again later';
    default: return error.message || 'An error occurred';
  }
}
// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);

// // Listen to auth state changes to ensure the user is logged in or not
// onAuthStateChanged(auth, function(user) {
//   if (user) {
//     // User is logged in, send the token to the server for validation
//     user.getIdToken().then((token) => {
//       fetch('/login', {
//         method: 'POST',
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify({ token })
//       })
//       .then(response => response.json())
//       .then(data => {
//         if (data.success && data.redirect) {
//           // Redirect to the feature page
//           window.location.href = data.redirect;
//         } else {
//           // If login failed, redirect to the login page
//           window.location.href = '/auth';
//         }
//       })
//       .catch(error => console.error('Login validation error:', error));
//     });
//   } else {
//     // If not logged in, show the login page
//     window.location.href = '/auth';
//   }
// });

// // Sign-In Functionality
// document.getElementById('submitSignIn')?.addEventListener('click', async (e) => {
//   e.preventDefault();
//   const email = document.getElementById('email').value;
//   const password = document.getElementById('password').value;

//   try {
//     const userCredential = await signInWithEmailAndPassword(auth, email, password);
//     const token = await userCredential.user.getIdToken();
    
//     const response = await fetch('/login', {
//       method: 'POST',
//       headers: {'Content-Type': 'application/json'},
//       body: JSON.stringify({ token })
//     });
    
//     const data = await response.json();
//     if (data.success && data.redirect) {
//       window.location.href = data.redirect;  // This will redirect to /feature
//     } else {
//       alert('Login failed: ' + (data.error || 'Unknown error'));
//     }
//   } catch (error) {
//     alert('Login error: ' + error.message);
//   }
// });


// // Sign Up Functionality
// document.getElementById('submitSignUp')?.addEventListener('click', async (e) => {
//   e.preventDefault();
//   const fName = document.getElementById('fName').value;
//   const lName = document.getElementById('lName').value;
//   const email = document.getElementById('rEmail').value;
//   const password = document.getElementById('rPassword').value;
//   const signUpMessage = document.getElementById('signUpMessage');
//   const submitButton = document.getElementById('submitSignUp');

//   try {
//     // Clear previous messages and show loading state
//     signUpMessage.style.display = 'none';
//     signUpMessage.textContent = '';
//     submitButton.disabled = true;
//     submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating account...';

//     // Basic client-side validation
//     if (!fName || !lName || !email || !password) {
//       throw new Error('All fields are required');
//     }

//     if (password.length < 6) {
//       throw new Error('Password must be at least 6 characters');
//     }

//     // Create user with Firebase Auth
//     const userCredential = await createUserWithEmailAndPassword(auth, email, password);
//     const token = await userCredential.user.getIdToken();

//     // Send additional user data to your backend
//     const response = await fetch('/register', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       credentials: 'include',
//       body: JSON.stringify({ 
//         token,
//         firstName: fName,
//         lastName: lName,
//         email
//       })
//     });

//     const data = await response.json();
    
//     if (!response.ok) {
//       throw new Error(data.error || 'Registration failed');
//     }

//     // Registration successful - redirect to feature page
//     window.location.href = '/feature';

//   } catch (error) {
//     console.error('Sign up error:', error);
//     signUpMessage.style.display = 'block';
//     signUpMessage.textContent = error.message || 'Registration failed. Please try again.';
    
//     // Firebase specific error handling
//     if (error.code) {
//       switch (error.code) {
//         case 'auth/email-already-in-use':
//           signUpMessage.textContent = 'Email already in use.';
//           break;
//         case 'auth/invalid-email':
//           signUpMessage.textContent = 'Invalid email address.';
//           break;
//         case 'auth/weak-password':
//           signUpMessage.textContent = 'Password should be at least 6 characters.';
//           break;
//         default:
//           signUpMessage.textContent = 'Registration failed. Please try again.';
//       }
//     }
//   } finally {
//     submitButton.disabled = false;
//     submitButton.textContent = 'Sign Up';
//   }
// });



// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);

// // Listen to auth state changes
// function setupAuthStateListener() {
//   onAuthStateChanged(auth, async (user) => {
//     if (user) {
//       try {
//         const token = await user.getIdToken();
//         const response = await fetch('/login', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ token })
//         });

//         const data = await response.json();
//         if (data.success) {
//           if (window.location.pathname !== '/feature') {
//             window.location.href = '/feature';
//           }
//         } else {
//           if (window.location.pathname !== '/auth') {
//             window.location.href = '/auth';
//           }
//         }
//       } catch (error) {
//         console.error('Token error:', error);
//         if (window.location.pathname !== '/auth') {
//           window.location.href = '/auth';
//         }
//       }
//     } else {
//       // Only redirect if we're not already on the login/signup page
//       if (window.location.pathname !== '/auth') {
//         console.log('No user signed in. Staying on current page.');
//       }
//     }
//   });
// }

// // Sign-In Functionality
// function setupSignInForm() {
//   const signInForm = document.getElementById('signInForm');
//   const signInMessage = document.getElementById('signInMessage');
  
//   if (signInForm) {
//     signInForm.addEventListener('submit', async (e) => {
//       e.preventDefault();
      
//       const email = document.getElementById('email').value;
//       const password = document.getElementById('password').value;
      
//       try {
//         const userCredential = await signInWithEmailAndPassword(auth, email, password);
//         console.log('Sign in successful:', userCredential.user.uid);
        
//         // The auth state listener will handle the redirect
//       } catch (error) {
//         console.error('Sign in error:', error);
//         signInMessage.textContent = getFirebaseErrorMessage(error);
//         signInMessage.style.display = 'block';
//       }
//     });
//   }
// }

// // Helper function for Firebase error messages
// function getFirebaseErrorMessage(error) {
//   switch(error.code) {
//     case 'auth/invalid-email':
//       return 'Invalid email address';
//     case 'auth/user-disabled':
//       return 'Account disabled';
//     case 'auth/user-not-found':
//       return 'Account not found';
//     case 'auth/wrong-password':
//       return 'Incorrect password';
//     case 'auth/too-many-requests':
//       return 'Too many attempts. Try again later';
//     default:
//       return 'Login failed. Please try again.';
//   }
// }

// // Initialize everything when DOM is loaded
// document.addEventListener('DOMContentLoaded', () => {
//   setupAuthStateListener();   // Now defined and works properly
//   setupSignInForm();          // Sign-in form handler
//   console.log('Current path:', window.location.pathname);
// });




// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);
// const db = getFirestore(app);

// // Track if login was explicit
// let isExplicitLogin = false;

// // DOM elements
// const signInForm = document.getElementById('signInForm');
// const signInMessage = document.getElementById('signInMessage');
// const loadingIndicator = document.getElementById('loading');
// const authContainer = document.getElementById('authContainer');

// // Show auth form after checking initial state
// setTimeout(() => {
//   if (loadingIndicator) loadingIndicator.style.display = 'none';
//   if (authContainer) authContainer.style.display = 'block';
// }, 500);

// // Sign-In Functionality
// if (signInForm) {
//   signInForm.addEventListener('submit', async (e) => {
//     e.preventDefault();
    
//     const email = document.getElementById('email').value;
//     const password = document.getElementById('password').value;

//     // Validate inputs
//     if (!email || !password) {
//       showMessage('Please enter both email and password', 'signInMessage');
//       return;
//     }

//     try {
//       isExplicitLogin = true;
//       const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
//       // Get the token and verify with backend
//       const token = await userCredential.user.getIdToken();
//       const response = await fetch('/login', {
//         method: 'POST',
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify({ token })
//       });
      
//       const data = await response.json();
//       if (data.success) {
//         window.location.href = '/feature';
//       } else {
//         showMessage(data.error || 'Login failed', 'signInMessage');
//         isExplicitLogin = false;
//       }
//     } catch (error) {
//       showMessage(getFirebaseErrorMessage(error), 'signInMessage');
//       isExplicitLogin = false;
//     }
//   });
// }

// // Auth state observer - handles page refreshes when already logged in
// onAuthStateChanged(auth, async (user) => {
//   if (user && isExplicitLogin) {
//     try {
//       const token = await user.getIdToken();
//       const response = await fetch('/login', {
//         method: 'POST',
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify({ token })
//       });
      
//       const data = await response.json();
//       if (data.success && window.location.pathname !== '/feature') {
//         window.location.href = '/feature';
//       }
//     } catch (error) {
//       console.error('Session verification error:', error);
//     }
//   }
// });
// // Updated Sign Up Functionality
// document.getElementById('submitSignUp')?.addEventListener('click', async (e) => {
//   e.preventDefault();
  
//   const email = document.getElementById('rEmail').value;
//   const password = document.getElementById('rPassword').value;
//   const firstName = document.getElementById('fName').value;
//   const lastName = document.getElementById('lName').value;

//   try {
//       // Create user in Firebase and your backend
//       const response = await fetch('/register', {
//           method: 'POST',
//           headers: {'Content-Type': 'application/json'},
//           body: JSON.stringify({
//               email,
//               password,
//               firstName,
//               lastName
//           })
//       });
      
//       const data = await response.json();
      
//       if (data.success) {
//           // Get Firebase token and complete login
//           const user = auth.currentUser;
//           const token = await user.getIdToken();
          
//           const loginResponse = await fetch('/login', {
//               method: 'POST',
//               headers: {'Content-Type': 'application/json'},
//               body: JSON.stringify({ token })
//           });
          
//           const loginData = await loginResponse.json();
          
//           if (loginData.success) {
//               window.location.href = '/profile';
//           } else {
//               showMessage(loginData.error || 'Login after signup failed', 'signUpMessage');
//           }
//       } else {
//           showMessage(data.error || 'Registration failed', 'signUpMessage');
//       }
//   } catch (error) {
//       showMessage(error.message || 'An error occurred', 'signUpMessage');
//   }
// });

// // Helper function
// function showMessage(message, elementId) {
//   const element = document.getElementById(elementId);
//   if (element) {
//       element.textContent = message;
//       element.style.display = 'block';
//       setTimeout(() => {
//           element.style.display = 'none';
//       }, 5000);
//   }
// }

// // // Helper function to show messages
// // function showMessage(message, elementId) {
// //   const element = document.getElementById(elementId);
// //   if (element) {
// //     element.textContent = message;
// //     element.style.display = 'block';
// //     setTimeout(() => {
// //       element.style.display = 'none';
// //     }, 5000);
// //   }
// // }

// // Helper function for Firebase errors
// function getFirebaseErrorMessage(error) {
//   switch(error.code) {
//     case 'auth/invalid-email': return 'Invalid email address';
//     case 'auth/user-disabled': return 'Account disabled';
//     case 'auth/user-not-found': return 'Account not found';
//     case 'auth/wrong-password': return 'Incorrect password';
//     case 'auth/too-many-requests': return 'Too many attempts. Try again later';
//     default: return 'Login failed. Please try again.';
//   }
// }