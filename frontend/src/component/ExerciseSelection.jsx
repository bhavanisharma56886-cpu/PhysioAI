const exercises = [
  {
    id: "bicep-curl",
    name: "Bicep Curl",
    target: "Arms",
    level: "Beginner",
    description:
      "Controlled elbow flexion and extension exercise.",
  },
  {
    id: "knee-rolling",
    name: "Knee Rolling",
    target: "Lower Body",
    level: "Beginner",
    description:
      "Gentle movement exercise for controlled lower-body mobility.",
  },
  {
    id: "bridging",
    name: "Bridging",
    target: "Core",
    level: "Beginner",
    description:
      "Controlled hip movement exercise.",
  },
  {
    id: "pelvic-tilt",
    name: "Pelvic Tilt",
    target: "Core",
    level: "Beginner",
    description:
      "Gentle pelvic movement exercise.",
  },
];

function ExerciseSelection({
  user,
  onSelect,
  onBack,
  onEditUser,
}) {
  return (
    <main className="exercise-selection-page">
      <header className="selection-header">
        <button className="back-link" onClick={onBack}>
          ← Back
        </button>

        <div>
          <span className="eyebrow">EXERCISE LIBRARY</span>

          <h1>Select an Exercise</h1>

          <p>
            Choose an exercise to begin your physiotherapy
            session.
          </p>
        </div>

        <div className="user-mini-card">
          <strong>{user.name}</strong>

          <span>
            Patient ID: {user.patientId}
          </span>

          <button onClick={onEditUser}>
            Edit
          </button>
        </div>
      </header>

      <section className="exercise-grid">
        {exercises.map((exercise) => (
          <article
            className="exercise-card"
            key={exercise.id}
          >
            <div className="exercise-card-top">
              <span className="exercise-level">
                {exercise.level}
              </span>

              <span className="exercise-target">
                {exercise.target}
              </span>
            </div>

            <div className="exercise-icon">
              ◎
            </div>

            <h2>{exercise.name}</h2>

            <p>{exercise.description}</p>

            <button
              className="secondary-button"
              onClick={() => onSelect(exercise)}
            >
              Start Exercise →
            </button>
          </article>
        ))}
      </section>
    </main>
  );
}

export default ExerciseSelection;