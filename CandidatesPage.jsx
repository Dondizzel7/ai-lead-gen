import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import Input from '../common/Input';
import Select from '../common/Select';

const CandidateList = () => {
  // In a real app, this would come from Redux state
  const candidates = [
    { 
      id: 1, 
      name: 'Jane Cooper', 
      role: 'Senior Software Engineer', 
      skills: ['React', 'Node.js', 'TypeScript'],
      experience: '8 years',
      status: 'Screening', 
      match: '92%'
    },
    { 
      id: 2, 
      name: 'Michael Foster', 
      role: 'Product Manager', 
      skills: ['Product Strategy', 'Agile', 'User Research'],
      experience: '6 years',
      status: 'Interview', 
      match: '87%'
    },
    { 
      id: 3, 
      name: 'Dries Vincent', 
      role: 'UX Designer', 
      skills: ['Figma', 'User Testing', 'Wireframing'],
      experience: '5 years',
      status: 'Offer', 
      match: '94%'
    },
    { 
      id: 4, 
      name: 'Lindsay Walton', 
      role: 'Frontend Developer', 
      skills: ['React', 'CSS', 'JavaScript'],
      experience: '4 years',
      status: 'Screening', 
      match: '85%'
    },
    { 
      id: 5, 
      name: 'Courtney Henry', 
      role: 'Backend Developer', 
      skills: ['Python', 'Django', 'PostgreSQL'],
      experience: '7 years',
      status: 'Interview', 
      match: '89%'
    },
  ];

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {candidates.map((candidate) => (
          <li key={candidate.id}>
            <div className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold">
                    {candidate.name.charAt(0)}
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">{candidate.name}</p>
                    <p className="text-sm text-gray-500">{candidate.role}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 mr-2">
                    {candidate.status}
                  </span>
                  <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                    {candidate.match} Match
                  </span>
                </div>
              </div>
              <div className="mt-2 sm:flex sm:justify-between">
                <div className="sm:flex">
                  <p className="flex items-center text-sm text-gray-500">
                    Experience: {candidate.experience}
                  </p>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <div className="flex flex-wrap">
                    {candidate.skills.map((skill, index) => (
                      <span key={index} className="mr-2 mb-1 px-2 py-1 text-xs bg-gray-100 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

const CandidateFilters = () => {
  return (
    <Card>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input 
          label="Search" 
          name="search" 
          placeholder="Search candidates..." 
        />
        <Select
          label="Status"
          name="status"
          placeholder="Select status"
          options={[
            { value: 'all', label: 'All Statuses' },
            { value: 'sourced', label: 'Sourced' },
            { value: 'screening', label: 'Screening' },
            { value: 'interview', label: 'Interview' },
            { value: 'offer', label: 'Offer' },
            { value: 'hired', label: 'Hired' },
            { value: 'rejected', label: 'Rejected' },
          ]}
        />
        <Select
          label="Job"
          name="job"
          placeholder="Select job"
          options={[
            { value: 'all', label: 'All Jobs' },
            { value: '1', label: 'Senior Software Engineer' },
            { value: '2', label: 'Product Manager' },
            { value: '3', label: 'UX Designer' },
            { value: '4', label: 'Frontend Developer' },
            { value: '5', label: 'Backend Developer' },
          ]}
        />
      </div>
      <div className="mt-4 flex justify-end">
        <Button variant="outline" className="mr-2">Reset</Button>
        <Button>Apply Filters</Button>
      </div>
    </Card>
  );
};

const CandidatesPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Candidates</h1>
        <div>
          <Button variant="outline" className="mr-2">Import Candidates</Button>
          <Button>Source New Candidates</Button>
        </div>
      </div>
      
      <CandidateFilters />
      
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Candidate List</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Showing 5 of 156 candidates</p>
          </div>
          <div className="flex items-center">
            <span className="mr-2 text-sm text-gray-500">Sort by:</span>
            <Select
              name="sort"
              className="mb-0"
              options={[
                { value: 'match', label: 'Match Score' },
                { value: 'name', label: 'Name' },
                { value: 'date', label: 'Date Added' },
              ]}
            />
          </div>
        </div>
        <CandidateList />
        <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">1</span> to <span className="font-medium">5</span> of <span className="font-medium">156</span> results
            </div>
            <div className="flex-1 flex justify-end">
              <Button variant="outline" className="mr-2" disabled>Previous</Button>
              <Button variant="outline">Next</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidatesPage;
