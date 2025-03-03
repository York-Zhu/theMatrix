import { TrackedUser, NewFollowing, UserResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'https://twitter-alert-tool-zkpnvsmg.fly.dev';

// Mock data for testing when API is unavailable
const MOCK_DATA = {
  users: [
    {
      id: 1,
      twitter_id: '12345',
      screen_name: 'cz_binance',
      name: 'CZ 🔶 BNB',
      last_updated: '2025-03-03T12:00:00'
    },
    {
      id: 2,
      twitter_id: '67890',
      screen_name: 'hosseeb.p',
      name: 'Haseeb Qureshi',
      last_updated: '2025-03-03T12:00:00'
    }
  ],
  newFollowings: [
    {
      id: 1,
      tracked_user_id: 1,
      following_twitter_id: '11111',
      following_screen_name: 'crypto_exchange',
      following_name: 'Crypto Exchange',
      detected_at: '2025-03-03T12:30:00',
      notified: false,
      tracked_screen_name: 'cz_binance',
      tracked_name: 'CZ 🔶 BNB'
    },
    {
      id: 2,
      tracked_user_id: 1,
      following_twitter_id: '22222',
      following_screen_name: 'defi_protocol',
      following_name: 'DeFi Protocol',
      detected_at: '2025-03-03T12:45:00',
      notified: false,
      tracked_screen_name: 'cz_binance',
      tracked_name: 'CZ 🔶 BNB'
    }
  ]
};

// Check if we should use mock data (API is unavailable)
const useMockData = true;

export const fetchTrackedUsers = async (): Promise<TrackedUser[]> => {
  if (useMockData) {
    console.log('Using mock data for users');
    return MOCK_DATA.users;
  }

  try {
    const response = await fetch(`${API_URL}/users`);
    if (!response.ok) {
      throw new Error(`Failed to fetch tracked users: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching tracked users:', error);
    throw new Error('Failed to fetch tracked users. API may be unavailable.');
  }
};

export const addTrackedUser = async (screenName: string): Promise<UserResponse> => {
  if (useMockData) {
    console.log('Using mock data for adding user');
    // Simulate adding a user
    const newUser = {
      id: MOCK_DATA.users.length + 1,
      twitter_id: Math.floor(Math.random() * 1000000).toString(),
      screen_name: screenName,
      name: `${screenName.charAt(0).toUpperCase()}${screenName.slice(1)}`,
      last_updated: new Date().toISOString()
    };
    
    MOCK_DATA.users.push(newUser);
    
    return {
      success: true,
      message: `Successfully added user @${screenName} to tracking list.`,
      user: newUser
    };
  }

  try {
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ screen_name: screenName }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to add tracked user: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error adding tracked user:', error);
    throw new Error('Failed to add user. API may be unavailable.');
  }
};

export const removeTrackedUser = async (screenName: string): Promise<UserResponse> => {
  if (useMockData) {
    console.log('Using mock data for removing user');
    // Simulate removing a user
    const userIndex = MOCK_DATA.users.findIndex(user => user.screen_name === screenName);
    
    if (userIndex === -1) {
      return {
        success: false,
        message: `User @${screenName} is not being tracked.`
      };
    }
    
    MOCK_DATA.users.splice(userIndex, 1);
    
    return {
      success: true,
      message: `Successfully removed user @${screenName} from tracking list.`
    };
  }

  try {
    const response = await fetch(`${API_URL}/users/${screenName}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to remove tracked user: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error removing tracked user:', error);
    throw new Error('Failed to remove user. API may be unavailable.');
  }
};

export const fetchNewFollowings = async (): Promise<NewFollowing[]> => {
  if (useMockData) {
    console.log('Using mock data for new followings');
    return MOCK_DATA.newFollowings;
  }

  try {
    const response = await fetch(`${API_URL}/new-followings`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch new followings: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error fetching new followings:', error);
    throw new Error('Failed to fetch new followings. API may be unavailable.');
  }
};

export const updateAllUsers = async (): Promise<{ message: string[] }> => {
  if (useMockData) {
    console.log('Using mock data for updating all users');
    // Simulate updating users
    return { message: ['Update started in background'] };
  }

  try {
    const response = await fetch(`${API_URL}/update`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update all users: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error updating all users:', error);
    throw new Error('Failed to update all users. API may be unavailable.');
  }
};

export const testUpdateUser = async (screenName: string): Promise<any> => {
  if (useMockData) {
    console.log('Using mock data for test update');
    // Simulate test update
    return {
      user_id: 1,
      screen_name: screenName,
      new_followings_count: 2,
      new_followings: [
        {
          id: Math.floor(Math.random() * 1000000),
          following_twitter_id: Math.floor(Math.random() * 1000000).toString(),
          following_screen_name: 'new_crypto_project',
          following_name: 'New Crypto Project',
          first_seen: new Date().toISOString()
        },
        {
          id: Math.floor(Math.random() * 1000000),
          following_twitter_id: Math.floor(Math.random() * 1000000).toString(),
          following_screen_name: 'defi_protocol',
          following_name: 'DeFi Protocol',
          first_seen: new Date().toISOString()
        }
      ]
    };
  }

  try {
    const response = await fetch(`${API_URL}/test-update/${screenName}`);
    
    if (!response.ok) {
      throw new Error(`Failed to test update for user ${screenName}: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`Error testing update for user ${screenName}:`, error);
    throw new Error(`Failed to test update for user ${screenName}. API may be unavailable.`);
  }
};

export const markAsNotified = async (followingIds: number[]): Promise<{ message: string }> => {
  if (useMockData) {
    console.log('Using mock data for marking as notified');
    // Simulate marking as notified
    MOCK_DATA.newFollowings = MOCK_DATA.newFollowings.map(following => 
      followingIds.includes(following.id) ? { ...following, notified: true } : following
    );
    
    return { message: `Marked ${followingIds.length} followings as notified` };
  }

  try {
    const response = await fetch(`${API_URL}/mark-notified`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(followingIds),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to mark followings as notified: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error marking followings as notified:', error);
    throw new Error('Failed to mark followings as notified. API may be unavailable.');
  }
};
