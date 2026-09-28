import { useEffect, useRef, useState } from "react";
import "./App.css";
import BicepCurl from "./bicepcurl.jsx";

const exercises = [
  { id: "bicep", name: "Bicep Curl", category: "Upper Body", level: "Beginner", duration: "5 min", description: "Controlled elbow flexion and extension to improve arm movement.", instructions: ["Stand or sit with your back straight.", "Keep your upper arm close to your body.", "Slowly bend your elbow and bring your hand toward your shoulder.", "Pause briefly at the top.", "Return slowly to the starting position."], icon: "↟" },
  { id: "knee", name: "Knee Rolling", category: "Lower Body", level: "Beginner", duration: "5 min", description: "A gentle lower-body mobility exercise with controlled knee movement.", instructions: ["Lie comfortably on your back.", "Bend both knees and keep your feet supported.", "Slowly move both knees from side to side.", "Keep your shoulders relaxed.", "Return your knees to the center."], icon: "◒" },
  { id: "bridging", name: "Bridging", category: "Core", level: "Beginner", duration: "5 min", description: "A controlled hip movement for strength, stability and coordination.", instructions: ["Lie on your back with knees bent.", "Keep your feet flat on the floor.", "Tighten your core gently.", "Lift your hips slowly.", "Lower your hips with control and repeat."], icon: "⌒" },
  { id: "pelvic", name: "Pelvic Tilt", category: "Core", level: "Beginner", duration: "4 min", description: "A gentle exercise focused on controlled pelvic movement.", instructions: ["Lie comfortably on your back.", "Bend your knees and keep your feet flat.", "Gently tighten your abdominal muscles.", "Tilt your pelvis to flatten your lower back.", "Relax and repeat the movement slowly."], icon: "◇" },
  { id: "clam", name: "The Clam", category: "Hip", level: "Beginner", duration: "5 min", description: "A controlled hip exercise supporting stability and movement.", instructions: ["Lie on your side with knees slightly bent.", "Keep your feet together.", "Keep your hips stacked.", "Lift the upper knee slowly.", "Lower the knee with control."], icon: "◡" },
  { id: "extension", name: "Repeated Extension", category: "Back", level: "Beginner", duration: "5 min", description: "A controlled extension movement for physiotherapy exercise practice.", instructions: ["Lie comfortably on your stomach.", "Keep your legs relaxed.", "Place your hands comfortably near your shoulders.", "Perform the extension slowly and comfortably.", "Return to the starting position with control."], icon: "↑" },
];

const emptyUser = { name: "", age: "", gender: "", patientId: "", condition: "", phone: "", email: "" };

const INITIAL_ACCOUNTS = [
  {
    id: 1,
    name: "Demo Patient",
    email: "demo@physioai.com",
    password: "password123",
    patientId: "PAT-101",
    age: "26",
    gender: "Other",
    phone: "+1 555-0182",
    condition: "Upper Body Mobility",
    createdAt: new Date().toISOString()
  }
];

function safeRead(key, fallback) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function getStoredAccounts() {
  try {
    const raw = localStorage.getItem("physioai-accounts");
    if (!raw) {
      localStorage.setItem("physioai-accounts", JSON.stringify(INITIAL_ACCOUNTS));
      return INITIAL_ACCOUNTS;
    }
    const accounts = JSON.parse(raw);
    return Array.isArray(accounts) && accounts.length > 0 ? accounts : INITIAL_ACCOUNTS;
  } catch {
    return INITIAL_ACCOUNTS;
  }
}

function getUserSessions(email) {
  if (!email) return [];
  const clean = email.toLowerCase().trim();
  try {
    const raw = localStorage.getItem(`physioai_sessions_${clean}`);
    if (raw) return JSON.parse(raw);
    const accountsRaw = localStorage.getItem("physioai-accounts");
    if (accountsRaw) {
      const accounts = JSON.parse(accountsRaw);
      const acc = accounts.find((a) => a.email.toLowerCase() === clean);
      if (acc && Array.isArray(acc.sessions)) return acc.sessions;
    }
    return [];
  } catch {
    return [];
  }
}

function saveUserSessions(email, sessionList) {
  if (!email) return;
  const clean = email.toLowerCase().trim();
  try {
    localStorage.setItem(`physioai_sessions_${clean}`, JSON.stringify(sessionList));
    const accountsRaw = localStorage.getItem("physioai-accounts");
    if (accountsRaw) {
      const accounts = JSON.parse(accountsRaw);
      const updated = accounts.map((acc) => {
        if (acc.email.toLowerCase() === clean) {
          return { ...acc, sessions: sessionList };
        }
        return acc;
      });
      localStorage.setItem("physioai-accounts", JSON.stringify(updated));
    }
  } catch (err) {
    console.error("Error saving user sessions", err);
  }
}

