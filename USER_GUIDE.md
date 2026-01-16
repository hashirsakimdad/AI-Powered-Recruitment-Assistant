# 📘 AI Recruit - Complete User Guide

**Version 1.0** | **Last Updated: January 2026**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Landing Page](#landing-page)
4. [For Candidates](#for-candidates)
5. [For Recruiters](#for-recruiters)
6. [AI Features Explained](#ai-features-explained)
7. [User Interface Features](#user-interface-features)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions](#frequently-asked-questions)
10. [Tips & Best Practices](#tips--best-practices)
11. [Keyboard Shortcuts](#keyboard-shortcuts)
12. [Account Management](#account-management)

---

## Introduction

### What is AI Recruit?

AI Recruit is an intelligent, AI-powered resume screening and recruitment platform that revolutionizes the hiring process. It uses advanced machine learning and natural language processing to:

- **Automatically analyze resumes** against job requirements
- **Score and rank candidates** based on multiple factors
- **Provide personalized feedback** to help candidates improve
- **Streamline recruitment** for hiring managers

### Key Benefits

**For Candidates:**
- Get instant AI-powered feedback on your resume
- Understand how well you match job requirements
- Receive actionable suggestions for improvement
- Track all your applications in one place

**For Recruiters:**
- Automatically rank candidates by match score
- Save time with intelligent resume screening
- Export candidate data for further analysis
- Manage multiple job postings efficiently

---

## Getting Started

### System Requirements

- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet Connection**: Stable connection for real-time processing
- **Resume Format**: PDF files only (for uploads)

### Creating Your Account

#### Step 1: Access the Sign-Up Page

1. Navigate to the landing page at `http://localhost:5000` (or your server URL)
2. Click the **"Get Started"** button in the hero section
3. Or click **"Sign In"** and then select **"Sign up"** link

#### Step 2: Fill in Registration Details

1. **Email Address**: Enter a valid email address
   - This will be your login username
   - Must be unique (not already registered)

2. **Password**: Create a secure password
   - Minimum 6 characters required
   - Use a mix of letters, numbers, and symbols for security

3. **Confirm Password**: Re-enter your password exactly
   - Must match the password field

4. **Role Selection**: Choose your role
   - **Candidate**: If you're looking for jobs and want to upload resumes
   - **Recruiter**: If you're hiring and want to post jobs and review candidates

#### Step 3: Complete Registration

1. Click **"Sign Up"** button
2. If successful, you'll see: "Account created successfully! Please login."
3. You'll be redirected to the login page

#### Step 4: Login

1. Enter your email and password
2. Click **"Sign In"**
3. You'll be redirected to your dashboard based on your role

### Demo Accounts

For testing purposes, the following demo accounts are available:

**Recruiter Account:**
- Email: `recruiter@example.com`
- Password: `recruiter123`

**Candidate Account:**
- Email: `candidate@example.com`
- Password: `candidate123`

---

## Landing Page

### Overview

The landing page is your first impression of AI Recruit. It features:

- **3D Galaxy Animation**: A stunning animated background with stars and particles
- **Hero Section**: Main call-to-action and platform introduction
- **Feature Highlights**: Key capabilities of the platform
- **How It Works**: Step-by-step process explanation

### Navigation

**Top Section:**
- **"Get Started"** button → Takes you to sign-up page
- **"Sign In"** button → Takes you to login page

**Feature Cards:**
- **Smart Detection**: AI-powered resume validation
- **AI Analysis**: Deep semantic analysis for matching
- **Personalized Feedback**: Tailored suggestions for improvement

**How It Works Section:**
1. **Upload Resume**: Drag and drop your PDF resume
2. **AI Analysis**: Advanced ML models analyze your qualifications
3. **Get Feedback**: Receive personalized, actionable feedback

### Visual Features

- **Galaxy Animation**: Interactive 3D background that responds to cursor movement
- **Smooth Animations**: Fade-in effects and hover interactions
- **Responsive Design**: Adapts to all screen sizes

---

## For Candidates

### Candidate Dashboard

#### Overview

The Candidate Dashboard is your central hub for:
- Discovering available job postings
- Searching and filtering jobs
- Viewing your application history
- Tracking your match scores

#### Accessing the Dashboard

1. Log in with your candidate account
2. You'll be automatically redirected to `/candidate/dashboard`
3. Or click **"My Dashboard"** in the navigation bar

### Job Search & Discovery

#### Search Functionality

**Basic Search:**
1. Locate the search bar at the top of the dashboard
2. Enter keywords such as:
   - Job titles (e.g., "Software Engineer")
   - Skills (e.g., "Python", "React")
   - Company names
   - Job descriptions
3. Click **"Search Jobs"** or press Enter

**Advanced Filters:**

1. **Job Type Filter:**
   - **All Types**: Shows all job types
   - **Full-time**: Permanent full-time positions
   - **Part-time**: Part-time positions
   - **Internship**: Internship opportunities
   - **Contract**: Contract-based roles

2. **Work Mode Filter:**
   - **All Modes**: Shows all work modes
   - **Remote**: Fully remote positions
   - **Onsite**: Office-based positions
   - **Hybrid**: Combination of remote and onsite

3. **Combining Filters:**
   - Use search + filters together for precise results
   - Example: Search "Python" + Filter "Remote" + Filter "Full-time"

**Reset Filters:**
- Click **"Reset"** button to clear all filters and show all jobs

### Viewing Job Details

#### From Job List

1. Click **"View Details"** on any job card
2. Or click the job title (blue link)
3. You'll see a detailed job page with:
   - Full job description
   - Required skills (highlighted)
   - Company information
   - Location and work mode
   - Experience level
   - Posting date

#### Job Details Page Features

**Information Displayed:**
- **Job Title**: Clear, prominent heading
- **Company Name**: With building icon
- **Location**: With location pin icon
- **Job Type Badges**: Color-coded badges for:
  - Job Type (Full-time, Part-time, etc.)
  - Work Mode (Remote, Onsite, Hybrid)
  - Experience Level (Entry, Mid, Senior, Executive)
- **Posting Date**: When the job was posted
- **Full Description**: Complete job requirements and responsibilities
- **Required Skills**: All skills listed as badges

**Apply Button:**
- Large, prominent **"Apply for This Position"** button
- Opens the application modal

### Applying for Jobs

#### Step 1: Open Application Modal

**From Job List:**
1. Click **"Apply Now"** button on any job card
2. Application modal opens

**From Job Details:**
1. Scroll to bottom of job details page
2. Click **"Apply for This Position"** button
3. Application modal opens

#### Step 2: Fill Application Form

**Required Information:**

1. **Full Name:**
   - Enter your complete name
   - Example: "John Doe"
   - This appears in recruiter dashboard

2. **Email Address:**
   - Enter a valid email address
   - Example: "john@example.com"
   - Used for communication

3. **Resume Upload:**
   - **Format**: PDF only
   - **Methods**:
     - **Drag & Drop**: Drag your PDF file into the upload area
     - **Browse**: Click "Browse Files" button to select from computer
   - **Validation**: System automatically validates it's a resume

#### Step 3: Submit Application

1. Review all information
2. Click **"Upload & Analyze"** button
3. Wait for processing (usually 5-15 seconds)
4. You'll see a success message with your match score
5. Modal closes automatically

#### Upload Process

**What Happens:**
1. **File Validation**: System checks if file is PDF
2. **Resume Detection**: AI validates it's actually a resume (not a random document)
3. **Text Extraction**: Extracts all text from PDF
4. **AI Analysis**: 
   - Parses resume sections (skills, experience, education)
   - Calculates semantic similarity with job requirements
   - Scores skill alignment
   - Generates personalized feedback
5. **Score Calculation**: Final match score (0-100%)
6. **Storage**: Resume and analysis saved to database

**Progress Indicators:**
- Progress bar shows processing status
- Status text updates: "Processing..." → "Analyzing..." → "Complete"

### Viewing Application Results

#### From Dashboard

**My Applications Section:**
- Located on the right side of the dashboard
- Shows all your submitted applications
- Displays in reverse chronological order (newest first)

#### Application Card Information

**Header:**
- **Job Title**: Name of the position you applied for
- **Submission Date**: When you applied (date and time)

**Match Score Badge:**
- **Color Coding**:
  - 🟢 **Green (70%+)**: Excellent match
  - 🟡 **Yellow (50-69%)**: Good match
  - 🔴 **Red (<50%)**: Needs improvement
- **Score Display**: Shows percentage (e.g., "85% Match")

**View Details Button:**
- Click to expand detailed feedback
- Collapsible section with comprehensive analysis

#### Detailed Feedback View

**Score Breakdown:**
- **Semantic Score**: How well your resume text matches job description
- **Skill Alignment**: Percentage of required skills you have

**AI Summary:**
- Overall assessment of your match
- Highlights strengths and areas for improvement

**AI Suggestions:**
- **Actionable Recommendations**: Specific steps to improve
- **Missing Skills**: Skills required but not in your resume
- **Improvement Areas**: Sections that need enhancement

**Example Suggestions:**
- "Add more details about your Python projects"
- "Highlight your AWS certification more prominently"
- "Include specific metrics for your achievements"

### Understanding Match Scores

#### Score Ranges

**90-100%**: Exceptional Match
- Your resume strongly aligns with job requirements
- High likelihood of being shortlisted
- Minor improvements possible

**70-89%**: Strong Match
- Good alignment with most requirements
- Competitive candidate
- Some skills may need emphasis

**50-69%**: Moderate Match
- Basic requirements met
- Some gaps in skills or experience
- Significant improvements recommended

**Below 50%**: Weak Match
- Major gaps in requirements
- Consider if this role is right for you
- Substantial resume improvements needed

#### Improving Your Score

**Based on Feedback:**
1. **Add Missing Skills**: Include skills mentioned in job requirements
2. **Enhance Descriptions**: Add more detail to experience sections
3. **Highlight Relevant Experience**: Emphasize projects/roles related to job
4. **Update Resume Format**: Ensure all sections are clearly structured
5. **Include Certifications**: Add relevant certifications and training

### Managing Applications

#### Viewing All Applications

- All applications appear in "My Applications" section
- Sorted by submission date (newest first)
- Each shows job title, date, and match score

#### Re-applying to Same Job

- You can apply multiple times to the same job
- Each application is tracked separately
- Useful if you've updated your resume

#### Tracking Status

- Applications show in recruiter dashboard
- Recruiters can update status (Pending, Shortlisted, Selected, Rejected)
- Status updates visible in your dashboard (if recruiter updates)

---

## For Recruiters

### Recruiter Dashboard

#### Overview

The Recruiter Dashboard is your command center for:
- Managing job postings
- Reviewing candidate applications
- Ranking candidates by AI match score
- Exporting candidate reports
- Making hiring decisions

#### Accessing the Dashboard

1. Log in with your recruiter account
2. Automatically redirected to `/recruiter/dashboard`
3. Or click **"Dashboard"** in navigation bar

### Creating Job Postings

#### Step 1: Access Job Creation

**Methods:**
1. Click **"Create New Job"** button (top right of dashboard)
2. Or navigate to `/recruiter/jobs/new`

#### Step 2: Fill Job Details Form

**Required Fields:**

1. **Job Title** ⭐
   - Clear, descriptive title
   - Example: "Senior Software Engineer"
   - Appears in candidate searches

2. **Required Skills** ⭐
   - Comma-separated list
   - Example: "Python, SQL, React, AWS, Docker"
   - Used for AI matching
   - Be specific and comprehensive

3. **Job Description** ⭐
   - Detailed description of:
     - Role responsibilities
     - Required qualifications
     - Preferred experience
     - Company culture
   - More detail = better AI matching
   - Minimum 100 words recommended

**Optional Fields:**

4. **Company Name**
   - Your company or organization name
   - Example: "Tech Innovations Inc."

5. **Location**
   - City, State, or "Remote"
   - Example: "San Francisco, CA" or "Remote"

6. **Job Type**
   - **Full-time**: Permanent, full-time position
   - **Part-time**: Part-time position
   - **Internship**: Internship opportunity
   - **Contract**: Contract-based role
   - Default: Full-time

7. **Work Mode**
   - **Remote**: Fully remote work
   - **Onsite**: Office-based work
   - **Hybrid**: Combination of remote and onsite
   - Default: Onsite

8. **Experience Level**
   - **Entry Level**: 0-2 years experience
   - **Mid Level**: 2-5 years experience
   - **Senior Level**: 5+ years experience
   - **Executive**: Leadership roles
   - **Any Level**: No specific requirement

#### Step 3: Submit Job Posting

1. Review all information
2. Click **"Create Job Posting"** button
3. Success message appears: "Job created"
4. Redirected to dashboard
5. Job appears in "My Job Postings" sidebar

#### Best Practices for Job Postings

**Writing Effective Job Descriptions:**

1. **Be Specific**: 
   - Use exact skill names (e.g., "Python 3.8+" not just "programming")
   - Include specific technologies and tools

2. **Include Context**:
   - What the role involves day-to-day
   - Team structure and collaboration
   - Growth opportunities

3. **List All Requirements**:
   - Technical skills
   - Soft skills
   - Education requirements
   - Years of experience

4. **Use Keywords**:
   - Include terms candidates might search for
   - Industry-standard terminology

**Skills List Tips:**

- **Be Comprehensive**: List all important skills
- **Use Standard Names**: "JavaScript" not "JS", "React.js" not "ReactJS"
- **Include Related Skills**: "Python, Django, Flask" (related frameworks)
- **Separate Clearly**: Use commas, avoid special characters

### Managing Job Postings

#### Viewing Your Jobs

**Sidebar Section:**
- Left side of dashboard shows "My Job Postings"
- Lists all jobs you've created
- Shows job title and ID
- Displays description preview (first 100 characters)

**Job Card Information:**
- **Job Title**: Clickable link
- **Job ID**: Unique identifier
- **Description Preview**: Truncated description
- **Export CSV Button**: Download candidate report

#### Exporting Candidate Reports

**For Each Job:**

1. Find the job in "My Job Postings" sidebar
2. Click **"Export CSV"** button on job card
3. CSV file downloads automatically
4. File name: `job_{job_id}_report.csv`

**CSV Contents:**
- **Column 1**: Candidate Name
- **Column 2**: Email Address
- **Column 3**: Match Score (percentage)
- **Column 4**: Submission Date/Time (ISO format)

**Using the Report:**
- Open in Excel, Google Sheets, or any spreadsheet software
- Sort by score to see top candidates
- Filter and analyze data
- Share with team members
- Import into other systems

### Reviewing Candidates

#### Candidate Ranking Table

**Location:**
- Main section of recruiter dashboard
- Right side (larger column)
- Title: "Candidate Ranking"

**Table Columns:**

1. **Candidate**: 
   - Avatar circle with initial
   - Full name (or "N/A" if not provided)

2. **Email**: 
   - Contact email address
   - Small, muted text

3. **Job Position**: 
   - Job title they applied for
   - Badge format

4. **Match Score**: 
   - Percentage score (0-100%)
   - Color-coded circle:
     - 🟢 Green: 70%+
     - 🟡 Yellow: 50-69%
     - 🔴 Red: <50%
   - Percentage displayed

5. **Status**: 
   - Current application status
   - Badge colors:
     - 🟢 **Selected**: Green badge
     - 🔵 **Shortlisted**: Blue badge
     - 🟡 **Under Review**: Yellow badge
     - 🔴 **Rejected**: Red badge
     - ⚪ **Pending**: Gray badge (default)

6. **Submitted**: 
   - Date of application
   - Format: MM/DD/YYYY

7. **Actions**: 
   - **View** button: Opens detailed candidate modal

**Sorting:**
- Candidates automatically sorted by match score (highest first)
- NULL scores appear last
- Sorting happens automatically on page load

#### Viewing Candidate Details

**Opening Candidate Modal:**

1. Click **"View"** button in Actions column
2. Large modal opens with comprehensive information
3. Modal title: "Resume Analysis - [Candidate Name]"

**Modal Sections:**

**1. Overall Match Score:**
- Large badge at top
- Color-coded (green/yellow/red)
- Percentage displayed prominently
- Progress bar visualization

**2. Score Breakdown:**
- **Semantic Similarity**: How well resume text matches job description
- **Skill Alignment**: Percentage of required skills present
- **Experience Bonus**: Additional points for relevant experience
- Each shown as card with percentage

**3. Resume Details:**

**Explicitly Listed Skills:**
- Skills directly mentioned in resume
- Green badges
- Shows up to 10 skills

**Inferred Skills:**
- Skills inferred from experience/projects
- Yellow badges
- Shows up to 10 skills
- Note: "These skills were inferred from the candidate's work experience and project descriptions."

**Experience:**
- Years of experience (if available)
- Extracted from resume

**4. AI Feedback:**

**Summary:**
- Overall assessment
- Highlighted in info alert box
- Key strengths and weaknesses

**Suggestions:**
- Actionable recommendations
- Up to 5 suggestions shown
- Bullet-point format with icons

**5. Decision Control:**

**Status Update Buttons:**
- **Shortlist** (Blue): Move to shortlist
- **Under Review** (Yellow): Mark as reviewing
- **Select** (Green): Mark as selected
- **Reject** (Red): Mark as rejected

**Actions:**
- **Close**: Close modal
- **Export Report**: Download CSV for this job

### Managing Candidate Status

#### Updating Status

**From Candidate Modal:**

1. Open candidate details (click "View")
2. Scroll to bottom of modal
3. Find "Decision Control" section
4. Click desired status button:
   - **Shortlist**: Candidate is promising
   - **Under Review**: Currently evaluating
   - **Select**: Chosen for next steps
   - **Reject**: Not proceeding with candidate
5. Status updates immediately
6. Badge in table updates automatically
7. No page refresh needed

**Status Meanings:**

- **Pending** (Default): New application, not yet reviewed
- **Shortlisted**: Promising candidate, keep in consideration
- **Under Review**: Actively evaluating this candidate
- **Selected**: Chosen candidate, proceed with hiring process
- **Rejected**: Not proceeding, candidate doesn't meet requirements

**Best Practices:**

- Update status as you review candidates
- Use "Under Review" for candidates you're actively considering
- "Shortlist" for promising candidates you want to revisit
- Update to "Selected" when making final decision
- Mark "Rejected" for candidates you won't proceed with

### Visual Analytics

#### Ranking Chart

**Location:**
- Below candidate ranking table
- Interactive bar chart
- Shows all candidates' scores visually

**Chart Features:**
- **X-Axis**: Candidate names
- **Y-Axis**: Match scores (0-100%)
- **Bars**: Color-coded by score range
- **Interactive**: Hover to see exact values

**Using the Chart:**
- Quickly identify top performers
- Compare candidates visually
- Spot score distribution patterns
- Identify candidates needing review

### Job Posting Management

#### Viewing All Postings

**Sidebar Display:**
- All your jobs listed vertically
- Scrollable if many jobs
- Each job shows:
  - Title
  - ID badge
  - Description preview
  - Export button

#### Job Information

**Job Card Shows:**
- **Title**: Full job title
- **ID**: Unique identifier (for reference)
- **Description**: First 100 characters
- **Export CSV**: Quick access to reports

#### Creating Multiple Jobs

- No limit on number of job postings
- Each job is independent
- Candidates apply to specific jobs
- Each job has its own candidate list

---

## AI Features Explained

### Resume Detection

#### How It Works

**Machine Learning Model:**
- Trained model with 100% accuracy
- Validates if uploaded document is actually a resume
- Prevents non-resume documents from being processed

**Detection Process:**
1. File uploaded
2. Text extracted from PDF
3. ML model analyzes text patterns
4. Checks for resume indicators:
   - Contact information
   - Work experience sections
   - Education sections
   - Skills lists
5. Returns validation result

**Fallback System:**
- If ML model unavailable, uses rule-based detection
- Checks for common resume keywords
- Validates document structure

#### Why It Matters

- **Prevents Errors**: Stops non-resume documents from being analyzed
- **Saves Time**: Only processes valid resumes
- **Improves Accuracy**: Ensures AI analyzes correct content

### Semantic Scoring

#### Understanding Semantic Similarity

**What It Means:**
- Measures how well your resume text matches job description
- Uses advanced NLP (Natural Language Processing)
- Goes beyond keyword matching

**How It Works:**
1. **Text Embedding**: Converts resume and job description to numerical vectors
2. **Similarity Calculation**: Measures distance between vectors
3. **Score Generation**: Converts similarity to percentage (0-100%)

**Fine-Tuned Model:**
- Custom-trained SentenceTransformer model
- Optimized for resume-job matching
- Understands context and meaning

**Example:**
- Job requires: "Experience with cloud computing platforms"
- Resume says: "Worked with AWS and Azure"
- High semantic score (even if exact words don't match)

### Skill Alignment

#### How Skills Are Matched

**Process:**
1. **Extraction**: AI extracts skills from both:
   - Job requirements (from "Required Skills" field)
   - Candidate resume (from skills section and experience)

2. **Normalization**: 
   - Standardizes skill names
   - Handles variations (e.g., "Python" = "Python 3" = "Python3")

3. **Matching**:
   - Direct matches: Skills explicitly listed
   - Inferred matches: Skills mentioned in experience/projects
   - Related matches: Similar or related technologies

4. **Calculation**:
   - Percentage = (Matched Skills / Total Required Skills) × 100

**Skill Types:**

**Explicit Skills:**
- Directly listed in resume skills section
- Easy to identify
- Shown with green badges

**Inferred Skills:**
- Extracted from job descriptions, projects, experience
- Example: "Built REST APIs" → infers "API Development"
- Shown with yellow badges

### Experience Analysis

#### How Experience Is Evaluated

**Extraction:**
- AI identifies work experience sections
- Extracts:
  - Job titles
  - Company names
  - Duration (dates)
  - Responsibilities
  - Technologies used

**Relevance Scoring:**
- Compares experience to job requirements
- Awards bonus points for:
  - Relevant job titles
  - Related industries
  - Similar responsibilities
  - Matching technologies

**Years Calculation:**
- Calculates total years of experience
- Compares to job requirements
- Factors into overall score

### Feedback Generation

#### Personalized Feedback System

**How Feedback Is Created:**

1. **Analysis Phase**:
   - Reviews resume sections
   - Compares to job requirements
   - Identifies gaps and strengths

2. **Score-Based Tailoring**:
   - High scores (70%+): Focus on minor improvements
   - Medium scores (50-69%): Highlight missing skills
   - Low scores (<50%): Comprehensive improvement suggestions

3. **Content-Aware Suggestions**:
   - Based on actual resume content
   - Specific to candidate's background
   - Actionable and relevant

**Feedback Categories:**

**Summary:**
- Overall assessment
- Key strengths
- Main areas for improvement

**Suggestions:**
- Specific actions to take
- Resume improvements
- Skill additions
- Formatting tips

**Missing Skills:**
- Required skills not in resume
- Prioritized by importance
- Actionable recommendations

### Scoring Algorithm

#### Score Components

**14+ Features Analyzed:**

1. **Semantic Similarity** (Weight: High)
   - Text matching between resume and job description

2. **Skill Alignment** (Weight: High)
   - Percentage of required skills present

3. **Experience Bonus** (Weight: Medium)
   - Relevance of work experience

4. **Education Match** (Weight: Medium)
   - Educational requirements alignment

5. **Certification Bonus** (Weight: Low)
   - Relevant certifications

6. **Project Relevance** (Weight: Medium)
   - Projects matching job requirements

7. **Keyword Density** (Weight: Low)
   - Frequency of important terms

8. **Section Completeness** (Weight: Low)
   - All resume sections present

9. **Experience Duration** (Weight: Medium)
   - Years of experience match

10. **Industry Match** (Weight: Medium)
    - Industry experience relevance

11. **Technology Stack** (Weight: High)
    - Technologies used match requirements

12. **Achievement Metrics** (Weight: Low)
    - Quantifiable achievements

13. **Language Proficiency** (Weight: Low)
    - Language skills if required

14. **Additional Factors** (Weight: Variable)
    - Other job-specific requirements

#### Final Score Calculation

**Formula:**
```
Final Score = (Semantic Score × 0.4) + 
              (Skill Alignment × 0.3) + 
              (Experience Bonus × 0.2) + 
              (Other Factors × 0.1)
```

**Normalization:**
- Scores normalized to 0-100% range
- Ensures consistent scoring across jobs
- Accounts for varying job requirements

---

## User Interface Features

### Dark Mode

#### Enabling Dark Mode

**Method 1: Navigation Menu**
1. Click **"Theme"** dropdown in navigation bar
2. Select **"Dark"** option
3. Theme changes immediately
4. Preference saved in session

**Method 2: Automatic Detection**
- System respects browser/OS dark mode preference
- Automatically switches if enabled

#### Dark Mode Features

**Color Scheme:**
- **Background**: Deep charcoal (#1a1f2e) - not pure black
- **Text**: Bright white (#f8fafc) for readability
- **Accents**: Brighter colors for visibility
- **Borders**: Visible gray borders

**Benefits:**
- Reduced eye strain in low light
- Better battery life on OLED screens
- Modern, professional appearance
- Consistent with galaxy animations

**Galaxy Animation:**
- Stars more visible in dark mode
- Enhanced glow effects
- Better contrast
- More immersive experience

### 3D Galaxy Animations

#### Landing Page Animation

**Features:**
- **400 Stars**: Rich starfield background
- **70 Particles**: Subtle particle clusters
- **6 Depth Layers**: Creates 3D depth effect
- **Parallax Effect**: Responds to cursor movement
- **Smooth Motion**: Cinematic, slow movement

**Interaction:**
- Move mouse to see parallax effect
- Stars move based on cursor position
- Creates immersive depth feeling
- Never interferes with content

**Performance:**
- Automatically reduces on low-end devices
- Respects reduced motion preferences
- Pauses when tab is inactive
- Optimized for smooth 60fps

#### Login Page Animation

**Features:**
- **280 Stars**: Lighter, refined version
- **45 Particles**: Subtle particle effects
- **Moderate Parallax**: Less intense than landing
- **Continuity**: Maintains visual language

**Purpose:**
- Seamless transition from landing page
- Maintains premium feel
- Doesn't distract from login form
- Professional, futuristic aesthetic

### Responsive Design

#### Mobile Optimization

**Features:**
- **Touch-Friendly**: Large buttons and tap targets
- **Responsive Layout**: Adapts to screen size
- **Optimized Animations**: Reduced effects on mobile
- **Readable Text**: Appropriate font sizes

**Breakpoints:**
- **Mobile**: < 768px (single column layout)
- **Tablet**: 768px - 992px (adjusted columns)
- **Desktop**: > 992px (full layout)

#### Tablet Support

- Optimized for iPad and Android tablets
- Touch gestures supported
- Responsive forms and modals
- Appropriate spacing and sizing

### Animations & Transitions

#### Page Transitions

- **Fade-In**: Smooth page load animations
- **Hover Effects**: Interactive button and card hovers
- **Modal Animations**: Smooth open/close transitions
- **Loading States**: Progress indicators during processing

#### Micro-Interactions

- **Button Hovers**: Color and scale changes
- **Card Lifts**: Subtle elevation on hover
- **Form Focus**: Highlighted input fields
- **Status Updates**: Smooth badge color changes

### Accessibility Features

#### Keyboard Navigation

- **Tab Navigation**: Navigate with Tab key
- **Enter to Submit**: Forms submit with Enter
- **Escape to Close**: Modals close with Esc
- **Arrow Keys**: Navigate dropdowns

#### Screen Reader Support

- Semantic HTML structure
- ARIA labels where needed
- Alt text for icons
- Form labels properly associated

#### Reduced Motion

- Respects `prefers-reduced-motion` setting
- Reduces animations if enabled
- Maintains functionality
- Still accessible and usable

---

## Troubleshooting

### Common Issues

#### Login Problems

**Issue: "Invalid credentials"**

**Solutions:**
1. Check email spelling (case-sensitive)
2. Verify password (no extra spaces)
3. Ensure account exists (try sign-up if new)
4. Check caps lock is off
5. Try demo accounts to test

**Issue: "Please login to access this page"**

**Solutions:**
1. Session may have expired
2. Log out and log back in
3. Clear browser cookies
4. Try different browser

#### Upload Problems

**Issue: "No file uploaded"**

**Solutions:**
1. Ensure file is selected
2. Check file size (not too large)
3. Try different file
4. Refresh page and try again

**Issue: "Upload failed: [error message]"**

**Common Errors:**
- **"Not a valid resume"**: File doesn't contain resume content
  - Solution: Ensure PDF is actually a resume
  - Check file isn't corrupted
  - Try re-saving resume

- **"File format not supported"**: Not a PDF
  - Solution: Convert to PDF format
  - Use PDF export from Word/Google Docs

- **"File too large"**: Exceeds size limit
  - Solution: Compress PDF
  - Reduce file size
  - Try smaller version

**Issue: Processing takes too long**

**Solutions:**
1. Wait 30-60 seconds (normal for complex resumes)
2. Check internet connection
3. Refresh page if stuck
4. Try uploading again

#### Score Issues

**Issue: Score seems incorrect**

**Possible Reasons:**
1. **Missing Skills**: Job requires skills not in resume
   - Solution: Add missing skills to resume

2. **Vague Description**: Job description too generic
   - Solution: Recruiter should add more detail

3. **Format Issues**: Resume not properly structured
   - Solution: Ensure clear sections (Skills, Experience, Education)

4. **Mismatch**: Resume genuinely doesn't match job
   - Solution: Apply to more relevant positions

**Issue: Score not appearing**

**Solutions:**
1. Wait for processing to complete
2. Refresh page
3. Check application was successful
4. Contact support if persists

#### Display Issues

**Issue: Page looks broken**

**Solutions:**
1. **Clear Browser Cache**: 
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

2. **Hard Refresh**: 
   - Windows: Ctrl+F5
   - Mac: Cmd+Shift+R

3. **Try Different Browser**: 
   - Chrome, Firefox, Safari, Edge

4. **Check JavaScript Enabled**: 
   - Ensure JS is not blocked

**Issue: Animations not working**

**Solutions:**
1. Check browser supports animations
2. Ensure JavaScript enabled
3. Try disabling browser extensions
4. Check reduced motion not enabled

**Issue: Dark mode not working**

**Solutions:**
1. Use theme dropdown in navigation
2. Clear browser cache
3. Check browser supports CSS variables
4. Try different browser

### Performance Issues

#### Slow Loading

**Causes:**
- Large number of jobs/candidates
- Slow internet connection
- Browser extensions interfering
- Old browser version

**Solutions:**
1. Wait for initial load (first time slower)
2. Check internet speed
3. Disable browser extensions
4. Update browser to latest version
5. Clear browser cache

#### Animation Lag

**Solutions:**
1. Animations auto-reduce on low-end devices
2. Close other browser tabs
3. Update graphics drivers
4. Use modern browser
5. Disable other animations if needed

### Browser Compatibility

#### Supported Browsers

**Recommended:**
- Chrome 90+ (Best support)
- Firefox 88+
- Safari 14+
- Edge 90+

**Minimum:**
- Chrome 80+
- Firefox 80+
- Safari 13+
- Edge 80+

#### Unsupported Features

**Older Browsers:**
- Some animations may not work
- Dark mode may have issues
- Some modern CSS features unavailable

**Solution:**
- Update to latest browser version
- Use recommended browsers

---

## Frequently Asked Questions

### General Questions

**Q: Is AI Recruit free to use?**
A: Yes, the platform is free for both candidates and recruiters. No subscription or payment required.

**Q: What file formats are supported for resumes?**
A: Currently, only PDF format is supported. This ensures consistent text extraction and analysis.

**Q: How accurate is the AI scoring?**
A: The AI uses advanced machine learning models with high accuracy. However, scores should be used as a guide alongside human judgment.

**Q: Can I delete my account?**
A: Account deletion is not currently available through the UI. Contact support if you need account removal.

**Q: Is my data secure?**
A: Yes, all data is stored securely. Resumes are only accessible to recruiters for jobs you apply to.

### For Candidates

**Q: Can I apply to multiple jobs?**
A: Yes, you can apply to as many jobs as you want. Each application is tracked separately.

**Q: Can I update my resume and re-apply?**
A: Yes, you can upload a new resume for the same job. Each application is tracked separately with its own score.

**Q: How long does resume analysis take?**
A: Typically 5-15 seconds, depending on resume complexity and server load.

**Q: Why is my score low?**
A: Low scores usually indicate:
- Missing required skills
- Insufficient relevant experience
- Resume doesn't match job requirements well
- Check AI feedback for specific improvements

**Q: Can I see what skills I'm missing?**
A: Yes, in the detailed feedback view, there's a "Missing Skills" section showing required skills not in your resume.

**Q: How do I improve my match score?**
A: Based on AI feedback:
1. Add missing required skills
2. Enhance experience descriptions
3. Highlight relevant projects
4. Include certifications
5. Improve resume structure

**Q: Can recruiters see my contact information?**
A: Yes, recruiters can see the name and email you provide when applying. This is necessary for them to contact you.

### For Recruiters

**Q: How many job postings can I create?**
A: There's no limit on the number of job postings you can create.

**Q: Can I edit a job posting after creating it?**
A: Job editing is not currently available. You can create a new job posting with updated information.

**Q: How are candidates ranked?**
A: Candidates are automatically ranked by AI match score (highest to lowest). Scores consider semantic similarity, skill alignment, and experience relevance.

**Q: Can I download candidate resumes?**
A: Resumes are stored in the system. You can view candidate details in the dashboard. CSV export includes candidate information but not the actual PDF files.

**Q: How do I contact candidates?**
A: Use the email address shown in the candidate details. The platform doesn't include built-in messaging.

**Q: Can multiple recruiters access the same account?**
A: Each account is individual. For team access, each recruiter should have their own account, or you can share login credentials (not recommended for security).

**Q: How accurate is the AI ranking?**
A: The AI provides highly accurate rankings based on multiple factors. However, always review top candidates manually to ensure fit.

**Q: Can I export all candidates at once?**
A: Currently, you can export candidates per job posting. Use the "Export CSV" button on each job card.

### Technical Questions

**Q: What browsers are supported?**
A: Modern browsers (Chrome, Firefox, Safari, Edge) with latest versions. See Browser Compatibility section.

**Q: Do I need to install anything?**
A: No, it's a web application. Just need a modern browser and internet connection.

**Q: Can I use it on mobile?**
A: Yes, the platform is fully responsive and works on mobile devices, though desktop is recommended for best experience.

**Q: Is my data stored locally?**
A: No, all data is stored on the server. You need internet connection to access your account and data.

**Q: How long is my data stored?**
A: Data is stored indefinitely until you request deletion or the account is removed.

---

## Tips & Best Practices

### For Candidates

#### Resume Preparation

**1. Format Your Resume Properly:**
- Use clear sections: Skills, Experience, Education
- Include contact information
- Use standard resume format
- Ensure PDF is readable (not scanned image)

**2. Include All Relevant Skills:**
- List skills explicitly in a "Skills" section
- Mention technologies in experience descriptions
- Include certifications and training
- Use standard skill names (e.g., "Python" not "python programming")

**3. Detail Your Experience:**
- Describe responsibilities clearly
- Mention technologies and tools used
- Include quantifiable achievements
- Highlight relevant projects

**4. Match Job Requirements:**
- Read job description carefully
- Include skills mentioned in requirements
- Emphasize relevant experience
- Tailor resume for each application (if possible)

#### Applying for Jobs

**1. Review Job Details:**
- Read full job description
- Check required skills
- Understand job requirements
- Ensure you're a good fit

**2. Use Accurate Information:**
- Provide correct name and email
- Use professional email address
- Ensure resume is up-to-date
- Double-check before submitting

**3. Apply to Relevant Jobs:**
- Focus on jobs matching your skills
- Don't apply to everything
- Quality over quantity
- Use search filters effectively

**4. Review Your Scores:**
- Check match scores after applying
- Read AI feedback carefully
- Use suggestions to improve
- Re-apply with updated resume if needed

#### Improving Your Profile

**1. Act on Feedback:**
- Add missing skills to resume
- Enhance descriptions based on suggestions
- Include recommended certifications
- Update resume format if needed

**2. Track Your Applications:**
- Monitor scores across applications
- Identify patterns in feedback
- Focus on improving weak areas
- Celebrate high scores

### For Recruiters

#### Writing Effective Job Postings

**1. Be Specific:**
- Use exact skill names
- Include specific technologies
- Mention required experience level
- Describe role clearly

**2. Comprehensive Descriptions:**
- Detail responsibilities
- Explain team structure
- Mention growth opportunities
- Include company culture

**3. Complete Skills List:**
- List all important skills
- Use standard names
- Include related technologies
- Separate with commas clearly

**4. Set Realistic Requirements:**
- Don't over-specify
- Focus on essential skills
- Consider experience levels
- Be clear about preferences vs. requirements

#### Reviewing Candidates

**1. Use AI Scores as Guide:**
- Review top-scoring candidates first
- Don't ignore lower scores (may have other strengths)
- Consider score breakdowns
- Use as initial filter, not final decision

**2. Read Detailed Feedback:**
- Check candidate details modal
- Review skill breakdown
- Read AI suggestions
- Consider inferred skills

**3. Update Status Regularly:**
- Mark candidates as you review
- Use "Under Review" for active candidates
- Shortlist promising candidates
- Reject clearly unsuitable candidates

**4. Export and Analyze:**
- Export CSV reports regularly
- Analyze score distributions
- Identify patterns
- Share with team if needed

#### Managing Multiple Jobs

**1. Organize Job Postings:**
- Use clear, descriptive titles
- Include company name in posting
- Add location information
- Keep descriptions updated

**2. Track Applications:**
- Review new applications regularly
- Update candidate statuses
- Export reports for record-keeping
- Follow up on shortlisted candidates

**3. Use Filters and Search:**
- Search candidates by name/email
- Filter by status
- Sort by score
- Organize workflow efficiently

---

## Keyboard Shortcuts

### General Navigation

- **Tab**: Navigate between form fields and buttons
- **Enter**: Submit forms, activate buttons
- **Esc**: Close modals, cancel actions
- **Arrow Keys**: Navigate dropdowns and lists

### Browser Shortcuts

- **Ctrl/Cmd + R**: Refresh page
- **Ctrl/Cmd + F5**: Hard refresh (clear cache)
- **Ctrl/Cmd + +/-**: Zoom in/out
- **F11**: Fullscreen mode

### Form Navigation

- **Tab**: Move to next field
- **Shift + Tab**: Move to previous field
- **Enter**: Submit form (when in text field)
- **Esc**: Cancel/close form

---

## Account Management

### Changing Password

**Current Limitation:**
- Password change not available in UI
- Contact support if needed
- Or create new account with same email (after deletion)

### Updating Email

**Current Limitation:**
- Email change not available in UI
- Email is your login username
- Contact support for email changes

### Logging Out

**Method:**
1. Click **"Logout"** button in navigation bar
2. Session cleared immediately
3. Redirected to login page
4. Must log in again to access dashboard

### Session Management

**Session Duration:**
- Sessions remain active while browser is open
- May expire after extended inactivity
- Log out and back in if session expires

**Multiple Devices:**
- Can log in from multiple devices
- Each device has separate session
- Log out from all devices for security

### Account Security

**Best Practices:**
1. Use strong, unique password
2. Don't share login credentials
3. Log out on shared computers
4. Use secure internet connection
5. Report suspicious activity

---

## Support & Contact

### Getting Help

**Documentation:**
- This user guide
- README.md for technical details
- In-app tooltips and help text

**Common Solutions:**
- Check Troubleshooting section
- Review FAQ
- Try solutions listed above

### Reporting Issues

**If You Encounter Problems:**
1. Note the exact error message
2. Record steps to reproduce
3. Check browser console for errors
4. Try solutions in Troubleshooting
5. Contact support with details

### Feature Requests

**Suggesting Improvements:**
- Note desired features
- Explain use case
- Consider if feature exists in different form
- Contact development team

---

## Appendix

### Glossary

**AI Match Score**: Percentage (0-100%) indicating how well a resume matches job requirements

**Semantic Similarity**: Measure of how similar the meaning of resume text is to job description

**Skill Alignment**: Percentage of required skills present in candidate's resume

**Explicit Skills**: Skills directly listed in resume skills section

**Inferred Skills**: Skills identified from experience descriptions and projects

**Status**: Current state of candidate application (Pending, Shortlisted, Selected, Rejected, Under Review)

**Parallax**: Visual effect where background moves slower than foreground, creating depth

**CSV Export**: Comma-separated values file format for data export

### Version History

**Version 1.0** (January 2026)
- Initial release
- Complete candidate and recruiter features
- AI-powered resume analysis
- 3D galaxy animations
- Dark mode support

### Credits

**Developed by:** Zeeshan & Co.
**Project:** Final Year Project (FYP)
**Technology:** Python, Flask, AI/ML

---

## Conclusion

Thank you for using AI Recruit! This guide covers all major features and functionality. For the best experience:

1. **Read job descriptions carefully** before applying
2. **Use AI feedback** to improve your resume
3. **Update candidate statuses** regularly as a recruiter
4. **Export reports** for record-keeping
5. **Explore all features** to maximize platform value

**Happy Recruiting! 🚀**

---

*This user guide is comprehensive and covers all aspects of the AI Recruit platform. For technical details, see README.md. For updates and new features, check the application changelog.*

**Last Updated:** January 2026
**Version:** 1.0
**Platform:** AI Recruit - AI-Powered Resume Screening & Recruitment Platform

