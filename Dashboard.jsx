import React from 'react';
import { useSelector } from 'react-redux';
import Card from '../common/Card';
import Button from '../common/Button';

const DashboardStats = () => {
  // In a real app, this would come from Redux state
  const stats = [
    { label: 'Active Jobs', value: 24, change: '+12%', color: 'text-green-500' },
    { label: 'Candidates', value: 156, change: '+8%', color: 'text-green-500' },
    { label: 'Interviews', value: 38, change: '+15%', color: 'text-green-500' },
    { label: 'Time Saved', value: '128h', change: '+22%', color: 'text-green-500' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <Card key={index} className="text-center">
          <h3 className="text-lg font-medium text-gray-500">{stat.label}</h3>
          <p className="mt-1 text-3xl font-semibold text-gray-900">{stat.value}</p>
          <p className={`mt-1 ${stat.color}`}>{stat.change} from last month</p>
        </Card>
      ))}
    </div>
  );
};

const RecentCandidates = () => {
  // In a real app, this would come from Redux state
  const candidates = [
    { id: 1, name: 'Jane Cooper', role: 'Senior Software Engineer', status: 'Screening', avatar: '/images/avatar1.jpg' },
    { id: 2, name: 'Michael Foster', role: 'Product Manager', status: 'Interview', avatar: '/images/avatar2.jpg' },
    { id: 3, name: 'Dries Vincent', role: 'UX Designer', status: 'Offer', avatar: '/images/avatar3.jpg' },
  ];

  return (
    <Card title="Recent Candidates">
      <div className="divide-y divide-gray-200">
        {candidates.map((candidate) => (
          <div key={candidate.id} className="py-3 flex items-center">
            <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold">
              {candidate.name.charAt(0)}
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">{candidate.name}</p>
              <p className="text-sm text-gray-500">{candidate.role}</p>
            </div>
            <div>
              <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                {candidate.status}
              </span>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <Button variant="outline" className="w-full">View All Candidates</Button>
      </div>
    </Card>
  );
};

const UpcomingInterviews = () => {
  // In a real app, this would come from Redux state
  const interviews = [
    { id: 1, candidate: 'Jane Cooper', position: 'Senior Software Engineer', date: 'Today, 2:00 PM', interviewer: 'Alex Johnson' },
    { id: 2, candidate: 'Michael Foster', position: 'Product Manager', date: 'Tomorrow, 10:00 AM', interviewer: 'Sarah Williams' },
    { id: 3, candidate: 'Dries Vincent', position: 'UX Designer', date: 'Mar 24, 3:30 PM', interviewer: 'David Chen' },
  ];

  return (
    <Card title="Upcoming Interviews">
      <div className="divide-y divide-gray-200">
        {interviews.map((interview) => (
          <div key={interview.id} className="py-3">
            <div className="flex justify-between">
              <p className="text-sm font-medium text-gray-900">{interview.candidate}</p>
              <p className="text-sm text-gray-500">{interview.date}</p>
            </div>
            <p className="text-sm text-gray-500">{interview.position}</p>
            <p className="text-xs text-gray-400 mt-1">Interviewer: {interview.interviewer}</p>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <Button variant="outline" className="w-full">View All Interviews</Button>
      </div>
    </Card>
  );
};

const AutomationInsights = () => {
  // In a real app, this would come from Redux state
  const insights = [
    { id: 1, title: 'AI Sourcing', description: '42 candidates automatically sourced this week', icon: '🤖' },
    { id: 2, title: 'Resume Screening', description: '78 resumes analyzed with 92% accuracy', icon: '📄' },
    { id: 3, title: 'Interview Scheduling', description: '24 interviews automatically scheduled', icon: '📅' },
  ];

  return (
    <Card title="Automation Insights">
      <div className="divide-y divide-gray-200">
        {insights.map((insight) => (
          <div key={insight.id} className="py-3 flex">
            <div className="text-2xl mr-3">{insight.icon}</div>
            <div>
              <p className="text-sm font-medium text-gray-900">{insight.title}</p>
              <p className="text-sm text-gray-500">{insight.description}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <Button variant="outline" className="w-full">View Detailed Analytics</Button>
      </div>
    </Card>
  );
};

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <Button>Start New Recruitment</Button>
      </div>
      
      <DashboardStats />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentCandidates />
        <UpcomingInterviews />
      </div>
      
      <AutomationInsights />
    </div>
  );
};

export default Dashboard;