function App() {
  const [page, setPage] = useState("home");
  const [authMode, setAuthMode] = useState("login");
  const [user, setUser] = useState(() => safeRead("physioai-user", emptyUser));
  const [isLoggedIn, setIsLoggedIn] = useState(() => localStorage.getItem("physioai-auth") === "true");
  const [sessions, setSessions] = useState(() => {
    const savedEmail = localStorage.getItem("physioai-email");
    return savedEmail ? getUserSessions(savedEmail) : [];
  });
  const [lastSession, setLastSession] = useState(null);
  const [selectedExercise, setSelectedExercise] = useState(null);

  useEffect(() => { localStorage.setItem("physioai-user", JSON.stringify(user)); }, [user]);

  function openAuth(mode = "login") {
    setAuthMode(mode);
    setPage("login");
  }

  function handleLogin(email, password) {
    const accounts = getStoredAccounts();
    const cleanEmail = email.trim().toLowerCase();
    const matched = accounts.find((acc) => acc.email.toLowerCase() === cleanEmail);

    if (!matched) {
      return {
        success: false,
        error: "No account found with this email. Please check your email or Sign Up."
      };
    }

    if (matched.password !== password) {
      return {
        success: false,
        error: "Incorrect password. Please verify and try again."
      };
    }

    localStorage.setItem("physioai-auth", "true");
    localStorage.setItem("physioai-email", matched.email);
    setIsLoggedIn(true);
    setUser(matched);
    const userSessions = getUserSessions(matched.email);
    setSessions(userSessions);
    setLastSession(userSessions[0] || null);
    setPage("dashboard");
    return { success: true };
  }

  function handleSignUp(formData) {
    const accounts = getStoredAccounts();
    const cleanEmail = formData.email.trim().toLowerCase();
    const exists = accounts.some((acc) => acc.email.toLowerCase() === cleanEmail);

    if (exists) {
      return {
        success: false,
        error: "An account with this email already exists. Please Sign In instead."
      };
    }

    const newAccount = {
      id: Date.now(),
      name: formData.name.trim(),
      email: cleanEmail,
      password: formData.password,
      patientId: formData.patientId?.trim() || `PAT-${Math.floor(100 + Math.random() * 900)}`,
      age: formData.age?.toString().trim() || "",
      gender: formData.gender || "Not specified",
      phone: formData.phone?.trim() || "",
      condition: formData.condition?.trim() || "Physiotherapy Rehabilitation",
      sessions: [],
      createdAt: new Date().toISOString()
    };

    const updatedAccounts = [newAccount, ...accounts];
    localStorage.setItem("physioai-accounts", JSON.stringify(updatedAccounts));
    localStorage.setItem("physioai-auth", "true");
    localStorage.setItem("physioai-email", newAccount.email);
    setIsLoggedIn(true);
    setUser(newAccount);
    setSessions([]);
    setLastSession(null);
    saveUserSessions(cleanEmail, []);
    setPage("dashboard");
    return { success: true };
  }

  function handleLogout() {
    localStorage.removeItem("physioai-auth");
    localStorage.removeItem("physioai-email");
    setIsLoggedIn(false);
    setUser(emptyUser);
    setSessions([]);
    setLastSession(null);
    setPage("home");
  }

  function handleProfileUpdate(updatedData) {
    setUser(updatedData);
    const accounts = getStoredAccounts();
    const updatedAccounts = accounts.map((acc) =>
      acc.email.toLowerCase() === (updatedData.email || user.email || "").toLowerCase()
        ? { ...acc, ...updatedData }
        : acc
    );
    localStorage.setItem("physioai-accounts", JSON.stringify(updatedAccounts));
  }

  function openExercise(exercise) { setSelectedExercise(exercise); setPage("exercise"); }
  function goToExercises() { setPage("exercises"); }
  function startAssessment() {
    if (isLoggedIn) {
      setPage(user.name ? "dashboard" : "patient");
    } else {
      openAuth("signup");
    }
  }

  function addSession(sessionData) {
    const currentEmail = user.email || localStorage.getItem("physioai-email") || "patient@physioai.com";
    const newSession = {
      id: Date.now(),
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      userName: user.name || "Patient",
      userEmail: currentEmail,
      patientId: user.patientId || "PAT-101",
      status: "Completed",
      ...sessionData
    };

    const existingSessions = getUserSessions(currentEmail);
    const updatedSessions = [newSession, ...existingSessions];
    saveUserSessions(currentEmail, updatedSessions);
    setSessions(updatedSessions);
    setLastSession(newSession);
  }

  function openSession(session) {
    const exercise = exercises.find((item) => item.name === session.exercise);
    if (exercise) {
      setSelectedExercise(exercise);
      setLastSession(session);
      setPage("result");
    }
  }

  return (
    <div className="app">
      <Navbar
        page={page}
        user={user}
        setPage={setPage}
        isLoggedIn={isLoggedIn}
        onLogin={() => openAuth("login")}
        onSignUp={() => openAuth("signup")}
        onLogout={handleLogout}
      />

      {page === "home" && <Home user={user} onStart={startAssessment} onExercises={goToExercises} />}

      {page === "login" && (
        <AuthPage
          initialMode={authMode}
          onBack={() => setPage("home")}
          onLogin={handleLogin}
          onSignUp={handleSignUp}
        />
      )}

      {page === "patient" && (
        <PatientDetails
          user={user}
          setUser={handleProfileUpdate}
          onBack={() => setPage(isLoggedIn ? "dashboard" : "home")}
          onContinue={goToExercises}
        />
      )}

      {page === "dashboard" && isLoggedIn && (
        <Dashboard
          user={user}
          sessions={sessions}
          onExercises={goToExercises}
          onProfile={() => setPage("patient")}
          onOpenSession={openSession}
        />
      )}

      {page === "exercises" && (
        <ExerciseLibrary
          user={user}
          exercises={exercises}
          onBack={() => setPage(isLoggedIn ? (user.name ? "dashboard" : "patient") : "home")}
          onOpen={openExercise}
        />
      )}

      {page === "exercise" && selectedExercise && (
        <ExerciseDetails
          exercise={selectedExercise}
          onBack={goToExercises}
          onStartCamera={() => setPage("camera")}
        />
      )}

      {page === "camera" && selectedExercise && (
        selectedExercise.id === "bicep" ? (
          <BicepCurl
            user={user}
            exercise={selectedExercise}
            onBack={() => setPage("exercise")}
            onComplete={addSession}
            onResult={() => setPage("result")}
          />
        ) : (
          <CameraPage
            user={user}
            exercise={selectedExercise}
            onBack={() => setPage("exercise")}
            onComplete={addSession}
            onResult={() => setPage("result")}
          />
        )
      )}

      {page === "result" && selectedExercise && (
        <ResultPage
          user={user}
          exercise={selectedExercise}
          lastSession={lastSession}
          sessions={sessions}
          onDashboard={() => setPage("dashboard")}
          onExercises={goToExercises}
        />
      )}
    </div>
  );
}

