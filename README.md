# 🎓 AI-Powered Student Growth Planner

A hackathon MVP that uses **Gemini 2.5 API** to provide personalized, continuous mentoring for students. The system generates dynamic learning roadmaps, tracks progress, and automatically builds professional profiles (Resume & LinkedIn).

## 🌟 Features

### Core Functionalities

1. **Personalized Student Onboarding** 📋
   - Collect academic background, career goals, skills, learning preferences
   - AI-powered profile analysis using Gemini 2.5
   - Extract insights on strengths, gaps, and career paths

2. **AI-Driven Growth Path Generation** 🗺️
   - Phased, personalized roadmap (4 phases)
   - Recommendations for:
     - 📚 Courses (online/university)
     - 📝 Tests & target scores
     - 💼 Internships (timing & companies)
     - 🏆 Certificates
     - 💻 Projects (portfolio building)
   - Industry trend-aware suggestions

3. **Progress Tracking & Feedback** ✅
   - Mark tasks as not_started/in_progress/completed
   - AI-generated encouragement messages
   - Real-time progress dashboard

4. **Dynamic Professional Profile Builder** 💼
   - **Auto-Resume Generator**: Continuously updated with achievements
   - **LinkedIn Assistant**: Post ideas, profile updates, skills suggestions
   - AI-crafted professional content

5. **Simulated Trend Awareness** 📈
   - Industry insights simulation for future-proof recommendations

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
    ↓ REST API
Backend (Flask + SQLAlchemy)
    ↓
Gemini 2.5 API (Core AI Engine)
    ↓
SQLite Database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone/Download the project**
```bash
cd student-growth-planner
```

2. **Backend Setup**

```bash
cd backend

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Configure environment
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY
nano .env  # or use any text editor
```

3. **Start Backend Server**

```bash
python app.py
```

Server runs at `http://localhost:5000`

4. **Frontend Setup**

```bash
cd ../frontend

# Open in browser (use a simple HTTP server or open directly)
# Option 1: Python HTTP server
python -m http.server 8080

# Option 2: Open index.html directly in browser
# Open: file:///path/to/frontend/index.html

# OR use any local server (Live Server in VSCode, etc.)
```

Frontend runs at `http://localhost:8080`

### First Run

1. Navigate to `http://localhost:8080` in your browser
2. Complete the onboarding form
3. AI generates your personalized growth path (takes 20-30 seconds)
4. Explore your roadmap, track progress, and build your profile!

## 📁 Project Structure

```
student-growth-planner/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models (SQLAlchemy)
│   ├── gemini_service.py      # Gemini API orchestrator
│   ├── requirements.txt       # Python dependencies
│   ├── .env.template          # Environment variables template
│   └── student_planner.db     # SQLite database (auto-created)
├── frontend/
│   ├── index.html             # Main UI
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend logic
└── README.md
```

## 🔌 API Endpoints

