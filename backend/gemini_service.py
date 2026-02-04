import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional


class GeminiService:
    """
    Orchestrates all interactions with Gemini 2.5 API
    """

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # 1. FORMALIZED SYSTEM INSTRUCTION
        # This keeps the AI "in character" for every single method call.
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction="""You are SkillPath AI, a sophisticated career strategist and technical mentor. 
            You provide raw, honest, and technically detailed advice. 
            You avoid corporate fluff (e.g., "Keep learning!") and favor 'Tech-in-the-trenches' storytelling.
            You always prioritize specific tool names (e.g., 'React Query' over 'libraries') and actionable metrics."""
        )

        # 2. NATIVE JSON CONFIGURATION
        # "response_mime_type": "application/json" guarantees valid JSON output.
        self.generation_config = {
            "temperature": 0.85,  # Slightly higher for creativity
            "top_p": 0.95,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json", 
        }

    def analyze_student_profile(self, profile_data: Dict) -> Dict:
        """
        Analyze student profile and provide insights
        """
        prompt = f"""
You are an expert career advisor analyzing a student's profile.

Student Information:
- Major: {profile_data.get('major', 'Not specified')}
- University: {profile_data.get('university', 'Not specified')}
- GPa: {profile_data.get('gpa', 'Not specified')}
- Experience Level: {profile_data.get('experience_level', 'Not specified')}
- Career Aspirations: {profile_data.get('career_aspirations', 'Not specified')}
- Target Industries: {', '.join(profile_data.get('target_industries', []))}
- Current Skills: {', '.join(profile_data.get('current_skills', []))}
- Preferred Learning Style: {profile_data.get('preferred_learning', 'Not specified')}
- Preferred Content Types: {', '.join(profile_data.get('preferred_content_types', []))}
- Time Commitment: {profile_data.get('time_commitment', 'Not specified')}
- Relocation Goal: {profile_data.get('relocation_goal', 'None')}
- Extracurricular Interests: {', '.join(profile_data.get('extracurricular_interests', []))}
- Planning Horizon: {profile_data.get('planning_horizon_years', 1)} Years

Task: Analyze this profile and provide:
1. Key strengths (2-3 points)
2. Skill gaps to address (2-3 points)
3. Recommended career paths (top 3, ordered from most specific to broad)
4. Learning approach optimization tips (2-3 actionable tips)
5. Advice on relocation and extracurricular balance (if applicable)

Format your response as JSON with keys: "strengths", "gaps", "career_paths", "learning_tips"
Each value should be an array of strings.

Return ONLY valid JSON, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in analyze_student_profile: {e}")
            return {
                "strengths": ["Motivated to learn", "Clear career direction"],
                "gaps": ["Need more hands-on experience"],
                "career_paths": ["Technology Professional", "Industry Specialist", "General Professional"],
                "learning_tips": ["Start with foundational courses", "Build portfolio projects"]
            }

    def generate_growth_path(self, profile_data: Dict, analysis: Dict, timeline_months: int = 12) -> Dict:
        """
        Generate comprehensive phased growth path
        """

        # Simulate trend data
        trend_data = self._get_simulated_trends(profile_data.get('career_aspirations', ''))

        target_role = analysis.get('career_paths', ['Professional'])[0]
        skill_gaps = ', '.join(analysis.get('gaps', []))

        years = int(profile_data.get('planning_horizon_years', 1))
        
        prompt = f"""
You are an expert educational and career strategist creating a personalized {years}-year growth roadmap.

Student Profile:
- Major: {profile_data.get('major')}
- University: {profile_data.get('university')}
- Target Role: {target_role}
- Target Industries: {', '.join(profile_data.get('target_industries', []))}
- Experience Level: {profile_data.get('experience_level')}
- Current Skills: {', '.join(profile_data.get('current_skills', []))}
- Skill Gaps: {skill_gaps}
- Time Commitment: {profile_data.get('time_commitment')}
- Content Preference: {', '.join(profile_data.get('preferred_content_types', []))}
- Relocation Goal: {profile_data.get('relocation_goal', 'None')}
- Extracurricular Interests: {', '.join(profile_data.get('extracurricular_interests', []))}
- Planning Horizon: {years} Years