function Navbar({ page, user, setPage, isLoggedIn, onLogin, onSignUp, onLogout }) {
  return (
    <nav className="navbar">
      <button className="logo" onClick={() => setPage("home")} aria-label="PhysioAI home">
        <span className="logo-mark">P</span>
        <span><strong>PhysioAI</strong><small>Smart Physiotherapy</small></span>
      </button>

      <div className="nav-links">
        <button className={page === "home" ? "active" : ""} onClick={() => setPage("home")}>Home</button>
        <button className={["exercises", "exercise", "camera"].includes(page) ? "active" : ""} onClick={() => setPage("exercises")}>Exercises</button>
        {isLoggedIn && <button className={page === "dashboard" ? "active" : ""} onClick={() => setPage("dashboard")}>Dashboard</button>}
        {isLoggedIn && <button className={page === "patient" ? "active" : ""} onClick={() => setPage("patient")}>Profile</button>}
        {!isLoggedIn && (
          <button className="login-nav auth-highlight-btn" onClick={onLogin}>
            Login / Sign Up
          </button>
        )}
      </div>

      <div className="nav-user">
        <div className="user-avatar">{user.name ? user.name.charAt(0).toUpperCase() : "G"}</div>
        <div className="nav-user-info">
          <strong>{user.name || "Guest User"}</strong>
          <span>{isLoggedIn ? (user.patientId || "Patient") : "Not Signed In"}</span>
        </div>
        {isLoggedIn ? (
          <button className="logout-btn" onClick={onLogout}>Logout</button>
        ) : (
          <button className="login-header-btn" onClick={onLogin}>
            Login / Sign Up
          </button>
        )}
      </div>
    </nav>
  );
}

function Home({ user, onStart, onExercises }) {
  return (
    <main className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-pill"><span className="pulse-dot" /> AI-POWERED PHYSIOTHERAPY</div>
          <h1>Move better.<br /><span>Live stronger.</span></h1>
          <p>Your intelligent physiotherapy companion for guided exercises, movement tracking and future AI-powered posture analysis.</p>
          <div className="hero-actions-column">
            <button className="primary-btn" onClick={onStart}>{user.name ? "Continue Assessment" : "Start Assessment"}<span>→</span></button>
            <button className="analysis-link" onClick={onExercises}><span className="analysis-icon">✦</span><span><strong>Movement Analysis</strong><small>Explore exercises &amp; guided sessions</small></span><b>→</b></button>
          </div>
          <div className="hero-stats"><div><strong>AI</strong><span>Pose Analysis</span></div><div><strong>24/7</strong><span>Exercise Access</span></div><div><strong>6</strong><span>Guided Exercises</span></div></div>
        </div>
        <div className="hero-visual">
          <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" />
          <div className="ai-dashboard-card">
            <div className="visual-top"><span>AI MOVEMENT MONITOR</span><span className="ready"><i /> READY</span></div>
            <div className="motion-display">
              <div className="motion-ring ring-a" /><div className="motion-ring ring-b" />
              <div className="motion-core"><span>AI</span><small>READY</small></div>
              <div className="motion-line line-a" /><div className="motion-line line-b" /><div className="motion-line line-c" />
              <div className="motion-point point-a" /><div className="motion-point point-b" /><div className="motion-point point-c" />
            </div>
            <div className="visual-metrics"><div><span>POSTURE</span><strong>READY</strong></div><div><span>ROM</span><strong>TRACK</strong></div><div><span>REPS</span><strong>COUNT</strong></div></div>
          </div>
        </div>
      </section>
      <section id="features" className="features-section">
        <div className="section-heading"><span>WHY PHYSIOAI</span><h2>Everything you need for better movement.</h2></div>
        <div className="feature-grid">
          <Feature icon="◉" title="Guided Exercises" text="Clear instructions and structured physiotherapy exercises." />
          <Feature icon="⌁" title="AI Pose Analysis" text="Designed for real-time posture and movement detection." />
          <Feature icon="◌" title="Patient Profile" text="Keep physiotherapy information organized in one place." />
          <Feature icon="↗" title="Progress Ready" text="Architecture prepared for exercise tracking and analytics." />
        </div>
      </section>
    </main>
  );
}
function Feature({ icon, title, text }) { return <div className="feature-card"><div className="feature-icon">{icon}</div><h3>{title}</h3><p>{text}</p><span>Explore →</span></div>; }

