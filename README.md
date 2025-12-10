# Nash Wu 17 - Creator Portfolio

This is a personal branding website tailored for YouTuber / Creator **Nash Wu 17**.

This project is a static site hosted on GitHub Pages, utilizing **GitHub Actions** to automate YouTube video updates and **FormSubmit** for contact form handling without a backend server.

## 🚀 Features

### 📺 Content Integration
*   **YouTube Sync**: Automatically fetches the latest channel videos via YouTube Data API v3 using a scheduled Python script in GitHub Actions.
*   **Security**: API Keys and Channel IDs are stored in GitHub Secrets, never exposed in the frontend code.
*   **Infinite Carousel**: Custom video carousel with pagination and looping support.

### ⚡ Instant Contact Form
*   **Privacy**: Frontend does not expose your real email (when using FormSubmit random string).
*   **AJAX Submission**: Visitors can send messages without page reloads.

### 🎨 Design & Experience
*   **Minimalist Aesthetic**: Modern visual style built with Tailwind CSS.
*   **Responsive Design (RWD)**: Perfectly supports Mobile, Tablet, and Desktop.
*   **English Interface**: Global-friendly interface.

## 🛠️ Tech Stack

*   **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
*   **Automation**: Python, GitHub Actions
*   **Icons**: Lucide Icons
*   **Services**: YouTube Data API v3, FormSubmit

## 📝 Setup Guide

1.  **Push Code**: Upload these files to your GitHub Repository.
2.  **Configure Secrets**:
    *   Go to Settings > Secrets and variables > Actions.
    *   Add `YOUTUBE_API_KEY` and `CHANNEL_ID`.
3.  **Enable Pages**:
    *   Go to Settings > Pages.
    *   Select `main` branch as source.
4.  **Update Email**:
    *   Edit `index.html` and change `CONTACT_EMAIL` to your email or FormSubmit GUID.

## ⚠️ Copyright

**Original Design & Code.**

This website is designed for the Nash Wu 17 personal brand. Please do not copy or reproduce the visual design without permission.

---
© Nash Wu 17. All rights reserved.