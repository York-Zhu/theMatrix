import { useState, useEffect } from 'react';
import { fetchTrackedUsers, addTrackedUser, removeTrackedUser } from '../services/api';
import { TrackedUser, UserResponse } from '../types';

export function useTrackedUsers() {
  const [users, setUsers] = useState<TrackedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTrackedUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tracked users');
    } finally {
      setLoading(false);
    }
  };

  const addUser = async (screenName: string): Promise<UserResponse> => {
    try {
      const response = await addTrackedUser(screenName);
      if (response.success && response.user) {
        setUsers((prevUsers) => [...prevUsers, response.user as TrackedUser]);
      }
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add user';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    }
  };

  const removeUser = async (screenName: string): Promise<UserResponse> => {
    try {
      const response = await removeTrackedUser(screenName);
      if (response.success) {
        setUsers((prevUsers) => prevUsers.filter(user => user.screen_name !== screenName));
      }
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to remove user';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return { users, loading, error, fetchUsers, addUser, removeUser };
}
