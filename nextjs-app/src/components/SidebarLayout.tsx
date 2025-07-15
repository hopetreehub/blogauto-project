'use client';

import { createContext, useContext, useState, ReactNode, useMemo } from 'react';

interface SidebarContextType {
  isOpen: boolean;
  toggle: () => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export function useSidebar() {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
}

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(true);

  const toggle = () => setIsOpen(!isOpen);

  // context value 메모이제이션으로 불필요한 리렌더링 방지
  const value = useMemo(() => ({ isOpen, toggle }), [isOpen]);

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  );
}

export function MainContent({ children }: { children: ReactNode }) {
  const { isOpen } = useSidebar();
  
  return (
    <div className={`transition-all duration-300 ${isOpen ? 'ml-64' : 'ml-16'}`}>
      {children}
    </div>
  );
}