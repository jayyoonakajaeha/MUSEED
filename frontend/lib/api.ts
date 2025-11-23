const API_BASE_URL = 'http://localhost:8000';

// --- Generic Fetch Helper ---
async function apiFetch(url: string, options: RequestInit = {}) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      let errorMessage = 'An unknown error occurred.';
      if (data.detail) {
        if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
          errorMessage = data.detail[0].msg;
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
      }
      throw new Error(errorMessage);
    }
    return { success: true, data };
  } catch (error: any) {
    console.error(`Failed to fetch from ${url}:`, error);
    return { success: false, error: error.message };
  }
}


export async function getBackendStatus() {
  return apiFetch(`${API_BASE_URL}/api/status`);
}

export async function registerUser(userData: { username: string; nickname: string; password: string }) {
  // email is no longer required for registration
  return apiFetch(`${API_BASE_URL}/api/auth/signup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
}

export async function loginUser(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  return apiFetch(`${API_BASE_URL}/api/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });
}

export async function getUserProfile(username: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/users/${username}`, { headers });
}

export async function updateUserProfile(username: string, token: string, updateData: any) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(updateData),
  });
}

export async function recordListen(trackData: { track_id: string; genre: string }, token: string) {
  return apiFetch(`${API_BASE_URL}/api/history/listen`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(trackData),
  });
}

export async function getUserStats(username: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/stats`);
}

export async function getUserGenreStats(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/genre-stats`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function createPlaylistFromId(name: string, seed_track_id: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ name, seed_track_id }),
  });
}

export async function createPlaylistFromUpload(name: string, file: File, token: string) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('file', file);

  // Note: apiFetch is not used here because of FormData content type
  try {
    const response = await fetch(`${API_BASE_URL}/api/playlists/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create playlist from upload');
    }
    return { success: true, data };
  } catch (error: any) {
    console.error("Failed to create playlist from upload:", error);
    return { success: false, error: error.message };
  }
}

export async function getPlaylist(playlistId: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function deletePlaylist(playlistId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function updatePlaylist(playlistId: number, updateData: { name?: string; is_public?: boolean }, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(updateData),
  });
}

export async function likePlaylist(playlistId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/like`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function unlikePlaylist(playlistId: number, token:string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/like`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getUserCreatedPlaylists(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/playlists`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getUserLikedPlaylists(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/likes`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getDiscoverPlaylists(token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/discover`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getTrendingPlaylists(token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/trending`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

// --- Search Functions ---

export async function searchTracks(query: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/tracks/search?q=${encodeURIComponent(query)}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function searchUsers(query: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/search?q=${encodeURIComponent(query)}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function searchPlaylists(query: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/search?q=${encodeURIComponent(query)}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

// --- Follow Functions ---

export async function followUser(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/follow`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function unfollowUser(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/follow`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getUserFollowers(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/followers`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getUserFollowing(username: string, token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/${username}/following`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getRecommendedUsers(token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/recommendations`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}