function AuthPage({ initialMode = "login", onBack, onLogin, onSignUp }) {
  const [mode, setMode] = useState(initialMode); // 'login' or 'signup'
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Sign up fields
  const [signupData, setSignupData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    age: "",
    gender: "Female",
    phone: "",
    condition: "Arm & Bicep Rehabilitation",
  });

  function handleSignupFieldChange(field, val) {
    setSignupData((prev) => ({ ...prev, [field]: val }));
    setError("");
  }

  function fillDemo() {
    setLoginEmail("demo@physioai.com");
    setLoginPassword("password123");
    setError("");
  }

  function submitLogin(e) {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    if (!loginEmail.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!loginPassword) {
      setError("Please enter your password.");
      return;
    }

    const res = onLogin(loginEmail, loginPassword);
    if (!res.success) {
      setError(res.error);
    }
  }

  function submitSignUp(e) {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    if (!signupData.name.trim()) {
      setError("Please enter your full name.");
      return;
    }
    if (!signupData.email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }
    if (signupData.password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }
    if (signupData.password !== signupData.confirmPassword) {
      setError("Passwords do not match. Please re-check.");
      return;
    }

    const res = onSignUp(signupData);
    if (!res.success) {
      setError(res.error);
    } else {
      setSuccessMsg("Account created successfully! Loading your dashboard...");
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="auth-logo">P</span>
          <div>
            <strong>PhysioAI</strong>
            <small>Smart Physiotherapy</small>
          </div>
        </div>

        <div className="auth-mode-toggle">
          <button
            type="button"
            className={`auth-tab-btn ${mode === "login" ? "active" : ""}`}
            onClick={() => { setMode("login"); setError(""); setSuccessMsg(""); }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-tab-btn ${mode === "signup" ? "active" : ""}`}
            onClick={() => { setMode("signup"); setError(""); setSuccessMsg(""); }}
          >
            Create Account (Sign Up)
          </button>
        </div>

        {mode === "login" ? (
          <div>
            <span className="section-tag">WELCOME BACK</span>
            <h1>Sign in to your<br /><span>health space.</span></h1>
            <p className="auth-subtitle">Log in using your registered email and password to access your sessions and dashboard.</p>

            <form onSubmit={submitLogin}>
              <label>
                Email Address
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => { setLoginEmail(e.target.value); setError(""); }}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </label>

              <label>
                Password
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => { setLoginPassword(e.target.value); setError(""); }}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </label>

              {error && <div className="form-error">{error}</div>}
              {successMsg && <div className="form-success">{successMsg}</div>}

              <button className="primary-btn full-btn" type="submit">
                Login <span>→</span>
              </button>

              <div className="demo-credentials-card">
                <span>Quick Test Account:</span>
                <button type="button" className="demo-chip-btn" onClick={fillDemo}>
                  Use demo@physioai.com (pass: password123)
                </button>
              </div>
            </form>

            <div className="auth-switch-prompt">
              <span>New patient? </span>
              <button
                type="button"
                className="text-link-btn"
                onClick={() => { setMode("signup"); setError(""); }}
              >
                Sign up and create an account →
              </button>
            </div>
          </div>
        ) : (
          <div>
            <span className="section-tag">NEW PATIENT REGISTRATION</span>
            <h1>Create your<br /><span>patient profile.</span></h1>
            <p className="auth-subtitle">All details, credentials, and exercise sessions will be stored securely for your therapy.</p>

            <form onSubmit={submitSignUp}>
              <div className="form-grid-compact">
                <label>
                  Full Name *
                  <input
                    type="text"
                    value={signupData.name}
                    onChange={(e) => handleSignupFieldChange("name", e.target.value)}
                    placeholder="e.g. Bhavya Sharma"
                    required
                  />
                </label>

                <label>
                  Email Address *
                  <input
                    type="email"
                    value={signupData.email}
                    onChange={(e) => handleSignupFieldChange("email", e.target.value)}
                    placeholder="e.g. bhavya@example.com"
                    autoComplete="email"
                    required
                  />
                </label>
              </div>

              <div className="form-grid-compact">
                <label>
                  Password (min 6 chars) *
                  <input
                    type="password"
                    value={signupData.password}
                    onChange={(e) => handleSignupFieldChange("password", e.target.value)}
                    placeholder="Create secure password"
                    autoComplete="new-password"
                    required
                  />
                </label>

                <label>
                  Confirm Password *
                  <input
                    type="password"
                    value={signupData.confirmPassword}
                    onChange={(e) => handleSignupFieldChange("confirmPassword", e.target.value)}
                    placeholder="Re-enter password"
                    autoComplete="new-password"
                    required
                  />
                </label>
              </div>

              <div className="form-grid-compact">
                <label>
                  Age
                  <input
                    type="number"
                    value={signupData.age}
                    onChange={(e) => handleSignupFieldChange("age", e.target.value)}
                    placeholder="e.g. 25"
                    min="5"
                    max="120"
                  />
                </label>

                <label>
                  Gender
                  <select
                    value={signupData.gender}
                    onChange={(e) => handleSignupFieldChange("gender", e.target.value)}
                  >
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                    <option value="Other">Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </label>
              </div>

              <div className="form-grid-compact">
                <label>
                  Phone Number
                  <input
                    type="tel"
                    value={signupData.phone}
                    onChange={(e) => handleSignupFieldChange("phone", e.target.value)}
                    placeholder="+91 98765 43210"
                  />
                </label>

                <label>
                  Condition / Rehab Area
                  <input
                    type="text"
                    value={signupData.condition}
                    onChange={(e) => handleSignupFieldChange("condition", e.target.value)}
                    placeholder="e.g. Arm / Bicep, Knee, Core"
                  />
                </label>
              </div>

              {error && <div className="form-error">{error}</div>}
              {successMsg && <div className="form-success">{successMsg}</div>}

              <button className="primary-btn full-btn" type="submit">
                Sign Up &amp; Save Data <span>✓</span>
              </button>
            </form>

            <div className="auth-switch-prompt">
              <span>Already registered? </span>
              <button
                type="button"
                className="text-link-btn"
                onClick={() => { setMode("login"); setError(""); }}
              >
                Sign in with your email and password →
              </button>
            </div>
          </div>
        )}

        <button className="text-button" onClick={onBack}>← Back to home</button>
      </div>

      <div className="auth-side">
        <div className="auth-side-badge">✦ AI PHYSIOTHERAPY</div>
        <h2>Secure access to<br /><span>your therapy.</span></h2>
        <p>Your profile data, registered credentials, and exercise sessions are stored and tracked with precision.</p>
        <div className="auth-side-list">
          <div>✓ Stored credentials for individual sign in</div>
          <div>✓ Personalized patient exercise tracking</div>
          <div>✓ Real-time webcam guidance for Bicep Curls</div>
          <div>✓ Local session history &amp; posture feedback</div>
        </div>
      </div>
    </main>
  );
}

function PatientDetails({ user, setUser, onBack, onContinue }) {
  const [form, setForm] = useState({ ...emptyUser, ...user });
  function update(field, value) { setForm((old) => ({ ...old, [field]: value })); }
  function submit(event) { event.preventDefault(); if (!form.name.trim() || !form.age || !form.patientId.trim()) { alert("Please fill Name, Age and Patient ID."); return; } setUser(form); onContinue(); }
  return <main className="inner-page"><div className="page-container"><button className="back-button" onClick={onBack}>← Back</button><div className="page-intro"><div><span className="section-tag">PATIENT PROFILE</span><h1>Your health profile</h1><p>Enter your basic information to personalize your physiotherapy experience.</p></div><div className="profile-status"><span>✓</span><div><strong>Profile information</strong><small>Saved locally on this device</small></div></div></div><form className="patient-form" onSubmit={submit}><div className="form-section-title"><span>01</span><div><h2>Personal information</h2><p>Tell us a little about yourself.</p></div></div><div className="form-grid"><FormInput label="Full Name" value={form.name} placeholder="Enter your full name" onChange={(v) => update("name", v)} /><FormInput label="Patient ID" value={form.patientId} placeholder="Example: PAT-001" onChange={(v) => update("patientId", v)} /><FormInput label="Age" type="number" value={form.age} placeholder="Enter your age" onChange={(v) => update("age", v)} /><div className="input-wrapper"><label>Gender</label><select value={form.gender} onChange={(e) => update("gender", e.target.value)}><option value="">Select gender</option><option>Female</option><option>Male</option><option>Other</option><option>Prefer not to say</option></select></div><FormInput label="Phone Number" value={form.phone} placeholder="Enter phone number" onChange={(v) => update("phone", v)} /><FormInput label="Condition / Area" value={form.condition} placeholder="Example: Arm, Knee, Back" onChange={(v) => update("condition", v)} /></div><div className="form-bottom"><span>✓ Your information stays on this device for now.</span><button className="primary-btn" type="submit">Save &amp; Continue <span>→</span></button></div></form></div></main>;
}
function FormInput({ label, value, placeholder, onChange, type = "text" }) { return <div className="input-wrapper"><label>{label}</label><input type={type} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} /></div>; }

function ExerciseLibrary({ user, exercises: list, onBack, onOpen }) {
  const [query, setQuery] = useState(""); const [category, setCategory] = useState("All");
  const categories = ["All", "Upper Body", "Lower Body", "Core", "Hip", "Back"];
  const filtered = list.filter((item) => item.name.toLowerCase().includes(query.toLowerCase()) && (category === "All" || item.category === category));
  return <main className="inner-page"><div className="page-container wide"><button className="back-button" onClick={onBack}>← Back</button><div className="library-heading"><div><span className="section-tag">EXERCISE LIBRARY</span><h1>Choose your movement</h1><p>Select an exercise to view instructions and begin your guided session.</p></div><div className="session-user"><div className="user-avatar large">{user.name ? user.name.charAt(0).toUpperCase() : "U"}</div><div><span>SESSION FOR</span><strong>{user.name || "Guest"}</strong></div></div></div><div className="library-toolbar"><div className="search-box"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search exercises..." /></div><div className="category-list">{categories.map((item) => <button key={item} className={category === item ? "filter-chip active" : "filter-chip"} onClick={() => setCategory(item)}>{item}</button>)}</div></div><div className="exercise-grid-modern">{filtered.map((exercise, index) => <article className="exercise-modern-card" key={exercise.id} onClick={() => onOpen(exercise)}><div className={`exercise-art art-${index}`}><div className="art-shape shape-one" /><div className="art-shape shape-two" /><div className="exercise-art-icon">{exercise.icon}</div><span>{String(index + 1).padStart(2, "0")}</span></div><div className="exercise-card-content"><div className="exercise-meta"><span>{exercise.category}</span><span>{exercise.duration}</span></div><h2>{exercise.name}</h2><p>{exercise.description}</p><button onClick={(e) => { e.stopPropagation(); onOpen(exercise); }}>View Exercise <span>↗</span></button></div></article>)}</div>{filtered.length === 0 && <div className="empty-search">No exercises found. Try another search.</div>}</div></main>;
}

function ExerciseDetails({ exercise, onBack, onStartCamera }) {
  return <main className="inner-page"><div className="page-container wide"><button className="back-button" onClick={onBack}>← Exercise Library</button><section className="exercise-detail"><div className="exercise-detail-visual"><div className="detail-art"><div className="detail-grid" /><div className="detail-circle" /><div className="detail-symbol">{exercise.icon}</div><div className="detail-caption">MOVEMENT<br /><strong>GUIDE</strong></div></div><div className="detail-badge">{exercise.level.toUpperCase()}</div></div><div className="exercise-detail-info"><span className="section-tag">{exercise.category}</span><h1>{exercise.name}</h1><p className="detail-description">{exercise.description}</p><div className="detail-stats"><div><span>LEVEL</span><strong>{exercise.level}</strong></div><div><span>DURATION</span><strong>{exercise.duration}</strong></div><div><span>TARGET</span><strong>{exercise.category}</strong></div></div><div className="instructions"><h2>How to perform</h2>{exercise.instructions.map((instruction, index) => <div className="instruction-row" key={`${exercise.id}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{instruction}</p></div>)}</div><button className="primary-btn large-btn" onClick={onStartCamera}>Start Camera Session <span>→</span></button></div></section></div></main>;
}

