// Web Application Configuration for Autonomous Recruitment System
// This file defines the core configuration for the web application deployment

module.exports = {
  // Application settings
  app: {
    name: 'Autonomous Recruitment System',
    description: 'AI-powered autonomous recruitment platform',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    port: process.env.PORT || 3000,
    apiUrl: process.env.API_URL || '/api',
    frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
    corsOrigins: process.env.CORS_ORIGINS || '*'
  },
  
  // Authentication settings
  auth: {
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-for-development-only',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshTokenExpiresIn: process.env.REFRESH_TOKEN_EXPIRES_IN || '30d',
    saltRounds: 10,
    passwordResetExpires: 3600000 // 1 hour
  },
  
  // Database settings
  database: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/recruitment-system',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      autoIndex: true
    }
  },
  
  // Email settings
  email: {
    from: process.env.EMAIL_FROM || 'noreply@autonomous-recruitment.com',
    smtp: {
      host: process.env.SMTP_HOST || 'smtp.example.com',
      port: process.env.SMTP_PORT || 587,
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER || '',
        pass: process.env.SMTP_PASS || ''
      }
    }
  },
  
  // Storage settings
  storage: {
    type: process.env.STORAGE_TYPE || 'local', // 'local', 's3', 'azure'
    local: {
      uploadDir: process.env.UPLOAD_DIR || 'uploads/'
    },
    s3: {
      bucket: process.env.S3_BUCKET || '',
      region: process.env.S3_REGION || 'us-east-1',
      accessKeyId: process.env.S3_ACCESS_KEY_ID || '',
      secretAccessKey: process.env.S3_SECRET_ACCESS_KEY || ''
    }
  },
  
  // AI services configuration
  ai: {
    // Sourcing AI configuration
    sourcing: {
      enabled: true,
      apiKey: process.env.SOURCING_AI_API_KEY || '',
      endpoint: process.env.SOURCING_AI_ENDPOINT || 'http://localhost:3001/api/sourcing',
      maxCandidatesPerJob: 100,
      refreshInterval: 86400000 // 24 hours
    },
    
    // Screening AI configuration
    screening: {
      enabled: true,
      apiKey: process.env.SCREENING_AI_API_KEY || '',
      endpoint: process.env.SCREENING_AI_ENDPOINT || 'http://localhost:3002/api/screening',
      matchThreshold: 0.7,
      maxProcessingTime: 300000 // 5 minutes
    },
    
    // Scheduling AI configuration
    scheduling: {
      enabled: true,
      apiKey: process.env.SCHEDULING_AI_API_KEY || '',
      endpoint: process.env.SCHEDULING_AI_ENDPOINT || 'http://localhost:3003/api/scheduling',
      defaultTimeZone: 'UTC',
      reminderIntervals: [86400000, 3600000] // 24 hours, 1 hour
    },
    
    // Evaluation AI configuration
    evaluation: {
      enabled: true,
      apiKey: process.env.EVALUATION_AI_API_KEY || '',
      endpoint: process.env.EVALUATION_AI_ENDPOINT || 'http://localhost:3004/api/evaluation',
      questionGenerationModel: 'advanced',
      responseAnalysisModel: 'comprehensive'
    },
    
    // Hiring workflow AI configuration
    hiringWorkflow: {
      enabled: true,
      apiKey: process.env.HIRING_WORKFLOW_AI_API_KEY || '',
      endpoint: process.env.HIRING_WORKFLOW_AI_ENDPOINT || 'http://localhost:3005/api/hiring',
      offerGenerationEnabled: true,
      onboardingAutomationEnabled: true
    }
  },
  
  // Integration settings
  integrations: {
    // Calendar integrations
    calendar: {
      google: {
        enabled: process.env.GOOGLE_CALENDAR_ENABLED === 'true',
        clientId: process.env.GOOGLE_CALENDAR_CLIENT_ID || '',
        clientSecret: process.env.GOOGLE_CALENDAR_CLIENT_SECRET || '',
        redirectUri: process.env.GOOGLE_CALENDAR_REDIRECT_URI || ''
      },
      microsoft: {
        enabled: process.env.MICROSOFT_CALENDAR_ENABLED === 'true',
        clientId: process.env.MICROSOFT_CALENDAR_CLIENT_ID || '',
        clientSecret: process.env.MICROSOFT_CALENDAR_CLIENT_SECRET || '',
        redirectUri: process.env.MICROSOFT_CALENDAR_REDIRECT_URI || ''
      }
    },
    
    // Job board integrations
    jobBoards: {
      indeed: {
        enabled: process.env.INDEED_ENABLED === 'true',
        publisherId: process.env.INDEED_PUBLISHER_ID || '',
        apiKey: process.env.INDEED_API_KEY || ''
      },
      linkedin: {
        enabled: process.env.LINKEDIN_ENABLED === 'true',
        clientId: process.env.LINKEDIN_CLIENT_ID || '',
        clientSecret: process.env.LINKEDIN_CLIENT_SECRET || ''
      }
    },
    
    // Background check integrations
    backgroundCheck: {
      checkr: {
        enabled: process.env.CHECKR_ENABLED === 'true',
        apiKey: process.env.CHECKR_API_KEY || ''
      }
    },
    
    // Video interview integrations
    videoInterview: {
      zoom: {
        enabled: process.env.ZOOM_ENABLED === 'true',
        apiKey: process.env.ZOOM_API_KEY || '',
        apiSecret: process.env.ZOOM_API_SECRET || ''
      },
      googleMeet: {
        enabled: process.env.GOOGLE_MEET_ENABLED === 'true'
        // Uses Google Calendar credentials
      }
    }
  },
  
  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info', // 'error', 'warn', 'info', 'debug'
    format: process.env.LOG_FORMAT || 'json', // 'json', 'text'
    file: {
      enabled: process.env.LOG_FILE_ENABLED === 'true',
      path: process.env.LOG_FILE_PATH || 'logs/'
    }
  },
  
  // Security settings
  security: {
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100 // limit each IP to 100 requests per windowMs
    },
    helmet: {
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "blob:"],
          connectSrc: ["'self'", "wss:", "https:"]
        }
      }
    }
  },
  
  // Feature flags
  features: {
    autonomousRecruitmentAgent: true,
    hyperPersonalizedCandidateExperience: true,
    predictiveSuccessModeling: true,
    ethicalAiBiasDetection: true,
    multiModalCandidateAssessment: true,
    autonomousInterviewConductor: true,
    continuousLearningRecruitmentIntelligence: true,
    globalTalentArbitrage: true,
    candidateJourneyOptimization: true,
    autonomousOnboardingOrchestrator: true
  }
};