Current Industry Trends:
{trend_data}

Task: Generate a detailed, phased growth plan with {years} phases, where each phase represents 1 YEAR.

For each phase (Year), provide:

1. **Courses**: 2-3 specific online courses with name, platform, estimated duration, and clear rationale
2. **Tests/Certifications**: Relevant exams with target scores, timing, and rationale
3. **Internships/Jobs**: Types, timing, target companies/industries, and rationale
4. **Extracurricular Activities**: Clubs, hobbies, or volunteering aligned with interests and goals
5. **Projects**: 2-3 practical projects with name, description, skills demonstrated, and rationale
6. **Weekly Routine**: A friendly, sample weekly schedule (e.g., "Mon/Wed: German Class, Sat: Coding Project") tailored to this phase's goals.

Guidelines:
- **Long-term View**: If relocation is a goal (e.g., to Germany), include language learning (A1-C1) and visa prep in earlier years.
- **Holistic**: Integrate extracurriculars to build soft skills.
- **Friendly Tone**: The "Weekly Routine" should sound encouraging and doable.
- **Progression**: ensuring skills build up year over year.

Format as JSON with this EXACT structure:
{{
  "phases": [
    {{
      "phase": 1,
      "title": "Year 1: [Theme Name]",
      "focus": "Main focus of this year",
      "weekly_routine": "Sample weekly schedule (e.g., Mon-Fri: ... Sat: ...)",
      "courses": [
        {{
          "id": "c1",
          "name": "Course Name",
          "platform": "Platform Name",
          "duration": "X weeks",
          "rationale": "Why this course"
        }}
      ],
      "tests": [
        {{
          "id": "t1",
          "name": "Test Name",
          "target_score": "Score or Grade",
          "timing": "When to take",
          "rationale": "Why this test"
        }}
      ],
      "internships": [
        {{
          "id": "i1",
          "type": "Internship Type",
          "when": "Application timeline",
          "companies": ["Company examples"],
          "rationale": "Why this internship"
        }}
      ],
      "certificates": [
        {{
          "id": "cert1",
          "name": "Certificate Name",
          "provider": "Provider Name",
          "timing": "When to get",
          "rationale": "Why this certificate"
        }}
      ],
      "projects": [
        {{
          "id": "p1",
          "name": "Project Name",
          "description": "Project description",
          "skills_demonstrated": ["skill1", "skill2"],
          "rationale": "Why this project"
        }}
      ]
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            response_text = response.text.strip()

            # Clean response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in generate_growth_path: {e}")
            return self._get_fallback_roadmap(target_role)

    def generate_encouragement(self, completed_item: Dict, user_context: Dict) -> str:
        """
        Generate personalized encouragement message
        """
        prompt = f"""
A student just completed: {completed_item.get('item_name')} ({completed_item.get('item_type')})

Student's journey so far:
- Completed items: {user_context.get('completed_count', 0)}
- Current phase: {user_context.get('current_phase', 1)}
- Career goal: {user_context.get('career_goal', 'Professional development')}

Generate a brief, encouraging message (2-3 sentences) that:
1. Acknowledges their specific achievement
2. Connects it to their career goal
3. Motivates next steps

Keep it genuine, specific, and energizing. Do not use emojis.
Return only the message text, nothing else.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.8, "max_output_tokens": 200}
            )
            return response.text.strip()

        except Exception as e:
            print(f"Error in generate_encouragement: {e}")
            return f"Great work completing {completed_item.get('item_name')}! You're making excellent progress toward your goals. Keep up the momentum!"

    def generate_resume_bullets(self, item_data: Dict) -> List[str]:
        """
        Generate professional resume bullet points
        """
        prompt = f"""
Generate professional resume bullet points for:

Type: {item_data.get('item_type')}
Title: {item_data.get('title')}
Description: {item_data.get('description', 'Not provided')}
Skills Used: {', '.join(item_data.get('skills', []))}
Target Role: {item_data.get('target_role', 'Professional')}

Guidelines:
- Start with strong action verbs (Developed, Implemented, Designed, Led, etc.)
- Include quantifiable metrics where possible
- Highlight technical skills and tools
- Show impact and results
- 2-3 bullet points
- Each bullet: 1-2 lines maximum

Format as JSON array:
{{"bullets": ["bullet 1", "bullet 2", "bullet 3"]}}

Return ONLY valid JSON, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.7, "max_output_tokens": 500}
            )

            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result.get('bullets', [])

        except Exception as e:
            print(f"Error in generate_resume_bullets: {e}")
            return [
                f"Completed {item_data.get('title')} demonstrating proficiency in {', '.join(item_data.get('skills', ['various skills']))}",
                f"Applied technical knowledge to solve real-world problems in {item_data.get('item_type')} context"
            ]

    def generate_linkedin_content(self, user_context: Dict) -> Dict:
        """
        Generate high-engagement LinkedIn post ideas and profile updates
        """
        prompt = f"""
        You are writing high-impact LinkedIn posts for a tech student.

        Student Profile:
        - Recent achievements: {', '.join(user_context.get('recent_achievements', []))}
        - Current Skills: {', '.join(user_context.get('current_skills', []))}
        - New skills: {', '.join(user_context.get('new_skills', []))}
        - Career goal: {user_context.get('career_goal', 'Professional development')}
        - Current phase: {user_context.get('current_phase', 'Learning')}

        ### NEGATIVE CONSTRAINTS (DO NOT DO THIS):
        - ❌ NEVER start a post with "Excited to share", "Thrilled to announce", or "Delighted to say".
        - ❌ Avoid generic advice like "Consistency is key" or "Keep grinding".
        - ❌ Do not use emojis in the hashtags.

        ### GOLD STANDARD EXAMPLE (MIMIC THIS DEPTH):
        "College syllabuses are often 5 years behind. I spent 12 hours a day in lectures learning outdated concepts while the industry moved to LLM orchestration. That’s why I built a custom RAG pipeline using LangChain and Pinecone. The hardest part wasn't the code; it was managing the context window limit. This project taught me more about vector databases than my entire semester."

        ### TASK:
        Generate:
        1. **Post Ideas**: 3 LinkedIn post ideas. The 'draft' MUST be a cohesive, first-person narrative (approx 150-200 words) using the "Problem-Agitation-Solution" framework. Mention specific tools from their skills list.
        2. **Profile Summary**: A 2-3 sentence professional summary.
        3. **Skills to Add**: 5-7 skills they should add.

        Format as JSON:
        {{
          "post_ideas": [
            {{
                "topic": "Short punchy topic", 
                "draft": "The full ~200 word post content...", 
                "hashtags": ["tag1", "tag2"]
            }},
            ...
          ],
          "profile_summary": "...",
          "skills_to_add": ["..."]
        }}
        """

        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # FIX 1: Parse the JSON string into a Python Dictionary
            return json.loads(response.text)

        except Exception as e:
            print(f"Error in generate_linkedin_content: {e}")
            # Fallback in case of error
            return {
                "post_ideas": [
                    {
                        "topic": "Error Generation",
                        "draft": f"I'm currently deep-diving into {user_context.get('career_goal')}. It's challenging but rewarding to build with {', '.join(user_context.get('current_skills', [])[:3])}.",
                        "hashtags": ["tech", "learning"]
                    }
                ],
                "profile_summary": "Aspiring technologist focused on continuous improvement.",
                "skills_to_add": []
            }

    # Override with richer prompt for personalization
    def generate_linkedin_content(self, user_context: Dict) -> Dict:
        """
        Generate richer LinkedIn post ideas and profile updates (overrides earlier version)
        """
        # Replace the prompt block inside generate_linkedin_content with this:
        prompt = f"""
        You are writing LinkedIn posts for a student in tech.

        Profile:
        - Name: {user_context.get('name', '')}
        - Major: {user_context.get('major', 'Not specified')}
        - University: {user_context.get('university', 'Not specified')}
        - Experience level: {user_context.get('experience_level', 'Not specified')}
        - Career goal: {user_context.get('career_goal', 'Professional development')}
        - Career aspirations: {user_context.get('career_aspirations', '')}
        - Target industries: {', '.join(user_context.get('target_industries', []))}
        - Current skills: {', '.join(user_context.get('current_skills', []))}
        - Recent achievements: {user_context.get('recent_achievements', [])}

        Write posts similar in depth and structure to this style (DO NOT copy content, just the pattern):

        Example Structure:
        - Hook: 1 punchy sentence calling out a real frustration or insight.
        - Problem: 2–3 sentences describing what’s broken or confusing today.
        - Solution: 2–3 sentences describing what the student built/learned/is doing.
        - How it works: 3–5 sentences with specific tools, APIs, stacks, or concepts.
        - Technical win: 2–3 sentences highlighting what they learned technically.
        - Vision: 2–3 sentences about why this matters for students / their career.
        - CTA: 1 sentence asking a genuine question to the audience.
        - Hashtags: 7–10 relevant hashtags, no emojis in hashtags.

        Generate 3 post ideas, each with this JSON structure:

        {{
        "post_ideas": [
            {{
            "topic": "Short topic line",
            "hook": "1 sentence hook",
            "problem": "2-3 sentences explaining the problem.",
            "solution": "2-3 sentences explaining their approach or tool.",
            "how_it_works": "3-5 sentences with concrete technical details (APIs, frameworks, models, datasets, etc.) tailored to their profile.",
            "technical_win": "2-3 sentences about what they learned technically.",
            "vision": "2-3 sentences about the bigger picture or impact.",
            "cta": "1 sentence question to invite replies.",
            "draft": "A single LinkedIn-ready post that weaves all of the above into 160-220 words, in first person, friendly but professional.",
            "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"]
            }},
            ...
         ],
         "profile_summary": "3-4 sentence summary tailored to their major, target industries, and recent achievements.",
         "skills_to_add": ["skill1", "skill2", ...]
        }}

        Requirements:
        - The "draft" must read like a complete LinkedIn post similar in richness and length to the example, not bullet points.
        - Use specific tools/skills relevant to the profile (for example: Python, Flask, Gemini AI, cybersecurity, etc., if they fit the user's data).
        - Always return ONLY valid JSON, no markdown, no extra text.
        """


        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.8, "max_output_tokens": 1200}
            )

            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error in generate_linkedin_content: {e}")
            return {
                "post_ideas": [
                    {
                        "topic": "Learning Journey",
                        "draft": f"Excited to share my progress in {user_context.get('career_goal', 'my career development')}! Recently completed projects are helping me deepen skills in {', '.join(user_context.get('current_skills', []))}.",
                        "angle": "Shows consistent growth and applied learning",
                        "call_to_action": "What resources helped you level up in this area?",
                        "hashtags": ["learning", "growth", "career"]
                    }
                ],
                "profile_summary": f"Aspiring professional focused on {user_context.get('career_goal', 'continuous learning')} with hands-on experience in recent projects.",
                "skills_to_add": user_context.get('new_skills', ["Problem Solving", "Project Management"])
            }

    def _get_simulated_trends(self, career_field: str) -> str:
        """
        Generate simulated industry trends
        """
        common_trends = """
Current Industry Trends (2025-2026):
- AI and Machine Learning integration across all sectors
- Cloud computing and distributed systems dominance
- Data privacy and cybersecurity critical importance
- Remote work and digital collaboration tools
- Sustainability and green technology focus
- API-first and microservices architectures
- Low-code/no-code platforms emergence
"""
        return common_trends

    def generate_growth_path_extension(self, profile_data: Dict, analysis: Dict, 
                                       completed_items: List[Dict], current_phase: int,
                                       planning_horizon_years: int = 1) -> Dict:
        """
        Generate next phase of growth path based on completed progress
        """
        target_role = analysis.get('career_paths', ['Professional'])[0]
        
        completed_summary = "\n".join([
            f"- {item['name']} ({item['type']})" 
            for item in completed_items[-10:]  # Last 10 completed items
        ])

        prompt = f"""
You are an expert educational and career strategist extending a personalized growth roadmap.

Student Profile:
- Major: {profile_data.get('major')}
- Target Role: {target_role}
- Target Industries: {', '.join(profile_data.get('target_industries', []))}
- Current Skills: {', '.join(profile_data.get('current_skills', []))}
- Time Commitment: {profile_data.get('time_commitment')}

Recently Completed Items:
{completed_summary}

Task: Generate Phase {current_phase} (Year {current_phase}) of the growth plan, building on the completed work.

This phase should:
1. Build upon skills gained from completed items
2. Progress to more advanced topics/projects
3. Include next-level courses, certifications, internships, and projects
4. Align with the target role and industries
5. Include a weekly routine that fits the time commitment

Format as JSON with this EXACT structure (single phase object, not wrapped in "phases" array):
{{
  "phase": {current_phase},
  "title": "Year {current_phase}: [Theme Name]",
  "focus": "Main focus of this year",
  "weekly_routine": "Sample weekly schedule",
  "courses": [
    {{
      "id": "c{current_phase}1",
      "name": "Course Name",
      "platform": "Platform Name",
      "duration": "X weeks",
      "rationale": "Why this course"
    }}
  ],
  "tests": [
    {{
      "id": "t{current_phase}1",
      "name": "Test Name",
      "target_score": "Score or Grade",
      "timing": "When to take",
      "rationale": "Why this test"
    }}
  ],
  "internships": [
    {{
      "id": "i{current_phase}1",
      "type": "Internship Type",
      "when": "Application timeline",
      "companies": ["Company examples"],
      "rationale": "Why this internship"
    }}
  ],
  "certificates": [
    {{
      "id": "cert{current_phase}1",
      "name": "Certificate Name",
      "provider": "Provider Name",
      "timing": "When to get",
      "rationale": "Why this certificate"
    }}
  ],
  "projects": [
    {{
      "id": "p{current_phase}1",
      "name": "Project Name",
      "description": "Project description",
      "skills_demonstrated": ["skill1", "skill2"],
      "rationale": "Why this project"
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            response_text = response.text.strip()
            
            # Clean response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            
            # Validate that we got a phase with items
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            if 'phase' not in result:
                raise ValueError("Response missing 'phase' field")
            
            # Ensure all category arrays exist (even if empty)
            for category in ['courses', 'tests', 'internships', 'certificates', 'projects']:
                if category not in result:
                    result[category] = []
                    print(f"Warning: {category} missing from response, adding empty array")
            
            # Log what was generated
            total_items = sum(len(result.get(cat, [])) for cat in ['courses', 'tests', 'internships', 'certificates', 'projects'])
            print(f"Generated phase {result.get('phase')} with {total_items} total items")
            
            return result

        except json.JSONDecodeError as e:
            print(f"JSON decode error in generate_growth_path_extension: {e}")
            print(f"Response text: {response_text[:500]}")  # First 500 chars
            raise
        except Exception as e:
            print(f"Error in generate_growth_path_extension: {e}")
            import traceback
            traceback.print_exc()
            # Return a simple fallback phase with at least some items
            return {
                "phase": current_phase,
                "title": f"Year {current_phase}: Advanced Development",
                "focus": "Building on completed foundations",
                "weekly_routine": "Continue learning and building projects",
                "courses": [
                    {
                        "id": f"c{current_phase}1",
                        "name": "Advanced Course",
                        "platform": "TBD",
                        "duration": "8 weeks",
                        "rationale": "Continue skill development"
                    }
                ],
                "tests": [],
                "internships": [],
                "certificates": [],
                "projects": [
                    {
                        "id": f"p{current_phase}1",
                        "name": "Advanced Project",
                        "description": "Build on previous skills",
                        "skills_demonstrated": ["Advanced Skills"],
                        "rationale": "Apply learned concepts"
                    }
                ]
            }

    def _get_fallback_roadmap(self, target_role: str) -> Dict:
        """
        Fallback roadmap if Gemini fails
        """
        return {
            "phases": [
                {
                    "phase": 1,
                    "title": "Foundation Building (Months 1-3)",
                    "focus": "Build core fundamentals",
                    "courses": [
                        {
                            "id": "c1",
                            "name": "Introduction to Programming",
                            "platform": "Coursera",
                            "duration": "4 weeks",
                            "rationale": "Essential programming foundation"
                        }
                    ],
                    "tests": [],
                    "internships": [],
                    "certificates": [],
                    "projects": [
                        {
                            "id": "p1",
                            "name": "Personal Portfolio Website",
                            "description": "Build a professional portfolio",
                            "skills_demonstrated": ["HTML", "CSS", "JavaScript"],
                            "rationale": "Demonstrate web development skills"
                        }
                    ]
                }
            ]
        }