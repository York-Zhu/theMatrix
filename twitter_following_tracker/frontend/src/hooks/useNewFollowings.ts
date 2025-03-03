import { useState, useEffect } from 'react';
import { fetchNewFollowings, markAsNotified, updateAllUsers } from '../services/api';
import { NewFollowing } from '../types';

export function useNewFollowings() {
  const [followings, setFollowings] = useState<NewFollowing[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFollowings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchNewFollowings();
      setFollowings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch new followings');
    } finally {
      setLoading(false);
    }
  };

  const markFollowingsAsNotified = async (ids: number[]) => {
    try {
      await markAsNotified(ids);
      setFollowings((prevFollowings) => 
        prevFollowings.map(following => 
          ids.includes(following.id) ? { ...following, notified: true } : following
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark followings as notified');
    }
  };

  const updateFollowings = async () => {
    try {
      setUpdating(true);
      setError(null);
      await updateAllUsers();
      // After updating, fetch the new followings
      await fetchFollowings();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update followings');
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    fetchFollowings();
  }, []);

  return { 
    followings, 
    loading, 
    updating,
    error, 
    fetchFollowings, 
    markFollowingsAsNotified,
    updateFollowings
  };
}
