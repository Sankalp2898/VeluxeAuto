import React, { useState, useEffect } from 'react';
import './App.css';

// Components
const RadialProgress = ({ percentage, label, color, size = 120 }) => {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold text-white">{percentage}%</span>
        </div>
      </div>
      <span className="text-sm text-gray-300 mt-2 font-medium">{label}</span>
    </div>
  );
};

const ServiceToggle = ({ selected, onSelect }) => (
  <div className="flex bg-gray-800 rounded-lg p-1 mb-6">
    <button
      className={`flex-1 px-4 py-3 rounded-md font-medium transition-all ${
        selected === 'white-glove' 
          ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-black' 
          : 'text-gray-300 hover:text-white'
      }`}
      onClick={() => onSelect('white-glove')}
    >
      White-Glove Pickup
    </button>
    <button
      className={`flex-1 px-4 py-3 rounded-md font-medium transition-all ${
        selected === 'in-garage' 
          ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-black' 
          : 'text-gray-300 hover:text-white'
      }`}
      onClick={() => onSelect('in-garage')}
    >
      In-Garage Service
    </button>
  </div>
);

const MembershipCard = ({ tier, price, features, isPopular }) => (
  <div className={`relative p-6 rounded-xl border-2 transition-all hover:scale-105 ${
    isPopular 
      ? 'border-yellow-400 bg-gradient-to-br from-gray-800 to-gray-900' 
      : 'border-gray-700 bg-gray-800'
  }`}>
    {isPopular && (
      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
        <span className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black px-4 py-1 rounded-full text-sm font-bold">
          MOST POPULAR
        </span>
      </div>
    )}
    <h3 className="text-xl font-bold text-white mb-2">{tier}</h3>
    <div className="text-3xl font-bold text-yellow-400 mb-4">{price}</div>
    <ul className="space-y-2">
      {features.map((feature, index) => (
        <li key={index} className="text-gray-300 flex items-center">
          <span className="text-yellow-400 mr-2">✓</span>
          {feature}
        </li>
      ))}
    </ul>
    <button className={`w-full mt-6 px-4 py-3 rounded-lg font-medium transition-all ${
      isPopular
        ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-black hover:shadow-lg'
        : 'border border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black'
    }`}>
      Choose Plan
    </button>
  </div>
);

