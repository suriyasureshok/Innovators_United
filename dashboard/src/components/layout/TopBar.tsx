import { Bell, Settings, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function TopBar() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-14 bg-card/50 backdrop-blur-sm border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-muted-foreground">
          Collective Intelligence Console
        </h2>
        <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-xs font-medium">
          v2.4.1
        </span>
      </div>

      <div className="flex items-center gap-6">
        {/* Live Clock */}
        <div className="flex items-center gap-2 text-muted-foreground">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-mono">
            {currentTime.toLocaleTimeString('en-US', { hour12: false })}
          </span>
        </div>

        {/* Alert Indicator */}
        <motion.button
          className="relative p-2 rounded-lg hover:bg-secondary/50 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Bell className="w-5 h-5 text-muted-foreground" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-destructive animate-pulse" />
        </motion.button>

        {/* Settings */}
        <motion.button
          className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Settings className="w-5 h-5 text-muted-foreground" />
        </motion.button>
      </div>
    </header>
  );
}
