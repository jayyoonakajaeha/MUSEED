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
