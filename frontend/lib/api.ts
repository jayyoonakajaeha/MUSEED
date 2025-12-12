const API_BASE_URL = typeof window === 'undefined' ? 'http://127.0.0.1:8000' : '';

// --- Generic Fetch Helper ---
export async function apiFetch(url: string, options: RequestInit = {}) {
  try {
    const response = await fetch(url, options);

    let data = null;
    if (response.status !== 204) {
      try {
        const text = await response.text();
        try {
          data = JSON.parse(text);
        } catch {
          // 응답 본문이 JSON이 아님 (HTML 에러 페이지 또는 일반 텍스트)
          if (!response.ok) {
            console.error('Non-JSON error response:', text.slice(0, 500)); // 처음 500자 로그 출력
            throw new Error(text.length < 100 ? text : `Server Error (${response.status})`);
          }
        }
      } catch (e: any) {
        // 텍스트 읽기 또는 파싱 실패
        if (!response.ok) throw e;
      }
    }

    if (!response.ok) {
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          return { success: false, error: "Session expired. Please login again." };
        }
      }

      let errorMessage = 'An unknown error occurred.';
      if (data && data.detail) {
        if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
          errorMessage = data.detail[0].msg;
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
      } else {
        errorMessage = response.statusText || errorMessage;
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

export async function getGlobalStats() {
  return apiFetch(`${API_BASE_URL}/api/stats`);
}

export async function registerUser(userData: { username: string; nickname: string; password: string }) {
  // email is no longer required for registration
  return apiFetch(`${API_BASE_URL}/api/auth/signup`, {
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

export async function getUserGenreStats(username: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/users/${username}/genre-stats`, { headers });
}

export async function createPlaylistFromId(name: string, seed_track_id: string, token: string | null) {
  return apiFetch(`${API_BASE_URL}/api/playlists`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ name, seed_track_id }),
  });
}

export async function createPlaylistFromUpload(name: string, file: File, token: string | null) {
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

export async function removeTrackFromPlaylist(playlistId: number, trackId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/tracks/${trackId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function addTrackToPlaylist(playlistId: number, trackId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/tracks/${trackId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function removePlaylistEntry(playlistId: number, entryId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/entries/${entryId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function reorderPlaylistTracks(playlistId: number, trackIds: number[], token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/tracks/reorder`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ track_ids: trackIds }),
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

export async function unlikePlaylist(playlistId: number, token: string) {
  return apiFetch(`${API_BASE_URL}/api/playlists/${playlistId}/like`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

export async function getUserCreatedPlaylists(username: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/users/${username}/playlists`, { headers });
}

export async function getUserLikedPlaylists(username: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/users/${username}/likes`, { headers });
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

export async function getUserFeed(token: string) {
  return apiFetch(`${API_BASE_URL}/api/users/feed`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
}

// --- Search Functions ---

export async function searchTracks(query: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/tracks/search?q=${encodeURIComponent(query)}`, { headers });
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
export async function getTaskStatus(taskId: string, token: string | null) {
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch(`${API_BASE_URL}/api/playlists/task/${taskId}`, { headers });
}
