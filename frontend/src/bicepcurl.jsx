import { useEffect, useRef, useState } from "react";
import "./bicepcurl.css";

function BicepCurl({ user = {}, exercise = {}, onBack, onComplete, onResult }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);

  // Camera state
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState("");

  // Workout metrics (starts at 0, NO fake auto-counting)
  const [workoutRunning, setWorkoutRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [repetitions, setRepetitions] = useState(0);
  const targetReps = 12;

  // ML API Integration state
  const [mlApiEndpoint, setMlApiEndpoint] = useState("http://localhost:5000/api/analyze-pose");
  const [mlConnected, setMlConnected] = useState(false);
  const [showApiConfig, setShowApiConfig] = useState(false);
  const [isApiStreaming, setIsApiStreaming] = useState(false);
  const [apiLog, setApiLog] = useState("ML API interface ready. Waiting for backend connection.");

  // Posture & Guidance Feedback
  const [showGuide, setShowGuide] = useState(true);
  const [currentAngle, setCurrentAngle] = useState(160); // 160 = extended, 40 = curled
  const [postureScore, setPostureScore] = useState(92);
  const [formFeedback, setFormFeedback] = useState("Align yourself in camera view. Keep upper arm pinned to torso.");
  const [feedbackType, setFeedbackType] = useState("info"); // 'info' | 'success' | 'warning'
  const [feedbackHistory, setFeedbackHistory] = useState([
    "Starting position: Arm extended, elbow close to ribs."
  ]);
  const [activeStep, setActiveStep] = useState(1);

  // 1. Initialize camera
  useEffect(() => {
    let isMounted = true;

    const startCamera = async () => {
      try {
        setCameraError("");
        setCameraReady(false);

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error("Camera API is not supported in this browser. Please use Chrome or Edge.");
        }

        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "user",
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        });

        if (!isMounted) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        streamRef.current = stream;
        const video = videoRef.current;
        if (!video) throw new Error("Video element could not be found.");

        video.srcObject = stream;

        video.onloadedmetadata = async () => {
          if (!isMounted) return;
          try {
            await video.play();
            if (isMounted) {
              setCameraReady(true);
              setWorkoutRunning(true);
            }
          } catch (playError) {
            if (isMounted) {
              setCameraError("Camera detected, but playback was blocked. Please grant autoplay permission.");
            }
          }
        };
      } catch (error) {
        if (isMounted) {
          setCameraError(`Unable to access camera: ${error.message}`);
        }
      }
    };

    startCamera();

    return () => {
      isMounted = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // 2. Workout elapsed timer (only counts while running)
  useEffect(() => {
    if (!workoutRunning || !cameraReady) return undefined;
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [workoutRunning, cameraReady]);

  // 3. Optional ML API Frame Streamer
  // When isApiStreaming is enabled, it grabs frames from video and sends to ML backend endpoint
  useEffect(() => {
    if (!isApiStreaming || !cameraReady || !workoutRunning) return undefined;

    const streamInterval = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current) return;
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      canvas.width = 320;
      canvas.height = 240;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const frameDataUrl = canvas.toDataURL("image/jpeg", 0.6);

      try {
        const response = await fetch(mlApiEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            exercise: "bicep_curl",
            image: frameDataUrl,
            userId: user.id || user.patientId,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          setMlConnected(true);
          setApiLog(`ML API Connected • Frame processed (${new Date().toLocaleTimeString()})`);

          // Update metrics from ML model response
          if (result.repCount !== undefined) setRepetitions(result.repCount);
          if (result.angle !== undefined) setCurrentAngle(result.angle);
          if (result.score !== undefined) setPostureScore(result.score);
          if (result.feedback) {
            setFormFeedback(result.feedback);
            setFeedbackType(result.isCorrectPosture ? "success" : "warning");
            setFeedbackHistory((prev) => [result.feedback, ...prev.slice(0, 4)]);
          }
        } else {
          setMlConnected(false);
          setApiLog(`ML API Response: ${response.status} ${response.statusText}`);
        }
      } catch (err) {
        setMlConnected(false);
        setApiLog(`ML API Backend Offline at ${mlApiEndpoint}. (Use practice controls below).`);
      }
    }, 1000);

    return () => clearInterval(streamInterval);
  }, [isApiStreaming, cameraReady, workoutRunning, mlApiEndpoint, user]);

  // Handle manual / simulated rep count with posture check
  function handleManualRep(postureQuality = "good") {
    setRepetitions((prev) => {
      const next = prev + 1;
      return next;
    });

    if (postureQuality === "good") {
      setCurrentAngle(38);
      setFormFeedback("Good repetition! Elbow anchored firmly, full bicep contraction.");
      setFeedbackType("success");
      setPostureScore((s) => Math.min(98, Math.max(85, s + 1)));
      setFeedbackHistory((prev) => ["Good rep: Elbow anchored, full contraction.", ...prev.slice(0, 4)]);
      setActiveStep(3);

      setTimeout(() => {
        setCurrentAngle(155);
        setActiveStep(4);
        setFormFeedback("Controlled lowering back to full extension (160°).");
        setFeedbackType("info");
      }, 1200);
    } else {
      setCurrentAngle(65);
      setFormFeedback("Warning: Elbow drifted forward. Keep your elbow pinned to your side.");
      setFeedbackType("warning");
      setPostureScore((s) => Math.max(75, s - 2));
      setFeedbackHistory((prev) => ["Posture alert: Elbow drifted forward. Keep upper arm still.", ...prev.slice(0, 4)]);
      setActiveStep(2);
    }
  }

  function handleResetReps() {
    setRepetitions(0);
    setFormFeedback("Rep counter reset. Ready for next set.");
    setFeedbackType("info");
  }

  function togglePlayPause() {
    setWorkoutRunning((prev) => !prev);
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60).toString().padStart(2, "0");
    const secs = (seconds % 60).toString().padStart(2, "0");
    return `${mins}:${secs}`;
  }

  // Finish session & save to particular user
  function handleFinishSession() {
    setWorkoutRunning(false);
    setIsApiStreaming(false);

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    const sessionData = {
      exercise: exercise?.name || "Bicep Curl",
      duration: formatTime(elapsed),
      repetitions: repetitions,
      postureScore: postureScore,
      accuracy: postureScore,
      feedbackNotes: feedbackHistory.length > 0 ? feedbackHistory : ["Consistent elbow anchor maintained.", "Completed full range of motion."],
      userName: user?.name || "Patient",
      userEmail: user?.email || "guest@physioai.com",
      patientId: user?.patientId || "PAT-101",
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    if (onComplete) {
      onComplete(sessionData);
    }

    if (onResult) {
      onResult();
    }
  }

  // Calculate SVG arm angle points
  const elbowX = 240;
  const elbowY = 240;
  const shoulderX = 240;
  const shoulderY = 100;
  const armLength = 120;
  const angleRad = ((180 - currentAngle) * Math.PI) / 180;
  const wristX = elbowX + Math.sin(angleRad) * armLength;
  const wristY = elbowY - Math.cos(angleRad) * armLength;

  return (
    <div className="bicep-workout-page">
      {/* Hidden canvas for capturing video frames to ML API */}
      <canvas ref={canvasRef} style={{ display: "none" }} />

      {/* HEADER */}
      <header className="bicep-nav-header">
        <div className="header-left">
          <button type="button" className="bicep-back-btn" onClick={onBack}>
            ← Exit Session
          </button>
          <div className="title-wrap">
            <span className="physio-eyebrow">PHYSIOAI • CAMERA WORKOUT SESSION</span>
            <h1>{exercise?.name || "Bicep Curl"}</h1>
          </div>
        </div>

        <div className="header-meta">
          <div className="ml-status-pill">
            <span className={mlConnected ? "dot-connected" : "dot-ready"} />
            <span>{mlConnected ? "ML API Connected" : "ML API Ready (via API)"}</span>
            <button
              type="button"
              className="ml-config-btn"
              onClick={() => setShowApiConfig(!showApiConfig)}
              title="Configure ML API Endpoint"
            >
              ⚙
            </button>
          </div>

          <div className="patient-pill">
            <div className="patient-avatar">{user?.name ? user.name.charAt(0).toUpperCase() : "P"}</div>
            <div>
              <strong>{user?.name || "Patient"}</strong>
              <small>{user?.patientId || "PAT-101"} • {user?.email || "Local"}</small>
            </div>
          </div>
        </div>
      </header>

      {/* API CONFIG MODAL / DROPDOWN */}
      {showApiConfig && (
        <div className="api-config-banner">
          <div className="api-config-content">
            <strong>ML Backend API Integration Settings</strong>
            <p>Connect your custom Python / Flask / FastAPI pose-detection server:</p>
            <div className="api-input-row">
              <input
                type="text"
                value={mlApiEndpoint}
                onChange={(e) => setMlApiEndpoint(e.target.value)}
                placeholder="http://localhost:5000/api/analyze-pose"
              />
              <button
                type="button"
                className={`api-stream-toggle ${isApiStreaming ? "streaming" : ""}`}
                onClick={() => setIsApiStreaming(!isApiStreaming)}
              >
                {isApiStreaming ? "Stop ML Stream" : "Start ML Frame Stream"}
              </button>
              <button
                type="button"
                className="api-close-btn"
                onClick={() => setShowApiConfig(false)}
              >
                Done
              </button>
            </div>
            <small className="api-log-msg">{apiLog}</small>
          </div>
        </div>
      )}

      {/* MAIN LAYOUT */}
      <div className="workout-container">
        {/* CAMERA VIEWPORT WITH HUD OVERLAY */}
        <section className="camera-viewport-card">
          <div className="video-wrapper">
            <video
              ref={videoRef}
              className="camera-stream"
              autoPlay
              muted
              playsInline
            />

            {/* CAMERA ERROR OVERLAY */}
            {cameraError && (
              <div className="hud-overlay-msg error">
                <div className="msg-icon">!</div>
                <h3>Camera Connection Failed</h3>
                <p>{cameraError}</p>
                <button type="button" className="hud-btn primary" onClick={() => window.location.reload()}>
                  Retry Camera
                </button>
              </div>
            )}

            {/* CAMERA LOADING OVERLAY */}
            {!cameraReady && !cameraError && (
              <div className="hud-overlay-msg loading">
                <div className="hud-spinner" />
                <h3>Activating Webcam...</h3>
                <p>Please grant camera permission in your browser.</p>
              </div>
            )}

            {/* REAL-TIME GUIDANCE HUD OVERLAYS */}
            {cameraReady && !cameraError && (
              <>
                {/* TOP STATUS BAR */}
                <div className="hud-top-bar">
                  <div className="hud-pill live-pill">
                    <span className="pulse-dot-green" />
                    <span>Live Camera Feed Active</span>
                  </div>

                  {/* FORM FEEDBACK PILL */}
                  <div className={`hud-feedback-pill ${feedbackType}`}>
                    <span className="feedback-icon">
                      {feedbackType === "success" ? "✓" : feedbackType === "warning" ? "⚠" : "✦"}
                    </span>
                    <span>{formFeedback}</span>
                  </div>

                  <div className="hud-pill timer-pill">
                    <span className="timer-icon">⏱</span>
                    <strong>{formatTime(elapsed)}</strong>
                  </div>
                </div>

                {/* TARGET ARM ALIGNMENT SILHOUETTE & ANGLE ARC OVERLAY */}
                {showGuide && (
                  <div className="hud-alignment-canvas">
                    <svg
                      viewBox="0 0 480 360"
                      className="alignment-svg"
                      preserveAspectRatio="xMidYMid meet"
                    >
                      {/* Body Guide Outline */}
                      <ellipse cx="140" cy="180" rx="40" ry="110" className="guide-body-silhouette" />
                      <circle cx="140" cy="55" r="28" className="guide-body-silhouette" />

                      {/* Shoulder Anchor */}
                      <circle cx={shoulderX} cy={shoulderY} r="8" className="guide-anchor-point" />
                      <text x={shoulderX + 14} y={shoulderY + 4} className="guide-label">Shoulder</text>

                      {/* Upper Arm Line (Fixed) */}
                      <line
                        x1={shoulderX}
                        y1={shoulderY}
                        x2={elbowX}
                        y2={elbowY}
                        className="guide-bone-line"
                      />

                      {/* Elbow Pivot Joint */}
                      <circle cx={elbowX} cy={elbowY} r="10" className="guide-pivot-joint" />
                      <circle cx={elbowX} cy={elbowY} r="18" className="guide-pivot-pulse" />
                      <text x={elbowX - 45} y={elbowY + 4} className="guide-label highlight">Elbow (Anchor)</text>

                      {/* Range of Motion Arc Background */}
                      <path
                        d="M 240 120 A 120 120 0 0 1 345 200"
                        className="guide-arc-bg"
                      />

                      {/* Moving Forearm Line */}
                      <line
                        x1={elbowX}
                        y1={elbowY}
                        x2={wristX}
                        y2={wristY}
                        className="guide-active-arm-line"
                      />

                      {/* Moving Wrist Tracker */}
                      <circle cx={wristX} cy={wristY} r="9" className="guide-wrist-joint" />
                      <text x={wristX + 12} y={wristY + 4} className="guide-wrist-label">
                        Arm ({currentAngle}°)
                      </text>
                    </svg>
                  </div>
                )}

                {/* FLOATING HUD METRIC CARDS */}
                <div className="hud-metrics-floating">
                  {/* Angle Meter Card */}
                  <div className="hud-card angle-card">
                    <span className="card-label">JOINT ANGLE &amp; POSTURE</span>
                    <div className="angle-value-row">
                      <strong>{currentAngle}°</strong>
                      <span className={`phase-badge ${currentAngle <= 60 ? "peak" : currentAngle <= 120 ? "curl_up" : "ready"}`}>
                        {currentAngle <= 60 ? "Peak Contraction" : currentAngle <= 120 ? "Mid Range" : "Extended"}
                      </span>
                    </div>
                    <div className="angle-bar-track">
                      <div
                        className="angle-bar-fill"
                        style={{ width: `${Math.min(100, Math.max(0, ((160 - currentAngle) / 120) * 100))}%` }}
                      />
                    </div>
                  </div>

                  {/* Rep Counter Floating Card */}
                  <div className="hud-card rep-card">
                    <span className="card-label">EXERCISE REPETITIONS</span>
                    <div className="rep-number-row">
                      <span className="rep-count-big">{repetitions}</span>
                      <span className="rep-target-sub">/ {targetReps} reps</span>
                    </div>

                    <div className="rep-actions">
                      <button
                        type="button"
                        className="rep-mini-btn primary-action"
                        onClick={() => handleManualRep("good")}
                        title="Record 1 correct repetition"
                      >
                        + Correct Rep
                      </button>
                      <button
                        type="button"
                        className="rep-mini-btn warn-action"
                        onClick={() => handleManualRep("warning")}
                        title="Test posture correction warning"
                      >
                        + Posture Alert
                      </button>
                      <button
                        type="button"
                        className="rep-mini-btn muted"
                        onClick={handleResetReps}
                        title="Reset rep count"
                      >
                        Reset
                      </button>
                    </div>
                  </div>
                </div>

                {/* FLOATING BOTTOM CONTROLS */}
                <div className="hud-bottom-controls">
                  <button
                    type="button"
                    className={`hud-control-btn ${workoutRunning ? "active" : "paused"}`}
                    onClick={togglePlayPause}
                  >
                    {workoutRunning ? "⏸ Pause Session" : "▶ Resume Session"}
                  </button>

                  <button
                    type="button"
                    className={`hud-control-btn toggle ${showGuide ? "on" : "off"}`}
                    onClick={() => setShowGuide(!showGuide)}
                  >
                    {showGuide ? "👁 Hide Guidelines" : "👁 Show Guidelines"}
                  </button>

                  <button
                    type="button"
                    className={`hud-control-btn ${isApiStreaming ? "streaming-active" : "outline"}`}
                    onClick={() => setIsApiStreaming(!isApiStreaming)}
                    title="Toggle streaming camera frames to ML API"
                  >
                    {isApiStreaming ? "● ML Stream: ON" : "○ ML Stream: OFF"}
                  </button>
                </div>
              </>
            )}
          </div>
        </section>

        {/* RIGHT SIDEBAR: EXERCISE GUIDANCE & TELEMETRY */}
        <aside className="workout-sidebar">
          {/* USER PROFILE INFO */}
          <div className="side-card user-session-card">
            <span className="side-eyebrow">ACTIVE PATIENT RECORD</span>
            <div className="user-record-row">
              <div className="user-badge">{user?.name ? user.name.charAt(0).toUpperCase() : "U"}</div>
              <div>
                <strong>{user?.name || "Guest Patient"}</strong>
                <p>{user?.email || "bhavya@physioai.com"}</p>
                <small>Patient ID: {user?.patientId || "PAT-101"}</small>
              </div>
            </div>
            <div className="session-target-area">
              <span>REHABILITATION AREA</span>
              <strong>{user?.condition || "Arm & Bicep Rehabilitation"}</strong>
            </div>
          </div>

          {/* SESSION TELEMETRY */}
          <div className="side-card stats-summary-card">
            <span className="side-eyebrow">POSTURE &amp; PERFORMANCE</span>
            <div className="telemetry-grid">
              <div className="telemetry-box">
                <span>POSTURE SCORE</span>
                <strong>{postureScore}%</strong>
                <small className="good">Optimal Form</small>
              </div>
              <div className="telemetry-box">
                <span>REPS COUNTED</span>
                <strong>{repetitions}</strong>
                <small>Goal: {targetReps} reps</small>
              </div>
              <div className="telemetry-box">
                <span>EST. CALORIES</span>
                <strong>{(repetitions * 1.8).toFixed(0)} kcal</strong>
                <small>Active Burn</small>
              </div>
              <div className="telemetry-box">
                <span>ML API STATUS</span>
                <strong>{isApiStreaming ? "Streaming" : "Ready"}</strong>
                <small>{mlConnected ? "Backend Connected" : "Local Camera Mode"}</small>
              </div>
            </div>
          </div>

          {/* REAL-TIME POSTURE FEEDBACK LOG */}
          <div className="side-card checklist-card">
            <h3>Posture Correction Guidance</h3>
            <div className="step-list">
              <div className={`step-item ${activeStep === 1 ? "current" : "completed"}`}>
                <span className="step-num">{activeStep > 1 ? "✓" : "1"}</span>
                <div>
                  <strong>Anchor Elbows to Torso</strong>
                  <p>Avoid swinging elbows forward or back during the curl.</p>
                </div>
              </div>

              <div className={`step-item ${activeStep === 2 ? "current" : activeStep > 2 ? "completed" : ""}`}>
                <span className="step-num">{activeStep > 2 ? "✓" : "2"}</span>
                <div>
                  <strong>Maintain Neutral Spine</strong>
                  <p>Do not lean backwards to compensate with momentum.</p>
                </div>
              </div>

              <div className={`step-item ${activeStep === 3 ? "current" : activeStep > 3 ? "completed" : ""}`}>
                <span className="step-num">{activeStep > 3 ? "✓" : "3"}</span>
                <div>
                  <strong>Full Peak Squeeze</strong>
                  <p>Contract bicep fully at top of motion (around 35°-45°).</p>
                </div>
              </div>

              <div className={`step-item ${activeStep === 4 ? "current" : ""}`}>
                <span className="step-num">4</span>
                <div>
                  <strong>Full Controlled Extension</strong>
                  <p>Lower arm all the way down (155°-160°) before the next rep.</p>
                </div>
              </div>
            </div>
          </div>

          {/* FINISH BUTTON */}
          <div className="side-card finish-action-card">
            <button
              type="button"
              className="finish-workout-btn"
              onClick={handleFinishSession}
            >
              Finish Workout &amp; Save to Profile <span>✓</span>
            </button>
            <p className="finish-note">
              This session will be saved to <strong>{user?.name || "Patient"}</strong>&apos;s history ({user?.email || "local"}).
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default BicepCurl;
