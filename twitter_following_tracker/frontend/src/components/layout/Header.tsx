import { Twitter } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-slate-900 text-white p-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Twitter size={24} className="text-blue-400" />
          <h1 className="text-xl font-bold">Twitter Following Tracker</h1>
        </div>
        <div className="text-sm text-slate-300">
          Track Twitter users' following lists
        </div>
      </div>
    </header>
  );
}
