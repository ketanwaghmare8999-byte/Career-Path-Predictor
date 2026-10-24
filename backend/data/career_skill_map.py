# career_skill_map.py
# Master mapping: career -> (required skills, related interests, description, learning resources)
# This is the "domain knowledge" used to (1) generate a synthetic training dataset
# for the ML model, and (2) run skill-gap analysis after prediction.

CAREER_SKILL_MAP = {
    "Software Developer": {
        "skills": ["Programming", "Problem Solving", "Logical Thinking", "Web Development", "Database Basics", "Debugging"],
        "interests": ["Technology", "Building Things"],
        "desc": "Builds websites, apps, and software.",
        "resources": "freeCodeCamp (Web Dev), CS50 (Harvard, free online), LeetCode practice"
    },
    "Data Scientist": {
        "skills": ["Programming", "Statistics", "Data Analysis", "Machine Learning", "Problem Solving", "Excel"],
        "interests": ["Technology", "Numbers & Data", "Research"],
        "desc": "Finds patterns in data to help businesses make better decisions.",
        "resources": "Kaggle Learn (free), Andrew Ng's ML course (Coursera), Python Pandas tutorials"
    },
    "UI/UX Designer": {
        "skills": ["Design Sense", "Creativity", "Communication", "User Research", "Wireframing"],
        "interests": ["Design & Art", "Technology", "People"],
        "desc": "Makes apps and websites beautiful and easy to use.",
        "resources": "Figma free tutorials, Google UX Design Certificate, Dribbble for inspiration"
    },
    "Digital Marketer": {
        "skills": ["Communication", "Creativity", "Social Media", "Content Writing", "Basic Analytics"],
        "interests": ["Marketing & Sales", "Communication", "Creativity"],
        "desc": "Grows a brand through social media, ads, and content.",
        "resources": "Google Digital Garage (free), HubSpot Academy, Meta Blueprint"
    },
    "Cybersecurity Analyst": {
        "skills": ["Networking", "Problem Solving", "Programming", "Attention to Detail", "Security Basics"],
        "interests": ["Technology", "Security", "Research"],
        "desc": "Protects a company's data and systems from hackers.",
        "resources": "TryHackMe (free labs), Cisco Networking Basics, CompTIA Security+ guide"
    },
    "Cloud Engineer": {
        "skills": ["Networking", "Programming", "Problem Solving", "Database Basics", "Linux Basics"],
        "interests": ["Technology", "Building Things"],
        "desc": "Sets up companies' servers and apps on the cloud (AWS/Azure).",
        "resources": "AWS Free Tier + AWS Educate, freeCodeCamp Cloud path"
    },
    "Business Analyst": {
        "skills": ["Data Analysis", "Communication", "Excel", "Problem Solving", "Presentation Skills"],
        "interests": ["Numbers & Data", "Business", "Communication"],
        "desc": "Studies company data and processes to help the business make better decisions.",
        "resources": "Excel free courses (YouTube), Google Data Analytics Certificate"
    },
    "Content Writer": {
        "skills": ["Communication", "Creativity", "Research", "Content Writing"],
        "interests": ["Writing", "Communication", "Creativity"],
        "desc": "Writes blogs, articles, and website content.",
        "resources": "HubSpot Content Marketing course (free), Grammarly for practice, Medium blogs"
    },
    "Mobile App Developer": {
        "skills": ["Programming", "Problem Solving", "Logical Thinking", "Design Sense", "Debugging"],
        "interests": ["Technology", "Building Things", "Design & Art"],
        "desc": "Builds mobile apps for Android/iOS.",
        "resources": "Android Developers free course, Flutter official docs, Kotlin Bootcamp (free)"
    },
    "AI/ML Engineer": {
        "skills": ["Programming", "Statistics", "Machine Learning", "Data Analysis", "Problem Solving"],
        "interests": ["Technology", "Numbers & Data", "Research"],
        "desc": "Builds systems that can learn and improve on their own.",
        "resources": "Andrew Ng ML/DL specialization, fast.ai (free), Kaggle competitions"
    },
    "Graphic Designer": {
        "skills": ["Design Sense", "Creativity", "Attention to Detail"],
        "interests": ["Design & Art", "Creativity"],
        "desc": "Designs posters, logos, and visuals.",
        "resources": "Canva Design School (free), Adobe free tutorials, Behance for inspiration"
    },
    "Product Manager": {
        "skills": ["Communication", "Problem Solving", "Presentation Skills", "Data Analysis", "Leadership"],
        "interests": ["Business", "Technology", "People"],
        "desc": "Coordinates a team to plan and launch a product.",
        "resources": "Product School free resources, Coursera 'Digital Product Management'"
    },
}

ALL_SKILLS = sorted({s for v in CAREER_SKILL_MAP.values() for s in v["skills"]})
ALL_INTERESTS = sorted({i for v in CAREER_SKILL_MAP.values() for i in v["interests"]})
ALL_CAREERS = sorted(CAREER_SKILL_MAP.keys())
