## 🧱 Phase-Based Breakdown for LeetPlay (Side Project Edition)

---

### 🔹 **Phase 1: Foundation (Week 1-2)**

**Goal:** Get skeleton app running with GraphQL, Docker, and authentication

**Both:**

* Set up GitHub monorepo (e.g., `/frontend`, `/backend`, `/infra`)
* Configure Docker for backend (Go + gqlgen) and frontend (Next.js + TS)

**Person 1 (Backend):**

* Setup GraphQL server with gqlgen
* Create basic schema: User, Submission, XPLog
* Setup Prisma + PostgreSQL
* Define models and run migrations
* Add GitHub OAuth (for login)

**Person 2 (Frontend):**

* Setup Next.js + TypeScript + Tailwind + Apollo Client
* Build basic layout: Sidebar, Header, Main Dashboard shell
* Implement login page + session context

---

### 🔹 **Phase 2: Core Gamification Logic (Week 3-4)**

**Goal:** Implement XP, streaks, levels, badges, and user dashboard

**Backend:**

* XP rules: difficulty → XP (Easy: 10, Med: 30, Hard: 50)
* Leveling logic (e.g., 100 XP per level)
* Streak tracking (store last submission date, update streak on fetch)
* Badges logic (e.g., "10 Easy", "7-day streak")

**Frontend:**

* Fetch and show XP bar, level, and streak
* Display badge list (locked vs unlocked)
* Submission log with filters (date, difficulty)

---

### 🔹 **Phase 3: Advanced Features (Week 5-6)**

**Goal:** Add leaderboards, missions, and deploy everything

**Backend:**

* Add leaderboard query (top XP users)
* Daily missions (e.g., random daily goal logic)
* Write unit tests for business logic
* Deploy backend with AWS (ECS or Lambda)

**Frontend:**

* Build leaderboard UI
* Create missions widget
* Add celebratory animations (level-up confetti)
* Deploy frontend (Vercel, Netlify, or AWS Amplify)

---

## 🧰 Tech Stack Summary

| Layer     | Tech                               |
| --------- | ---------------------------------- |
| Frontend  | Next.js, TypeScript, Tailwind      |
| Backend   | Go (gqlgen), GraphQL               |
| ORM/DB    | Prisma + PostgreSQL                |
| Infra     | Docker, AWS (Lambda, ECS, RDS)     |
| Auth      | GitHub OAuth via NextAuth          |
| Dev Tools | Husky, ESlint, Prettier, GitHub CI |