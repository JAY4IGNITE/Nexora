import { useEffect, useState } from 'react';

export default function Placeholder({ title }: { title: string }) {
  const [health, setHealth] = useState<string>('checking...');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/v1/health')
      .then(res => res.json())
      .then(data => setHealth(data.status || 'unknown'))
      .catch(() => setHealth('error'));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-4 animate-in fade-in duration-500">
      <div className="p-4 bg-muted rounded-full">
        <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
          <span className="text-xl font-bold text-primary">N</span>
        </div>
      </div>
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="text-muted-foreground max-w-sm">
        This module is part of the future NEXORA platform roadmap and is not yet implemented in Module 0.
      </p>
      <div className="mt-8 p-4 border rounded-md shadow-apple">
        <p className="text-sm font-medium">Backend Connectivity: <span className={health === 'ok' ? 'text-green-500' : 'text-red-500'}>{health}</span></p>
      </div>
    </div>
  )
}
