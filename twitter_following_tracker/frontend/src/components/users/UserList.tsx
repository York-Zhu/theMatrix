import { useState } from 'react';
import { useTrackedUsers } from '../../hooks/useTrackedUsers';
import { formatDate, getTwitterUrl } from '../../lib/utils';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Loading } from '../ui/loading';
import { Error } from '../ui/error';
import { EmptyState } from '../ui/empty-state';
import { UserForm } from './UserForm';
import { ExternalLink, RefreshCw, Trash2, Twitter } from 'lucide-react';

export function UserList() {
  const { users, loading, error, fetchUsers, removeUser } = useTrackedUsers();
  const [isRemoving, setIsRemoving] = useState<string | null>(null);

  const handleRemoveUser = async (screenName: string) => {
    setIsRemoving(screenName);
    try {
      await removeUser(screenName);
    } finally {
      setIsRemoving(null);
    }
  };

  if (loading) return <Loading />;
  if (error) return <Error message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tracked Users</h2>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => fetchUsers()}
          className="flex items-center gap-1"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      <UserForm />

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>
            Twitter users being tracked for new followings
          </CardDescription>
        </CardHeader>
        <CardContent>
          {users.length === 0 ? (
            <EmptyState message="No users are being tracked. Add a user to start tracking." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Twitter className="h-4 w-4 text-blue-500" />
                        @{user.screen_name}
                      </div>
                    </TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{formatDate(user.last_updated)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(getTwitterUrl(user.screen_name), '_blank')}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleRemoveUser(user.screen_name)}
                          disabled={isRemoving === user.screen_name}
                        >
                          {isRemoving === user.screen_name ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