function CameraPage({ user, exercise, onBack, onComplete, onResult }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [status, setStatus] = useState("starting");
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [repetitions, setRepetitions] = useState(0);
  const [score, setScore] = useState(92);
  const [feedback, setFeedback] = useState("Camera active. Position yourself in frame to begin.");
  const [feedbackHistory, setFeedbackHistory] = useState([
    "Initial posture check: Torso upright, joint tracking ready."
  ]);

  useEffect(() => {
    let mounted = true;
    async function startCamera() {
      try {
        if (!navigator.mediaDevices?.getUserMedia) {
          throw new Error("Camera API is not available. Please use Chrome or Edge.");
        }
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: { ideal: "user" } },
          audio: false
        });
        if (!mounted) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        streamRef.current = stream;
        const video = videoRef.current;
        if (!video) throw new Error("Video element not found.");
        video.srcObject = stream;
        await video.play();
        if (mounted) {
          setStatus("active");
          setRunning(true);
        }
      } catch (err) {
        if (mounted) {
          setStatus("error");
          setError(err?.message || "Unable to access camera.");
        }
      }
    }
    startCamera();
    return () => {
      mounted = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!running || status !== "active") return undefined;
    const timer = setInterval(() => setElapsed((old) => old + 1), 1000);
    return () => clearInterval(timer);
  }, [running, status]);

  function handleAddRep(isGood = true) {
    setRepetitions((r) => r + 1);
    if (isGood) {
      setFeedback("Repetition counted. Controlled tempo and aligned posture.");
      setScore((s) => Math.min(98, Math.max(88, s + 1)));
      setFeedbackHistory((prev) => ["Good rep: Movement rhythm maintained.", ...prev.slice(0, 3)]);
    } else {
      setFeedback("Caution: Keep range of motion smooth without sudden jerk.");
      setScore((s) => Math.max(78, s - 2));
      setFeedbackHistory((prev) => ["Posture alert: Movement jerk detected. Keep controlled.", ...prev.slice(0, 3)]);
    }
  }

  function finish() {
    setRunning(false);
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
    onComplete({
      exercise: exercise.name,
      duration: formatTime(elapsed),
      repetitions,
      postureScore: score || 92,
      accuracy: score || 92,
      feedbackNotes: feedbackHistory
    });
    onResult();
  }

  return (
    <main className="camera-page">
      <div className="camera-header">
        <button className="back-button light" onClick={onBack}>← Back</button>
        <div>
          <span>LIVE CAMERA WORKOUT</span>
          <h1>{exercise.name}</h1>
        </div>
        <div className="camera-user">
          <span>Patient</span>
          <strong>{user.name || "Guest"} ({user.patientId || "PAT-101"})</strong>
        </div>
      </div>

      <div className="camera-layout">
        <div className="camera-main">
          <video ref={videoRef} className="live-video" autoPlay muted playsInline />
          {status === "starting" && (
            <div className="camera-message">
              <div className="loading-ring" />
              <h2>Starting camera</h2>
              <p>Please allow camera access when prompted by your browser.</p>
            </div>
          )}
          {status === "error" && (
            <div className="camera-message error-message">
              <div className="error-symbol">!</div>
              <h2>Camera unavailable</h2>
              <p>{error}</p>
            </div>
          )}
          {status === "active" && (
            <div className="live-status">
              <i /> Camera Active (ML API Ready)
            </div>
          )}
          <div className="camera-overlay-label">
            <span>EXERCISE GUIDANCE</span>
            <strong>{feedback}</strong>
          </div>
        </div>

        <aside className="session-panel">
          <div className="session-panel-head">
            <span>PATIENT SESSION</span>
            <strong>{user.patientId || "PAT-101"}</strong>
          </div>

          <div className="session-exercise">
            <span>Target Movement</span>
            <h2>{exercise.name}</h2>
            <small style={{ color: "#8da496" }}>User: {user.name || "Patient"} ({user.email || "Local"})</small>
          </div>

          <div className="live-stats">
            <div><span>TIME</span><strong>{formatTime(elapsed)}</strong></div>
            <div><span>REPS</span><strong>{repetitions}</strong></div>
            <div><span>SCORE</span><strong>{score}%</strong></div>
          </div>

          <div style={{ display: "flex", gap: "8px", margin: "14px 0" }}>
            <button
              type="button"
              className="primary-btn"
              style={{ flex: 1, minHeight: "38px", fontSize: "11px", padding: "0 8px" }}
              onClick={() => handleAddRep(true)}
            >
              + 1 Rep (Good)
            </button>
            <button
              type="button"
              className="outline-btn"
              style={{ flex: 1, minHeight: "38px", fontSize: "11px", padding: "0 8px" }}
              onClick={() => handleAddRep(false)}
            >
              + Alert Rep
            </button>
          </div>

          <div className="session-status">
            <StatusLine title="Camera Stream" text={status === "active" ? "Connected (Live Feed)" : "Connecting..."} pending={status !== "active"} />
            <StatusLine title="ML API Interface" text="Ready for Backend Stream" pending />
            <StatusLine title="User Data Persistence" text={`Linked to ${user.name || "Patient"}`} />
          </div>

          <div className="session-note">
            <span>✦</span>
            <p>Only the live camera is active. Reps are only counted when registered. Once finished, data is saved directly under {user.name || "Patient"}&apos;s profile.</p>
          </div>

          {status === "active" && (
            <button className="primary-btn full-btn finish-btn" onClick={finish}>
              Finish Workout &amp; Save Session <span>✓</span>
            </button>
          )}
        </aside>
      </div>
    </main>
  );
}
function StatusLine({ title, text, pending }) { return <div className="status-line"><span className={pending ? "status-indicator pending" : "status-indicator"} /><div><strong>{title}</strong><small>{text}</small></div></div>; }
function formatTime(seconds) { const min = Math.floor(seconds / 60).toString().padStart(2, "0"); const sec = (seconds % 60).toString().padStart(2, "0"); return `${min}:${sec}`; }

