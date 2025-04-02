import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';

const AnalyticsCard = ({ title, value, change, changeType = 'positive', description }) => {
  const changeColor = changeType === 'positive' ? 'text-green-500' : 'text-red-500';
  const changeIcon = changeType === 'positive' ? '↑' : '↓';
  
  return (
    <Card>
      <h3 className="text-lg font-medium text-gray-500">{title}</h3>
      <div className="mt-1 flex items-baseline">
        <p className="text-3xl font-semibold text-gray-900">{value}</p>
        {change && (
          <p className={`ml-2 flex items-baseline text-sm font-semibold ${changeColor}`}>
            {changeIcon} {change}
          </p>
        )}
      </div>
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
    </Card>
  );
};

const SourceEffectivenessChart = () => {
  // In a real app, this would be a real chart component
  return (
    <Card title="Candidate Source Effectiveness">
      <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
        <p className="text-gray-500">Source Effectiveness Chart</p>
      </div>
      <div className="mt-4 grid grid-cols-4 gap-4 text-center">
        <div>
          <p className="text-sm font-medium text-gray-500">LinkedIn</p>
          <p className="text-lg font-semibold text-gray-900">42%</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">GitHub</p>
          <p className="text-lg font-semibold text-gray-900">28%</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Stack Overflow</p>
          <p className="text-lg font-semibold text-gray-900">18%</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Other</p>
          <p className="text-lg font-semibold text-gray-900">12%</p>
        </div>
      </div>
    </Card>
  );
};

const RecruitmentFunnelChart = () => {
  // In a real app, this would be a real chart component
  return (
    <Card title="Recruitment Funnel">
      <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
        <p className="text-gray-500">Recruitment Funnel Chart</p>
      </div>
      <div className="mt-4 grid grid-cols-5 gap-4 text-center">
        <div>
          <p className="text-sm font-medium text-gray-500">Sourced</p>
          <p className="text-lg font-semibold text-gray-900">156</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Screened</p>
          <p className="text-lg font-semibold text-gray-900">98</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Interviewed</p>
          <p className="text-lg font-semibold text-gray-900">42</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Offered</p>
          <p className="text-lg font-semibold text-gray-900">18</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Hired</p>
          <p className="text-lg font-semibold text-gray-900">12</p>
        </div>
      </div>
    </Card>
  );
};

const TimeToHireChart = () => {
  // In a real app, this would be a real chart component
  return (
    <Card title="Time to Hire by Role">
      <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
        <p className="text-gray-500">Time to Hire Chart</p>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-sm font-medium text-gray-500">Engineering</p>
          <p className="text-lg font-semibold text-gray-900">18 days</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Product</p>
          <p className="text-lg font-semibold text-gray-900">22 days</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Design</p>
          <p className="text-lg font-semibold text-gray-900">15 days</p>
        </div>
      </div>
    </Card>
  );
};

const AutomationSavingsChart = () => {
  // In a real app, this would be a real chart component
  return (
    <Card title="Automation Savings">
      <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
        <p className="text-gray-500">Automation Savings Chart</p>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-sm font-medium text-gray-500">Time Saved</p>
          <p className="text-lg font-semibold text-gray-900">128 hours</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Cost Saved</p>
          <p className="text-lg font-semibold text-gray-900">$12,800</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Efficiency Gain</p>
          <p className="text-lg font-semibold text-gray-900">68%</p>
        </div>
      </div>
    </Card>
  );
};

const AnalyticsPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
        <div>
          <Button variant="outline" className="mr-2">Export Data</Button>
          <Button>Generate Report</Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnalyticsCard 
          title="Total Candidates" 
          value="156" 
          change="12%" 
          description="Last 30 days" 
        />
        <AnalyticsCard 
          title="Active Jobs" 
          value="24" 
          change="8%" 
          description="Last 30 days" 
        />
        <AnalyticsCard 
          title="Interviews Scheduled" 
          value="38" 
          change="15%" 
          description="Last 30 days" 
        />
        <AnalyticsCard 
          title="Time to Hire" 
          value="18 days" 
          change="22%" 
          description="Improvement from last quarter" 
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SourceEffectivenessChart />
        <RecruitmentFunnelChart />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TimeToHireChart />
        <AutomationSavingsChart />
      </div>
    </div>
  );
};

export default AnalyticsPage;