### User & Onboarding
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/onboard` - Complete onboarding with profile data
- `GET /api/v1/users/{user_id}/profile` - Get user profile

### Growth Path
- `POST /api/v1/growth-path/generate` - Generate initial roadmap
- `GET /api/v1/growth-path/{user_id}` - Fetch current roadmap
- `POST /api/v1/growth-path/regenerate` - Refresh roadmap

### Progress Tracking
- `POST /api/v1/progress/update` - Mark task complete
- `GET /api/v1/progress/{user_id}/summary` - Get progress statistics
- `GET /api/v1/progress/{user_id}/tasks` - Get all tasks with status

### Professional Profile
- `GET /api/v1/profile/{user_id}/resume` - Get auto-generated resume
- `GET /api/v1/profile/{user_id}/linkedin` - Get LinkedIn suggestions
- `POST /api/v1/profile/refresh` - Regenerate profiles

### Utility
- `GET /api/v1/health` - Health check
- `POST /api/v1/trends/simulate` - Trigger trend simulation

## 🧠 Gemini 2.5 Integration Points

### 1. Profile Analysis
**Prompt**: Analyzes student data to identify strengths, gaps, career paths, and learning tips.
**Output**: JSON with categorized insights.

### 2. Growth Path Generation
**Prompt**: Synthesizes profile + trends to generate phased roadmap with courses, tests, internships, certificates, and projects.
**Output**: Structured JSON with 4 phases, each containing detailed recommendations.

### 3. Progress Encouragement
**Prompt**: Generates personalized encouragement when tasks are completed.
**Output**: 2-3 sentence motivational message.

### 4. Resume Bullet Generation
**Prompt**: Creates professional resume bullets for completed projects/internships.
**Output**: Array of action-verb-driven bullet points.

### 5. LinkedIn Content Generation
**Prompt**: Generates post ideas, profile summary, and skills suggestions.
**Output**: JSON with post drafts, hashtags, and profile updates.

## 🎯 Hackathon Prioritization

### MVP - Absolute Minimum (4-6 hours)

✅ **Must Have:**
1. Basic onboarding form (name, major, career goal)
2. Single-phase roadmap generation with Gemini
3. Display roadmap on UI
4. Simple progress tracking (mark complete)

### Enhanced MVP (8-12 hours)

✅ **Should Have:**
1. Multi-phase roadmap (4 phases)
2. Profile analysis display
3. Progress dashboard with stats
4. Basic resume generation

### Full MVP (16-24 hours) ← **Current Implementation**

✅ **Complete Feature Set:**
1. Full onboarding with validation
2. 4-phase detailed roadmap
3. Progress tracking with AI encouragement
4. Auto-resume builder
5. LinkedIn suggestions
6. Polished UI/UX

## 🛠️ Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **AI**: Google Gemini 2.5 API (gemini-2.0-flash-exp)
- **API**: RESTful architecture

## 🎨 UI/UX Features

- Clean, modern interface with gradient accents
- Responsive design (mobile-friendly)
- Toast notifications for user feedback
- Loading states during AI generation
- Intuitive navigation
- Empty states with guidance
- Status badges and progress visualization

## 📊 Database Schema

### Tables:
1. **users** - User accounts
2. **student_profiles** - Academic & career data
3. **growth_paths** - Generated roadmaps
4. **progress_tracker** - Task completion tracking
5. **professional_profiles** - Resume & LinkedIn data
6. **simulated_trends** - Industry trends (hackathon scope)

## 🔒 Environment Variables

```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///student_planner.db
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

## 🐛 Troubleshooting

### Issue: "Gemini service not available"
**Solution**: Verify your API key in `.env` file is correct.

### Issue: Database errors
**Solution**: Delete `student_planner.db` and restart backend to recreate.

### Issue: CORS errors
**Solution**: Ensure backend is running on port 5000 and frontend accesses correct URL.

### Issue: No roadmap generated
**Solution**: Check backend logs for Gemini API errors. Ensure API key has sufficient quota.

## 🚀 Deployment Considerations

### For Production:
1. Use PostgreSQL instead of SQLite
2. Add user authentication (JWT/OAuth)
3. Implement rate limiting
4. Add API key rotation
5. Deploy backend to cloud (Heroku, AWS, GCP)
6. Use CDN for frontend assets
7. Enable HTTPS
8. Add monitoring and logging

## 📝 Demo Script

1. **Onboarding** (2 min)
   - Fill form with sample data
   - Show AI analysis results

2. **Roadmap** (3 min)
   - Navigate through 4 phases
   - Highlight course/project recommendations
   - Show rationale for each item

3. **Progress** (2 min)
   - Mark items as complete
   - Show AI encouragement
   - Display updated statistics

4. **Profile** (2 min)
   - Show auto-generated resume
   - Display LinkedIn suggestions
   - Download resume

**Total Demo**: ~10 minutes

## 🎉 Key Differentiators

1. **Continuous Mentoring**: Not just one-time plan, evolves with progress
2. **Professional Profile Automation**: Resume & LinkedIn build themselves
3. **Phased Approach**: Logical progression over time
4. **Rationale-Driven**: Every recommendation explained
5. **Encouragement System**: Motivates students to stay on track

## 📄 License

MIT License - Free to use for hackathons and educational purposes.

## 🤝 Contributing

This is a hackathon MVP. For improvements:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## 💡 Future Enhancements

- Real-time job market API integration
- Peer networking features
- Mentor matching
- Course completion verification
- Integration with learning platforms (Coursera, Udemy)
- Mobile app (React Native)
- Skill assessment quizzes
- Career trajectory visualization

## 📞 Support

For questions or issues:
- Check troubleshooting section
- Review API documentation
- Check Gemini API status

---

**Built with ❤️ for student success** 🎓