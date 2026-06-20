import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import OrbitBackground from '@/components/OrbitBackground';

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      <OrbitBackground />
      
      <div className="relative z-10 text-center space-y-6 p-8">
        <h1 className="text-6xl font-bold text-white">404</h1>
        <p className="text-2xl text-gray-300">Page Not Found</p>
        <p className="text-gray-400 max-w-md">
          The page you are looking for does not exist or has been moved.
        </p>
        
        <Link to="/dashboard">
          <Button className="mt-8">
            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
