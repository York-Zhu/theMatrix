import { FileQuestion } from 'lucide-react';

interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <FileQuestion className="h-16 w-16 text-slate-400 mb-4" />
      <p className="text-slate-500">{message}</p>
    </div>
  );
}
