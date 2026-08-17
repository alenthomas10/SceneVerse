# SceneVerse

### Social Platform for Filmmakers and Artists

SceneVerse is a web-based social platform developed to bring filmmakers, artists, and other creative professionals together in one place. The platform allows users to create profiles, showcase their creative work, publish projects, create casting calls, apply for opportunities, and interact with other creators.

The system is designed to provide a dedicated digital space for the filmmaking community to discover talent, share creative work, and collaborate on projects.

---

## 📌 Project Overview

Finding suitable artists and creative professionals for filmmaking projects can be difficult when information is scattered across different social media platforms.

SceneVerse addresses this problem by providing a centralized platform where filmmakers and artists can:

- Create and manage professional profiles
- Showcase their creative projects
- Publish posts containing images and videos
- Create casting calls
- Discover casting opportunities
- Apply for available roles
- Like and comment on projects
- Connect with other creative professionals

The platform also provides an administrative interface for managing users and platform content.

---

## 🎯 Objectives

The main objectives of SceneVerse are:

- To create a dedicated social platform for filmmakers and artists.
- To provide artists with a space to showcase their work.
- To simplify the process of finding artists for filmmaking projects.
- To provide an organized casting-call and application system.
- To encourage collaboration among creative professionals.
- To provide an easy-to-use platform for sharing creative content.
- To provide administrators with tools to manage the platform.

---

## ✨ Key Features

### 👤 User Management

- User registration and login
- Secure user authentication
- User profile management
- Artist details and professional information
- Profile viewing and management

### 🎬 Project Management

- Create and publish projects
- View project details
- Manage personal projects
- Showcase filmmaking work
- Upload project-related media

### 🎭 Casting Calls

- Create casting calls
- Publish available roles
- View casting opportunities
- Submit applications for casting calls
- Manage received applications

### 📸 Social Posts

- Create posts
- Share images and videos
- View posts from other creators
- Like posts
- Comment on projects and posts

### 📊 Artist Dashboard

The artist dashboard provides users with a centralized place to manage their activities, including:

- Projects
- Posts
- Casting calls
- Applications
- Profile information

### 🛡️ Administration

Administrators can manage the platform and its users through the administrative interface.

Administrative functions include:

- User management
- Content management
- Project management
- Casting-call management
- Application management

---

## 🏗️ System Modules

The major modules of SceneVerse are:

1. **User Authentication Module**
2. **Artist Profile Module**
3. **Project Management Module**
4. **Casting Call Module**
5. **Application Module**
6. **Social Post Module**
7. **Like and Comment Module**
8. **Artist Dashboard Module**
9. **Admin Management Module**

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

### Backend

- Python
- Django

### Database

- SQLite

### Development Tools

- Visual Studio Code
- Git
- GitHub

---

## 🏛️ System Architecture

SceneVerse follows a web-based client-server architecture using the Django framework.

```text
┌───────────────────────────────┐
│           User                │
│     Web Browser / Client      │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          Frontend             │
│       HTML / CSS / JS         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Django Backend         │
│   Views / URLs / Application  │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│   Database   │  │ Media Files  │
│    SQLite    │  │ Images/Video │
└──────────────┘  └──────────────┘
