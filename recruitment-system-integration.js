const path = require('path');
const fs = require('fs');

// Import autonomous recruitment modules
const sourcingAI = require('./sourcing_ai');
const screeningAI = require('./screening_ai');
const schedulingSystem = require('./scheduling_system');
const evaluationAI = require('./evaluation_ai');
const hiringWorkflow = require('./hiring_workflow');

// Integration service for the autonomous recruitment system
class RecruitmentSystemIntegration {
  constructor() {
    this.modules = {
      sourcing: sourcingAI,
      screening: screeningAI,
      scheduling: schedulingSystem,
      evaluation: evaluationAI,
      hiring: hiringWorkflow
    };
    
    this.logger = console; // Replace with proper logging in production
  }
  
  // Source candidates from various platforms
  async sourceCandidate(jobId, criteria, options = {}) {
    try {
      this.logger.info(`Sourcing candidates for job ${jobId}`);
      
      // Call the sourcing AI module
      const candidates = await this.modules.sourcing.findCandidates(jobId, criteria, options);
      
      this.logger.info(`Found ${candidates.length} candidates for job ${jobId}`);
      return candidates;
    } catch (error) {
      this.logger.error(`Error sourcing candidates: ${error.message}`);
      throw new Error(`Sourcing failed: ${error.message}`);
    }
  }
  
  // Screen candidate resume
  async screenResume(candidateId, resumeData, jobId) {
    try {
      this.logger.info(`Screening resume for candidate ${candidateId}`);
      
      // Call the screening AI module
      const screeningResults = await this.modules.screening.analyzeResume(
        candidateId, 
        resumeData, 
        jobId
      );
      
      this.logger.info(`Resume screening completed for candidate ${candidateId}`);
      return screeningResults;
    } catch (error) {
      this.logger.error(`Error screening resume: ${error.message}`);
      throw new Error(`Resume screening failed: ${error.message}`);
    }
  }
  
  // Schedule interview automatically
  async scheduleInterview(candidateId, jobId, interviewerIds, options = {}) {
    try {
      this.logger.info(`Scheduling interview for candidate ${candidateId} and job ${jobId}`);
      
      // Call the scheduling system module
      const schedulingResult = await this.modules.scheduling.findOptimalSlot(
        candidateId,
        jobId,
        interviewerIds,
        options
      );
      
      this.logger.info(`Interview scheduled for candidate ${candidateId}`);
      return schedulingResult;
    } catch (error) {
      this.logger.error(`Error scheduling interview: ${error.message}`);
      throw new Error(`Interview scheduling failed: ${error.message}`);
    }
  }
  
  // Generate interview questions
  async generateQuestions(interviewId, candidateId, jobId, interviewType) {
    try {
      this.logger.info(`Generating questions for interview ${interviewId}`);
      
      // Call the evaluation AI module
      const questions = await this.modules.evaluation.generateQuestions(
        interviewId,
        candidateId,
        jobId,
        interviewType
      );
      
      this.logger.info(`Generated ${questions.length} questions for interview ${interviewId}`);
      return questions;
    } catch (error) {
      this.logger.error(`Error generating questions: ${error.message}`);
      throw new Error(`Question generation failed: ${error.message}`);
    }
  }
  
  // Analyze interview responses
  async analyzeResponses(interviewId, responses) {
    try {
      this.logger.info(`Analyzing responses for interview ${interviewId}`);
      
      // Call the evaluation AI module
      const analysis = await this.modules.evaluation.analyzeResponses(
        interviewId,
        responses
      );
      
      this.logger.info(`Response analysis completed for interview ${interviewId}`);
      return analysis;
    } catch (error) {
      this.logger.error(`Error analyzing responses: ${error.message}`);
      throw new Error(`Response analysis failed: ${error.message}`);
    }
  }
  
  // Generate hiring recommendation
  async generateHiringRecommendation(candidateId, jobId) {
    try {
      this.logger.info(`Generating hiring recommendation for candidate ${candidateId} and job ${jobId}`);
      
      // Call the hiring workflow module
      const recommendation = await this.modules.hiring.generateRecommendation(
        candidateId,
        jobId
      );
      
      this.logger.info(`Hiring recommendation generated for candidate ${candidateId}`);
      return recommendation;
    } catch (error) {
      this.logger.error(`Error generating hiring recommendation: ${error.message}`);
      throw new Error(`Recommendation generation failed: ${error.message}`);
    }
  }
  
  // Create offer letter
  async createOffer(candidateId, jobId, offerDetails) {
    try {
      this.logger.info(`Creating offer for candidate ${candidateId} and job ${jobId}`);
      
      // Call the hiring workflow module
      const offer = await this.modules.hiring.createOffer(
        candidateId,
        jobId,
        offerDetails
      );
      
      this.logger.info(`Offer created for candidate ${candidateId}`);
      return offer;
    } catch (error) {
      this.logger.error(`Error creating offer: ${error.message}`);
      throw new Error(`Offer creation failed: ${error.message}`);
    }
  }
  
  // Generate onboarding plan
  async createOnboardingPlan(candidateId, jobId) {
    try {
      this.logger.info(`Creating onboarding plan for candidate ${candidateId} and job ${jobId}`);
      
      // Call the hiring workflow module
      const onboardingPlan = await this.modules.hiring.createOnboardingPlan(
        candidateId,
        jobId
      );
      
      this.logger.info(`Onboarding plan created for candidate ${candidateId}`);
      return onboardingPlan;
    } catch (error) {
      this.logger.error(`Error creating onboarding plan: ${error.message}`);
      throw new Error(`Onboarding plan creation failed: ${error.message}`);
    }
  }
  
  // Run the entire recruitment process autonomously
  async runAutonomousRecruitment(jobId, options = {}) {
    try {
      this.logger.info(`Starting autonomous recruitment for job ${jobId}`);
      
      // 1. Source candidates
      const candidates = await this.sourceCandidate(jobId, options.sourcingCriteria);
      
      // 2. Screen candidates
      const screenedCandidates = [];
      for (const candidate of candidates) {
        const screeningResults = await this.screenResume(
          candidate.id, 
          candidate.resumeData, 
          jobId
        );
        
        if (screeningResults.overallScore >= options.screeningThreshold || 70) {
          screenedCandidates.push({
            ...candidate,
            screeningResults
          });
        }
      }
      
      // 3. Schedule interviews for qualified candidates
      const interviews = [];
      for (const candidate of screenedCandidates) {
        const interviewSchedule = await this.scheduleInterview(
          candidate.id,
          jobId,
          options.interviewerIds,
          options.schedulingOptions
        );
        
        interviews.push({
          candidate: candidate.id,
          schedule: interviewSchedule
        });
      }
      
      this.logger.info(`Autonomous recruitment process completed for job ${jobId}`);
      return {
        job: jobId,
        candidatesSourced: candidates.length,
        candidatesScreened: screenedCandidates.length,
        interviewsScheduled: interviews.length,
        interviews
      };
    } catch (error) {
      this.logger.error(`Error in autonomous recruitment: ${error.message}`);
      throw new Error(`Autonomous recruitment failed: ${error.message}`);
    }
  }
}

module.exports = new RecruitmentSystemIntegration();
