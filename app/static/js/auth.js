/**
 * auth.js
 * Backend Auth & Storage integration for Career Copilot.
 * Handles Google Login, Token Management, and UI Sync.
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
    getAuth,
    signInWithPopup,
    GoogleAuthProvider,
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// ── Firebase Configuration ──────────────────────────────────────────────────
const firebaseConfig = {
    apiKey: "AIzaSyAmQ-i-qA29YHQzawYlyLG-Sa3JSfnb_BM",
    authDomain: "career-copilot-86707.firebaseapp.com",
    projectId: "career-copilot-86707",
    storageBucket: "career-copilot-86707.firebasestorage.app",
    messagingSenderId: "22783734816",
    appId: "1:22783734816:web:711a73aa735214a195b845",
    measurementId: "G-SXF2N8FTFX"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// ── Auth Actions ────────────────────────────────────────────────────────────

/**
 * Trigger Google Login Popup and sync with Backend.
 */
async function loginWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider);
        const token = await result.user.getIdToken();

        // Notify backend of Login
        const response = await fetch('/verify-user', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            console.log("[Auth] User verified with backend ✓");
            window.location.reload();
        } else {
            console.error("[Auth] Backend verification failed");
        }
    } catch (error) {
        console.error("[Auth] Login error:", error);
        if (error.code !== 'auth/popup-closed-by-user') {
            alert("Login failed: " + error.message);
        }
    }
}

/**
 * Sign out and refresh page.
 */
async function logout() {
    try {
        await signOut(auth);
        window.location.href = '/';
    } catch (error) {
        console.error("[Auth] Logout error:", error);
    }
}

/**
 * Helper to get Authorization header for fetch calls.
 */
async function getAuthHeader() {
    const user = auth.currentUser;
    if (user) {
        const token = await user.getIdToken();
        return { 'Authorization': `Bearer ${token}` };
    }
    return {};
}

// Expose to window for inline HTML onclick handlers
window.auth = {
    loginWithGoogle,
    logout,
    getAuthHeader
};

// ── UI Integration ──────────────────────────────────────────────────────────

onAuthStateChanged(auth, async (user) => {
    const loginBtn = document.getElementById('loginBtn');
    const userNav = document.getElementById('userNav');
    const userName = document.getElementById('userName');
    const userImg = document.getElementById('userImg');
    const submitBtn = document.getElementById('submitBtn');

    if (user) {
        // Logged In
        if (loginBtn) loginBtn.classList.add('hidden');
        if (userNav) userNav.classList.remove('hidden');
        if (userName) userName.textContent = user.displayName;
        if (userImg) userImg.src = user.photoURL || '';

        // Enable features
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }

        // ── Necessary: Sync Token to Cookie for direct browser navigation ──
        try {
            const token = await user.getIdToken();
            // Store token in a short-lived session cookie
            document.cookie = `firebase_token=${token}; path=/; max-age=3600; SameSite=Lax`;
            console.log("[Auth] Session cookie synced ✓");
        } catch (err) {
            console.error("[Auth] Cookie sync failed:", err);
        }

    } else {
        // Logged Out
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (userNav) userNav.classList.add('hidden');

        // Clear session cookie
        document.cookie = "firebase_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC";

        // Disable features that require UID
        if (submitBtn && submitBtn.closest('form')?.action?.includes('/analyze')) {
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
            const btnText = document.getElementById('btnText');
            if (btnText) btnText.innerHTML = 'Sign In to Analyze';
        }
    }
});
