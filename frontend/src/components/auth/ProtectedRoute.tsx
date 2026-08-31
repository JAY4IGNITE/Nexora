import { Navigate, Outlet } from 'react-router-dom';
import { useAuth, UserRole } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  allowedRoles?: UserRole[];
}

export default function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, loading, role } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-pulse flex flex-col items-center space-y-4">
          <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
            <span className="text-xl font-bold text-primary">N</span>
          </div>
          <p className="text-sm text-muted-foreground">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center space-y-4 animate-in fade-in duration-500">
        <h2 className="text-2xl font-semibold tracking-tight text-destructive">Access Denied</h2>
        <p className="text-muted-foreground max-w-sm">
          You do not have the required permissions to view this module.
        </p>
      </div>
    );
  }

  return <Outlet />;
}
