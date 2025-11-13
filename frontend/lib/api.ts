const API_BASE_URL = 'http://localhost:8000';

export async function getBackendStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/status`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch backend status:", error);
    return { status: "error" };
  }
}

export async function registerUser(userData: any) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (!response.ok) {
      let errorMessage = 'An unknown error occurred.';
      if (data.detail) {
        // If detail is an array (like FastAPI validation errors), use the first message
        if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
          errorMessage = data.detail[0].msg;
        } 
        // If detail is just a string
        else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
      }
      throw new Error(errorMessage);
    }

    return { success: true, data };
  } catch (error: any) {
    console.error("Failed to register user:", error);
    return { success: false, error: error.message };
  }
}

export async function loginUser(username: string, password: string) {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to login');
    }

    return { success: true, data };
  } catch (error: any) {
    console.error("Failed to login user:", error);
    return { success: false, error: error.message };
  }
}

export async function getUserProfile(username: string, token: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/${username}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch user profile');
    }

    return { success: true, data };
  } catch (error: any) {
    console.error("Failed to fetch user profile:", error);
    return { success: false, error: error.message };
  }
}

export async function updateUserProfile(username: string, token: string, updateData: any) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${username}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updateData),
      });
  
      const data = await response.json();
  
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update user profile');
      }
  
      return { success: true, data };
    } catch (error: any) {
      console.error("Failed to update user profile:", error);
      return { success: false, error: error.message };
    }
  }

export async function recordListen(trackData: { track_id: string; genre: string }, token: string) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/history/listen`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(trackData),
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to record listening event');
        }

        // We don't necessarily need to return data if it's just a confirmation
        return { success: true };
    } catch (error: any) {
        console.error("Failed to record listening event:", error);
        return { success: false, error: error.message };
    }
}

export async function getUserStats(username: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${username}/stats`);
  
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to fetch user stats');
      }
  
      return { success: true, data: await response.json() };
    } catch (error: any) {
      console.error("Failed to fetch user stats:", error);
      return { success: false, error: error.message };
    }
  }

export async function createPlaylistFromId(name: string, seed_track_id: string, token: string) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/playlists/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ name, seed_track_id }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to create playlist');
        }

        return { success: true, data };
    } catch (error: any) {
        console.error("Failed to create playlist:", error);
        return { success: false, error: error.message };
    }
}

export async function createPlaylistFromUpload(name: string, file: File, token: string) {
    try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/playlists/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
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
  try {
    const response = await fetch(`${API_BASE_URL}/api/playlists/${playlistId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch playlist');
    }

    return { success: true, data };
  } catch (error: any) {
    console.error("Failed to fetch playlist:", error);
    return { success: false, error: error.message };
  }
}
