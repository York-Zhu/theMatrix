export interface TwitterUser {
  screen_name: string;
}

export interface TrackedUser {
  id: number;
  twitter_id: string;
  screen_name: string;
  name: string;
  last_updated: string | null;
}

export interface UserResponse {
  success: boolean;
  message: string;
  user?: TrackedUser;
}

export interface Following {
  id: number;
  tracked_user_id: number;
  following_twitter_id: string;
  following_screen_name: string;
  following_name: string;
  first_seen: string;
}

export interface NewFollowing {
  id: number;
  tracked_user_id: number;
  following_twitter_id: string;
  following_screen_name: string;
  following_name: string;
  detected_at: string;
  notified: boolean;
  tracked_screen_name: string;
  tracked_name: string;
}