const EventCard = ({ event, onRSVP }) => (
  <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-yellow-400 transition-all">
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-xl font-bold text-white">{event.title}</h3>
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
        event.event_type === 'track-day' 
          ? 'bg-red-500 text-white' 
          : event.event_type === 'exclusive'
          ? 'bg-yellow-400 text-black'
          : 'bg-blue-500 text-white'
      }`}>
        {event.event_type.toUpperCase()}
      </span>
    </div>
    <p className="text-gray-300 mb-3">{event.description}</p>
    <div className="space-y-2 mb-4">
      <div className="flex items-center text-gray-400">
        <span className="mr-2">📅</span>
        {event.date}
      </div>
      <div className="flex items-center text-gray-400">
        <span className="mr-2">📍</span>
        {event.location}
      </div>
      <div className="flex items-center text-gray-400">
        <span className="mr-2">👥</span>
        {event.current_attendees}/{event.max_attendees} attending
      </div>
    </div>
    <button 
      onClick={() => onRSVP(event.id)}
      className="w-full bg-gradient-to-r from-yellow-400 to-yellow-600 text-black px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all"
    >
      RSVP
    </button>
  </div>
);

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [serviceType, setServiceType] = useState('white-glove');
  const [selectedService, setSelectedService] = useState('maintenance');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [carHealth, setCarHealth] = useState({
    oil_status: 85,
    brake_status: 92,
    battery_status: 88,
    tire_status: 76,
    ai_predictions: {
      overall_health: "Excellent",
      next_service: "Oil change recommended in 2 weeks",
      alerts: ["Tire pressure check recommended"]
    }
  });
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/events`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const handleRSVP = async (eventId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/events/${eventId}/rsvp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'demo-user' })
      });
      const result = await response.json();
      if (result.success) {
        fetchEvents(); // Refresh events
      }
    } catch (error) {
      console.error('Error RSVP:', error);
    }
  };

  const renderHome = () => (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome to Veluxe</h1>
        <p className="text-gray-300">Your premium car concierge experience</p>
      </div>

      {/* Car Card */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-white">2023 Porsche 911</h2>
            <p className="text-gray-300">Carrera S • Black</p>
          </div>
          <div className="text-right">
            <div className="text-yellow-400 font-bold">12,450 mi</div>
            <div className="text-sm text-gray-400">Last service: 2 weeks ago</div>
          </div>
        </div>
        
        {/* Car Health Preview */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <RadialProgress percentage={carHealth.oil_status} label="Oil" color="#10B981" size={80} />
          <RadialProgress percentage={carHealth.brake_status} label="Brakes" color="#3B82F6" size={80} />
          <RadialProgress percentage={carHealth.battery_status} label="Battery" color="#F59E0B" size={80} />
          <RadialProgress percentage={carHealth.tire_status} label="Tires" color="#EF4444" size={80} />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <button 
          onClick={() => setActiveTab('services')}
          className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black p-4 rounded-xl font-bold text-center hover:shadow-lg transition-all"
        >
          Book Service
        </button>
        <button 
          onClick={() => setActiveTab('alerts')}
          className="bg-gray-800 border border-yellow-400 text-yellow-400 p-4 rounded-xl font-bold text-center hover:bg-yellow-400 hover:text-black transition-all"
        >
          Smart Alerts
        </button>
      </div>

      {/* AI Insights */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">AI Insights</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">Overall Health</span>
            <span className="text-green-400 font-medium">{carHealth.ai_predictions.overall_health}</span>
          </div>
          <div className="text-yellow-400 text-sm">
            💡 {carHealth.ai_predictions.next_service}
          </div>
          {carHealth.ai_predictions.alerts?.map((alert, index) => (
            <div key={index} className="text-blue-400 text-sm">
              ⚠️ {alert}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderServices = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Book Service</h2>
      
      <ServiceToggle selected={serviceType} onSelect={setServiceType} />

      <div>
        <label className="block text-white font-medium mb-2">Service Type</label>
        <select 
          value={selectedService}
          onChange={(e) => setSelectedService(e.target.value)}
          className="w-full bg-gray-800 border border-gray-600 text-white p-3 rounded-lg focus:border-yellow-400 focus:outline-none"
        >
          <option value="maintenance">General Maintenance</option>
          <option value="detailing">Premium Detailing</option>
          <option value="tire-change">Tire Change/Rotation</option>
          <option value="oil-change">Oil Change</option>
          <option value="brake-service">Brake Service</option>
          <option value="battery">Battery Service</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-white font-medium mb-2">Date</label>
          <input 
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 text-white p-3 rounded-lg focus:border-yellow-400 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-white font-medium mb-2">Time</label>
          <select 
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 text-white p-3 rounded-lg focus:border-yellow-400 focus:outline-none"
          >
            <option value="">Select time</option>
            <option value="09:00">9:00 AM</option>
            <option value="10:00">10:00 AM</option>
            <option value="11:00">11:00 AM</option>
            <option value="14:00">2:00 PM</option>
            <option value="15:00">3:00 PM</option>
            <option value="16:00">4:00 PM</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-white font-medium mb-2">Special Instructions</label>
        <textarea 
          className="w-full bg-gray-800 border border-gray-600 text-white p-3 rounded-lg h-24 focus:border-yellow-400 focus:outline-none"
          placeholder="Any special requirements or notes..."
        />
      </div>

      <button className="w-full bg-gradient-to-r from-yellow-400 to-yellow-600 text-black px-6 py-4 rounded-lg font-bold text-lg hover:shadow-lg transition-all">
        Confirm Booking
      </button>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Car Health Dashboard</h2>
      
      {/* Health Rings */}
      <div className="grid grid-cols-2 gap-6">
        <RadialProgress percentage={carHealth.oil_status} label="Engine Oil" color="#10B981" />
        <RadialProgress percentage={carHealth.brake_status} label="Brake System" color="#3B82F6" />
        <RadialProgress percentage={carHealth.battery_status} label="Battery" color="#F59E0B" />
        <RadialProgress percentage={carHealth.tire_status} label="Tires" color="#EF4444" />
      </div>

      {/* Detailed Insights */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Maintenance Predictions</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <div className="text-white font-medium">Oil Change</div>
              <div className="text-gray-400 text-sm">Due in 2 weeks</div>
            </div>
            <div className="text-yellow-400">📅</div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <div className="text-white font-medium">Tire Rotation</div>
              <div className="text-gray-400 text-sm">Due in 1 month</div>
            </div>
            <div className="text-blue-400">🔄</div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <div className="text-white font-medium">Brake Inspection</div>
              <div className="text-gray-400 text-sm">Due in 3 months</div>
            </div>
            <div className="text-green-400">✅</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderExperiences = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Exclusive Experiences</h2>
      
      <div className="space-y-4">
        {events.map((event) => (
          <EventCard key={event.id} event={event} onRSVP={handleRSVP} />
        ))}
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Membership & Settings</h2>
      
      {/* Current Membership */}
      <div className="bg-gray-800 rounded-xl p-6 border border-yellow-400">
        <h3 className="text-xl font-bold text-white mb-2">Current Plan: Premium</h3>
        <p className="text-gray-300">Enjoy white-glove service and exclusive events</p>
      </div>

      {/* Membership Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MembershipCard 
          tier="Basic"
          price="$29/mo"
          features={["Basic maintenance reminders", "Service booking", "Email support"]}
        />
        <MembershipCard 
          tier="Premium"
          price="$79/mo"
          features={["White-glove pickup", "AI health predictions", "Priority booking", "Phone support"]}
          isPopular={true}
        />
        <MembershipCard 
          tier="Veluxe Elite"
          price="$149/mo"
          features={["All Premium features", "Exclusive events", "24/7 concierge", "Free detailing"]}
        />
      </div>

      {/* Settings */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Preferences</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-white">Push Notifications</span>
            <button className="bg-yellow-400 w-12 h-6 rounded-full relative">
              <div className="bg-black w-5 h-5 rounded-full absolute right-0.5 top-0.5"></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white">Email Updates</span>
            <button className="bg-gray-600 w-12 h-6 rounded-full relative">
              <div className="bg-white w-5 h-5 rounded-full absolute left-0.5 top-0.5"></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white">Location Services</span>
            <button className="bg-yellow-400 w-12 h-6 rounded-full relative">
              <div className="bg-black w-5 h-5 rounded-full absolute right-0.5 top-0.5"></div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch(activeTab) {
      case 'home': return renderHome();
      case 'services': return renderServices();
      case 'alerts': return renderAlerts();
      case 'experiences': return renderExperiences();
      case 'settings': return renderSettings();
      default: return renderHome();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header */}
      <div className="bg-black bg-opacity-50 backdrop-blur-md p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-600">
            VELUXE
          </h1>
          <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full"></div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-6 pb-20">
        {renderContent()}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-black bg-opacity-80 backdrop-blur-md border-t border-gray-700">
        <div className="flex justify-around items-center py-2">
          {[
            { id: 'home', icon: '🏠', label: 'Home' },
            { id: 'services', icon: '🔧', label: 'Services' },
            { id: 'alerts', icon: '💡', label: 'Alerts' },
            { id: 'experiences', icon: '🏁', label: 'Events' },
            { id: 'settings', icon: '⚙️', label: 'Settings' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center py-2 px-3 rounded-lg transition-all ${
                activeTab === tab.id 
                  ? 'text-yellow-400' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <span className="text-lg mb-1">{tab.icon}</span>
              <span className="text-xs font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;