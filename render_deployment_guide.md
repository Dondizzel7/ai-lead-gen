# Render Deployment Guide for Lead Generation Software

This guide explains how to deploy the Lead Generation Software with Autonomous AI Agents on Render.com.

## Prerequisites

- GitHub account
- Render.com account (free tier available)
- Your lead generation software code ready to deploy

## Step 1: Prepare Your Repository

1. Make sure your code is in a GitHub repository
2. Ensure your project structure has separate frontend and backend folders
3. Verify that package.json files exist in both folders

## Step 2: Set Up Database on Render

1. Log in to your Render dashboard
2. Click "New" and select "PostgreSQL"
3. Configure your database:
   - Name: leadgen-db
   - Database: leadgen
   - User: leadgen_user
   - Select the free plan
4. Click "Create Database"
5. Save the internal database URL for later use

## Step 3: Deploy Backend Service

1. From your Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - Name: leadgen-backend
   - Root Directory: backend
   - Runtime: Node
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Select the free plan
4. Add environment variables:
   - DATABASE_URL: (your database URL from step 2)
   - JWT_SECRET: (generate a random string)
   - NODE_ENV: production
   - PORT: 8080
5. Click "Create Web Service"
6. Wait for deployment to complete and note the service URL

## Step 4: Deploy Frontend

1. From your Render dashboard, click "New" and select "Static Site"
2. Connect your GitHub repository
3. Configure the static site:
   - Name: leadgen-frontend
   - Root Directory: frontend
   - Build Command: `npm install && npm run build`
   - Publish Directory: dist
4. Add environment variables:
   - VITE_API_URL: (your backend service URL from step 3)
5. Click "Create Static Site"
6. Wait for deployment to complete

## Step 5: Create Admin User

1. Access your backend service URL and add "/api/setup" to create an admin account
2. Fill in the required information to create your admin user
3. Use these credentials to log in to your application

## Troubleshooting

- Check service logs in the Render dashboard for any errors
- Verify environment variables are correctly set
- Ensure your database connection is working properly
- If needed, use "Manual Deploy" with "Clear Build Cache" option

## Maintenance

- Render automatically deploys when you push changes to your GitHub repository
- Monitor your usage to stay within free tier limits or upgrade as needed
- Regularly backup your database using Render's backup feature
