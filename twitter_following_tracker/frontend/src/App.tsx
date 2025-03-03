import { Layout } from './components/layout/Layout';
import { UserList } from './components/users/UserList';
import { FollowingList } from './components/followings/FollowingList';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from './components/ui/alert';
import { InfoIcon, UserPlus, Users } from 'lucide-react';

function App() {
  return (
    <Layout>
      <div className="space-y-6 py-4">
        <h1 className="text-3xl font-bold">Twitter Following Tracker</h1>
        <p className="text-slate-600">
          Track Twitter users' following lists and get notified about new followings.
        </p>

        <Alert>
          <InfoIcon className="h-4 w-4" />
          <AlertTitle>Mock Data Mode</AlertTitle>
          <AlertDescription>
            The application is currently running in mock data mode because the backend API is unavailable.
            All actions are simulated with sample data.
          </AlertDescription>
        </Alert>

        <Tabs defaultValue="users" className="w-full">
          <TabsList className="grid w-full md:w-[400px] grid-cols-2">
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span>Tracked Users</span>
            </TabsTrigger>
            <TabsTrigger value="followings" className="flex items-center gap-2">
              <UserPlus className="h-4 w-4" />
              <span>New Followings</span>
            </TabsTrigger>
          </TabsList>
          <TabsContent value="users" className="mt-6">
            <UserList />
          </TabsContent>
          <TabsContent value="followings" className="mt-6">
            <FollowingList />
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}

export default App;
