

// Fixed & Cleaned Firebase Auth 

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, setDoc, doc, getDoc, updateDoc } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: “——“,
  authDomain: “—“,
  projectId: “——“,
  storageBucket: “——“,
  messagingSenderId: “——“,
  appId: “1——“
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
const db = getFirestore();

function showMessage(message, divId) {
  const messageDiv = document.getElementById(divId);
  messageDiv.style.display = "block";
  messageDiv.innerHTML = message;
  messageDiv.style.opacity = 1;
  setTimeout(() => {
    messageDiv.style.opacity = 0;
  }, 5000);
}

// Sign Up
const signUp = document.getElementById('submitSignUp');
signUp.addEventListener('click', async (event) => {
  event.preventDefault();
  console.log("Sign up button clicked"); // Debug log

  const email = document.getElementById('rEmail').value;
  const password = document.getElementById('rPassword').value;
  const firstName = document.getElementById('fName').value;
  const lastName = document.getElementById('lName').value;

    // Add validation
    if (!email || !password || !firstName || !lastName) {
        showMessage('Please fill all fields', 'signUpMessage');
        return;
      }

  try {
    console.log("Attempting to create user..."); // Debug log
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    const todayStr = new Date().toISOString().split('T')[0];
    console.log("User created:", user.uid); // Debug log

    const userData = {
      email,
      firstName,
      lastName,
      lastLoginDate: todayStr,
    };

    await setDoc(doc(db, "users", user.uid), userData);
    console.log("User data saved to Firestore"); // Debug log
    showMessage('Account Created Successfully', 'signUpMessage');
    window.location.href = '/';

  } catch (error) {
    console.error("Signup error:", error); // Debug log
    if (error.code === 'auth/email-already-in-use') {
      showMessage('Email Address Already Exists !!!', 'signUpMessage');
    } else if (error.code === 'auth/weak-password') {
        showMessage('Password should be at least 6 characters', 'signUpMessage');
    } else {
      showMessage('Unable to create user', 'signUpMessage');
    }
  }
});

// Sign In
const signIn = document.getElementById('submitSignIn');
signIn.addEventListener('click', async (event) => {
  event.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  console.log("Attempting login with:", email); // Debug log

  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    console.log("Firebase auth success, user:", user.uid); // debug log

     // Send token to your backend for session creation
    const token = await user.getIdToken();

    console.log("Firebase ID token:", token); // Verify token is generated

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
    });
    
    const data = await response.json();
    console.log("Backend response:", data); // Debug response

    if (response.ok) {
        window.location.href = '/';  // Redirect to home
    } else {
        showMessage('Login failed: '+ (data.error || 'Unknown error'), 'signInMessage');
    }

  } catch (error) {
    if (error.code === 'auth/invalid-credential') {
      showMessage('Incorrect Email or Password', 'signInMessage');
    } else {
      showMessage('Account does not Exist', 'signInMessage');
    }
  }
});

// Helper function for Firebase errors
function getFirebaseError(error) {
  switch(error.code) {
    case 'auth/invalid-email': return 'Invalid email address';
    case 'auth/user-disabled': return 'Account disabled';
    case 'auth/user-not-found': return 'Account not found';
    case 'auth/wrong-password': return 'Incorrect password';
    default: return 'Login failed. Please try again.';
  }
}



import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { 
  getAuth, 
  signInWithEmailAndPassword,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCqRzCp699fXrKP9Kk6bud_k7hvTYHEGXw",
  authDomain: "login-page-c697a.firebaseapp.com",
  projectId: "login-page-c697a",
  storageBucket: "login-page-c697a.appspot.com",
  messagingSenderId: "539007861058",
  appId: "1:539007861058:web:3dde526996102eb3f948db",
  measurementId: "G-75DDR1YBQH"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Auth state observer
function setupAuthStateListener() {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      console.log('User is signed in:', user.uid);
      try {
        const token = await user.getIdToken();
        console.log('Firebase ID token:', token);
        
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token })
        });
        
        const data = await response.json();
        console.log('Server response:', data);
        
        if (data.success) {
          if (window.location.pathname !== '/feature') {
            window.location.href = '/feature';
          }
        } else {
          console.error('Server rejected login:', data.error);
          redirectToAuth();
        }
      } catch (error) {
        console.error('Error during auth state change:', error);
        redirectToAuth();
      }
    } else {
      console.log('User is signed out');
      redirectToAuth();
    }
  });
}

function redirectToAuth() {
  if (window.location.pathname !== '/auth') {
    window.location.href = '/auth';
  }
}

// Sign-in form handler
function setupSignInForm() {
  const signInForm = document.getElementById('signInForm');
  const signInMessage = document.getElementById('signInMessage');
  
  if (signInForm) {
    signInForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('Sign in successful:', userCredential.user.uid);
        
        // The auth state listener will handle the redirect
      } catch (error) {
        console.error('Sign in error:', error);
        signInMessage.textContent = getFirebaseErrorMessage(error);
        signInMessage.style.display = 'block';
      }
    });
  }
}

// Helper function for Firebase error messages
function getFirebaseErrorMessage(error) {
  switch(error.code) {
    case 'auth/invalid-email':
      return 'Invalid email address';
    case 'auth/user-disabled':
      return 'Account disabled';
    case 'auth/user-not-found':
      return 'Account not found';
    case 'auth/wrong-password':
      return 'Incorrect password';
    case 'auth/too-many-requests':
      return 'Too many attempts. Try again later';
    default:
      return 'Login failed. Please try again.';
  }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  setupAuthStateListener();
  setupSignInForm();
  
  // Debug: log current path
  console.log('Current path:', window.location.pathname);
});