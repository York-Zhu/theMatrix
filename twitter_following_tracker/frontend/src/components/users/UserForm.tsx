import { useState } from 'react';
import { useTrackedUsers } from '../../hooks/useTrackedUsers';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

export function UserForm() {
  const { addUser } = useTrackedUsers();
  const [screenName, setScreenName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!screenName.trim()) return;
    
    setIsSubmitting(true);
    setMessage(null);
    
    try {
      const response = await addUser(screenName);
      
      if (response.success) {
        setMessage({ type: 'success', text: response.message });
        setScreenName('');
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to add user' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add User</CardTitle>
        <CardDescription>
          Enter a Twitter handle to start tracking their following list
        </CardDescription>
      </CardHeader>
      <CardContent>
        {message && (
          <Alert variant={message.type === 'success' ? 'default' : 'destructive'} className="mb-4">
            {message.type === 'success' ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <AlertTitle>{message.type === 'success' ? 'Success' : 'Error'}</AlertTitle>
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-grow">
            <Input
              placeholder="Twitter handle (e.g. cz_binance)"
              value={screenName}
              onChange={(e) => setScreenName(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
          <Button type="submit" disabled={isSubmitting || !screenName.trim()}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Adding...
              </>
            ) : (
              'Add User'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
