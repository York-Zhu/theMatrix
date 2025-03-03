import { useNewFollowings } from '../../hooks/useNewFollowings';
import { formatDate, getTwitterUrl } from '../../lib/utils';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Loading } from '../ui/loading';
import { Error } from '../ui/error';
import { EmptyState } from '../ui/empty-state';
import { ExternalLink, RefreshCw, Twitter, UserPlus } from 'lucide-react';

export function FollowingList() {
  const { followings, loading, updating, error, fetchFollowings, updateFollowings } = useNewFollowings();
  
  if (loading) return <Loading />;
  if (error) return <Error message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">New Followings</h2>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => fetchFollowings()}
            className="flex items-center gap-1"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button 
            variant="default" 
            size="sm" 
            onClick={() => updateFollowings()}
            disabled={updating}
            className="flex items-center gap-1"
          >
            {updating ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Updating...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                Update All
              </>
            )}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New Followings</CardTitle>
          <CardDescription>
            Recently detected new Twitter followings
          </CardDescription>
        </CardHeader>
        <CardContent>
          {followings.length === 0 ? (
            <EmptyState message="No new followings detected. Update to check for new followings." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Following</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Tracked User</TableHead>
                  <TableHead>Detected At</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {followings.map((following) => (
                  <TableRow key={following.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <UserPlus className="h-4 w-4 text-green-500" />
                        @{following.following_screen_name}
                      </div>
                    </TableCell>
                    <TableCell>{following.following_name}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Twitter className="h-4 w-4 text-blue-500" />
                        @{following.tracked_screen_name}
                      </div>
                    </TableCell>
                    <TableCell>{formatDate(following.detected_at)}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(getTwitterUrl(following.following_screen_name), '_blank')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
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