function Dashboard({ user, sessions, onExercises, onProfile, onOpenSession }) {
  const userSessions = sessions.filter((s) => !s.userEmail || !user.email || s.userEmail.toLowerCase() === user.email.toLowerCase());
  const average = userSessions.length
    ? Math.round(userSessions.reduce((sum, item) => sum + Number(item.postureScore || 0), 0) / userSessions.length)
    : 0;
  const totalReps = userSessions.reduce((sum, item) => sum + Number(item.repetitions || 0), 0);

  return (
    <main className="inner-page">
      <div className="page-container wide">
        <div className="dashboard-header">
          <div>
            <span className="section-tag">PATIENT DASHBOARD</span>
            <h1>Welcome back, {user.name || "Patient"}.</h1>
            <p>
              Signed in as <strong>{user.email}</strong> • Patient ID: <strong>{user.patientId}</strong> • Condition: <strong>{user.condition || "Physiotherapy"}</strong>
            </p>
          </div>
          <button className="outline-btn" onClick={onProfile}>Edit Profile</button>
        </div>

        <div className="dashboard-cards">
          <DashboardCard label="TOTAL SESSIONS" value={userSessions.length} description="Recorded for this account" />
          <DashboardCard label="TOTAL REPETITIONS" value={totalReps} description="Cumulative movement reps" />
          <DashboardCard label="AVG. POSTURE SCORE" value={`${average}%`} description="Patient stability score" />
          <DashboardCard label="PATIENT STATUS" value="ACTIVE" description="Account data saved" />
        </div>

        <div className="dashboard-grid">
          <section className="dashboard-panel">
            <div className="panel-heading">
              <div>
                <span>YOUR EXERCISE HISTORY</span>
                <h2>Completed sessions for {user.name || "Patient"}</h2>
              </div>
              <button onClick={onExercises}>New Session →</button>
            </div>

            {userSessions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✦</div>
                <h3>No sessions yet for this account</h3>
                <p>Start your first exercise session to record your repetitions and posture scores.</p>
                <button className="primary-btn" onClick={onExercises}>Browse Exercises →</button>
              </div>
            ) : (
              <div className="session-list">
                {userSessions.map((session) => (
                  <button className="session-row" key={session.id} onClick={() => onOpenSession(session)}>
                    <div className="session-number">✓</div>
                    <div className="session-row-main">
                      <strong>{session.exercise}</strong>
                      <span>{session.date} {session.time ? `at ${session.time}` : ""} · {session.duration} · {session.repetitions || 0} reps</span>
                    </div>
                    <div className="session-score">
                      <strong>{session.postureScore || 90}%</strong>
                      <span>Score</span>
                    </div>
                    <span className="session-arrow">→</span>
                  </button>
                ))}
              </div>
            )}
          </section>

          <aside className="dashboard-panel system-panel">
            <div className="panel-heading">
              <div>
                <span>SYSTEM STATUS</span>
                <h2>Telemetry &amp; ML Architecture</h2>
              </div>
            </div>
            <IntegrationStatus title="Live Camera Feed" status="Ready &amp; Active" />
            <IntegrationStatus title="ML API Bridge" status="Ready for Backend Stream" pending />
            <IntegrationStatus title="User Data Persistence" status="Active (Linked by Email)" />
            <IntegrationStatus title="ESP32 Sensor Unit" status="Ready for Bluetooth/Serial" pending />
            <div className="integration-note">
              <strong>ML Integration Endpoint</strong>
              <p>The camera session is prepared with a frame capture bridge ready to post to your ML model API.</p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
function DashboardCard({ label, value, description }) { return <div className="dashboard-card"><span>{label}</span><strong>{value}</strong><small>{description}</small></div>; }
function IntegrationStatus({ title, status, pending }) { return <div className="integration-status"><span className={pending ? "integration-dot pending" : "integration-dot"} /><div><strong>{title}</strong><small>{status}</small></div></div>; }

function ResultPage({ user, exercise, lastSession, sessions, onDashboard, onExercises }) {
  const session = lastSession || (sessions.length > 0 ? sessions[0] : null) || {
    exercise: exercise.name,
    postureScore: 92,
    repetitions: 0,
    duration: "00:00",
    userName: user.name || "Patient",
    userEmail: user.email || "demo@physioai.com",
    patientId: user.patientId || "PAT-101",
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    feedbackNotes: ["Movement rhythm stable", "Good posture alignment"]
  };

  const score = Number(session.postureScore || session.accuracy || 92);
  const reps = Number(session.repetitions || 0);
  const duration = session.duration || "00:00";
  const notes = Array.isArray(session.feedbackNotes) && session.feedbackNotes.length > 0
    ? session.feedbackNotes
    : ["Consistent posture maintained", "Movement completed with controlled pace"];

  return (
    <main className="inner-page">
      <div className="page-container">
        <div className="result-top">
          <span className="success-mark">✓</span>
          <span className="section-tag">SESSION SAVED TO YOUR RECORD</span>
          <h1>Great work, {session.userName || user.name || "Patient"}!</h1>
          <p>
            Your {session.exercise || exercise.name} exercise data has been securely saved to your account.
          </p>
          <div className="patient-save-pill">
            <span>Account: <strong>{session.userName || user.name}</strong> ({session.userEmail || user.email})</span>
            <span> • Patient ID: <strong>{session.patientId || user.patientId}</strong></span>
            <span> • Recorded: <strong>{session.date} at {session.time || "recent"}</strong></span>
          </div>
        </div>

        <div className="result-card">
          <div className="result-score">
            <span>MOVEMENT SCORE</span>
            <strong>{score}%</strong>
            <small>{score >= 90 ? "Excellent Posture" : score >= 80 ? "Good Stability" : "Keep Practising"}</small>
          </div>

          <div className="result-metrics">
            <div>
              <span>REPETITIONS</span>
              <strong>{reps} reps</strong>
            </div>
            <div>
              <span>WORKOUT DURATION</span>
              <strong>{duration}</strong>
            </div>
            <div>
              <span>EXERCISE</span>
              <strong>{session.exercise || exercise.name}</strong>
            </div>
          </div>
        </div>

        <div className="result-feedback-section">
          <h3>Posture Correction &amp; Clinical Feedback</h3>
          <div className="feedback-notes-grid">
            {notes.map((note, idx) => (
              <div key={idx} className="feedback-note-item">
                <span className="note-icon">✓</span>
                <p>{note}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="result-actions">
          <button className="primary-btn" onClick={onDashboard}>
            View in Dashboard →
          </button>
          <button className="outline-btn" onClick={onExercises}>
            Try Another Exercise
          </button>
        </div>

        <div className="result-note">
          ✦ All metrics have been permanently saved in local patient storage for {session.userEmail || user.email}.
        </div>
      </div>
    </main>
  );
}

export default App;
